# 잔재 디자인 시안 그림: 롤러코스터 안쪽 잔디밭(탁 트인 곳)에 시안 A·B·C를 나란히 세워 찍는다. 시안 모델은 ch5_rem_mock.js에 있고 페이지 파일에는 넣지 않는다.
# 저장소 서버 8096(파일도 서빙)을 띄운 채: python -X utf8 scripts/pending/ch5_shot_rem_mock.py <그림 폴더>
import asyncio, re, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1]; MOCK = open(os.path.join(os.path.dirname(__file__), 'ch5_rem_mock.js'), encoding='utf-8').read()
CAM = "([x, y, z, tx, ty, tz])=>{ const b = __dbg; b.controls.target.set(tx, ty, tz); b.camera.position.set(x, y, z); b.camera.lookAt(tx, ty, tz); b.controls.update && b.controls.update(); }"
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1366, 'height': 768}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        async def hook(r):
            res = await r.fetch(); body = (await res.text()).replace('window.__remAim = ', 'window.__ev = s=> eval(s);\nwindow.__remAim = ', 1); await r.fulfill(response=res, body=body)
        await pg.route(re.compile(r'.*/chapter05/index\.html.*'), hook)
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__ev==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        await pg.evaluate("()=>{ const s = [...document.querySelectorAll('#teamPick button')].find(b=> b.textContent.trim() === '나중에'); if(s) s.click(); const st = document.createElement('style'); st.textContent = '#islandActions,#bar,.bar,#worldTabs,#topBar,header,#simBtn,#sndBtn,#adminBtn,[id^=void],#toast{visibility:hidden!important}'; document.head.appendChild(st); }")
        await pg.evaluate("(s)=> __ev(s)", MOCK); X, Z = -262, 262
        for i, d in enumerate(['A', 'B', 'C']): await pg.evaluate("([d, x, z])=> __remMock(d, x, z, 0.5)", [d, X + (i - 1)*13, Z])
        y = await pg.evaluate("([x, z])=> __dbg.groundY(x, z)", [X, Z]); await asyncio.sleep(1)
        await pg.evaluate(CAM, [X + 3, y + 7.5, Z + 27, X, y + 3.0, Z]); await asyncio.sleep(2); await pg.screenshot(path=os.path.join(OUT, 'rem_design_all.png'), timeout=60000)
        for i, d in enumerate(['A', 'B', 'C']):
            cx = X + (i - 1)*13
            await pg.evaluate(CAM, [cx + 4.5, y + 5.2, Z + 12.5, cx, y + 3.3, Z]); await asyncio.sleep(1.5); await pg.screenshot(path=os.path.join(OUT, f'rem_design_{d}.png'), timeout=60000); print('shot', d, flush=True)
        print('errs', errs); await br.close()
asyncio.run(main())
