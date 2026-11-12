# 2026-11-12 (사용자 "미로 들어갔을 때 다 깨진다"): 미로 안에서는 카메라와 캐릭터 사이의 울타리를 잘라내는 처리(MAZE.clip) 때문에
#   울타리가 비스듬히 썰려 보였다. 잘라내지 않고, 위에서 내려다보는 시점(뒤 6.5·높이 13)으로 바꾼다. 울타리 높이에서는 가려지지 않는 각도다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70]); s = s.replace(old, new)
rep("const cpi = inMaze ? -0.4 : w.pitch;", "const cpi = inMaze ? 0 : w.pitch;")
rep("let D = inMaze ? 5.6 : Math.max(7.5, w.eye*3.4), H = inMaze ? 4.4 : w.eye*1.1;", "let D = inMaze ? 6.5 : Math.max(7.5, w.eye*3.4), H = inMaze ? 13 : w.eye*1.1;   /* in the maze: looking down from above, nothing is cut (user, 2026-11-12) */")
rep("if(inMaze){ MAZE.clip.normal.set(cs, 0, cc); MAZE.clip.constant = -cs*(w.x - cs*0.75) - cc*(w.z - cc*0.75); }\n  else if(MAZE) MAZE.clip.constant = 1e6;", "if(MAZE) MAZE.clip.constant = 1e6;")
rep("_wt.set(w.x + (inMaze ? sy*1.2 : 0), gy + w.eye*(inMaze ? 0.7 : 0.85) + lift, w.z + (inMaze ? cy*1.2 : 0));", "_wt.set(w.x + (inMaze ? sy*2.6 : 0), gy + w.eye*(inMaze ? 0.7 : 0.85) + lift, w.z + (inMaze ? cy*2.6 : 0));")
P.write_bytes(s.encode('utf-8')); print('ok')
