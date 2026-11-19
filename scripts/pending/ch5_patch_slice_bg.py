# 2026-11-19 (사용자): 연구실 게임의 뒷배경(흐린 아이콘 타일·가짜 섬 윤곽)을 없애고, 제로·리코의 장난스러움이 보이는 배경으로. 깨면 게임 창이 걷히며 자일로의 모니터 벽이 드러난다.
#  배경은 시안 세 가지를 같이 넣어 두고 window.__sliceBg('A'|'B'|'C')로 바꿔 찍는다. 고른 뒤 기본값(SLICE_BG)을 바꾸고 나머지는 지운다. 게임 화면에서만 마우스 포인터가 별 지팡이.
# 한 번만 적용: python scripts/pending/ch5_patch_slice_bg.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
a = s.index("    /* behind everything: the simulator, the island outline and its flow */"); b = s.index("    S.items.forEach(it=> glyph(it, 0)); S.halves.forEach(", a)
NEW = r"""    /* behind everything: 제로·리코's own game screen (user, 2026-11-19: the dim tiles and the fake island outline said nothing). Three looks while the user chooses: A notebook doodles, B arcade, C stickers */
    const BG = window.__sliceBgV || SLICE_BG, rnd2 = i=>{ const v = Math.sin(i*127.1 + 311.7)*43758.5453; return v - Math.floor(v); };
    if(BG === 'A'){ g.fillStyle = '#fbf6e6'; g.fillRect(0, 0, W2, H2); g.strokeStyle = 'rgba(86,150,214,.28)'; g.lineWidth = 1.5*k; for(let y = 46*k; y < H2; y += 46*k){ g.beginPath(); g.moveTo(0, y); g.lineTo(W2, y); g.stroke(); }
      g.strokeStyle = 'rgba(226,87,76,.5)'; g.lineWidth = 2.5*k; g.beginPath(); g.moveTo(92*k, 0); g.lineTo(92*k, H2); g.stroke();
      g.lineCap = 'round'; g.lineJoin = 'round'; const star = (x, y, r, c, rot)=>{ g.save(); g.translate(x, y); g.rotate(rot); g.strokeStyle = c; g.lineWidth = 5*k; g.beginPath(); for(let i = 0; i <= 10; i++){ const q = i % 2 ? r*0.45 : r, an = i*Math.PI/5 - Math.PI/2; g.lineTo(Math.cos(an)*q, Math.sin(an)*q); } g.stroke(); g.restore(); };
      for(let i = 0; i < 9; i++) star((0.1 + rnd2(i)*0.84)*W2, (0.12 + rnd2(i + 40)*0.8)*H2, (22 + rnd2(i + 9)*26)*k, ['#f39a3b', '#5aa0e6', '#58b368', '#e2574c', '#b07ad8'][i % 5], rnd2(i + 3)*2 + Math.sin(S.t*0.8 + i)*0.12);
      for(let i = 0; i < 5; i++){ const x = (0.16 + rnd2(i + 70)*0.7)*W2, y = (0.2 + rnd2(i + 80)*0.62)*H2; g.strokeStyle = ['#e2574c', '#5aa0e6', '#58b368'][i % 3]; g.lineWidth = 5*k; g.beginPath(); for(let j = 0; j < 7; j++) g.lineTo(x + j*20*k, y + (j % 2 ? -14 : 14)*k); g.stroke(); }
      g.save(); g.translate(W2*0.5, H2*0.52); g.rotate(-0.06); g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `900 ${Math.round(88*k)}px sans-serif`; g.lineWidth = 7*k; g.strokeStyle = 'rgba(29,47,85,.16)'; g.strokeText('제로 & 리코', 0, -50*k); g.font = `900 ${Math.round(56*k)}px sans-serif`; g.strokeText('최강 게임 ★', 0, 44*k); g.restore(); }
    else if(BG === 'B'){ const gr = g.createLinearGradient(0, 0, 0, H2); gr.addColorStop(0, '#1a1146'); gr.addColorStop(1, '#3b1a6e'); g.fillStyle = gr; g.fillRect(0, 0, W2, H2);
      for(let i = 0; i < 70; i++){ const x = rnd2(i)*W2, y = (rnd2(i + 200)*H2 + S.t*(10 + rnd2(i + 5)*26)*k) % H2, q = (2 + Math.floor(rnd2(i + 9)*3))*2*k; g.fillStyle = ['#ffe14a', '#7fe9ff', '#ff8ad0', '#ffffff'][i % 4]; g.globalAlpha = 0.35 + 0.5*Math.abs(Math.sin(S.t*2 + i)); g.fillRect(Math.round(x), Math.round(y), q, q); } g.globalAlpha = 1;
      g.save(); g.translate(W2/2, H2*0.5); g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `900 ${Math.round(120*k)}px monospace`; g.fillStyle = 'rgba(255,225,74,.13)'; g.fillText('ZERO × RICO', 0, -40*k); g.font = `900 ${Math.round(64*k)}px monospace`; g.fillStyle = 'rgba(127,233,255,.13)'; g.fillText('ARCADE', 0, 70*k); g.restore();
      const n = 26; for(let i = 0; i < n; i++){ const on = (Math.floor(S.t*4) + i) % 3 === 0; g.fillStyle = on ? '#ffe14a' : 'rgba(255,225,74,.25)'; const x = (i + 0.5)/n*W2; [14*k, H2 - 14*k].forEach(y=>{ g.beginPath(); g.arc(x, y, 7*k, 0, 6.3); g.fill(); }); } }
    else { g.fillStyle = '#bfe6ff'; g.fillRect(0, 0, W2, H2); g.fillStyle = 'rgba(255,255,255,.55)'; for(let y = 0, r0 = 0; y < H2 + 60*k; y += 64*k, r0++) for(let x = (r0 % 2 ? 32 : 0)*k; x < W2 + 60*k; x += 64*k){ g.beginPath(); g.arc(x, y, 9*k, 0, 6.3); g.fill(); }
      for(let i = 0; i < 40; i++){ const x = rnd2(i)*W2, y = (rnd2(i + 300)*H2 + S.t*(18 + rnd2(i + 7)*30)*k) % H2; g.save(); g.translate(x, y); g.rotate(S.t*(1 + rnd2(i)) + i); g.fillStyle = ['#e2574c', '#ffd400', '#58b368', '#b07ad8', '#f39a3b'][i % 5]; g.fillRect(-9*k, -4*k, 18*k, 8*k); g.restore(); }
      [[SLICE_PIC[0], 0.13, -0.09], [SLICE_PIC[1], 0.87, 0.09]].forEach(([im, fx, rot], i)=>{ if(!im.complete || !im.naturalWidth) return; const hh = H2*0.62, ww = hh*im.naturalWidth/im.naturalHeight; g.save(); g.translate(fx*W2, H2 - hh*0.42 + Math.sin(S.t*2 + i*2)*8*k); g.rotate(rot); g.shadowColor = 'rgba(20,40,80,.28)'; g.shadowBlur = 18*k; g.shadowOffsetY = 8*k; g.drawImage(im, -ww/2, -hh/2, ww, hh); g.restore(); }); }
"""
s = s[:a] + NEW + s[b:]
def rep(x, y):
    global s
    assert s.count(x) == 1, (s.count(x), x[:60]); s = s.replace(x, y)
