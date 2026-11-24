# 2026-11-24: 덤불은 걸어서는 못 지나가고 점프하면 지나간다 / 걷는 화면 오른쪽 위 패널과 소리·관리자 버튼이 겹치지 않는다 / 미로에서 natyWob 소리가 안 난다.
#  python -X utf8 ch5_check_hop_bush.py <그림 폴더>   (정적 서버 8097 또는 시험 서버 8096에서 페이지를 연다)
import asyncio, sys, os, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
fails = []
def ok(c, m):
    print(('OK   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, vp, touch in [('laptop', (1280, 800), False), ('tablet', (1280, 800), True)]:
            ctx = await br.new_context(viewport={'width': vp[0], 'height': vp[1]}, has_touch=touch, is_mobile=touch)
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
            src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8').replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&admin=0', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await ev("typeof window.__dbg!=='undefined' && !!window.__t"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(8)
            await ev("(()=>{ for(const id of ['teamPick','intro']){ const e = document.getElementById(id); if(e){ e.style.display='none'; delete e.dataset.on; } } })()")
            await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2)
            await ev("__t['(walkerOpen = ()=> true, 1)']"); await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5); print(name, 'walk', await ev("!!__t['walk']"))
            # a bush cell (2) with walkable ground (0) right beside it, away from paths
            spot = await ev("""(()=>{ const t = __t; t['WGRID'] || t['buildWalkGrid']; let G = t['WGRID']; if(!G || !G.W){ G = t['buildWalkGrid'](); } const a = G.a, W = G.W;
              let n2 = 0; for(let i = 0; i < a.length; i++) if(a[i] === 2) n2++;
              for(let z = 2; z < G.H - 8; z++) for(let x = 8; x < W - 8; x++){ const i = z*W + x; if(a[i] !== 2) continue;
                // a run west→east: 6 free cells, then bush cells, then free again within 8
                let ok = true; for(let d = 1; d <= 6; d++) if(a[i - d] !== 0 || G.path[i - d]) ok = false; if(!ok) continue;
                let e = 0; while(e < 8 && a[i + e] === 2) e++; if(e < 1 || e > 5 || a[i + e] !== 0) continue;
                return {n2, x:G.X0 + x - 5 + 0.5, z:G.Z0 + z + 0.5, bush:G.X0 + x + 0.5, after:G.X0 + x + e + 1.5}; }
              return {n2}; })()""")
            print(name, 'bush cells', spot.get('n2'))
            ok(spot.get('n2', 0) > 0, f'{name}: bushes are marked as jumpable cells')
            if 'x' in spot:
                JS = """(async()=>{ const w = __t['walk']; w.x = SX; w.z = SZ; w.yaw = Math.PI/2; w.snap = true; w.jv = null; w.jy = 0; await new Promise(r=> setTimeout(r, 300));
                  __t['WALK_KEYS'].KeyW = true; const t0 = performance.now(); let maxX = w.x;
                  while(performance.now() - t0 < 3200){ await new Promise(r=> requestAnimationFrame(r)); maxX = Math.max(maxX, w.x); if(JUMP && w.jv == null && w.x < BX && w.x > BX - 3.5){ w.jv = 7.6; w.jy = 0.01; } }
                  delete __t['WALK_KEYS'].KeyW; return {x:w.x, maxX}; })()"""
                walk = lambda jump: ev(JS.replace('SX', str(spot['x'])).replace('SZ', str(spot['z'])).replace('BX', str(spot['bush'])).replace('JUMP', 'true' if jump else 'false'))
                r0 = await walk(False); r1 = await walk(True)
                print(name, 'no jump', r0, 'jump', r1, 'bush at', spot['bush'], 'after', spot['after']); print('row', await ev("(()=>{ const G = __t['WGRID'], x0 = Math.floor(" + str(spot['x']) + " - G.X0), z = Math.floor(" + str(spot['z']) + " - G.Z0); return Array.from({length:14}, (_, d)=> G.a[z*G.W + x0 + d]).join(''); })()"), 'walkBlocked at stop', await ev("__dbg.walkBlocked(" + str(r1['x'] + 0.4) + ',' + str(spot['z']) + ')'))
                ok(r0['maxX'] < spot['bush'], f'{name}: walking stops at the bush')
                ok(r1['maxX'] > spot['after'], f'{name}: a jump goes over the bush to the far side')
            # top-right: walk panel vs sound/admin buttons
            await ev("(()=>{ const w = __t['walk']; w.x = 0; w.z = 470; w.snap = true; })()"); await asyncio.sleep(.8)
            rects = await ev("""(()=>{ const r = id=>{ const e = document.getElementById(id); if(!e) return null; const b = e.getBoundingClientRect(); return getComputedStyle(e).display === 'none' || !b.width ? null : [b.left, b.top, b.right, b.bottom]; }; return {hud:r('walkHud'), snd:r('sndBtn'), adm:r('adminBtn')}; })()""")
            print(name, rects)
            hud = rects['hud']
            for k in ('snd', 'adm'):
                b = rects[k]
                if hud and b: ok(not (b[0] < hud[2] and b[2] > hud[0] and b[1] < hud[3] and b[3] > hud[1]), f'{name}: {k} button clear of the walk panel (gap {round(b[1] - hud[3], 1)})')
            await pg.screenshot(path=os.path.join(OUT, f'top_{name}.png'), clip={'x': vp[0] - 360, 'y': 0, 'width': 360, 'height': 160})
            ok(not errs, f'{name}: no page errors {errs[:2]}')
            await ctx.close()
        await br.close()
    print('FAILS', fails)
asyncio.run(main())
