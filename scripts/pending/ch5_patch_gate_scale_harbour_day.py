# 2026-11-12 저녁 (사용자) — 이미 적용된 상태를 다시 만들 때 쓰는 기록용 패치. ch5_patch_maze_carpet_move.py 뒤에 돌린다.
#  1) 보이지 않는 벽: 정문 그룹은 화면에 0.55배로 그려지는데 「5. the gate」 단계의 scale.set(1.2,1.1,1)이 걷기 격자에만 반영돼 x 166까지 막혀 있었다 → 그 줄 삭제.
#  2) 숨은 그룹 아래 메시는 걷기 격자에서 뺀다.
#  3) 항구로 나가는 길 두 개(PATHS[26]·[28])를 없앤다(둥근 정문 광장을 침범). 길 번호가 밀리지 않게 부두 길 위의 짧은 토막으로 남긴다.
#  4) 섬의 낮을 길게: 07:30~17:30은 절반 속도, 그 밖은 2.5배 속도(하루 한 바퀴는 실제 약 68분 → 낮 60분 + 나머지 약 8분).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
E = [("gate.position.z=PARK_ENTRY.z; gate.scale.set(1.2,1.1,1);", "gate.position.z=PARK_ENTRY.z;   /* 2026-11-12: the gate is drawn at 0.55 (a later step put that scale back); scale.set(1.2,1.1,1) here only reached the walk grid, which then held an invisible wall out to x 166 */"),
     ("const skipped = o => { for(let p = o; p; p = p.parent) if(SKIP.has(p)) return true; return false; };", "const skipped = o => { for(let p = o; p; p = p.parent) if(SKIP.has(p) || !p.visible) return true; return false; };   /* a mesh under a hidden group is not there (2026-11-12) */"),
     ("PATHS[26]=[[0,430],PATHS[26][PATHS[26].length-1]];", "PATHS[26]=[[0,340],[0,344]];   /* 2026-11-12 (user): no path out to the harbour, it cut into the round gate plaza. Kept as a stub on the main street so the path numbers stay */"),
     ("PATHS[28]=[[-155,435],[-115,440],[0,430]];", "PATHS[28]=[[0,346],[0,350]];   /* the harbour arc: removed the same way */"),
     ("  walkway(PATHS[26],12,'harbour-main-concourse');\n", ""),
     ("flowHour += 20/60/60*2; if(flowHour > 21) flowHour = 6;", "flowHour += 20/60/60*2*(flowHour >= 7.5 && flowHour < 17.5 ? 0.5 : 2.5); if(flowHour > 21) flowHour = 6;   /* a longer day (user, 2026-11-12): daytime at half speed, dusk and night quicker */")]
n = 0
for a, b in E:
    if b and b in s: continue
    if a in s: s = s.replace(a, b); n += 1
P.write_bytes(s.encode('utf-8')); print('ok', n)
