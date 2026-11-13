# 조 태블릿 화면 두 장: ① 캠퍼스의 현황판(복구율) ② 섬에서 걷는 화면의 조이스틱과 「달리기」 버튼. 사설 API 8096 + 정적 8097.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True, is_mobile=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','brd');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'brd', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(5); await pg.screenshot(path=os.path.join(OUT, 'board.png'))
        print('board', await pg.evaluate("({n:document.getElementById('bN').innerText, rows:document.getElementById('bRows').innerText.replace(/\\s+/g,' '), lbl:document.getElementById('lLbl').getAttribute('aria-pressed'), labels:[...document.querySelectorAll('.lbl')].filter(e=> e.offsetParent && getComputedStyle(e).display !== 'none' && +getComputedStyle(e).opacity > 0.1).length})"))
        await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2)
        await pg.evaluate("()=>{ const h = document.getElementById('heroPick'); if(h.dataset.on) document.getElementById('hpGo').click(); }"); await asyncio.sleep(2.5)
        for _ in range(30):
            if not await pg.evaluate("!!__dbg.quest().vn()"): break
            await pg.evaluate("__dbg.quest().next()"); await asyncio.sleep(.15)
        await asyncio.sleep(1); r0 = await pg.evaluate("(()=>{ const b = document.getElementById('walkRun'), r = b.getBoundingClientRect(), p = document.getElementById('walkPad').getBoundingClientRect(); return {hidden:b.hidden, disp:getComputedStyle(b).display, box:[r.left, r.top, r.width, r.height].map(Math.round), pad:[p.left, p.top, p.width, p.height].map(Math.round)}; })()")
        await pg.tap('#walkRun'); await asyncio.sleep(.4); print('run', r0, 'pressed', await pg.evaluate("document.getElementById('walkRun').getAttribute('aria-pressed')"))
        await pg.screenshot(path=os.path.join(OUT, 'walk.png')); print('errs', errs[:2]); await br.close()
asyncio.run(main())
