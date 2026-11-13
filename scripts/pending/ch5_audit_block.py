# 섬 걷기 막힘 영역 감사: 그려진 물체(몸 높이 0.7~1.7m에 있는 모든 면)와 걷기 판정(walkBlocked)을 1m 칸마다 견준다.
#  P1 물체가 있는데 걸어서 통과되는 칸  P2 아무것도 없는데 막힌 경계  P3 배포 상태(조각 합침)와 감사 상태의 판정 차이  P4 지금 숨겨져 있어 판정에 안 들어간 물체
# python scripts/pending/ch5_audit_block.py <포트> <결과 폴더>
import asyncio, sys, json, os, base64
from playwright.async_api import async_playwright
from PIL import Image
PORT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
B64 = "const b64 = u8=>{ let s = ''; for(let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return btoa(s); };"
FINAL = "() => { " + B64 + r""" const b = __dbg, g = b.walkGrid(), n = g.W*g.H, f = new Uint8Array(n); for(let j = 0; j < g.H; j++) for(let i = 0; i < g.W; i++) f[j*g.W + i] = b.walkBlocked(g.X0 + i + 0.5, g.Z0 + j + 0.5) ? 1 : 0; return {X0:g.X0, Z0:g.Z0, W:g.W, H:g.H, f:b64(f)}; }"""
JS = "() => { " + B64 + r"""
  const b = __dbg, T = b.THREE, G = b.G, t0 = performance.now(); b.islRoot.updateMatrixWorld(true);
  const g = b.walkGrid(), W = g.W, H = g.H, X0 = g.X0, Z0 = g.Z0, N = W*H;
  const gy = new Float32Array(N), fin = new Uint8Array(N), inIsl = new Uint8Array(N);
  for(let j = 0; j < H; j++) for(let i = 0; i < W; i++){ const x = X0 + i + 0.5, z = Z0 + j + 0.5, c = j*W + i; gy[c] = b.groundY(x, z); fin[c] = b.walkBlocked(x, z) ? 1 : 0; inIsl[c] = Math.hypot(x, z) < 640 ? 1 : 0; }
  const shown = o=>{ for(let p = o; p; p = p.parent) if(!p.visible) return false; return true; };
  const labelOf = o=>{ for(let p = o; p; p = p.parent){ if(p.userData && p.userData.i != null && b.IB[p.userData.i]) return b.IB[p.userData.i].label; } return ''; };
  const RIB = /^(public-path|facility-spur|phantom-approach|parking-exit|parking-entry|T-course-exit|course-entry|exam-hall-walk|lake-promenade|lake-west-link|lake-fishing-link|phantom-gate-link|ferry-to-gate|queue-arrival|queue-to-gate)$/, skipName = /^(park-visitors|queue-visitors|rico|zero|codex|naty)/;
  const LO = 0.7, HI = 1.7; const own = new Int32Array(N).fill(-1), ylo = new Float32Array(N).fill(9), yhi = new Float32Array(N).fill(-9), owners = [];
  const a = new T.Vector3(), c2 = new T.Vector3(), d = new T.Vector3(); let tris = 0, samples = 0;
  const sample = (geo, M, oid)=>{ const pos = geo.attributes.position, ix = geo.index, n = ix ? ix.count : pos.count;
    for(let i = 0; i + 2 < n; i += 3){ const i0 = ix ? ix.getX(i) : i, i1 = ix ? ix.getX(i + 1) : i + 1, i2 = ix ? ix.getX(i + 2) : i + 2;
      a.fromBufferAttribute(pos, i0).applyMatrix4(M); c2.fromBufferAttribute(pos, i1).applyMatrix4(M); d.fromBufferAttribute(pos, i2).applyMatrix4(M);
      const ymin = Math.min(a.y, c2.y, d.y), ymax = Math.max(a.y, c2.y, d.y); if(ymax < G + LO - 1.3 || ymin > G + 30) continue;
      const me = Math.max(a.distanceTo(c2), c2.distanceTo(d), d.distanceTo(a)); if(!(me > 0)) continue; const k = Math.min(400, Math.max(1, Math.ceil(me/0.45))); tris++;
      for(let p = 0; p <= k; p++) for(let q = 0; q <= k - p; q++){ const u = p/k, v = q/k, w = 1 - u - v, x = a.x*u + c2.x*v + d.x*w, z = a.z*u + c2.z*v + d.z*w, ci = Math.floor(x) - X0, cj = Math.floor(z) - Z0; if(ci < 0 || cj < 0 || ci >= W || cj >= H) continue; const cc = cj*W + ci, y = a.y*u + c2.y*v + d.y*w - gy[cc]; samples++;
        if(y < LO || y > HI) continue; if(own[cc] < 0) own[cc] = oid; if(y < ylo[cc]) ylo[cc] = y; if(y > yhi[cc]) yhi[cc] = y; } } };
  const M = new T.Matrix4(), bx = new T.Box3(), hidden = new Map();
  b.islRoot.traverse(o=>{ if(!(o.isMesh || o.isInstancedMesh) || o.isSkinnedMesh || RIB.test(o.name) || skipName.test(o.name)) return; if(!o.geometry || !o.geometry.attributes.position) return;
    const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || m.visible === false) return;
    if(!o.geometry.boundingBox) o.geometry.computeBoundingBox();
    if(!shown(o)){ let top = o; for(let p = o; p; p = p.parent) if(!p.visible) top = p; bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); if(!isFinite(bx.min.x) || bx.max.y < G + LO || bx.min.y > G + 3) return; let e = hidden.get(top); if(!e) hidden.set(top, e = {n:0, box:new T.Box3(), label:labelOf(o), name:top.name || ''}); e.n++; e.box.union(bx); return; }
    if(m.transparent && m.opacity < 0.3) return;
    bx.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); const sz = [bx.max.x - bx.min.x, bx.max.y - bx.min.y, bx.max.z - bx.min.z].map(v=> Math.round(v*10)/10);
    const oid = owners.push({label:labelOf(o), geo:o.geometry.type, col:m.color ? m.color.getHexString() : '', sz:o.isInstancedMesh ? null : sz, inst:!!o.isInstancedMesh, base:o.isInstancedMesh ? null : Math.round((bx.min.y - G)*10)/10}) - 1;
    if(o.isInstancedMesh){ for(let k = 0; k < o.count; k++){ o.getMatrixAt(k, M); M.premultiply(o.matrixWorld); sample(o.geometry, M, oid); } } else sample(o.geometry, o.matrixWorld, oid); });
  /* ---- P1: something stands there, and the walker goes through it ---- */
  const key = o=> [o.label, o.geo, o.col, o.inst ? 'inst' : (o.sz || []).join('x')].join('|'); const G1 = new Map(); const thru = new Uint8Array(N);
  for(let c = 0; c < N; c++){ if(own[c] < 0 || fin[c] || !inIsl[c]) continue; const o = owners[own[c]], k = key(o); thru[c] = 1; let e = G1.get(k); if(!e) G1.set(k, e = {n:0, tall:0, path:0, pts:[], o}); e.n++; if(yhi[c] - ylo[c] > 0.55) e.tall++; if(g.path[c]) e.path++; if(e.pts.length < 6 || (e.n % 37 === 0 && e.pts.length < 12)) e.pts.push([X0 + (c % W), Z0 + ((c / W) | 0)]); }
  /* ---- P2: nothing stands there, and the walker is stopped ---- */
  const q = b.quest ? b.quest() : null;
  const rule = (x, z)=>{ const ci = Math.floor(x) - X0, cj = Math.floor(z) - Z0, c = cj*W + ci; if(b.mazeBlocked(x, z)) return 'maze'; if(g.a[c] && !g.path[c]) return 'grid'; if(Math.hypot(x, z) > 600) return 'edge'; return 'other'; };
  const bare = new Uint8Array(N); const near = (i, j, R)=>{ for(let dj = -R; dj <= R; dj++) for(let di = -R; di <= R; di++){ const ii = i + di, jj = j + dj; if(ii < 0 || jj < 0 || ii >= W || jj >= H) continue; if(own[jj*W + ii] >= 0) return true; } return false; };
  for(let j = 1; j < H - 1; j++) for(let i = 1; i < W - 1; i++){ const c = j*W + i; if(!fin[c] || !inIsl[c]) continue; if(fin[c - 1] && fin[c + 1] && fin[c - W] && fin[c + W]) continue; if(near(i, j, 3)) continue; bare[c] = 1; }
  const comp = new Int32Array(N).fill(-1), comps = [];
  for(let c = 0; c < N; c++){ if(!bare[c] || comp[c] >= 0) continue; const st = [c]; comp[c] = comps.length; const e = {n:0, x0:1e9, x1:-1e9, z0:1e9, z1:-1e9, sx:0, sz:0, rules:{}}; while(st.length){ const k = st.pop(), i = k % W, j = (k / W) | 0, x = X0 + i + 0.5, z = Z0 + j + 0.5; e.n++; e.sx += x; e.sz += z; e.x0 = Math.min(e.x0, x); e.x1 = Math.max(e.x1, x); e.z0 = Math.min(e.z0, z); e.z1 = Math.max(e.z1, z); if(e.n % 5 === 1){ const r = rule(x, z); e.rules[r] = (e.rules[r] || 0) + 1; }
      for(let dj = -2; dj <= 2; dj++) for(let di = -2; di <= 2; di++){ const ii = i + di, jj = j + dj; if(ii < 0 || jj < 0 || ii >= W || jj >= H) continue; const kk = jj*W + ii; if(bare[kk] && comp[kk] < 0){ comp[kk] = comps.length; st.push(kk); } } } comps.push(e); }
  const nearOf = (x, z)=>{ let best = '', bd = 1e9; b.IB.forEach(o=>{ if(!o) return; const dd = Math.hypot(x - o.cx, z - o.cz) - (o.r || 0); if(dd < bd){ bd = dd; best = o.label + (dd < 0 ? '(안)' : '(' + Math.round(dd) + 'm)'); } }); return best; };
  const solid = new Uint8Array(N); for(let c = 0; c < N; c++) solid[c] = own[c] >= 0 ? 1 : 0;
  return {ms:Math.round(performance.now() - t0), tris, samples, owners:owners.length, X0, Z0, W, H, G,
    p1:[...G1].map(([k, e])=> ({k, n:e.n, tall:e.tall, path:e.path, pts:e.pts, base:e.o.base})).sort((p, q)=> q.n - p.n),
    p2:comps.filter(e=> e.n >= 5).map(e=> ({n:e.n, cx:Math.round(e.sx/e.n), cz:Math.round(e.sz/e.n), box:[e.x0, e.x1, e.z0, e.z1].map(Math.round), rules:e.rules, near:nearOf(e.sx/e.n, e.sz/e.n)})).sort((p, q)=> q.n - p.n),
    hidden:[...hidden.values()].map(e=> ({label:e.label, name:e.name, n:e.n, box:[e.box.min.x, e.box.max.x, e.box.min.z, e.box.max.z].map(Math.round), h:Math.round((e.box.max.y - G)*10)/10})).sort((p, q)=> q.n - p.n),
    maps:{fin:b64(fin), solid:b64(solid), thru:b64(thru), bare:b64(bare), path:b64(g.path), grid:b64(g.a)}}; }"""
