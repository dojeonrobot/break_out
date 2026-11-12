"""2026-11-12 바이킹: 받침대와 배가 함께 든 어셈블리 파일(Onshape 「Assembly N.stl」)을 올리면 받침대는 서 있고 배만 흔들리게.
- 올린 파일을 이어진 덩어리로 나눈다(같은 꼭짓점을 쓰는 삼각형끼리 한 덩어리).
- 바닥에 닿은 덩어리 = 받침대, 떠 있는 덩어리 = 배. 받침대가 배 위를 가로지르는 봉을 찾아 그 봉을 회전축으로 삼는다.
- 봉을 못 찾으면(배만 올린 파일, 한 덩어리 파일) 전처럼 기본 받침대의 팔에 배로 건다.
python scripts/pending/ch5_patch_viking_assembly.py"""
import io, os, sys
P = os.path.join(os.path.dirname(__file__), '..', '..', 'chapter05', 'index.html')
s = io.open(P, encoding='utf-8', newline='').read()
assert '\r\n' not in s, 'index.html must be LF'
n0 = len(s)

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) 기본 받침대(A자 기둥·가로대·축)를 따로 떼어 낼 수 있는 묶음으로
rep("""  const PIV = 36;
  [-9, 9].forEach(z=>{
    [-1, 1].forEach(s=>{ const L = Math.hypot(18, PIV); const leg = add(vik, BOX(2, L, 2), mat(0x2f62b8), 0, 0, z); leg.position.set(s*18, 1.2, z); leg.rotation.z = s*Math.atan2(18, PIV); });
    add(vik, BOX(22, 1.2, 1.2), mat(0x3f74c8), 0, 16, z);
  });
  add(vik, new THREE.CylinderGeometry(1.2, 1.2, 22, 12).rotateX(Math.PI/2), mat(0x555a66), 0, PIV, 0);
""", """  const PIV = 36;
  const frm = new THREE.Group(); frm.userData.dynamic = true; vik.add(frm);   /* the built-in stand: taken off while a team's own stand (an uploaded assembly) is up (2026-11-12) */
  [-9, 9].forEach(z=>{
    [-1, 1].forEach(s=>{ const L = Math.hypot(18, PIV); const leg = add(frm, BOX(2, L, 2), mat(0x2f62b8), 0, 0, z); leg.position.set(s*18, 1.2, z); leg.rotation.z = s*Math.atan2(18, PIV); });
    add(frm, BOX(22, 1.2, 1.2), mat(0x3f74c8), 0, 16, z);
  });
  add(frm, new THREE.CylinderGeometry(1.2, 1.2, 22, 12).rotateX(Math.PI/2), mat(0x555a66), 0, PIV, 0);
""")

rep("""  Object.assign(VK, {vik, swing, hold, site});
  poweredAnim(t=>{ swing.rotation.z = VK.on ? Math.sin(t*0.75)*0.95 : 0; });
""", """  const stand = new THREE.Group(); stand.position.y = 1.2; stand.userData.dynamic = true; vik.add(stand);   /* an uploaded assembly (own stand + ship) sits on the deck */
  Object.assign(VK, {vik, swing, hold, site, frm, stand, pivot:null});
  poweredAnim(t=>{ const a = VK.on ? Math.sin(t*0.75) : 0; swing.rotation.z = a*0.95; if(VK.pivot) VK.pivot.rotation.z = a*(VK.amp || 0.95); });
""")

# 2) 어셈블리 판별
rep("""  if(tris > VIK_TRIS) throw new Error('면이 너무 많습니다');
  const turn = new THREE.Group(), fit = new THREE.Group(); turn.add(obj); fit.add(turn); fit.updateMatrixWorld(true);
""", """  if(tris > VIK_TRIS) throw new Error('면이 너무 많습니다');
  const asm = vikAssembly(obj, ext === 'glb'); if(asm){ asm.userData.tris = tris; return asm; }
  const turn = new THREE.Group(), fit = new THREE.Group(); turn.add(obj); fit.add(turn); fit.updateMatrixWorld(true);
""")

