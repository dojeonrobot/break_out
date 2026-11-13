# 2026-11-13 (사용자: 지하실에서 「제로·리코가 깔아 둔 간단한 게임을 통과해야 시뮬레이션을 제대로 볼 수 있는 걸로」, 아이콘 베기 안을 고름)
#  미션 4, 연구실 도착 뒤 시뮬레이션을 켜기 전에: 모니터를 덮은 게임 아이콘을 손가락(마우스 끌기)으로 그어 벤다.
#  30개를 베면 화면을 덮은 칸 30개가 모두 걷히고 뒤의 시뮬레이터가 드러난다. 보이드 얼굴은 베면 안 됨(칸 둘이 다시 덮임).
#  대사는 초안(STORY.labGame / labGameDone). 사용자가 대본에서 고치면 반영.
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]; P = R / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
JS = r"""
/* ---------- the lab monitor game (user, 2026-11-13): 제로·리코's games cover the screen; slice the icons away and the simulator shows through ---------- */
Object.assign(STORY, {labGame:[{who:'자일로', text:'시뮬레이터를 켜 볼게요. ……어?'}, {who:'제로', text:'아, 그거요. 저번에 저희가 깔아 둔 게임이에요.'}, {who:'리코', text:'화면을 전부 덮어 버렸네. 저희가 치울게요.'}, {who:'보이드', text:'아이콘을 손가락으로 그어서 지워 줘. 내 얼굴은 베지 마.'}], labGameDone:[{who:'자일로', text:'됐어요. 이제 시뮬레이터가 보입니다.'}]});
let SLICE = null;
function sliceDlg(){ let d = $('sliceDlg'); if(d) return d; d = document.createElement('div'); d.id = 'sliceDlg'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-labelledby', 'slT');
  d.innerHTML = '<div class="in"><div class="hd"><h1 id="slT">모니터 치우기</h1><p id="slP">아이콘을 그어서 베세요</p><b id="slN">0 / 30</b></div><canvas id="slCv" aria-hidden="true"></canvas></div>'; document.body.appendChild(d); return d; }
function sliceGame(){ return new Promise(done=>{ if(ffOn()){ done(); return; }
  const d = sliceDlg(), cv = $('slCv'), g = cv.getContext('2d'), NEED = 30, COLS = 6, ROWS = 5, face = new Image(); face.src = 'img/chars/void_face.png?v=20261028d';
  const S = SLICE = {n:0, items:[], halves:[], trail:[], cover:Array.from({length:COLS*ROWS}, (_, i)=> i), t:0, spawn:0.4, last:performance.now(), down:false, done:false, msg:0, shake:0, raf:0};
  const fit = ()=>{ const r = cv.getBoundingClientRect(), dpr = Math.min(2, devicePixelRatio || 1); cv.width = Math.round(r.width*dpr); cv.height = Math.round(r.height*dpr); S.w = cv.width; S.h = cv.height; S.k = cv.width/900; }; d.dataset.on = '1'; fit(); addEventListener('resize', fit);
  const COL = ['#e2574c', '#f39a3b', '#ffd400', '#58b368', '#5aa0e6', '#b07ad8'];
  const spawn = ()=>{ const bad = S.n > 3 && Math.random() < 0.16, x = S.w*(0.15 + Math.random()*0.7), vx = (S.w/2 - x)/S.w*S.w*0.5 + (Math.random() - 0.5)*S.w*0.25, vy = -S.h*(1.05 + Math.random()*0.25);
    S.items.push({x, y:S.h + 50*S.k, vx, vy, r:(bad ? 44 : 40)*S.k, rot:Math.random()*6, vr:(Math.random() - 0.5)*5, bad, c:COL[Math.floor(Math.random()*COL.length)], shape:Math.floor(Math.random()*4)}); };
  const glyph = (it, half)=>{ const r = it.r; g.save(); g.translate(it.x, it.y); g.rotate(it.rot); if(half){ g.beginPath(); g.rect(half < 0 ? -r*1.2 : 0, -r*1.2, r*1.2, r*2.4); g.clip(); }
    if(it.bad){ g.beginPath(); g.arc(0, 0, r, 0, 6.3); g.fillStyle = '#f4f7fb'; g.fill(); if(face.complete && face.naturalWidth) g.drawImage(face, -r*0.86, -r*0.86, r*1.72, r*1.72); g.lineWidth = 4*S.k; g.strokeStyle = '#ff5a4e'; g.stroke(); }
    else { g.beginPath(); g.roundRect(-r, -r, r*2, r*2, r*0.36); g.fillStyle = it.c; g.shadowColor = 'rgba(0,0,0,.55)'; g.shadowBlur = 16*S.k; g.fill(); g.shadowBlur = 0; g.lineWidth = 4*S.k; g.strokeStyle = '#ffffff'; g.stroke(); g.fillStyle = 'rgba(255,255,255,.95)'; g.beginPath();
      if(it.shape === 0){ g.moveTo(-r*0.45, -r*0.5); g.lineTo(r*0.55, 0); g.lineTo(-r*0.45, r*0.5); }
      else if(it.shape === 1){ g.arc(0, 0, r*0.5, 0, 6.3); }
      else if(it.shape === 2){ g.rect(-r*0.5, -r*0.5, r*0.44, r*0.44); g.rect(r*0.06, -r*0.5, r*0.44, r*0.44); g.rect(-r*0.5, r*0.06, r*0.44, r*0.44); g.rect(r*0.06, r*0.06, r*0.44, r*0.44); }
      else { for(let i = 0; i < 10; i++){ const a = i*Math.PI/5 - Math.PI/2, q = i % 2 ? r*0.25 : r*0.58; g.lineTo(Math.cos(a)*q, Math.sin(a)*q); } }
      g.closePath(); g.fill(); }
    g.restore(); };
  const hit = (ax, ay, bx, by, it)=>{ const dx = bx - ax, dy = by - ay, L = dx*dx + dy*dy || 1, u = Math.max(0, Math.min(1, ((it.x - ax)*dx + (it.y - ay)*dy)/L)); return Math.hypot(it.x - ax - dx*u, it.y - ay - dy*u) < it.r*1.05; };
  const cut = (it, a)=>{ it.dead = true; const nx = Math.cos(a + Math.PI/2), ny = Math.sin(a + Math.PI/2); [-1, 1].forEach(sd=> S.halves.push({...it, dead:false, half:sd, vx:it.vx + nx*sd*220*S.k, vy:it.vy + ny*sd*220*S.k - 80*S.k, vr:sd*6, life:0.8}));
    if(it.bad){ S.n = Math.max(0, S.n - 2); for(let i = 0; i < 2 && S.cover.length < COLS*ROWS; i++){ const free = Array.from({length:COLS*ROWS}, (_, k)=> k).filter(k=> !S.cover.includes(k)); S.cover.push(free[Math.floor(Math.random()*free.length)]); }
      S.shake = 0.35; S.msg = 1.4; $('slP').textContent = '보이드는 베면 안 돼요!'; sfx('error'); }
    else { S.n++; if(S.cover.length) S.cover.splice(Math.floor(Math.random()*S.cover.length), 1); S.strokeN = (S.strokeN || 0) + 1; if(S.strokeN === 3){ S.msg = 1.1; $('slP').textContent = '한 번에 셋! 잘했어요'; } sfx('tap'); }
    $('slN').textContent = `${Math.min(S.n, NEED)} / ${NEED}`; if(S.n >= NEED && !S.done) win(); };
  const pos = e=>{ const r = cv.getBoundingClientRect(); return [(e.clientX - r.left)/r.width*S.w, (e.clientY - r.top)/r.height*S.h]; };
  const move = e=>{ if(!S.down || S.done) return; const [x, y] = pos(e), p = S.trail[S.trail.length - 1]; S.trail.push({x, y, t:S.t}); if(!p) return; const a = Math.atan2(y - p.y, x - p.x); if(Math.hypot(x - p.x, y - p.y) < 2) return; S.items.forEach(it=>{ if(!it.dead && hit(p.x, p.y, x, y, it)) cut(it, a); }); };
  const dn = e=>{ e.preventDefault(); S.down = true; S.strokeN = 0; S.trail = []; const [x, y] = pos(e); S.trail.push({x, y, t:S.t}); try{ cv.setPointerCapture(e.pointerId); }catch(er){} }, up = ()=>{ S.down = false; };
  cv.addEventListener('pointerdown', dn); cv.addEventListener('pointermove', move); ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev=> cv.addEventListener(ev, up));
  const finish = ()=>{ cancelAnimationFrame(S.raf); removeEventListener('resize', fit); cv.removeEventListener('pointerdown', dn); cv.removeEventListener('pointermove', move); delete d.dataset.on; SLICE = null; done(); };
  function win(){ S.done = true; S.cover = []; $('slP').textContent = '화면이 깨끗해졌어요'; sfx('success'); setTimeout(finish, reduce ? 300 : 1300); }
  S.win = ()=>{ if(!S.done){ S.n = NEED; $('slN').textContent = `${NEED} / ${NEED}`; win(); } };
  const draw = ()=>{ const now = performance.now(), dt = Math.min(0.05, (now - S.last)/1000); S.last = now; S.t += dt; const W2 = S.w, H2 = S.h, k = S.k, G2 = H2*1.9;
    if(!S.done){ S.spawn -= dt; if(S.spawn <= 0){ const many = S.n > 12 ? 3 : S.n > 5 ? 2 : 1; for(let i = 0; i < 1 + Math.floor(Math.random()*many); i++) spawn(); S.spawn = (reduce ? 1.3 : 0.95) - Math.min(0.4, S.n*0.014); } }
    S.items.forEach(it=>{ it.vy += G2*dt; it.x += it.vx*dt; it.y += it.vy*dt; it.rot += it.vr*dt; }); S.items = S.items.filter(it=> !it.dead && it.y < H2 + 90*k);
    S.halves.forEach(it=>{ it.vy += G2*dt; it.x += it.vx*dt; it.y += it.vy*dt; it.rot += it.vr*dt; it.life -= dt; }); S.halves = S.halves.filter(it=> it.life > 0);
    S.trail = S.trail.filter(p=> S.t - p.t < 0.22); if(S.msg > 0){ S.msg -= dt; if(S.msg <= 0 && !S.done) $('slP').textContent = '아이콘을 그어서 베세요'; } S.shake = Math.max(0, S.shake - dt);
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W2, H2); if(S.shake > 0) g.translate((Math.random() - 0.5)*14*k, (Math.random() - 0.5)*14*k);
    /* behind everything: the simulator, the island outline and its flow */
    g.fillStyle = '#061426'; g.fillRect(0, 0, W2, H2); g.strokeStyle = 'rgba(120,220,255,.16)'; g.lineWidth = 1; for(let x = 0; x < W2; x += 40*k){ g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H2); g.stroke(); } for(let y = 0; y < H2; y += 40*k){ g.beginPath(); g.moveTo(0, y); g.lineTo(W2, y); g.stroke(); }
    g.save(); g.translate(W2/2, H2*0.54); g.shadowColor = '#5fe4ff'; g.shadowBlur = 22*k; g.strokeStyle = '#8cecff'; g.lineWidth = 5*k; g.beginPath(); for(let i = 0; i <= 60; i++){ const a = i/60*Math.PI*2, r = 1 + 0.09*Math.sin(a*3 + 1) + 0.05*Math.sin(a*5); g.lineTo(Math.cos(a)*W2*0.36*r, Math.sin(a)*H2*0.3*r); } g.closePath(); g.stroke();
    g.lineWidth = 3*k; g.globalAlpha = 0.5 + 0.3*Math.sin(S.t*2); g.beginPath(); g.ellipse(0, 0, W2*0.13, H2*0.1, 0, 0, 6.3); g.stroke(); g.restore();
    /* the clutter that covers it: one tile goes with every icon sliced */
    const cw = W2/COLS, ch = H2/ROWS; S.cover.forEach(i=>{ const cx = (i % COLS)*cw, cy = Math.floor(i/COLS)*ch; g.fillStyle = '#1c2434'; g.fillRect(cx, cy, cw + 1, ch + 1); g.fillStyle = COL[i % COL.length]; g.globalAlpha = 0.3; g.beginPath(); g.roundRect(cx + cw*0.2, cy + ch*0.18, cw*0.6, ch*0.5, 10*k); g.fill(); g.globalAlpha = 0.18; g.fillStyle = '#fff'; g.fillRect(cx + cw*0.25, cy + ch*0.76, cw*0.5, 5*k); g.globalAlpha = 1; });
    S.items.forEach(it=> glyph(it, 0)); S.halves.forEach(it=>{ g.globalAlpha = Math.min(1, it.life*2); glyph(it, it.half); g.globalAlpha = 1; });
    if(S.trail.length > 1){ g.lineCap = 'round'; g.lineJoin = 'round'; for(let i = 1; i < S.trail.length; i++){ const a = S.trail[i - 1], b2 = S.trail[i], f = 1 - (S.t - b2.t)/0.22; g.strokeStyle = `rgba(255,255,255,${(0.9*f).toFixed(2)})`; g.lineWidth = (3 + 9*f)*k; g.beginPath(); g.moveTo(a.x, a.y); g.lineTo(b2.x, b2.y); g.stroke(); } }
    S.raf = requestAnimationFrame(draw); };
  draw(); }); }
window.__slice = ()=> SLICE ? {n:SLICE.n, items:SLICE.items.map(it=> [Math.round(it.x/SLICE.w*1000)/1000, Math.round(it.y/SLICE.h*1000)/1000, it.bad ? 1 : 0]), cover:SLICE.cover.length, done:SLICE.done} : null;
"""
rep("// the mid-check: the simulator over the island shows the records so far", JS.strip('\n') + "\n// the mid-check: the simulator over the island shows the records so far")
rep("async function midCheck(q){ miniSave('mid'); actBusy = true; stopWalk(); await wait(300); setSim(true);",
    "async function midCheck(q){ miniSave('mid'); actBusy = true; stopWalk(); await wait(300);\n  await new Promise(r=> say(STORY.labGame, r)); await sliceGame(); await new Promise(r=> say(STORY.labGameDone, r));   /* the monitor is cleared first (user, 2026-11-13) */\n  setSim(true);")
