# 2026-11-18: 회전목마(말 모양·방향) 그림과, 미션 4 연구실 장면(모니터 화면 위 대사 → 게임 설명 3단계 → 게임의 등장 범위·놓치면 목숨·게임 오버)을 본다.
# 로컬 서버 하나: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_check_batch_1118.py <그림 폴더> [horse|slice ...]
import asyncio, json, re, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
OUT = sys.argv[1]; WHAT = sys.argv[2:] or ['horse', 'slice']; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']; HOOK = "const tutWorld = goWorld;"

async def ready(pg, extra=''):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState" + extra): return
        except Exception: pass
        await asyncio.sleep(.25)

async def horse(br):
    pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src; src = src.replace(HOOK, HOOK + " window.__cap = {camera, controls, G};")
    await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    await pg.add_init_script("localStorage.setItem('void-sound','0');")
    await pg.goto(BASE + '/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000); await ready(pg, " && !!window.__cap"); await asyncio.sleep(9)
    await pg.evaluate("""()=>{ const cv = document.querySelector('#stage canvas') || document.querySelector('canvas'); const keep = new Set(); for(let p = cv; p; p = p.parentElement) keep.add(p);
      document.querySelectorAll('body *').forEach(e=>{ if(!keep.has(e) && !cv.contains(e)) e.style.setProperty('visibility', 'hidden', 'important'); }); }""")
    K = await pg.evaluate("__dbg.K"); cx, cz = 135*K, 100*K; print('K', K)
    for name, (dx, y, dz, ty) in {'horse_near': (24, 11, 24, 7), 'horse_side': (0, 9, 30, 7), 'horse_wide': (60, 40, 60, 10)}.items():
        await pg.evaluate("([x,y,z,tx,ty,tz])=>{ const c = __cap; c.controls.minDistance = 1; c.camera.position.set(x, c.G + y, z); c.controls.target.set(tx, c.G + ty, tz); c.controls.update(); c.camera.lookAt(tx, c.G + ty, tz); }", [cx + dx, y, cz + dz, cx, ty, cz])
        await asyncio.sleep(1.6); await pg.screenshot(path=f'{OUT}/{name}.jpg', type='jpeg', quality=85)
    print('horse errs', errs[:3]); await pg.close()

async def slice_(br):
    ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
    await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','slc');localStorage.setItem('void-sound','0');")
    post = lambda path, body, adm=False: rq.post(BASE + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
    await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
    for z in ('z1', 'z2'): await post('admin/skip', {'team': T, 'mission': z}, True)
    await post('quest', {'team': T, 'dev': 'slc', 'done': ['q1', 'q2', 'q4'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
    await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000); await ready(pg)
    await asyncio.sleep(8); await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
    said = []; VN = "document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''"
    SL = "!!document.getElementById('sliceDlg') && !!document.getElementById('sliceDlg').dataset.on"
    async def drain(stop_on_slice=False):
        for _ in range(80):
            if stop_on_slice and await ev(SL): return
            t = await ev(VN)
            if not t:
                await asyncio.sleep(.4)
                if not await ev("!!document.getElementById('vn').dataset.on"): return
                continue
            if not said or said[-1] != t: said.append(t)
            await ev('__dbg.quest().next()'); await asyncio.sleep(.15)
    await drain(); print('live', await ev("__dbg.quest().live?.id"))
    tg = await ev('__dbg.target()'); await ev("([x, z])=> __dbg.walkTo(x, z + 3)", tg)
    for _ in range(90):
        await drain(True)
        if await ev(SL): break
        await asyncio.sleep(.4)
    print('slice dialog while talking', await ev(SL), 'vn', bool(await ev(VN)))
    await asyncio.sleep(1.0); await pg.screenshot(path=os.path.join(OUT, 'lab_talk.png'))
    await drain(); print('lines', [t for t in said if '게임' in t or '돌려놓' in t or '시뮬레이터를 켜' in t])
    for i in range(3):
        await asyncio.sleep(1.5); print('tut', i, await ev("document.getElementById('slP').textContent + ' | ' + document.getElementById('slTut').textContent")); await pg.screenshot(path=os.path.join(OUT, f'tut_{i}.png'))
        if i < 2: await pg.click('#slTut')
        else: await pg.keyboard.press('Space')
    xs, ys, lives = [], [], []; fail = None
    for i in range(140):
        st = await ev('__slice()')
        if not st: break
        for x, y, b in st['items']:
            if 0 <= y <= 1 and 0 <= x <= 1: xs.append(x); ys.append(y)
        lives.append(st['life'])
        if i == 30: await pg.screenshot(path=os.path.join(OUT, 'slice_play.png'))
        if st.get('failed'): fail = await ev("document.getElementById('slWhy').textContent"); await pg.screenshot(path=os.path.join(OUT, 'slice_fail.png')); break
        await asyncio.sleep(.1)
    if xs: print('items x', round(min(xs), 2), round(max(xs), 2), 'y', round(min(ys), 2), round(max(ys), 2), 'upper half share', round(sum(1 for y in ys if y < .5)/len(ys), 2), 'n', len(xs))
    print('lives seen', sorted(set(lives), reverse=True), 'fail text', fail)
    await pg.click('#slRetry') if fail else None; await asyncio.sleep(2); await ev('__sliceWin()'); await asyncio.sleep(2.5); await drain()
    print('after game: slice on', await ev(SL), 'sim', (await ev('__dbg.simState()'))['simOn'])
    for _ in range(60):
        await drain()
        if await ev("!!document.getElementById('missionCard') && !!document.getElementById('missionCard').dataset.on"): break
        await asyncio.sleep(.5)
    print('mission card after lab', await ev("(()=>{ const c = document.getElementById('missionCard'); return c && c.dataset.on ? c.innerText.replace(/\\s+/g, ' ') : null; })()"), '(자동 점검에서는 카드가 뜨지 않을 수 있음)')
    # 2026-11-18: 걷는 중 관리자 버튼, 연구실로 돌아온 뒤(잔재 셋을 부순 것으로 두고) 노이즈가 사라지고 다시 계산하고 마지막 위치를 알려 주는 장면
    await asyncio.sleep(2); await drain(); await pg.screenshot(path=os.path.join(OUT, 'walk_admin.png'))
    print('admin button while walking', await ev("(()=>{ const b = document.getElementById('adminBtn'), r = b.getBoundingClientRect(); return {shown:getComputedStyle(b).display !== 'none', x:Math.round(r.left), y:Math.round(r.top), walk:document.body.classList.contains('walk')}; })()"))
    await ev("(()=>{ const f = __t['()=>{ mini.got = [0, 1, 2]; remRerun(); }']; f(); })()")
    seen = set()
    for i in range(140):
        st = await ev("__labRoom()"); t = await ev(VN)
        if st and st['on']:
            key = ('noise' if st['noise'] else 'ping' if st['ping'] else 'calm') + '|' + st['stat']
            if key not in seen: seen.add(key); print('  lab', st, '|', t[:40]); await asyncio.sleep(.5); await pg.screenshot(path=os.path.join(OUT, f'rerun_{len(seen)}.png'))
        if t:
            if not said or said[-1] != t: said.append(t)
            await ev('__dbg.quest().next()'); await asyncio.sleep(.2)
        if await ev("!!document.getElementById('qReward').dataset.on"): break
        await asyncio.sleep(.35)
    print('reward', await ev("(()=>{ const c = document.getElementById('qReward'); return c.dataset.on ? c.innerText.replace(/\s+/g, ' ').slice(0, 160) : null; })()"))
    print('rerun lines', [t for t in said if '노이즈' in t or '관람차 근처' in t or '흔들리지' in t])
    print('slice errs', errs[:3]); await ctx.close()

async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        if 'horse' in WHAT: await horse(br)
        if 'slice' in WHAT: await slice_(br)
        await br.close()
asyncio.run(main())
