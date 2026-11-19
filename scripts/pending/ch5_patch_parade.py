# 2026-11-19 (사용자: 퍼레이드도 제대로 만들자, 뭔지도 모르겠는 게 움직인다): 꽃수레 네 대를 사방에서 알아볼 수 있는 입체 조형으로 다시 만든다.
#  1 보이드(손 흔드는 로봇)  2 하모니아(가로로 도는 톱니 탑·오르간 관·음표)  3 네이티 불꽃(큰 불꽃 + 둘레 작은 불꽃)  4 보랏빛 성(성벽·탑·깃발)
#  수레 받침은 앞뒤가 둥근 판 + 줄무늬 치마(바퀴를 가림) + 금색 테 + 전구 + 깃발 줄 + 풍선 다발. 크기·경로·속도·악대는 그대로.
# 한 번만 적용: python scripts/pending/ch5_patch_parade.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
a = s.index("  const floats = [];\n  function floatBase(c1, c2){"); b = s.index("  const band = [];\n  for(let i=0;i<12;i++){const m=rider(parade", a)
NEW = r"""  const floats = [], PAL = [0xe2574c, 0xffd400, 0x5aa0e6, 0x58b368, 0xff9fcf, 0xb07ad8];
  /* 2026-11-19 (user: 뭔지도 모르겠는 게 움직인다): each float is one solid figure that reads from every side, on a proper float body */
  function floatBase(c1, c2){
    const g = new THREE.Group(), stripe = new THREE.MeshLambertMaterial({map:stripeTexI(c2, '#ffffff', 14)});
    add(g, BOX(10.6, 1.5, 12.6), stripe, 0, 0.1, 0); [-6.3, 6.3].forEach(z=> add(g, CYL(5.3, 5.3, 1.5, 22), stripe, 0, 0.1, z));          /* the skirt hides the wheels */
    add(g, BOX(10, 1.3, 12.6), mat(c1), 0, 1.6, 0); [-6.3, 6.3].forEach(z=> add(g, CYL(5, 5, 1.3, 22), mat(c1), 0, 1.6, z));
    add(g, BOX(10.2, 0.25, 12.6), mat(C.gold), 0, 2.9, 0); [-6.3, 6.3].forEach(z=> add(g, CYL(5.1, 5.1, 0.25, 22), mat(C.gold), 0, 2.9, z));
    for(let i = 0; i < 9; i++) [-5.15, 5.15].forEach((x, j)=> add(g, SPH(0.34, 8, 6), glowMat(PAL[(i + j) % 6], 0.95), x, 2.3, -6 + i*1.5, false));
    [[-4.4, -8.6], [4.4, -8.6], [-4.4, 8.6], [4.4, 8.6]].forEach(([x, z])=>{ add(g, CYL(0.14, 0.14, 7.2, 6), mat(0xffffff), x, 3.1, z, false); add(g, SPH(0.4, 8, 6), mat(C.gold), x, 10.5, z, false); });
    [-4.4, 4.4].forEach(x=>{ for(let i = 0; i < 9; i++){ const u = (i + 0.5)/9, f = add(g, CONE(0.55, 1.1, 4), mat(PAL[i % 6]), x, 9.6 - Math.sin(u*Math.PI)*1.5, -8.6 + u*17.2, false); f.rotation.x = Math.PI; } });
    [[-1.4, 0], [1.4, 0.3], [0, 1.9], [-0.9, 1.6], [0.9, 2.2]].forEach(([x, y], i)=>{ add(g, SPH(1.05, 10, 8), mat(PAL[(i*2 + 1) % 6]), x, 9.6 + y, -9.2, false); add(g, CYL(0.04, 0.04, 6.6 + y, 4), mat(0xdddddd), x*0.25, 3.1, -9.2, false); });
    return g;
  }
  const sideSign = (f, txt, bg, fg)=>{ [-5.34, 5.34].forEach(x=>{ const m = add(f, new THREE.PlaneGeometry(9.6, 1.25), new THREE.MeshBasicMaterial({map:signTex(txt, {bg, fg, size:64, w:512, h:68})}), x, 0.25, 0, false); m.rotation.y = x > 0 ? Math.PI/2 : -Math.PI/2; m.position.y = 0.85; }); };
  /* 1. 보이드: the island's recording robot, waving */
  const f1 = floatBase(0x1d2f55, '#ffd400'); sideSign(f1, 'DOROLAND PARADE', '#1d2f55', '#ffd400');
  const vb = new THREE.Group(); vb.position.set(0, 3.1, 0.5); f1.add(vb); const WH = 0xf6f8fb, BL = 0x2f9fe6;
  add(vb, CYL(2.2, 2.7, 3.4, 16), mat(WH)); add(vb, CYL(2.72, 2.72, 0.5, 16), mat(BL), 0, 0.5, 0); add(vb, SPH(3.3, 20, 14), mat(WH), 0, 6.2, 0);
  { const v = add(vb, SPH(2.75, 18, 12), mat(0x23262e), 0, 6.1, 0.95); v.scale.set(1, 0.84, 0.9); [-0.9, 0.9].forEach(x=>{ const e = add(vb, SPH(0.4, 10, 8), glowMat(0xffffff, 1), x, 6.3, 3.3, false); e.scale.set(0.8, 1.6, 0.5); }); }
  [-3.25, 3.25].forEach(x=> add(vb, new THREE.CylinderGeometry(1.15, 1.15, 0.8, 16).rotateZ(Math.PI/2), mat(BL), x, 6.2, 0));
  const vArm = [-1, 1].map(sd=>{ const a = new THREE.Group(); a.position.set(sd*2.5, 3.0, 0); vb.add(a); add(a, CYL(0.5, 0.6, 3.2, 10), mat(WH)); add(a, SPH(0.8, 10, 8), mat(WH), 0, 3.5, 0); a.rotation.z = -sd*0.9; return a; });
  /* 2. 하모니아: a tower of gears turning flat, organ pipes behind, notes above */
  const f2 = floatBase(0x5a55ad, '#7fd7ff'); const fg = [], notes = [];
  add(f2, CYL(1.1, 1.4, 9.4, 12), mat(C.lav), 0, 3.1, 0.6); add(f2, SPH(1.5, 12, 10), mat(C.gold), 0, 13, 0.6);
  [[4.4, 3.9], [3.2, 6.6], [2.2, 9.2]].forEach(([r, y], i)=>{ const gg = new THREE.Group(); gg.position.set(0, y, 0.6); f2.add(gg); add(gg, CYL(r, r, 0.9, 24), mat(i === 1 ? C.rose || 0xf39ac0 : C.gold)); add(gg, CYL(r*0.45, r*0.45, 1.1, 16), mat(C.violet), 0, -0.1, 0);
    const n = 10 + i*2; for(let k = 0; k < n; k++){ const an = k/n*Math.PI*2, t = add(gg, BOX(r*0.26, 0.9, r*0.3), mat(i === 1 ? C.rose || 0xf39ac0 : C.gold), Math.cos(an)*r*1.08, 0, Math.sin(an)*r*1.08); t.rotation.y = -an; } fg.push(gg); });
  [6.2, 8, 9.6, 8, 6.2].forEach((h, i)=>{ add(f2, CYL(0.55, 0.55, h, 10), mat(C.gold), -3.2 + i*1.6, 3.1, -6.6); add(f2, CYL(0.62, 0.62, 0.4, 10), mat(C.violet), -3.2 + i*1.6, 3.1 + h*0.3, -6.6); });
  [[-3.4, 12.5, 3], [3.2, 13.6, 1], [0.4, 15.6, -3]].forEach(([x, y, z], i)=>{ const n = new THREE.Group(); n.position.set(x, y, z); f2.add(n); add(n, SPH(0.75, 10, 8), mat(0xffffff)).scale.set(1.2, 0.85, 1); add(n, CYL(0.12, 0.12, 2.6, 5), mat(0xffffff), 0.75, 0, 0, false); add(n, BOX(1.1, 0.5, 0.14), mat(0xffffff), 1.2, 2.2, 0, false); n.userData.y0 = y; notes.push(n); });
  /* 3. 네이티: the island's flame */
  const f3 = floatBase(0xb8457f, '#ffd1ec'); add(f3, CYL(3.8, 4.4, 1.3, 20), mat(0x23375f), 0, 3.1, 0); add(f3, CYL(3.9, 3.9, 0.3, 20), mat(C.gold), 0, 4.4, 0);
  const flameGeo = (r, h)=> new THREE.LatheGeometry(Array.from({length:12}, (_, i)=>{ const u = i/11; return new THREE.Vector2(Math.max(0.01, u < 0.45 ? Math.sin(u/0.45*Math.PI/2)*r : r*Math.pow(1 - (u - 0.45)/0.55, 1.4)), u*h); }), 16);
  const flameMat = new THREE.MeshLambertMaterial({color:0x7cc8f0, emissive:0x2a6a9a, emissiveIntensity:0.5}), flame = add(f3, flameGeo(3.4, 10.5), flameMat, 0, 4.6, 0), wisps = [];
  for(let i = 0; i < 6; i++){ const an = i/6*Math.PI*2, w = add(f3, flameGeo(0.9, 3), flameMat, Math.cos(an)*4.1, 3.2, Math.sin(an)*6.6, false); w.userData.ph = i; wisps.push(w); }
  { const e = [-1.05, 1.05].map(x=>{ const m = add(f3, SPH(0.55, 10, 8), mat(0x1b2333), x, 8.6, 2.75, false); m.scale.set(0.8, 1.3, 0.5); return m; }); }
  /* 4. 보랏빛 성 */
  const f4 = floatBase(0x1f6297, '#d8bdec'); add(f4, BOX(7.4, 4.6, 9.6), mat(C.lav), 0, 3.1, 0); for(let i = 0; i < 5; i++) [-3.5, 3.5].forEach(x=> add(f4, BOX(0.7, 0.8, 1.1), mat(C.lav), x, 7.7, -4.2 + i*2.1, false));
  add(f4, BOX(2.4, 3, 0.3), mat(0x3b2a66), 0, 3.1, 4.85, false); add(f4, new THREE.CylinderGeometry(1.2, 1.2, 0.3, 16, 1, false, 0, Math.PI).rotateZ(Math.PI/2).rotateY(Math.PI/2), mat(0x3b2a66), 0, 6.1, 4.85, false);
  [[-3.6, -4.6, 9], [3.6, -4.6, 9], [-3.6, 4.6, 9], [3.6, 4.6, 9], [0, 0, 14]].forEach(([x, z, h], i)=>{ add(f4, CYL(1.5, 1.7, h, 14), mat(i === 4 ? 0xe9defa : C.lav), x, 3.1, z); add(f4, CONE(2.1, 4.2, 14), mat(C.violet), x, 3.1 + h, z);
    add(f4, CYL(0.07, 0.07, 2.2, 4), mat(0xffffff), x, 7.3 + h, z, false); const fl = add(f4, new THREE.PlaneGeometry(1.5, 0.9), new THREE.MeshLambertMaterial({color:PAL[i % 6], side:THREE.DoubleSide}), x + 0.78, 9 + h, z, false); });
  [f1, f2, f3, f4].forEach(f=>{ f.scale.setScalar(0.42); parade.add(f); floats.push(f); });
"""
s = s[:a] + NEW + s[b:]
x = "    fg.forEach((g,i)=> g.rotation.z = t*(i%2 ? -0.8 : 0.6)); flame.material.color.setHSL((t*0.05) % 1, 0.7, 0.65); flame.material.emissive.setHSL((t*0.05) % 1, 0.7, 0.3);"
assert s.count(x) == 1
s = s.replace(x, "    fg.forEach((g,i)=> g.rotation.y = t*(i%2 ? -0.9 : 0.7)); flameMat.color.setHSL(0.55 + 0.05*Math.sin(t*0.6), 0.75, 0.66); flameMat.emissive.setHSL(0.55 + 0.05*Math.sin(t*0.6), 0.7, 0.3); flame.scale.set(1 + 0.05*Math.sin(t*5), 1 + 0.07*Math.sin(t*3.3), 1 + 0.05*Math.cos(t*4.2)); wisps.forEach(w=>{ w.scale.setScalar(0.8 + 0.3*Math.abs(Math.sin(t*3 + w.userData.ph))); });\n    vArm[0].rotation.z = 0.9 + 0.12*Math.sin(t*2); vArm[1].rotation.z = -2.2 + 0.5*Math.sin(t*4); vb.position.y = 3.1 + 0.15*Math.sin(t*2.4); notes.forEach((n, i)=>{ n.position.y = n.userData.y0 + 0.6*Math.sin(t*2 + i*2); n.rotation.y = t*0.8 + i; });")
x = "desc:'악대를 앞세운 꽃수레 네 대가 정문과 분수 광장 사이를 오가는 퍼레이드. 해님 수레, 하모니아 톱니 수레, 네이티 불꽃 수레, 보랏빛 성 수레가 차례로 지나갑니다.'"
assert s.count(x) == 1
s = s.replace(x, "desc:'악대를 앞세운 꽃수레 네 대가 정문과 분수 광장 사이를 오가는 퍼레이드. 보이드 수레, 하모니아 톱니 수레, 네이티 불꽃 수레, 보랏빛 성 수레가 차례로 지나갑니다.'")
p.write_bytes(s.encode('utf-8')); print('ok', len(s))
