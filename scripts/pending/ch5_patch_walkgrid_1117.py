# 2026-11-17 걷기 판정 보강(벽 통과): ① 몸 높이(0.9~1.5m)에 걸리는 선 면도 벽으로 ② 인스턴스 물체(생울타리·나무·울타리·가로등·벤치)도 판정에
# ③ 놀이기구 둘레는 네모 상자 대신 실제 꼭짓점으로 잡은 볼록 껍질(둥근 울타리 밖 모서리가 이유 없이 막히던 것). 한 번만 적용.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# ① 면 규칙: 예전(1.6 아래에서 2.3 위까지 선 면) 또는 그 자리 땅에서 0.9~1.5m 사이를 0.15m 넘게 가리는 선 면
rep("const ymin = Math.min(va.y, vb.y, vc.y), ymax = Math.max(va.y, vb.y, vc.y); if(ymin > G + 1.6 || ymax < G + 2.3) continue;\n        nm.copy(e1.subVectors(vb, va)).cross(e2.subVectors(vc, va)); const L = nm.length(); if(!L || Math.abs(nm.y/L) > 0.6) continue;",
    "const ymin = Math.min(va.y, vb.y, vc.y), ymax = Math.max(va.y, vb.y, vc.y); if(ymax < G + 1.05 || ymin > G + 12) continue;\n        nm.copy(e1.subVectors(vb, va)).cross(e2.subVectors(vc, va)); const L = nm.length(); if(!L || Math.abs(nm.y/L) > 0.6) continue;\n"
    "        if(ymin > G + 1.6 || ymax < G + 2.3){ const gy = groundY((va.x + vb.x + vc.x)/3, (va.z + vb.z + vc.z)/3); if(Math.min(ymax, gy + 1.5) - Math.max(ymin, gy + 0.9) < 0.15) continue; }   /* body-height walls: hedges, planters, a dais, fence rails (2026-11-17) */")

# ② 인스턴스 물체: 놀이기구 밖의 것(기구 안은 아래 상자·껍질이 맡는다), 방문객·움직이는 것 제외. 물체의 실제 방향대로 바닥 면을 0.5m 간격으로 찍는다.
INST = (
"    /* instanced things stand in the way too (2026-11-17, user: 벽 통과): path hedges, tree trunks, bushes, fence posts and rails, lamp posts, benches */\n"
"    { const rideRoots = new Set(); IB.forEach(b=>{ if(b.c === 'ride' && b.mesh) rideRoots.add(b.mesh); }); const ib = new THREE.Box3(), pv = new THREE.Vector3();\n"
"      root.traverse(m=>{ if(!m.isInstancedMesh || /^(park-visitors|queue-visitors)/.test(m.name) || skipped(m)) return; for(let p = m; p; p = p.parent) if(rideRoots.has(p) || (p.userData && p.userData.dynamic) || /^(park-visitors|queue-visitors)/.test(p.name || '')) return;\n"
"        const g = m.geometry; if(!g || !g.attributes.position) return; if(!g.boundingBox) g.computeBoundingBox(); const lb = g.boundingBox, ly = (lb.min.y + lb.max.y)/2;\n"
"        for(let k = 0; k < m.count; k++){ m.getMatrixAt(k, _wgM); _wgM.premultiply(m.matrixWorld); ib.copy(lb).applyMatrix4(_wgM); const wx = ib.max.x - ib.min.x, wz = ib.max.z - ib.min.z; if(!(wx > 1e-6) || wx > 14 || wz > 14) continue;\n"
"          const gy = groundY((ib.min.x + ib.max.x)/2, (ib.min.z + ib.max.z)/2); if(Math.min(ib.max.y, gy + 1.5) - Math.max(ib.min.y, gy + 0.9) < 0.15) continue; if(ib.min.y > gy + 1.0 && Math.max(wx, wz) > 5) continue;   /* a crown overhead is not a wall */\n"
"          const e = _wgM.elements, sx = Math.hypot(e[0], e[2])*(lb.max.x - lb.min.x), sz = Math.hypot(e[8], e[10])*(lb.max.z - lb.min.z), nx = Math.max(1, Math.ceil(sx/0.5)), nz = Math.max(1, Math.ceil(sz/0.5)), pad = Math.max(sx, sz) > 3 ? 0.12 : 0;\n"
"          for(let i = 0; i <= nx; i++) for(let j = 0; j <= nz; j++){ const u = pad + (1 - 2*pad)*i/nx, v = pad + (1 - 2*pad)*j/nz; pv.set(lb.min.x + (lb.max.x - lb.min.x)*u, ly, lb.min.z + (lb.max.z - lb.min.z)*v).applyMatrix4(_wgM); if(inb(pv.x, pv.z)) a[at(pv.x, pv.z)] = 1; } } }); }\n")
rep("    // rides (2026-11-02, user: \"이유 없이 못 가는 곳\")", INST + "    // rides (2026-11-02, user: \"이유 없이 못 가는 곳\")")

# ③ 놀이기구: 큰 조각(합쳐진 메시)은 상자로 채우지 않고, 껍질은 그 조각의 실제 낮은 꼭짓점으로 잡는다
rep("bx.setFromObject(m); if(bx.isEmpty()) return; if(bx.min.y < G + 2.3 && bx.max.y > G + 0.6 && (bx.max.x - bx.min.x)*(bx.max.z - bx.min.z) < 3000) fillBox(",
    "bx.setFromObject(m); if(bx.isEmpty()) return; if(bx.min.y < G + 2.3 && bx.max.y > G + 0.6 && (bx.max.x - bx.min.x)*(bx.max.z - bx.min.z) < 400) fillBox(")
rep("boxes.push(bx.clone()); low = Math.min(low, bx.min.y); });\n      boxes.forEach(q=>{ if(q.min.y > Math.max(low, base) + 8) return; pts.push([q.min.x, q.min.z], [q.max.x, q.min.z], [q.max.x, q.max.z], [q.min.x, q.max.z]); });",
    "const q = bx.clone(); q.m = m; boxes.push(q); low = Math.min(low, bx.min.y); });\n      boxes.forEach(q=>{ const top = Math.max(low, base) + 8; if(q.min.y > top) return;\n"
    "        const pos = q.m.geometry && q.m.geometry.attributes.position; if(pos && !q.m.isInstancedMesh && (q.max.x - q.min.x)*(q.max.z - q.min.z) >= 400){ const st = Math.max(1, Math.floor(pos.count/1500)); let n = 0; for(let i = 0; i < pos.count; i += st){ va.fromBufferAttribute(pos, i).applyMatrix4(q.m.matrixWorld); if(va.y <= top){ pts.push([va.x, va.z]); n++; } } if(n >= 3) return; }   /* a merged piece: its real outline, not its box (2026-11-17) */\n"
    "        pts.push([q.min.x, q.min.z], [q.max.x, q.min.z], [q.max.x, q.max.z], [q.min.x, q.max.z]); });")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('patched', len(s))
