# 2026-11-18: 처음(튜토리얼 직후)부터 엔딩 영상까지 실제 페이지를 진행시키며, 나오는 대사·카드·알림·화면 상태를 순서대로 적는다(흐름이 맞는지 사람이 읽고 확인하는 용도).
# 관리자 로그인 기기로 진행한다: 「관리자 · ○○ 건너뛰기」가 보이면 누르고, 게임은 점검 손잡이로 통과하고, 대사·카드는 Space로 넘긴다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_flow_log.py <결과 폴더> [시작 단계 번호 0~11]
import asyncio, json, sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); START = int(sys.argv[2]) if len(sys.argv) > 2 else 0; LIMIT = float(os.environ.get('LIMIT', '1500'))
SHOT_SAY = ('됐다! 우리가 만든', '잘 움직이네요')
STEP_SKIPS = ('스캔 건너뛰기', '이동', '퍼즐 풀기', '네이티를 찾았다', '바이킹 올리기', '잔재 찾기', '따라잡기', '추격')
STAGES = [([], [], 0), (['z1'], [], 0), (['z1'], [], 1), (['z1'], ['q1'], 1), (['z1'], ['q1', 'q2'], 1), (['z1', 'z2'], ['q1', 'q2'], 1), (['z1', 'z2'], ['q1', 'q2'], 2), (['z1', 'z2'], ['q1', 'q2', 'q4'], 2), (['z1', 'z2'], ['q1', 'q2', 'q4', 'q5'], 2), (['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5'], 2), (['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5'], 3), (['z1', 'z2', 'z3'], ['q1', 'q2', 'q4', 'q5', 'q3'], 3)]
SNAP = r"""()=>{ const on = id=>{ const e = document.getElementById(id); return !!e && !!e.dataset.on; }, tx = id=>{ const e = document.getElementById(id); return e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : ''; }, vis = id=>{ const e = document.getElementById(id); return !!e && !e.hidden && e.getClientRects().length > 0; };
  const a = document.getElementById('admSkip'), s = __dbg.simState(), q = __dbg.quest ? __dbg.quest() : {};
  return {vn:on('vn') ? (document.getElementById('vnName').textContent || '(해설)') + ': ' + document.getElementById('vnText').textContent : '', vnTyping:!!document.getElementById('vn').dataset.typing,
    void:on('voidVn') ? tx('voidTxt') : '', mcard:on('missionCard') ? tx('missionCard') : '', rec:on('recDone') ? tx('recDone') : '', reward:on('qReward') ? tx('qReward') : '', simDone:on('simDone') ? tx('simDone') : '', call:on('callDlg') ? tx('callDlg') : '', restore:on('restoreDlg') ? tx('restoreDlg') : '',
    choice:window.__choice ? __choice() : null, slice:window.__slice ? __slice() : null, rem:window.__remGame ? __remGame() : null, lab:window.__labRoom ? __labRoom() : null, labset:window.__labSet ? __labSet() : null, fx:window.__restoreFx ? __restoreFx() : null,
    skip:a && !a.hidden && a.getClientRects().length ? a.innerText.replace(/\s+/g, ' ') : '', hud:vis('questHud') ? tx('questHud') : '', mini:vis('miniBox') ? tx('miniBox') : '', toast:vis('toast') ? tx('toast') : '', pill:vis('questPill') ? tx('questPill') : '',
    world:__dbg.tutState().world, sim:s.simOn, lit:s.lit, walk:s.walk, busy:s.busy, cinema:!document.getElementById('cinema').hidden, live:q.live ? q.live.id : null, board:tx('board').slice(0, 80), simHud:on('simHud') || document.body.classList.contains('sim') ? tx('simHud') : '',
    dlg:[...document.querySelectorAll('[data-on]')].map(e=> e.id).filter(Boolean).join(',')}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); rq = ctx.request
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','flw');localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));sessionStorage.setItem('void-view','%d');" % T)
        post = lambda path, body, adm=False: rq.post(BASE + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'flw', 'tut': True})
        z, d, a = STAGES[START]; r = await post('admin/stage', {'team': T, 'zones': z, 'done': d, 'act': a}, True); print('stage', START, r.status)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' and '404' not in m.text and 'Failed to load' not in m.text else None)
        await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(7); log = open(os.path.join(OUT, f'flow_{START}.txt'), 'w', encoding='utf-8'); t0 = time.time(); last = {}; shots = 0; idle = 0; ne = 0
        def w(kind, text):
            line = f"[{time.time() - t0:6.1f}] {kind:<8} {text}"; log.write(line + '\n'); log.flush()
        async def shot(tag):
            nonlocal shots; shots += 1; await pg.screenshot(path=os.path.join(OUT, f'f{START}_{shots:03d}_{tag}.jpg'), type='jpeg', quality=70)
        state_key = None
        while time.time() - t0 < LIMIT:
            try: s = await pg.evaluate(SNAP)
            except Exception as e: w('ERROR', str(e)[:200]); await asyncio.sleep(1); continue
            while ne < len(errs): w('PAGEERR', errs[ne]); ne += 1
            sk = (s['world'], s['sim'], bool(s['lab'] and s['lab']['on']), bool(s['labset'] and s['labset']['on']), (s['fx'] or {}).get('phase'), s['walk'], s['live'], s['lit'])
            if sk != state_key: state_key = sk; w('STATE', f"world={s['world']} sim={s['sim']}(lit {s['lit']}) lab={sk[2]} labset={sk[3]} fx={sk[4]} walk={s['walk']} live={s['live']} | board: {s['board']}")
            for k in ('hud', 'toast', 'pill', 'simHud', 'mini'):
                if s[k] and last.get(k) != s[k]: last[k] = s[k]; w(k.upper(), s[k][:200])
                if k == 'mini' and s[k] and last.get('shotmini') != s[k]: last['shotmini'] = s[k]; await asyncio.sleep(1.2); await shot('mini')
            acted = True
            if s['cinema']: w('CINEMA', '영상 시작'); await shot('cinema'); break
            if s['mcard']: w('MCARD', s['mcard']); await asyncio.sleep(1.0); await shot('mcard'); await pg.keyboard.press('Space'); await asyncio.sleep(.5)
            elif s['choice']:
                k = await pg.evaluate("(()=>{ const q = __choice().q, c = __t_choice(q); return c; })()") if False else None
                ok = await pg.evaluate("(q=>{ try{ return window.__choiceOk ? __choiceOk(q) : 0; }catch(e){ return 0; } })", s['choice']['q']); w('CHOICE', f"{s['choice']['q']} (믿음 {s['choice']['trust']}) → {ok + 1}번"); await shot('choice') if s['choice']['trust'] == 0 else None; await pg.keyboard.press(f'Digit{ok + 1}'); await asyncio.sleep(.5)
            elif s['vn']:
                if s['vnTyping']: await pg.keyboard.press('Space'); await asyncio.sleep(.08)
                else:
                    if last.get('vn') != s['vn']: last['vn'] = s['vn']; w('SAY', s['vn'])
                    if any(k in s['vn'] for k in SHOT_SAY) and last.get('shotsay') != s['vn']: last['shotsay'] = s['vn']; await shot('say')
                    await pg.keyboard.press('Space'); await asyncio.sleep(.12)
            elif s['void']:
                if last.get('void') != s['void']: last['void'] = s['void']; w('VOID', s['void'][:240])
                await pg.keyboard.press('Space')
                await asyncio.sleep(.5)
            elif s['rec']: w('CARD', '기록 완료: ' + s['rec']); await shot('rec'); await asyncio.sleep(1.0); await pg.keyboard.press('Space'); await asyncio.sleep(.6)
            elif s['reward']:
                if last.get('reward') != s['reward']: last['reward'] = s['reward']; w('CARD', '미션 완료: ' + s['reward'][:260]); await shot('reward')
                await asyncio.sleep(.8); await pg.evaluate("(()=>{ const b = document.getElementById('qrMap'); if(b && !b.disabled) b.click(); })()"); await asyncio.sleep(.8)
            elif s['simDone']: w('CARD', '시뮬레이션: ' + s['simDone']); await pg.click('#simDoneX'); await asyncio.sleep(.6)
            elif s['call']: w('CARD', '부름: ' + s['call'][:200]); await pg.click('#callGo'); await asyncio.sleep(.6)
            elif s['slice'] and not s['slice']['done']:
                if last.get('slice') != 1: last['slice'] = 1; w('GAME', '게임 지우기 시작'); await shot('slice')
                await pg.evaluate("(()=>{ const b = document.getElementById('slTut'); if(b && !b.hidden) b.click(); else __sliceWin(); })()"); await asyncio.sleep(.7)
            elif s['rem'] and not s['rem']['done']: w('GAME', f"잔재 부수기 종류 {s['rem']['kind']}"); await asyncio.sleep(1.2); await shot(f"rem{s['rem']['kind']}"); await pg.evaluate("__remWin()"); await asyncio.sleep(1.5)
            elif s['skip'] and any(k in s['skip'] for k in STEP_SKIPS):   # only moves and puzzles: talk, scenes and whole missions are played as the child sees them
                if last.get('skip') != s['skip']: last['skip'] = s['skip']; w('SKIP', s['skip'])
                await pg.click('#admSkip'); await asyncio.sleep(1.4); await shot('after_skip')
            else:
                acted = False
                if s['skip'] and last.get('skipseen') != s['skip']: last['skipseen'] = s['skip']; w('(skip)', '누르지 않음: ' + s['skip'])
            if s['lab'] and s['lab']['on'] and last.get('lab') != s['lab']['stat']: last['lab'] = s['lab']['stat']; w('LAB', json.dumps(s['lab'], ensure_ascii=False)); await asyncio.sleep(.4); await shot('lab')
            if s['labset'] and s['labset']['on'] and last.get('labset') != (s['labset']['open'] > 0.5): last['labset'] = s['labset']['open'] > 0.5; w('LABSET', json.dumps(s['labset'])); await shot('labset')
            if s['fx'] and s['fx']['on'] and last.get('fx') != s['fx']['phase']: last['fx'] = s['fx']['phase']; w('RESTORE', json.dumps(s['fx'])); await shot('fx_' + s['fx']['phase'])
            if acted: idle = 0
            else:
                idle += 1
                if idle == 40: w('WAIT', f"20초째 멈춤: dlg={s['dlg']} busy={s['busy']} walk={s['walk']} live={s['live']} hud={s['hud'][:60]} mini={s['mini'][:60]} pill={s['pill'][:40]}"); await shot('stuck')
                if idle == 40 and s['pill']: await pg.click('#questPill'); w('ACT', '미션 알약 누름')
                elif idle == 40 and s['skip']: await pg.click('#admSkip'); w('FALLBACK', '20초 멈춰서 누름: ' + s['skip'])
                elif idle == 80 and s['skip']: await pg.click('#admSkip'); w('FALLBACK', '40초 멈춰서 누름: ' + s['skip'])
                if idle >= 120: w('STUCK', '60초 동안 진행 없음, 끝냄'); break
                await asyncio.sleep(.5)
        w('END', f'errs {errs[:5]}'); log.close(); print('done', time.time() - t0, 'shots', shots, 'errs', errs[:3]); await br.close()
asyncio.run(main())
