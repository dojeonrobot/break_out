# 연구실 모니터 게임(아이콘 베기) 점검: 미션 4 시작 → 연구실 도착 → 대사 → 게임. 실제 마우스 끌기로 아이콘을 베어 30개를 채우고, 끝나면 시뮬레이터 장면으로 넘어가는지 본다.
# 보이드 얼굴을 베면 수가 줄어드는지도 본다. 사설 API 8096 + 정적 8097.  python scripts/pending/ch5_check_lab_slice.py [그림 폴더]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1] if len(sys.argv) > 1 else None; fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg, flush=True)
    if not ok: fails.append(msg)
async def main():
    if OUT: os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','slc');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
        for z in ('z1', 'z2'): await post('admin/skip', {'team': T, 'mission': z}, True)
        await post('quest', {'team': T, 'dev': 'slc', 'done': ['q1', 'q2', 'q4'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4); await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        said = []
        async def drain():
            for _ in range(60):
                t = await ev("document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''")
                if not t:
                    await asyncio.sleep(.4)
                    if not await ev("!!document.getElementById('vn').dataset.on"): return
                    continue
                if not said or said[-1] != t: said.append(t)
                await ev('__dbg.quest().next()'); await asyncio.sleep(.1)
        await drain(); check(await ev("__dbg.quest().live?.id") == 'q5', '미션 4가 진행 중')
        tg = await ev('__dbg.target()'); await ev("([x, z])=> __dbg.walkTo(x, z + 3)", tg)
        for _ in range(80):
            await drain()
            if await ev("!!document.getElementById('sliceDlg') && !!document.getElementById('sliceDlg').dataset.on"): break
            await asyncio.sleep(.4)
        on = await ev("!!document.getElementById('sliceDlg') && !!document.getElementById('sliceDlg').dataset.on"); check(on, '연구실 도착 뒤 모니터 게임이 뜬다')
        check(any('깔아 둔 게임' in t for t in said), '게임 전 대사가 나온다'); print('  대사', [t for t in said if '게임' in t or '아이콘' in t or '시뮬레이터를 켜' in t])
        if not on: print('FAILS', fails, errs[:2]); await br.close(); return
        box = await ev("(()=>{ const r = document.getElementById('slCv').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()"); await asyncio.sleep(1.2)
        if OUT: await pg.screenshot(path=os.path.join(OUT, 'slice_start.png'))
        # 보이드 얼굴을 한 번 벤다(수가 줄어야 함)
        bad_done = False; shots = 0; t0 = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - t0 < 150:
            st = await ev('__slice()')
            if not st or st['done']: break
            tgt = None
            for x, y, bad in st['items']:
                if 0.12 < y < 0.8 and (bad == 0 or (not bad_done and st['n'] >= 6)): tgt = (x, y, bad); break
            if not tgt: await asyncio.sleep(.05); continue
            x, y, bad = tgt; px, py = box[0] + x*box[2], box[1] + y*box[3]; n0 = st['n']
            await pg.mouse.move(px - 70, py - 50); await pg.mouse.down(); await pg.mouse.move(px, py, steps=3); await pg.mouse.move(px + 70, py + 50, steps=3); await pg.mouse.up()
            if bad:
                st2 = await ev('__slice()'); bad_done = True; check(st2 and st2['n'] < n0, f"보이드 얼굴을 베면 수가 줄어든다 ({n0} → {st2['n'] if st2 else '?'})")
                if OUT: await pg.screenshot(path=os.path.join(OUT, 'slice_void.png'))
            elif OUT and shots == 0 and n0 >= 12: shots = 1; await pg.screenshot(path=os.path.join(OUT, 'slice_mid.png'))
        el = asyncio.get_event_loop().time() - t0; st = await ev('__slice()'); print(f'  걸린 시간 {el:.0f}초', st and {'n': st['n'], 'cover': st['cover']})
        for _ in range(40):
            if not await ev("!!document.getElementById('sliceDlg').dataset.on"): break
            await asyncio.sleep(.25)
        check(not await ev("!!document.getElementById('sliceDlg').dataset.on"), '30개를 베면 게임이 닫힌다'); check(bad_done, '보이드 얼굴이 나왔다')
        said.clear()
        for _ in range(60):
            await drain()
            if await ev('__dbg.simState().simOn'): break
            await asyncio.sleep(.3)
        check(any('시뮬레이터가 보입니다' in t for t in said), '끝난 뒤 대사가 나온다'); check(await ev('__dbg.simState().simOn'), '그 뒤 시뮬레이터가 켜진다')
        if OUT: await asyncio.sleep(3); await pg.screenshot(path=os.path.join(OUT, 'slice_after.png'))
        check(not errs, f'페이지 오류 없음 {errs[:2]}'); await br.close(); print('FAILS', fails)
asyncio.run(main())
