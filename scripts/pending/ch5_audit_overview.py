# 섬 전체를 격자로 나눠 위에서 본 그림을 찍어 3×3 장씩 모은다(전체 눈 점검용).  python ch5_audit_overview.py <포트> <폴더> [칸 크기=220]
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
PORT, OUT = sys.argv[1], sys.argv[2]; C = int(sys.argv[3]) if len(sys.argv) > 3 else 220; os.makedirs(OUT, exist_ok=True)
async def main():
    cells = [(x, z) for z in range(-500, 521, C) for x in range(-500, 561, C) if (x*x + z*z)**.5 < 640]
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']); pg = await br.new_page(viewport={'width': 800, 'height': 800})
        await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }"); await asyncio.sleep(4)
        shots = []
        for k, (x, z) in enumerate(cells):
            await pg.evaluate("([cx, cz, h])=>{ const T = __dbg.THREE; __dbg.controls.minDistance = 3; __dbg.flyTo(new T.Vector3(cx, __dbg.G + h, cz + 1), new T.Vector3(cx, __dbg.G, cz), 10); }", [x, z, C*1.25]); await asyncio.sleep(1.6)
            f = os.path.join(OUT, f'c{k:02d}.png'); await pg.screenshot(path=f, timeout=60000); shots.append((x, z, f))
        await br.close()
    ft = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 20)
    for s in range(0, len(shots), 9):
        sh = Image.new('RGB', (1800, 1800))
        for j, (x, z, f) in enumerate(shots[s:s+9]):
            im = Image.open(f).convert('RGB').resize((600, 600)); d = ImageDraw.Draw(im); d.rectangle([0, 0, 150, 26], fill=(0, 0, 0)); d.text((4, 2), f'{x},{z}', fill=(255, 255, 0), font=ft); sh.paste(im, ((j % 3)*600, (j//3)*600))
        p = os.path.join(OUT, f'ov_{s//9}.png'); sh.save(p); print(p)
asyncio.run(main())
