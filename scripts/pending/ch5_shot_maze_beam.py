# 미션 2 상태(미션 1 끝)에서 미로 입구와 미로 안 통로에 눈높이로 서서 한가운데 쪽을 본 그림. 붉은 빛기둥과 네이티가 보이는지 확인. 사설 API 8096 + 정적 8097.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','beam');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'beam', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(3); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
        await pg.evaluate("()=>{ const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }")
        for name, x, z in (('entrance', 155, 368), ('corridor', 132.5, 391.5), ('far', 100, 362)):
            await pg.evaluate("([x, z])=>{ const T = __dbg.THREE, M = __dbg.maze(), y = __dbg.groundY(x, z); __dbg.controls.minDistance = 0.5; __dbg.flyTo(new T.Vector3(x, y + 1.5, z), new T.Vector3(M.cx, y + 7, M.cz), 10); }", [x, z]); await asyncio.sleep(2)
            await pg.screenshot(path=os.path.join(OUT, name + '.png'), timeout=60000)
        print('naty', await pg.evaluate("(()=>{ const n = __dbg.chars().NATY; return {pos:n.position.toArray().map(v=> Math.round(v)), beam:!!n.userData.beam && n.userData.beam.visible}; })()"), 'errs', errs[:2]); await br.close()
asyncio.run(main())
