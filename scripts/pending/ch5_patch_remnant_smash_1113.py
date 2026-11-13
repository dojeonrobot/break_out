# 2026-11-13 (사용자: 「잔재를 부수는 그런 게 있어야 하는데 … 심장을 멈추는 건 재미가 없네」 「레일 위에서 갑자기 부수지 말고 시점은 아래로 내려가서 부수고 나서 다시 탑승하는 것처럼」)
#  잔재 해체: 고리 틈 맞추기(창) → 3D에서 직접 부수기. 잔재 둘레를 도는 노란 약점이 앞으로 올 때 「부수기」(탭·약점 누르기·Space).
#    여섯 번 치면 산산조각(파편·화면 흔들림). 두 번마다 고리가 하나씩 떨어지고 약점이 빨라진다. 뒤에 있을 때 치면 빗나감.
#  시점: 잔재를 찾으면 열차에서 내려 잔재 앞 땅 높이로 내려가고, 부순 뒤 열차로 돌아가 이어 달린다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
def cut(a, b, new):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]
# ---- camera: down to the remnant while it is being broken ----
rep("  _ct.set(_rp.x - ux*15, _rp.y + 12.5, _rp.z - uz*15); if(w.snap){",
    "  if(R.down){ const sp = R.down, m = REM.models[sp.i], tx = _rp.x - sp.x, tz = _rp.z - sp.z, tl = Math.hypot(tx, tz) || 1, gx = sp.x + tx/tl*9.5, gz = sp.z + tz/tl*9.5, sh = REM.game && REM.game.shake > performance.now() ? 0.4 : 0;\n"
    "    _ct.set(gx + (Math.random() - 0.5)*sh, groundY(gx, gz) + 2.6 + (Math.random() - 0.5)*sh, gz); camera.position.lerp(_ct, 1 - Math.pow(0.02, dt)); _wt.set(sp.x, m.y0 + 3.3, sp.z); camera.lookAt(_wt); controls.target.copy(_wt);\n"
    "    w.mates.forEach((mt, i)=>{ const k = i ? 2.4 : -2.4, sx = gx + tz/tl*k - tx/tl*2.5, sz = gz - tx/tl*k - tz/tl*2.5; mt.g.position.set(sx, groundY(sx, sz), sz); mt.g.rotation.y = Math.atan2(sp.x - sx, sp.z - sz); if(mt.g.userData.legL) walkPose(mt.g, 0, 1); });\n"
    "    w.x = _rp.x; w.z = _rp.z; return; }   /* off the train and down beside the remnant (user, 2026-11-13); the train waits on the rail above */\n"
    "  _ct.set(_rp.x - ux*15, _rp.y + 12.5, _rp.z - uz*15); if(w.snap){")
rep("R.pause = true; R.look = sp; miniGo.classList.remove('hot'); miniBox.hidden = true; remPulse(0); mini.phase = 'dig';", "R.pause = true; R.look = sp; R.down = sp; miniGo.classList.remove('hot'); miniBox.hidden = true; remPulse(0); mini.phase = 'dig';")
rep("()=>{ if(!mini || ride !== R) return; mini.phase = 'ride'; R.pause = false; R.look = null; miniBox.hidden = false; }); return; }",
    "()=>{ if(!mini || ride !== R) return; mini.phase = 'ride'; R.down = null; R.pause = false; R.look = null; miniGo.textContent = '탐지'; miniGo.classList.remove('hot'); remDots(); miniBox.hidden = false; }); return; }")
