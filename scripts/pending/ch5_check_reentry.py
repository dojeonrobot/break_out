# 재진입 점검: 조의 진행 단계마다 서버 상태를 심어 두고, ① 같은 태블릿으로 ② 새 태블릿으로 페이지를 새로 열었을 때 아무것도 누르지 않은 채 처음 뜨는 것을 받아 적는다.
# 사설 API 8096(CH5_ADMIN_KEY=0101, VOID_STATIC=0) + 정적 8097.  python scripts/pending/ch5_check_reentry.py [단계 번호들 예: 5,6,7]
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
STAGES = [  # (이름, 건너뛴 캠퍼스 기록, 끝낸 섬 미션, 본 막, 튜토리얼)
 ('0 처음', [], [], 0, False), ('1 튜토리얼 끝', [], [], 0, True), ('2 기록1 제출 직후(1막 전)', ['z1'], [], 0, True), ('3 1막 봄', ['z1'], [], 1, True),
 ('4 미션1 끝', ['z1'], ['q1'], 1, True), ('5 미션2 끝', ['z1'], ['q1', 'q2'], 1, True), ('6 기록2 제출 직후(2막 전)', ['z1', 'z2'], ['q1', 'q2'], 1, True), ('7 2막 봄', ['z1', 'z2'], ['q1', 'q2'], 2, True),
 ('8 미션3 끝', ['z1', 'z2'], ['q1', 'q2', 'q4'], 2, True), ('9 미션4 끝', ['z1', 'z2'], ['q1', 'q2', 'q4', 'q5'], 2, True), ('10 기록3 제출 직후(3막 전)', ['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5'], 2, True),
 ('11 3막 봄', ['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5'], 3, True), ('12 미션5 끝', ['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5', 'q3'], 3, True),
 ('13 튜토리얼 표시 없이 미션3까지(관리자 건너뛰기로 진행한 기기)', ['z1', 'z2'], ['q1', 'q2', 'q4'], 2, False)]
ONLY = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else None
SNAP = """()=>{ const on = id=> !!document.getElementById(id) && !!document.getElementById(id).dataset.on, tx = id=> (document.getElementById(id) || {}).innerText || '';
  const o = {}; if(on('voidVn')) o.void = tx('voidTxt').replace(/\\s+/g, ' ').slice(0, 70); if(on('vn')) o.vn = (tx('vnName') + ': ' + tx('vnText')).replace(/\\s+/g, ' ').slice(0, 70);
  if(on('recDone')) o.card = tx('rdT'); if(on('teamPick')) o.teamPick = 1; if(on('heroPick')) o.heroPick = 1; if(on('restoreDlg')) o.restoreDlg = 1;
  const qr = document.getElementById('qReward'); if(qr && qr.dataset.on) o.reward = qr.innerText.replace(/\\s+/g, ' ').slice(0, 60);
  const qh = document.getElementById('questHud'); if(qh && !qh.hidden) o.hud = qh.innerText.replace(/\\s+/g, ' ').slice(0, 60);
  const qp = document.getElementById('questPill'); if(qp && !qp.hidden && qp.offsetParent) o.pill = qp.innerText.replace(/\\s+/g, ' ').slice(0, 50);
  const ts = __dbg.tutState(), ss = __dbg.simState(); o.tut = ts.step; o.world = ts.world; if(ss.busy) o.actBusy = 1; if(ss.simOn) o.sim = 1; if(ss.walk) o.walk = 1; if(ss.cinema) o.cinema = 1; return o; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for si, (name, zones, done, act, tut) in enumerate(STAGES):
            if ONLY and si not in ONLY: continue
            for dev in ('deva', 'devb'):
                ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
                async def route(r):
                    q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                    await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
                await ctx.route(re.compile(r'.*/api/void/.*'), route)
                await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');localStorage.setItem('void-sound','0');")
                post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
                if dev == 'deva':   # 단계마다 처음부터 심는다. 새 태블릿(devb)은 그 상태 그대로 이어서 연다
                    await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
                    for z in zones: await post('admin/skip', {'team': T, 'mission': z}, True)
                    body = {'team': T, 'dev': 'deva', 'done': done, 'act': act}
                    if tut: body['tut'] = True
                    if done: body.update(story=3, power=True)
                    if tut or done or act: await post('quest', body)
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
                await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
                for _ in range(480):
                    try:
                        if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
                    except Exception: pass
                    await asyncio.sleep(.25)
                for _ in range(6):
                    if await pg.evaluate("!!document.getElementById('teamPick').dataset.on"): break
                    await asyncio.sleep(.5)
                picked = await pg.evaluate("(t)=>{ const tp = document.getElementById('teamPick'); if(!tp || !tp.dataset.on) return 'no popup'; const b = [...document.querySelectorAll('#tpGrid button')].find(x=> (x.textContent.match(/\\d+/) || [])[0] == t); if(!b) return 'no button'; b.click(); return 'picked'; }", T)   # 아이가 하듯 조 선택 창에서 우리 조를 누른다
                seen = [picked]
                for _ in range(28):
                    try: s = json.dumps(await pg.evaluate(SNAP), ensure_ascii=False)
                    except Exception as e: s = 'ERR ' + str(e)[:80]
                    if not seen or seen[-1] != s: seen.append(s)
                    await asyncio.sleep(.5)
                print(f"== {name} · {'같은 태블릿' if dev == 'deva' else '새 태블릿'}"); [print('   ', s) for s in seen[-4:]]
                if errs: print('    errs', errs[:2])
                sys.stdout.flush(); await ctx.close()
        await br.close()
asyncio.run(main())
