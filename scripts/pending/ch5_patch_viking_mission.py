# 2026-11-12 (사용자 결정): 섬 미션 3을 「잔재 수색」에서 「바이킹 복구」로 바꾼다.
#   두 번째 캠퍼스 기록 → 2막 → 바이킹 공사장에서 자일로를 만남 → 조가 만든 바이킹 모델 올리기 → 바이킹이 서면 마지막 좌표.
#   이유(사용자): 바이킹은 코덱스의 공격으로 무너졌고 그 피해를 복구하는 것.
#   미션 id는 q4 그대로(서버 저장값·현황판과 맞춤). 잔재 코드는 지우지 않고 호출만 끊는다.
# 사용: python scripts/pending/ch5_patch_viking_mission.py   (한 번만)
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'vikSpot' not in s, '이미 적용됨'

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f'{c}건(기대 {n}): {old[:70]}'
    s = s.replace(old, new)

def L(who, text, **k):
    return dict(who=who, text=text, **k)

STORY = {
    'record2': [L('보이드', '이번에는 관람차 언덕 주변의 흐름을 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.'),
                L('리코', '이제 비어 있는 기록은 하나뿐이야.')],
    'act2': [L('보이드', '자일로가 바이킹 공사장에서 기다리고 있어.'),
             L('제로', '바이킹? 무너져 있던 그 놀이기구 말이지? 가 보자!')],
    'vikIntro': [L('리코', '바이킹 공사장은 정문 거리 동쪽이야. 가 보자.')],
    'vikFound': [L('자일로', '오셨군요. 여기가 바이킹이 있던 자리예요.'),
                 L('자일로', '코덱스가 도로랜드를 공격했을 때 배가 팔에서 떨어져 무너졌습니다. 전선이 끊긴 것도 그때예요.'),
                 L('리코', '전기는 돌아왔는데 바이킹만 아직 멈춰 있네요.'),
                 L('자일로', '네. 배가 부서져서 전기가 들어와도 움직일 수 없어요. 여러분이 만든 바이킹으로 다시 세워 주세요.'),
                 L('제로', '우리가 만든 바이킹을 올리면 되는 거죠? 해 볼게요!')],
    'vikDone': [L('제로', '섰다! 우리가 만든 바이킹이야!'),
                L('자일로', '잘 움직이네요. 고맙습니다. 무너졌던 바이킹이 돌아왔어요.'),
                L('보이드', '마지막 빈자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어. 카드에 띄워 둘게.'),
                L('제로', '마지막 기록을 스캔하러 가자!')],
}
story_js = ('Object.assign(STORY, ' + json.dumps(STORY, ensure_ascii=False) + ');   /* 2026-11-12 미션 3 바이킹 복구 (잔재 수색을 대신함) */\n'
            "STORY.act3 = STORY.act3.map(L=> ({...L, text:L.text.replace('시뮬레이션을 어지럽히던 잔재도 없앴고요. ', '')}));\n"
            "STORY.q3found = STORY.q3found.filter(L=> L.text.indexOf('잔재는 해체했다고') < 0 && L.text.indexOf('시뮬레이션을 믿을 수 없으니까요') < 0);\n"
            "Object.keys(STORY).forEach(k=>{ if(Array.isArray(STORY[k])) STORY[k] = STORY[k].map(L=> L && L.text && L.text.indexOf('계산을 어지럽히던 잔재도 이미 없앴어. ') >= 0 ? {...L, text:L.text.replace('계산을 어지럽히던 잔재도 이미 없앴어. ', '')} : L); });\n")
rep('const QUESTS = [\n', story_js + 'const QUESTS = [\n')

# the mission itself
rep("{id:'q4', act:2, who:[PAIR], short:'중간 점검·잔재', title:'숨겨진 잔재를 찾아라', title0:'시뮬레이션을 어지럽히는 것', hint:'관람차 언덕 아래 연구실', needs:['z2'], zones:['z3'], mini:'device', r:8, pop:'연구실 도착'},",
    "{id:'q4', act:2, who:[PAIR], short:'바이킹 복구', title:'바이킹을 다시 세워라', hint:'정문 거리 동쪽 공사장', needs:['z2'], zones:['z3'], mini:'viking', r:13, pop:'자일로 발견!'},")
rep('q4:()=>STORY.deviceIntro', 'q4:()=>STORY.vikIntro')
rep('q4:()=>STORY.deviceFound', 'q4:()=>STORY.vikFound')

