# 관람차 언덕 둘레 조사(정적 8097만). 가장 가까운 길 방향, 언덕 발치 둘레의 걷기 막힘, 길까지 거리, 비스듬한 화면.
# python scripts/pending/ch5_probe_ferris_back.py <그림 폴더>
import asyncio, sys, os, json
from playwright.async_api import async_playwright
OUT = sys.argv[1]
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1180, 'height': 820}); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400]))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&admin=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && typeof window.__islandCam==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        ev = pg.evaluate
        await ev("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }")
        await asyncio.sleep(2)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(3)
        FX, FZ = 216, -243
        r = await ev(f"""(()=>{{ const FX={FX}, FZ={FZ}, ps = __dbg.pathSamples || []; let best=null, bd=1e9; for(const [x,z] of ps){{ const d=Math.hypot(x-FX,z-FZ); if(d<bd){{bd=d;best=[x,z];}} }}
          const ring=[]; for(let a=0;a<360;a+=15){{ const c=Math.cos(a*Math.PI/180), s=Math.sin(a*Math.PI/180); const row={{a}}; for(const R of [82,88,94,104]){{ const x=FX+c*R, z=FZ+s*R; row['b'+R]=__dbg.walkBlocked(x,z)?1:0; }}
            let pd=1e9; for(const [x,z] of ps){{ const d=Math.hypot(x-(FX+c*90),z-(FZ+s*90)); if(d<pd) pd=d; }} row.path=Math.round(pd); row.edge=Math.round(Math.hypot(FX+c*90,FZ+s*90)); ring.push(row); }}
          return {{best, bd:Math.round(bd), bestAng: best ? Math.round(Math.atan2(best[1]-FZ,best[0]-FX)*180/Math.PI) : null, nps:ps.length, ring}}; }})()""")
        print(json.dumps({k: v for k, v in r.items() if k != 'ring'})); [print(x) for x in r['ring']]
        await ev("__dbg.stopWalk()"); await asyncio.sleep(1)
        for k, (x, z, d) in {'1_home': (FX, FZ, 230), '2_near': (FX, FZ, 150)}.items():
            await ev(f"__islandCam({x}, {z}, {d})"); await asyncio.sleep(3); await pg.screenshot(path=os.path.join(OUT, f'ferris_{k}.png'), timeout=60000)
        print('errors:', errs); await br.close()
asyncio.run(main())
