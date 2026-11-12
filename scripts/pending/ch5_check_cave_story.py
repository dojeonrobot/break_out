# 미션 5 「동굴 벽화 스토리」 점검. 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_cave_story.py [그림 폴더]
#  기록 다섯·미션 1~4 완료·3막까지 본 조로 시작 → 코덱스에게 감 → 발견 대사 → 동굴 안(벽화 방) → 벽화 4점이 차례로 밝아지고 닳은 자리가 채워짐 → 마지막 벽
#  → 밖으로 나오고(캐릭터 원위치) 환원 시뮬레이션으로 이어짐. 동굴 바깥 모습도 찍는다.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 4
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg, flush=True)
    if not ok: fails.append(msg)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','cavestory');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
        for z in ('z1', 'z2', 'z3'): await post('admin/skip', {'team': T, 'mission': z}, True)
        await post('quest', {'team': T, 'dev': 'cavestory', 'done': ['q1', 'q2', 'q4', 'q5'], 'act': 3, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:400]))
        ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__cave==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        async def shot(n):
            if SHOT:
                os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, n + '.png'), timeout=60000)
        async def line():
            return await ev("document.getElementById('vn').dataset.on ? (document.getElementById('vnName').textContent || '(서술)') + ': ' + document.getElementById('vnText').textContent : ''")
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(2)
        # the cave from outside
        for n, a in {'out_front': (-28, -488, -42, -524, 9), 'out_side': (-78, -500, -42, -526, 12), 'out_far': (-10, -440, -42, -528, 26)}.items():
            for _ in range(2):
                await ev(f"__vikEye({a[0]},{a[1]},{a[2]},{a[3]},{a[4]})"); await asyncio.sleep(1.4)
            await shot(n)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        for _ in range(30):
            if not await line(): break
            await ev('__dbg.quest().next()'); await asyncio.sleep(.1)
        check(await ev("__dbg.quest().live?.id") == 'q3', 'mission 5 is live')
        t = await ev('__dbg.target()'); await ev(f"__dbg.walkTo({t[0] + 2}, {t[1] + 2})")
        for _ in range(80):
            if await line(): break
            await asyncio.sleep(.25)
        await asyncio.sleep(1); await shot('found')
        seen = []; shots = {'보이드의 불빛만': 'in_0', '노아, 루나, 렌이야': 'mural_1', '원류민은 섬에 대해': 'mural_2', '측정기를 든 루나가': 'mural_3_worn', '……나다': 'mural_3', '렌의 장치는 점점': 'mural_4_worn', '보이드다! 보이드가': 'mural_4', '이건…… 우리 같아': 'mural_5'}
        states = {}
        for i in range(700):
            c = await ev('__cave()'); ln = await line()
            if ln and (not seen or seen[-1] != ln):
                seen.append(ln)
                for k, n in shots.items():
                    if k in ln:
                        await asyncio.sleep(1.6); states[n] = await ev('__cave()'); await shot(n)
            if await ev("!!document.getElementById('simDone').dataset.on || document.getElementById('simHud') && __dbg.simState && false"): break
            if not c['on'] and len(seen) > 30 and not ln: break
            if ln: await ev('__dbg.quest().next()')
            await asyncio.sleep(.22)
        print('\n'.join(seen))
        check(sum('코덱스: 왔군. 기록을 모두 채웠다고 들었다.' in x for x in seen) == 1, 'the found dialogue is the script one')
        check(all(n in states for n in shots.values()), f'every mural step was reached {sorted(set(shots.values()) - set(states))}')
        if 'mural_3_worn' in states and 'mural_3' in states:
            a, b = states['mural_3_worn']['room'], states['mural_3']['room']
            check(a['focus'] == 2 and a['k'][2] < 0.05 and b['k'][2] > 0.95, f"mural 3: worn before the line, whole after it ({a['k'][2]} -> {b['k'][2]})")
            check(b['lit'][2] > 0.9 and b['lit'][3] < 0.35, f"the mural in focus is lit, the next one is still dark ({b['lit']})")
        check(states.get('mural_5', {}).get('room', {}).get('focus') == 4, 'the last wall is shown')
        await asyncio.sleep(3); c = await ev('__cave()'); check(not c['on'] and not c['inside'], f'after the story the room is left {c}')
        check('q3' in await ev('__dbg.quest().done'), 'mission 5 is saved as done')
        back = await ev("(()=>{ const c = __dbg.chars(); return Object.entries(c).map(([k, g])=> [k, g.parent ? (g.parent.type === 'Scene' && g.parent !== __dbg.islRoot.parent ? 'ROOM' : 'ok') : 'none']); })()")
        check(all(v == 'ok' for _, v in back), f'the characters are back on the island {back}')
        await asyncio.sleep(4); await shot('after'); print('sim', await ev("__dbg.simState ? JSON.stringify(__dbg.simState()).slice(0, 160) : ''"))
        print('errors:', errs); check(not errs, 'no page errors'); print('FAILS', len(fails), fails)
        await br.close()
asyncio.run(main())
