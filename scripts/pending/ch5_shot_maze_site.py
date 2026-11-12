# 미로 터와 정문 동쪽 날개 벽 둘레 찍기(정적 서버 8097만 있으면 됨, 서버 없는 모드).
# python scripts/pending/ch5_shot_maze_site.py <그림 폴더> [접두어]
# 비스듬한 시점 세 장 + 걷기 차단 격자를 글자 지도로 찍는다(# 막힘, . 통과, 2칸 간격).
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else 'mazesite'
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1180, 'height': 820}); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400]))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&admin=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && typeof window.__islandCam==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        ev = pg.evaluate
        print('GL', await ev("(()=>{const g=__dbg.renderer.getContext(),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"))
        await ev("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }")
        await asyncio.sleep(3)
        nh = await ev("__dbg.quest().NATY_HIDE"); print('maze centre', nh)
        cx, cz = nh
        for k, (x, z, d) in {'1_wide': (cx - 30, cz - 20, 170), '2_mid': (cx - 15, cz - 12, 105), '3_gateside': (cx - 60, cz - 25, 120)}.items():
            await ev(f"__islandCam({x}, {z}, {d})"); await asyncio.sleep(3)
            await pg.screenshot(path=os.path.join(OUT, f'{PRE}_{k}.png'), timeout=60000)
        try:
            await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(3)
            rows = await ev("(()=>{ const out=[]; for(let z=350; z<=450; z+=2){ let r=''; for(let x=90; x<=250; x+=2) r += __dbg.walkBlocked(x, z) ? '#' : '.'; out.push(String(z).padStart(4)+' '+r); } return out; })()")
            print('     x=90 … 250 (2칸 간격)'); print('\n'.join(rows))
        except Exception as e: print('grid failed', str(e)[:300])
        print('errors:', errs)
        await br.close()
asyncio.run(main())
