# 섬 걷기 감사: ① 정문에서 걸어서 닿지 않는 빈 땅·길·미션 목표 ② 걸을 수 있는 칸인데 사람 키 높이에 물체가 있는 곳(통과해서 걷게 되는 것) ③ 놀이기구 전원 상태.
# python scripts/pending/ch5_audit_walk.py <포트> <결과 json>
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT, OUT = sys.argv[1], sys.argv[2]
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
REACH = r"""() => { const b = __dbg; const g = b.walkGrid();
  const step = 2, X0 = g.X0, Z0 = g.Z0, W = Math.ceil(g.W/step), H = Math.ceil(g.H/step);
  const blk = new Uint8Array(W*H), seen = new Uint8Array(W*H);
  for(let j = 0; j < H; j++) for(let i = 0; i < W; i++){ const x = X0 + i*step + 1, z = Z0 + j*step + 1; blk[j*W + i] = b.walkBlocked(x, z) ? 1 : 0; }
  const sx = Math.floor((0 - X0)/step), sz = Math.floor((405 - Z0)/step); const q = [sz*W + sx]; seen[q[0]] = 1;
  while(q.length){ const c = q.pop(), i = c % W, j = (c / W) | 0; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const ni = i + di, nj = j + dj; if(ni < 0 || nj < 0 || ni >= W || nj >= H) continue; const n = nj*W + ni; if(seen[n] || blk[n]) continue; seen[n] = 1; q.push(n); } }
  const pocket = new Int32Array(W*H).fill(-1), pockets = [];
  for(let c = 0; c < W*H; c++){ if(blk[c] || seen[c] || pocket[c] >= 0) continue; const x = X0 + (c % W)*step, z = Z0 + ((c / W) | 0)*step; if(Math.hypot(x, z) > 640) continue;
    const st = [c]; pocket[c] = pockets.length; let n = 0, sx2 = 0, sz2 = 0; while(st.length){ const d = st.pop(); n++; sx2 += d % W; sz2 += (d / W) | 0; const i = d % W, j = (d / W) | 0; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const ni = i + di, nj = j + dj; if(ni < 0 || nj < 0 || ni >= W || nj >= H) continue; const e = nj*W + ni; if(blk[e] || seen[e] || pocket[e] >= 0) continue; pocket[e] = pockets.length; st.push(e); } }
    pockets.push({cells:n, x:Math.round(X0 + sx2/n*step), z:Math.round(Z0 + sz2/n*step)}); }
  const big = pockets.filter(p=> p.cells >= 12).sort((a, b)=> b.cells - a.cells);
  const nearOf = (x, z)=>{ let best = '', bd = 1e9; b.IB.forEach(o=>{ if(!o) return; const d = Math.hypot(x - o.cx, z - o.cz) - (o.r || 0); if(d < bd){ bd = d; best = o.label + (d < 0 ? '(안)' : `(${Math.round(d)}m)`); } }); return best; };
  const pathBad = []; b.pathSamples.forEach(([x, z])=>{ const i = Math.floor((x - X0)/step), j = Math.floor((z - Z0)/step), c = j*W + i; if(blk[c] || !seen[c]) pathBad.push([Math.round(x), Math.round(z), blk[c] ? 'blocked' : 'unreached']); });
  const pbG = {}; pathBad.forEach(p=>{ const k = nearOf(p[0], p[1]) + ' ' + p[2]; (pbG[k] = pbG[k] || []).push([p[0], p[1]]); });
  const pb = {}; for(const k in pbG){ const v = pbG[k]; pb[k] = [v.length, v[0], v[v.length - 1]]; }
  let T = {}; try{ const qd = b.quest(); T = {xylo:qd.XYLO_HIDE, naty:qd.NATY_HIDE, cave:qd.CAVE_MOUTH, yard:b.yardDoor && b.yardDoor(), lab:b.labDoor && b.labDoor(), station:b.station && b.station() && b.station().spot}; }catch(e){ T = {err:String(e)}; }
  const tg = {}; for(const k in T){ const v = T[k]; if(!v || !v.length){ tg[k] = 'n/a'; continue; } let ok = false; for(let dj = -3; dj <= 3 && !ok; dj++) for(let di = -3; di <= 3 && !ok; di++){ const i = Math.floor((v[0] - X0)/step) + di, j = Math.floor((v[1] - Z0)/step) + dj; if(seen[j*W + i]) ok = true; } tg[k] = [ok, Math.round(v[0]), Math.round(v[1])]; }
  /* every facility: is some reachable cell within 10 of its edge? */
  const fac = b.IB.filter(o=> o).map(o=>{ let best = 1e9; const R = (o.r || 0) + 14; for(let z = o.cz - R; z <= o.cz + R; z += step) for(let x = o.cx - R; x <= o.cx + R; x += step){ const i = Math.floor((x - X0)/step), j = Math.floor((z - Z0)/step); if(i < 0 || j < 0 || i >= W || j >= H || !seen[j*W + i]) continue; const d = Math.hypot(x - o.cx, z - o.cz) - (o.r || 0); if(d < best) best = d; } return [o.label, Math.round(best*10)/10]; }).filter(f=> f[1] > 4);
  return {pockets:big.slice(0, 30).map(p=> [p.cells*4, p.x, p.z, nearOf(p.x, p.z)]), pathBad:pathBad.length, pathBadBy:pb, targets:tg, farFacilities:fac}; }"""
