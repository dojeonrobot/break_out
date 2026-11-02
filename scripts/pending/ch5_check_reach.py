import asyncio, json
from playwright.async_api import async_playwright
JS = r"""() => { const b = __dbg; const t0 = performance.now(); const g = b.walkGrid();
  const step = 2, X0 = g.X0, Z0 = g.Z0, W = Math.ceil(g.W/step), H = Math.ceil(g.H/step);
  const blk = new Uint8Array(W*H), seen = new Uint8Array(W*H);
  for(let j = 0; j < H; j++) for(let i = 0; i < W; i++){ const x = X0 + i*step + 1, z = Z0 + j*step + 1; blk[j*W + i] = b.walkBlocked(x, z) ? 1 : 0; }
  // start at the gate road
  const sx = Math.floor((0 - X0)/step), sz = Math.floor((405 - Z0)/step); const q = [sz*W + sx]; seen[q[0]] = 1;
  while(q.length){ const c = q.pop(), i = c % W, j = (c / W) | 0; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const ni = i + di, nj = j + dj; if(ni < 0 || nj < 0 || ni >= W || nj >= H) continue; const n = nj*W + ni; if(seen[n] || blk[n]) continue; seen[n] = 1; q.push(n); } }
  // free but unreachable pockets, grouped
  const pocket = new Int32Array(W*H).fill(-1), pockets = [];
  for(let c = 0; c < W*H; c++){ if(blk[c] || seen[c] || pocket[c] >= 0) continue; const x = X0 + (c % W)*step, z = Z0 + ((c / W) | 0)*step; if(Math.hypot(x, z) > 640) continue;
    const st = [c]; pocket[c] = pockets.length; let n = 0, sx2 = 0, sz2 = 0; while(st.length){ const d = st.pop(); n++; sx2 += d % W; sz2 += (d / W) | 0; const i = d % W, j = (d / W) | 0; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const ni = i + di, nj = j + dj; if(ni < 0 || nj < 0 || ni >= W || nj >= H) continue; const e = nj*W + ni; if(blk[e] || seen[e] || pocket[e] >= 0) continue; pocket[e] = pockets.length; st.push(e); } }
    pockets.push({cells:n, x:Math.round(X0 + sx2/n*step), z:Math.round(Z0 + sz2/n*step)}); }
  const big = pockets.filter(p=> p.cells >= 12).sort((a, b)=> b.cells - a.cells);
  const nearOf = (x, z)=>{ let best = '', bd = 1e9; b.IB.forEach(o=>{ const d = Math.hypot(x - o.cx, z - o.cz) - (o.r || 0); if(d < bd){ bd = d; best = o.label + (d < 0 ? '(안)' : `(${Math.round(d)}m)`); } }); return best; };
  // path samples: blocked or unreachable
  const pathBad = []; b.pathSamples.forEach(([x, z])=>{ const i = Math.floor((x - X0)/step), j = Math.floor((z - Z0)/step), c = j*W + i; if(blk[c] || !seen[c]) pathBad.push([Math.round(x), Math.round(z), blk[c] ? 'blocked' : 'unreached']); });
  const pbG = {}; pathBad.forEach(p=>{ const k = nearOf(p[0], p[1]) + ' ' + p[2]; pbG[k] = (pbG[k] || 0) + 1; });
  // targets
  const qd = b.quest(); const T = {xylo:qd.XYLO_HIDE, naty:qd.NATY_HIDE, cave:qd.CAVE_MOUTH, yard:b.yardDoor(), lab:b.labDoor && b.labDoor(), station:b.station() && b.station().spot};
  const tg = {}; for(const k in T){ const v = T[k]; if(!v){ tg[k] = 'n/a'; continue; } let ok = false; for(let dj = -3; dj <= 3 && !ok; dj++) for(let di = -3; di <= 3 && !ok; di++){ const i = Math.floor((v[0] - X0)/step) + di, j = Math.floor((v[1] - Z0)/step) + dj; if(seen[j*W + i]) ok = true; } tg[k] = ok; }
  const reach = seen.reduce((a, c)=> a + c, 0), free = blk.reduce((a, c)=> a + (1 - c), 0);
  return {ms:Math.round(performance.now() - t0), reachCells:reach, freeCells:free, pockets:big.slice(0, 25).map(p=> [p.cells*4 + 'm²', p.x, p.z, nearOf(p.x, p.z)]), pathBad:pathBad.length, pathBadBy:pbG, targets:tg}; }"""
async def run():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = await br.new_context(viewport={'width':1152,'height':720}); await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load'); await pg.wait_for_timeout(8000)
        await pg.evaluate("() => { try{ __dbg.tutEnd(); }catch(e){} }"); await pg.wait_for_timeout(500)
        await pg.evaluate("() => { __dbg.station && __dbg.station(); }")
        r = await pg.evaluate(JS); print(json.dumps(r, ensure_ascii=False, indent=0)); print('errs', errs[:2]); await br.close()
asyncio.run(run())
