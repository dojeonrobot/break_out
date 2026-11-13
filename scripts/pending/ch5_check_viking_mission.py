# 미션 3 「바이킹을 다시 세워라」 점검. 사설 API 8096(VOID_STATIC=0 CH5_ADMIN_KEY=0101) + 정적 8097.
# 사용: python scripts/pending/ch5_check_viking_mission.py <어셈블리.stl> [그림 폴더]
#  1) 두 번째 캠퍼스 기록 전에는 바이킹 카드에 올리기 버튼이 없다
#  2) 기록 2 뒤: 미션 3이 열리고 자일로가 공사장에 있다 → 찾아가면 대사 → 「바이킹 모델 올리기」 상자
#  3) 새로고침 뒤 「이어하기」로 올리기 단계가 다시 뜬다
#  4) 모델을 올리면 바이킹이 서고 대사 → 완료 카드(마지막 좌표) → 캠퍼스
#  5) 같은 조의 다른 태블릿: 바이킹이 이미 서 있으면 「이 바이킹으로 계속」으로 끝낸다
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
STL = sys.argv[1]; SHOT = sys.argv[2] if len(sys.argv) > 2 else None
fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg, flush=True)
    if not ok: fails.append(msg)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        errs = []
        async def device(dev):
            ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True)
            rq = ctx.request
            async def route(r):
                q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','{dev}');localStorage.setItem('void-sound','0');")
            pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            return ctx, rq, pg
        ctx, rq, pg = await device('vikone')
        ev = pg.evaluate
        async def wf(pg, expr, t=90):
            for _ in range(int(t*4)):
                try:
                    if await pg.evaluate(expr): return True
                except Exception: pass
                await asyncio.sleep(.25)
            raise AssertionError('timeout ' + expr + ' ' + json.dumps(await pg.evaluate("({vn:__dbg.quest().vn()?.lines?.map(l=>l.text.slice(0,20)), mini:__dbg.mini(), vik:__vikQ(), live:__dbg.quest().live?.id, done:__dbg.quest().done})"), ensure_ascii=False)[:700])
        async def drain(pg, n=80):
            said = []
            for _ in range(n):
                if not await pg.evaluate('!!__dbg.quest().vn()'):
                    await asyncio.sleep(.4)
                    if not await pg.evaluate('!!__dbg.quest().vn()'): return said
                t = await pg.evaluate("document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent")
                if not said or said[-1] != t: said.append(t)
                await pg.evaluate('__dbg.quest().next()'); await asyncio.sleep(.08)
            return said
        async def shot(pg, n):
            if SHOT:
                os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, n + '.png'), timeout=60000)
        async def load(pg):
            await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
            await wf(pg, "typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__vikQ==='function' && !!window.__rem", 120)
            await pg.evaluate("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(1.5)
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/viking_clear', {'team': T}, True)
        await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'vikone', 'done': ['q1', 'q2'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        # 1) before the second campus record
        await load(pg)
        print('GL', await ev("(()=>{const g=__dbg.renderer.getContext(),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)
        check(await ev('__vikGate()') is False, 'before record 2: the upload is closed')
        await ev('__vikOpen()'); await asyncio.sleep(.8)
        card = await ev("document.querySelector('#iIsl .vik')?.innerText || ''")
        check('올려' not in card and '미션 3' in card, f'before record 2: the place card has no upload button ({card!r})')
        await shot(pg, 'vm0_card_closed')
        # 2) record 2 is back, act 2 seen
        await post('admin/skip', {'team': T, 'mission': 'z2'}, True)
        await post('quest', {'team': T, 'dev': 'vikone', 'done': ['q1', 'q2'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
        await load(pg)
        check(await ev('__vikGate()') is True, 'after record 2: the upload is open')
        pill = await ev("(()=>{const e=document.getElementById('questPill');return e&&!e.hidden?e.innerText:''})()")
        print('pill', repr(pill))
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); said = await drain(pg); print('intro', said)
        check(await ev("__dbg.quest().live?.id") == 'q4', 'mission 3 is live')
        hud = await ev("document.getElementById('questHud').innerText"); print('hud', repr(hud))
        check('바이킹을 다시 세워라' in hud and '1 / 2' in hud, 'the mission box names the viking mission, step 1 / 2')
        q = await ev('__vikQ()'); print('vikQ', q)
        d = ((q['spot'][3] - q['xylo'][0])**2 + (q['spot'][4] - q['xylo'][1])**2)**.5
        check(d < 1, f'자일로 stands at the viking site (off by {d:.1f})')
        blocked = await ev(f"[__dbg.walkBlocked({q['spot'][0]},{q['spot'][1]}), __dbg.walkBlocked({q['spot'][3]},{q['spot'][4]})]"); check(blocked == [False, False], f'the meeting point and 자일로 are on walkable ground {blocked}')
        await ev(f"__dbg.walkTo({q['spot'][0] + 3},{q['spot'][1] + 3})"); await wf(pg, '!!__dbg.quest().vn()', 20); await asyncio.sleep(1.2); await shot(pg, 'vm1_found')
        said = await drain(pg); print('found', said)
        check(any('코덱스가 도로랜드를 공격했을 때' in t for t in said), 'the found dialogue gives the reason (the attack)')
        await wf(pg, "__vikQ().phase==='upload' && __vikQ().box", 20)
        q = await ev('__vikQ()'); check(q['go'] == '바이킹 모델 올리기' and not q['done'], f"upload step: one button 「{q['go']}」")
        hud = await ev("document.getElementById('questHud').innerText"); check('2 / 2' in hud, f'step 2 / 2 ({hud!r})')
        await asyncio.sleep(1); await shot(pg, 'vm2_upload_box')
        # 3) reload: resume
        await load(pg)
        pill = await ev("(()=>{const e=document.getElementById('questPill');return e&&!e.hidden?e.innerText:''})()"); check('이어하기' in pill, f'after a reload the pill offers to resume ({pill!r})')
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5); await drain(pg); await asyncio.sleep(7)
        q = await ev('__vikQ()'); print('resume', q['phase'], repr(await ev("document.getElementById('questHud').innerText")))
        if q['phase'] == 'walk':
            await shot(pg, 'vm2b_resume_far'); await ev(f"__dbg.walkTo({q['spot'][3] - 3},{q['spot'][4] - 3})")
        await wf(pg, "__vikQ().phase==='upload' && __vikQ().box", 20); check(True, 'resumed at the upload step'); await asyncio.sleep(1); await shot(pg, 'vm2c_resume_box')
        # 4) upload
        inp = await pg.evaluate_handle("[...document.querySelectorAll('input[type=file]')].find(i=> i.parentElement===document.body && i.hidden)")
        await inp.as_element().set_input_files(STL)
        await wf(pg, '__vik().on', 30); check(True, 'the viking stands after the upload'); await asyncio.sleep(2.5); await shot(pg, 'vm3_rising')
        await wf(pg, '!!__dbg.quest().vn()', 20); await asyncio.sleep(.8); await shot(pg, 'vm4_done_dialogue')
        said = await drain(pg); print('done', said); check(any('우리가 만든 바이킹' in t for t in said), 'the completion dialogue plays')
        await wf(pg, "!!document.getElementById('qReward').dataset.on", 20)
        rw = await ev("document.getElementById('qReward').innerText"); print('reward', repr(rw)); await shot(pg, 'vm5_reward')
        check('MISSION 3' in rw and '바이킹 복구' in rw and '미션 4 · 숨겨진 잔재를 찾아라' in rw and '37.' not in rw, 'reward card: mission 3, the viking, straight on to mission 4 (no coordinate yet)')
        check('q4' in await ev('__dbg.quest().done'), 'mission 3 is saved as done')
        v = await ev('__vik()'); check(v['on'] and v['asm'], f"the uploaded assembly is up (asm {v['asm']}, parts {v['parts']})")
        # 4b) mission 4: the lab under the wheel, the measurement, three remnants, the last coordinate
        await ev("document.getElementById('qrMap').click()"); await asyncio.sleep(2.5); said = await drain(pg); print('m4 intro', said)
        check(await ev("__dbg.quest().live?.id") == 'q5', 'mission 4 (the lab) is live right after the viking')
        hud = await ev("document.getElementById('questHud').innerText"); print('hud', repr(hud)); check('미션 4' in hud and '연구실' in hud, 'the mission box points to the lab')
        await ev('__dbg.walkTo(...__dbg.labDoor())'); await wf(pg, '!!__dbg.quest().vn()', 20); said = []
        for _ in range(240):
            said += [t for t in await drain(pg) if t not in said]
            await ev("window.__sliceWin && __sliceWin()")
            if await ev("__rem().noise") and SHOT and not os.path.exists(os.path.join(SHOT, 'vm5b_noise.png')): await shot(pg, 'vm5b_noise')
            if await ev("__rem().mini?.phase==='hunt'"): break
            await asyncio.sleep(.5)
        print('lab', said)
        # the hunt is on the rail now: a cut to the Sky Loop station, board, lock on three times while riding, dismantle each
        for _ in range(120):
            said += [t for t in await drain(pg) if t not in said]
            if await ev("__rem().mini?.phase==='walk'"): break
            await asyncio.sleep(.5)
        r0 = await ev('__rem()'); st = r0['station']; ws = await ev('__dbg.walkState()'); dist = ((ws['x'] - st[0])**2 + (ws['z'] - st[1])**2)**.5
        check(r0['mini'] and r0['mini']['phase'] == 'walk' and dist < 40, f'after the measurement the pair stand by the Sky Loop station ({dist:.0f} away) and walk to it')
        check(min(r0['edge']) > 400, f"the three remnants sit on the outskirts, just outside the track (distance from the centre {r0['edge']}; the track is not a circle)")
        hud = await ev("document.getElementById('questHud').innerText"); check('스카이 루프 역' in hud, f'the mission box points to the station ({hud!r})'); await shot(pg, 'vm5c_station')
        await ev(f"__dbg.walkTo({st[0]}, {st[1]})"); await wf(pg, '!!__dbg.quest().vn()', 20); said = await drain(pg); print('board', said)
        await wf(pg, "!!__rem().ride", 20); check(await ev("document.getElementById('miniGo').textContent") == '탐지', 'on the train: the 「탐지」 button'); await asyncio.sleep(1.5); await shot(pg, 'vm5c_riding')
        await ev('__remBoost(6)'); await pg.keyboard.down('Space'); found = 0
        for i in range(3):
            if i == 0:
                await wf(pg, '!!(__rem().ride && __rem().ride.pause)', 60); await asyncio.sleep(1.3); await shot(pg, 'vm5c_found')
            for _ in range(400):
                await drain(pg)
                if await ev("!!(__rem().game && !__rem().game.done)"): break
                await asyncio.sleep(.25)
            await asyncio.sleep(1.2); r1 = await ev('__rem()')
            if i == 0:
                await shot(pg, 'vm5c_game'); print('  on the ground', r1['down'], 'camera', r1['cam']); check(r1['down'] and r1['cam'][1] < r1['station'][0]*0 + 12, 'the view comes down beside the remnant (camera low)')
                await ev("()=>{ const G = __rem().game; }"); await pg.keyboard.up('Space')
                miss = await ev("(()=>{ const m = document.getElementById('qhHint'); return m.textContent; })()"); print('  hint', repr(miss))
            for k in range(8):
                if await ev("!__rem().game || __rem().game.done"): break
                await ev("__remAim()"); await asyncio.sleep(.12); await ev("document.getElementById('miniGo').click()"); await asyncio.sleep(.25)
                if i == 0 and k == 2: await shot(pg, 'vm5c_game_mid')
            await wf(pg, "!__rem().game", 30); await asyncio.sleep(.5); await drain(pg); found += 1
            if i == 0:
                await asyncio.sleep(2.5); r2 = await ev('__rem()'); print('  back on the train', r2['down'], r2['cam']); check(not r2['down'] and r2['cam'][1] > 20, 'after it the view is back on the train'); await shot(pg, 'vm5c_back')
            await pg.keyboard.down('Space')
            print('  remnant', i + 1, await ev("[__rem().models, __rem().mini?.got, __rem().ride]"), flush=True)
        check(found == 3 and await ev("(__rem().mini?.got || []).length") == 3, 'three remnants found from the train and dismantled')
        await pg.keyboard.up('Space'); said = []
        for _ in range(240):
            said += [t for t in await drain(pg) if t not in said]
            if await ev("!!document.querySelector('#qReward[data-on]')"): break
            await asyncio.sleep(.5)
        print('rerun', said); rw = await ev("document.getElementById('qReward').innerText"); print('reward', repr(rw)); await shot(pg, 'vm5d_reward4')
        check('MISSION 4' in rw and '선대의 잔재 해체' in rw and '기록 3' in rw and '37.' in rw, 'reward card: mission 4, the remnants, the third coordinate')
        check('q5' in await ev('__dbg.quest().done'), 'mission 4 is saved as done')
        await ev("document.getElementById('qrMap').click()"); await wf(pg, "!!document.getElementById('voidVn').dataset.on", 20)
        vt = await ev("document.getElementById('voidTxt').textContent"); print('campus', repr(vt)); check('마지막 좌표' in vt, 'back on the campus the void points to the last coordinate'); await shot(pg, 'vm6_campus')
        await ctx.close()
        # 5) another tablet of the same team: the viking is already up
        ctx, rq2, pg2 = await device('viktwo')
        await rq2.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'viktwo', 'done': ['q1', 'q2'], 'act': 2, 'tut': True, 'story': 3, 'power': True}), headers={'content-type': 'application/json'})
        await load(pg2)
        await pg2.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); await drain(pg2)
        q = await pg2.evaluate('__vikQ()'); await pg2.evaluate(f"__dbg.walkTo({q['spot'][0] + 3},{q['spot'][1] + 3})"); await wf(pg2, '!!__dbg.quest().vn()', 20); await drain(pg2)
        await wf(pg2, "__vikQ().phase==='upload' && __vikQ().box", 20); q = await pg2.evaluate('__vikQ()')
        check(q['go'] == '다른 모델로 바꾸기' and q['done'], f"second tablet: 「{q['go']}」 + 「이 바이킹으로 계속」"); await asyncio.sleep(1); await shot(pg2, 'vm7_second_tablet')
        await pg2.evaluate("document.getElementById('miniDone').click()"); await wf(pg2, '!!__dbg.quest().vn()', 20); await drain(pg2)
        await wf(pg2, "!!document.getElementById('qReward').dataset.on", 20); check('q4' in await pg2.evaluate('__dbg.quest().done'), 'second tablet finishes with the viking that is up')
        check(await pg2.evaluate('__dbg.bakedAudit().length') == 0, 'bakedAudit is empty')
        await ctx.close(); await br.close()
        print('errors:', errs)
        check(not errs, 'no page errors')
        print('FAILS', len(fails), fails)
asyncio.run(main())
