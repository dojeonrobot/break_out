# 2026-11-24 사용자: 동굴 앞 장면 재구성
#  1) 아이들이 먼저 기록을 다 채웠다고 말함 → 코덱스 「어떻게 믿지」  2) 네이티 흔들림 연출 → 섬이 가라앉는다 → 「시뮬레이션으로는 문제없다」
#  3) 연구는 지긋지긋하다 → 따라와라(벽화) → 미션 카드 → 암전 컷으로 동굴 안 → 벽화
import json, pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')

def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:80]}')
    s = s.replace(a, b)

def L(who, text, **k):
    d = {'who': who, 'text': text}; d.update(k); return d
NAR = lambda t: {'who': '', 'text': t, 'nar': True}

found = [L('제로', '코덱스!'),
         L('코덱스', '……또 너희냐. 아직도 이 섬을 떠나지 않았군.'),
         L('리코', '저희, 비어 있던 기록을 전부 채웠어요.'),
         L('리코', '이제 일루아가 원래 어디로 흘렀는지 알아요.'),
         L('코덱스', '기록을 다 채웠다고? 그걸 내가 어떻게 믿지.'),
         L('코덱스', '이 섬에 온 사람들은 늘 그렇게 말했다. 그 말 끝에 섬은 늘 망가졌다.')]
shake = [NAR('그때 네이티가 크게 일렁인다. 붉은 빛이 흩어졌다가 겨우 다시 모인다.'),
         L('제로', '네이티! 왜 그래?'),
         L('코덱스', '일루아가 더는 버티지 못하는군.'),
         L('코덱스', '이대로 흔들리면 섬이 일루아를 붙잡지 못한다. 땅이 꺼지고, 이 섬은 바다 아래로 가라앉을 거다.'),
         L('리코', '아니에요! 그렇게 안 돼요!'),
         L('리코', '저희가 채운 기록으로 시뮬레이션을 돌려 봤어요. 원천에서 섬 끝까지 일루아의 흐름이 끊기지 않고 이어졌어요.'),
         L('제로', '원래 자리로 조금씩 돌려보내면 문제없이 돌아와요!')]
toCave = [L('코덱스', '시뮬레이션이라. ……연구라면 지긋지긋하다.'),
          L('코덱스', '그때도 시작은 연구였다. 섬을 조사하겠다던 자들이 오고 나서 섬은 급격히 나빠졌다.'),
          L('코덱스', '그들은 일루아를 제멋대로 끌어다 썼다. 섬이 버티지 못할 때까지.'),
          L('코덱스', '그래서 너희를 믿을 수 없다.'),
          L('리코', '저희는 그 사람들이랑 달라요!'),
          L('코덱스', '다른지 아닌지는 말로 알 수 없다.'),
          L('코덱스', '따라와라. 이 동굴에는 우리 선대가 그때 일을 새겨 두었다.'),
          L('코덱스', '그걸 보고도 같은 말을 할 수 있는지 보겠다.'),
          NAR('코덱스가 동굴 안으로 들어간다. 흔들리는 네이티가 그 뒤를 따른다.')]

# 1. the last q3found definition wins: replace its array
key = 'Object.assign(STORY, {"q3found": ['
i = s.rfind(key)
if i < 0: sys.exit('no q3found')
a = i + len(key) - 1; d = 0
for j in range(a, len(s)):
    if s[j] == '[': d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0: break
dump = lambda v: json.dumps(v, ensure_ascii=False)
s = s[:a] + dump(found) + ', "q3shake": ' + dump(shake) + ', "q3cave": ' + dump(toCave) + s[j + 1:]

# 2. 네이티 beside 코덱스 when he is found, unsteady while scene 2 runs
rep("qPop(q.pop || '발견!'); say(QUEST_FOUND[q.id](walk.name),",
    "qPop(q.pop || '발견!'); if(q.id === 'q3') natyBeside(); say(QUEST_FOUND[q.id](walk.name),")
helpers = ("/* 2026-11-24 (user): at the cave mouth 네이티 floats beside 코덱스, red; while 코덱스 says the Ilua cannot hold, it shakes (alarm edge, its unsteady sound) */\n"
  "function natyBeside(){ const c = codexWait(); NATY.userData.run = [c[0] + 3.2, c[1] - 2.4, 3.2, Math.atan2(-c[0], -c[1])]; NATY.userData.heal = null; NATY.userData.hold = {color:0xe05a4e, t:performance.now(), keep:true}; NATY.visible = true; }\n"
  "let NATY_SHAKE = null;\n"
  "function natyShake(on){ const el = $('alarmEdge') || (()=>{ const e = document.createElement('div'); e.id = 'alarmEdge'; e.setAttribute('aria-hidden', 'true'); document.body.appendChild(e); void e.offsetWidth; return e; })();\n"
  "  if(NATY_SHAKE){ clearInterval(NATY_SHAKE.iv); NATY.scale.setScalar(NATY_SHAKE.s0); if(NATY.userData.run) NATY.userData.run[2] = NATY_SHAKE.h0; NATY_SHAKE = null; delete el.dataset.on; }\n"
  "  if(!on) return; const r = NATY.userData.run; NATY_SHAKE = {s0:NATY.scale.x, h0:r ? r[2] : 3.2, t0:performance.now(), snd:0};\n"
  "  el.dataset.on = '1'; try{ sfx('error'); }catch(e){}\n"
  "  NATY_SHAKE.iv = setInterval(()=>{ const k = (performance.now() - NATY_SHAKE.t0)/1000, b = 0.5 + 0.5*Math.sin(k*9); NATY.scale.setScalar(NATY_SHAKE.s0*(0.72 + 0.5*b*Math.abs(Math.sin(k*2.3)))); if(NATY.userData.run) NATY.userData.run[2] = NATY_SHAKE.h0 + (Math.random() - 0.5)*0.5;\n"
  "    if(k - NATY_SHAKE.snd > 0.85){ NATY_SHAKE.snd = k; try{ sfx('natyWob'); }catch(e){} } }, 50); }\n")
rep("async function caveStory(q){", helpers + "async function caveStory(q){")

# 3. caveStory: the talk at the cave mouth, the mission card, then the cut into the cave
rep("  let room = null; const row = [RICO, ZERO, CODEX, XYLO, NATY];\n  await cut(()=>{ room = caveEnter();",
    "  let room = null; const row = [RICO, ZERO, CODEX, XYLO, NATY];\n"
    "  natyBeside(); natyShake(true); await talk(STORY.q3shake); natyShake(false); if(dead()) return;\n"
    "  await talk(STORY.q3cave); if(dead()) return;\n"
    "  await missionCard(q); if(dead()) return;\n"
    "  NATY.userData.run = null;\n"
    "  await cut(()=>{ room = caveEnter();")
rep("await talk(STORY.caveIn); if(dead()) return;\n  await missionCard(q); if(dead()) return;\n",
    "await talk(STORY.caveIn); if(dead()) return;\n")

# 4. the mission card says what the children know at that moment
rep("q3:{sit:'코덱스가 환원이 잘못될까 봐 망설이고 있다!', act:'알맞은 말을 골라 코덱스를 설득하자!', who:'codex'}",
    "q3:{sit:'코덱스가 우리를 믿지 못하고 있다!', act:'동굴 벽화를 보며 코덱스를 설득하자!', hint:'코덱스의 동굴 안', who:'codex'}")

P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
