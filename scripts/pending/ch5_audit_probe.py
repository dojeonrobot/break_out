# 섬 길 감사 준비: 메시 이름 목록, 걷기 격자 구조, IB 구조를 찍는다. 정적 서버 포트는 인자(기본 8197).
import asyncio, sys, json
from playwright.async_api import async_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '8197'
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
REN = """() => { const g = document.createElement('canvas').getContext('webgl'); if(!g) return 'no-webgl'; const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'no-ext'; }"""
JS = """() => { const b = __dbg, names = {};
  b.islRoot.traverse(o=>{ if(!o.isMesh && !o.isInstancedMesh) return; const k = o.name || '(이름 없음)'; names[k] = (names[k] || 0) + 1; });
  const g = b.walkGrid(); const gk = {}; for(const k in g){ const v = g[k]; gk[k] = v && v.length != null ? (v.constructor.name + ':' + v.length) : (typeof v === 'function' ? 'fn' : v); }
  const ib = b.IB.filter(x=> x).slice(0, 4).map(x=>{ const o = {}; for(const k in x){ const v = x[k]; o[k] = (typeof v === 'object' && v) ? (v.isObject3D ? 'Object3D' : Object.keys(v).slice(0, 6)) : v; } return o; });
  return {names, grid:gk, ib, nIB:b.IB.length, spurs:(b.islRoot.userData.spurs || []).length, dbg:Object.keys(b)}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        pg = await br.new_page(viewport={'width': 1300, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island&nobatch=1', wait_until='domcontentloaded', timeout=120000)
        print('renderer:', await pg.evaluate(REN))
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await asyncio.sleep(3)
        r = await pg.evaluate(JS)
        print(json.dumps(r, ensure_ascii=False)); print('errs', errs[:3])
        await br.close()
asyncio.run(main())
