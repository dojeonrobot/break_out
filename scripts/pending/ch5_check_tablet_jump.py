# 2026-11-25 (사용자: 태블릿에 점프 기능이 없음): 태블릿(터치) 걷기 화면에 「점프」 버튼이 보이고, 누르면 실제로 뛰는지 본다.
# 걷기를 막 시작하고 3초쯤 된 첫 탭은 뛰지 않았다(원인 미확인, 그때 Space도 같은지 미확인). 판정은 그 뒤의 탭(tap2Peak).
# 노트북(마우스)에서는 버튼이 안 보여야 한다(Space로 뜀).
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_check_tablet_jump.py <그림 폴더>
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
async def run(pw, label, touch, results):
    br = await pw.chromium.launch(args=GPU)
    kw = dict(viewport={'width': 1280, 'height': 800})
    if touch: kw.update(has_touch=True, is_mobile=True, user_agent='Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36')
    ctx = await br.new_context(**kw); pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/api/void/**', proxy)
    dev = 'jmp' + ('t' if touch else 'l')
    await pg.request.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': dev, 'tut': True}), headers={'content-type': 'application/json'})
    await pg.request.post(API + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
    await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','%s');localStorage.setItem('void-ctrl-seen','1');" % dev)
    await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=%d' % T, wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!__dbg.walkTo"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await asyncio.sleep(8); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
    await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(3)
    st = await pg.evaluate("(()=>{ const b = document.getElementById('walkJump'), r = b.getBoundingClientRect(), run = document.getElementById('walkRun').getBoundingClientRect(); return {walk: !!__dbg.walk(), shown: r.width > 0 && getComputedStyle(b).display !== 'none', rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], run: [Math.round(run.left), Math.round(run.top), Math.round(run.width)]}; })()")
    jumped = None
    if st['shown']:
        y0 = await pg.evaluate("__dbg.walk().jy ?? 0")
        x, y = st['rect'][0] + st['rect'][2] / 2, st['rect'][1] + st['rect'][3] / 2
        await pg.touchscreen.tap(x, y)
        peak = 0
        for _ in range(12):
            await asyncio.sleep(.05); peak = max(peak, await pg.evaluate("__dbg.walk().jy ?? 0"))
        jumped = round(peak - y0, 2)
        await asyncio.sleep(1.5); await pg.keyboard.press('Space'); sp = 0
        for _ in range(12):
            await asyncio.sleep(.05); sp = max(sp, await pg.evaluate("__dbg.walk().jy ?? 0"))
        st['spacePeak'] = round(sp, 2)
        await asyncio.sleep(1.5); await pg.evaluate("window.__ev=[]; ['pointerdown','touchstart','click'].forEach(t=>document.getElementById('walkJump').addEventListener(t, e=>__ev.push(t+(e.defaultPrevented?'!':'')), true)); ['pointerdown','touchstart','click'].forEach(t=>window.addEventListener(t, e=>__ev.push('win:'+t+':'+(e.target.id||e.target.tagName)), true))")
        await pg.touchscreen.tap(x, y); tp = 0
        for _ in range(12):
            await asyncio.sleep(.05); tp = max(tp, await pg.evaluate("__dbg.walk().jy ?? 0"))
        st['tap2Peak'] = round(tp, 2); st['events'] = await pg.evaluate("__ev.join(' ')")
        st['state'] = await pg.evaluate("(()=>{ const w = __dbg.walk(); return {jv: w.jv, ride: !!w.ride, fly: !!w.fly}; })()")
        await asyncio.sleep(1.5); await pg.evaluate("document.getElementById('walkJump').click()"); ck = 0
        for _ in range(12):
            await asyncio.sleep(.05); ck = max(ck, await pg.evaluate("__dbg.walk().jy ?? 0"))
        st['elClickPeak'] = round(ck, 2); st['keys'] = await pg.evaluate("Object.keys(__dbg.walk()).filter(k=>/^j/.test(k)).join(',')")
        await pg.screenshot(path=os.path.join(OUT, f'jump_{label}.png'))
    else:
        await pg.screenshot(path=os.path.join(OUT, f'jump_{label}.png'))
    results.append({'device': label, **st, 'jumpPeak': jumped, 'errors': errs[:2]})
    await br.close()
async def main():
    res = []
    async with async_playwright() as pw:
        await run(pw, 'tablet', True, res)
        await run(pw, 'laptop', False, res)
    for r in res: print(json.dumps(r, ensure_ascii=False))
    ok = res[0]['shown'] and (res[0].get('tap2Peak') or 0) > 0.5 and not res[1]['shown'] and not res[0]['errors'] and not res[1]['errors']
    print('PASS' if ok else 'FAIL')
asyncio.run(main())
