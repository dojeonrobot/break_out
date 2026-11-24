# 2026-11-24 사용자가 고른 벽화 시안(bak/sian_1124/벽화_시안.png 아래 줄)을 페이지에 넣는다.
#  bak/sian_1124/mural_art.js(채운 실루엣·원류민 잎 귀·손자국·바위결)를 muralRoom 앞에 넣고, muralRoom의 옛 SCENES·그리기를 그것으로 바꾼다.
import pathlib, sys, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
art = (ROOT / 'bak/sian_1124/mural_art.js').read_text(encoding='utf-8').replace('\r\n', '\n')
art = art.replace('(function(root){', '(function(root){', 1).replace('})(window);', '})(window);')
if 'MURAL_SCENES' in s: sys.exit('already applied')
i = s.find('function muralRoom(){')
a = s.find('  const OC = ', i); b = s.find('  const SP = [-72', i)
if min(i, a, b) < 0 or not (i < a < b): sys.exit('scene block not found')
s = s[:a] + '  const SCENES = MURAL_SCENES;   /* 2026-11-24: the paintings, redrawn (user picked the mock-up) */\n' + s[b:]
i = s.find('function muralRoom(){')
c = s.find('const tex = canvasTex(768, 480, g=>{', i); d = s.find('    const a = SP[i], dir', c)
if min(c, d) < 0: sys.exit('painter not found')
s = s[:c] + 'const tex = canvasTex(768, 480, g=> muralPaint(g, i, st.k));\n' + s[d:]
s = s[:s.find('function muralRoom(){')] + art.strip() + '\n' + s[s.find('function muralRoom(){'):]
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
