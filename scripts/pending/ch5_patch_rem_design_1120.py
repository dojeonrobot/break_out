# 2026-11-20 잔재 세 개의 모양을 사용자가 고른 시안대로(첫째 A 녹슨 연구 장비, 둘째 B 유적에 박힌 장치, 셋째 C 일루아 채집기).
# python -X utf8 scripts/pending/ch5_patch_rem_design_1120.py   (chapter05/index.html을 고친다, LF 유지)
import os
P = os.path.join(os.path.dirname(__file__), '..', '..', 'chapter05', 'index.html'); src = open(P, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global src; assert src.count(a) == n, (src.count(a), a[:70]); src = src.replace(a, b)
a = src.index("  const kind = i % 3, tone = k=> mat(k % 2 ? 0x6e7570 : 0x7b7264)"); END = "  REM.models.push({g, parts, core, rings, s, y0, state:0, kind, cy}); });"; b = src.index(END, a) + len(END)
NEW = r"""  /* 2026-11-20 (user picked all three mock-ups, one each): 0 a rusted research rig (drum, warning band, gauges, aerial, cables into the ground),
     1 a device set into old stone (mossy plinth, leaning slabs with red carvings, bronze rings round a red crystal), 2 an Ilua collector (glass tank, brass funnel, suction hoses).
     parts = the chunks that topple when it breaks (groups with their origin on the ground), rings = what falls away hit by hit, core = the red heart */
  const kind = i % 3, v3 = (x, y, z)=> new THREE.Vector3(x, y, z), grp = (x = 0, y = 0, z = 0)=>{ const o = new THREE.Group(); o.position.set(x, y, z); g.add(o); return o; };
  const tube = (P2, pts, r, mt, seg = 20)=> add(P2, new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p=> v3(...p))), seg, r, 7), mt), tor = (P2, R, r, mt, x, y, z)=>{ const o = add(P2, new THREE.TorusGeometry(R, r, 8, 28), mt, x, y, z); o.rotation.x = Math.PI/2; return o; };
  const red = ()=> glowMat(0xff5a3c, 0.95), redA = ()=> glowMat(0xff6a4e, 0.5, true); let parts, core, rings, cy, wr = 2.7, far = 0, look = 0;
  if(kind === 0){ const steel = flat(0x5b6d74), dark = flat(0x2c3439), rust = flat(0xa2582f), yel = flat(0xe3b22c), pale = flat(0xcfd6d8), slab = flat(0x6a6b66); cy = 2.3; wr = 3.6; far = 15; look = 4.7;
    add(g, CYL(3.7, 4.1, 0.45, 10), slab); const drum = grp(), top = grp(0, 3.3, 0), cab = grp(), box = grp(-3.3, 0, -1.6), mast = grp(2.1, 3.3, -0.6);
    add(drum, CYL(2.5, 2.7, 3.0, 14), steel, 0, 0.45, 0); add(drum, CYL(2.78, 2.78, 0.5, 14), yel, 0, 1.0, 0);
    for(let k = 0; k < 10; k++){ const an = k/10*6.283, bl = add(drum, BOX(0.42, 0.52, 0.08), dark, Math.cos(an)*2.8, 0.99, Math.sin(an)*2.8); bl.rotation.y = -an + 1.57; bl.rotation.z = 0.5; }
    [[1.9, 2.3, 1.75, 0.9, 0.7], [-2.2, 1.9, 1.3, 0.7, 1.0], [0.3, 2.9, -2.55, 1.1, 0.5]].forEach(([x, y, z, w, h])=>{ const p = add(drum, BOX(w, h, 0.12), rust, x, y, z); p.rotation.y = Math.atan2(x, z); });
    [[-0.9, 2.35], [0.55, 2.35]].forEach(([x, y])=>{ add(drum, CYL(0.52, 0.52, 0.16, 14).rotateX(Math.PI/2), dark, x, y, 2.62); add(drum, CYL(0.42, 0.42, 0.18, 14).rotateX(Math.PI/2), pale, x, y, 2.64); const n = add(drum, BOX(0.06, 0.34, 0.05), red(), x, y - 0.02, 2.76, false); n.rotation.z = x < 0 ? 0.8 : -0.5; });
    add(top, CYL(2.72, 2.72, 0.22, 14), rust); add(top, CYL(1.5, 2.5, 0.8, 14), steel, 0, 0.15, 0); add(top, CYL(1.6, 1.6, 0.25, 14), dark, 0, 0.95, 0);
    for(let k = 0; k < 12; k++){ const an = k/12*6.283; add(top, SPH(0.11, 6, 5), dark, Math.cos(an)*2.74, 0.12, Math.sin(an)*2.74); }
    [0, 1, 2, 3].forEach(k=>{ const an = k*1.571 + 0.78; add(top, CYL(0.09, 0.09, 1.9, 6), dark, Math.cos(an)*1.25, 1.2, Math.sin(an)*1.25); });
    core = add(g, new THREE.IcosahedronGeometry(0.85, 0), red(), 0, 5.4, 0, false); add(core, SPH(1.5, 14, 10), redA(), 0, 0, 0, false);
    rings = [3.1, 2.1, 1.1].map((y, k)=> tor(g, 1.3 + (k === 1 ? 0.08 : 0), 0.1, dark, 0, 3.3 + y, 0));
    add(mast, CYL(0.07, 0.1, 3.4, 6), dark); add(mast, SPH(0.2, 8, 6), red(), 0, 3.45, 0, false); add(mast, BOX(0.9, 0.06, 0.06), dark, 0, 2.7, 0); add(mast, BOX(0.6, 0.06, 0.06), dark, 0, 2.2, 0);
    [[2.4, 1.2, 0.9, 4.6, 0.3, 2.2], [-2.5, 1.5, 0.4, -4.8, 0.3, 1.4], [-1.2, 1.3, -2.3, -2.6, 0.3, -4.4]].forEach(([x, y, z, ex, ey, ez])=>{ tube(cab, [[x, y, z], [x*1.35, y + 0.5, z*1.35], [(x + ex)/2, 0.9, (z + ez)/2], [ex, ey, ez], [ex*1.06, -0.4, ez*1.06]], 0.2, dark); add(g, CYL(0.42, 0.5, 0.35, 8), slab, ex*1.04, 0, ez*1.04); });
    add(box, BOX(1.3, 1.5, 0.9), steel, 0, 0.2, 0); add(box, BOX(1.0, 0.5, 0.06), yel, 0, 1.0, 0.47); add(box, SPH(0.13, 8, 6), red(), 0.35, 1.45, 0.48, false);
    parts = [drum, top, mast, box, cab]; }
  else if(kind === 1){ const stone = flat(0x8d9084), stoneD = flat(0x6d7168), moss = flat(0x6f9450), bronze = flat(0xb48a45), bronzeD = flat(0x7d6233); cy = 3.2; far = 14.5; look = 4.5;
    [[0, 0, 3.4, 0.55], [2.6, 1.4, 1.5, 0.5], [-2.7, 1.0, 1.7, 0.45], [-1.6, -2.6, 1.6, 0.5], [2.0, -2.3, 1.4, 0.55]].forEach(([x, z, r, sy], k)=>{ const o = add(g, new THREE.IcosahedronGeometry(r, 0), k ? stoneD : stone, x, r*sy*0.5, z); o.scale.y = sy; o.rotation.y = k*1.3; });
    const plinth = grp(); add(plinth, CYL(2.3, 2.7, 1.3, 7), stone, 0, 0.9, 0); add(plinth, CYL(2.0, 2.3, 0.35, 7), stoneD, 0, 2.2, 0);
    [[2.3, 1.0, 1.2, 0.9], [-2.4, 0.8, 0.8, 1.1], [-0.6, 2.5, 1.5, 0.8], [1.4, 0.7, -2.2, 1.0]].forEach(([x, y, z, r])=>{ const o = add(g, SPH(r, 8, 6), moss, x, y, z); o.scale.y = 0.35; });
    const slabs = [[-2.9, 0.42, 0.3], [2.9, -0.36, -0.2], [0.2, 0.1, -3.0]].map(([x, rz, z], k)=>{ const sg = grp(x, 0.2, z); sg.rotation.z = rz*0.5; sg.rotation.y = k*0.9; const h = 4.6 - k*0.7; add(sg, BOX(1.5, h, 1.0), k % 2 ? stoneD : stone);
      [1.2, 2.0, 2.8].forEach((y, j)=>{ const l = add(sg, BOX(0.9 - j*0.2, 0.1, 0.06), red(), 0, y, 0.52, false); l.rotation.z = j % 2 ? 0.25 : -0.2; }); add(sg, BOX(0.1, 1.9, 0.06), red(), 0, 1.1, 0.52, false); const cap = add(sg, SPH(0.8, 8, 6), moss, 0, h, 0); cap.scale.y = 0.3; return sg; });
    const claws = grp(0, 2.45, 0); [0, 1, 2].forEach(k=>{ const an = k*2.094 + 0.5, c = add(claws, BOX(0.28, 1.9, 0.28), bronze, Math.cos(an)*1.25, 0, Math.sin(an)*1.25); c.rotation.set(Math.sin(an)*0.5, 0, -Math.cos(an)*0.5); });
    tor(plinth, 2.5, 0.2, bronze, 0, 2.0, 0); tor(plinth, 1.7, 0.16, bronzeD, 0, 2.6, 0);
    rings = [[2.3, 0.14, bronze, 1.1, 0], [1.9, 0.12, bronzeD, 0.5, 0.9], [1.55, 0.1, bronze, 2.0, 0.4]].map(([R, r, mt, rx, ry])=>{ const o = add(g, new THREE.TorusGeometry(R, r, 8, 28), mt, 0, 4.4, 0); o.rotation.set(rx, ry, 0); return o; });
    core = add(g, new THREE.OctahedronGeometry(0.95, 0), red(), 0, 4.4, 0, false); core.scale.y = 1.6; add(core, SPH(1.7, 14, 10), redA(), 0, 0, 0, false).scale.y = 1/1.6;
    [0, 1, 2, 3, 4, 5].forEach(k=>{ const an = k*1.047; add(g, BOX(0.08, 0.05, 1.5), red(), Math.cos(an)*3.9, 0.3, Math.sin(an)*3.9, false).rotation.y = -an + 1.57; });
    const vines = grp(); tube(vines, [[-2.9, 3.6, 0.3], [-2.2, 3.0, 0.9], [-1.4, 2.4, 1.6], [-0.8, 1.2, 2.5], [-0.6, 0.2, 3.1]], 0.09, moss); tube(vines, [[2.9, 3.4, -0.2], [2.0, 2.7, 0.6], [1.7, 1.4, 1.9], [2.1, 0.2, 2.6]], 0.08, moss);
    parts = [plinth, ...slabs, claws, vines]; }
  else { const brass = flat(0xc0903c), brassD = flat(0x8a6427), iron = flat(0x3a4046), glass = new THREE.MeshLambertMaterial({color:0xbff3f6, transparent:true, opacity:0.3, depthWrite:false, side:THREE.DoubleSide}); cy = 3.2; far = 16.5; look = 4.4;
    add(g, CYL(3.4, 3.8, 0.4, 12), flat(0x6a6b66)); add(g, CYL(2.5, 2.8, 0.7, 16), brassD, 0, 0.4, 0); add(g, CYL(2.2, 2.5, 0.35, 16), brass, 0, 1.1, 0);
    const tank = grp(0, 1.4, 0), lid = grp(0, 5.0, 0), hoses = grp(), pump = grp(-3.0, 0, 1.9);
    add(tank, new THREE.CylinderGeometry(1.9, 1.9, 3.6, 20, 1, true).translate(0, 1.8, 0), glass, 0, 0, 0, false); [0, 1, 2, 3].forEach(k=>{ const an = k*1.571 + 0.4; add(tank, CYL(0.1, 0.1, 3.6, 6), brassD, Math.cos(an)*1.98, 0, Math.sin(an)*1.98); });
    core = add(g, new THREE.IcosahedronGeometry(1.2, 1), glowMat(0xff5a3c, 0.9), 0, 2.4, 0, false);
    [[0.6, 0.9, 0.3, 0.8, 0xff7a4e, 0.8], [-0.5, 1.6, -0.2, 0.6, 0xff9a6a, 0.7], [0.2, 2.3, 0.3, 0.4, 0x8cecff, 0.8], [-0.7, -0.4, 0.5, 0.45, 0x8cecff, 0.7]].forEach(([x, y, z, r, c, o])=> add(core, new THREE.IcosahedronGeometry(r, 1), glowMat(c, o), x, y, z, false));
    add(lid, CYL(2.1, 2.2, 0.45, 16), brass); add(lid, CYL(1.2, 2.0, 0.6, 16), brassD, 0, 0.45, 0); add(lid, new THREE.CylinderGeometry(2.3, 0.9, 1.3, 16, 1, true).translate(0, 0.65, 0), new THREE.MeshLambertMaterial({color:0xc0903c, flatShading:true, side:THREE.DoubleSide}), 0, 1.0, 0); add(lid, SPH(0.55, 10, 8), glowMat(0x8cecff, 0.85), 0, 1.5, 0, false);
    rings = [tor(g, 1.98, 0.09, brass, 0, 4.6, 0), tor(g, 1.98, 0.09, brass, 0, 3.2, 0), tor(g, 1.98, 0.09, brass, 0, 1.8, 0)];
    [[2.0, 0.8, 4.6, 2.4], [-2.2, 0.5, -4.8, 1.2], [0.4, -2.2, 1.6, -4.9]].forEach(([x, z, ex, ez], k)=>{ tube(hoses, [[x, 5.1, z], [x*1.7, 5.6, z*1.7], [(x + ex)*0.62, 3.6, (z + ez)*0.62], [ex*0.95, 1.6, ez*0.95], [ex, 0.5, ez]], 0.26, iron, 26);
      add(g, CYL(0.5, 0.75, 0.9, 10), brassD, ex, 0, ez); const d = add(g, new THREE.CircleGeometry(1.6, 24).rotateX(-Math.PI/2), glowMat(k === 2 ? 0xff6a4e : 0x8cecff, 0.45, true), ex, 0.32, ez, false); d.renderOrder = 4; });
    add(pump, CYL(0.55, 0.55, 1.5, 10), brass, 0, 0.3, 0); add(pump, SPH(0.55, 10, 8), brass, 0, 1.8, 0); add(pump, CYL(0.32, 0.32, 0.12, 12).rotateX(Math.PI/2), flat(0xe9eef0), 0, 1.2, 0.56);
    parts = [tank, lid, hoses, pump]; }
  { let fx = -s.x, fz = -s.z; try{ const rp = TRAIN.curve.getPointAt(s.u); fx = rp.x - s.x; fz = rp.z - s.z; }catch(e){} g.rotation.y = Math.atan2(fx, fz); }   /* its face looks at the spot on the track where the train stops and the view comes down */ g.traverse(o=>{ o.userData.dynamic = true; });
  REM.models.push({g, parts, core, rings, s, y0, state:0, kind, cy, wr, far, look}); });"""
src = src[:a] + NEW + src[b:]
rep("m.core.rotation.y = t*2; m.rings.forEach((r, k)=>{ if(r.visible) r.rotation.z = t*(0.8 + k*0.5)*(k%2 ? -1 : 1); });", "m.core.rotation.y = t*2; if(m.kind === 1) m.rings.forEach((r, k)=>{ if(r.visible) r.rotation.z = t*(0.8 + k*0.5)*(k%2 ? -1 : 1); });   /* only the bronze rings turn; the cage and the tank hoops stand still */")
rep("const r = 2.7; m.weak.position.set(", "const r = m.wr || 2.7; m.weak.position.set(")
rep("far = 9.5 + Math.max(0, (m.cy || 3.6) - 3.6)*1.3,", "far = m.far || 9.5 + Math.max(0, (m.cy || 3.6) - 3.6)*1.3,")
rep("_wt.set(sp.x, m.y0 + Math.max(3.3, (m.cy || 3.6)*0.72), sp.z);", "_wt.set(sp.x, m.y0 + (m.look || Math.max(3.3, (m.cy || 3.6)*0.72)), sp.z);")
rep("const from = m.parts.map(p=> [p.position.y, p.rotation.z]); const end = (p, k, i)=>{ p.position.y = from[i][0]*(1 - k) + 0.5*k; p.rotation.z = from[i][1] + k*(i%2 ? -1.2 : 1.1); };",
    "const from = m.parts.map(p=> [p.position.y, p.rotation.z]); const end = (p, k, i)=>{ p.position.y = from[i][0]*(1 - k) + (from[i][0] > 1 ? 0.9 : 0.1)*k; p.rotation.z = from[i][1] + k*(i%2 ? -1.2 : 1.1); };   /* chunks that sit on the ground only tip over; the upper ones drop */")
# the mission's light column stood on the remnant all through the game and washed the model out: none while a remnant is being broken
rep("qBeam.visible = d > 18; qBeam.position.set(tx, groundY(tx, tz), tz); qBeam.material.uniforms.uTime.value = t/1000; return; }", "qBeam.visible = d > 18 && !(ride && ride.down); qBeam.position.set(tx, groundY(tx, tz), tz); qBeam.material.uniforms.uTime.value = t/1000; return; }")
rep("qTrailMat.uniforms.uTime.value = t/1000; qBeam.visible = d > 18; qBeam.position.set(", "qTrailMat.uniforms.uTime.value = t/1000; qBeam.visible = d > 18 && !(ride && ride.down); qBeam.position.set(")
# the trees that stood over a remnant hid its upper half: none within 11 of each spot
rep("function remBuild(){ if(REM.models.length) return; remSpots().forEach((s, i)=>{",
    "function remBuild(){ if(REM.models.length) return;\n  try{ const Z0 = new THREE.Matrix4().makeScale(0, 0, 0); let hit = false; remSpots().forEach(s=>{ roundSpots.forEach(([tx, tz], k)=>{ if(Math.hypot(tx - s.x, tz - s.z) < 11){ roundTree.setMatrixAt(k, Z0); trunkI.setMatrixAt(k, Z0); hit = true; } }); pineSpots.forEach(([tx, tz], k)=>{ if(Math.hypot(tx - s.x, tz - s.z) < 11){ pineTree.setMatrixAt(k*2, Z0); pineTree.setMatrixAt(k*2 + 1, Z0); trunkI.setMatrixAt(roundSpots.length + k, Z0); hit = true; } }); });\n    if(hit){ roundTree.instanceMatrix.needsUpdate = true; pineTree.instanceMatrix.needsUpdate = true; trunkI.instanceMatrix.needsUpdate = true; } }catch(e){ console.warn('remnant trees', e); }\n  remSpots().forEach((s, i)=>{")
open(P, 'w', encoding='utf-8', newline='').write(src); print('patched', len(src))
