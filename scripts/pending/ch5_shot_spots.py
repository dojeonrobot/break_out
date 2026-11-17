# 섬의 정해 둔 자리들을 화면 요소 없이 찍는다(배치 확인용). 정적 서버 8097.  python scripts/pending/ch5_shot_spots.py <그림 폴더> [이름,...]
import asyncio, pathlib, sys, os
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']; HOOK = "const tutWorld = goWorld;"
SPOTS = {  # 이름: (카메라 x, 높이, z, 보는 곳 x, 높이, z)
 'gate_top': (0, 330, 452, 0, 0, 450), 'gate_oblique': (0, 120, 640, 0, 0, 440), 'fountain_top': (0, 300, 172, 0, 0, 170), 'boulevard': (0, 60, 330, 0, 10, 120),
 'sign1': (-70 + 14, 9, 120 + 14, -70, 3, 120), 'sign2': (40 + 14, 9, 200 + 14, 40, 3, 200), 'sign3': (110 + 14, 9, 0 + 14, 110, 3, 0), 'sign4': (-120 + 14, 9, 180 + 14, -120, 3, 180), 'plaza_south': (0, 150, 300, 0, 0, 130), 'flume': (358 + 60, 70, 173 + 90, 358, 8, 173), 'lake_deck': (354 + 20, 16, 262 + 26, 344, 2, 262)}
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU); pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); src = src.replace(HOOK, HOOK + " window.__cap = {camera, controls, G};")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__cap"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        await pg.evaluate("""()=>{ const cv = document.querySelector('#stage canvas') || document.querySelector('canvas'); const keep = new Set(); for(let p = cv; p; p = p.parentElement) keep.add(p);
          document.querySelectorAll('body *').forEach(e=>{ if(!keep.has(e) && !cv.contains(e)) e.style.setProperty('visibility', 'hidden', 'important'); }); }""")
        for name, (x, y, z, tx, ty, tz) in SPOTS.items():
            if ONLY and name not in ONLY: continue
            await pg.evaluate("([x,y,z,tx,ty,tz])=>{ const c = __cap; c.controls.minDistance = 1; c.camera.position.set(x, c.G + y, z); c.controls.target.set(tx, c.G + ty, tz); c.controls.update(); c.camera.lookAt(tx, c.G + ty, tz); }", [x, y, z, tx, ty, tz])
            await asyncio.sleep(1.8); await pg.screenshot(path=f'{OUT}/{name}.jpg', type='jpeg', quality=82)
        print('errs', errs); await br.close()
asyncio.run(main())
