"""방문객 분포 점검(2026-11-25): 몇 명인지, 40×40 칸 몇 곳에 퍼져 있는지, 한 칸에 가장 많이 몰린 수.
사용: python -I ch5_check_visitor_spread.py   (정적 서버 8097 필요)"""
import asyncio, json
from playwright.async_api import async_playwright
J = r"""(async()=>{ const A = __dbg.islRoot.userData.visitorAudit; if(!A) return 'no audit';
  const pathCells = new Set(A.nodes.filter(n=>n.edges.length).map(n=> Math.floor(n.p.x/40) + ',' + Math.floor(n.p.z/40)));
  const res = [];
  for(let s = 0; s < 4; s++){ await new Promise(r=> setTimeout(r, 1500));
    const c = {}; A.positions.forEach(p=>{ if(!p) return; const k = Math.floor(p[0]/40) + ',' + Math.floor(p[1]/40); c[k] = (c[k]||0) + 1; });
    const v = Object.values(c).sort((a,b)=> b - a); res.push({cells:v.length, top5:v.slice(0,5), top10share:+(v.slice(0,10).reduce((a,b)=>a+b,0)/A.positions.filter(Boolean).length).toFixed(2)}); }
  return {walkers:A.walkers.length, pathCells:pathCells.size, samples:res}; })()"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width':1366,'height':768}); await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load', timeout=120000)
        for _ in range(60):
            if await pg.evaluate('typeof __dbg !== "undefined" && !!__dbg.renderer'): break
            await asyncio.sleep(1)
        await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(1); await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(3)
        print(json.dumps(await pg.evaluate(J), ensure_ascii=False))
        await pg.evaluate("__dbg.camera.position.set(0, 900, 900); __dbg.camera.lookAt(0,0,0)")
        await pg.screenshot(path='C:/Users/dlgus/AppData/Local/Temp/claude/da9ee7796ec0941b/eb69335a-5ca1-4220-92e1-452bc147d385/scratchpad/visitors.png')
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
