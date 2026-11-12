# 바이킹 공사장 화면 찍기(정적 서버 8097만 있으면 됨, 서버 없는 모드). python scripts/pending/ch5_shot_viking_site.py <그림 폴더> [접두어]
# 가까이(앞·옆·뒤), 걷는 눈높이, 섬 기본 시점까지 찍는다. 굳은 조각 검사와 오류도 찍는다.
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else 'site'
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1180, 'height': 820}); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400]))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && typeof window.__vikQ==='function' && typeof window.__islandCam==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        print('GL', await pg.evaluate("(()=>{const g=__dbg.renderer.getContext(),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"))
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }")
        await asyncio.sleep(3); await pg.screenshot(path=os.path.join(OUT, PRE + '_0_home.png'), timeout=60000)
        b = await pg.evaluate("__vikQ().spot")
        cx, cz = 70*1, 167*1
        c = await pg.evaluate("(()=>{ const v = new __dbg.THREE.Vector3(); let o = null; __dbg.THREE && 0; return null; })()")
        views = {'1_front': "__islandCam(CX, CZ, 95)", '2_close': "__islandCam(CX, CZ, 52)", '3_far': "__islandCam(CX, CZ, 230)"}
        ctr = await pg.evaluate("(()=>{ const s = __vikQ().spot; return [s[0], s[1]]; })()")
        # the lot centre in world units: ask the page (the pickable box)
        box = await pg.evaluate("window.__vikCentre ? __vikCentre() : null")
        CX, CZ = (box or ctr)
        for k, js in views.items():
            await pg.evaluate(js.replace('CX', str(CX)).replace('CZ', str(CZ))); await asyncio.sleep(2.5)
            await pg.screenshot(path=os.path.join(OUT, f'{PRE}_{k}.png'), timeout=60000)
        # eye level from the path, and from the other three sides
        for k, (dx, dz) in {'4_eye_path': (ctr[0] - CX, ctr[1] - CZ), '5_eye_back': (CX - ctr[0], CZ - ctr[1]), '6_eye_side': (-(ctr[1] - CZ), ctr[0] - CX)}.items():
            L = (dx*dx + dz*dz)**.5 or 1; ex, ez = CX + dx/L*(L + 22), CZ + dz/L*(L + 22)
            await pg.evaluate(f"__vikEye({ex}, {ez}, {CX}, {CZ})"); await asyncio.sleep(2.5)
            await pg.screenshot(path=os.path.join(OUT, f'{PRE}_{k}.png'), timeout=60000)
        print('baked', await pg.evaluate('__dbg.bakedAudit()')); print('errors:', errs)
        await br.close()
asyncio.run(main())
