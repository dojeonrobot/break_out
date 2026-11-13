# 스카이 루프 선로 감사: 선로 관(회색 튜브)에서 중심선을 뽑아, 열차가 지나가는 공간(선로 위 1.5·3.5, 좌우 0·±1.8)에 걸리는 물체를 찾는다.
# python scripts/pending/ch5_audit_track.py <포트>
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT = sys.argv[1]
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
JS = r"""() => { const b = __dbg, T = b.THREE, G = b.G; b.islRoot.updateMatrixWorld(true);
  let tube = null; b.islRoot.children.forEach(o=>{ if(o.isMesh && o.geometry.type === 'TubeGeometry' && o.geometry.parameters && o.geometry.parameters.tubularSegments === 720 && Math.abs(o.geometry.parameters.radius - 0.45) < 1e-6) tube = o; });
  if(!tube) return {err:'선로 관을 못 찾음'};
  const p = tube.geometry.attributes.position, per = p.count/721, C = []; const v = new T.Vector3();
  for(let i = 0; i < 720; i++){ let x = 0, y = 0, z = 0; for(let k = 0; k < per; k++){ v.fromBufferAttribute(p, i*per + k).applyMatrix4(tube.matrixWorld); x += v.x; y += v.y; z += v.z; } C.push([x/per, y/per, z/per]); }
  const shown = o=>{ for(let q = o; q; q = q.parent) if(!q.visible) return false; return true; };
  const labelOf = o=>{ for(let q = o; q; q = q.parent){ if(q.userData && q.userData.i != null && b.IB[q.userData.i]) return b.IB[q.userData.i].label; } return ''; };
  const cand = [], bx = new T.Box3(); b.islRoot.traverse(o=>{ if(!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh || o === tube || !shown(o)) return; if(/^(park-visitors|queue-visitors)/.test(o.name)) return; const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || m.visible === false || (m.transparent && m.opacity < 0.3)) return;
    if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); if(!isFinite(bx.min.x)) return; cand.push({o, q:[bx.min.x, bx.max.x, bx.min.y, bx.max.y, bx.min.z, bx.max.z]}); });
  const rc = new T.Raycaster(), O = new T.Vector3(), D = new T.Vector3(), out = new Map();
  for(let i = 0; i < 720; i++){ const a = C[i], c = C[(i + 1) % 720]; let tx = c[0] - a[0], tz = c[2] - a[2]; const L = Math.hypot(tx, tz) || 1; tx /= L; tz /= L; const nx = -tz, nz = tx;
    for(const lane of [0, -1.8, 1.8]) for(const hh of [1.9, 3.9]){ const x = a[0] + nx*lane, z = a[2] + nz*lane, y = a[1] + hh, x2 = c[0] + nx*lane, z2 = c[2] + nz*lane, y2 = c[1] + hh; O.set(x, y, z); D.set(x2 - x, y2 - y, z2 - z); const far = D.length(); D.normalize(); rc.set(O, D); rc.near = 0; rc.far = far;
      const x0 = Math.min(x, x2), x1 = Math.max(x, x2), z0 = Math.min(z, z2), z1 = Math.max(z, z2), y0 = Math.min(y, y2), y1 = Math.max(y, y2);
      for(const k of cand){ const q = k.q; if(q[1] < x0 || q[0] > x1 || q[3] < y0 || q[2] > y1 || q[5] < z0 || q[4] > z1) continue; const r = rc.intersectObject(k.o, false); if(!r.length) continue; const o = k.o, m = Array.isArray(o.material) ? o.material[0] : o.material;
        const key = [labelOf(o), o.geometry.type, m.color ? m.color.getHexString() : '', [q[1] - q[0], q[3] - q[2], q[5] - q[4]].map(n=> Math.round(n*10)/10).join('x'), 'y' + Math.round((q[2] - G)*10)/10].join('|'); let e = out.get(key); if(!e) out.set(key, e = {n:0, i0:i, i1:i, pts:[]}); e.n++; e.i1 = i; if(e.pts.length < 4) e.pts.push([Math.round(r[0].point.x), Math.round(r[0].point.y - G), Math.round(r[0].point.z)]); } } }
  return {railY:[Math.min(...C.map(c=> c[1])) - G, Math.max(...C.map(c=> c[1])) - G], n:cand.length, hits:[...out].map(([k, e])=> [k, e.n, e.i0, e.i1, e.pts]).sort((a, b)=> a[2] - b[2])}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU); pg = await br.new_page(viewport={'width': 900, 'height': 600})
        await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island&nobatch=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(3); r = await pg.evaluate(JS); await br.close()
        if 'err' in r: print(r); return
        print('선로 높이', r['railY'], '후보', r['n'], '걸리는 물체 묶음', len(r['hits']))
        for k, n, i0, i1, pts in r['hits']: print(f'  {n:>4} 구간 {i0}~{i1} {k} 예 {pts[:3]}')
asyncio.run(main())
