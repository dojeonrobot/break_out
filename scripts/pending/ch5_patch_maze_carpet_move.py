# 2026-11-12 (사용자: 「벽 길이를 왜 줄였어, 미로랑 놀이기구를 옮기면 되는데」)
#   정문 동쪽 날개 벽은 원래 길이 그대로 둔다(ch5_patch_gate_wing_garden.py의 벽 부분은 되돌림. 꽃밭 통로는 유지).
#   미로: (165,420) → 벽 끝 탑의 동쪽 빈터 (198,408), 벽과 나란하게(회전 0). 플라잉 카펫: (119,369) → 레일 북쪽 잔디 (112,312).
#   미로 길은 벽 북쪽을 따라가 탑을 돌아 들어간다(벽을 지나지 않는다).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
assert 'for(let i=0;i<5;i++){ const x = s*(44 + i*16);' in s and 'const tx = s*128;' in s, '벽이 원래 길이가 아니다'
rep("MX = 165, MZ = 420, MR = 0.2;", "MX = 198, MZ = 408, MR = 0;   /* 2026-11-12: east of the gate wing's corner tower, square to the wall */")
rep("place(maze, 165/K, 420/K, 0.2);", "place(maze, 198/K, 408/K, 0);")
rep("sub:'미로 정원', cx:165/K, cz:420/K,", "sub:'미로 정원', cx:198/K, cz:408/K,")
rep("[165,420,40],[-150,412,24]", "[198,408,38],[-150,412,24]")
rep("NATY_HIDE = [165, 420];", "NATY_HIDE = [198, 408];")
rep("place(carpetRide, 119/K, 369/K, 0.3);", "place(carpetRide, 112/K, 312/K, 0.3);")
rep("sub:'스윙 라이드', cx:119/K, cz:369/K,", "sub:'스윙 라이드', cx:112/K, cz:312/K,")
rep("PATHS[17]=[[0,360],[68,360],[96,376],[116,407],[140,421]];   /* through the garden lane, then east of the gate's corner tower */", "PATHS[17]=[[0,360],[68,360],[120,364],[166,366],[190,371]];   /* through the garden lane, along the north side of the gate wing, round its corner tower to the maze */")
rep("PATHS[24]=[[96,376],[101,374]];", "PATHS[24]=[[108,286],[110,290]];   /* the flying carpet, off the lake path */")
P.write_bytes(s.encode('utf-8')); print('ok')
