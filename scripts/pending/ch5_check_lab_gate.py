# 관람차 뒤 지하 연구실 입구 점검. 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_lab_gate.py <그림 폴더>
#  1) 미션 4가 열린 조(q1·q2·q4 완료): 멀리서는 입구가 안 보임(k=0) → 38 안으로 오면 열림(k=1) → 도착하면 「연구실 도착」 대사
#  2) 미션 4가 아직 안 열린 조(q1만): 가까이 가도 안 열림
import asyncio, json, re, sys, os, math
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
OUT = sys.argv[1]; FAILS = []
def check(ok, msg): print(('OK  ' if ok else 'FAIL'), msg); (None if ok else FAILS.append(msg))
async def run(pw, T, done, tag):
    br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
    ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','labgate');localStorage.setItem('void-sound','0');")
    post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
    await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
    if 'q4' in done: await post('admin/skip', {'team': T, 'mission': 'z2'}, True)
    await post('quest', {'team': T, 'dev': 'labgate', 'done': done, 'act': 2 if 'q4' in done else 1, 'tut': True, 'story': 3, 'power': True})
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400])); ev = pg.evaluate
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await ev("typeof window.__dbg!=='undefined' && typeof window.__labGate==='function' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    async def drain(n=60):
        for _ in range(n):
            if not await ev('!!__dbg.quest().vn()'):
                await asyncio.sleep(.4)
                if not await ev('!!__dbg.quest().vn()'): return
            await ev('__dbg.quest().next()'); await asyncio.sleep(.08)
    shot = lambda n: pg.screenshot(path=os.path.join(OUT, f'{tag}_{n}.png'), timeout=60000)
    await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(1.5)
    await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); await drain()
    g = await ev('__labGate()'); print(tag, 'gate', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in g.items()})
    FX, FZ = 216, -243; ux, uz = (g['x'] - FX)/76, (g['z'] - FZ)/76
    async def stand(R, wait):
        x, z = FX + ux*R, FZ + uz*R
        await ev(f"(()=>{{ __dbg.walkTo({x}, {z}); const w = __dbg.walkState(); w.yaw = Math.atan2({g['x']} - w.x, {g['z']} - w.z); w.pitch = -0.05; w.snap = true; }})()"); await asyncio.sleep(wait)
        return await ev("(()=>{ const w = __dbg.walkState(), o = __labGate(); return {k:o.k, vis:o.visible, blocked:__dbg.walkBlocked(w.x, w.z), x:Math.round(w.x), z:Math.round(w.z), vn:!!__dbg.quest().vn(), live:__dbg.quest().live && __dbg.quest().live.id}; })()")
    far = await stand(76 + 60, 2.5); print(tag, 'far', far); await shot('1_far')
    check(far['k'] == 0 and not far['vis'], f'{tag}: 60 떨어진 곳에서는 입구가 안 보인다')
    mid = await stand(76 + 30, 1.0); await shot('2_opening'); print(tag, 'opening', mid)
    await asyncio.sleep(3); mid2 = await ev('__labGate()'); await shot('3_open'); print(tag, 'after 4s', mid2['k'])
    if 'q4' in done:
        check(0 < mid['k'] < 1, f'{tag}: 다가가면 나오기 시작한다(k={mid["k"]})'); check(mid2['k'] == 1, f'{tag}: 약 4초 뒤 다 열린다')
        sp = g['door'] or g['spot']; print(tag, 'door spot', sp, 'live', mid['live'])
        await ev(f"__dbg.walkTo({sp[0]}, {sp[1]})"); await asyncio.sleep(2.5)
        vn = await ev("(()=>{ const v = __dbg.quest().vn(); return v ? (v.who || '') + ': ' + (v.text || JSON.stringify(v).slice(0, 80)) : null; })()"); print(tag, 'arrival line', vn); await shot('4_arrive')
        check(vn is not None, f'{tag}: 입구 앞에 도착하면 대사가 나온다')
        for _ in range(22): await drain(); await ev("window.__sliceWin && __sliceWin()"); await asyncio.sleep(1.2)   # 모니터 게임과 측정 장면(시뮬레이터)까지 넘긴다
        rm = await ev("(()=>{ const r = __rem(); return {mini:r.mini, walking:!!__dbg.walkState()}; })()"); print(tag, 'after the measuring scene', rm)
        check(rm['mini'] is not None, f'{tag}: 측정 뒤 잔재 수색 단계로 넘어간다')
        if rm['walking']:
            back = await stand(76 + 80, 3.5); print(tag, 'walk away during the mission', back)
            check(back['k'] == 1, f'{tag}: 미션 4를 하는 동안에는 멀어져도 열려 있다')
    else:
        check(mid2['k'] == 0, f'{tag}: 미션 4가 열리기 전에는 다가가도 안 열린다')
    check(not errs, f'{tag}: 페이지 오류 없음 {errs}')
    await br.close()
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        await run(pw, 7, ['q1', 'q2', 'q4'], 'open'); await run(pw, 6, ['q1'], 'early')
    print('FAILS', FAILS)
asyncio.run(main())
