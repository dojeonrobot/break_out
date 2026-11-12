# 2026-11-12 (사용자 설계): 바이킹 복구 뒤에 관람차 아래 연구실 → 측정 → 선대 장치(잔재) 제거 → 마지막 스캔 →
#   연구실로 돌아와 시뮬레이션 가동(코덱스 문양과 같은 흐름) → 코덱스 동굴.
#   미션 순서: q1 전원 · q2 네이티 · q4 바이킹(미션 3) · q5 잔재(미션 4, 새 id) · q3 동굴(미션 5).
#   ch5_patch_viking_mission.py 를 적용한 파일 위에 한 번만 돌린다.
import json, pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'vikSpot' in s and 'nextIsl' not in s, '바이킹 패치가 먼저이고, 이 패치는 한 번만'

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f'{c}건(기대 {n}): {old[:70]}'
    s = s.replace(old, new)

def L(who, text, **k):
    return dict(who=who, text=text, **k)

# the remnant lines taken out by the viking patch come back (the remnant mission is in the flow again)
a = s.index("STORY.act3 = STORY.act3.map(L=> ({...L, text:L.text.replace('시뮬레이션을 어지럽히던"); b = s.index('const QUESTS = [\n')
s = s[:a] + s[b:]
rep('다섯 기록으로 원래 자리를 확인했습니다.<br>원천에서', '다섯 기록으로 원래 자리를 확인했습니다.<br>시뮬레이션을 어지럽히던 선대의 잔재는 해체했습니다.<br>원천에서')
rep('<p class="device-status">기록 5 / 5</p>', '<p class="device-status">선대의 잔재 해체 완료 · 기록 5 / 5</p>')
rep("seen === 2 ? '이제 마지막 좌표로 가서 남은 기록을 채우자.'", "seen === 2 ? '시뮬레이션이 다시 맞기 시작했어. 마지막 좌표에서 남은 기록 하나를 채우자.'")

STORY = {
    'vikDone': [L('제로', '섰다! 우리가 만든 바이킹이야!'),
                L('자일로', '잘 움직이네요. 고맙습니다. 무너졌던 바이킹이 돌아왔어요.'),
                L('자일로', '이제 관람차 아래 연구실로 갑시다. 지금까지 모은 기록으로 일루아의 흐름을 측정해 볼 거예요.'),
                L('제로', '좋아요. 가요!')],
    'deviceFound': [L('자일로', '오셨군요. 지금까지 모은 기록으로 일루아의 흐름을 측정해 보죠.')],
    'act3pre': [L('자일로', '마지막 기록까지 들어왔군요. 수고했어요.'),
                L('제로', '다섯 개를 전부 채웠어요!'),
                L('자일로', '이제 일루아의 흐름을 완벽하게 복원할 수 있어요. 시뮬레이션을 가동해 봅시다.')],
    'record3': [L('보이드', '사파리 주변의 흐름도 확인했어. 원천에서 나온 일루아가 사파리 아래로 이어지고 있었구나.'),
                L('보이드', '이걸로 누락됐던 다섯 기록을 모두 채웠어. 원천에서 다섯 기록의 자리까지 전부 이어졌어.'),
                L('제로', '잠깐…… 이 모양, 코덱스 문양이잖아?'),
                L('리코', '정말이야. 코덱스한테도 보여 줘야겠어.')],
}
story_js = ('Object.assign(STORY, ' + json.dumps(STORY, ensure_ascii=False) + ');   /* 2026-11-12 바이킹 → 연구실 측정·잔재 → 마지막 스캔 → 연구실에서 문양 시뮬레이션 */\n'
            "STORY.act3 = [{who:'자일로', text:'흐름은 모두 찾았어요. 이제 환원만 남았습니다.'}, ...STORY.act3.slice(4)];   /* the first lines moved before the simulation (act3pre) */\n"
            "STORY.ending = STORY.ending.filter(L=> L.text.indexOf('이 모양, 코덱스 문양이잖아') < 0);   /* the glyph is found in act 3 now; in the ending 코덱스 sees it for the first time */\n")
rep('const QUESTS = [\n', story_js + 'const QUESTS = [\n')

# missions: the viking no longer gives the coordinate; the remnant mission (new id q5) follows it without a campus record in between
rep("needs:['z2'], zones:['z3'], mini:'viking', r:13, pop:'자일로 발견!'},",
    "needs:['z2'], zones:[], mini:'viking', r:13, pop:'자일로 발견!'},\n"
    "  {id:'q5', act:2, who:[PAIR], short:'측정·잔재', title:'숨겨진 잔재를 찾아라', title0:'일루아의 흐름을 가리는 것', hint:'관람차 언덕 아래 연구실', needs:['z2'], zones:['z3'], mini:'device', r:8, pop:'연구실 도착'},")
