# 캠퍼스에서 섬으로 처음 넘어갈 때의 끊김을 잰다(정적 서버 8097). 프레임 간격을 3초 동안 받아 가장 긴 멈춤과 0.1초 넘는 멈춤의 합을 찍는다.
# 첫 전환과 두 번째 전환(캠퍼스로 갔다가 다시)을 비교한다. python scripts/pending/ch5_measure_first_island.py [cpu배속]
import asyncio, sys, json
from playwright.async_api import async_playwright
THR = float(sys.argv[1]) if len(sys.argv) > 1 else 1
REC = """(id)=> new Promise(res=>{ const gaps = []; let last = performance.now(); const t0 = last; __dbg.setWorld(id, true);
  (function f(){ const n = performance.now(); gaps.push(n - last); last = n; if(n - t0 < 3000) requestAnimationFrame(f); else { const big = gaps.filter(g=> g > 100); res({frames:gaps.length, worst:Math.round(Math.max(...gaps)), stalled:Math.round(big.reduce((a, b)=> a + b, 0)), stalls:big.map(Math.round).slice(0, 8)}); } })(); })"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1180, 'height': 820})
        if THR > 1:
            cdp = await pg.context.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': THR})
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html', wait_until='domcontentloaded', timeout=180000)
        for _ in range(900):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3)
        info = await pg.evaluate("(()=>{ const i = __dbg.renderer.info; return {programs:i.programs ? i.programs.length : 0, geometries:i.memory.geometries, textures:i.memory.textures}; })()"); print('before', info)
        print('first  island', await pg.evaluate(REC, 'island'))
        info = await pg.evaluate("(()=>{ const i = __dbg.renderer.info; return {programs:i.programs ? i.programs.length : 0, geometries:i.memory.geometries, textures:i.memory.textures}; })()"); print('after', info)
        print('back   erica ', await pg.evaluate(REC, 'erica'))
        print('second island', await pg.evaluate(REC, 'island'))
        await br.close()
asyncio.run(main())
