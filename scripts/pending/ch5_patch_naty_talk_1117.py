# 2026-11-17 사용자: 미로 한가운데에 갔는데 도착 표시도 네이티도 없었다 / 네이티에게는 Space(태블릿은 버튼)로 말을 건다. 한 번만 적용.
#  원인: 네이티를 미로에 세우는 줄이 questApply 안에서 「대사·장면 중이면 돌아가기」 뒤에 있어, 미션 1을 끝내고 새로 열지 않은 채 이어 가면 실행되지 않았다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

rep("function questApply(){ try{ flowLockUI();",
    "function questApply(){ try{ NATY.userData.park = (questDone(QUESTS[0]) && !questDone(QUESTS[1]) && TEAM && !flowFree()) ? [NATY_HIDE[0], NATY_HIDE[1], G + 2.6] : null; }catch(e){}   /* before the early return below: a team that went straight on from mission 1 found the maze empty (2026-11-17) */\n  try{ flowLockUI();")
# 말 걸기: 한가운데 칸에 서면 버튼(Space)이 뜨고, 눌러야 대사가 시작된다
rep("  if(q.mini === 'maze' && !mazeHeart(walk.x, walk.z)) return;   // through a hedge from the next corridor does not count (user, 2026-11-02)\n  q.found = true; miniSave('found');",
    "  if(q.mini === 'maze' && !mazeHeart(walk.x, walk.z)){ natyAsk(q, false); return; }   // through a hedge from the next corridor does not count (user, 2026-11-02)\n"
    "  if(q.mini === 'maze' && !q.talk){ natyAsk(q, true); return; }   /* the child speaks to 네이티: Space, or the button on a tablet (user, 2026-11-17) */\n"
    "  q.found = true; miniSave('found');")
rep("function questTick(){\n  const q = questLive; if(!q || !walk || vn || q.found || mini) return;\n  if(q.mini==='maze'&&q.mazeEntered)mazeGuide(walk,performance.now());\n  const [tx, tz] = questTarget(q); if(Math.hypot(walk.x - tx, walk.z - tz) > q.r) return;",
    "function natyAsk(q, on){ if(!!q.ask === on) return; q.ask = on; if(on){ miniGo.textContent = '말 걸기'; miniGo.disabled = false; miniGo.classList.remove('hot'); miniDoneBtn.hidden = true; miniDots.innerHTML = ''; miniBox.hidden = false; $('qhHint').textContent = matchMedia('(pointer:coarse)').matches ? '「말 걸기」를 눌러요' : 'Space를 눌러 말을 걸어요'; sfx('open'); } else { miniBox.hidden = true; $('qhHint').textContent = '붉은 화살표가 가리키는 곳까지 가기'; } }\n"
    "function natyTalk(){ const q = questLive; if(!q || !q.ask || q.found || mini || vn || !walk) return false; q.ask = false; q.talk = true; miniBox.hidden = true; sfx('tap'); questTick(); return true; }\n"
    "addEventListener('keydown', e=>{ if(e.code !== 'Space' || e.repeat || !questLive || !questLive.ask) return; if(e.target.matches && e.target.matches('input,textarea,select')) return; if(natyTalk()){ e.preventDefault(); e.stopImmediatePropagation(); } }, true);\n"
    "function questTick(){\n  const q = questLive; if(!q || !walk || vn || q.found || mini) return;\n  if(q.mini==='maze'&&q.mazeEntered)mazeGuide(walk,performance.now());\n  const [tx, tz] = questTarget(q); if(Math.hypot(walk.x - tx, walk.z - tz) > q.r){ if(q.ask) natyAsk(q, false); return; }")
rep("q.mazeEntered=false;delete q.cellD;", "q.mazeEntered=false;delete q.cellD;q.ask=false;q.talk=false;")
rep("const miniBox = $('miniBox'), miniGo = $('miniGo'), miniDoneBtn = $('miniDone'), miniDots = $('miniDots');", "const miniBox = $('miniBox'), miniGo = $('miniGo'), miniDoneBtn = $('miniDone'), miniDots = $('miniDots');\nminiGo.addEventListener('click', ()=>{ natyTalk(); });")
rep("  if(!mini) return q.found ? null : go(", "  if(!mini && q.ask) return {t:'말 걸기', run:()=> natyTalk()};\n  if(!mini) return q.found ? null : go(")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('patched', len(s))