rep('q4:()=>STORY.vikIntro', 'q4:()=>STORY.vikIntro,q5:()=>STORY.deviceIntro')
rep('q4:()=>STORY.vikFound', 'q4:()=>STORY.vikFound,q5:()=>STORY.deviceFound')
rep("q.id==='q4' ? vikSpot().slice(3) : CAVE_MOUTH", "q.id==='q4' ? vikSpot().slice(3) : q.id==='q5' ? (buildLabDoor(), LAB_DOOR) : CAVE_MOUTH")
rep("following=walk&&(mini?.kind==='maze'", "following=walk&&(questLive?.id==='q5'||mini?.kind==='maze'")
rep("return ['q1', 'q2', 'q4', 'q3'].filter(", "return ['q1', 'q2', 'q4', 'q5', 'q3'].filter(")
rep("QDONE.has('q4')?3:mini?.kind==='device'", "QDONE.has('q5')?3:mini?.kind==='device'")
rep("q.id==='q4' ? '두 번째 캠퍼스 기록을 찾은 뒤' :", "q.id==='q4' ? '두 번째 캠퍼스 기록을 찾은 뒤' : q.id==='q5' ? '바이킹을 다시 세운 뒤' :")

# reward card: a mission followed by another island mission (q1 → q2, q4 → q5) goes straight on
rep("q.id==='q4'?'바이킹 복구 · 마지막 좌표 확보':", "q.id==='q4'?'바이킹 복구':q.id==='q5'?'선대의 잔재 해체':")
rep("q4:{card:{who:'자일로',img:'xylo_talk',text:'마지막 캠퍼스 좌표입니다. 서둘러 주세요.'}}};",
    "q4:{card:{who:'자일로',img:'xylo_talk',text:'관람차 아래 연구실에서 만납시다.'}},\n q5:{card:{who:'자일로',img:'xylo_talk',text:'마지막 캠퍼스 좌표입니다. 서둘러 주세요.'}}};")
rep('function rewardWaitTick(){', "const nextIsl = q => { const n = q && QUESTS[QUESTS.indexOf(q) + 1]; return n && !q.zones.length && n.act === q.act ? n : null; };\nfunction rewardWaitTick(){")
rep("(q.id==='q1'?'미션 2 · 네이티를 찾아라':'다음 캠퍼스 기록 보기')", "(nextIsl(q)?`미션 ${QUESTS.indexOf(q)+2} · ${nextIsl(q).title}`:'다음 캠퍼스 기록 보기')")
rep("stopWalk();if(id==='q1'){", "stopWalk();if(nextIsl(QUESTS.find(x=>x.id===id))){")

# the void's 「지금 할 일」
rep("if(q.id==='q4')return step==='vik'?'우리 조가 만든 바이킹 모델을 올려 줘. 바이킹이 다시 서면 마지막 좌표를 알려 줄게.':",
    "if(q.id==='q5')return step==='device-return'?'잔재 세 개를 모두 없앴어. 연구실로 돌아가서 시뮬레이션을 다시 돌려 보자.':step==='hunt'?`내 탐지 소리가 빨라지는 쪽으로 가 봐. 잔재는 눈에 안 띄게 숨겨져 있어. 지금 ${3-((m?.got||cp?.got||[]).length)}개 남았어.`:'관람차 아래 연구실로 가자. 지금까지 모은 기록으로 일루아의 흐름을 측정해 볼 거야.';\n"
    " if(q.id==='q4')return step==='vik'?'우리 조가 만든 바이킹 모델을 올려 줘.':")

# act 3: back at the lab under the wheel → 「시뮬레이션을 가동해 봅시다」 → the whole glyph → on to the cave
rep("const ACT_CAST = {", "const ACT_STAGE = {1:'dl-harmonia', 2:'dl-ferris', 3:'dl-ferris'};   /* act 3 is played by the lab under the wheel (user, 2026-11-12) */\nconst ACT_CAST = {")
rep('stageAt(ACT_ZONE[n], ACT_CAST[n]())', 'stageAt(ACT_STAGE[n], ACT_CAST[n]())', 2)
rep("  if(!simOn) setSim(true); SIM_REVEAL_T = null; await wait(reduce ? 300 : 1900);",
    "  if(n === 3){ stageAt(ACT_STAGE[3], ACT_CAST[3]()); await wait(900); await new Promise(r=> say(STORY.act3pre, r)); STAGED = false; controls.minDistance = 40; await wait(250); }\n"
    "  if(!simOn) setSim(true); SIM_REVEAL_T = null; await wait(reduce ? 300 : 1900);")
rep("3:[{who:'자일로',text:'마지막 기록이 들어왔군요. 사파리 앞에서 만납시다.'}", "3:[{who:'자일로',text:'마지막 기록이 들어왔군요. 관람차 아래 연구실로 와 주세요.'}")

assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('ok', len(s))
