# 2026-11-25 (노션 scan break 8번: 보이드 좀만 더 위로): 보이드 대사 초상화가 대사 창에 얼마나 가리는지 태블릿 가로·세로로 잰다. TAG=before|after
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_vn_tablet.py <그림 폴더>
import asyncio, sys, os, json, pathlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HOOK = 'const _pwP = new THREE.Vector3()'
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
MEAS = r"""(()=>{ const R = s=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return r.width ? [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] : null; };
  return {img:R('#vnImg'), box:R('#vn .box'), prev:R('#vnPrev'), next:R('#vnNext')}; })()"""
async def main():
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src
    src = src.replace(HOOK, "window.__say = (l)=> say(l); " + HOOK, 1)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        for name, vp in [('land', (1280, 690)), ('port', (800, 1180))]:
            ctx = await br.new_context(viewport={'width': vp[0], 'height': vp[1]}, has_touch=True, is_mobile=True, user_agent=UA)
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
            await pg.route('**/api/void/**', lambda rt: rt.abort())
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-team','3');")
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=3&world=island', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__say"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7); await pg.evaluate("(()=>{ const t = document.getElementById('teamPick'); if(t) delete t.dataset.on; })()")
            await pg.evaluate("__say([{who:'보이드',text:'루나는 값이 이상한 자리마다 이 아이에게 먼저 물어봤어.'},{who:'보이드',text:'아이가 고개를 끄덕이면 그 값을 믿고 적었지.'}])")
            await asyncio.sleep(2.5); await pg.evaluate("__dbg.quest().next && __dbg.quest().next()"); await asyncio.sleep(3)
            print(name, json.dumps(await pg.evaluate(MEAS)), errs[:1])
            await pg.screenshot(path=os.path.join(OUT, f'vnvoid_{name}_' + os.environ.get('TAG','a') + '.png'))
            # notion 9: board at 100%, closed (펼치기) — title and button should stay on one line
            await pg.evaluate("document.getElementById('voidVn')?.removeAttribute('data-on'); document.getElementById('vn').style.display='none'")
            await pg.evaluate("(()=>{ const b = document.getElementById('board'); b.hidden = false; b.classList.add('solo','closed'); document.getElementById('bN').textContent = '100%'; document.getElementById('bMin').textContent = '펼치기'; })()")
            await asyncio.sleep(.5)
            print(name, 'board', json.dumps(await pg.evaluate("(()=>{ const h = document.querySelector('#board .bh h2'), x = document.getElementById('bMin'), n = document.getElementById('bN'), b = document.getElementById('board'); const lh = e=> Math.round(e.getBoundingClientRect().height); return {board: Math.round(b.getBoundingClientRect().width), h2H: lh(h), h2Line: parseFloat(getComputedStyle(h).lineHeight) || null, h2Over: h.scrollWidth > h.clientWidth + 1, btnH: lh(x), num: Math.round(n.getBoundingClientRect().width), numFont: getComputedStyle(n).fontSize}; })()")))
            await pg.screenshot(path=os.path.join(OUT, f'board_{name}_' + os.environ.get('TAG','a') + '.png'))
            await ctx.close()
        await br.close()
asyncio.run(main())
