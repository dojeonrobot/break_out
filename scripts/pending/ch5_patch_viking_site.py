# 2026-11-12 (사용자): 바이킹 공사장을 확실히 공사 중·출입금지로 보이게.
#   둘레: 얇은 띠 → 주황 기둥 + 노랑·검정 빗금 판 두 줄 + 주황 안전망, 모서리 경광등, 출입금지 표지 6개
#   안: 안전제일·관계자 외 출입금지 현수막(비계), 굴착기, 자재(파이프·시멘트 포대·파란 천막 더미)
#   전부 VK.site 안이라 바이킹이 서면 함께 사라진다. 둘레 자리는 그대로(걷기 막힘 범위 변화 없음).
# 사용: python scripts/pending/ch5_patch_viking_site.py   (한 번만)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'hazTex' not in s, '이미 적용됨'
a = s.index('  const TAPE_Y = 0xffd400, TAPE_K = 0x22252b;\n'); b = s.index("  /* the island's main power line ran past the lot;")
NEW = r'''  /* 2026-11-12 (user): a real construction site that reads 「공사 중 · 출입금지」 at a glance. Textured long pieces instead of many small boxes (the site is never baked). */
  const hazTex = rep=>{ const t = canvasTex(256, 64, g=>{ g.fillStyle = '#ffd400'; g.fillRect(0, 0, 256, 64); g.fillStyle = '#22252b'; for(let i = -2; i < 6; i++){ g.beginPath(); g.moveTo(i*64, 64); g.lineTo(i*64 + 32, 64); g.lineTo(i*64 + 96, 0); g.lineTo(i*64 + 64, 0); g.fill(); } }); t.wrapS = THREE.RepeatWrapping; t.repeat.set(rep, 1); t.needsUpdate = true; return t; };
  const netTex = (rx, ry)=>{ const t = canvasTex(64, 64, g=>{ g.clearRect(0, 0, 64, 64); g.strokeStyle = '#ff7a1a'; g.lineWidth = 7; for(let i = -1; i < 3; i++){ g.beginPath(); g.moveTo(i*32, 0); g.lineTo(i*32 + 64, 64); g.stroke(); g.beginPath(); g.moveTo(i*32 + 64, 0); g.lineTo(i*32, 64); g.stroke(); } }); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); t.needsUpdate = true; return t; };
  const stopTex = canvasTex(256, 320, g=>{ g.fillStyle = '#ffffff'; g.fillRect(0, 0, 256, 320); g.strokeStyle = '#d7261e'; g.lineWidth = 12; g.strokeRect(6, 6, 244, 308);
    g.lineWidth = 22; g.beginPath(); g.arc(128, 116, 76, 0, Math.PI*2); g.stroke(); g.beginPath(); g.moveTo(74, 62); g.lineTo(182, 170); g.stroke();
    g.fillStyle = '#22252b'; g.beginPath(); g.arc(128, 84, 15, 0, Math.PI*2); g.fill(); g.fillRect(110, 102, 36, 50);   /* a figure behind the bar */
    g.strokeStyle = '#d7261e'; g.beginPath(); g.moveTo(74, 62); g.lineTo(182, 170); g.stroke();
    g.fillStyle = '#d7261e'; g.font = '800 54px "IBM Plex Sans KR", system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('출입금지', 128, 262); });
  const safeTex = canvasTex(512, 128, g=>{ g.fillStyle = '#ffffff'; g.fillRect(0, 0, 512, 128); g.strokeStyle = '#1f8f4d'; g.lineWidth = 10; g.strokeRect(5, 5, 502, 118);
    g.fillStyle = '#1f8f4d'; g.fillRect(52, 28, 26, 72); g.fillRect(29, 51, 72, 26); g.fillStyle = '#22252b'; g.font = '800 74px "IBM Plex Sans KR", system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('안전제일', 306, 68); });
  const flat = map=> new THREE.MeshBasicMaterial({map});
  const board = (parent, w, h, map, x, y, z, ry=0)=>{ const m = flat(map); [0, Math.PI].forEach(tw=>{ const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); p.position.set(x, y, z); p.rotation.y = ry + tw; p.translateZ(0.06); parent.add(p); }); };   /* readable from both sides: two faces back to back, never mirrored */
  const ORANGE = mat(0xff7a1a), BEACON = new THREE.MeshBasicMaterial({color:0x7a5200});
  [[-31,-16,31,-16],[31,-16,31,16],[31,16,-31,16],[-31,16,-31,-16]].forEach(([x0,z0,x1,z1])=>{ const L = Math.hypot(x1-x0, z1-z0), ry = -Math.atan2(z1-z0, x1-x0), mx = (x0+x1)/2, mz = (z0+z1)/2;
    [2.0, 3.5].forEach(y=>{ add(site, BOX(L, 0.75, 0.16), new THREE.MeshLambertMaterial({map:hazTex(L/5)}), mx, y, mz, false).rotation.y = ry; });
    const net = new THREE.Mesh(new THREE.PlaneGeometry(L, 3.1), new THREE.MeshBasicMaterial({map:netTex(L/1.5, 2), alphaTest:0.5, side:THREE.DoubleSide})); net.position.set(mx, 1.2 + 1.55, mz); net.rotation.y = ry; site.add(net);
    const n = Math.round(L/8); for(let k = 0; k < n; k++){ const u = k/n; add(site, BOX(0.36, 3.4, 0.36), ORANGE, x0+(x1-x0)*u, 1.2, z0+(z1-z0)*u, false); }
    add(site, CYL(0.42, 0.42, 0.7, 10), BEACON, x0, 4.6, z0, false); add(site, CYL(0.5, 0.5, 0.18, 10), mat(0x22252b), x0, 4.5, z0, false); });
  /* 출입금지: on tall posts just outside the boards, two at the front and one on every other side */
  [[-21, 16.5, 0], [21, 16.5, 0], [0, -16.5, Math.PI], [31.5, 0, Math.PI/2], [-31.5, 0, -Math.PI/2], [-31.5, 11, -Math.PI/2]].forEach(([x, z, ry])=>{ const g = new THREE.Group(); g.position.set(x, 1.2, z); g.rotation.y = ry; site.add(g);
    add(g, BOX(0.3, 6.6, 0.3), mat(0x3a3f4a), 0, 0, -0.2, false); board(g, 3.4, 4.25, stopTex, 0, 5.4, 0); });
  /* banners on the scaffolds, facing the front */
  { const warn = signTex('관계자 외 출입금지', {bg:'#d7261e', fg:'#ffffff', size:64, w:512, h:108}), reb = signTex('REBUILDING', {bg:'#ffd400', fg:'#22252b', size:72, w:512, h:124});
    [[1, 12.3], [-1, -12.3]].forEach(([f, z])=>{ board(site, 16, 4, safeTex, -15*f, 19.4, z); board(site, 16, 3.4, warn, 15*f, 19.1, z); });
    board(site, 14, 3.4, reb, 0, 6.2, -16.6); [-6.4, 6.4].forEach(x=> add(site, BOX(0.4, 7.9, 0.4), mat(0x3a3f4a), x, 0, -16.6, false));   /* the path runs along this side */
    board(site, 14, 3.4, reb, 0, 6.2, 16.6); }
  /* an excavator parked in the gap between the scaffolds, boom towards the front */
  { const ex = new THREE.Group(); ex.position.set(0, 1.2, -5); ex.rotation.y = Math.PI/2; ex.scale.setScalar(1.15); site.add(ex);
    const YL = mat(0xf2b705), DK = mat(0x2b2f36);
    [-1.5, 1.5].forEach(z=> add(ex, BOX(5.4, 1.1, 1.1), DK, 0, 0, z, false)); add(ex, BOX(4.4, 1.7, 3.4), YL, 0.3, 1.1, 0, false); add(ex, BOX(1.5, 1.0, 3.2), DK, 2.0, 1.4, 0, false);
    add(ex, BOX(1.9, 1.9, 1.5), mat(0x39424e), -0.4, 2.8, -0.9, false); add(ex, BOX(2.0, 0.2, 1.6), YL, -0.4, 4.7, -0.9, false);
    const boom = add(ex, BOX(0.7, 7, 0.7), YL, -1.5, 2.8, 0.7, false); boom.rotation.z = 0.8;
    const stick = add(ex, BOX(0.5, 5, 0.5), YL, -6.52, 7.68, 0.7, false); stick.rotation.z = 2.6;
    add(ex, BOX(1.5, 1.3, 1.5), DK, -9.3, 2.3, 0.7, false).rotation.z = 0.5; }
  /* materials under the scaffolds: pipes, cement bags, a pile under a blue tarp */
  [[0, 0], [0.8, 0], [1.6, 0], [0.4, 0.68], [1.2, 0.68]].forEach(([dz, dy])=>{ const p = add(site, new THREE.CylinderGeometry(0.38, 0.38, 11, 8).rotateZ(Math.PI/2), mat(0x9aa1ab), -15, 1.6 + dy, -3 + dz, false); });
  [[0, 0, 0], [0, 0.7, 0.1], [2.3, 0, -0.1], [1.1, 1.4, 0.2]].forEach(([dx, dy, r])=>{ add(site, BOX(2.1, 0.7, 1.3), mat(0xcfc6b0), 10 + dx, 1.2 + dy, 2.5, false).rotation.y = r; });
  { const tp = add(site, BOX(6, 2.3, 4), mat(0x2b6fd6), 12.5, 1.2, -4.2, false); tp.rotation.y = 0.12; add(site, BOX(6.3, 0.25, 0.3), mat(0xe8e8e8), 12.5, 2.6, -4.2, false).rotation.y = 0.12; }
  poweredAnim(t=>{ BEACON.color.setHex(t > 0 && (t*1.4) % 1 < 0.5 ? 0xffb300 : 0x7a5200); });   /* the corner lamps blink only while the park has power */
'''
s = s[:a] + NEW + s[b:]
# the old one-sided REBUILDING plane goes (the two-faced board replaces it); its posts stay
i = s.index("  { const sg = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.4)"); j = s.index("sg.position.set(0, 6.2, 16.6); site.add(sg); ", i) + len("sg.position.set(0, 6.2, 16.6); site.add(sg); ")
k = s.index("\n", j); line = s[j:k]; assert line.rstrip().endswith("}"), line
s = s[:i] + "  " + line.rstrip()[:-1].rstrip() + s[k:]
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]; s = s.replace(old, new)
rep("window.__vikOpen = ()=> select(VIK_B.i, true);",
    "window.__vikOpen = ()=> select(VIK_B.i, true);\n"
    "window.__vikCentre = ()=>{ const v = VK.vik.getWorldPosition(new THREE.Vector3()); return [v.x, v.z]; };\n"
    "window.__vikEye = (ex, ez, cx, cz, h=7)=> flyTo(new THREE.Vector3(ex, G + h, ez), new THREE.Vector3(cx, G + 10, cz), 10);")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8')); print('ok', len(s))
