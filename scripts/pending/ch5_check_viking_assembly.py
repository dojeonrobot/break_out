"""2026-11-12 바이킹 어셈블리 점검: 받침대와 배가 함께 든 STL을 올리면 받침대는 서 있고 배만 봉을 축으로 흔들리는지.
사설 API(server 복사본, VOID_PORT=8096 VOID_STATIC=0 CH5_ADMIN_KEY=0101) + 정적 8097(저장소 루트) 필요.
python scripts/pending/ch5_check_viking_assembly.py <assembly.stl> [shot_dir] [ship_only.stl]"""
import asyncio, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'
ASM = sys.argv[1]; SHOT = sys.argv[2] if len(sys.argv) > 2 else None; SHIP = sys.argv[3] if len(sys.argv) > 3 else None
ADM = {'X-Admin-Key': '0101'}; T = 12

async def ready(pg, t=120):
    for _ in range(t*2):
        try:
            if await pg.evaluate('!!window.__vik && !!window.__dbg'): return
        except Exception: pass
        await asyncio.sleep(.5)
    raise AssertionError('page not ready')

async def wait_vik(pg, cond, t=30):
    for _ in range(t*5):
        v = await pg.evaluate('__vik()')
        if cond(v): return v
        await asyncio.sleep(.2)
    raise AssertionError(await pg.evaluate('__vik()'))

async def shot(pg, name):
    if not SHOT: return
    await pg.evaluate('()=>{ window.__raf0 = window.__raf0 || requestAnimationFrame; window.__rafQ = []; requestAnimationFrame = f=>{ window.__rafQ.push(f); return 0; }; }'); await asyncio.sleep(.3)
    await pg.screenshot(path=os.path.join(SHOT, name)); await pg.evaluate('()=>{ requestAnimationFrame = window.__raf0; (window.__rafQ||[]).splice(0).forEach(f=> requestAnimationFrame(f)); }')

async def upload(pg, path):
    await pg.evaluate("__vikOpen()"); await asyncio.sleep(1.2)
    async with pg.expect_file_chooser() as fc:
        await pg.locator('#iIsl .vik [data-vik="up"]').click()
    await (await fc.value).set_files(path)

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=.75)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','vikasm');localStorage.setItem('void-sound','0');")
        rq = ctx.request
        await rq.post(API + '/api/void/team_reset', data={'team': T, 'confirm': 'AGAIN'}, headers=ADM)
        for z in ('z1', 'z2'): await rq.post(API + '/api/void/admin/skip', data={'team': T, 'mission': z}, headers=ADM)   # 올리기 버튼은 미션 3(두 번째 캠퍼스 기록 뒤)부터 보인다
        await rq.post(API + '/api/void/quest', data={'team': T, 'dev': 'vikasm', 'done': ['q1', 'q2'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
        async def route(r):
            q = r.request
            res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' and 'favicon' not in m.text and 'Failed to load resource' not in m.text else None)
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}&world=island', wait_until='load', timeout=120000)
        await ready(pg)
        print('renderer:', await pg.evaluate("(()=>{ const c = document.createElement('canvas').getContext('webgl2'); const e = c.getExtension('WEBGL_debug_renderer_info'); return e ? c.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'n/a'; })()"), flush=True)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick').forEach(e=> delete e.dataset.on); }")
        await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(1.5)
        v = await pg.evaluate('__vik()'); assert not v['on'] and v['site'] and v['frame'], v
        print('OK before upload: construction site with the built-in stand', flush=True)

        await upload(pg, ASM)
        v = await wait_vik(pg, lambda v: v['on'] and v['kids'] == 1)
        assert v['asm'] and not v['frame'] and not v['swing'] and not v['site'], v
        assert v['parts'][0] >= 1 and v['parts'][1] >= 1, v
        sx, sy, sz = v['size']; assert sx <= 52.5 and sz <= 24.5 and sy <= 38.5, v
        print(f"OK assembly recognised: stand pieces {v['parts'][0]}, ship pieces {v['parts'][1]}, size {[round(x,1) for x in v['size']]}, axis at {[round(x,1) for x in v['piv']]}", flush=True)
        st = await (await rq.get(API + '/api/void/state')).json(); assert st['vikings'][str(T)]['ext'] == 'stl', st.get('vikings')
        rots = []
        for _ in range(12): rots.append((await pg.evaluate('__vik()'))['rot']); await asyncio.sleep(.5)
        assert max(rots) - min(rots) > 0.5, rots
        print(f'OK the ship swings on its own axis: {round(min(rots),2)} .. {round(max(rots),2)} rad', flush=True)
        # the stand must stay still while the ship moves
        mv = await pg.evaluate("""async ()=>{ const s = __dbg.scene || null; return null; }""")
        if SHOT:
            await pg.evaluate("()=>{ const c = document.querySelector('#info .x, #iClose'); if(c) c.click(); }")
            cx, cz = await pg.evaluate("(()=>{ const b = __dbg.IB.find(b=> b.label==='바이킹'); return [b.cx, b.cz]; })()")
            await pg.evaluate(f"__islandCam({cx}, {cz}, 150)"); await asyncio.sleep(2.5)
            for i in range(4): await shot(pg, f'asm_{i}.png'); await asyncio.sleep(1.1)
        await pg.reload(wait_until='load', timeout=120000); await ready(pg)
        v = await wait_vik(pg, lambda v: v['on'] and v['kids'] == 1 and v['asm']); print('OK reload keeps the assembly', flush=True)

        if SHIP:
            await pg.evaluate("()=>{ document.querySelectorAll('#teamPick').forEach(e=> delete e.dataset.on); }")
            await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(1.5)
            await upload(pg, SHIP)
            v = await wait_vik(pg, lambda v: v['on'] and v['kids'] == 1 and not v['asm'])
            assert v['frame'] and v['swing'], v
            print(f"OK a ship on its own still hangs from the built-in stand, size {[round(x,1) for x in v['size']]}", flush=True)
            if SHOT:
                cx, cz = await pg.evaluate("(()=>{ const b = __dbg.IB.find(b=> b.label==='바이킹'); return [b.cx, b.cz]; })()")
                await pg.evaluate(f"__islandCam({cx}, {cz}, 150)"); await asyncio.sleep(2.5); await shot(pg, 'ship_only.png')
        r = await rq.post(API + '/api/void/admin/viking_clear', data={'team': T}, headers=ADM); assert r.status == 200
        v = await wait_vik(pg, lambda v: not v['on'] and v['site'] and v['frame'] and v['kids'] == 0, 30); print('OK admin clear: back to the construction site with the built-in stand', flush=True)
        print('baked audit:', await pg.evaluate("__dbg.bakedAudit ? __dbg.bakedAudit() : 'n/a'"), flush=True)
        assert not errs, errs; print('OK no runtime errors', flush=True)
        await br.close()
asyncio.run(main())
