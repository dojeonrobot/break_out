# 섬 놀이기구 감사: 움직이는 물체가 지나가는 자리를 실제 진행 중에 따라가며, 가만히 있는 물체를 뚫고 지나가는 곳을 찾는다.
# 조각을 합치지 않은 상태(nobatch)에서 물체 상자를 미리 떠 두고, 그리기를 꺼서 프레임을 빠르게 돌린다.
# python scripts/pending/ch5_audit_rides.py <포트> <결과 json> [초=200]
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT, OUT = sys.argv[1], sys.argv[2]; SECS = int(sys.argv[3]) if len(sys.argv) > 3 else 200
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
SETUP = r"""() => { const b = __dbg, T = b.THREE, G = b.G; b.islRoot.updateMatrixWorld(true);
  const A = window.__aud = {snaps:[], objs:[], frames:0, hits:new Map(), pts:[], dist:0};
  b.islRoot.traverse(o=>{ if(o.isInstancedMesh || o.isSkinnedMesh) return; A.objs.push(o); });
  A.snap = ()=>{ A.snaps.push(A.objs.map(o=> o.matrixWorld.elements.slice(12, 15).concat(o.matrixWorld.elements.slice(0, 3)))); };
  A.snap(); return A.objs.length; }"""
ARM = r"""() => { const b = __dbg, T = b.THREE, G = b.G, A = window.__aud; const S = A.snaps, n = A.objs.length;
  const moving = new Set(); for(let i = 0; i < n; i++){ const a = S[0][i]; if(S.some(s=> s[i].some((v, k)=> Math.abs(v - a[k]) > 1e-3))) moving.add(A.objs[i]); }
  const roots = [...moving].filter(o=> !moving.has(o.parent));
  const shown = o=>{ for(let p = o; p; p = p.parent) if(!p.visible) return false; return true; };
  const labelOf = o=>{ for(let p = o; p; p = p.parent){ if(p.userData && p.userData.i != null && b.IB[p.userData.i]) return b.IB[p.userData.i].label; } return ''; };
  const under = new Set(); roots.forEach(r=> r.traverse(o=> under.add(o)));
  /* static candidates, hashed by box */
  const CELL = 8, hash = new Map(), items = [], bx = new T.Box3(); const skipName = /^(park-visitors|queue-visitors|rico|zero|codex|naty|public-path|facility-spur|queue-)/;
  b.islRoot.traverse(o=>{ if(!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh || under.has(o) || skipName.test(o.name) || !shown(o)) return; const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || m.visible === false || (m.transparent && m.opacity < 0.3)) return;
    if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); if(!isFinite(bx.min.x)) return; if((bx.max.x - bx.min.x) > 250 && (bx.max.z - bx.min.z) > 250) return;
    const q = [bx.min.x, bx.max.x, bx.min.y, bx.max.y, bx.min.z, bx.max.z], id = items.push({o, box:q}) - 1; for(let i = Math.floor(q[0]/CELL); i <= Math.floor(q[1]/CELL); i++) for(let j = Math.floor(q[4]/CELL); j <= Math.floor(q[5]/CELL); j++){ const k = i*4096 + j; let a = hash.get(k); if(!a) hash.set(k, a = []); a.push(id); } });
  /* tracked points: the biggest pieces of every moving root */
  const c = new T.Vector3(), sz = new T.Vector3();
  roots.forEach(r=>{ if(!shown(r)) return; const ms = []; r.traverse(o=>{ if(!o.isMesh || o.isInstancedMesh || !shown(o)) return; if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); o.geometry.boundingBox.getSize(sz); const ws = new T.Vector3().setFromMatrixScale(o.matrixWorld); ms.push({o, v:sz.x*ws.x*sz.y*ws.y*sz.z*ws.z, s:[sz.x*ws.x, sz.y*ws.y, sz.z*ws.z]}); });
    ms.sort((p, q)=> q.v - p.v); ms.slice(0, 3).forEach(m=>{ const m0 = Array.isArray(m.o.material) ? m.o.material[0] : m.o.material; m.o.geometry.boundingBox.getCenter(c); A.pts.push({o:m.o, lc:c.clone(), prev:null, root:r, d:0, desc:[labelOf(m.o), m.o.geometry.type, m0 && m0.color ? m0.color.getHexString() : '', m.s.map(v=> Math.round(v*10)/10).join('x'), r.name || ''].join('|')}); }); });
  const rc = new T.Raycaster(), cur = new T.Vector3(), dir = new T.Vector3();
  const desc = o=>{ const m = Array.isArray(o.material) ? o.material[0] : o.material; bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); return [labelOf(o), o.geometry.type, m.color ? m.color.getHexString() : '', [bx.max.x - bx.min.x, bx.max.y - bx.min.y, bx.max.z - bx.min.z].map(v=> Math.round(v*10)/10).join('x'), 'y' + Math.round((bx.min.y - G)*10)/10].join('|'); };
  b.islRoot.visible = false;   /* nothing to draw: frames run fast, the animation still advances */
  const tick = ()=>{ A.frames++; for(const p of A.pts){ p.o.updateWorldMatrix(true, false); cur.copy(p.lc).applyMatrix4(p.o.matrixWorld); if(p.prev){ const L = cur.distanceTo(p.prev); if(L > 0.02 && L < 12){ p.d += L; A.dist += L; dir.subVectors(cur, p.prev).normalize(); rc.set(p.prev, dir); rc.near = 0; rc.far = L;
          const x0 = Math.min(cur.x, p.prev.x), x1 = Math.max(cur.x, p.prev.x), z0 = Math.min(cur.z, p.prev.z), z1 = Math.max(cur.z, p.prev.z), y0 = Math.min(cur.y, p.prev.y), y1 = Math.max(cur.y, p.prev.y); const seen = new Set();
          for(let i = Math.floor(x0/CELL); i <= Math.floor(x1/CELL); i++) for(let j = Math.floor(z0/CELL); j <= Math.floor(z1/CELL); j++){ const a = hash.get(i*4096 + j); if(!a) continue; for(const id of a){ if(seen.has(id)) continue; seen.add(id); const it = items[id], q = it.box; if(q[1] < x0 || q[0] > x1 || q[3] < y0 || q[2] > y1 || q[5] < z0 || q[4] > z1) continue;
              const r = rc.intersectObject(it.o, false); if(!r.length) continue; const k = p.desc + '  >>  ' + desc(it.o); let e = A.hits.get(k); if(!e) A.hits.set(k, e = {n:0, pts:[]}); e.n++; if(e.pts.length < 5) e.pts.push([Math.round(r[0].point.x), Math.round(r[0].point.y - G), Math.round(r[0].point.z)]); } } }
        p.prev.copy(cur); } else p.prev = cur.clone(); }
    A.raf = requestAnimationFrame(tick); };
  A.raf = requestAnimationFrame(tick);
  return {moving:moving.size, roots:roots.length, pts:A.pts.length, statics:items.length}; }"""