rep("""async function vikLoad(buf, ext){
""", """/* 2026-11-12 (user): the children upload the whole ride they modelled, stand and ship in one file (Onshape 「Assembly N.stl」).
   vikSplit cuts a triangle soup into connected pieces (triangles that share a vertex position, bit for bit). vikAssembly sorts the pieces:
   on the ground = stand, hanging = ship; the stand's bar that crosses above the ship is the axis the ship swings on.
   No such bar (a ship on its own, a single fused piece) -> null, and the model hangs from the built-in stand as before. */
function vikSplit(a){
  const nv = a.length/3, nt = Math.floor(nv/3), u = new Uint32Array(a.buffer, a.byteOffset, a.length); let cap = 8; while(cap < nv*2) cap <<= 1;
  const tab = new Int32Array(cap).fill(-1), id = new Int32Array(nv), par = new Int32Array(nv);
  for(let i = 0; i < nv; i++){ const x = u[i*3], y = u[i*3+1], z = u[i*3+2]; let h = Math.imul(x, 73856093) ^ Math.imul(y, 19349663) ^ Math.imul(z, 83492791); h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d); h ^= h >>> 12; h &= cap - 1;
    for(;;){ const j = tab[h]; if(j < 0){ tab[h] = i; id[i] = i; break; } if(u[j*3] === x && u[j*3+1] === y && u[j*3+2] === z){ id[i] = j; break; } h = (h + 1) & (cap - 1); } par[i] = i; }
  const find = x=>{ while(par[x] !== x){ par[x] = par[par[x]]; x = par[x]; } return x; };
  for(let t = 0; t < nt; t++){ const r = find(id[t*3]); par[find(id[t*3+1])] = r; par[find(id[t*3+2])] = r; }
  const map = new Map(), cnt = [], ct = new Int32Array(nt);
  for(let t = 0; t < nt; t++){ const r = find(id[t*3]); let g = map.get(r); if(g === undefined){ g = cnt.length; map.set(r, g); cnt.push(0); } ct[t] = g; cnt[g]++; }
  const out = cnt.map(n=> ({a:new Float32Array(n*9), n:0, lo:[1e30, 1e30, 1e30], hi:[-1e30, -1e30, -1e30]}));
  for(let t = 0; t < nt; t++){ const c = out[ct[t]]; for(let k = 0; k < 9; k++){ const val = a[t*9+k], d = k%3; c.a[c.n++] = val; if(val < c.lo[d]) c.lo[d] = val; if(val > c.hi[d]) c.hi[d] = val; } }
  return out;
}
function vikAssembly(obj, own){
  obj.updateMatrixWorld(true); const comps = [], v = new THREE.Vector3();
  obj.traverse(o=>{ if(!o.isMesh) return; const g = o.geometry, p = g.attributes.position, ix = g.index, n = Math.floor((ix ? ix.count : p.count)/3)*3, a = new Float32Array(n*3);
    for(let i = 0; i < n; i++){ v.fromBufferAttribute(p, ix ? ix.getX(i) : i).applyMatrix4(o.matrixWorld); a[i*3] = v.x + 0; a[i*3+1] = v.y + 0; a[i*3+2] = v.z + 0; }
    const m = Array.isArray(o.material) ? o.material[0] : o.material, col = own && m && m.color ? m.color.getHex() : null; vikSplit(a).forEach(c=>{ c.col = col; comps.push(c); }); });
  if(comps.length < 2 || comps.length > 400) return null;
  const lo = [1e30, 1e30, 1e30], hi = [-1e30, -1e30, -1e30]; comps.forEach(c=>{ for(let d = 0; d < 3; d++){ lo[d] = Math.min(lo[d], c.lo[d]); hi[d] = Math.max(hi[d], c.hi[d]); } });
  const H = hi[1] - lo[1]; if(!(H > 0)) return null;
  const len = (c, d)=> c.hi[d] - c.lo[d], diag = c=> Math.hypot(len(c, 0), len(c, 1), len(c, 2)), gy = lo[1] + H*0.03;
  const tryAxis = W=>{ const X = 2 - W;   /* W: the axis the bar runs along (the ride's width), X: the swing direction */
    const up = comps.filter(c=> c.lo[1] > gy), bars = up.filter(c=> len(c, W) >= 2.5*Math.max(len(c, X), len(c, 1))), hang = up.filter(c=> !bars.includes(c));
    if(!hang.length || hang.length === comps.length) return null;
    const core = hang.reduce((m, c)=> diag(c) > diag(m) ? c : m);
    const swing = hang.filter(c=> c.hi[W] >= core.lo[W] && c.lo[W] <= core.hi[W]), fixed = comps.filter(c=> !swing.includes(c));
    const fb = d=> [Math.min(...fixed.map(c=> c.lo[d])), Math.max(...fixed.map(c=> c.hi[d]))], fw = fb(W), tw = hi[W] - lo[W];
    if(!(fw[0] < core.lo[W] - tw*0.02 && fw[1] > core.hi[W] + tw*0.02)) return null;   /* the stand stands on both sides of the ship */
    if(len(core, X) < (hi[X] - lo[X])*0.45) return null;
    const mid = (core.lo[W] + core.hi[W])/2 + len(core, W)*0.013, lc = (core.lo[X] + core.hi[X])/2, lr = len(core, X)*0.3, ymin = core.lo[1] + len(core, 1)*0.5, hits = [];
    fixed.forEach(c=>{ const a = c.a; for(let i = 0; i < a.length; i += 9){ const w0 = a[i+W], w1 = a[i+3+W], w2 = a[i+6+W]; if(Math.min(w0, w1, w2) >= mid || Math.max(w0, w1, w2) <= mid) continue;
      const l0 = Math.min(a[i+X], a[i+3+X], a[i+6+X]), l1 = Math.max(a[i+X], a[i+3+X], a[i+6+X]), y0 = Math.min(a[i+1], a[i+4], a[i+7]), y1 = Math.max(a[i+1], a[i+4], a[i+7]);
      if((y0 + y1)/2 < ymin || (l0 + l1)/2 < lc - lr || (l0 + l1)/2 > lc + lr) continue; hits.push([l0, l1, y0, y1]); } });
    if(!hits.length) return null;   /* nothing of the stand crosses above the ship: not a ride with its own stand */
    const top = core.hi[1]; let near = hits.filter(h=> h[3] >= top - H*0.12 && h[2] <= top + H*0.05);
    if(!near.length){ let ty = -1e30; hits.forEach(h=>{ if(h[3] > ty) ty = h[3]; }); near = hits.filter(h=> h[3] >= ty - H*0.1); }
    let l0 = 1e30, l1 = -1e30, y0 = 1e30, y1 = -1e30; near.forEach(h=>{ if(h[0] < l0) l0 = h[0]; if(h[1] > l1) l1 = h[1]; if(h[2] < y0) y0 = h[2]; if(h[3] > y1) y1 = h[3]; });
    return {W, X, swing, fixed, fx:fb(X), fw, pl:(l0 + l1)/2, py:(y0 + y1)/2};
  };
  const r = tryAxis(2) || tryAxis(0); if(!r) return null;
  const {W, X} = r, sg = W === 0 ? -1 : 1, k = Math.min(52/Math.max(hi[X] - lo[X], 1e-9), 24/Math.max(hi[W] - lo[W], 1e-9), 38/H), ox = (r.fx[0] + r.fx[1])/2, ow = (r.fw[0] + r.fw[1])/2;
  const PX = (r.pl - ox)*k, PY = (r.py - lo[1])*k;
  let amp = 0.95;   /* swing as far as the built-in ride, less if a long ship would dip into the deck */
  r.swing.forEach(c=>{ const a = c.a; for(let i = 0; i < a.length; i += 3){ const dx = (a[i+X] - ox)*k - PX, dy = (a[i+1] - lo[1])*k - PY, rr = Math.hypot(dx, dy); if(rr <= PY - 0.6) continue;
    const lim = Math.atan2(Math.abs(dx), -dy) - Math.acos(Math.max(-1, Math.min(1, (PY - 0.6)/rr))); if(lim < amp) amp = lim; } }); amp = Math.max(0.3, amp);
  const build = (list, dc, px, py)=>{ let n = 0; list.forEach(c=> n += c.a.length); const pos = new Float32Array(n), col = new Float32Array(n), cc = new THREE.Color(); let o = 0;
    list.forEach(c=>{ cc.setHex(c.col == null ? dc : c.col); const a = c.a; for(let i = 0; i < a.length; i += 3, o += 3){ pos[o] = (a[i+X] - ox)*k - px; pos[o+1] = (a[i+1] - lo[1])*k - py; pos[o+2] = (a[i+W] - ow)*k*sg; col[o] = cc.r; col[o+1] = cc.g; col[o+2] = cc.b; } });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({vertexColors:true})); m.castShadow = m.receiveShadow = true; return m; };
  const fit = new THREE.Group(), piv = new THREE.Group(); piv.position.set(PX, PY, 0); fit.add(build(r.fixed, 0x2f62b8, 0, 0)); piv.add(build(r.swing, 0xc0392b, PX, PY)); fit.add(piv);
  fit.userData = {asm:true, pivot:piv, size:[(hi[X] - lo[X])*k, H*k, (hi[W] - lo[W])*k], parts:[r.fixed.length, r.swing.length], piv:[PX, PY], amp}; return fit;
}
async function vikLoad(buf, ext){
""")

