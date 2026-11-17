# 미션 시작 카드 → 전원 연출 → 네이티가 사라진 장면 → 미션 완료(좌표) 카드를 찍는다(관리자 건너뛰기로 미션 1·2를 지나며). 사설 API 8096 + 정적 8097.  python scripts/pending/ch5_shot_park_wake.py <그림 폴더>
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 6; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','pwk');localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));sessionStorage.setItem('void-view','%d');" % T)
        post = lambda path, body: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM)
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}); await post('admin/skip', {'team': T, 'mission': 'z1'}); await post('quest', {'team': T, 'dev': 'pwk', 'done': [], 'act': 1, 'tut': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.skip"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4); await pg.evaluate("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; __dbg.setWorld('island', true); }"); await asyncio.sleep(1.5); await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2)
        async def shot(n): await pg.screenshot(path=f'{OUT}/{n}.png')
        async def until(label, n=80, snap=None):
            seen = []
            for _ in range(n):
                w = await pg.evaluate("__dbg.skipWhat()"); seen.append(w)
                if w == label:
                    if snap: await asyncio.sleep(1.2); await shot(snap)
                    await pg.evaluate("__dbg.skip()"); await asyncio.sleep(.8); return True
                if w: await pg.evaluate("__dbg.skip()")
                await asyncio.sleep(.8)
            print('not reached', label, seen[-6:]); return False
        await until('미션 시작', snap='1_mission_card')
        await until('전원 연출 보기')
        for i in range(14):
            await asyncio.sleep(1.5)
            if await pg.evaluate("!!(document.getElementById('alarmEdge') && document.getElementById('alarmEdge').dataset.on)"): await asyncio.sleep(.5); await shot('2_alarm_pop'); await asyncio.sleep(2.2); await shot('3_alarm_line'); break
        await until('보상 카드 닫기', snap='4_reward_q1')
        await asyncio.sleep(2); await until('미션 시작', snap='5_mission_card_2')
        await until('네이티를 찾았다!', snap='6_naty_found_button')
        await until('보상 카드 닫기', snap='7_reward_q2_coords')
        print('errs', errs); await br.close()
asyncio.run(main())