rep("if(on('callDlg')) return {t:'전화 건너뛰기', run:()=> $('callGo').click()};", "if(on('sliceDlg')) return {t:'게임 건너뛰기', run:()=>{ if(SLICE) SLICE.win(); }};\n  if(on('callDlg')) return {t:'전화 건너뛰기', run:()=> $('callGo').click()};")
CSS = ("#sliceDlg{position:fixed;inset:0;z-index:34;display:none;place-items:center;background:#05080f;-webkit-user-select:none;user-select:none;touch-action:none}#sliceDlg[data-on]{display:grid}"
       "#sliceDlg .in{display:grid;grid-template-rows:auto 1fr;gap:12px;width:min(1100px,96vw);height:min(760px,92dvh)}"
       "#sliceDlg .hd{display:grid;grid-template-columns:auto 1fr auto;align-items:baseline;gap:16px;color:#eaf7ff;padding:0 4px}#sliceDlg h1{margin:0;font-size:22px;font-weight:800}#sliceDlg p{margin:0;font-size:15px;color:#b9cbe0}#sliceDlg b{font-size:26px;font-variant-numeric:tabular-nums;color:#8cecff}"
       "#slCv{width:100%;height:100%;border-radius:14px;border:2px solid #2a3a55;background:#061426;touch-action:none;cursor:crosshair}"
       "@media (max-width:600px){#sliceDlg .hd{grid-template-columns:1fr auto}#sliceDlg p{grid-column:1 / -1;grid-row:2}}\n")
mk = '</style></head><body>'; assert s.count(mk) == 1 and s.count('#sliceDlg{') == 0; i = s.index(mk); s = s[:i] + CSS + s[i:]
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
