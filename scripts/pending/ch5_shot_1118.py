# 2026-11-18: 새로 만든 것들을 장면별로 찍는다(연구실 옹벽 닫힘·열림, 연구실 모니터 화면, 잔재 셋과 부수기 화면, 동굴 선택지, 3막 장면, 현황판, 걷는 중 관리자 버튼).
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_shot_1118.py <그림 폴더> [gate room rem choice act board ...]
import asyncio, sys, os, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; WHAT = sys.argv[2:] or ['gate', 'room', 'rem', 'choice', 'act', 'board']; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
EXPOSE = " window.__t = new Proxy({}, {get:(_, k)=> k === 'setMini' ? (v=>{ mini = v; }) : eval(String(k))});"   # looked up lazily: most of these are declared further down the module
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src; src = src.replace(HOOK, HOOK + EXPOSE)
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); ev = pg.evaluate
        await pg.add_style_tag(content='#teamPick{display:none!important}')
        try: await ev("__dbg.setDemo(['dl-harmonia','dl-carousel','dl-coaster'], true)")
        except Exception as e: print('setDemo', str(e)[:120])
        shot = lambda n: pg.screenshot(path=f'{OUT}/{n}.jpg', type='jpeg', quality=85)
        CAM = "([x,y,z,tx,ty,tz])=>{ const c = __t; c.controls.minDistance = 1; c.camera.position.set(x, y, z); c.controls.target.set(tx, ty, tz); c.controls.update(); c.camera.lookAt(tx, ty, tz); }"
        if 'gate' in WHAT:
            o = await ev("(()=>{ const o = __t.labGateBuild(); return {x:o.g.position.x, z:o.g.position.z, ux:o.face[0], uz:o.face[1], G:__t.G}; })()"); print('gate', o)
            x, z, ux, uz, G = o['x'], o['z'], o['ux'], o['uz'], o['G']
            await ev(CAM, [x + ux*26 - uz*9, G + 6, z + uz*26 + ux*9, x, G + 3.5, z]); await asyncio.sleep(1.5); await shot('gate_closed')
            await ev(CAM, [x + ux*70, G + 34, z + uz*70, x - ux*40, G + 20, z - uz*40]); await asyncio.sleep(1.2); await shot('gate_far')
            await ev("__t.labGateBuild().st.want = true"); await ev(CAM, [x + ux*26 - uz*9, G + 6, z + uz*26 + ux*9, x, G + 3.5, z]); await asyncio.sleep(1.0); await shot('gate_opening'); await asyncio.sleep(2.2); await shot('gate_open')
            await ev("__t.labGateBuild().st.want = false"); await asyncio.sleep(1.6)
        if 'rem' in WHAT:
            await ev("(()=>{ __t.setMini({kind:'device', got:[], q:__t.QUESTS.find(q=> q.id === 'q5')}); __t.remBuild(); })()")
            for i in range(3):
                p = await ev("(i)=>{ const m = __t.REM.models[i]; m.g.visible = true; m.g.position.y = m.y0; m.state = 1; return {x:m.g.position.x, y:m.y0, z:m.g.position.z, kind:m.kind, cy:m.cy}; }", i); print('rem', i, p)
                L = (p['x']**2 + p['z']**2)**.5; ox, oz = -p['x']/L, -p['z']/L
                await ev(CAM, [p['x'] + ox*15, p['y'] + 7.5, p['z'] + oz*15, p['x'], p['y'] + max(3, p['cy']*0.6), p['z']]); await ev("(i)=> __t.remGame(i)", i); await asyncio.sleep(1.6); await shot(f'rem_{i}'); print('  game', await ev("__remGame()"))
                if i == 2:
                    for k in (await ev("__remGame().seq"))[:2]: await pg.keyboard.press('Arrow' + k); await asyncio.sleep(.15)
                    await asyncio.sleep(.3); await shot('rem_2_mid'); print('  after two keys', await ev("__remGame().at"))
                if i == 1:
                    hit = 0
                    for _ in range(400):
                        g = await ev("__remGame()")
                        if g['done'] or g['hits'] >= 2: break
                        if g['front']: await pg.keyboard.press('Space'); await asyncio.sleep(.2)
                        else: await asyncio.sleep(.02)
                    print('  bar hits', (await ev("__remGame()"))['hits']); await shot('rem_1_mid')
                await ev("__remWin()"); await asyncio.sleep(1.8); await ev("document.getElementById('vn').dataset.on && __dbg.quest().next()"); await asyncio.sleep(.6)
                await ev("(()=>{ const v = document.getElementById('vn'); for(let k = 0; k < 6 && v.dataset.on; k++) __dbg.quest().next(); })()"); await asyncio.sleep(.5)
            print('remPlay hidden after', await ev("document.getElementById('remPlay').hidden"))
        if 'room' in WHAT:
            await ev("__t.labRoomOpen(false)"); await asyncio.sleep(.8); await shot('room_calm'); await ev("__t.labRoomNoise(true)"); await asyncio.sleep(.7); await shot('room_noise')
            await ev("__t.labRoomNoise(false); __t.labRoomPing(); __t.say(__t.STORY.remDone.slice(2, 3))"); await asyncio.sleep(1.6); await shot('room_ping'); print('room', await ev("__labRoom()"))
            await ev("(()=>{ const v = document.getElementById('vn'); for(let k = 0; k < 6 && v.dataset.on; k++) __dbg.quest().next(); delete __t.labRoom().d.dataset.on; })()")
            for vp in ((1024, 600), (780, 360)):
                await pg.set_viewport_size({'width': vp[0], 'height': vp[1]}); await ev("__t.labRoomOpen(true)"); await asyncio.sleep(.6); await shot(f'room_{vp[0]}'); await ev("delete __t.labRoom().d.dataset.on")
            await pg.set_viewport_size({'width': 1280, 'height': 800})
        if 'choice' in WHAT:
            await ev("(()=>{ window.__pick = null; __t.choiceAsk(__t.CAVE_CHOICE[0], 1).then(k=>{ window.__pick = k; }); })()"); await asyncio.sleep(1.0); await shot('choice'); print('choice', await ev("__choice()"))
            await pg.set_viewport_size({'width': 780, 'height': 360}); await asyncio.sleep(.4); await shot('choice_780'); await pg.set_viewport_size({'width': 390, 'height': 800}); await asyncio.sleep(.4); await shot('choice_390'); await pg.set_viewport_size({'width': 1280, 'height': 800})
            await pg.keyboard.press('Digit2'); await asyncio.sleep(.4); print('picked', await ev("window.__pick"), 'open', await ev("__choice()"))
            await ev("(()=>{ __t.missionCard(__t.QUESTS.find(q=> q.id === 'q3'), {title0:null, hint:'알맞은 말을 골라 코덱스의 믿음을 얻으세요'}); })()"); await asyncio.sleep(1.2); await shot('card_cave'); await pg.keyboard.press('Space'); await asyncio.sleep(.5)
        if 'act' in WHAT:
            await ev("__t.stageAt('dl-ferris', __t.ACT_CAST[3]())"); await asyncio.sleep(2.6); await shot('act3_stage')
        if 'board' in WHAT:
            await pg.goto('http://127.0.0.1:8096/chapter05/index.html?team=9', wait_until='domcontentloaded', timeout=120000); await asyncio.sleep(14); await pg.keyboard.press('Escape')
            await ev("(()=>{ const v = document.getElementById('voidVn'); if(v) v.style.display = 'none'; })()"); await shot('board')
            print('board', await ev("document.getElementById('board').innerText.replace(/\\s+/g, ' ')"))
        print('errs', errs[:4]); await br.close()
asyncio.run(main())
