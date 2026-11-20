/* 잔재 디자인 시안(2026-11-20): 페이지 안에서 eval로 불러 잔재 0번 자리에 시안 모델을 세운다. 페이지 파일에는 들어가지 않는다.
   window.__remMock('A' | 'B' | 'C' | null)  — null이면 원래 모델로 되돌린다 */
window.__remMock = (dir, x, z, rot)=>{ const m = {y0:groundY(x, z) - 0.1};
  const g = new THREE.Group(); g.position.set(x, m.y0, z); g.rotation.y = rot || 0; islRoot.add(g); (window.__remMockGs = window.__remMockGs || []).push(g);
  const v = (x, y, z)=> new THREE.Vector3(x, y, z), tube = (pts, r, mt, seg = 20)=> add(g, new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p=> v(...p))), seg, r, 7), mt), tor = (R, r, mt, x, y, z)=>{ const o = add(g, new THREE.TorusGeometry(R, r, 8, 28), mt, x, y, z); o.rotation.x = Math.PI/2; return o; };
  const red = ()=> glowMat(0xff5a3c, 0.95), redA = ()=> glowMat(0xff6a4e, 0.55, true);
  if(dir === 'A'){   /* 녹슨 연구 장비: 철제 드럼, 경고 띠, 계기, 안테나, 땅에 박힌 굵은 전선 */
    const steel = flat(0x5b6d74), dark = flat(0x2c3439), rust = flat(0xa2582f), yel = flat(0xe3b22c), pale = flat(0xcfd6d8);
    add(g, CYL(3.7, 4.1, 0.45, 10), flat(0x6a6b66)); add(g, CYL(2.5, 2.7, 3.0, 14), steel, 0, 0.45, 0); add(g, CYL(2.78, 2.78, 0.5, 14), yel, 0, 1.0, 0);
    for(let k = 0; k < 10; k++){ const a = k/10*6.283, b = add(g, BOX(0.42, 0.52, 0.08), dark, Math.cos(a)*2.8, 0.99, Math.sin(a)*2.8); b.rotation.y = -a + 1.57; b.rotation.z = 0.5; }
    add(g, CYL(2.72, 2.72, 0.22, 14), rust, 0, 3.3, 0); add(g, CYL(1.5, 2.5, 0.8, 14), steel, 0, 3.45, 0); add(g, CYL(1.6, 1.6, 0.25, 14), dark, 0, 4.25, 0);
    [[1.9, 2.3, 1.75, 0.9, 0.7], [-2.2, 1.9, 1.3, 0.7, 1.0], [0.3, 2.9, -2.55, 1.1, 0.5]].forEach(([x, y, z, w, h])=>{ const p = add(g, BOX(w, h, 0.12), rust, x, y, z); p.lookAt(g.position.x + x*3, m.y0 + y, g.position.z + z*3); });   /* 녹 */
    for(let k = 0; k < 12; k++){ const a = k/12*6.283; add(g, SPH(0.11, 6, 5), dark, Math.cos(a)*2.74, 3.42, Math.sin(a)*2.74); }
    [[-0.9, 2.35], [0.55, 2.35]].forEach(([x, y])=>{ add(g, CYL(0.52, 0.52, 0.16, 14).rotateX(Math.PI/2), dark, x, y, 2.62); add(g, CYL(0.42, 0.42, 0.18, 14).rotateX(Math.PI/2), pale, x, y, 2.64); const n = add(g, BOX(0.06, 0.34, 0.05), red(), x, y - 0.02, 2.76, false); n.rotation.z = x < 0 ? 0.8 : -0.5; });   /* 계기 두 개 */
    [0, 1, 2, 3].forEach(k=>{ const a = k*1.571 + 0.78; add(g, CYL(0.09, 0.09, 1.9, 6), dark, Math.cos(a)*1.25, 4.5, Math.sin(a)*1.25); }); tor(1.3, 0.1, dark, 0, 6.4, 0); tor(1.3, 0.1, dark, 0, 5.4, 0);
    add(g, new THREE.IcosahedronGeometry(0.85, 0), red(), 0, 5.4, 0, false); add(g, SPH(1.5, 14, 10), redA(), 0, 5.4, 0, false);
    add(g, CYL(0.07, 0.1, 3.4, 6), dark, 2.1, 3.3, -0.6); add(g, SPH(0.2, 8, 6), red(), 2.1, 6.75, -0.6, false); add(g, BOX(0.9, 0.06, 0.06), dark, 2.1, 6.0, -0.6); add(g, BOX(0.6, 0.06, 0.06), dark, 2.1, 5.5, -0.6);
    [[2.4, 1.2, 0.9, 4.6, 0.3, 2.2], [-2.5, 1.5, 0.4, -4.8, 0.3, 1.4], [-1.2, 1.3, -2.3, -2.6, 0.3, -4.4]].forEach(([x, y, z, ex, ey, ez])=>{ tube([[x, y, z], [x*1.35, y + 0.5, z*1.35], [(x + ex)/2, 0.9, (z + ez)/2], [ex, ey, ez], [ex*1.06, -0.4, ez*1.06]], 0.2, dark); add(g, CYL(0.42, 0.5, 0.35, 8), flat(0x6a6b66), ex*1.04, 0, ez*1.04); });
    add(g, BOX(1.3, 1.5, 0.9), steel, -3.3, 0.2, -1.6); add(g, BOX(1.0, 0.5, 0.06), yel, -3.3, 1.0, -1.13); add(g, SPH(0.13, 8, 6), red(), -2.95, 1.45, -1.12, false); }
  else if(dir === 'B'){   /* 유적에 박힌 장치: 이끼 낀 돌 기단, 청동 고리, 붉게 새는 새김 문양, 붉은 결정 */
    const stone = flat(0x8d9084), stoneD = flat(0x6d7168), moss = flat(0x6f9450), bronze = flat(0xb48a45), bronzeD = flat(0x7d6233);
    [[0, 0, 0, 3.4, 0.55], [2.6, 0, 1.4, 1.5, 0.5], [-2.7, 0, 1.0, 1.7, 0.45], [-1.6, 0, -2.6, 1.6, 0.5], [2.0, 0, -2.3, 1.4, 0.55]].forEach(([x, y, z, r, sy], k)=>{ const o = add(g, new THREE.IcosahedronGeometry(r, 0), k ? stoneD : stone, x, r*sy*0.5, z); o.scale.y = sy; o.rotation.y = k*1.3; });
    add(g, CYL(2.3, 2.7, 1.3, 7), stone, 0, 0.9, 0); add(g, CYL(2.0, 2.3, 0.35, 7), stoneD, 0, 2.2, 0);
    [[2.3, 1.0, 1.2, 0.9], [-2.4, 0.8, 0.8, 1.1], [-0.6, 2.5, 1.5, 0.8], [1.4, 0.7, -2.2, 1.0]].forEach(([x, y, z, r])=>{ const o = add(g, SPH(r, 8, 6), moss, x, y, z); o.scale.y = 0.35; });
    [[-2.9, 0.42, 0.3], [2.9, -0.36, -0.2], [0.2, 0.1, -3.0]].forEach(([x, rz, z], k)=>{ const s = add(g, BOX(1.5, 4.6 - k*0.7, 1.0), k % 2 ? stoneD : stone, x, 0.2, z); s.rotation.z = rz*0.5; s.rotation.y = k*0.9;
      [1.2, 2.0, 2.8].forEach((y, j)=>{ const l = add(s, BOX(0.9 - j*0.2, 0.1, 0.06), red(), 0, y, 0.52, false); l.rotation.z = j % 2 ? 0.25 : -0.2; }); add(s, BOX(0.1, 1.9, 0.06), red(), 0, 1.1, 0.52, false); const cap = add(s, SPH(0.8, 8, 6), moss, 0, 4.5 - k*0.7, 0); cap.scale.y = 0.3; });
    tor(2.5, 0.2, bronze, 0, 2.0, 0); tor(1.7, 0.16, bronzeD, 0, 2.6, 0); const r2 = tor(2.1, 0.13, bronze, 0, 4.3, 0); r2.rotation.x = 1.1; const r3 = tor(1.6, 0.11, bronzeD, 0, 4.3, 0); r3.rotation.set(0.5, 0.9, 0);
    [0, 1, 2].forEach(k=>{ const a = k*2.094 + 0.5, c = add(g, BOX(0.28, 1.9, 0.28), bronze, Math.cos(a)*1.25, 2.45, Math.sin(a)*1.25); c.rotation.set(Math.sin(a)*0.5, 0, -Math.cos(a)*0.5); });
    const cr = add(g, new THREE.OctahedronGeometry(0.95, 0), red(), 0, 4.3, 0, false); cr.scale.y = 1.6; add(g, SPH(1.7, 14, 10), redA(), 0, 4.3, 0, false);
    [0, 1, 2, 3, 4, 5].forEach(k=>{ const a = k*1.047; add(g, BOX(0.08, 0.05, 1.5), red(), Math.cos(a)*3.9, 0.12, Math.sin(a)*3.9, false).rotation.y = -a + 1.57; });
    tube([[-2.9, 3.6, 0.3], [-2.2, 3.0, 0.9], [-1.4, 2.4, 1.6], [-0.8, 1.2, 2.5], [-0.6, 0.2, 3.1]], 0.09, moss); tube([[2.9, 3.4, -0.2], [2.0, 2.7, 0.6], [1.7, 1.4, 1.9], [2.1, 0.2, 2.6]], 0.08, moss); }
  else {   /* 일루아 채집기: 유리 통 안에서 붉게 변해 도는 일루아, 황동 뚜껑, 땅에 박힌 흡입 호스 */
    const brass = flat(0xc0903c), brassD = flat(0x8a6427), iron = flat(0x3a4046), glass = new THREE.MeshLambertMaterial({color:0xbff3f6, transparent:true, opacity:0.3, depthWrite:false, side:THREE.DoubleSide});
    add(g, CYL(3.4, 3.8, 0.4, 12), flat(0x6a6b66)); add(g, CYL(2.5, 2.8, 0.7, 16), brassD, 0, 0.4, 0); add(g, CYL(2.2, 2.5, 0.35, 16), brass, 0, 1.1, 0);
    add(g, new THREE.CylinderGeometry(1.9, 1.9, 3.6, 20, 1, true).translate(0, 1.8, 0), glass, 0, 1.4, 0, false);
    [[0, 0.5, 0, 1.25, 0xff5a3c, 0.9], [0.5, 1.5, 0.3, 0.9, 0xff7a4e, 0.8], [-0.4, 2.3, -0.2, 0.7, 0xff9a6a, 0.7], [0.2, 3.0, 0.2, 0.45, 0x8cecff, 0.8], [-0.5, 0.2, 0.5, 0.5, 0x8cecff, 0.7]].forEach(([x, y, z, r, c, o])=> add(g, new THREE.IcosahedronGeometry(r, 1), glowMat(c, o), x, 1.6 + y, z, false));
    [0, 1, 2, 3].forEach(k=>{ const a = k*1.571 + 0.4; add(g, CYL(0.1, 0.1, 3.6, 6), brassD, Math.cos(a)*1.98, 1.4, Math.sin(a)*1.98); }); tor(1.98, 0.09, brass, 0, 3.2, 0);
    add(g, CYL(2.1, 2.2, 0.45, 16), brass, 0, 5.0, 0); add(g, CYL(1.2, 2.0, 0.6, 16), brassD, 0, 5.45, 0); add(g, new THREE.CylinderGeometry(2.3, 0.9, 1.3, 16, 1, true).translate(0, 0.65, 0), new THREE.MeshLambertMaterial({color:0xc0903c, flatShading:true, side:THREE.DoubleSide}), 0, 6.0, 0);
    add(g, SPH(0.55, 10, 8), glowMat(0x8cecff, 0.85), 0, 6.5, 0, false);
    [[2.0, 0.8, 4.6, 2.4], [-2.2, 0.5, -4.8, 1.2], [0.4, -2.2, 1.6, -4.9]].forEach(([x, z, ex, ez], k)=>{ tube([[x, 5.1, z], [x*1.7, 5.6, z*1.7], [(x + ex)*0.62, 3.6, (z + ez)*0.62], [ex*0.95, 1.6, ez*0.95], [ex, 0.5, ez]], 0.26, iron, 26);
      for(let j = 1; j < 7; j++){ const t = j/7, rx = x + (ex - x)*t, rz = z + (ez - z)*t; } add(g, CYL(0.5, 0.75, 0.9, 10), brassD, ex, 0, ez); const d = add(g, new THREE.CircleGeometry(1.6, 24).rotateX(-Math.PI/2), glowMat(k === 2 ? 0xff6a4e : 0x8cecff, 0.45, true), ex, 0.12, ez, false); d.renderOrder = 4; tor(1.2, 0.05, glowMat(0x8cecff, 0.9), ex, 0.16, ez); });
    add(g, CYL(0.55, 0.55, 1.5, 10), brass, -3.0, 0.3, 1.9); add(g, SPH(0.55, 10, 8), brass, -3.0, 1.8, 1.9); add(g, CYL(0.32, 0.32, 0.12, 12).rotateX(Math.PI/2), flat(0xe9eef0), -3.0, 1.2, 2.46); }
  return true; };
