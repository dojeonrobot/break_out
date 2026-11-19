# 2026-11-19: 사용자가 게임 배경 A안(공책 낙서)을 골랐다. 시안 B·C 코드와 시안 전환 손잡이, 쓰지 않는 그림 불러오기를 지운다.
# 한 번만 적용: python scripts/pending/ch5_patch_slice_bg_pick.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
a = s.index("    else if(BG === 'B'){"); b = s.index("    S.items.forEach(it=> glyph(it, 0)); S.halves.forEach(", a); s = s[:a] + s[b:]
R = [("    const BG = window.__sliceBgV || SLICE_BG, rnd2 = ", "    const rnd2 = "),
     ("    if(BG === 'A'){ g.fillStyle = '#fbf6e6';", "    { g.fillStyle = '#fbf6e6';"),
     ("Three looks while the user chooses: A notebook doodles, B arcade, C stickers */", "A lined notebook page with their doodles (the user picked it from three mock-ups) */"),
     (" d.classList.remove('out'); if(!SLICE_PIC.length) ['zero_joy', 'rico_joy'].forEach(n=>{ const im = new Image(); im.src = `img/chars/${n}.png?v=20261028c`; SLICE_PIC.push(im); });\n", " d.classList.remove('out');\n"),
     ("const SLICE_BG = 'A', SLICE_PIC = []; window.__sliceBg = v=>{ window.__sliceBgV = v; };\n", "")]
for x, y in R:
    assert s.count(x) == 1, (s.count(x), x[:60]); s = s.replace(x, y)
assert 'SLICE_PIC' not in s and '__sliceBg' not in s
p.write_bytes(s.encode('utf-8')); print('ok', len(s))
