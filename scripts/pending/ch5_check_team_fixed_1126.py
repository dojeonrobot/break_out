# 조 고정 확인: ① 조가 있는 태블릿 = 「우리 조 9조」 글자만(고르는 칸 없음) ② 조 없는 기기 = 「조 고르기」 → 조 고르기 창 → 고르면 글자로 바뀜. 사설 API 8096 + 정적 8097. 인자: 출력 폴더
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; OUT = sys.argv[1]
ST = "({txt:document.querySelector('#panel .team').innerText.replace(/\\s+/g,' '), selVisible: !!document.getElementById('teamSel').offsetParent, pick: !document.getElementById('teamPickBtn').hidden, dlg: !!document.getElementById('teamPick').dataset.on, sub: getComputedStyle(document.getElementById('pSub')).display})"
async def open_page(br, team):
    ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True, is_mobile=True); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');localStorage.removeItem('void-board');localStorage.removeItem('void-panel');")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{STATIC}/chapter05/index.html' + (f'?team={team}' if team else ''), wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await asyncio.sleep(4); return ctx, pg, errs
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        rq = (await br.new_context()).request
        await rq.post(API + '/api/void/team_reset', data=json.dumps({'team': 9, 'confirm': 'AGAIN'}), headers=ADM)
        ctx, pg, errs = await open_page(br, 9)
        print('team9', await pg.evaluate(ST)); await pg.screenshot(path=os.path.join(OUT, 'team9.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 300}); print('errs', errs[:2]); await ctx.close()
        ctx, pg, errs = await open_page(br, 0)
        for _ in range(40):   # the intro opens the team dialog; close it with 「나중에」
            if await pg.evaluate("!!document.getElementById('teamPick').dataset.on"): break
            await pg.evaluate("window.__dbg && __dbg.skipIntro && __dbg.skipIntro()"); await asyncio.sleep(.5)
        if await pg.evaluate("!!document.getElementById('teamPick').dataset.on"): await pg.click('#tpSkip'); await asyncio.sleep(.4)
        print('noteam', await pg.evaluate(ST)); await pg.screenshot(path=os.path.join(OUT, 'noteam.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 300})
        await pg.evaluate("document.getElementById('teamPickBtn').click()"); await asyncio.sleep(.4); print('after pick btn', await pg.evaluate(ST))
        await pg.click('#tpGrid [data-t="9"]'); await asyncio.sleep(1); print('after choose', await pg.evaluate(ST)); print('errs', errs[:2])
        await br.close()
asyncio.run(main())
