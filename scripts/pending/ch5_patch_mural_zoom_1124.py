# 2026-11-24 사용자: 벽화 줌인. 그리고 동굴 앞 대사 중 목적지 표시 숨김.
#  - room.zoom(i): 그 벽화를 화면 위쪽에 크게(아래쪽 대사·선택지 창에 덜 가리게). 빛줄기는 끄고 빛 구슬은 벽화 위로.
#  - caveStory: 벽화 앞에 선 모습을 잠깐 보여 준 뒤 줌인 → 닳은 자리가 채워짐 → 대사 → 질문
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')

def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

# 1. no way-marker while the cave mission talks at the mouth (the walk is still on)
rep("q.found || PARK_WAKE ||", "q.found || PARK_WAKE || (mini && mini.kind === 'cave') ||")

# 2. the zoom
rep("    reveal(i){ murals[i].fill = 1; },",
    "    zoom(i){ const mu = murals[i], d = mu.dir, P = mu.m.position, D = 3.6*H;   /* the mural fills the upper part of the screen; the dialogue strip and the choices sit below it (user, 2026-11-24) */\n"
    "      cam.p2.set(P.x - d.x*D, 1.85*H, P.z - d.z*D); cam.t2.set(P.x, P.y - 0.45*H, P.z); beam.visible = false;\n"
    "      _o.set(P.x - d.x*0.9*H, P.y + MH*0.62, P.z - d.z*0.9*H); orb.position.copy(_o); halo.position.copy(_o); orbL.position.copy(_o); if(reduce) cam.snap = true; },\n"
    "    reveal(i){ murals[i].fill = 1; },")

# 3. caveStory: zoom in before the worn spot fills, also on the second round and on the last wall
rep("    if(before){ await talk(before); if(dead()) return; }\n    room.reveal(i);",
    "    room.zoom(i); await wait(reduce ? 200 : 1500); if(dead()) return;\n"
    "    if(before){ await talk(before); if(dead()) return; }\n    room.reveal(i);")
rep("await cut(()=> room.place(i, row)); if(dead()) return; await wait(reduce ? 200 : 700); if(dead()) return; await ask(i);",
    "await cut(()=>{ room.place(i, row); room.zoom(i); }); if(dead()) return; await wait(reduce ? 200 : 900); if(dead()) return; await ask(i);")
rep("  await cut(()=> room.place(4, row)); if(dead()) return; await wait(reduce ? 200 : 1300); if(dead()) return;\n  await talk(STORY.caveEnd);",
    "  await cut(()=> room.place(4, row)); if(dead()) return; await wait(reduce ? 200 : 1300); if(dead()) return;\n"
    "  room.zoom(4); await wait(reduce ? 200 : 1500); if(dead()) return;\n  await talk(STORY.caveEnd);")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
