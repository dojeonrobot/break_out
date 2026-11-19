# 전원 복구 연출(parkWake)을 바로 재생하며 시간대별로 찍는다(어둑 → 깜빡 → 번쩍 → 빛 고리 → 기구).  정적 서버 8097.  python ch5_shot_power.py <결과 폴더>
import asyncio, sys, pathlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
HOOK = "\n;window.__pw = ()=>{ walkerOpen = ()=> true; startWalk(PAIR); PARK_HOLD = true; rideSync(); setTimeout(()=> parkWake(()=>{ window.__pwDone = 1; }), 900); return !!walk; }; window.__pwk = ()=> PARK_WAKE ? +PARK_WAKE.k.toFixed(2) : -1;\n"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&team=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__pw === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1)
        print('walk', await pg.evaluate("__pw()")); await asyncio.sleep(.8); await pg.screenshot(path=f'{OUT}/pw_0_before.png')
        want = [0.35, 0.64, 0.75, 1.5, 2.4, 4.0, 6.5]; got = 0
        for _ in range(900):
            k = await pg.evaluate("__pwk()")
            if got < len(want) and k >= want[got]: await pg.screenshot(path=f'{OUT}/pw_{got + 1}_k{k}.png'); got += 1
            if got >= len(want) or (k < 0 and got > 0): break
            await asyncio.sleep(.02)
        print('shots', got, 'errs', errs[:3]); await br.close()
asyncio.run(main())
