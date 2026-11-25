# 동굴 벽화 다섯 장을 평면 그림으로 뽑는다(닳은 상태 / 다 드러난 상태). 3D 동굴 없이 window.muralPaint만 부른다.
# python -I scripts/pending/ch5_shot_murals_flat.py <그림 폴더>
import asyncio, sys, os, pathlib, base64
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
JS = """async ()=>{ const out = []; for(let i = 0; i < MURAL_SCENES.length; i++){ for(const [k, k2] of [[0, 0], [1, 0], [1, 1]]){ if(k2 && !MURAL_SCENES[i].gap2) continue;
  const c = document.createElement('canvas'); c.width = 768; c.height = 480; const g = c.getContext('2d'); g.fillStyle = '#222'; g.fillRect(0, 0, 768, 480); muralPaint(g, i, k, k2); out.push([`mural${i + 1}_${k}${k2}`, c.toDataURL('image/png')]); } } return out; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(); await pg.goto((ROOT / 'chapter05/index.html').as_uri(), wait_until='domcontentloaded')
        for _ in range(200):
            if await pg.evaluate("typeof window.muralPaint === 'function'"): break
            await asyncio.sleep(.2)
        for name, url in await pg.evaluate(JS):
            open(os.path.join(OUT, name + '.png'), 'wb').write(base64.b64decode(url.split(',')[1]))
        await br.close(); print('ok')
asyncio.run(main())
