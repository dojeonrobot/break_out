# 관리자 「시점 이동」 점검: 미션 2까지 간 조 태블릿이 대사 창을 띄운 채로 있을 때, 관리자 화면에서 그 조를 「미션 3 시작 전」으로 옮긴다.
# 기대: 태블릿이 새로 열리고, 서버 상태가 z1·z2 복구 + q1·q2 완료 + 2막 봄, 다시 열린 태블릿은 대사 겹침 없이 미션 3이 다음 할 일. 다시 「미션 1 시작 전」으로 되돌려도 같다.
# 사설 API 8096 + 정적 8097. 서버는 고친 ch5_void_server.py 여야 한다.
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg)
    if not ok: fails.append(msg)
async def mk(br, dev, admin):
    ctx = await br.new_context(viewport={'width': 1300, 'height': 860}); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');localStorage.setItem('void-sound','0');" + ("sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));" if admin else ''))
    pg = await ctx.new_page(); pg.errs = []; pg.loads = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)[:160])); pg.on('load', lambda: pg.loads.append(1)); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    return ctx, pg
async def ready(pg):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): return
        except Exception: pass
        await asyncio.sleep(.25)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx, tab = await mk(br, 'stg', False); rq = ctx.request
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'stg', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        await tab.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000); await ready(tab); await asyncio.sleep(4)
        await tab.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await tab.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(3)
        check(await tab.evaluate("!!__dbg.walk()"), '태블릿: 미션 2를 걷는 중')
        actx, adm = await mk(br, 'admdev', True); await adm.goto(f'{STATIC}/chapter05/index.html?admin=1', wait_until='domcontentloaded', timeout=120000); await ready(adm); await asyncio.sleep(3)
        if await adm.evaluate("document.getElementById('adminDlg').hidden"): await adm.evaluate("document.getElementById('adminBtn').click()"); await asyncio.sleep(2)
        opts = await adm.evaluate(f"[...document.querySelectorAll('[data-astage=\"{T}\"] option')].map(o=> o.textContent)"); print('  고를 수 있는 시점', len(opts) - 1)
        check(len(opts) == 13, '관리자 표에 시점 이동 고르기가 있다')
        async def move(label, zones, done, act, due):
            n0 = len(tab.loads); await adm.select_option(f'[data-astage="{T}"]', label=label); await asyncio.sleep(1.5)
            st = await (await rq.get(API + '/api/void/state')).json(); mine = [s['mission'] for s in st['subs'] if s['team'] == T]; ent = list(st['quests'].get(str(T), {}).values())[0]
            qs = sorted(k for k in ent if re.match(r'^q\d$', k)); check(sorted(mine) == zones and qs == sorted(done) and (ent.get('act') or 0) == act, f'서버: {label} → 기록 {sorted(mine)} 미션 {qs} 막 {ent.get("act") or 0}')
            for _ in range(60):
                if len(tab.loads) > n0: break
                await asyncio.sleep(.5)
            check(len(tab.loads) > n0, '태블릿이 새로 열렸다'); await ready(tab); both = 0; last = {}
            for _ in range(24):
                try:
                    last = await tab.evaluate("({void:!!document.getElementById('voidVn').dataset.on, vn:!!document.getElementById('vn').dataset.on, card:!!document.getElementById('recDone').dataset.on, tut:__dbg.tutState().step, walk:!!__dbg.walk(), due:(__dbg.quests().find(q=> q.open && !q.done) || {}).id || null, n:document.getElementById('bN').innerText})")
                    if last['void'] and last['vn']: both += 1
                except Exception: pass
                await asyncio.sleep(.5)
            print('   ', last); check(both == 0 and last.get('tut') in (-1, 99) and not last.get('walk'), '다시 열린 뒤 대사 겹침·튜토리얼·걷기 잔재 없음'); check(last.get('due') == due, f'다음 할 미션 {last.get("due")} (기대 {due})')
        await move('미션 3 시작 전', ['z1', 'z2'], ['q1', 'q2'], 2, 'q4')
        await move('미션 1 시작 전', ['z1'], [], 1, 'q1')
        check(not tab.errs and not adm.errs, f'페이지 오류 없음 {tab.errs[:1]} {adm.errs[:1]}'); await br.close(); print('FAILS', fails)
asyncio.run(main())
