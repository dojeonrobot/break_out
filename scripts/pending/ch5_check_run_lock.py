# 2026-11-25 (사용자: 태블릿에서 RUN을 눌러 켠 상태일 때만 빨라야 함, 껐다 켰다 하면 버그)
# 조이스틱을 끝까지 밀어도 RUN이 꺼져 있으면 걷기 속도, RUN이 켜져 있으면 달리기 속도인지 잰다.
# 조이스틱이 잠깐 숨었다 다시 나와도 RUN 상태가 그대로인지, 걷기를 끝내면 꺼지는지 본다.
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_check_run_lock.py <그림 폴더>
import asyncio, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
T = 11
API = 'http://127.0.0.1:8096'
async def proxy(rt):
    r = rt.request; url = API + r.url[r.url.index('/api/void'):]
    try:
        resp = await rt.fetch(url=url); await rt.fulfill(response=resp)
    except Exception: await rt.abort()
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, has_touch=True, is_mobile=True,
                                   user_agent='Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/api/void/**', proxy)
        dev = 'runlk'
        await pg.request.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': dev, 'tut': True}), headers={'content-type': 'application/json'})
        await pg.request.post(API + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
        await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','%s');localStorage.setItem('void-ctrl-seen','1');" % dev)
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=%d' % T, wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!__dbg.walkTo"): break
            except Exception: pass
            await asyncio.sleep(.25)
        print('renderer', await pg.evaluate("(()=>{const g=document.createElement('canvas').getContext('webgl');const e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"))
        await asyncio.sleep(8); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
        await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(3)
        print('overlay', await pg.evaluate("(()=>{const e=document.elementFromPoint(innerWidth/2,innerHeight/2);const h=document.getElementById('heroPick');return {hero:!!h.dataset.on, top:e&&(e.id||e.className||e.tagName)}})()"))
        await pg.screenshot(path=os.path.join(OUT, 'run_lock_start.png'))
        for _ in range(30):   # the walk opens with a dialog: tap through it first
            top = await pg.evaluate("(()=>{const e=document.elementFromPoint(innerWidth/2,innerHeight/2);return e&&(e.closest('#vn,#voidVn,#missionCard,#ctrlCard')||{}).id||''})()")
            if not top: break
            await pg.touchscreen.tap(640, 400); await asyncio.sleep(.8)
        await asyncio.sleep(1)
        cdp = await ctx.new_cdp_session(pg)
        pad = await pg.evaluate("(()=>{const r=document.getElementById('walkPad').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        async def push(sec=1.2):
            cx, cy = pad
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': cx, 'y': cy, 'id': 1}]})
            for i in range(1, 6):
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': cx, 'y': cy - 14 * i, 'id': 1}]})
            p0 = await pg.evaluate("[__dbg.walk().x, __dbg.walk().z]"); await asyncio.sleep(sec)
            p1 = await pg.evaluate("[__dbg.walk().x, __dbg.walk().z]")
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            await asyncio.sleep(.4)
            return round(((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2) ** .5 / sec, 2)
        aria = "document.getElementById('walkRun').getAttribute('aria-pressed')"
        run = await pg.evaluate("(()=>{const r=document.getElementById('walkRun').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
        res = {}
        res['offEdge'] = await push()
        await pg.touchscreen.tap(*run); await asyncio.sleep(.3); res['ariaAfterTap'] = await pg.evaluate(aria)
        res['onEdge'] = await push()
        await pg.evaluate("document.getElementById('walkPad').hidden=true"); await asyncio.sleep(.2)
        await pg.evaluate("document.getElementById('walkPad').hidden=false"); await asyncio.sleep(.2)
        res['ariaAfterHideShow'] = await pg.evaluate(aria)
        res['onAfterHideShow'] = await push()
        await pg.touchscreen.tap(*run); await asyncio.sleep(.3); res['ariaAfterTap2'] = await pg.evaluate(aria)
        res['offAgain'] = await push()
        await pg.touchscreen.tap(*run); await asyncio.sleep(.3)
        await pg.evaluate("__dbg.stopWalk ? __dbg.stopWalk() : null"); await asyncio.sleep(.5)
        res['ariaAfterStop'] = await pg.evaluate(aria)
        await pg.screenshot(path=os.path.join(OUT, 'run_lock.png'))
        res['errors'] = errs[:3]
        print(json.dumps(res, ensure_ascii=False))
        ok = (res['offEdge'] < 7 and res['onEdge'] > 9 and res['onAfterHideShow'] > 9 and res['offAgain'] < 7
              and res['ariaAfterTap'] == 'true' and res['ariaAfterHideShow'] == 'true' and res['ariaAfterTap2'] == 'false' and not errs)
        print('PASS' if ok else 'FAIL')
        await br.close()
asyncio.run(main())