# where to go: the path point nearest the viking lot; 자일로 stands a few steps inside, facing the path
rep('function questTarget(q){',
    "function vikSpot(){ if(vikSpot.p) return vikSpot.p; const b = VIK_B, R0 = b.r || 40; let best = null, bd = 1e9; for(const [px, pz] of pathSamples){ const d = Math.hypot(px - b.cx, pz - b.cz); if(d > R0 + 2 && d < bd){ bd = d; best = [px, pz]; } }\n"
    "  const p = best ? freeSpot(best[0], best[1]) : freeSpot(b.cx, b.cz + R0 + 12), dx = b.cx - p[0], dz = b.cz - p[1], D = Math.hypot(dx, dz) || 1, x = freeSpot(p[0] + dx/D*6 - dz/D*4, p[1] + dz/D*6 + dx/D*4);\n"
    "  return vikSpot.p = [p[0], p[1], Math.atan2(p[0] - x[0], p[1] - x[1]), x[0], x[1]]; }   /* [길 x, 길 z, 자일로 방향, 자일로 x, 자일로 z] */\n"
    'function questTarget(q){')
rep("q.id==='q4' ? (buildLabDoor(), LAB_DOOR) : CAVE_MOUTH", "q.id==='q4' ? vikSpot().slice(3) : CAVE_MOUTH")
rep("if(questDone(QUESTS[0])){ XYLO.position.set(XYLO_HOME[0], G, XYLO_HOME[1]); XYLO.rotation.y = XYLO_HOME[2]; } else {",
    "if(questDone(QUESTS[1]) && !questDone(QUESTS[2]) && needsBack(QUESTS[2]) && TEAM && !flowFree()){ const vs = vikSpot(); XYLO.position.set(vs[3], G, vs[4]); XYLO.rotation.y = vs[2]; }   /* mission 3: 자일로 waits at the viking site */\n"
    "  else if(questDone(QUESTS[0])){ XYLO.position.set(XYLO_HOME[0], G, XYLO_HOME[1]); XYLO.rotation.y = XYLO_HOME[2]; } else {")
rep('2:()=> [XYLO, ZERO, RICO], 3:', '2:()=> [ZERO, RICO], 3:')   # the one to find is not in the scene before
rep("following=walk&&(questLive?.id==='q4'||mini?.kind==='maze'", "following=walk&&(mini?.kind==='maze'")

# start / resume
rep("if(q.mini==='device'){mini={q,kind:'device',phase:'mid',got:[]};midCheck(q);return;}",
    "if(q.mini==='viking'){ mini = {q, kind:'viking'}; vikAsk(); return; }\n  if(q.mini==='device'){mini={q,kind:'device',phase:'mid',got:[]};midCheck(q);return;}")
rep("else if(q.mini==='device'){mini={q,kind:'device',phase:st,got:cp.got||[]};",
    "else if(q.mini==='viking'){ mini = {q, kind:'viking'}; vikAsk(); }\n  else if(q.mini==='device'){mini={q,kind:'device',phase:st,got:cp.got||[]};")
rep("const STEP_LINE = {hunt:", "const STEP_LINE = {vik:'우리 조가 만든 바이킹 모델을 올려 줘.', hunt:")

# the upload step: the mission box carries the upload button; a team whose viking is already up may go on with it
rep('miniGo.onclick=async()=>{',
    "const vikMine = ()=> LOCAL ? VIKINGS.local : VIKINGS[TEAM];\n"
    "function vikAsk(){ if(!mini || mini.kind !== 'viking') return; miniSave('vik'); const t = vikSpot().slice(3);   /* resumed far from the site: walk back first */\n"
    "  if(walk && Math.hypot(walk.x - t[0], walk.z - t[1]) > 20){ miniWalkTo(2, '바이킹을 다시 세워라', '바이킹 공사장으로 돌아가기', t, 13, vikShow); return; } vikShow(); }\n"
    "function vikShow(){ if(!mini || mini.kind !== 'viking') return; mini.phase = 'upload'; if(walk) walk.yaw = Math.atan2(VIK_B.cx - walk.x, VIK_B.cz - walk.z); vikMini(); }\n"
    "function vikMini(){ if(!mini || mini.kind !== 'viking' || mini.phase !== 'upload') return; const has = !!vikMine();\n"
    "  miniHud(2, '바이킹을 다시 세워라', has ? '우리 조의 바이킹이 섰어요' : '우리 조가 만든 바이킹 모델 올리기');\n"
    "  miniGo.textContent = VIK_BUSY ? '올리는 중' : has ? '다른 모델로 바꾸기' : '바이킹 모델 올리기'; miniGo.disabled = !!VIK_BUSY; miniDots.innerHTML = ''; miniDoneBtn.textContent = '이 바이킹으로 계속'; miniDoneBtn.hidden = !has || !!VIK_BUSY; miniBox.hidden = false; }\n"
    "async function vikWon(rise){ const cur = mini; if(!cur || cur.kind !== 'viking' || cur.phase !== 'upload') return; cur.phase = 'done'; miniBox.hidden = true; $('questHud').hidden = true; qNavHide();\n"
    "  if(walk){ walk.yaw = Math.atan2(VIK_B.cx - walk.x, VIK_B.cz - walk.z); }\n"
    "  await wait(reduce || !rise ? 500 : 4200); if(mini !== cur) return; say(STORY.vikDone, ()=>{ if(mini === cur) questComplete(cur.q); }); }\n"
    "miniGo.addEventListener('click', ()=>{ if(mini && mini.kind === 'viking' && mini.phase === 'upload' && !vn && !VIK_BUSY) vikFile.click(); });\n"
    "miniDoneBtn.addEventListener('click', ()=>{ if(mini && mini.kind === 'viking' && mini.phase === 'upload' && !vn && !VIK_BUSY && vikMine()) vikWon(false); });\n"
    "window.__vikMini = vikMini; window.__vikUp = ()=> vikWon(true); window.__vikGate = ()=> questDone(QUESTS[2]) || chainOpen(QUESTS[2]);\n"
    "window.__vikQ = ()=> ({spot:vikSpot(), xylo:[XYLO.position.x, XYLO.position.z], phase:mini && mini.kind === 'viking' ? mini.phase : null, box:!miniBox.hidden, go:miniGo.textContent, done:!miniDoneBtn.hidden, mine:!!vikMine()});\n"
    'miniGo.onclick=async()=>{')
