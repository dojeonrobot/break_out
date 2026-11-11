"""2026-11-04 바이킹 복구 점검: 공사장 → 조가 STL 업로드 → 배가 팔에 걸려 흔들림, 다른 조는 공사장 그대로, 관리자 되돌리기, 잘못된 파일 거부.
사설 API(server 복사본, VOID_PORT=8096 VOID_STATIC=0 CH5_ADMIN_KEY=0101) + 정적 8097(저장소 루트) 필요.
python scripts/pending/ch5_check_viking.py <ship.stl> <ship.obj> <bad.stl> [shot_dir]"""
import asyncio, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'
STL, OBJ, BAD = sys.argv[1:4]; SHOT = sys.argv[4] if len(sys.argv) > 4 else None
ADM = {'X-Admin-Key': '0101'}

async def ready(pg, t=120):
    for _ in range(t*2):
        try:
            if await pg.evaluate('!!window.__vik && !!window.__dbg'): return
        except Exception: pass
        await asyncio.sleep(.5)
    raise AssertionError('page not ready')

async def page_for(br, team, dev):
    ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=.5)
    await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');")
    async def route(r):
        q = r.request
        res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(f'{STATIC}/chapter05/index.html?team={team}&world=island', wait_until='load', timeout=120000)
    await ready(pg)
    await pg.evaluate("()=>{ document.querySelectorAll('#teamPick').forEach(e=> delete e.dataset.on); }")
    return ctx, pg, errs

async def wait_vik(pg, cond, t=20):
    for _ in range(t*5):
        v = await pg.evaluate('__vik()')
        if cond(v): return v
        await asyncio.sleep(.2)
    raise AssertionError(await pg.evaluate('__vik()'))

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        rq = (await br.new_context()).request
        for t in (10, 11):
            await rq.post(API + '/api/void/team_reset', data={'team': t, 'confirm': 'AGAIN'}, headers=ADM)
            await rq.post(API + '/api/void/quest', data={'team': t, 'dev': f'vik{t}', 'done': [], 'act': 1, 'tut': True, 'story': 3})
        r = await rq.post(API + '/api/void/viking?team=10&ext=stl', data=open(BAD, 'rb').read(), headers={'Content-Type': 'application/octet-stream'})
        assert r.status == 400, r.status; print('OK server rejects a file that is not an STL', flush=True)

        c1, pg, e1 = await page_for(br, 10, 'vik10')
        v = await pg.evaluate('__vik()'); assert not v['on'] and v['site'] and not v['swing'] and v['kids'] == 0, v
        print('OK before upload the viking is a construction site (no ship, scaffolding shown)', flush=True)
        await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(1)
        i = await pg.evaluate("__dbg.IB ? __dbg.IB.findIndex(b=> b.label==='바이킹') : -1")
        await pg.evaluate("__vikOpen()"); await asyncio.sleep(1.2)
        assert await pg.locator('#iIsl .vik [data-vik="up"]').count() == 1, await pg.locator('#iIsl').inner_html()
        print('OK the viking card offers the upload button on a team tablet', flush=True)
        if SHOT: await pg.evaluate('requestAnimationFrame=()=>0'); await pg.screenshot(path=os.path.join(SHOT, 'vik_site.png')); await pg.reload(wait_until='load', timeout=120000); await ready(pg)
        await pg.evaluate("__vikOpen()"); await asyncio.sleep(1)
        async with pg.expect_file_chooser() as fc:
            await pg.locator('#iIsl .vik [data-vik="up"]').click()
        await (await fc.value).set_files(STL)
        v = await wait_vik(pg, lambda v: v['on'] and v['kids'] == 1)
        assert not v['site'] and v['swing'] and v['size'] and v['size'][0] <= 42.5 and v['size'][2] <= 12.5 and v['size'][0] > v['size'][2], v
        r0 = (await pg.evaluate('__vik()'))['rot']; await asyncio.sleep(1.2); r1 = (await pg.evaluate('__vik()'))['rot']
        print(f'OK STL upload rebuilds the viking on this tablet, ship fitted {[round(x,1) for x in v["size"]]}, swing {round(r0,2)} -> {round(r1,2)}', flush=True)
        st = await (await rq.get(API + '/api/void/state')).json(); assert st['vikings']['10']['ext'] == 'stl', st.get('vikings')
        f = await rq.get(API + '/api/void/viking/10.stl'); assert f.status == 200 and len(await f.body()) == os.path.getsize(STL)
        print('OK server keeps the file per team and serves it back unchanged', flush=True)
        if SHOT:
            await pg.evaluate("__vikOpen()"); await asyncio.sleep(4)
            await pg.evaluate('requestAnimationFrame=()=>0'); await pg.screenshot(path=os.path.join(SHOT, 'vik_rebuilt.png'))
            await pg.reload(wait_until='load', timeout=120000); await ready(pg)
        await pg.reload(wait_until='load', timeout=120000); await ready(pg)
        await wait_vik(pg, lambda v: v['on'] and v['kids'] == 1); print('OK reload keeps the rebuilt viking', flush=True)

        c2, pg2, e2 = await page_for(br, 11, 'vik11')
        await asyncio.sleep(3); v2 = await pg2.evaluate('__vik()'); assert not v2['on'] and v2['site'], v2
        print("OK another team's tablet still shows its own construction site", flush=True)
        r = await rq.post(API + '/api/void/viking?team=11&ext=obj&name=ship.obj', data=open(OBJ, 'rb').read(), headers={'Content-Type': 'application/octet-stream'})
        assert r.status == 200; await wait_vik(pg2, lambda v: v['on'] and v['kids'] == 1, 30)
        print('OK an OBJ upload for team 11 reaches that tablet through the state poll', flush=True)
        v = await pg.evaluate('__vik()'); assert v['team'] == '10', v

        r = await rq.post(API + '/api/void/admin/viking_clear', data={'team': 11}, headers=ADM); assert r.status == 200
        await wait_vik(pg2, lambda v: not v['on'] and v['site'], 30); print('OK admin clear turns team 11 back into a construction site', flush=True)
        await rq.post(API + '/api/void/team_reset', data={'team': 10, 'confirm': 'AGAIN'}, headers=ADM)
        st = await (await rq.get(API + '/api/void/state')).json(); assert '10' not in st['vikings']
        print('OK team reset removes the team ship too', flush=True)
        pl = await pg.evaluate("__dbg.IB ? __dbg.IB.some(b=> b.label==='끊어진 배전선') : null")
        print('power line pickable:', pl, flush=True)
        assert not e1 and not e2, (e1, e2); print('OK no runtime errors', flush=True)
        await br.close()
asyncio.run(main())
