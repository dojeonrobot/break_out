# 2026-11-18: 코덱스 설득 뒤 실제 섬 환원 장면을 처음부터 끝까지 돌리며 단계마다 찍는다(동굴 앞 → 흐름이 번짐 → 섬 전체로 퍼져 스며듦 → 네이티 → 영상).
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_shot_restore.py <그림 폴더>
import asyncio, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1366, 'height': 768}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); ev = pg.evaluate; await pg.add_style_tag(content='#teamPick{display:none!important}')
        await ev("(()=>{ __t.restoreShow(); })()")
        VN = "document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''"
        said = []; n = 0; last = None; t0 = asyncio.get_event_loop().time(); nxt = 0
        while asyncio.get_event_loop().time() - t0 < 110:
            st = await ev("__restoreFx()"); t = await ev(VN); now = asyncio.get_event_loop().time() - t0
            key = (st or {}).get('phase'), bool(t)
            if t and (not said or said[-1] != t):
                said.append(t); await asyncio.sleep(1.0); n += 1; await pg.screenshot(path=f'{OUT}/r{n:02d}_talk.jpg', type='jpeg', quality=84); print(f'{now:5.1f}', n, 'talk', st, t[:34]); await ev('__dbg.quest().next()'); await ev('__dbg.quest().next()'); await asyncio.sleep(.2); continue
            if t: await ev('__dbg.quest().next()'); await asyncio.sleep(.15); continue
            if st and st['on'] and now >= nxt and st['phase'] in ('flow', 'spread', 'idle'):
                n += 1; await pg.screenshot(path=f'{OUT}/r{n:02d}_{st["phase"]}.jpg', type='jpeg', quality=84); print(f'{now:5.1f}', n, st); nxt = now + (2.4 if st['phase'] == 'flow' else 1.5)
            if not await ev("document.getElementById('cinema').hidden"): print(f'{now:5.1f}', 'film started'); break
            await asyncio.sleep(.25)
        print('lines', len(said), 'cine class left', await ev("document.body.classList.contains('cine')"), 'errs', errs[:4]); await br.close()
asyncio.run(main())
