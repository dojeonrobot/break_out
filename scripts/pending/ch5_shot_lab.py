# 2026-11-18: 연구실 입구(섬 바깥의 지하 출입구 덮개, 관람차 아래 기계실 장면 닫힘·열림·들어가는 시점)와 연구실 화면(평소·불안정·관람차 반응, 태블릿·폰 크기)을 찍는다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_shot_lab.py <그림 폴더>
import asyncio, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1366, 'height': 768}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src; src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});"); LIT = "const lit = id=>{"; assert LIT in src; src = src.replace(LIT, LIT + " if(window.__litAll) return true;")   # 찍을 때만: 기록이 다 들어온 상태(window.__litAll)로 볼 수 있게
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); ev = pg.evaluate; await pg.add_style_tag(content='#teamPick{display:none!important}')
        try: await ev("__dbg.setDemo(['dl-harmonia','dl-carousel','dl-coaster'], true)")
        except Exception as e: print('setDemo', str(e)[:100])
        shot = lambda n: pg.screenshot(path=f'{OUT}/{n}.jpg', type='jpeg', quality=86)
        o = await ev("(()=>{ const o = __t.labGateBuild(); return {x:o.g.position.x, z:o.g.position.z, ux:o.face[0], uz:o.face[1], G:__t.G}; })()"); x, z, ux, uz, G = o['x'], o['z'], o['ux'], o['uz'], o['G']
        CAM = "([x,y,z,tx,ty,tz])=>{ const c = __t; c.controls.minDistance = 1; c.camera.position.set(x, y, z); c.controls.target.set(tx, ty, tz); c.controls.update(); c.camera.lookAt(tx, ty, tz); }"
        await ev(CAM, [x + ux*24 - uz*10, G + 7, z + uz*24 + ux*10, x, G + 2, z]); await asyncio.sleep(1.5); await shot('out_hatch')
        await ev(CAM, [x + ux*75, G + 36, z + uz*75, x - ux*40, G + 20, z - uz*40]); await asyncio.sleep(1.2); await shot('out_far')
        await ev("(()=>{ __t.labSetEnter(); })()"); await asyncio.sleep(1.2); await shot('set_closed'); print('set', await ev("__labSet()"))
        await ev("(()=>{ const r = __t.labSet(); r.view('near', 900); r.want = 1; })()"); await asyncio.sleep(1.2); await shot('set_opening'); await asyncio.sleep(1.6); await shot('set_open_near')
        await ev("(()=>{ __t.labSet().view('wide', 0); })()"); await asyncio.sleep(.5); await shot('set_open'); await ev("(()=>{ __t.labSet().view('in', 700); })()"); await asyncio.sleep(1.1); await shot('set_in')
        await ev("(()=>{ __t.labSetLeave(); })()"); await asyncio.sleep(.6); print('left', await ev("__labSet()"))
        await ev("__t.labRoomOpen(false)"); await asyncio.sleep(.9); await shot('room_empty'); await ev("(()=>{ window.__litAll = true; __t.labRoomOpen(false); })()"); await asyncio.sleep(.9); await shot('room_calm'); await ev("__t.labRoomNoise(true)"); await asyncio.sleep(.6)
        await ev("(()=>{ __t.say(__t.STORY.midB.slice(1, 2)); })()"); await asyncio.sleep(1.8); await shot('room_noise')
        await ev("(()=>{ const v = document.getElementById('vn'); for(let k = 0; k < 6 && v.dataset.on; k++) __dbg.quest().next(); __t.labRoomNoise(false); __t.labRoomPing(); })()"); await asyncio.sleep(.8); await shot('room_ping'); print('room', await ev("__labRoom()"))
        for vp in ((1280, 800), (1024, 600), (780, 360), (390, 800)):
            await pg.set_viewport_size({'width': vp[0], 'height': vp[1]}); await asyncio.sleep(.5); await ev("__t.labRoomNoise(true)"); await asyncio.sleep(.3); await shot(f'room_{vp[0]}')
            print(vp, await ev("(()=>{ const m = document.querySelector('#labRoom .col.c .mon').getBoundingClientRect(), w = document.querySelector('#labRoom .wall').getBoundingClientRect(); return {map:[Math.round(m.width), Math.round(m.height)], wall:[Math.round(w.width), Math.round(w.height)], overflow:document.documentElement.scrollWidth > innerWidth}; })()"))
        print('errs', errs[:4]); await br.close()
asyncio.run(main())