rep("VIK_BUSY = false; vikingSync(); toast('바이킹을 다시 세웠습니다');",
    "VIK_BUSY = false; await vikingSync(); toast('바이킹을 다시 세웠습니다'); if(window.__vikUp) window.__vikUp();")
rep("function vikCard(){ const box = document.querySelector('#iIsl .vik'); if(box) box.outerHTML = vikCardHTML(); }",
    "function vikCard(){ const box = document.querySelector('#iIsl .vik'); if(box) box.outerHTML = vikCardHTML(); if(window.__vikMini) window.__vikMini(); }")
# the place card: the upload opens with mission 3 (admin devices and the no-server mode keep it open)
rep("mine = LOCAL || (TEAM > 0 && (!v || +t === TEAM));\n  let hh = '<div class=\"vik\">';",
    "gate = LOCAL || !!ADMIN_KEY || !!(window.__vikGate && window.__vikGate()), mine = gate && (LOCAL || (TEAM > 0 && (!v || +t === TEAM)));\n  let hh = '<div class=\"vik\">';")
rep("else if(!v && !TEAM && !ADMIN_KEY) hh += '<small>우리 조를 고르면 배 모델을 올릴 수 있습니다</small>';",
    "else if(!v && !TEAM && !ADMIN_KEY) hh += '<small>우리 조를 고르면 배 모델을 올릴 수 있습니다</small>';\n  else if(!v && !gate) hh += '<small>미션 3에서 다시 세울 수 있습니다</small>';")

# labels and help
rep("${mini?.kind==='loop'||mini?.kind==='maze'?4:3}", "${mini?.kind==='loop'||mini?.kind==='maze'?4:mini?.kind==='viking'?2:3}")
rep("function miniHud(step, title, hint){ ", "function miniHud(step, title, hint){ if(questLive) $('qhStep').previousSibling.textContent = `미션 ${QUESTS.indexOf(questLive) + 1} `;   /* resumed missions kept the bare 「MISSION」 label */ ")
rep("q.mini === 'loop' ? '1 / 4' : '1 / 3'", "q.mini === 'loop' ? '1 / 4' : q.mini === 'viking' ? '1 / 2' : '1 / 3'")
rep("q.id==='q4'?'선대의 잔재 해체':", "q.id==='q4'?'바이킹 복구 · 마지막 좌표 확보':")
a = s.index("if(q.id==='q4')return step==='device-return'"); b = s.index("돌려 볼 거야.';", a) + len("돌려 볼 거야.';")
s = s[:a] + "if(q.id==='q4')return step==='vik'?'우리 조가 만든 바이킹 모델을 올려 줘. 바이킹이 다시 서면 마지막 좌표를 알려 줄게.':'바이킹 공사장으로 가자. 자일로가 기다리고 있어.';" + s[b:]
rep("seen === 2 ? '시뮬레이션이 다시 맞기 시작했어. 마지막 좌표에서 남은 기록 하나를 채우자.'", "seen === 2 ? '이제 마지막 좌표로 가서 남은 기록을 채우자.'")
rep("2:[{who:'자일로',text:'제로, 리코! 관람차 앞입니다. 연구실에서 시뮬레이션을 돌려 봅시다.'},{who:'제로',text:'지금까지 모은 걸 확인하러 가자!'}],",
    "2:[{who:'자일로',text:'제로, 리코! 바이킹 공사장으로 와 주세요.'},{who:'제로',text:'가 보자!'}],")
rep('시뮬레이션을 어지럽히던 선대의 잔재는 해체했습니다.<br>', '')
rep('<p class="device-status">선대의 잔재 해체 완료 · 기록 5 / 5</p>', '<p class="device-status">기록 5 / 5</p>')

# Space 키 처리: #remDlg는 잔재를 처음 찾을 때 만들어지는 창이라 그 전에는 없다 → null.dataset 오류로 그 뒤 처리가 끊겼다
rep("const on = id => !!$(id).dataset.on, go = id => {", "const on = id => { const el = $(id); return !!(el && el.dataset.on); }, go = id => {")

assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('ok', len(s))
