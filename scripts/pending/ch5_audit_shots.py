# 섬의 여러 지점을 위에서 내려다본 그림으로 찍어 한 장에 모은다(실제 배포와 같은 batch 상태).
# python scripts/pending/ch5_audit_shots.py <포트> <결과 폴더> <지점 json: [[이름, x, z, 폭], ...]> [기울기 0~1]
import asyncio, sys, json, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
PORT, OUT, SPOTS = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8')); TILT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 900, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }"); await asyncio.sleep(4)
        files = []
        for k, (name, x, z, span) in enumerate(SPOTS):
            h = span*1.25
            await pg.evaluate("([cx, cz, h, t])=>{ const T = __dbg.THREE; __dbg.controls.minDistance = 3; __dbg.flyTo(new T.Vector3(cx, __dbg.G + h, cz + 2 + h*t), new T.Vector3(cx, __dbg.G, cz), 10); }", [x, z, h, TILT]); await asyncio.sleep(2.2)
            f = os.path.join(OUT, f'{k:02d}.png'); await pg.screenshot(path=f, timeout=60000); files.append((name, x, z, span, f))
        await br.close(); print('errs', errs[:3])
    try: ft = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 22)
    except Exception: ft = ImageFont.load_default()
    for s in range(0, len(files), 4):
        part = files[s:s+4]; sheet = Image.new('RGB', (1800, 1800), (255, 255, 255))
        for j, (name, x, z, span, f) in enumerate(part):
            im = Image.open(f).convert('RGB'); d = ImageDraw.Draw(im); t = f'{s+j}. {name} ({x},{z}) 폭 {span}'; d.rectangle([0, 0, 900, 34], fill=(0, 0, 0)); d.text((8, 4), t, fill=(255, 255, 0), font=ft)
            sheet.paste(im, ((j % 2)*900, (j//2)*900))
        p = os.path.join(OUT, f'sheet_{s//4:02d}.png'); sheet.save(p); print(p)
asyncio.run(main())
