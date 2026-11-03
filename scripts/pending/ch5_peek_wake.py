# 주변 점등 파동을 반지름별로 멈춰 찍기 (2026-11-03): python ch5_peek_wake.py → shots_zone_return/peek_<기구>_<반지름>.png
import asyncio, base64, os, re, sys
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; HERE=os.path.dirname(os.path.abspath(__file__)); SHOT=os.path.join(HERE,'shots_zone_return'); os.makedirs(SHOT, exist_ok=True)
CAM={'dl-carousel':(135,100,34)}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-angle=swiftshader','--ignore-gpu-blocklist']); ctx=await b.new_context(viewport={'width':1280,'height':800})
        await ctx.route(re.compile(r'.*/api/void/.*'), lambda r: r.fulfill(status=503, body='x'))
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); ev=pg.evaluate; cdp=await ctx.new_cdp_session(pg)
        await pg.goto(f'{STATIC}/chapter05/index.html?world=island', wait_until='domcontentloaded')
        for i in range(120):
            if await ev("typeof window.__dbg !== 'undefined' && !!window.__dbg.wakePeek"): break
            await asyncio.sleep(0.5)
        await asyncio.sleep(8); await ev("document.querySelectorAll('body > div').forEach(d=>{ if(/몇 조/.test(d.textContent) && getComputedStyle(d).position==='fixed') d.style.display='none'; })")
        for rid,(x,z,r) in CAM.items():
            k=await ev(f"(()=>{{ const m = __dbg.rideState(); return true; }})()")
            await ev(f"window.__islandCam && window.__islandCam({x*1.0}, {z*1.0}, {r*6+160})"); await asyncio.sleep(3)
            for rad in (r*0.6, r*1.6, r*2.6):
                info=await ev(f"__dbg.wakePeek('{rid}', {rad})"); await asyncio.sleep(1.2)
                o=await cdp.send('Page.captureScreenshot',{'format':'png'}); open(os.path.join(SHOT,f'peek_{rid}_{int(rad)}.png'),'wb').write(base64.b64decode(o['data'])); print(rid, rad, info)
            await ev(f"__dbg.wakePeek('{rid}', null)")
        print('errs', errs); await b.close()
asyncio.run(main())
