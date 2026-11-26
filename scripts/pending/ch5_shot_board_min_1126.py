# 조 현황판(기록 복구 현황) 열림/접힘을 노트북·태블릿에서 찍음. 사설 API 8096 + 정적 8097. 인자: 출력 폴더
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]
async def shoot(br, name, vp, touch):
    ctx = await br.new_context(viewport=vp, has_touch=touch, is_mobile=touch); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','brd');localStorage.setItem('void-sound','0');localStorage.removeItem('void-board');")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    if name == 'laptop': print('renderer', await pg.evaluate("(()=>{const g=document.createElement('canvas').getContext('webgl');const e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)})()"))
    await asyncio.sleep(4)
    b = await pg.query_selector('#board')
    print(name, 'open', await pg.evaluate("({txt:document.getElementById('board').innerText.replace(/\\s+/g,' '), btn:document.getElementById('bMin').getAttribute('aria-label')})"))
    await b.screenshot(path=os.path.join(OUT, f'{name}_open.png'))
    await pg.click('#bMin'); await asyncio.sleep(.6)
    print(name, 'closed', await pg.evaluate("({txt:document.getElementById('board').innerText.replace(/\\s+/g,' '), btn:document.getElementById('bMin').getAttribute('aria-label')})"))
    await b.screenshot(path=os.path.join(OUT, f'{name}_closed.png'))
    print(name, 'errs', errs[:2]); await ctx.close()
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        rq = (await br.new_context()).request
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'brd', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        await shoot(br, 'laptop', {'width': 1440, 'height': 900}, False)
        await shoot(br, 'tablet', {'width': 1180, 'height': 820}, True)
        await br.close()
asyncio.run(main())