# 배경 기본값·그림, 깨면 창이 걷히며 모니터 벽이 드러남
rep("  const d = sliceDlg(), cv = $('slCv'), g = cv.getContext('2d'), STG = ", "  const d = sliceDlg(), cv = $('slCv'), g = cv.getContext('2d'); d.classList.remove('out'); if(!SLICE_PIC.length) ['zero_joy', 'rico_joy'].forEach(n=>{ const im = new Image(); im.src = `img/chars/${n}.png?v=20261028c`; SLICE_PIC.push(im); });\n  const STG = ")
rep("function sliceDlg(){ let d = $('sliceDlg');", "const SLICE_BG = 'A', SLICE_PIC = []; window.__sliceBg = v=>{ window.__sliceBgV = v; };\nfunction sliceDlg(){ let d = $('sliceDlg');")
rep("  function win(){ S.done = true; S.cover = []; $('slP').textContent = '화면이 깨끗해졌어요'; sfx('success'); setTimeout(finish, reduce ? 300 : 1300); }",
    "  function win(){ S.done = true; S.cover = []; $('slP').textContent = '화면이 깨끗해졌어요'; sfx('success'); setTimeout(()=> d.classList.add('out'), reduce ? 0 : 700); setTimeout(finish, reduce ? 300 : 1900); }   /* the game window lifts and 자일로's monitors are there behind it (user, 2026-11-19) */")
rep("#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}",
    "#sliceDlg{transition:opacity 1.1s ease}#sliceDlg.out{opacity:0;pointer-events:none}#sliceDlg #slCv{cursor:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44' viewBox='0 0 44 44'%3E%3Cpath d='M15 15 39 39' stroke='%231d2f55' stroke-width='7' stroke-linecap='round'/%3E%3Cpath d='M15 15 39 39' stroke='%23fff' stroke-width='3' stroke-linecap='round'/%3E%3Cpath d='M12 1l3.2 7.4 8 .8-6 5.4 1.8 7.9L12 18.4 5 22.5l1.8-7.9-6-5.4 8-.8z' fill='%23ffd400' stroke='%231d2f55' stroke-width='2' stroke-linejoin='round'/%3E%3C/svg%3E\") 12 12,crosshair}\n#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}")
p.write_bytes(s.encode('utf-8')); print('ok', len(s))
