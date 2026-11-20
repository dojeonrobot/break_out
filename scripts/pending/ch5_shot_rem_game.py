# 잔재 부수기(약점 치기·때 맞춰 치기·순서대로 누르기) 화면을 찍고, Space를 연타했을 때 상태가 어긋나는지 받아 적는다.
# 사설 API 8096 + 정적 8097(ch5_with_servers.py로 띄움).  python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_rem_game.py <그림 폴더> [mash]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
OUT = sys.argv[1]; MASH = len(sys.argv) > 2 and sys.argv[2] == 'mash'; T = 9
ST = "(()=>{ const r = __rem(), g = window.__remGame ? __remGame() : null, q = __dbg.quest(); return {game:g && {kind:g.kind, hits:g.hits, need:g.need, done:g.done}, phase:r.mini && r.mini.phase, got:r.mini && r.mini.got, ride:r.ride, down:r.down, vn:!!q.vn(), box:!document.getElementById('miniBox').hidden, go:document.getElementById('miniGo').textContent, play:!document.getElementById('remPlay')?.hidden, pop:(document.getElementById('qPop')||{}).textContent, hud:document.getElementById('qhHint').textContent}; })()"
TALL = "(()=>{ const out = [], s = REM.models[REM.game.i].g.position, v = new THREE.Vector3(), b = new THREE.Box3(); scene.traverse(o=>{ if(!o.isMesh || !o.visible || o.isInstancedMesh) return; let p = o, vis = true; while(p){ if(!p.visible) vis = false; p = p.parent; } if(!vis) return; o.getWorldPosition(v); if(Math.hypot(v.x - s.x, v.z - s.z) > 12) return; b.setFromObject(o); const h = b.max.y - b.min.y; if(h < 9) return; let n = ''; p = o; while(p && !n){ n = p.name; p = p.parent; } out.push([o.geometry.type, Math.round(h), Math.round(b.max.x - b.min.x), o.material.color ? o.material.color.getHexString() : '', o.material.opacity, n]); }); return out; })()"   # 잔재 둘레의 키 큰 물체(빛기둥 찾기)
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1366, 'height': 768}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        async def hook(r):   # 점검용 창구(__ev)는 받아 온 본문에만 끼운다
            res = await r.fetch(); body = (await res.text()).replace('window.__remAim = ', 'window.__ev = s=> eval(s);\nwindow.__remAim = ', 1); await r.fulfill(response=res, body=body)
        await ctx.route(re.compile(r'.*/chapter05/index[.]html.*'), hook)
        cp = json.dumps({'q': 'q5', 'step': 'rail', 'got': []})
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','remgame');localStorage.setItem('void-sound','0');if(!sessionStorage.getItem('rem-set')){localStorage.setItem('void-mini-%d', '%s');}addEventListener('load',()=>setTimeout(()=>sessionStorage.setItem('rem-set','1'),9000));" % (T, cp.replace("'", "\\'")))
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True); await post('admin/skip', {'team': T, 'mission': 'z2'}, True)
        await post('quest', {'team': T, 'dev': 'remgame', 'done': ['q1', 'q2', 'q4'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:300])); ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for rnd in range(2):   # 조 초기화가 닿으면 페이지가 한 번 새로 열린다: 한 번 뜬 뒤 6초 두고 다시 기다린다
            for _ in range(480):
                try:
                    if await ev("typeof window.__dbg!=='undefined' && typeof window.__rem==='function' && !!window.__dbg.rideState"): break
                except Exception: pass
                await asyncio.sleep(.25)
            if rnd == 0: await asyncio.sleep(6)
        print('renderer', await ev("(()=>{const c=document.createElement('canvas').getContext('webgl');const e=c.getExtension('WEBGL_debug_renderer_info');return e?c.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)
        async def drain(n=60):
            for _ in range(n):
                if await ev("!!window.__mcard && __mcard()"): pass
                await ev("(()=>{ const b = document.getElementById('mcGo'); const d = document.getElementById('mCard') || (b && b.closest('[data-on]')); if(b && d && d.dataset.on) b.click(); })()")
                if not await ev('!!__dbg.quest().vn()'):
                    await asyncio.sleep(.4)
                    if not await ev('!!__dbg.quest().vn()'): return
                await ev('__dbg.quest().next()'); await asyncio.sleep(.08)
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(1.5)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5); await drain(); await asyncio.sleep(1); await drain()
        print('start', await ev(ST), flush=True)
        st = await ev('__rem().station'); await ev(f"__dbg.walkTo({st[0]}, {st[1]})")
        for _ in range(80):
            await drain(6)
            if await ev('!!__rem().ride'): break
            await asyncio.sleep(.4)
        print('riding', await ev(ST), flush=True); await ev('__remBoost(6)')
        await ev("()=>{ window.__autoDet = setInterval(()=>{ const b = document.getElementById('miniGo'), r = __rem().ride; if(b && b.classList.contains('hot') && r && !r.pause && !__rem().game){ document.body.dispatchEvent(new KeyboardEvent('keydown', {code:'Space', bubbles:true})); setTimeout(()=> document.body.dispatchEvent(new KeyboardEvent('keyup', {code:'Space', bubbles:true})), 50); } }, 70); }")
        for i in range(3):
            for _ in range(500):
                await drain(4)
                if await ev("!!(__rem().game && !__rem().game.done)"): break
                await asyncio.sleep(.25)
            await asyncio.sleep(2.2); s = await ev(ST); print('GAME', i, s, flush=True); k = s['game']['kind'] if s['game'] else i
            await pg.screenshot(path=os.path.join(OUT, f'rem_kind{k}.png'), timeout=60000)
            print('  tall', json.dumps(await ev('(s)=> __ev(s)', TALL), ensure_ascii=False)[:900], flush=True)
            if MASH:
                await ev("()=>{ clearInterval(window.__autoDet); }"); seen = []
                for n in range(260):   # 약 20초 동안 75ms마다 Space
                    await pg.keyboard.press('Space')
                    if n % 4 == 0:
                        s = await ev(ST); key = json.dumps(s, ensure_ascii=False)
                        if not seen or seen[-1] != key: seen.append(key); print('  mash', n, key[:420], flush=True)
                    await asyncio.sleep(.075)
                await pg.screenshot(path=os.path.join(OUT, f'rem_mash{i}.png'), timeout=60000); await asyncio.sleep(3); print('  after mash', await ev(ST), flush=True)
                await pg.screenshot(path=os.path.join(OUT, f'rem_mash{i}_after.png'), timeout=60000)
                break
            await ev('__remWin()'); await asyncio.sleep(2.5); await drain(); await asyncio.sleep(1)
        print('errs', errs); await br.close()
asyncio.run(main())
