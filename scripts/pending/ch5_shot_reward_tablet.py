# 2026-11-25 (사용자: 미션 클리어 카드의 좌표가 상자 왼쪽으로 치우침): 좌표를 주는 미션 완료 카드를 태블릿 가로·세로로 찍고 좌표 줄 위치를 잰다.
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_reward_tablet.py <그림 폴더> [미션 id=q2]
import asyncio, sys, os, json, pathlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); Q = sys.argv[2] if len(sys.argv) > 2 else 'q2'
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HOOK = 'const _pwP = new THREE.Vector3()'
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
MEAS = r"""(()=>{ const R = e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  const z = document.querySelector('#qReward .z'), c = z && z.querySelector('code'), s = z && z.querySelector('span'); return z ? {z:R(z), code:R(c), span:R(s), disp:getComputedStyle(z).display, ji:getComputedStyle(z).justifyItems} : null; })()"""
async def main():
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src
    src = src.replace(HOOK, "window.__rew = (id)=> showReward(QUESTS.find(q=> q.id === id)); " + HOOK, 1)
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
                    if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__rew"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7); await pg.evaluate("(()=>{ const t = document.getElementById('teamPick'); if(t) delete t.dataset.on; })()")
            await pg.evaluate(f"__rew('{Q}')"); await asyncio.sleep(2.5)
            print(name, json.dumps(await pg.evaluate(MEAS)), errs[:1])
            await pg.screenshot(path=os.path.join(OUT, f'rew_{name}.png'))
            await ctx.close()
        await br.close()
asyncio.run(main())
