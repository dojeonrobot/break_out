# 「다음 할 일」 미션 카드와 사과 표정 대사를 찍는다(글꼴·얼굴 잘림 확인).  정적 서버 8097.  python ch5_shot_card.py <결과 폴더>
import asyncio, sys, pathlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
HOOK = "\n;window.__nextCard = ()=>{ missionCard(QUESTS[0], {card:MCARDS.q1, label:'다음 할 일', go:'섬으로 가기'}); return 1; }; window.__sorry = ()=>{ say(STORY.labGame.slice(1)); return 1; };\n"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for dev, vp in (('pc', {'width': 1280, 'height': 800}), ('tab', {'width': 800, 'height': 1280})):
            pg = await br.new_page(viewport=vp); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
            src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');")
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=1', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await pg.evaluate("typeof window.__nextCard === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7)
            await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1)
            await pg.evaluate("__nextCard()"); await asyncio.sleep(1.2); await pg.screenshot(path=f'{OUT}/card_{dev}.png'); await pg.keyboard.press('Space'); await asyncio.sleep(.8)
            await pg.evaluate("__sorry()"); await asyncio.sleep(1.6); await pg.screenshot(path=f'{OUT}/sorry_zero_{dev}.png')
            for _ in range(4): await pg.keyboard.press('Space'); await asyncio.sleep(.5)
            await asyncio.sleep(1); await pg.screenshot(path=f'{OUT}/sorry_rico_{dev}.png'); print(dev, errs[:2]); await pg.close()
        await br.close()
asyncio.run(main())
