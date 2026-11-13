# 걷기 막힘 감사 확인용 그림. ① 지점별로 막힘 지도 조각(왼쪽)과 위에서 본 화면(오른쪽)을 나란히 ② 걷는 시점(1인칭)으로 그 자리에 서서 본 화면.
# python scripts/pending/ch5_audit_block_shots.py <포트> <block 폴더(block_map.png)> <지점 json: {"top":[[이름,x,z,폭]], "walk":[[이름,x,z,바라볼 x,바라볼 z]]}>
import asyncio, sys, json, os, math
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
PORT, DIR, SP = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8')); X0, Z0 = -558, -626
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
HIDE = "()=>{ const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }"
async def main():
    mp = Image.open(os.path.join(DIR, 'block_map.png')).convert('RGB')
    try: ft = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 20)
    except Exception: ft = ImageFont.load_default()
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU); pg = await br.new_page(viewport={'width': 800, 'height': 800}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); }"); await pg.evaluate(HIDE); await asyncio.sleep(4)
        rows = []
        for k, (name, x, z, span) in enumerate(SP.get('top', [])):
            await pg.evaluate("([cx, cz, h])=>{ const T = __dbg.THREE; __dbg.controls.minDistance = 3; __dbg.flyTo(new T.Vector3(cx, __dbg.G + h, cz + 1), new T.Vector3(cx, __dbg.G, cz), 10); }", [x, z, span*1.21]); await asyncio.sleep(2.0)
            f = os.path.join(DIR, f'top_{k:02d}.png'); await pg.screenshot(path=f, timeout=60000)
            h = span/2; crop = mp.crop((int((x - h - X0)*2), int((z - h - Z0)*2), int((x + h - X0)*2), int((z + h - Z0)*2))).resize((800, 800), Image.NEAREST)
            row = Image.new('RGB', (1600, 800)); row.paste(crop, (0, 0)); row.paste(Image.open(f).convert('RGB'), (800, 0)); d = ImageDraw.Draw(row); d.rectangle([0, 0, 1600, 30], fill=(0, 0, 0)); d.text((8, 3), f'{name} ({x},{z}) 폭 {span} · 회색=막힘 진회색=물체+막힘 빨강=물체인데 통과 파랑=빈 곳인데 막힘', fill=(255, 255, 0), font=ft); rows.append(row)
        for s in range(0, len(rows), 2):
            sh = Image.new('RGB', (1600, 800*len(rows[s:s+2]))); [sh.paste(r, (0, 800*j)) for j, r in enumerate(rows[s:s+2])]; p = os.path.join(DIR, f'topsheet_{s//2:02d}.png'); sh.save(p); print(p)
        wk = SP.get('walk', [])
        if wk:
            await asyncio.sleep(0.5)
            await pg.evaluate("()=>{ document.querySelectorAll('#heroPick').forEach(e=>{ delete e.dataset.on; }); }"); await pg.evaluate(HIDE); tiles = []
            for k, (name, x, z, tx, tz) in enumerate(wk):
                st = await pg.evaluate("([x, z, tx, tz])=>{ const T = __dbg.THREE, y = __dbg.groundY(x, z), d = Math.hypot(tx - x, tz - z) || 1, ux = (tx - x)/d, uz = (tz - z)/d; __dbg.controls.minDistance = 0.5; __dbg.camera.near = 0.3; __dbg.camera.updateProjectionMatrix(); __dbg.flyTo(new T.Vector3(x, y + 1.5, z), new T.Vector3(x + ux*6, y + 1.1, z + uz*6), 10); return {blocked:__dbg.walkBlocked(x, z), gy:y - __dbg.G}; }", [x, z, tx, tz]); await asyncio.sleep(1.6)   # 걷기 모드는 진행 상태가 있어야 열리므로, 걷는 사람의 눈 자리(땅 + 1.5)에 카메라를 직접 놓는다
                cam = await pg.evaluate("()=> [__dbg.camera.position.x, __dbg.camera.position.y - __dbg.G, __dbg.camera.position.z].map(v=> Math.round(v*10)/10)")
                f = os.path.join(DIR, f'walk_{k:02d}.png'); await pg.screenshot(path=f, timeout=60000); im = Image.open(f).convert('RGB'); d = ImageDraw.Draw(im); d.rectangle([0, 0, 800, 30], fill=(0, 0, 0)); d.text((8, 3), f'{k}. {name} 막힘={st["blocked"]} 눈 {cam[1]}', fill=(255, 255, 0), font=ft); tiles.append(im); print(k, name, st, cam)
            for s in range(0, len(tiles), 4):
                sh = Image.new('RGB', (1600, 1600), (255, 255, 255)); [sh.paste(t, ((j % 2)*800, (j//2)*800)) for j, t in enumerate(tiles[s:s+4])]; p = os.path.join(DIR, f'walksheet_{s//4:02d}.png'); sh.save(p); print(p)
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
