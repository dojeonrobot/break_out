# 2026-11-12 (사용자: 「미로를 조금만 입구쪽에 가깝게 살짝 옮겨줘」)
#   미로: (198,408) → (NX,408), 정문 쪽(서쪽)으로. MX·place·pickable·OCC·NATY_HIDE·미로 길(PATHS[17]) 끝을 같이 옮긴다.
#   python ch5_patch_maze_nearer_gate.py [새 x, 기본 176]
import pathlib, sys
NX = int(sys.argv[1]) if len(sys.argv) > 1 else 176; D = NX - 198
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep("MX = 198, MZ = 408, MR = 0;   /* 2026-11-12: east of the gate wing's corner tower, square to the wall */", f"MX = {NX}, MZ = 408, MR = 0;   /* 2026-11-12: east of the gate, square to it; moved a little nearer the gate the same day (user) */")
rep("place(maze, 198/K, 408/K, 0);", f"place(maze, {NX}/K, 408/K, 0);")
rep("sub:'미로 정원', cx:198/K, cz:408/K,", f"sub:'미로 정원', cx:{NX}/K, cz:408/K,")
rep("[198,408,38],[-150,412,24]", f"[{NX},408,38],[-150,412,24]")
rep("NATY_HIDE = [198, 408];", f"NATY_HIDE = [{NX}, 408];")
rep("PATHS[17]=[[0,360],[68,360],[120,364],[166,366],[190,371]];", f"PATHS[17]=[[0,360],[68,360],[120,364],[{166 + D},366],[{190 + D},371]];")
P.write_bytes(s.encode('utf-8')); print('ok', NX)