DONE = r"""() => { const A = window.__aud; cancelAnimationFrame(A.raf); __dbg.islRoot.visible = true;
  const byRoot = new Map(); A.pts.forEach(p=>{ const k = p.desc.split('|')[0] || '(시설 없음)'; byRoot.set(k, (byRoot.get(k) || 0) + p.d); });
  return {frames:A.frames, dist:Math.round(A.dist), travelled:[...byRoot].map(([k, v])=> [k, Math.round(v)]).sort((a, b)=> b[1] - a[1]), hits:[...A.hits].map(([k, e])=> [k, e.n, e.pts]).sort((a, b)=> b[1] - a[1])}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 900, 'height': 600}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island&nobatch=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3)
        print('objs', await pg.evaluate(SETUP))
        for _ in range(8): await asyncio.sleep(2.5); await pg.evaluate("()=> __aud.snap()")
        print('arm', await pg.evaluate(ARM))
        await asyncio.sleep(SECS)
        r = await pg.evaluate(DONE); json.dump(r, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('frames', r['frames'], 'dist', r['dist'], 'errs', errs[:3]); print('== 시설별 움직인 거리'); [print('  ', t) for t in r['travelled'][:40]]
        print('== 뚫고 지나간 곳', len(r['hits']))
        for k, n, pts in r['hits'][:120]: print(f'  {n:>5} {k}  예 {pts[:3]}')
        await br.close()
asyncio.run(main())
