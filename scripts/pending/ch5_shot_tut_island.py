# 튜토리얼에서 섬을 3D로 여는 대신 보여 줄 그림 두 장을 찍는다(전원이 끊긴 처음 상태, 화면 요소 없이 3D만).
#  img/tut_island.jpg   섬 전체(기본 시점)      img/tut_harmonia.jpg   하모니아 근처(튜토리얼 13번째 대사의 시점)
# 정적 서버 8097. 섬 모습을 고치면 다시 찍는다.  python scripts/pending/ch5_shot_tut_island.py
import asyncio, pathlib, io
from playwright.async_api import async_playwright
from PIL import Image, ImageEnhance
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = ROOT / 'chapter05/img'
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=3); errs = []   # 2배로 찍어 2560x1600으로 저장(태블릿에서 흐리지 않게, 사용자 2026-11-19)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert src.count(HOOK) == 1
        src = src.replace(HOOK, HOOK + " window.__cap = {camera, controls, HOME, MI, G, THREE, power:()=> parkPowerOn()};")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&hour=12', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__cap"): break
            except Exception: pass
            await asyncio.sleep(.25)
        print('renderer', await pg.evaluate("()=>{ const g = document.createElement('canvas').getContext('webgl'); const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '' }"))
        await asyncio.sleep(8)   # the entrance swoop
        print('power', await pg.evaluate("__cap.power()"), 'world', await pg.evaluate("__dbg.tutState().world"))
        await pg.evaluate("""()=>{ const cv = document.querySelector('#stage canvas') || document.querySelector('canvas'); const keep = new Set(); for(let p = cv; p; p = p.parentElement) keep.add(p);
          document.querySelectorAll('body *').forEach(e=>{ if(!keep.has(e) && !cv.contains(e)) e.style.setProperty('visibility', 'hidden', 'important'); }); }""")
        async def shot(name):
            await asyncio.sleep(2.5); png = await pg.screenshot(type='png'); im = Image.open(io.BytesIO(png)).convert('RGB').resize((3200, 2000), Image.LANCZOS); im = ImageEnhance.Color(ImageEnhance.Brightness(im).enhance(1.1)).enhance(1.18); p = OUT / name; im.save(p, 'JPEG', quality=90, optimize=True, progressive=True); print(name, im.size, p.stat().st_size)
        await pg.evaluate("()=>{ const c = __cap; c.camera.position.copy(c.HOME.tgt).lerp(c.HOME.pos, 0.66); c.controls.target.copy(c.HOME.tgt); c.controls.update(); }")
        await shot('tut_island.jpg')
        await pg.evaluate("()=>{ const c = __cap, b = c.MI.find(x=> x.id === 'dl-harmonia').b; c.controls.minDistance = 3; c.camera.position.set(b.cx + 95, c.G + 120, b.cz + 150); c.controls.target.set(b.cx, c.G + 20, b.cz); c.controls.update(); }")
        await shot('tut_harmonia.jpg')
        print('errs', errs); await br.close()
asyncio.run(main())
