# 2026-11-13 (사용자: 「미로 너무 쉬워가지고 미로 크기 1.5배로 키우고 좀 더 어렵게 수정해」)
#   미로: 한 변 50 → 75(1.5배), 칸 9×9 → 15×15(81칸 → 225칸, 통로 폭은 비슷하게 5). 한가운데 칸은 (n-1)/2.
#   자리: (176,408) → (155,414). 그대로 키우면 남쪽 바닷가(걷기 한계 z≈456)와 동쪽 언덕 옹벽(x≈195)에 걸려 서쪽으로 21, 남쪽으로 6 옮긴다.
#   같이 옮기는 것: place·pickable(반지름 36→54)·OCC·NATY_HIDE·미로 길(PATHS[17]) 끝·나무 치우기.
#   python scripts/pending/ch5_patch_maze_bigger.py   (한 번만)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:80]); s = s.replace(old, new)
NX, NZ = 155, 414
rep("const S = 50, n = 9, cell = S/n, TH = 1.2, hedge = mat(0x3f7a36).clone(), MX = 176, MZ = 408, MR = 0;   /* 2026-11-12: east of the gate, square to it; moved a little nearer the gate the same day (user) */",
    f"const S = 75, n = 15, mid = (n - 1)/2, cell = S/n, TH = 1.2, hedge = mat(0x3f7a36).clone(), MX = {NX}, MZ = {NZ}, MR = 0;   /* 2026-11-13 (user: too easy): 1.5 times the side, 15 x 15 cells instead of 9 x 9; moved west and south so it clears the shore and the hill wall */")
rep("st = [[4, 4]]; seen[4][4] = true;", "st = [[mid, mid]]; seen[mid][mid] = true;")
rep("if(lx < 0){ V[4][0] = 0; ent = [4, 0, 'W']; } else { V[4][n] = 0; ent = [4, n - 1, 'E']; } } else { if(lz < 0){ H[0][4] = 0; ent = [0, 4, 'N']; } else { H[n][4] = 0; ent = [n - 1, 4, 'S']; } }",
    "if(lx < 0){ V[mid][0] = 0; ent = [mid, 0, 'W']; } else { V[mid][n] = 0; ent = [mid, n - 1, 'E']; } } else { if(lz < 0){ H[0][mid] = 0; ent = [0, mid, 'N']; } else { H[n][mid] = 0; ent = [n - 1, mid, 'S']; } }")
rep("dist[4][4] = 0; const q = [[4, 4]];", "dist[mid][mid] = 0; const q = [[mid, mid]];")
rep("place(maze, 176/K, 408/K, 0);", f"place(maze, {NX}/K, {NZ}/K, 0);")
rep("sub:'미로 정원', cx:176/K, cz:408/K, h:8, r:36,", f"sub:'미로 정원', cx:{NX}/K, cz:{NZ}/K, h:8, r:54,")
rep("[176,408,38],[-150,412,24]", f"[{NX},{NZ},42],[{NX-27},{NZ-27},15],[{NX+27},{NZ-27},15],[{NX-27},{NZ+27},15],[{NX+27},{NZ+27},15],[-150,412,24]")
rep("NATY_HIDE = [176, 408];", f"NATY_HIDE = [{NX}, {NZ}];")
rep("PATHS[17]=[[0,360],[68,360],[120,364],[144,366],[168,371]];", f"PATHS[17]=[[0,360],[68,360],[120,363],[142,365],[{NX},369]];")
rep("clearTreesAt(-70, 405, 42); clearTreesAt(70, 405, 42);", f"clearTreesAt(-70, 405, 42); clearTreesAt(70, 405, 42); clearTreesAt({NX}, {NZ}, 58);   /* the bigger maze (2026-11-13) */")
P.write_bytes(s.encode('utf-8')); print('ok', NX, NZ, 'crlf', s.count('\r\n'))
