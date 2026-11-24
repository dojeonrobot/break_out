# 2026-11-24 사용자 실기 (코덱스 구간 점검):
#  1) 「코덱스 문양」 → 「코덱스 가문이 쓰는 문양」(대사와 그 문장을 찾는 코드 세 곳)
#  2) 복구 연출이 끝나기 전에 넘어감 → arriveShow가 연출 사슬이 다 끝날 때까지 기다림(마지막 단계 시작이 아니라)
#  3) 동굴 앞에서 코덱스를 찾았을 때 엉뚱한 곳을 비춤 → 동굴 입구가 코덱스 뒤로 보이는 자리에서 코덱스를 봄
#  4) 틀린 선택지를 골라도 환원됨 → 하나라도 틀리면 「설득 실패」 뒤 첫 벽화부터 다시(네 문 모두 맞혀야 함)
#  5) 벽화 대사가 스토리와 안 맞음(챕터 4에서 코덱스가 보여 준 과거로 아이들은 토네이도·원류민·약속을 이미 앎) → 벽화 1·2는 「코덱스가 보여 준 그 장면」으로 알아보는 대사
import pathlib, sys, json
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

# 1. wording
rep('"잠깐…… 이 모양, 코덱스 문양이잖아?"', '"잠깐…… 이 모양, 코덱스 가문이 쓰는 문양이잖아?"')
rep("STORY.ending = STORY.ending.filter(L=> L.text.indexOf('이 모양, 코덱스 문양이잖아') < 0);", "STORY.ending = STORY.ending.filter(L=> L.text.indexOf('이 모양, 코덱스') < 0 || L.text.indexOf('이잖아') < 0);")
rep("gi = L3.findIndex(L=> L.text.indexOf('코덱스 문양이잖아') >= 0);", "gi = L3.findIndex(L=> L.text.indexOf('문양이잖아') >= 0);")
rep('"코덱스, 보세요. 이 모양이 코덱스의 문양이에요!"', '"코덱스, 보세요. 이 모양이 코덱스 가문이 쓰는 문양이에요!"')

# 2. wait for the whole chain
rep("const dark = !parkPowerOn(), over = c=> !c || (dark ? false : last(c));", "const dark = !parkPowerOn(), over = c=> !c || c.dead;   /* the whole chain, the 일루아 settling included (user, 2026-11-24: 연출 끝나기도 전에 넘김) */")
rep("while(R.chain && !over(R.chain) && Date.now() - t0 < 16000)", "while(R.chain && !over(R.chain) && Date.now() - t0 < 20000)")

# 3. the cave mouth in view behind Codex
rep("    tg.rotation.y = Math.atan2(walk.x - gx, walk.z - gz); walk.yaw = Math.atan2(gx - walk.x, gz - walk.z); }   // the one found turns to the walker",
    "    if(q.id === 'q3'){ const dx2 = gx - CAVE_MOUTH[0], dz2 = gz - CAVE_MOUTH[1], L2 = Math.hypot(dx2, dz2) || 1; let px = gx + dx2/L2*11, pz = gz + dz2/L2*11; if(walkBlocked(px, pz)) [px, pz] = freeSpot(px, pz); walk.x = px; walk.z = pz; walk.snap = true; walk.imx = walk.imz = 0; }   /* the cave behind 코덱스 (user, 2026-11-24) */\n"
    "    tg.rotation.y = Math.atan2(walk.x - gx, walk.z - gz); walk.yaw = Math.atan2(gx - walk.x, gz - walk.z); }   // the one found turns to the walker")
rep("walk.pitch = q.mini === 'maze' ? 0.2 : q.id === 'q5' ? -0.16 : -0.05;", "walk.pitch = q.mini === 'maze' ? 0.2 : q.id === 'q5' ? -0.16 : q.id === 'q3' ? 0.06 : -0.05;")

