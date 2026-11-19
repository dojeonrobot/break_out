# 아일랜드 익스프레스 열차를 가까이에서 찍는다(옆·앞쪽 비스듬히·역에 선 모습).  정적 서버 8097.  python ch5_shot_train.py <결과 폴더> [이름 앞머리]
import asyncio, sys, pathlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else 'train'; os.makedirs(OUT, exist_ok=True)
HOOK = r"""
;window.__tr = (side, dist, up, back)=>{ PARK_HOLD = false; TRAIN.lit = true; const c = TRAIN.cars, a = c[0].position, b = c[2].position, e = c[c.length - 1].position, mid = new THREE.Vector3().addVectors(a, e).multiplyScalar(.5);
  const dir = new THREE.Vector3().subVectors(a, e).normalize(), out = new THREE.Vector3(mid.x, 0, mid.z).normalize().multiplyScalar(side);
  controls.minDistance = 3; controls.enabled = false; camera.position.set(b.x + out.x*dist + dir.x*back, b.y + up, b.z + out.z*dist + dir.z*back); controls.target.set(b.x + dir.x*back*0.2, b.y + 2.5, b.z + dir.z*back*0.2); camera.lookAt(controls.target); return [a.x, a.y, a.z].map(v=> Math.round(v)); };
window.__lo = (dist, up, fwd)=>{ const c = TRAIN.cars, a = c[0].position, e = c[1].position, dir = new THREE.Vector3().subVectors(a, e).normalize(), out = new THREE.Vector3(a.x, 0, a.z).normalize();
  camera.position.set(a.x + out.x*dist + dir.x*fwd, a.y + up, a.z + out.z*dist + dir.z*fwd); controls.target.set(a.x, a.y + 3, a.z); camera.lookAt(controls.target); return 1; };
window.__freeze =()=>{ TRAIN.mode = 'stop'; };
"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&hour=12&admin=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__tr === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9)
        await pg.evaluate("""()=>{ const cv = document.querySelector('canvas'); const keep = new Set(); for(let p = cv; p; p = p.parentElement) keep.add(p); document.querySelectorAll('body *').forEach(e=>{ if(!keep.has(e) && !cv.contains(e)) e.style.setProperty('visibility', 'hidden', 'important'); }); }""")
        await pg.evaluate("__freeze()"); await asyncio.sleep(1.5)
        for name, args in (('side', '1, 30, 6, 0'), ('front', '1, 16, 5, 22'), ('rear', '1, 14, 4, -16')):
            print(name, await pg.evaluate(f"__tr({args})")); await asyncio.sleep(1.2); await pg.evaluate(f"__tr({args})"); await asyncio.sleep(.6)
            await pg.screenshot(path=f'{OUT}/{PRE}_{name}.png')
        for name, args in (('loco', '24, 6, 12'), ('loco_side', '26, 4, -2')):
            await pg.evaluate(f"__lo({args})"); await asyncio.sleep(1.2); await pg.evaluate(f"__lo({args})"); await asyncio.sleep(.6); await pg.screenshot(path=f'{OUT}/{PRE}_{name}.png')
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
