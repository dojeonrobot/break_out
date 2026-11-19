# 첫 화면(표지) 아래 로딩 바가 시간에 따라 차는지 잰다: 페이지 안에서 0.2초마다 ::after의 background-size를 적는다. 그림도 한 장 남긴다.
# 정적 서버 8097.  python ch5_shot_cover.py <결과 폴더>
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
INIT = "window.__bar = []; const t0 = performance.now(); const iv = setInterval(()=>{ const e = document.getElementById('intro'); if(!e) return; const ld = e.querySelector('.ld'); const s = ld ? getComputedStyle(ld, '::after') : {}; window.__bar.push([Math.round(performance.now() - t0), String(s.transform), getComputedStyle(e).display, e.className]); if(window.__bar.length > 40) clearInterval(iv); }, 200);"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, vp in (('pc', {'width': 1280, 'height': 800}), ('tab', {'width': 800, 'height': 1280})):
            pg = await br.new_page(viewport=vp); await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script(INIT)
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html', wait_until='commit', timeout=120000)
            await asyncio.sleep(1.0); await pg.screenshot(path=f'{OUT}/cover_{name}_1.png'); await asyncio.sleep(6)
            print(name, [(t, s.split(',')[0], c) for t, s, d, c in (await pg.evaluate('window.__bar'))[:26]]); await pg.close()
        await br.close()
asyncio.run(main())
