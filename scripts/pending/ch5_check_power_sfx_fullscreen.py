# 2026-11-25 (사용자): ① 처음 들어가서 첫 탭에 전체 화면이 되는지 ② 전원 연출에서 하모니아·롤러코스터·관람차를 비출 때 각각 효과음이 나는지(SND.log에 이름이 쌓임).
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_check_power_sfx_fullscreen.py
import asyncio, sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
T = 10; API = 'http://127.0.0.1:8096'
HOOK = 'const _pwP = new THREE.Vector3()'
async def proxy(rt):
    r = rt.request; url = API + r.url[r.url.index('/api/void'):]
    try:
        resp = await rt.fetch(url=url); await rt.fulfill(response=resp)
    except Exception: await rt.abort()
async def main():
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src
    src = src.replace(HOOK, 'window.__pw = (d)=> parkWake(d || (()=>{})); window.__pwOn = ()=> !!PARK_WAKE; window.__ph = ()=> PARK_HOLD; window.__phSet = v=> { PARK_HOLD = v; }; ' + HOOK, 1)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, reduced_motion='no-preference'); pg = await ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/api/void/**', proxy)
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.request.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'pwsfx', 'tut': True}), headers={'content-type': 'application/json'})
        await pg.request.post(API + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
        await pg.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','pwsfx');localStorage.setItem('void-ctrl-seen','1');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=%d' % T, wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!__dbg.walkTo && !!window.__pw"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(2)
        fs0 = await pg.evaluate('!!document.fullscreenElement')
        await pg.mouse.click(640, 400); await asyncio.sleep(1)
        fs1 = await pg.evaluate('!!document.fullscreenElement')
        print(json.dumps({'fullscreenBefore': fs0, 'fullscreenAfterFirstTap': fs1}))
        await asyncio.sleep(6); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2)
        await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2)
        print(json.dumps({'parkHold': await pg.evaluate('__ph()'), 'walk': await pg.evaluate('!!__dbg.walk()')}))
        await pg.evaluate("__phSet(true); SND.log = []; __pw()"); await asyncio.sleep(1)
        print(json.dumps({'tourRunning': await pg.evaluate('__pwOn()')}))
        await asyncio.sleep(16)
        log = await pg.evaluate("SND.log.slice()")
        print(json.dumps({'sfx': log}, ensure_ascii=False))
        need = ['rideHarmonia', 'rideCoaster', 'rideWheel']; order = [n for n in log if n in need]
        print('PASS' if fs1 and order == need and not errs else 'FAIL', errs[:2])
        await br.close()
asyncio.run(main())
