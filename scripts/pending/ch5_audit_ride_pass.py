# 2026-11-18 (사용자: 관람차가 뚫린다, 이런 건 다 확인할 것): 모든 놀이기구·명소에 대해, 그 자리 안쪽(반지름의 0.75)에서 걸어 들어갈 수 있는 칸을 센다.
# 기구마다 한 줄: 안쪽 칸 수, 걸을 수 있는 칸 수, 그중 길로 뚫린 칸 수, 중심이 막혔는지. 그림 폴더를 주면 기구별 작은 지도(빨강=막힘, 흰색=통과, 노랑=길)를 남긴다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_audit_ride_pass.py [그림 폴더]
import asyncio, sys, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
from PIL import Image
OUT = sys.argv[1] if len(sys.argv) > 1 else None
JS = r"""()=>{ const b = __dbg, g = b.walkGrid(), out = [];
  b.IB.forEach(e=>{ if(!(e.c === 'ride' || e.mission) || !e.mesh) return; const R = Math.max(6, (e.r || 20)*0.75), n = Math.ceil(R), rows = []; let all = 0, free = 0, path = 0;
    for(let dz = -n; dz <= n; dz++){ let row = ''; for(let dx = -n; dx <= n; dx++){ if(dx*dx + dz*dz > R*R){ row += ' '; continue; } const x = e.cx + dx, z = e.cz + dz, ix = Math.floor(x) - g.X0, iz = Math.floor(z) - g.Z0, i = iz*g.W + ix; all++;
        const bl = b.walkBlocked(x, z), p = ix >= 0 && iz >= 0 && ix < g.W && iz < g.H && g.path[i]; if(!bl){ free++; if(p) path++; } row += bl ? '#' : p ? 'p' : '.'; } rows.push(row); }
    out.push({label:e.label, c:e.c, r:Math.round(e.r || 0), all, free, path, centre:b.walkBlocked(e.cx, e.cz), rows}); });
  return out; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); res = await pg.evaluate(JS); await br.close()
    bad = 0
    for r in sorted(res, key=lambda r: -r['free']/max(1, r['all'])):
        share = r['free']/max(1, r['all']); flag = 'FAIL' if (share > 0.12 or not r['centre']) else 'OK  '; bad += flag == 'FAIL'
        print(f"{flag} {r['label']:<14} 반지름 {r['r']:>3}  안쪽 {r['all']:>5}칸  통과 {r['free']:>5}칸({share:.0%})  그중 길 {r['path']:>4}  중심 {'막힘' if r['centre'] else '뚫림'}")
        if OUT:
            os.makedirs(OUT, exist_ok=True); rows = r['rows']; im = Image.new('RGB', (len(rows[0]), len(rows)), (40, 40, 40)); px = im.load()
            for j, row in enumerate(rows):
                for i, ch in enumerate(row): px[i, j] = {'#': (200, 60, 50), '.': (255, 255, 255), 'p': (250, 210, 60), ' ': (40, 40, 40)}[ch]
            im.resize((im.width*4, im.height*4), Image.NEAREST).save(os.path.join(OUT, f"pass_{r['label']}.png"))
    print('FAIL', bad, '/', len(res), 'errs', errs[:2])
asyncio.run(main())
