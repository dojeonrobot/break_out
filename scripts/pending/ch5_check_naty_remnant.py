"""2026-11-04 새 섬 흐름 점검: 예비 배전선 → 전원 연출 → 네이티 사라짐(미션 1 완료) → 미로에서 네이티 발견 → 두 번째 좌표(미션 2 완료)
→ (캠퍼스 2 건너뛰기) → 연구실 중간 점검(시뮬레이터 노이즈) → 잔재 3개 탐지·파내기·고리 해체 → 연구실 재실행 → 마지막 좌표(미션 3 완료).
사설 API 8096(VOID_STATIC=0, CH5_ADMIN_KEY=0101) + 정적 8097(저장소 루트). python scripts/pending/ch5_check_naty_remnant.py [shot_dir]"""
import asyncio, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'X-Admin-Key': '0101'}; T = 12
SHOT = sys.argv[1] if len(sys.argv) > 1 else None

async def wf(pg, expr, timeout=120):
    for _ in range(timeout*4):
        try:
            v = await pg.evaluate(expr)
            if v: return v
        except Exception: pass
        await asyncio.sleep(.25)
    raise AssertionError('timeout: ' + expr)

async def drain(pg, n=60):
    for _ in range(n):
        if not await pg.evaluate('!!__dbg.quest().vn()'): return
        await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.08)

