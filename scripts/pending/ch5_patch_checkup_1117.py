# 2026-11-17 전체 점검에서 찾은 확실한 결함 묶음 (관리자 제어·대사 대기·터치). 한 번만 적용. 앵커가 하나가 아니면 멈춘다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
n0 = len(s)
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# 1. 관리자 표·현황판: 섬 기록 둘째 칸이 q2를 찾아 비어 있었다(지금 관람차는 q5) → 80%에서 멈춤
rep("return [c('z1'), by('q1'), c('z2'), by('q2'), c('z3'),", "return [c('z1'), by('q1'), c('z2'), by('q5') || by('q2'), c('z3'),")
# 2. 태블릿 미션 완료 되돌리기에 확인 창
rep("else { const d = new Set(devQuests(team, l)); if(on === '1'){",
    "else { if(on !== '1' && !confirm(`${team}조-${l} 태블릿의 섬 미션 완료를 되돌립니다.\\n그 태블릿은 이 미션부터 다시 하게 됩니다.`)) return; const d = new Set(devQuests(team, l)); if(on === '1'){")
# 3. 시점 이동 확인 창에 지워지는 것 알림
rep("조 태블릿은 15초 안에 새로 열립니다.`)) return;", "조 태블릿은 15초 안에 새로 열립니다.\\n앞 시점으로 되돌리면 그 뒤에 낸 스캔 제출과 바이킹 모델은 지워집니다.`)) return;")
# 4. 잔재 부수기 중에는 「잔재 부수기 건너뛰기」, 미션을 통째로 치울 때 부수기 루프도 끝냄
rep("function admStep(q){ const w = walk; if(!w) return null;",
    "function admStep(q){ { let G2 = null; try{ G2 = REM.game; }catch(e){} if(G2 && !G2.done) return {t:'잔재 부수기 건너뛰기', run:()=>{ if(!G2.done){ G2.done = true; remFinish(G2.i); } }}; } const w = walk; if(!w) return null;")
rep("if(ride) rideEnd(false); mini = null;", "if(ride) rideEnd(false); mini = null; try{ if(REM.game){ REM.game.done = true; REM.game = null; } }catch(e){}")
# 5. ?admin=1 로 연 운영 기기는 30분 자동 해제에서 뺌(조 태블릿만)
rep("if(ADMIN_KEY && TEAM){ let at = 0;", "if(ADMIN_KEY && TEAM && QS.get('admin') !== '1'){ let at = 0;")
# 6. 넘겨야 하는 보이드 대사(voidAsk)가 떠 있을 때 시간 제한 대사가 덮어쓰면 막이 멈췄다 → 그동안은 덮어쓰지 않음
rep("if(tutStep >= 0 && tutStep < 99) return; voidShow(text, pose, ms); }", "if(tutStep >= 0 && tutStep < 99) return; if(voidWait) return; voidShow(text, pose, ms); }")
# 7. 막 연출 중 화면을 탭해도 장면 카메라 이동이 끊기지 않게
rep("down=[e.clientX,e.clientY]; fly=null; });", "down=[e.clientX,e.clientY]; if(!(actBusy || STAGED)) fly=null; });")
# 8. 대사·보상 카드가 떠 있는 동안에는 막 연출을 시작하지 않고 잠시 뒤 다시 본다
rep("typeof MI === 'undefined' || intro || document.body.classList.contains('admin')) return; if(!tutDone() || (tutStep >= 0 && tutStep < 99)) return;\n  const seen = actSeen();",
    "typeof MI === 'undefined' || intro || document.body.classList.contains('admin')) return; if(!tutDone() || (tutStep >= 0 && tutStep < 99)) return;\n  if(vn || $('voidVn').dataset.on || qRewardEl.dataset.on){ clearTimeout(actCheck.t); actCheck.t = setTimeout(actCheck, 1200); return; }\n  const seen = actSeen();")
# 9. 아이콘 베기: 첫 손가락만 받는다(두 손가락 사이가 이어져 보이드 얼굴까지 베이던 것)
rep("const move = e=>{ if(!S.down || S.done) return;", "const move = e=>{ if(!S.down || S.done || (S.pid != null && e.pointerId !== S.pid)) return;")
rep("const dn = e=>{ e.preventDefault(); S.down = true;", "const dn = e=>{ e.preventDefault(); if(S.down && S.pid != null && S.pid !== e.pointerId) return; S.pid = e.pointerId; S.down = true;")
rep("up = ()=>{ S.down = false; };", "up = e=>{ if(e && S.pid != null && e.pointerId != null && e.pointerId !== S.pid) return; S.down = false; S.pid = null; };")
# 10. 터치 기기: 페이지 확대·당겨서 새로고침·길게 눌러 뜨는 메뉴·글자 선택을 막는다
rep('<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">', '<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">')
CSS = ("html,body{overscroll-behavior:none;touch-action:pan-x pan-y}#voidVn img{pointer-events:none;-webkit-user-drag:none}"
       "@media (pointer:coarse){body{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}input,textarea{-webkit-user-select:text;user-select:text}}")
rep("</style></head><body>", CSS + "</style></head><body>")
JS = ("/* touch helpers (2026-11-17 checkup): no long-press menu, a second finger's tap still presses buttons while the pad is held, and the tap that closed a dialogue does not press what appears under it */\n"
      "{ const COARSE = matchMedia('(pointer:coarse)').matches; let SYN = null;\n"
      "  document.addEventListener('contextmenu', e=>{ if(COARSE && !(e.target.closest && e.target.closest('input,textarea,a'))) e.preventDefault(); });\n"
      "  document.addEventListener('pointerup', e=>{ if(e.isPrimary || e.pointerType !== 'touch' || !e.target.closest) return; const b = e.target.closest('button') || e.target.closest('#vn,#voidVn,#recDone'); if(!b || b.disabled) return; SYN = {t:performance.now(), el:b}; b.click(); }, true);\n"
      "  document.addEventListener('click', e=>{ if(!e.isTrusted || !e.target.closest) return; const now = performance.now();\n"
      "    if(SYN && now - SYN.t < 500 && (SYN.el === e.target || SYN.el.contains(e.target))){ e.stopPropagation(); e.preventDefault(); return; }\n"
      "    if(e.pointerType === 'touch' && now - VN_CLOSED < 350 && e.target.closest('button') && !e.target.closest('#vn,#voidVn,#admSkip,#adminDlg')){ e.stopPropagation(); e.preventDefault(); } }, true); }\n")
rep("$('admSkip').onclick = e=>{ e.stopPropagation(); e.preventDefault(); const w = admSkipWhat();", JS + "$('admSkip').onclick = e=>{ e.stopPropagation(); e.preventDefault(); const w = admSkipWhat();")
# 11. 동굴(미션 5)을 끝내고 환원 전인 태블릿을 다시 열면 섬 버튼이 잠겨 있었다 → 잠그지 않음
rep("function stepWorld(){ if(flowFree() || !TEAM || AUX ||", "function stepWorld(){ if(flowFree() || QDONE.has('q3') || !TEAM || AUX ||")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('patched', n0, '->', len(s))
