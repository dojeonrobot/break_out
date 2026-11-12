# 섬의 한 구역을 글자 지도로 찍는다(# 막힘, = 길, . 걸을 수 있음) + 그 구역의 시설 목록 + 위에서 본 그림. 정적 서버 8097.
# python scripts/pending/ch5_probe_map.py <x0> <x1> <z0> <z1> [칸 크기] [그림 파일]
import asyncio, sys, os, json
from playwright.async_api import async_playwright
X0, X1, Z0, Z1 = [int(v) for v in sys.argv[1:5]]; ST = int(sys.argv[5]) if len(sys.argv) > 5 else 8; OUT = sys.argv[6] if len(sys.argv) > 6 else None
JS = """([x0, x1, z0, z1, st])=>{ const rows = []; for(let z = z0; z <= z1; z += st){ let o = ''; for(let x = x0; x <= x1; x += st) o += __dbg.walkBlocked(x, z) ? '#' : (__dbg.onPath(x, z) ? '=' : '.'); rows.push(String(z).padStart(5) + ' ' + o); } return rows; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1300, 'height': 900})
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3); await pg.evaluate("__dbg.walkGrid()")
        ib = await pg.evaluate("([x0, x1, z0, z1])=> __dbg.IB.filter(b=> b && b.cx > x0 && b.cx < x1 && b.cz > z0 && b.cz < z1).map(b=> [b.label, Math.round(b.cx), Math.round(b.cz), Math.round(b.r||0)])", [X0, X1, Z0, Z1])
        print(json.dumps(ib, ensure_ascii=False))
        print('x from', X0, 'step', ST)
        for r in await pg.evaluate(JS, [X0, X1, Z0, Z1, ST]): print(r)
        if OUT:
            cx, cz, h = (X0 + X1)/2, (Z0 + Z1)/2, max(X1 - X0, Z1 - Z0)*1.05
            await pg.evaluate("([cx, cz, h])=> __dbg.flyTo(new __dbg.THREE.Vector3(cx, __dbg.G + h, cz + 2), new __dbg.THREE.Vector3(cx, __dbg.G, cz), 10)", [cx, cz, h]); await asyncio.sleep(2.5)
            await pg.screenshot(path=OUT, timeout=60000)
        await br.close()
asyncio.run(main())