# ---- the game ----
cut("function remGame(i){ const d = remDlg(); mini.phase = 'game';", "function remFinish(i){",
    "/* breaking a remnant (user, 2026-11-13): a yellow weak point circles the device; strike it while it is on this side. Six strikes and it bursts. */\n"
    "function remAimEl(){ let el = $('remAim'); if(!el){ el = document.createElement('button'); el.type = 'button'; el.id = 'remAim'; el.hidden = true; el.setAttribute('aria-label', '약점 치기'); document.body.appendChild(el); el.addEventListener('pointerdown', e=>{ e.preventDefault(); e.stopPropagation(); remTap(); }); } return el; }\n"
    "function remPips(){ const G2 = REM.game; miniDots.innerHTML = G2 ? `<i class=\"on\">타격 ${G2.hits} / ${G2.need}</i>` : ''; }\n"
    "function remDebris(pos, n){ const bits = [], x = pos.x, y = pos.y, z = pos.z, floor = groundY(x, z) + 0.2; for(let j = 0; j < n; j++){ const b = add(islRoot, BOX(0.5, 0.4, 0.45), mat(j % 3 ? 0x7b7264 : 0xff6a4e), x, y, z, false); b.userData.dynamic = true; const a = Math.random()*6.28, v = 5 + Math.random()*9; bits.push([b, Math.cos(a)*v, 6 + Math.random()*9, Math.sin(a)*v, Math.random()*6]); }\n"
    "  remTween(1100, k=>{ const t = k*1.1; bits.forEach(([b, vx, vy, vz, r])=>{ b.position.set(x + vx*t, Math.max(floor, y + vy*t - 14*t*t), z + vz*t); b.rotation.set(r + t*6, r + t*4, 0); b.scale.setScalar(1 - k*0.6); }); if(k >= 1) bits.forEach(([b])=>{ if(b.parent) b.parent.remove(b); }); }); }\n"
    "function remGame(i){ const m = REM.models[i]; remDlg(); mini.phase = 'game';\n"
    "  REM.game = {i, hits:0, need:6, ang:Math.random()*6.28, sp:reduce ? 1.1 : 1.7, boost:0, shake:0, tapAt:0, last:performance.now(), done:false, front:false};\n"
    "  if(!m.weak){ m.weak = add(m.g, SPH(0.55, 12, 10), glowMat(0xffe14a, 0.99), 0, 3.6, 0, false); m.weak.userData.dynamic = true; } m.weak.visible = true;\n"
    "  miniGo.textContent = '부수기'; miniGo.disabled = false; miniGo.classList.remove('hot'); miniGo.style.setProperty('--p', 0); miniDoneBtn.hidden = true; remPips(); miniBox.hidden = false; $('qhHint').textContent = '노란 약점이 앞으로 올 때 「부수기」'; sfx('open');\n"
    "  const aim = remAimEl(), wp = new THREE.Vector3();\n"
    "  const loop = ()=>{ const G2 = REM.game; if(!G2 || G2.done){ aim.hidden = true; return; } const now = performance.now(), dt = Math.min(0.05, (now - G2.last)/1000); G2.last = now;\n"
    "    G2.ang = (G2.ang + G2.sp*(1 + G2.hits*0.16)*(G2.boost > now ? 1.7 : 1)*dt) % (Math.PI*2); const r = 2.7; m.weak.position.set(Math.cos(G2.ang)*r, 3.6 + Math.sin(G2.ang*2)*0.7, Math.sin(G2.ang)*r);\n"
    "    m.weak.getWorldPosition(wp); const cx = m.g.position.x, cz = m.g.position.z, cd = Math.hypot(camera.position.x - cx, camera.position.z - cz) || 1;\n"
    "    G2.front = ((wp.x - cx)*(camera.position.x - cx) + (wp.z - cz)*(camera.position.z - cz))/(r*cd) > 0.25; m.weak.material.opacity = G2.front ? 0.99 : 0.22; m.weak.scale.setScalar(G2.front ? 1 + 0.25*Math.sin(now/90) : 0.6);\n"
    "    wp.project(camera); aim.hidden = !G2.front || !!vn; aim.style.transform = `translate(${((wp.x + 1)/2*innerWidth).toFixed(0)}px, ${((1 - wp.y)/2*innerHeight).toFixed(0)}px) translate(-50%, -50%)`; miniGo.classList.toggle('hot', G2.front);\n"
    "    G2.raf = requestAnimationFrame(loop); }; loop(); }\n"
    "function remTap(){ const G2 = REM.game; if(!G2 || G2.done || vn) return; const m = REM.models[G2.i], now = performance.now(); if(now - G2.tapAt < 170) return; G2.tapAt = now;\n"
    "  if(!G2.front){ G2.boost = now + 800; sfx('error'); $('qhHint').textContent = '빗나갔어. 약점이 앞으로 돌아올 때 쳐'; return; }\n"
    "  G2.hits++; G2.shake = now + 260; sfx('chain'); remDebris(m.weak.getWorldPosition(new THREE.Vector3()), 7); remPips();\n"
    "  if(G2.hits % 2 === 0){ const k = G2.hits/2 - 1; if(m.rings[k]) m.rings[k].visible = false; }\n"
    "  G2.ang += Math.PI*(0.7 + Math.random()*0.5);\n"
    "  if(G2.hits >= G2.need){ G2.done = true; cancelAnimationFrame(G2.raf); m.weak.visible = false; remAimEl().hidden = true; miniBox.hidden = true; miniGo.classList.remove('hot'); G2.shake = now + 700; flash(); sfx('success'); remDebris(new THREE.Vector3(m.g.position.x, m.y0 + 3.6, m.g.position.z), 26); qPop('부서졌다!'); setTimeout(()=> remFinish(G2.i), reduce ? 200 : 1100); }\n"
    "  else $('qhHint').textContent = `금이 갔어! 남은 타격 ${G2.need - G2.hits}`; }\n"
    "miniGo.addEventListener('click', ()=>{ if(REM.game && !REM.game.done) remTap(); });\n")
rep("if(rd && rd.dataset.on){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) remTap(); return; }", "if(REM.game && !REM.game.done){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) remTap(); return; }")
rep("game:REM.game ? {ring:REM.game.ring, a:REM.game.a, done:REM.game.done} : null,", "game:REM.game ? {hits:REM.game.hits, need:REM.game.need, front:REM.game.front, done:REM.game.done} : null, down:!!(ride && ride.down), cam:camera.position.toArray().map(v=> Math.round(v*10)/10),")
rep("window.__remAim = ()=>{ const G2 = REM.game; if(G2) G2.a[G2.ring] = -Math.PI/2; };", "window.__remAim = ()=>{ const G2 = REM.game; if(G2){ const m = REM.models[G2.i]; G2.ang = Math.atan2(camera.position.z - m.g.position.z, camera.position.x - m.g.position.x); } };")
CSS = "#remAim{position:fixed;left:0;top:0;z-index:20;width:88px;height:88px;border-radius:50%;border:4px solid #ffe14a;background:none;padding:0;box-shadow:0 0 0 3px rgba(0,0,0,.4),inset 0 0 0 3px rgba(0,0,0,.4);touch-action:manipulation;cursor:pointer}#remAim[hidden]{display:none}\n"
mk = '</style></head><body>'; assert s.count(mk) == 1 and s.count('#remAim{') == 0; i = s.index(mk); s = s[:i] + CSS + s[i:]
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))

# 그 뒤 손으로 더한 두 줄(index.html): qMarkPlace 첫 줄에서 ride.down이면 길 표식 숨김, remGame에서 발견 빛기둥(m.beam) 끔.
