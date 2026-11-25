"""갤럭시 탭처럼(터치·pointer:coarse) 띄워 걷기 화면을 찍는다. 사용: python -I ch5_shot_tab_touch_1125.py <출력폴더> [w h]
서버: API 8096(VOID_STATIC=0, CH5_ADMIN_KEY=0101), 정적 8097"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1280, 690)
STATIC, API = 'http://127.0.0.1:8097', 'http://127.0.0.1:8096'
UA = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': W, 'height': H}, screen={'width': W, 'height': H}, has_touch=True, is_mobile=True, device_scale_factor=2, user_agent=UA)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));")
        async def route(r):
            q = r.request
            rs = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=rs.status, body=await rs.body(), headers={'content-type': rs.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
        await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team': 4, 'confirm': 'AGAIN'}), headers=ADM)
        await ctx.request.post(API + '/api/void/admin/skip', data=json.dumps({'team': 4, 'mission': 'z1'}), headers=ADM)   # 기록 1 완료 → 미션 1(걷기) 열림
        await ctx.request.post(API + '/api/void/quest', data=json.dumps({'team': 4, 'dev': 'tab', 'tut': True}), headers={'content-type': 'application/json'})
        pg = await ctx.new_page()
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Emulation.setEmitTouchEventsForMouse', {'enabled': True, 'configuration': 'mobile'})
        await cdp.send('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
        await pg.goto(f'{STATIC}/chapter05/index.html?team=4', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        print('media', await pg.evaluate("({coarse:matchMedia('(pointer:coarse)').matches, fine:matchMedia('(pointer:fine)').matches, hover:matchMedia('(hover:none)').matches, touch:'ontouchstart' in window})"))
        await asyncio.sleep(3)
        await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(2)
        for _ in range(40):   # 기록 1 복구 막 연출을 끝까지 넘긴다(관리자 건너뛰기·카드·대사)
            st = await pg.evaluate("({skip:(()=>{const a=document.getElementById('admSkip');return !!a&&!a.hidden})(), busy:['recDone','vn','voidVn','missionCard','qReward','restoreDlg'].some(i=>{const e=document.getElementById(i);return e&&e.dataset.on!==undefined}), sim:__dbg.simState().simOn})")
            if st['skip']: await pg.locator('#admSkip').tap()
            elif st['busy']: await pg.touchscreen.tap(W // 2, H // 3)
            elif not st['sim']: break
            await asyncio.sleep(1.2)
        print('act done', st)
        await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(4)
        r = await pg.evaluate("(()=>{try{__dbg.startWalk('리코·제로');return 'ok '+((document.getElementById('toast')||{}).textContent||'')}catch(e){return String(e)}})()"); await asyncio.sleep(5)
        if 'ok' in r and not await pg.evaluate("document.body.classList.contains('walk')"):
            # 섬의 「탐험」 버튼으로 실제 사용자처럼 들어간다
            for sel in ['#lWalk', '#walkPick .pair', '#heroPick button']:
                try:
                    if await pg.locator(sel).first.is_visible(): await pg.locator(sel).first.tap(); await asyncio.sleep(3)
                except Exception: pass
            r += ' | ui-path walk=' + str(await pg.evaluate("document.body.classList.contains('walk')")) + ' toast=' + str(await pg.evaluate("(document.getElementById('toast')||{}).textContent||''"))
        info = await pg.evaluate(r'''()=>({walk:document.body.classList.contains('walk'), btn:['walkRun','walkJump','walkPad','sndBtn','adminBtn','questHud','walkHud'].map(id=>{const e=document.getElementById(id);if(!e)return [id,'none'];const s=getComputedStyle(e);if(e.hidden||s.display==='none')return [id,'hidden'];const q=e.getBoundingClientRect();return [id,Math.round(q.left),Math.round(q.top),Math.round(q.right),Math.round(q.bottom)]})})''')
        print('startWalk', r, json.dumps(info, ensure_ascii=False))
        # 캐릭터 고르기 창이 떠 있으면 첫 캐릭터
        try:
            if await pg.evaluate("(()=>{const e=document.getElementById('heroPick');return !!e&&getComputedStyle(e).display!=='none'})()"):
                await pg.locator('#heroPick button').first.tap(); await asyncio.sleep(4)
                info = await pg.evaluate(r'''()=>({walk:document.body.classList.contains('walk'), btn:['walkRun','walkJump','walkPad','sndBtn'].map(id=>{const e=document.getElementById(id);if(!e||e.hidden||getComputedStyle(e).display==='none')return [id,'hidden'];const q=e.getBoundingClientRect();return [id,Math.round(q.left),Math.round(q.top),Math.round(q.right),Math.round(q.bottom)]})})''')
                print('after pick', json.dumps(info, ensure_ascii=False))
        except Exception as e: print('pick', e)
        for _ in range(30):   # 완료 카드·대사는 탭으로 넘긴다
            busy = await pg.evaluate("['recDone','vn','voidVn','missionCard','qReward'].some(i=>{const e=document.getElementById(i);return e&&e.dataset.on!==undefined})")
            if not busy: break
            await pg.touchscreen.tap(W // 2, H // 3); await asyncio.sleep(1.2)
        await asyncio.sleep(1.5)
        await pg.screenshot(path=str(OUT / f'walk_{W}x{H}_off.png'))
        try:
            await pg.locator('#walkRun').tap(timeout=3000); await asyncio.sleep(.8)
            await pg.screenshot(path=str(OUT / f'walk_{W}x{H}_on.png'))
            print('run pressed', await pg.evaluate("document.getElementById('walkRun').getAttribute('aria-pressed')"))
        except Exception as e: print('tap run', str(e)[:120])
        await br.close()
asyncio.run(main())
