# 찾은 인물과 겹쳐 서지 않는지 점검(미션 1 자일로). 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_found_gap.py [그림 폴더]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 3
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','foundgap');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'foundgap', 'done': [], 'act': 1, 'tut': True, 'story': 3})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(2)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        for _ in range(30):
            if not await ev('!!__dbg.quest().vn()'): break
            await ev('__dbg.quest().next()'); await asyncio.sleep(.1)
        t = await ev('__dbg.target()'); await ev(f"__dbg.walkTo({t[0]}, {t[1]})")   # exactly on 자일로
        for _ in range(60):
            if await ev('!!__dbg.quest().vn()'): break
            await asyncio.sleep(.2)
        await asyncio.sleep(1.2)
        g = await ev("(()=>{ const w = __dbg.walkState(), x = __dbg.chars().XYLO.position; return [Math.hypot(w.x - x.x, w.z - x.z), __dbg.walkBlocked(w.x, w.z)]; })()")
        print(('OK   ' if 4 <= g[0] <= 5 and not g[1] else 'FAIL ') + f'found dialogue: the walker stands {g[0]:.1f} from 자일로, on walkable ground')
        if SHOT:
            os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, 'found_xylo.png'), timeout=60000)
        print('errors:', errs); await br.close()
asyncio.run(main())