SOLID = r"""() => { const b = __dbg, T = b.THREE, G = b.G, t0 = performance.now(); b.islRoot.updateMatrixWorld(true);
  const RIB = /^(public-path|facility-spur|phantom-approach|parking-exit|parking-entry|T-course-exit|course-entry|exam-hall-walk|lake-promenade|lake-west-link|lake-fishing-link|phantom-gate-link|ferry-to-gate|queue-arrival|queue-to-gate)$/, skipName = /^(park-visitors|queue-visitors|rico|zero|codex|naty)/;
  const shown = o=>{ for(let p = o; p; p = p.parent) if(!p.visible) return false; return true; };
  const labelOf = o=>{ for(let p = o; p; p = p.parent){ if(p.userData && p.userData.i != null && b.IB[p.userData.i]) return b.IB[p.userData.i].label; } return ''; };
  const LO = G + 0.6, HI = G + 2.2, CELL = 8, hash = new Map(), items = []; const bx = new T.Box3(), ib = new T.Box3(), M = new T.Matrix4();
  const put = (it)=>{ const q = it.box; if(q[3] < LO || q[2] > HI) return; if((q[1] - q[0]) > 300 && (q[5] - q[4]) > 300) return; const id = items.push(it) - 1; for(let i = Math.floor(q[0]/CELL); i <= Math.floor(q[1]/CELL); i++) for(let j = Math.floor(q[4]/CELL); j <= Math.floor(q[5]/CELL); j++){ const k = i*4096 + j; let a = hash.get(k); if(!a) hash.set(k, a = []); a.push(id); } };
  b.islRoot.traverse(o=>{ if(!(o.isMesh || o.isInstancedMesh) || o.isSkinnedMesh || RIB.test(o.name) || skipName.test(o.name) || !shown(o)) return; const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || m.visible === false || (m.transparent && m.opacity < 0.05)) return;
    if(!o.geometry.boundingBox) o.geometry.computeBoundingBox();
    if(o.isInstancedMesh){ for(let k = 0; k < o.count; k++){ o.getMatrixAt(k, M); M.premultiply(o.matrixWorld); ib.copy(o.geometry.boundingBox).applyMatrix4(M); if(!isFinite(ib.min.x) || ib.max.x - ib.min.x < 1e-6) continue; put({o, inst:true, box:[ib.min.x, ib.max.x, ib.min.y, ib.max.y, ib.min.z, ib.max.z]}); } return; }
    bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); if(!isFinite(bx.min.x)) return; put({o, inst:false, box:[bx.min.x, bx.max.x, bx.min.y, bx.max.y, bx.min.z, bx.max.z]}); });
  const rc = new T.Raycaster(), O = new T.Vector3(), D = new T.Vector3(0, -1, 0); const g = b.walkGrid(), out = new Map(), ST = 2.5; let n = 0, bad = 0;
  for(let z = g.Z0 + 1; z < g.Z0 + g.H; z += ST) for(let x = g.X0 + 1; x < g.X0 + g.W; x += ST){ if(Math.hypot(x, z) > 640 || b.walkBlocked(x, z)) continue; n++; const a = hash.get(Math.floor(x/CELL)*4096 + Math.floor(z/CELL)); if(!a) continue; let hit = null;
    for(const id of a){ const it = items[id], q = it.box; if(x < q[0] || x > q[1] || z < q[4] || z > q[5]) continue;
      if(it.inst){ if(x > q[0] + 0.15 && x < q[1] - 0.15 && z > q[4] + 0.15 && z < q[5] - 0.15){ hit = it; break; } continue; }
      O.set(x, G + 60, z); rc.set(O, D); rc.near = 0; rc.far = 70; const r = rc.intersectObject(it.o, false); if(r.some(h=> h.point.y > LO && h.point.y < HI)){ hit = it; break; } }
    if(!hit) continue; bad++; const o = hit.o, m = Array.isArray(o.material) ? o.material[0] : o.material; const q = hit.box; const k = [labelOf(o), o.geometry.type, m.color ? m.color.getHexString() : '', hit.inst ? 'inst' : '', b.onPath(x, z) ? '길' : ''].join('|');
    let e = out.get(k); if(!e) out.set(k, e = {n:0, pts:[], sz:[q[1] - q[0], q[3] - q[2], q[5] - q[4]].map(v=> Math.round(v*10)/10)}); e.n++; if(e.pts.length < 6) e.pts.push([Math.round(x), Math.round(z)]); }
  let rides = {}; try{ rides = b.rideState(); }catch(e){}
  return {ms:Math.round(performance.now() - t0), cells:n, bad, groups:[...out].map(([k, e])=> [k, e.n, e.sz, e.pts]).sort((a, b)=> b[1] - a[1]), rides}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 1300, 'height': 900}); errs = []
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
        r = {'reach': await pg.evaluate(REACH)}; r['solid'] = await pg.evaluate(SOLID)
        json.dump(r, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('errs', errs[:3]); await br.close()
    print('== 닿지 않는 빈 땅(㎡, x, z, 가까운 시설)'); [print('  ', p) for p in r['reach']['pockets']]
    print('== 길 표본 중 막힘·미도달', r['reach']['pathBad']); [print('  ', k, v) for k, v in r['reach']['pathBadBy'].items()]
    print('== 미션 목표', r['reach']['targets']); print('== 걸어서 4m 안으로 못 가는 시설', r['reach']['farFacilities'])
    s = r['solid']; print(f"== 걸을 수 있는 칸 {s['cells']} 중 키 높이에 물체가 있는 칸 {s['bad']} ({s['ms']}ms)")
    for k, n, sz, pts in s['groups'][:70]: print(f'  {n:>5} {k} 크기 {sz} 예 {pts[:4]}')
    print('== 놀이기구 전원', {k: v.get('on') for k, v in s['rides'].items()})
asyncio.run(main())
