# 2026-11-25 (사용자: 태블릿에서 소리 버튼이 보이드 대사 위에 있어 거슬림): 보이드 대사 창이 뜬 화면을 태블릿 가로·세로로 찍고 소리 버튼과 대사 창 위치를 잰다.
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_snd_vs_void.py <그림 폴더>
import asyncio, sys, os, json, pathlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HOOK = 'const _pwP = new THREE.Vector3()'
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
MEAS = r"""(()=>{ const R = id=>{ const e = document.getElementById(id); if(!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  const box = document.querySelector('#voidVn .box'), b = box ? box.getBoundingClientRect() : null, img = document.querySelector('#voidVn img'), ir = img ? img.getBoundingClientRect() : null;
  return {snd:R('sndBtn'), admin:R('adminBtn'), worlds:R('worlds'), box: b ? [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)] : null, img: ir ? [Math.round(ir.left), Math.round(ir.top), Math.round(ir.right), Math.round(ir.bottom)] : null}; })()"""
async def main():
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src
    src = src.replace(HOOK, "window.__vs = (t)=> voidSay(t, 60000); " + HOOK, 1)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        for name, vp in [('land', (1280, 800)), ('port', (800, 1280))]:
            ctx = await br.new_context(viewport={'width': vp[0], 'height': vp[1]}, has_touch=True, is_mobile=True, user_agent=UA)
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
            await pg.route('**/api/void/**', lambda rt: rt.abort())
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-team','3');")
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=3', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__vs"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7); await pg.evaluate("(()=>{ const t = document.getElementById('teamPick'); if(t) delete t.dataset.on; })()")
            await pg.evaluate("(()=>{ __vs('여기가 지금 네가 있는 건물이야. 근처를 둘러보며 비어 있는 곳을 찾아 줘.'); })()"); await asyncio.sleep(2)
            print(name, json.dumps(await pg.evaluate(MEAS)), errs[:1])
            await pg.screenshot(path=os.path.join(OUT, f'snd_{name}.png'))
            await ctx.close()
        await br.close()
asyncio.run(main())
