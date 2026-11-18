# 조작 안내 카드(태블릿)에 넣는 걷는 화면 그림을 찍는다: 자일로를 처음 찾아가는 자리, 화면 요소 없이. 결과 chapter05/img/ctrl_walk.jpg (960x600)
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_shot_ctrl_walk.py
import asyncio, json, io, pathlib
from playwright.async_api import async_playwright
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = 11; B = 'http://127.0.0.1:8096'
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']); pg = await br.new_page(viewport={'width': 1280, 'height': 800})
        H = {'content-type': 'application/json'}
        await pg.request.post(B + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'ctl', 'tut': True}), headers=H)
        await pg.request.post(B + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={**H, 'X-Admin-Key': '0101'})
        await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','ctl');")
        await pg.goto(f'{B}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3); await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        for _ in range(30):
            if not await pg.evaluate("document.querySelectorAll('[data-on]').length"): break
            await pg.keyboard.press('Space'); await asyncio.sleep(.5)
        await pg.evaluate("(()=>{ const w = __dbg.walk(); w.pitch = -0.05; const cv = document.querySelector('canvas'); document.querySelectorAll('body *').forEach(e=>{ if(!e.contains(cv) && e !== cv) e.style.setProperty('visibility', 'hidden', 'important'); }); })()")
        await asyncio.sleep(1.5); png = await pg.screenshot(); await br.close()
    im = Image.open(io.BytesIO(png)).convert('RGB').resize((960, 600), Image.LANCZOS); out = ROOT / 'chapter05/img/ctrl_walk.jpg'; im.save(out, quality=80); print(out, out.stat().st_size)
asyncio.run(main())
