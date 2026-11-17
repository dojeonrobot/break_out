# 2026-11-17 점검: ① 튜토리얼의 섬 단계가 그림으로 나오고 월드는 캠퍼스 그대로인지, 좌표 카드 예시가 뜨는지 ② 미션을 걷는 중에는 나가기·Esc가 안 먹는지(아이 기기).
# 사설 API 8096(CH5_ADMIN_KEY=0101) + 정적 8097.  python scripts/pending/ch5_check_flowlock_tut.py <그림 폴더>
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 7; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg)
    if not ok: fails.append(msg)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','flk');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        async def ready():
            for _ in range(480):
                try:
                    if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): return
                except Exception: pass
                await asyncio.sleep(.25)
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000); await ready()
        for _ in range(120):
            if await pg.evaluate("__dbg.tutState().step") == 0: break
            await asyncio.sleep(.5)
        check(await pg.evaluate("__dbg.tutState().step") == 0, '튜토리얼이 시작됐다')
        async def step_to(n):
            for _ in range(200):
                st = await pg.evaluate("__dbg.tutState().step")
                if st >= n: return
                await pg.keyboard.press('Space'); await asyncio.sleep(.35)
        for n, name in ((7, 'tut07_island'), (12, 'tut12_harmonia')):
            await step_to(n); await asyncio.sleep(1.4)
            r = await pg.evaluate("()=>{ const e = document.getElementById('tutStill'); const i = e && e.querySelector('img[data-on]'); return {world:__dbg.tutState().world, on:!!(e && e.dataset.on), k:i && i.dataset.k, ok:!!(i && i.complete && i.naturalWidth > 0), txt:document.getElementById('voidTxt').innerText.slice(0, 30)}; }")
            print('   ', r); check(r['world'] == 'erica' and r['on'] and r['ok'], f'{n}번째 단계: 그림이 뜨고 월드는 캠퍼스 그대로 ({r["k"]})')
            await pg.screenshot(path=f'{OUT}/{name}.png')
        await step_to(13); await asyncio.sleep(1.2)
        r = await pg.evaluate("()=>{ const e = document.getElementById('tutStill'); return {on:!!(e && e.dataset.on), world:__dbg.tutState().world}; }"); check(not r['on'] and r['world'] == 'erica', '13번째 단계: 그림이 걷히고 캠퍼스')
        await step_to(21); await asyncio.sleep(2.2)
        r = await pg.evaluate("()=>{ const e = document.getElementById('meCoord'); return {hidden:e.hidden, txt:e.innerText.replace(/\\s+/g, ' ')}; }"); print('   ', r); check(not r['hidden'] and '남음' in r['txt'], '21번째 단계: 좌표 카드 예시가 뜬다')
        await pg.screenshot(path=f'{OUT}/tut21_coord.png')
        await step_to(22); await asyncio.sleep(.8); check(await pg.evaluate("document.getElementById('meCoord').hidden"), '다음 단계에서 좌표 카드가 다시 숨는다')
        for _ in range(40):
            if await pg.evaluate("__dbg.tutState().step") in (-1, 99): break
            await pg.keyboard.press('Space'); await asyncio.sleep(.4)
        # ② flow lock: 기록 1을 건너뛰고 1막을 넘겨 미션 1을 걷는 상태로
        await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        for _ in range(400):
            if await pg.evaluate("__dbg.simState().walk"): break
            await pg.keyboard.press('Space'); await asyncio.sleep(.5)
        check(await pg.evaluate("__dbg.simState().walk"), '1막 뒤 미션 1 걷기가 시작됐다')
        await asyncio.sleep(1.5)
        r = await pg.evaluate("()=>({xHidden:document.getElementById('walkX').hidden, void:getComputedStyle(document.getElementById('restoreBtn')).display, sim:getComputedStyle(document.getElementById('simBtn')).display, worlds:getComputedStyle(document.getElementById('worlds')).display})"); print('   ', r)
        check(r['xHidden'] and r['void'] == 'none' and r['sim'] == 'none' and r['worlds'] == 'none', '미션 중: 나가기·보이드·시뮬레이터·월드 버튼이 없다')
        await pg.keyboard.press('Escape'); await asyncio.sleep(.6); check(await pg.evaluate("__dbg.simState().walk"), '미션 중: Esc로 나가지지 않는다')
        await pg.screenshot(path=f'{OUT}/mission_walk.png')
        fx = await pg.evaluate("__dbg.fxlog().filter(e=> e.c.startsWith('arrive:')).map(e=> e.c + ' ' + e.n + ' ' + e.ev)"); print('    fx', fx[:12]); check(any('draw end' in x for x in fx), '1막에서 기록 복귀 연출(그려지는 단계)이 끝까지 재생됐다')
        check(not any(' bulbs ' in x or ' run ' in x for x in fx), '정전 중이라 전구·출발 단계는 없다')
        print('errs', errs); check(not errs, '페이지 오류 없음'); print('FAILS', fails); await br.close()
asyncio.run(main())
