# 패치 뒤 페이지가 열리는지: pageerror와 __dbg 유무만 본다(정적 서버 8097). python -X utf8 ch5_load_errors.py
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=3', wait_until='domcontentloaded', timeout=120000)
        ok = False
        for _ in range(120):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined'"): ok = True; break
            except Exception: pass
            await asyncio.sleep(.5)
        print('dbg', ok, 'errs', errs[:3]); await br.close()
asyncio.run(main())