# 3) 세우기·치우기
rep("""function vikDrop(){ while(VK.hold.children.length){ const o = VK.hold.children.pop(); o.traverse(x=>{ if(x.isMesh){ x.geometry.dispose(); (Array.isArray(x.material) ? x.material : [x.material]).forEach(m=>{ if(m.map) m.map.dispose(); m.dispose(); }); } }); } }
function vikSet(on, model, live){
  vikDrop(); if(model) VK.hold.add(model);
  VK.on = !!on; VK.site.visible = !on; VK.swing.visible = !!on;
  if(on){ if(VK.site.parent) VK.site.parent.remove(VK.site); } else if(!VK.site.parent) VK.vik.add(VK.site);   /* detached while restored: rideSweep draws every mesh whose own flag is visible */
""", """function vikDrop(){ VK.pivot = null; [VK.hold, VK.stand].forEach(h=>{ while(h.children.length){ const o = h.children.pop(); o.traverse(x=>{ if(x.isMesh){ x.geometry.dispose(); (Array.isArray(x.material) ? x.material : [x.material]).forEach(m=>{ if(m.map) m.map.dispose(); m.dispose(); }); } }); } }); }
function vikSet(on, model, live){
  vikDrop(); const asm = !!(model && model.userData.asm); if(model) (asm ? VK.stand : VK.hold).add(model); VK.pivot = asm ? model.userData.pivot : null; VK.amp = asm ? model.userData.amp : 0.95;
  VK.on = !!on; VK.site.visible = !on; VK.swing.visible = !!on;
  const att = (o, yes)=>{ if(yes){ if(!o.parent) VK.vik.add(o); } else if(o.parent) o.parent.remove(o); };   /* detached, not hidden: rideSweep draws every mesh whose own flag is visible */
  att(VK.site, !on); att(VK.frm, !asm); att(VK.swing, !asm);   /* an uploaded assembly brings its own stand and arms */
""")

