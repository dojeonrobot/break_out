# 2026-11-18 묶음 8 (사용자): 미션 카드는 「할 일(미션)」을 받는 순간에 뜬다. 누군가를 그냥 찾아가는 것은 미션이 아니다(네이티 찾기는 미로가 있으니 미션).
# 제목은 두 줄: 「무슨 일이 일어났다!」 / 「이렇게 하자!」.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
MARK = "</style></head><body>"
rep(MARK, "#missionCard h1.two{font:700 clamp(25px,3.6vw,38px)/1.28 var(--sans);letter-spacing:-.02em;text-wrap:balance}#missionCard h1 .sit{display:block;margin-bottom:12px;font:600 clamp(16px,2.1vw,22px)/1.5 var(--sans);letter-spacing:0;color:#bfd6ea}#missionCard h1 .act{display:block}\n" + MARK)

# the cards: when each is shown, what happened, what to do
rep("let MCARD = null, MCARD_R = null, MCARD_NEXT = null;",
    "/* 2026-11-18 (user): a card opens when a task is handed over, never for just walking to someone. sit = what happened, act = what to do */\n"
    "const MCARDS = {\n"
    "  q1:{sit:'바이킹이 무너지면서 섬 전체에 전기가 끊겼다!', act:'예비 배전선을 찾아 전기를 복구하자!', hint:'롤러코스터 옆 정비동', who:'xylo'},\n"
    "  q2:{sit:'전기가 한꺼번에 들어오면서 네이티가 사라졌다!', act:'정문 동쪽 길에서 네이티를 찾아내자!', hint:'정문 동쪽 길', who:'naty'},\n"
    "  q2chase:{sit:'네이티가 미로 밖으로 날아가 버렸다!', act:'놓치지 말고 끝까지 따라가자!', who:'naty'},\n"
    "  q4:{sit:'코덱스의 공격으로 바이킹이 무너져 있다!', act:'우리가 만든 바이킹으로 다시 세우자!', hint:'바이킹 공사장', who:'xylo'},\n"
    "  q5:{sit:'연구실 화면이 게임으로 뒤덮였다!', act:'게임을 끝까지 깨서 화면을 되돌리자!', who:'xylo'},\n"
    "  q5rem:{sit:'선대의 잔재가 일루아의 흐름을 어지럽히고 있다!', act:'열차를 타고 잔재를 찾아 부수자!', hint:'스카이 루프 역', who:'void'},\n"
    "  q3:{sit:'코덱스가 환원이 잘못될까 봐 망설이고 있다!', act:'알맞은 말을 골라 코덱스를 설득하자!', who:'codex'}};\n"
    "const GO_TO = {q1:['자일로에게 가기', '자일로가 기다리고 있다!'], q4:['바이킹 공사장으로 가기', '자일로가 바이킹 공사장에서 기다리고 있다!'], q5:['연구실로 가기', '자일로가 연구실에서 기다리고 있다!'], q3:['코덱스의 동굴로 가기', '코덱스가 북쪽 해안 동굴에 있다!']};   // on the way to someone: a destination, not a mission\n"
    "let MCARD = null, MCARD_R = null, MCARD_NEXT = null;")
rep("$('mcWho').src = `img/chars/${MCARD_WHO[q.id] || 'void'}.png?v=20261028c`; $('mcT').textContent = q.title0 || q.title; $('mcH').textContent = q.hint ? (q.plain ? q.hint : '위치 : ' + q.hint) : '';",
    "const C = (ov && ov.card) || MCARDS[q0.id]; $('mcWho').src = `img/chars/${(C && C.who) || MCARD_WHO[q.id] || 'void'}.png?v=20261028c`;\n"
    "  if(C){ $('mcT').className = 'two'; $('mcT').innerHTML = `<span class=\"sit\">${esc(C.sit)}</span><span class=\"act\">${esc(C.act)}</span>`; $('mcH').textContent = C.hint ? '위치 : ' + C.hint : ''; } else { $('mcT').className = ''; $('mcT').textContent = q.title0 || q.title; $('mcH').textContent = q.hint ? (q.plain ? q.hint : '위치 : ' + q.hint) : ''; }")
# walking to someone: no card (only 네이티: looking for it is the mission), and the HUD names a destination
rep("  missionCard(q).then(()=>{ if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name)); }, 500); } });\n}",
    "  const go = GO_TO[q.id]; if(go){ $('qhT').textContent = go[0]; $('qhStep').previousSibling.textContent = '이동 '; $('qhStep').textContent = ''; }\n"
    "  (go ? Promise.resolve() : missionCard(q)).then(()=>{ if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name)); }, go ? 900 : 500); } });\n}")
# the task is handed over after the giver has explained it
rep("  qPop(q.pop || '발견!'); say(QUEST_FOUND[q.id](walk.name), ()=> miniStart(q), {dark:q.dark});", "  qPop(q.pop || '발견!'); say(QUEST_FOUND[q.id](walk.name), ()=>{ if(q.id === 'q1' || q.id === 'q4') missionCard(q).then(()=> miniStart(q)); else miniStart(q); }, {dark:q.dark});")
# Naty leaves the maze: the chase is its own task
rep("function chaseIntro(q){ const w = walk; if(!w) return; mini = {q, kind:'chase', phase:'intro'};", "async function chaseIntro(q){ if(!walk) return; await missionCard(q, {card:MCARDS.q2chase}); const w = walk; if(!w) return; mini = {q, kind:'chase', phase:'intro'};")
# the lab: the game is the first task there (after Xylo's telling-off), the remnants the second
rep("  await sliceGame(ffOn() ? null : new Promise(r=> say(STORY.labGame, r))); if(ffOn())", "  await sliceGame(ffOn() ? null : new Promise(r=> say(STORY.labGame, ()=> missionCard(q).then(r)))); if(ffOn())")
rep("MCARD_NEXT = {title0:null, hint:'스카이 루프 역'}; startWalk(PAIR); }", "MCARD_NEXT = {card:MCARDS.q5rem}; startWalk(PAIR); }")
rep("await missionCard(q, {title0:null, plain:true, hint:'알맞은 말을 골라 코덱스의 믿음을 얻으세요'});", "await missionCard(q);")
# coming back to the page: a mission that was under way gets its own card; otherwise only where to go
a = s.index("  missionCard(q, {label:mid ? `MISSION ${n} · 하던 미션`"); b = s.index("\n", a)
s = s[:a] + ("  const C = !mid ? {sit:(GO_TO[q.id] || ['', '섬에서 할 일이 남아 있다!'])[1], act:(GO_TO[q.id] ? GO_TO[q.id][0].replace(/가기$/, '가자!') : MCARDS[q.id].act), who:MCARDS[q.id].who} : q.id === 'q5' && ['rail', 'hunt', 'device-return'].includes(cp.step) ? MCARDS.q5rem : q.id === 'q2' && cp.step === 'chase' ? MCARDS.q2chase : MCARDS[q.id];\n"
    "  missionCard(q, {card:C, label:mid ? `MISSION ${n} · 하던 미션` : '다음 할 일', go:mid ? '이어서 하기' : '섬으로 가기'}).then(async ()=>{ MCARD_SKIP = !mid; await goWorld('island'); await wait(300); if(!walk && !actBusy) startWalk(PAIR); }); }") + s[b:]
rep("function missionCard(q0, ov){ if(MCARD_SKIP && !ov){ MCARD_SKIP = false; return Promise.resolve(); }", "function missionCard(q0, ov){ if(MCARD_SKIP && !ov){ MCARD_SKIP = false; if(q0.id === 'q2') return Promise.resolve(); }")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
