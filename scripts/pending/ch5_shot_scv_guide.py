# Scaniverse 찍는 법 안내 창(#scvGuide)을 단계별로 찍는다(노트북·태블릿 세로·폰 가로).  정적 서버 8097.
#  python -X utf8 ch5_shot_scv_guide.py <그림 폴더>
import asyncio, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, vp in [('laptop', (1280, 800)), ('tabport', (800, 1280)), ('phoneland', (667, 375))]:
            ctx = await br.new_context(viewport={'width': vp[0], 'height': vp[1]})
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
            src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8').replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await ev("typeof window.__dbg!=='undefined' && !!window.__t"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7)
            await ev("(()=>{ for(const id of ['teamPick','intro']){ const e = document.getElementById(id); if(e){ e.style.display='none'; delete e.dataset.on; } } __t['scvGuide'](); })()")
            for i in range(8):
                await asyncio.sleep(1.0)
                if i in (0, 2, 5, 7) or name == 'laptop': await pg.screenshot(path=os.path.join(OUT, f'scv_{name}_{i + 1}.png'))
                await pg.keyboard.press('Space')
            await asyncio.sleep(.6); print(name, 'closed after last step:', await ev("!window.__scv()"), 'errors', errs[:2])
            await ctx.close()
        await br.close()
asyncio.run(main())
