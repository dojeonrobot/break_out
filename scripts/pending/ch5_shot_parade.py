# 퍼레이드를 가까이에서 찍는다(행렬 전체 옆모습, 수레 네 대 각각, 악대).  정적 서버 8097.  python ch5_shot_parade.py <결과 폴더> [이름 앞머리]
import asyncio, sys, pathlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else 'parade'; os.makedirs(OUT, exist_ok=True)
HOOK = r"""
;window.__PR = ()=> IB.find(b=> b && b.label === "도로랜드 퍼레이드").mesh;
window.__pr = (k, dist, up)=>{ PARK_HOLD = false; const a = __PR().userData.audit, o = k < 0 ? a.band[4] : a.floats[k], p = o.getWorldPosition(new THREE.Vector3()), s = Math.sign(p.x) || 1;
  controls.minDistance = 3; controls.enabled = false; camera.position.set(p.x + s*dist, p.y + up, p.z + dist*0.35); controls.target.set(p.x, p.y + 2.6, p.z); camera.lookAt(controls.target); return [Math.round(p.x), Math.round(p.z)]; };
window.__prAll = ()=>{ const a = __PR().userData.audit, p = a.floats[1].getWorldPosition(new THREE.Vector3()), s = Math.sign(p.x) || 1; camera.position.set(p.x + s*46, p.y + 12, p.z + 8); controls.target.set(p.x, p.y + 3, p.z + 8); camera.lookAt(controls.target); return 1; };
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
                if await pg.evaluate("typeof window.__pr === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9)
        await pg.evaluate("""()=>{ const cv = document.querySelector('canvas'); const keep = new Set(); for(let p = cv; p; p = p.parentElement) keep.add(p); document.querySelectorAll('body *').forEach(e=>{ if(!keep.has(e) && !cv.contains(e)) e.style.setProperty('visibility', 'hidden', 'important'); }); }""")
        for _ in range(60):   # 수레들이 곧은 구간에 있을 때까지 기다린다
            ok = await pg.evaluate("(()=>{ PARK_HOLD = false; const a = __PR().userData.audit; if(!a) return false; return a.floats.every(f=> f.position.z > a.north + 12 && f.position.z < a.south - 12) && new Set(a.floats.map(f=> Math.sign(f.position.x))).size === 1; })()")
            if ok: break
            await asyncio.sleep(1)
        async def snap(name, js):
            await pg.evaluate(js); await asyncio.sleep(.15); await pg.evaluate(js); await asyncio.sleep(.1); await pg.screenshot(path=f'{OUT}/{PRE}_{name}.png')
        await snap('all', "__prAll()")
        for k in range(4): await snap(f'f{k + 1}', f"__pr({k}, 15, 6)")
        await snap('band', "__pr(-1, 8, 3)")
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
