"""2026-11-04 사용자: 바이킹 옆에 끊어진 배전선, 아이들이 고치는 곳 이름은 「예비 배전선」. (ch5_patch_viking.py 뒤에 한 번)"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'chapter05', 'index.html')
h = io.open(P, encoding='utf-8', newline='').read().replace('\r\n', '\n')
assert 'POWER_LINE' not in h, 'already patched'
def rep(a, b, cnt=1):
    global h
    assert h.count(a) == cnt, (a[:60], h.count(a)); h = h.replace(a, b)
rep('예비 배전반', '예비 배전선', 3)
rep('이 배전반이 섬 전체', '이 예비 배전선이 섬 전체')
rep('배전반을 이어야 해', '예비 배전선을 이어야 해')
rep('배전반 ${y + 1}행 ${x + 1}열', '예비 배전선 ${y + 1}행 ${x + 1}열')
anchor = '  Object.assign(VK, {vik, swing, hold, site});'
add = r'''  /* the island's main power line ran past the lot; the collapse knocked a pole down and snapped the cable (story 2026-11-04). It stays cut:
     the children restore the park through the backup line (예비 배전선) at the coaster's service yard. */
  const line = new THREE.Group(); line.userData.dynamic = true; vik.add(line); VK.line = line;
  const WOOD = mat(0x6b4f36), CAB = new THREE.MeshLambertMaterial({color:0x1f2328});
  const pole = (x, z)=>{ const g = new THREE.Group(); g.position.set(x, 1.2, z); line.add(g);
    add(g, CYL(0.45, 0.6, 20, 8), WOOD); add(g, BOX(6, 0.5, 0.5), WOOD, 0, 18, 0); [-2.4, 0, 2.4].forEach(dx=> add(g, CYL(0.18, 0.25, 0.8, 6), mat(0xe8e8e8), dx, 18.5, 0, false));
    return g; };
  const p1 = pole(-27, -14.5); add(p1, BOX(1.8, 2.4, 1.4), mat(0x8c939c), 0.9, 13, 0.4);
  const p2 = pole(-6, -14.5); p2.rotation.z = -1.38; p2.position.y = 1.6;   /* knocked flat towards the ship */
  const tipOf = g=>{ g.updateMatrix(); return new THREE.Vector3(0, 18.6, 0).applyMatrix4(g.matrix); };
  const a = new THREE.Vector3(-27, 19.8, -14.5), b = tipOf(p2), cut = new THREE.Vector3(6, 1.5, -12.4);
  [-2.4, 0, 2.4].forEach((dz, j)=>{ const off = new THREE.Vector3(0, 0, dz*0.35);
    const sag = new THREE.CatmullRomCurve3([a.clone().add(new THREE.Vector3(dz, 0, 0)), a.clone().lerp(b, 0.5).add(new THREE.Vector3(0, -7 - j, dz*0.4)), b.clone().add(off)]);
    add(line, new THREE.TubeGeometry(sag, 24, 0.14, 5), CAB, 0, 0, 0, false);
    const loose = new THREE.CatmullRomCurve3([b.clone().add(off), b.clone().lerp(cut, 0.5).add(new THREE.Vector3(0, 0.4, dz*0.6)), cut.clone().add(new THREE.Vector3(j*0.8 - 0.8, 0, dz*0.5))]);
    add(line, new THREE.TubeGeometry(loose, 20, 0.14, 5), CAB, 0, 0, 0, false); });
  const sparks = []; for(let i = 0; i < 7; i++){ const s = add(line, SPH(0.32, 6, 4), glowMat(i%2 ? 0xfff2a8 : 0x9fe8ff, 1, true), cut.x, cut.y, cut.z, false); s.visible = false; sparks.push({s, d:new THREE.Vector3(Math.random()*2 - 1, Math.random()*1.6 + 0.4, Math.random()*2 - 1).normalize(), ph:Math.random()}); }
  islAnim.push(t=>{ const burst = (t*0.55) % 1 < 0.12; sparks.forEach(p=>{ const k = ((t*0.55) % 1)/0.12 + p.ph*0.3; p.s.visible = burst && k < 1; if(!p.s.visible) return;
    p.s.position.copy(cut).addScaledVector(p.d, 0.4 + k*3.2); p.s.position.y -= k*k*1.6; p.s.scale.setScalar(1 - k*0.8); }); });
'''
rep(anchor, add + anchor)
pick = "const VIK_B = pickable(viking, {n:'바이킹'"
rep(pick, '''viking.updateMatrixWorld(true);
{ const w = VK.line.children[0].getWorldPosition(new THREE.Vector3());
  window.POWER_LINE = pickable(VK.line, {n:'끊어진 배전선', c:'place', sub:'시설', cx:w.x/K, cz:w.z/K, keepSize:false,
    desc:'섬으로 전기를 보내던 배전선. 바이킹이 무너질 때 전봇대가 쓰러지면서 끊어졌습니다.',
    facts:[['위치','바이킹 공사장 옆'],['상태','끊어짐 · 접근 금지']]}); }
''' + pick)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('patched')