async def shot(pg, name):
    if not SHOT: return
    await pg.evaluate('window.__raf0 = window.__raf0 || requestAnimationFrame; requestAnimationFrame = ()=>0'); await asyncio.sleep(.3)
    await pg.screenshot(path=os.path.join(SHOT, name)); await pg.evaluate('requestAnimationFrame = window.__raf0')

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=.6)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','natycheck');localStorage.setItem('void-sound','0');")
        rq = ctx.request
        await rq.post(API + '/api/void/team_reset', data={'team': T, 'confirm': 'AGAIN'}, headers=ADM)
        await rq.post(API + '/api/void/admin/skip', data={'team': T, 'mission': 'z1'}, headers=ADM)
        await rq.post(API + '/api/void/quest', data={'team': T, 'dev': 'natycheck', 'done': [], 'act': 1, 'tut': True, 'story': 3})
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='load', timeout=120000)
        await wf(pg, '!!window.__dbg?.rideState && !!window.__rem')
        await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(1)

        # ---- mission 1 ----
        await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(1); await drain(pg)
        print('dbg', await pg.evaluate("({live:__dbg.quest().live?.id, t:__dbg.target(), done:__dbg.quest().done, walk:!!__dbg.walkState?.(), mini:__dbg.quest().mini()?.kind, cp:localStorage.getItem('void-mini-12')})"), flush=True)
        await pg.evaluate('__dbg.walkTo(...__dbg.target())'); await wf(pg, "__dbg.quest().vn()?.lines[0].who==='자일로'", 40); await drain(pg)
        await pg.evaluate('__dbg.walkTo(...__dbg.yardDoor())'); await wf(pg, "!!document.querySelector('#yardDlg[data-on]')"); await asyncio.sleep(1); await drain(pg)
        await pg.evaluate('()=>{const y=__dbg.yard();y.tiles=y.sol.map(r=>r.map(c=>new Set(c)));__dbg.yardPaint()}'); await asyncio.sleep(.5)
        await pg.locator('#ydContinue').click()
        await wf(pg, "!window.__parkWake() && !!__dbg.quest().vn()", 300)
        lines = await pg.evaluate("__dbg.quest().vn().lines.map(l=>l.text).join(' / ')")
        assert '네이티가 없어요' in lines and '스카이' not in lines, lines
        await drain(pg); await wf(pg, "!!document.querySelector('#qReward[data-on]')")
        t = await pg.evaluate("[document.getElementById('qrT').textContent, document.getElementById('qrMap').textContent]")
        assert t[0] == '섬 전체 전원 복구', t
        print('OK mission 1: backup line → park wakes → Naty is gone → MISSION 1 CLEAR, no Sky Loop ride or forest shot', t, flush=True)
        await shot(pg, 'n1_reward.png')
        await asyncio.sleep(1.2); await pg.locator('#qrMap').click(); await asyncio.sleep(1.5); await drain(pg)

        # ---- mission 2 ----
        q = await pg.evaluate("__dbg.quest().done"); assert 'q1' in q, q
        await pg.evaluate('__dbg.walkTo(...__dbg.target())'); await wf(pg, "__dbg.quest().vn()?.lines[0].text.includes('깜빡여')")
        ml = await pg.evaluate("__dbg.quest().vn().lines.map(l=>l.text).join(' / ')"); assert '빛이 보이는 쪽' not in ml, ml; await drain(pg)
        await pg.evaluate('__dbg.walkTo(...__dbg.target())'); await wf(pg, "!!__dbg.quest().vn()")
        fl = await pg.evaluate("__dbg.quest().vn().lines.map(l=>l.text).join(' / ')"); assert '캠퍼스 좌표를 찾았어' in fl and '미로 정원' not in fl, fl
        await drain(pg); await wf(pg, "!!document.querySelector('#qReward[data-on]')")
        t = await pg.evaluate("[document.getElementById('qrT').textContent, document.getElementById('qrList').textContent]")
        assert t[0] == '네이티 발견 · 두 번째 좌표 확보' and '37.' in t[1], t
        print('OK mission 2: maze without light guide, Naty found, second campus coordinate given', t, flush=True)
        await shot(pg, 'n2_reward.png')
        await asyncio.sleep(1.2); await pg.locator('#qrMap').click(); await asyncio.sleep(2)

        # ---- campus 2 done by the server, act 2 already seen: start mission 3 directly ----
        await rq.post(API + '/api/void/admin/skip', data={'team': T, 'mission': 'z2'}, headers=ADM)
        await rq.post(API + '/api/void/quest', data={'team': T, 'dev': 'natycheck', 'act': 2})
        await pg.reload(wait_until='load', timeout=120000); await wf(pg, '!!window.__dbg?.rideState && !!window.__rem')
        await pg.evaluate("()=>{ const tp=document.getElementById('teamPick'); if(tp) tp.dataset.on=''; }")
        await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(1)
        await wf(pg, "__dbg.quest().done.includes('q2')")
        await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(1); await drain(pg)
        await pg.evaluate('__dbg.walkTo(...__dbg.target())'); await wf(pg, "!!__dbg.quest().vn()"); await drain(pg)
        await wf(pg, "__rem().noise", 120); await shot(pg, 'n3_midcheck_noise.png')
        print('OK mission 3: lab mid-check shows the simulator with red noise at the remnant areas', flush=True)
        for _ in range(40):
            await drain(pg)
            if await pg.evaluate("__rem().mini?.phase==='hunt'"): break
            await asyncio.sleep(.5)
        r = await pg.evaluate('__rem()'); assert r['mini'] and r['mini']['phase'] == 'hunt' and r['models'] == [0, 0, 0], r
        print('OK hunt starts with three hidden remnants (none visible)', flush=True)
        for i in range(3):
            s = (await pg.evaluate('__rem()'))['spots'][i]
            await pg.evaluate(f"__dbg.walkTo({s['x']}, {s['z']})"); await asyncio.sleep(.8)
            assert await pg.locator('#miniGo').is_visible(), 'dig button not shown near remnant'
            await pg.evaluate("()=>{ const b=document.getElementById('miniGo'); b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:1})); }")
            await wf(pg, "['dig','game'].includes(__rem().mini?.phase)", 60)
            await pg.evaluate("()=>{ const b=document.getElementById('miniGo'); b.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1})); }")
            if i == 0: await shot(pg, 'n4_dug.png')
            for _ in range(60):
                await drain(pg)
                if await pg.evaluate("!!document.querySelector('#remDlg[data-on]')"): break
                await asyncio.sleep(.25)
            await pg.locator('#rmGo').click(); await asyncio.sleep(.2)
            miss = await pg.evaluate('__rem().game.ring')
            for k in range(3):
                await pg.evaluate('__remAim()'); await pg.locator('#rmGo').click(); await asyncio.sleep(.15)
                if i == 0 and k == 0: await shot(pg, 'n5_rings.png')
            await wf(pg, "!document.querySelector('#remDlg[data-on]')", 30); await asyncio.sleep(.5); await drain(pg)
            r = await pg.evaluate('__rem()'); print(f'  remnant {i+1}: models {r["models"]} got {r["mini"]["got"] if r["mini"] else None} (miss tap kept ring {miss})', flush=True)
        await wf(pg, "__rem().mini?.phase==='walk'", 30)
        await pg.evaluate('__dbg.walkTo(...__dbg.labDoor())'); await asyncio.sleep(1)
        for _ in range(80):
            await drain(pg)
            if await pg.evaluate("!!document.querySelector('#qReward[data-on]')"): break
            await asyncio.sleep(.5)
        t = await pg.evaluate("[document.getElementById('qrT').textContent, document.getElementById('qrList').textContent, document.getElementById('qrCount').textContent]")
        assert t[0] == '선대의 잔재 해체' and '37.' in t[1], t
        print('OK three remnants dismantled, lab re-run, last campus coordinate given', t, flush=True)
        await shot(pg, 'n6_reward.png')
        nc = await pg.evaluate("NATY_COLOR = null");
        assert not errs, errs; print('OK no runtime errors', flush=True)
        await br.close()
asyncio.run(main())
