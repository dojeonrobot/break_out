# 2026-11-12 (사용자)
#  1) 예비 배전선 판을 크게: 440px → 화면 높이에 맞춰 최대 780px.
#  2) 관리자 건너뛰기를 단계별로: 미션 시작 → 목적지로 이동 → 퍼즐 풀기 / 추격 / 바이킹 올리기 / 잔재 자리로 이동 / 잔재 해체 ...
#     미션을 통째로 끝내는 것은 안내 상자의 「관리자 · 미션 완료」 버튼(기존)으로 남는다.
# 사용: python scripts/pending/ch5_patch_yard_admstep.py   (한 번만)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'admStep' not in s
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60]); s = s.replace(old, new)
rep('@keyframes tutSpotBob{50%{translate:0 -5px}}\n',
    '@keyframes tutSpotBob{50%{translate:0 -5px}}\n'
    '#yardDlg .in{width:min(900px,96vw);gap:14px}\n'
    '#yardDlg .board{width:min(780px,92vw,calc((100dvh - 300px)*1.25));gap:6px;padding:14px}\n'
    '#yardDlg p{font-size:17px}\n'
    '#yardDlg .board button.stn::after{width:12px;height:12px;right:7px;top:7px}\n')
rep("  if(questLive && !questDone(questLive)) return {t:`미션 ${QUESTS.indexOf(questLive) + 1} 건너뛰기`, run:()=> admSkipQuest(questLive)};",
    "  if(questLive && !questDone(questLive)) { const st = admStep(questLive); if(st === false) return null; return st || {t:`미션 ${QUESTS.indexOf(questLive) + 1} 건너뛰기`, run:()=> admSkipQuest(questLive)}; }")
rep("const todo=QUESTS.find(x=>x.act===n&&!questDone(x));if(todo)return {t:`미션 ${QUESTS.indexOf(todo)+1} 건너뛰기`,run:()=>admSkipQuest(todo)};",
    "const todo=QUESTS.find(x=>x.act===n&&!questDone(x));if(todo)return walk ? {t:`미션 ${QUESTS.indexOf(todo)+1} 건너뛰기`,run:()=>admSkipQuest(todo)} : {t:`미션 ${QUESTS.indexOf(todo)+1} 시작`, run:()=>{ if(W.id !== 'island') setWorld('island', true); if(simOn) setSim(false); setTimeout(()=> startWalk(PAIR), 400); }};")
rep("function ffFlush(){ FF_UNTIL = Date.now() + 3000;",
    "/* one step of the mission that is being walked (user, 2026-11-12): go to the place, then each game inside it; null = nothing finer, skip the mission */\n"
    "function admStep(q){ const w = walk; if(!w) return null; if(typeof PARK_WAKE !== 'undefined' && PARK_WAKE) return false;   /* the power-on scene plays out: no skip offered */ const dl = id => { const el = document.getElementById(id); return !!(el && el.dataset.on); }, go = (t, p)=> p ? {t, run:()=>{ w.x = p[0]; w.z = p[1]; }} : null;\n"
    "  if(dl('yardDlg')) return yard && yard.done ? {t:'전원 연출 보기', run:()=> $('ydContinue').click()} : {t:'배전선 퍼즐 풀기', run:()=>{ if(yard && !yard.done){ yard.tiles = yard.sol.map(r=> r.map(c=> new Set(c))); yardPaint(); } }};\n"
    "  if(dl('remDlg')) return {t:'잔재 해체 건너뛰기', run:()=>{ const G2 = REM.game; if(G2 && !G2.done){ G2.done = true; cancelAnimationFrame(G2.raf); remFinish(G2.i); } }};\n"
    "  if(dl('caveDlg') || dl('deviceDlg') || dl('labDlg')) return null;\n"
    "  if(!mini) return q.found ? null : go(q.mini === 'maze' && q.mazeEntered ? '미로 한가운데로 이동' : q.mini === 'maze' ? '미로 입구로 이동' : '목적지로 이동', questTarget(q));\n"
    "  if(mini.kind === 'chase') return chase && !chase.over ? {t:'추격 건너뛰기', run:()=>{ const e = chase.R && chase.R.pts ? chase.R.pts[chase.R.pts.length - 1] : null; if(e){ chase.x = e[0]; chase.z = e[1]; w.x = e[0] - 3; w.z = e[1] - 3; } chaseWin(); }} : null;\n"
    "  if(mini.kind === 'viking' && mini.phase === 'upload') return {t:'바이킹 올리기 건너뛰기', run:()=> vikWon(false)};\n"
    "  if(mini.kind === 'device' && mini.phase === 'hunt'){ const got = mini.got || [], i = remSpots().findIndex((sp, k)=> !got.includes(k)); if(i < 0) return null; const sp = remSpots()[i]; return Math.hypot(w.x - sp.x, w.z - sp.z) < 2 ? {t:'파내기', run:()=>{ mini.dig = 0; mini.press = false; remReveal(i); }} : go(`잔재 자리로 이동 · 남은 ${3 - got.length}`, [sp.x, sp.z]); }\n"
    "  if(mini.phase === 'walk' && mini.target && !mini.arrived) return go('목적지로 이동', mini.target);\n"
    "  return null; }\n"
    "function ffFlush(){ FF_UNTIL = Date.now() + 3000;")
P.write_bytes(s.encode('utf-8')); print('ok')
