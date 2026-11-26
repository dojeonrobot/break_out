# 진도 맞추기 확인: 노트북(먼저 들어와 진도 없음)이 같은 조 태블릿(미션 3개·2막)의 진도를 가져오는지, 거꾸로 태블릿도 노트북 것을 가져올 수 있는지.
# 사설 API 8096 + 정적 8097. 인자: 출력 폴더
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]
J = {'content-type': 'application/json'}
async def page(br, dev, vp, touch):
    ctx = await br.new_context(viewport=vp, has_touch=touch, is_mobile=touch); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');localStorage.setItem('void-sound','0');")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    await ready(pg); return ctx, pg, errs
async def ready(pg):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await asyncio.sleep(4)
async def entries(rq):
    st = await (await rq.get(API + f'/api/void/state')).json()
    return {l: (v.get('kind'), sorted(k for k in v if re.match(r'^q\d$', k)), v.get('act')) for l, v in st['quests'].get(str(T), {}).items()}
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        rq = (await br.new_context()).request
        await rq.post(API + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers=ADM)
        await rq.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'lap1', 'kind': 'laptop', 'tut': True}), headers=J)
        await rq.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'tab1', 'kind': 'tablet', 'tut': True}), headers=J)
        await rq.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'tab1', 'done': ['q1', 'q2', 'q4'], 'act': 2, 'story': 3, 'power': True}), headers=J)
        print('before', await entries(rq))
        ctx, pg, errs = await page(br, 'lap1', {'width': 1440, 'height': 900}, False)
        await pg.click('#syncBtn'); await asyncio.sleep(1)
        print('dialog', await pg.evaluate("document.getElementById('syList').innerText.replace(/\\s+/g,' ')"))
        await pg.screenshot(path=os.path.join(OUT, 'sync_dialog.png'))
        await pg.screenshot(path=os.path.join(OUT, 'sync_panel.png'), clip={'x': 0, 'y': 0, 'width': 420, 'height': 200})
        await pg.click('[data-sy]'); await asyncio.sleep(2); await ready(pg)
        print('after laptop pull', await entries(rq), 'errs', errs[:2])
        print('laptop page sees', await pg.evaluate("Object.keys((window.__dbg && __dbg.quest && __dbg.quest().done) ? {} : {}).length"))
        await ctx.close()
        # reverse: laptop finishes q5 (the STL side), the tablet pulls it back
        await rq.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'lap1', 'done': ['q1', 'q2', 'q4', 'q5'], 'act': 2}), headers=J)
        ctx, pg, errs = await page(br, 'tab1', {'width': 1180, 'height': 820}, True)
        await pg.tap('#syncBtn'); await asyncio.sleep(1)
        print('tablet dialog', await pg.evaluate("document.getElementById('syList').innerText.replace(/\\s+/g,' ')"))
        await pg.screenshot(path=os.path.join(OUT, 'sync_dialog_tablet.png'))
        await pg.tap('[data-sy]'); await asyncio.sleep(2); await ready(pg)
        print('after tablet pull', await entries(rq), 'errs', errs[:2])
        await br.close()
asyncio.run(main())
