# 2026-11-20 저녁 (사용자): 첫째 잔재가 다른 것에 가려 안 보임, 빗나간 뒤 문구가 안 돌아옴·부수기 화면이 남음, 셋째 화살표가 상자 밖으로 넘침, 셋째를 5단계로, 열차 떨림.
# python -X utf8 scripts/pending/ch5_patch_rem_fix2_1120.py   (chapter05/index.html을 고친다, LF 유지)
import os
P = os.path.join(os.path.dirname(__file__), '..', '..', 'chapter05', 'index.html'); src = open(P, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global src; assert src.count(a) == n, (src.count(a), a[:70]); src = src.replace(a, b)
# 1) the view beside a remnant came down toward wherever the train had stopped (anywhere in a 90 m window), so it could land behind the viaduct, the train or a tree.
#    It now always comes from one fixed point up the track, the one the models face and the trees are cleared for
rep("if(R.down){ const sp = R.down, m = REM.models[sp.i], tx = _rp.x - sp.x, tz = _rp.z - sp.z,", "if(R.down){ R.ct = null; const sp = R.down, m = REM.models[sp.i], vp = sp.vp || (sp.vp = c.getPointAt((sp.u - 0.0125 + 1) % 1).clone()), tx = vp.x - sp.x, tz = vp.z - sp.z,")
rep("try{ const rp = TRAIN.curve.getPointAt(s.u); fx = rp.x - s.x; fz = rp.z - s.z; }catch(e){}", "try{ const rp = TRAIN.curve.getPointAt((s.u - 0.0125 + 1) % 1); fx = rp.x - s.x; fz = rp.z - s.z; }catch(e){}")
rep("remSpots().forEach(s=>{ roundSpots.forEach(([tx, tz], k)=>{ if(Math.hypot(tx - s.x, tz - s.z) < 11){", "remSpots().forEach(s=>{ let vx = 0, vz = 0; try{ const rp = TRAIN.curve.getPointAt((s.u - 0.0125 + 1) % 1), L = Math.hypot(rp.x - s.x, rp.z - s.z) || 1; vx = (rp.x - s.x)/L; vz = (rp.z - s.z)/L; }catch(e){}\n      const near = (tx, tz)=>{ const dx = tx - s.x, dz = tz - s.z, al = dx*vx + dz*vz; return Math.hypot(dx, dz) < 11 || (al > 0 && al < 24 && Math.abs(dx*vz - dz*vx) < 7); };   /* round the remnant and along the line of sight */\n      roundSpots.forEach(([tx, tz], k)=>{ if(near(tx, tz)){")
rep("pineSpots.forEach(([tx, tz], k)=>{ if(Math.hypot(tx - s.x, tz - s.z) < 11){ pineTree.setMatrixAt(k*2, Z0);", "pineSpots.forEach(([tx, tz], k)=>{ if(near(tx, tz)){ pineTree.setMatrixAt(k*2, Z0);")
# 2) after a miss the line went back to nothing; and a game that ended any other way left its panel, aim ring and weak point on screen
rep("remSay(G2.kind === 0 ? '빗나갔어! 잠깐 멈췄다가 약점이 앞에 올 때 쳐' : '빗나갔어! 잠깐 멈췄다가 노란 칸에 들어올 때 쳐'); return; }",
    "remSay(G2.kind === 0 ? '빗나갔어! 잠깐 멈췄다가 약점이 앞에 올 때 쳐' : '빗나갔어! 잠깐 멈췄다가 노란 칸에 들어올 때 쳐'); setTimeout(()=>{ if(REM.game === G2 && !G2.done) remSay(G2.kind === 0 ? (REM_TOUCH() ? '노란 약점이 앞으로 올 때 약점을 누르세요' : '노란 약점이 앞으로 올 때 <kbd>Space</kbd>') : (REM_TOUCH() ? '흰 표시가 노란 칸에 들어올 때 막대를 누르세요' : '흰 표시가 노란 칸에 들어올 때 <kbd>Space</kbd>')); }, 1300); return; }")
rep("islAnim.push(t=> REM.models.forEach((m, i)=>{ if(m.state !== 1) return;", "islAnim.push(()=>{ const G2 = REM.game, live = G2 && !G2.done; if(!live){ const p = $('remPlay'), a = $('remAim'); if(p && !p.hidden) p.hidden = true; if(a && !a.hidden) a.hidden = true; } REM.models.forEach((m, i)=>{ if(m.weak && m.weak.visible && !(live && G2.kind === 0 && G2.i === i)) m.weak.visible = false; }); });   /* nothing of the game stays on screen once it is over, however it ended (user, 2026-11-20) */\n  islAnim.push(t=> REM.models.forEach((m, i)=>{ if(m.state !== 1) return;")
# 3) the arrows: five rounds of 6-7-8-9-10 (user: 단계 5개로), and they wrap inside the box instead of running out of it
rep("need:kind === 0 ? 6 : kind === 1 ? 4 : 3,", "need:kind === 0 ? 6 : kind === 1 ? 4 : 5,")
rep("const n = reduce ? 4 + G2.hits : 8 + G2.hits*2,", "const n = reduce ? 4 + G2.hits : 6 + G2.hits,")
rep("G2.limit = reduce ? 9 + n*0.4 : 2 + n*0.28;", "G2.limit = reduce ? 9 + n*0.4 : 2 + n*0.3;")
CSS = ("/* 2026-11-20 evening (user: 화살표가 블록 밖으로 다 나와 있다): the arrows keep their size and wrap, eight to a row at most */\n"
       "body #remPlay .seq{flex-wrap:wrap;max-width:520px;margin:0 auto}body #remPlay .seq i{flex:0 0 58px}\n"
       "@media (max-width:620px){body #remPlay .seq{max-width:376px;gap:6px}body #remPlay .seq i{flex-basis:40px;width:40px;height:40px;font-size:22px}}\n"
       "@media (max-height:520px){body #remPlay .seq{max-width:392px}body #remPlay .seq i{flex-basis:42px}}\n")
rep("</style></head><body>", CSS + "</style></head><body>")
# 4) the train shook now and then: the camera chased its place on the track with a lag that grew and shrank with every uneven frame, and the cars were set one frame
#    behind it. The lag is now kept in the train's own frame (it only ever shrinks) and the cars are put on the track in the same step as the camera
rep("if(w.snap){ camera.position.copy(_ct); w.snap = false; } else camera.position.lerp(_ct, 1 - Math.pow(0.001, dt));   /* higher than the old ride camera: the cab must not fill the view */",
    "if(w.snap){ camera.position.copy(_ct); w.snap = false; } else camera.position.sub(R.ct || _ct).multiplyScalar(Math.pow(0.001, dt)).add(_ct); (R.ct = R.ct || new THREE.Vector3()).copy(_ct);   /* higher than the old ride camera: the cab must not fill the view */")
rep("train.forEach((c,k)=>{ const u = (u0 - k*0.0075 + 1) % 1; const p = curve.getPointAt(u), q = curve.getPointAt((u + 0.002) % 1); c.position.copy(p).y += 0.8; c.lookAt(q.x, p.y + 0.8, q.z); });",
    "(T.place = T.place || (uu=>{ train.forEach((c,k)=>{ const u = (uu - k*0.0075 + 1) % 1; const p = curve.getPointAt(u), q = curve.getPointAt((u + 0.002) % 1); c.position.copy(p).y += 0.8; c.lookAt(q.x, p.y + 0.8, q.z); }); }))(u0);")
rep("R.u = (R.u + dt/REM_LAP*go*(1 + 0.18*got.length)) % 1; TRAIN.u = R.u;", "R.u = (R.u + dt/REM_LAP*go*(1 + 0.18*got.length)) % 1; TRAIN.u = R.u; if(TRAIN.place) TRAIN.place(R.u);")
open(P, 'w', encoding='utf-8', newline='').write(src); print('patched', len(src))
