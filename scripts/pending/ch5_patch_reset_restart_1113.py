# 2026-11-13 (사용자 캡처: 관리자 모드로 초기화하고 나면 대사가 여러 개 동시에 뜸 / 캠퍼스 건물 이름도 기본은 꺼짐)
#  원인: 초기화가 조만 다시 고르게 하고, 그 태블릿에서 진행 중이던 대사 창·막 연출(기다리는 중인 비동기 사슬)·걷기와 기기에 남은 진행 기억은 그대로 뒀다.
#        조를 다시 고르면 그 위에 튜토리얼이 시작돼 대사 창이 겹쳤다.
#  고침: 초기화가 닿으면 그 기기의 진행 기억을 지우고 페이지를 새로 연다(hardRestart). 진행 중인 연출을 확실히 끊는 방법은 이것뿐이다.
#        ① 전체 초기화 ② 「처음부터」 ③ 관리자가 그 조·그 태블릿의 진행을 지웠을 때(내 칸이 서버에서 사라짐)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
rep("function checkReset(st){",
    "function wipeLocal(){ try{ Object.keys(localStorage).filter(k=> /^void-(quest|records|seen-lit|found|mini|hero)-/.test(k)).forEach(k=> localStorage.removeItem(k)); Object.keys(sessionStorage).filter(k=> /^void-(vn|restore|simdone)-/.test(k)).forEach(k=> sessionStorage.removeItem(k)); }catch(e){} }\n"
    "/* a reset reaches this device: forget its progress and open the page afresh. A reload is the one sure way to stop a dialogue, an act or a walk that is in the middle of its awaits (user, 2026-11-13: after an admin reset several dialogues showed at once) */\n"
    "let RESTARTING = false;\n"
    "function hardRestart(dropTeam){ if(RESTARTING) return; RESTARTING = true; wipeLocal(); try{ const u = new URL(location.href); if(dropTeam) u.searchParams.delete('team'); location.replace(u.href); }catch(e){ location.reload(); } }\n"
    "function checkReset(st){")
rep("  clearLocalDemo();\n  if(!TEAM) return;\n  TEAM = 0; try{ localStorage.removeItem('void-team'); }catch(e){}",
    "  clearLocalDemo(); wipeLocal();\n  if(!TEAM) return;\n  try{ localStorage.removeItem('void-team'); }catch(e){}\n  if(!SCREEN){ hardRestart(true); return; }\n  TEAM = 0;")
rep("SQ_JSON = qj; SQUESTS = st.quests || {}; changed = true;",
    "const hadMine = !LOCAL && TEAM && !SCREEN && (()=>{ const e = myEntry(); return !!(e.tut || e.act || Object.keys(e).some(k=> QID.test(k))); })(); SQ_JSON = qj; SQUESTS = st.quests || {}; changed = true;\n"
    "    if(hadMine && !myLetter()){ hardRestart(false); return; }   /* the admin cleared this team or this tablet */")
rep("const st = await api('/team_reset', {team:TEAM, confirm:'AGAIN'}, key);   /* the server (and the password) go first: a refused reset leaves this tablet untouched */",
    "const st = await api('/team_reset', {team:TEAM, confirm:'AGAIN'}, key);   /* the server (and the password) go first: a refused reset leaves this tablet untouched */\n    hardRestart(false); return;")
rep("const LBL_ON = {erica:true, island:false};", "const LBL_ON = {erica:false, island:false};   /* 2026-11-13 (user): the campus starts without building names too, there were too many on the first screen */")
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
