# 2026-11-25 (사용자: 태블릿에서 자일로가 대사 밑에 숨음, 이전 버튼이 다음보다 위아래로 큼): 인물 대사·보이드 대사를 태블릿 가로·세로로 찍고 초상화·버튼 크기를 잰다.
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
        for name, vp in [('land', (1280, 800)), ('port', (800, 1280))]:
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
            await pg.evaluate("__say([{who:'자일로',text:'제로, 리코! 와 줬군요.'},{who:'자일로',text:'바이킹이 무너지면서 섬 전체에 전기가 끊겼어요. 예비 배전선을 찾아 전기를 복구해 주세요.'}])")
            await asyncio.sleep(2.5); await pg.evaluate("__dbg.quest().next && __dbg.quest().next()"); await asyncio.sleep(3)
            print(name, json.dumps(await pg.evaluate(MEAS)), errs[:1])
            await pg.screenshot(path=os.path.join(OUT, f'vn_{name}.png'))
            await ctx.close()
        await br.close()
asyncio.run(main())
