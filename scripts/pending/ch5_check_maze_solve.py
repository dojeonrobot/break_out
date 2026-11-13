# 미로 점검: 0.5m 간격으로 걷기 판정을 채워 입구에서 모든 칸·한가운데까지 닿는지, 정답 경로가 몇 칸인지, 막다른 길이 몇 개인지 잰다. 정적 서버 포트는 인자.
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '8197'
JS = r"""() => { const b = __dbg, M = b.maze(); b.walkGrid(); const h = M.S/2, st = 0.5, N = Math.round((M.S + 16)/st), x0 = M.cx - h - 8, z0 = M.cz - h - 8;
  const blk = new Uint8Array(N*N), seen = new Uint8Array(N*N); for(let j = 0; j < N; j++) for(let i = 0; i < N; i++) blk[j*N + i] = b.walkBlocked(x0 + i*st, z0 + j*st) ? 1 : 0;
  const [ei, ej, side] = M.ent; let ex = M.cx - h + (ej + 0.5)*M.cell, ez = M.cz - h + (ei + 0.5)*M.cell; if(side === 'N') ez = M.cz - h - 4; if(side === 'S') ez = M.cz + h + 4; if(side === 'W') ex = M.cx - h - 4; if(side === 'E') ex = M.cx + h + 4;
  const q = [Math.round((ez - z0)/st)*N + Math.round((ex - x0)/st)]; seen[q[0]] = 1; while(q.length){ const c = q.pop(), i = c % N, j = (c/N) | 0; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const a = i + di, d = j + dj; if(a < 0 || d < 0 || a >= N || d >= N) continue; const k = d*N + a; if(seen[k] || blk[k]) continue; seen[k] = 1; q.push(k); } }
  let ok = 0; const miss = []; for(let i = 0; i < M.n; i++) for(let j = 0; j < M.n; j++){ const x = M.cx - h + (j + 0.5)*M.cell, z = M.cz - h + (i + 0.5)*M.cell; if(seen[Math.round((z - z0)/st)*N + Math.round((x - x0)/st)]) ok++; else miss.push([i, j]); }
  let dead = 0, far = 0; for(let i = 0; i < M.n; i++) for(let j = 0; j < M.n; j++){ const open = [!M.H[i][j] || (i === 0 && ei === 0 && ej === j && side === 'N'), !M.H[i + 1][j], !M.V[i][j], !M.V[i][j + 1]].filter(Boolean).length; if(open === 1 && M.dist[i][j] > 0) dead++; far = Math.max(far, M.dist[i][j]); }
  return {S:M.S, n:M.n, cell:M.cell, ent:M.ent, entrance:[ex, ez].map(Math.round), entBlocked:b.walkBlocked(ex, ez), cellsReached:ok, cells:M.n*M.n, miss:miss.slice(0, 8), solution:M.dist[ei][ej], farthest:far, deadEnds:dead, corridor:M.cell - M.TH - 0.9}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']); pg = await br.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(2); print(json.dumps(await pg.evaluate(JS), ensure_ascii=False)); print('errs', errs[:2]); await br.close()
asyncio.run(main())