async def load(pw, query):
    br = await pw.chromium.launch(args=GPU); pg = await br.new_page(viewport={'width': 900, 'height': 600}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script("localStorage.setItem('void-sound','0');")
    await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island{query}', wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3)
    return br, pg, errs
async def main():
    async with async_playwright() as pw:
        br, pg, errs = await load(pw, ''); live = await pg.evaluate(FINAL); print('배포 상태 errs', errs[:2]); await br.close()
        br, pg, errs = await load(pw, '&nobatch=1'); r = await pg.evaluate(JS); print('감사 상태 errs', errs[:2], 'ms', r['ms'], '삼각형', r['tris'], '표본', r['samples'], '물체', r['owners']); await br.close()
    W, H, X0, Z0 = r['W'], r['H'], r['X0'], r['Z0']; mp = {k: base64.b64decode(v) for k, v in r['maps'].items()}; del r['maps']
    json.dump(r, open(os.path.join(OUT, 'block.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    # P3
    lf = base64.b64decode(live['f'])
    if (live['W'], live['H'], live['X0'], live['Z0']) != (W, H, X0, Z0): print('== P3 격자 크기가 다름', live['W'], live['H'], live['X0'], live['Z0'], 'vs', W, H, X0, Z0)
    else:
        fin = mp['fin']; more = [i for i in range(W*H) if lf[i] and not fin[i]]; less = [i for i in range(W*H) if fin[i] and not lf[i]]
        print(f'== P3 배포 상태에서만 막힘 {len(more)}칸 / 배포 상태에서만 뚫림 {len(less)}칸')
        for nm, arr in (('배포에서만 막힘', more), ('배포에서만 뚫림', less)):
            bk = {}
            for i in arr: k = ((X0 + i % W)//20*20, (Z0 + i//W)//20*20); bk[k] = bk.get(k, 0) + 1
            print('  ', nm, sorted(bk.items(), key=lambda t: -t[1])[:15])
    s = sum(mp['solid']); t = sum(mp['thru']); print(f"== 몸 높이에 물체가 있는 칸 {s}, 그중 걸어서 통과되는 칸 {t}")
    print('== P1 물체가 있는데 통과되는 것 (칸 수, 그중 키 큰 면, 그중 길 위 | 시설|모양|색|크기 | 바닥 높이 | 예)')
    for e in r['p1'][:110]: print(f"  {e['n']:>5} 큰면 {e['tall']:>5} 길 {e['path']:>4} | {e['k']} | 바닥 {e['base']} | {e['pts'][:5]}")
    print('== P2 아무것도 없는데 막힌 경계 (칸 수, 중심, 범위, 판정 종류, 가까운 시설)')
    for e in r['p2'][:80]: print(f"  {e['n']:>5} ({e['cx']},{e['cz']}) x {e['box'][0]}~{e['box'][1]} z {e['box'][2]}~{e['box'][3]} {e['rules']} {e['near']}")
    print('== P4 지금 숨겨져 있어 판정에 안 들어간 물체 묶음'); [print('  ', e) for e in r['hidden'][:40]]
    im = Image.new('RGB', (W, H), (250, 250, 246)); px = im.load(); fin, sol, thru, bare, path = mp['fin'], mp['solid'], mp['thru'], mp['bare'], mp['path']
    for j in range(H):
        for i in range(W):
            c = j*W + i; col = None
            if fin[c]: col = (205, 205, 205)
            if path[c]: col = (232, 212, 170)
            if sol[c] and fin[c]: col = (120, 120, 120)
            if thru[c]: col = (225, 40, 40)
            if bare[c]: col = (30, 90, 230)
            if col: px[i, j] = col
    im = im.resize((W*2, H*2), Image.NEAREST); p = os.path.join(OUT, 'block_map.png'); im.save(p); print('map', p, 'X0', X0, 'Z0', Z0)
asyncio.run(main())
