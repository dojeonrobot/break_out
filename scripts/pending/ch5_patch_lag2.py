# 2026-11-11 렉 2차(사용자: 1~3 전부 진행)
#  1. 조각 합치기: 명소 안의 평범한 단색 재질 조각을 색이 달라도 한 덩어리로(색은 꼭짓점 색으로 굽기) → 그리기 명령 수 감소
#  2. 그림자: 움직이는 물체는 그림자를 만들지 않고, 고정 그림자는 해·시점이 바뀔 때만 다시 그림(탐험 중 매 장 다시 그리지 않음)
#  3. 멀리 있는 것: 탐험 중 먼 방문객은 그리지 않음, 태블릿은 방문객 400명
# 사용: python ch5_patch_lag2.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)

# ---- 1. vertex-colour merge ----
swap("""  const keep = ['position','normal','uv','color'];
  function mergeUnder(node){""", """  const keep = ['position','normal','uv','color'];
  // A plain single-colour Lambert surface carries nothing but its colour, so pieces of different colours can share one mesh with the colour baked per vertex (2026-11-11).
  const plainMat = m => m && m.isMeshLambertMaterial && !m.map && !m.emissiveMap && !m.transparent && m.opacity === 1 && m.side === THREE.FrontSide && !m.vertexColors && !m.polygonOffset && m.blending === THREE.NormalBlending
    && m.depthWrite && m.depthTest && !m.alphaTest && !m.wireframe && !m.clippingPlanes && !m.userData.keep && m.emissive.getHex() === 0 && m.onBeforeCompile === THREE.Material.prototype.onBeforeCompile;
  const VC_MAT = [new THREE.MeshLambertMaterial({vertexColors:true}), new THREE.MeshLambertMaterial({vertexColors:true, flatShading:true})];
  function mergeUnder(node){""")
swap("""          const k = sig(c.material) + '|' + c.castShadow + '|' + c.receiveShadow + '|' + (c.userData.keepReal ? 1 : 0) + '|' + c.renderOrder + '|' + Object.keys(c.geometry.attributes).filter(n=>keep.includes(n)).sort().join();""",
"""          const plain = !NO_VC && plainMat(c.material) && !!c.geometry.attributes.normal;
          const k = (plain ? 'VC|' + (c.material.flatShading ? 1 : 0) : sig(c.material) + '|' + Object.keys(c.geometry.attributes).filter(n=>keep.includes(n)).sort().join()) + '|' + c.castShadow + '|' + c.receiveShadow + '|' + (c.userData.keepReal ? 1 : 0) + '|' + c.renderOrder;""")
swap("""    buckets.forEach(list=>{
      if(list.length < 2) return;
      const geos = list.map(c=>{ const g = c.geometry.index ? c.geometry.toNonIndexed() : c.geometry.clone(); g.clearGroups();
        Object.keys(g.attributes).forEach(n=>{ if(!keep.includes(n)) g.deleteAttribute(n); });
        g.applyMatrix4(rel(c)); return g; });
      const merged = mergeGeometries(geos, false); if(!merged) return;
      const f = list[0], mesh = new THREE.Mesh(merged, f.material);""", """    buckets.forEach((list, key)=>{
      if(list.length < 2) return;
      const vc = key.startsWith('VC|');
      const geos = list.map(c=>{ const g = c.geometry.index ? c.geometry.toNonIndexed() : c.geometry.clone(); g.clearGroups();
        Object.keys(g.attributes).forEach(n=>{ if(!keep.includes(n) || (vc && n === 'color')) g.deleteAttribute(n); });
        if(vc){ const n = g.attributes.position.count, col = new Float32Array(n*3), mc = c.material.color; for(let i = 0; i < n; i++){ col[i*3] = mc.r; col[i*3+1] = mc.g; col[i*3+2] = mc.b; } g.setAttribute('color', new THREE.BufferAttribute(col, 3)); }
        g.applyMatrix4(rel(c)); return g; });
      const merged = mergeGeometries(geos, false); if(!merged) return;
      const f = list[0], mesh = new THREE.Mesh(merged, vc ? VC_MAT[key.charAt(3) === '1' ? 1 : 0] : f.material);""")
swap("function batchIsland(){\n", "const NO_VC = /[?&]novc/.test(location.search);   // ?novc=1 keeps the old per-colour merge (comparison)\nfunction batchIsland(){\n")
# places whose tagged group is not the one the list entry points at (the harbour) were never merged: sweep every tagged group once
swap("""  IB.forEach(b=>{ if(b.c==='char') return; mergeUnder(b.mesh); prepGroup(b); });
}""", """  const mergedRoots = new Set(), charRoots = new Set(IB.filter(b=> b.c==='char').map(b=> b.mesh));
  IB.forEach(b=>{ if(b.c==='char') return; mergeUnder(b.mesh); mergedRoots.add(b.mesh); prepGroup(b); });
  const missed = []; islRoot.traverse(o=>{ if(o.userData.i !== undefined && !mergedRoots.has(o) && !charRoots.has(o) && !(IB[o.userData.i] && IB[o.userData.i].c === 'char')) missed.push(o); });
  missed.forEach(o=>{ if(!mergedRoots.has(o)){ mergeUnder(o); mergedRoots.add(o); } });
}""")

# ---- 2. shadows: moving things cast none, the static shadow map is redrawn only when the sun or the view moved (every 2nd frame while exploring, for the explorers' own shadows) ----
swap("""  missed.forEach(o=>{ if(!mergedRoots.has(o)){ mergeUnder(o); mergedRoots.add(o); } });
}""", """  missed.forEach(o=>{ if(!mergedRoots.has(o)){ mergeUnder(o); mergedRoots.add(o); } });
  const isChar = o=>{ for(let p = o; p; p = p.parent) if(charGroups.includes(p)) return true; return false; };
  const still = o=>{ o.traverse(c=>{ if(c.isMesh && !c.isInstancedMesh){ c.castShadow = false; c.userData.noShadow = true; } }); };
  DYN.forEach(o=>{ if(o.parent && !isChar(o)) still(o); }); islRoot.traverse(o=>{ if(o.userData.dynamic && !isChar(o)) still(o); });
}""")
swap("o.material = on ? ghostMat : o.userData.mat; o.castShadow = !on; }", "o.material = on ? ghostMat : o.userData.mat; o.castShadow = !on && !o.userData.noShadow; }")
swap("if(!renderer.shadowMap.autoUpdate){ shadowFrame++; if(walk || shadowFrame % 3 === 0 || shadowDirty){", "if(!renderer.shadowMap.autoUpdate){ shadowFrame++; if(shadowDirty || shadowFrame % (walk ? 2 : 20) === 0){")

# ---- 3. far things: fewer visitors on tablets, and while exploring the ones too far to see are not drawn ----
swap("const NW=PHONE?320:640,walkers", "const NW=PHONE?320:COARSE?400:640,walkers")
swap("positions[i]=[x,z];guests.set(i,x,groundY(x,z)+.04,z,yaw,t,moving);", "positions[i]=[x,z];guests.set(i,x,groundY(x,z)+.04,z,yaw,t,moving,walk&&!walk.fly&&Math.hypot(x-walk.x,z-walk.z)>230?0:.4);")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
