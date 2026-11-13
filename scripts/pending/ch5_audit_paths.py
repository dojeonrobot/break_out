# 섬 길 감사: 그려진 길 띠(메시)에서 중심선을 뽑아 ① 길 위·길을 가로지르는 물체(수직·수평 광선) ② 길 밑의 걷기 막힘 칸(벽을 통과해 걷게 되는 곳)을 잰다.
# 결과는 JSON 파일로 저장한다. 분석은 ch5_audit_paths_report.py.
# python scripts/pending/ch5_audit_paths.py <포트> <결과 json>
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT, OUT = sys.argv[1], sys.argv[2]
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
REN = """() => { const g = document.createElement('canvas').getContext('webgl'); if(!g) return 'no-webgl'; const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'no-ext'; }"""
JS = r"""() => { const b = __dbg, T = b.THREE, G = b.G, t0 = performance.now();
  b.islRoot.updateMatrixWorld(true);
  const RIB = /^(public-path|facility-spur|phantom-approach|parking-exit|parking-entry|T-course-exit|course-entry|exam-hall-walk|lake-promenade|lake-west-link|lake-fishing-link|phantom-gate-link|ferry-to-gate|queue-arrival|queue-to-gate)$/;
  const shown = o=>{ for(let p = o; p; p = p.parent) if(!p.visible) return false; return true; };
  const labelOf = o=>{ for(let p = o; p; p = p.parent){ if(p.userData && p.userData.i != null && b.IB[p.userData.i]) return b.IB[p.userData.i].label; } return ''; };
  /* 1. routes from the drawn ribbons */
  const routes = [], cnt = {}; const v = new T.Vector3(), w = new T.Vector3();
  b.islRoot.traverse(o=>{ if(!o.isMesh || !RIB.test(o.name)) return; const p = o.geometry.attributes.position, n = (p.count - 52)/2; if(n < 2) return;
    const k = cnt[o.name] = (cnt[o.name] || 0); cnt[o.name]++; const pts = []; let wd = 0;
    for(let i = 0; i < n; i++){ v.fromBufferAttribute(p, i*2).applyMatrix4(o.matrixWorld); w.fromBufferAttribute(p, i*2 + 1).applyMatrix4(o.matrixWorld); if(!i) wd = v.distanceTo(w); pts.push([(v.x + w.x)/2, (v.z + w.z)/2, (v.y + w.y)/2]); }
    routes.push({name:o.name, k, hw:wd/2, pts, shown:shown(o), owner:labelOf(o)}); });
  /* 2. obstacle candidates */
  const skipName = /^(park-visitors|queue-visitors|rico|zero|codex|naty)/; const cand = []; const bx = new T.Box3();
  b.islRoot.traverse(o=>{ if(!(o.isMesh || o.isInstancedMesh) || o.isSkinnedMesh) return; if(RIB.test(o.name) || skipName.test(o.name)) return; if(!shown(o)) return;
    const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || m.visible === false || (m.transparent && m.opacity < 0.05)) return;
    for(let p = o; p; p = p.parent) if(p.isSkinnedMesh || (p.userData && p.userData.isChar)) return;
    if(o.isInstancedMesh){ cand.push({o, box:null}); return; }
    if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); if(!isFinite(bx.min.x)) return;
    cand.push({o, box:[bx.min.x, bx.max.x, bx.min.y, bx.max.y, bx.min.z, bx.max.z]}); });
  const desc = o=>{ const m = Array.isArray(o.material) ? o.material[0] : o.material; let sz = null; if(!o.isInstancedMesh){ bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); sz = [bx.max.x - bx.min.x, bx.max.y - bx.min.y, bx.max.z - bx.min.z].map(a=> Math.round(a*10)/10); }
    const chain = []; for(let p = o.parent; p && p !== b.islRoot && chain.length < 4; p = p.parent) if(p.name) chain.push(p.name);
    return {label:labelOf(o), name:o.name || '', geo:o.geometry.type, col:m.color ? m.color.getHexString() : '', sz, inst:!!o.isInstancedMesh, chain:chain.join('<'), base:sz ? Math.round((bx.min.y - G)*10)/10 : null}; };
  const rc = new T.Raycaster(); const hits = []; const O = new T.Vector3(), D = new T.Vector3();
  const cast = (ox, oy, oz, dx, dy, dz, far, x0, x1, y0, y1, z0, z1)=>{ O.set(ox, oy, oz); D.set(dx, dy, dz).normalize(); rc.set(O, D); rc.near = 0; rc.far = far; const out = [];
    for(const c of cand){ const q = c.box; if(q && (q[1] < x0 || q[0] > x1 || q[3] < y0 || q[2] > y1 || q[5] < z0 || q[4] > z1)) continue; const r = rc.intersectObject(c.o, false); for(const h of r) out.push(h); } return out; };
  const LO = G + 0.3, HI = G + 6.5;
  routes.forEach((r, ri)=>{ if(!r.shown) return; const P = r.pts, n = P.length;
    for(let i = 0; i < n; i++){ const a = P[Math.max(0, i - 1)], c = P[Math.min(n - 1, i + 1)]; let tx = c[0] - a[0], tz = c[1] - a[1]; const L = Math.hypot(tx, tz) || 1; tx /= L; tz /= L; const nx = -tz, nz = tx;
      for(const lane of [0, -0.6, 0.6]){ const x = P[i][0] + nx*r.hw*lane, z = P[i][1] + nz*r.hw*lane;
        /* vertical: anything standing in the walker's height band */
        for(const h of cast(x, G + 120, z, 0, -1, 0, 125, x, x, LO, 1e9, z, z)){ if(h.point.y > LO && h.point.y < HI){ hits.push({k:'v', ri, i, lane, x, z, y:h.point.y - G, d:desc(h.object)}); break; } }
        /* horizontal: anything crossing the path between this sample and the next */
        if(i < n - 1){ const x2 = P[i + 1][0] + nx*r.hw*lane, z2 = P[i + 1][1] + nz*r.hw*lane, far = Math.hypot(x2 - x, z2 - z);
          for(const hh of [1.2, 3.2]){ const r2 = cast(x, G + hh, z, x2 - x, 0, z2 - z, far, Math.min(x, x2), Math.max(x, x2), G + hh, G + hh, Math.min(z, z2), Math.max(z, z2)); if(r2.length){ r2.sort((p, q)=> p.distance - q.distance); const h = r2[0]; hits.push({k:'h', hh, ri, i, lane, x:h.point.x, z:h.point.z, y:hh, d:desc(h.object)}); } } } } } });
  /* 3. walk grid under the routes: path cells that sit on a blocked cell (the walker goes through whatever blocks it) */
  const g = b.walkGrid(); const cell = (x, z)=>{ const i = Math.floor(x - g.X0), j = Math.floor(z - g.Z0); return (i < 0 || j < 0 || i >= g.W || j >= g.H) ? -1 : j*g.W + i; };
  const under = []; routes.forEach((r, ri)=>{ r.pts.forEach((p, i)=>{ const a = r.pts[Math.max(0, i - 1)], c = r.pts[Math.min(r.pts.length - 1, i + 1)]; let tx = c[0] - a[0], tz = c[1] - a[1]; const L = Math.hypot(tx, tz) || 1; const nx = -tz/L, nz = tx/L;
    for(const lane of [0, -0.7, 0.7]){ const x = p[0] + nx*r.hw*lane, z = p[1] + nz*r.hw*lane, ci = cell(x, z); if(ci < 0) continue; under.push([ri, i, lane, Math.round(x*10)/10, Math.round(z*10)/10, g.a[ci], g.path[ci], b.walkBlocked(x, z) ? 1 : 0]); } }); });
  const ib = b.IB.map(x=> x ? {label:x.label, c:x.c, sub:x.sub, cx:x.cx, cz:x.cz, r:x.r || 0, h:x.h, shown:x.mesh ? shown(x.mesh) : null} : null);
  return {ms:Math.round(performance.now() - t0), G, cand:cand.length, routes, hits, under:under.filter(u=> u[5] || !u[6] || u[7]), underN:under.length, ib, occ:b.OCC, grid:{X0:g.X0, Z0:g.Z0, W:g.W, H:g.H}}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 1300, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island&nobatch=1', wait_until='domcontentloaded', timeout=120000)
        print('renderer:', await pg.evaluate(REN))
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3)
        r = await pg.evaluate(JS)
        json.dump(r, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
        print('ms', r['ms'], 'cand', r['cand'], 'routes', len(r['routes']), 'hits', len(r['hits']), 'under', len(r['under']), '/', r['underN']); print('errs', errs[:3])
        await br.close()
asyncio.run(main())
