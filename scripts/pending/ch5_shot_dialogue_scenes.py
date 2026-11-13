# 대사 장면의 배경 확인: 대사 창이 뜬 순간의 화면을 장면마다 찍는다. ① 미션 1 자일로 발견 ② 배전선 뒤 자일로(전원 연출 뒤) ③ 미션 2 네이티 발견(앞모습) ④ 1막 시뮬레이터(흐름을 따라가는 중 파동이 없는지)
# 사설 API 8096 + 정적 8097.  python scripts/pending/ch5_shot_dialogue_scenes.py <그림 폴더>
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
async def session(br, dev, zones, done, act):
    ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
    async def route(r):
        q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
        await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
    await ctx.route(re.compile(r'.*/api/void/.*'), route)
    await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');localStorage.setItem('void-sound','0');")
    post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
    await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
    for z in zones: await post('admin/skip', {'team': T, 'mission': z}, True)
    body = {'team': T, 'dev': dev, 'done': done, 'act': act, 'tut': True}
    if done: body.update(story=3, power=True)
    await post('quest', body)
    pg = await ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200]))
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
        except Exception: pass
        await asyncio.sleep(.25)
    await asyncio.sleep(4); return ctx, pg
VN = "document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''"
async def until_line(pg, word, shot, limit=200):
    for _ in range(limit):
        t = await pg.evaluate(VN)
        if t and word in t: await asyncio.sleep(.9); await pg.screenshot(path=os.path.join(OUT, shot)); print('shot', shot, '|', t[:40]); return True
        if t: await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.12)
        else: await asyncio.sleep(.35)
    print('MISS', shot, word); return False
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        only = sys.argv[2] if len(sys.argv) > 2 else ''
        # ①② mission 1
        ctx, pg = await session(br, 'dsa', ['z1'], [], 1)
        await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        for _ in range(40):
            if not await pg.evaluate(VN): break
            await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.12)
        tg = await pg.evaluate('__dbg.target()'); await pg.evaluate("([x, z])=> __dbg.walkTo(x + 2, z + 2)", tg); await asyncio.sleep(2.5)
        await pg.screenshot(path=os.path.join(OUT, '1_xylo_found.png')); print('shot 1_xylo_found |', (await pg.evaluate(VN))[:40])
        for _ in range(80):
            if await pg.evaluate("!!__dbg.mini() && __dbg.mini().phase === 'walk'"): break
            if await pg.evaluate(VN): await pg.evaluate('__dbg.quest().next()')
            await asyncio.sleep(.15)
        yd = await pg.evaluate('__dbg.yardDoor()'); await pg.evaluate("([x, z])=> __dbg.walkTo(x, z)", yd)
        for _ in range(60):
            if await pg.evaluate("!!document.getElementById('yardDlg').dataset.on"): break
            await asyncio.sleep(.3)
        for _ in range(30):
            if not await pg.evaluate(VN): break
            await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.12)
        await pg.evaluate("__dbg.yardWin ? __dbg.yardWin() : (__dbg.yard() && (__dbg.yard().done = true))"); await asyncio.sleep(1)
        await pg.evaluate("(()=>{ const b = document.getElementById('ydContinue'); b.hidden = false; b.click(); })()")
        await until_line(pg, '돌아간다', '2_after_yard_1.png', 260); await until_line(pg, '네이티가 없어요', '2_after_yard_2.png', 60); print('errs', pg.errs[:2]); await ctx.close()
        # ③ mission 2: Naty in the maze
        ctx, pg = await session(br, 'dsb', ['z1'], ['q1'], 1)
        await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        for _ in range(40):
            if not await pg.evaluate(VN): break
            await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.12)
        M = await pg.evaluate("(()=>{ const M = __dbg.maze(); return {cx:M.cx, cz:M.cz, S:M.S, cell:M.cell}; })()")
        await pg.evaluate("([x, z])=> __dbg.walkTo(x, z)", [M['cx'], M['cz'] - M['S']/2 - 3]); await asyncio.sleep(2)
        for _ in range(40):
            if not await pg.evaluate(VN): await asyncio.sleep(.4)
            if not await pg.evaluate(VN): break
            await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.12)
        await pg.evaluate("([x, z, cx, cz])=>{ const w = __dbg.walk(); w.x = x; w.z = z; w.yaw = Math.atan2(cx - x, cz - z); w.pitch = 0; w.snap = true; }", [M['cx'], M['cz'] - M['cell']*0.9, M['cx'], M['cz']]); await asyncio.sleep(1.2)
        await pg.screenshot(path=os.path.join(OUT, '3_naty_before.png'))
        await pg.evaluate("([x, z])=> __dbg.walkTo(x, z)", [M['cx'] + 0.5, M['cz'] - 1.5]); await asyncio.sleep(2.2); await pg.screenshot(path=os.path.join(OUT, '3_naty_found.png')); print('shot 3_naty_found |', (await pg.evaluate(VN))[:40], 'errs', pg.errs[:2]); await ctx.close()
        # ④ act 1 simulator: no shock rings while the flow is followed
        ctx, pg = await session(br, 'dsc', ['z1'], [], 0); seen = 0
        for _ in range(260):
            st = await pg.evaluate("({sim:__dbg.simState().simOn, vn:" + VN + "})")
            if st['sim']:
                seen += 1
                if seen in (4, 9, 14, 20, 40): await pg.screenshot(path=os.path.join(OUT, f'4_sim_follow_{seen}.png')); print('shot sim', seen, st['vn'][:30])
                if seen > 41: break
            else: await pg.keyboard.press('Space')
            await asyncio.sleep(.5)
        print('errs', pg.errs[:2]); await ctx.close(); await br.close()
asyncio.run(main())