# 4. one wrong answer fails the persuasion; start again from the first mural
old_loop_start = "  let trust = 0, round = 0; const ask = async i=>{"
rep(old_loop_start, "  let trust = 0, round = 0, failed = false; const ask = async i=>{")
rep("const o = c.opts[k]; if(o.ok){ trust++; sfx('sparkle'); } else sfx('error');", "const o = c.opts[k]; if(o.ok){ trust++; sfx('sparkle'); } else { failed = true; sfx('error'); }")
rep("    await talk(after); if(dead()) return; await ask(i); if(dead()) return; }",
    "    await talk(after); if(dead()) return; await ask(i); if(dead()) return; if(failed) break; }")
rep("  while(trust < CAVE_NEED){ round++; await talk([{who:'코덱스', img:'codex_dark', text:'……아직은 너희를 믿기 어렵다.'}, {who:'보이드', text:'벽화를 다시 보면서 코덱스의 마음을 생각해 보자.'}]); if(dead()) return; trust = 0;\n"
    "    for(let i = 0; i < CAVE_CHOICE.length; i++){ await cut(()=>{ room.place(i, row); room.zoom(i); }); if(dead()) return; await wait(reduce ? 200 : 900); if(dead()) return; await ask(i); if(dead()) return; } }",
    "  while(failed){ round++; qPop('설득 실패!'); await talk([{who:'코덱스', img:'codex_dark', text:'……됐다. 역시 너희도 다르지 않군.'}, {who:'', nar:true, text:'코덱스가 등을 돌린다. 설득에 실패했다.'}, {who:'보이드', text:'처음 벽화부터 다시 보자. 코덱스가 무엇을 두려워하는지 생각하면서.'}]); if(dead()) return; trust = 0; failed = false;\n"
    "    for(let i = 0; i < CAVE_CHOICE.length; i++){ await cut(()=>{ room.place(i, row); room.zoom(i); }); if(dead()) return; await wait(reduce ? 200 : 900); if(dead()) return; await ask(i); if(dead()) return; if(failed) break; } }")
rep("const CAVE_NEED = 3;", "const CAVE_NEED = 4;   /* every answer must be right; one wrong answer starts the walls over (user, 2026-11-24) */")

# 5. murals 1 and 2: the children recognise what 코덱스 showed them (ch.4: the tornado, the 원류민, the elder's promise)
def setStory(key, lines):
    global s
    k = f'"{key}": ['
    i = s.rfind(k)
    if i < 0: sys.exit('no ' + key)
    a = i + len(k) - 1; d = 0
    for j in range(a, len(s)):
        if s[j] == '[': d += 1
        elif s[j] == ']':
            d -= 1
            if d == 0: break
    s = s[:a] + json.dumps(lines, ensure_ascii=False) + s[j + 1:]
L = lambda who, text: {'who': who, 'text': text}
setStory('mural1', [L('제로', '이거…… 코덱스가 보여 줬던 그 장면이야. 토네이도에 휩쓸려서 섬에 왔던 날.'),
                    L('리코', '쓰러진 노아, 루나, 렌을 원류민들이 데려가고 있어.'),
                    L('코덱스', '그래. 너희도 봤지. 그날 우리 선대가 그들을 받아들였다.')])
setStory('mural2', [L('리코', '장로님이 연구를 허락하던 날이야.'),
                    L('제로', '절대 자연을 해치지 않겠다고 약속했었지.'),
                    L('코덱스', '그 약속이 우리 선대가 인간을 믿은 이유였다.')])
rep('"q": "선대는 그들을 구했다. 그 뒤에 섬이 어떻게 됐는지는 너희도 봤을 거다. 할 말이 있나?"', '"q": "선대는 그들을 받아들였다. 그 뒤에 섬이 어떻게 됐는지는 너희도 봤을 거다. 할 말이 있나?"')
rep('"text": "구해 준 은혜를 저희가 대신 갚고 싶어요. 그래서 여기까지 왔어요."', '"text": "받아 준 은혜를 저희가 대신 갚고 싶어요. 그래서 여기까지 왔어요."')
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
