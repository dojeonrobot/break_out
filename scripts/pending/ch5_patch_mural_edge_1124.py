# 2026-11-24 점검: 벽화 판의 위·옆 가장자리가 네모로 딱 잘려 보임 → 타원으로 가장자리를 흐리게. 줌은 조금 물러나 벽화 위쪽이 잘리지 않게.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b):
    global s
    if s.count(a) != 1: sys.exit(f'anchor x{s.count(a)}: {a[:80]}')
    s = s.replace(a, b)
rep("g.fillRect(x, y, 7 + rn()*14, 5 + rn()*9); } g.globalAlpha = 1; } });",
    "g.fillRect(x, y, 7 + rn()*14, 5 + rn()*9); } g.globalAlpha = 1; }\n"
    "      g.save(); g.globalCompositeOperation = 'destination-in'; g.translate(384, 240); g.scale(1, 0.66); const fe = g.createRadialGradient(0, 0, 0, 0, 0, 400); fe.addColorStop(0.8, 'rgba(0,0,0,1)'); fe.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = fe; g.fillRect(-384, -364, 768, 728); g.restore(); });   /* soft edge: the painting sits in the rock, not on a board (2026-11-24) */")
rep("const mu = murals[i], d = mu.dir, P = mu.m.position, D = 3.6*H;", "const mu = murals[i], d = mu.dir, P = mu.m.position, D = 4.3*H;")
rep("cam.t2.set(P.x, P.y - 0.45*H, P.z);", "cam.t2.set(P.x, P.y - 0.55*H, P.z);")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
