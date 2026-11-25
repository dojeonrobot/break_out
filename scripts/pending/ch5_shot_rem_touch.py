# 2026-11-25 (사용자: 태블릿에서 잔재 부수기 때 어디를 눌러야 하는지 안내가 없음): 태블릿에서 잔재 게임 세 종류의 패널을 찍고, 「치기」 버튼을 누르면 실제로 판정되는지 본다.
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_rem_touch.py <그림 폴더>
import asyncio, sys, os, json, pathlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HOOK = 'const _pwP = new THREE.Vector3()'
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
async def main():
    src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src
    src = src.replace(HOOK, "window.__rg = (i, k)=>{ if(REM.game) REM.game.done = true; remBuild(); if(!mini) mini = {kind:'device', phase:'game'}; REM.models[i].kind = k; remGame(i); }; window.__rgf = ()=>{ const g = REM.game; if(g){ g.sp = 0; g.boost = 0; g.dir = 0; g.tapAt = 0; g.lock = 0; } }; window.__rgs = ()=> REM.game ? {hits:REM.game.hits, front:REM.game.front, kind:REM.game.kind} : null; " + HOOK, 1)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, has_touch=True, is_mobile=True, user_agent=UA)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-team','3');localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=3&world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__rg"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(7); await pg.evaluate("(()=>{ const t = document.getElementById('teamPick'); if(t) delete t.dataset.on; })()")
        for k in (0, 1):
            await pg.evaluate(f"__rg({k}, {k})"); await asyncio.sleep(1.2)
            hit = await pg.evaluate("(()=>{ const b = document.querySelector('#remPlay .hit'); if(!b) return null; const r = b.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; })()")
            hits = 0
            if hit:
                for _ in range(200):
                    st = await pg.evaluate('__rgs()')
                    if st and st['front']:
                        await pg.evaluate("__rgf()"); await asyncio.sleep(.3)   # freeze in the window so evaluate latency cannot miss it
                        await pg.touchscreen.tap(hit[0], hit[1]); await asyncio.sleep(1.0)
                        hits = (await pg.evaluate('__rgs()'))['hits']; break
                    await asyncio.sleep(.02)
            await pg.screenshot(path=os.path.join(OUT, f'rem_kind{k}.png'))
            print(json.dumps({'kind': k, 'hitButton': hit, 'hitsAfterTap': hits, 'tip': await pg.evaluate("document.getElementById('remTip')?.textContent")}, ensure_ascii=False))
            await pg.evaluate("document.getElementById('remPlay').hidden = true")
        print('errs', errs[:2]); await br.close()
asyncio.run(main())