rep("""window.__vik = ()=>{ return {on:VK.on, site:!!VK.site.parent, swing:VK.swing.visible, kids:VK.hold.children.length, rot:VK.swing.rotation.z, tris:VK.hold.children[0] ? VK.hold.children[0].userData.tris : 0, size:VK.hold.children[0] ? VK.hold.children[0].userData.size : null, team:vikTeam(), shown:VIK_SHOWN}; };""",
    """window.__vik = ()=>{ const m = VK.stand.children[0] || VK.hold.children[0]; return {on:VK.on, site:!!VK.site.parent, swing:VK.swing.visible && !!VK.swing.parent, kids:VK.hold.children.length + VK.stand.children.length, rot:VK.pivot ? VK.pivot.rotation.z : VK.swing.rotation.z, tris:m ? m.userData.tris : 0, size:m ? m.userData.size : null, asm:!!(m && m.userData.asm), parts:m ? m.userData.parts || null : null, piv:m ? m.userData.piv || null : null, amp:VK.amp || 0.95, frame:!!VK.frm.parent, team:vikTeam(), shown:VIK_SHOWN}; };""")

# 4) 태블릿 파일 선택 창: 확장자 거르기를 두면 안드로이드가 STL을 못 고르게 흐리는 일이 있어, 터치 기기에서는 거르지 않는다(확장자는 고른 뒤에 검사)
rep("""{type:'file', accept:'.stl,.obj,.glb', hidden:true}""", """{type:'file', accept:matchMedia('(pointer:coarse)').matches ? '' : '.stl,.obj,.glb', hidden:true}""")

# 5) 버튼 글자: 배만이 아니라 받침대까지 든 모델을 올린다
rep("""v ? '다른 배로 바꾸기' : '배 모델 올려 복구하기'""", """v ? '다른 모델로 바꾸기' : '바이킹 모델 올려 복구하기'""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', n0, '->', len(s))
