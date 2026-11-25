# 2026-11-25 (사용자: 태블릿에서 자일로가 대사 밑에 숨음): 미션 1에서 자일로를 찾아 대사가 뜬 장면을 태블릿 크기로 찍는다(3D 자일로가 대사 창에 가리는지).
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_xylo_meet_tablet.py <그림 폴더>
import asyncio, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
API = 'http://127.0.0.1:8096'; T = 9
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
async def proxy(rt):
    r = rt.request; url = API + r.url[r.url.index('/api/void'):]
    try:
        resp = await rt.fetch(url=url); await rt.fulfill(response=resp)
    except Exception: await rt.abort()
async def shot(pw, name, vp):
    br = await pw.chromium.launch(args=GPU)
    ctx = await br.new_context(viewport={'width': vp[0], 'height': vp[1]}, has_touch=True, is_mobile=True, user_agent=UA)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    await pg.route('**/api/void/**', proxy)
    dev = 'xm' + name
    await pg.request.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': dev, 'tut': True}), headers={'content-type': 'application/json'})
    await pg.request.post(API + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
    await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','%s');localStorage.setItem('void-ctrl-seen','1');" % dev)
    await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=%d' % T, wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!__dbg.walkTo && !!__dbg.target"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await asyncio.sleep(8); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2)
    await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2)
    got = False
    for _try in range(8):
        idle = 0
        while idle < 6:
            if await pg.evaluate('!!__dbg.quest().vn()'): await pg.evaluate('__dbg.quest().next()'); idle = 0
            else: idle += 1
            await asyncio.sleep(.25)
        await pg.evaluate('__dbg.walkTo(...__dbg.target())')
        for _ in range(40):
            if await pg.evaluate("__dbg.quest().vn()?.lines[0].who==='자일로'"): got = True; break
            await asyncio.sleep(.25)
        if got: break
    await asyncio.sleep(3)
    await pg.screenshot(path=os.path.join(OUT, f'xylo_{name}.png'))
    print(name, 'xylo dialogue', got, errs[:1])
    await br.close()
async def main():
    async with async_playwright() as pw:
        for name, vp in [('land', (1280, 800)), ('land_bar', (1280, 712)), ('port', (800, 1280))]:
            await shot(pw, name, vp)
asyncio.run(main())
