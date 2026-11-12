# 미로 안 화면 찍기(미션 2). 사설 API 8096 + 정적 8097. python scripts/pending/ch5_shot_maze.py <그림 폴더> [접두어] [가로 세로]
# 입구 앞 → 입구 대사 뒤 → 미로 안 여러 칸(실제로 키를 눌러 걷기) → 한가운데 앞까지. 칸마다 화면과 걷기 상태를 찍는다.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 7
OUT = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else 'maze'; VW = int(sys.argv[3]) if len(sys.argv) > 4 else 1180; VH = int(sys.argv[4]) if len(sys.argv) > 4 else 820
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': VW, 'height': VH}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','mazeshot');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'mazeshot', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400])); logs = []; pg.on('console', lambda m: logs.append(m.text[:200]) if m.type in ('error', 'warning') else None)
        ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__chase==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        async def drain(n=60):
            for _ in range(n):
                if not await ev('!!__dbg.quest().vn()'):
                    await asyncio.sleep(.4)
                    if not await ev('!!__dbg.quest().vn()'): return
                await ev('__dbg.quest().next()'); await asyncio.sleep(.08)
        shot = lambda n: pg.screenshot(path=os.path.join(OUT, f'{PRE}_{n}.png'), timeout=60000)
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(1.5)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); await drain()
        t = await ev('__dbg.target()'); print('entrance', t)
        await ev(f"__dbg.walkTo({t[0]}, {t[1]})"); await asyncio.sleep(1.5); await shot('1_entrance_dialogue'); await drain(); await asyncio.sleep(1); await shot('2_entrance')
        heart = await ev('__dbg.target()'); print('heart', heart)
        # walk in for real: hold W, steer towards the heart a little at a time
        for k in range(6):
            await pg.keyboard.down('KeyW'); await asyncio.sleep(1.6); await pg.keyboard.up('KeyW'); await asyncio.sleep(.3)
            st = await ev("(()=>{ const w = __dbg.walkState(); const i = __dbg.renderer.info.render; return {x:Math.round(w.x), z:Math.round(w.z), inside:__dbg.mazeInside(w.x, w.z), calls:i.calls, tris:i.triangles}; })()"); print('walk', k, st)
            await shot(f'3_in_{k}')
            if k == 2: await pg.keyboard.down('KeyD'); await asyncio.sleep(.5); await pg.keyboard.up('KeyD')
        # a few cells towards the heart, by teleport, to see deep corridors
        e = t
        for k, u in enumerate((.25, .5, .75, .93)):
            x, z = e[0] + (heart[0] - e[0])*u, e[1] + (heart[1] - e[1])*u
            await ev(f"__dbg.walkTo({x}, {z})"); await asyncio.sleep(1.2)
            print('tele', k, await ev("(()=>{ const w = __dbg.walkState(); return {x:Math.round(w.x), z:Math.round(w.z), blocked:__dbg.walkBlocked(w.x, w.z)}; })()")); await shot(f'4_deep_{k}')
        print('errors:', errs); print('console:', logs[:8])
        await br.close()
asyncio.run(main())
