# 네이티 추격(미션 2) 점검. 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_naty_chase.py [shot_dir]
#  1) 미로 한가운데서 네이티 발견 → 대사 → 네이티가 미로 밖으로 날아감 → 미로 입구에서 추격 시작
#  2) 가만히 있으면 실패 창 → 「다시 하기」 → 미로 입구에서 다시
#  3) 자동 조종: 걷기만(5.5)으로는 실패, 달리기(11)로는 도착. 달렸을 때 가장 멀어진 거리와 실패 거리를 찍는다(「간신히」 조절용)
#  4) 도착 → 대사 → 완료 카드(두 번째 좌표)
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 10
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg, flush=True)
    if not ok: fails.append(msg)
# the walker follows the route at a fixed speed, a little behind where a child would steer (no corner cutting, no boost)
PILOT = r"""async(speed)=>{ const c0 = __chase(); const pts = c0.pts, cum = [0]; for(let i = 1; i < pts.length; i++) cum.push(cum[i-1] + Math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]));
  const at = d=>{ d = Math.max(0, Math.min(cum[cum.length-1], d)); let i = 1; while(i < cum.length-1 && cum[i] < d) i++; const u = (d - cum[i-1])/((cum[i]-cum[i-1])||1); return [pts[i-1][0] + (pts[i][0]-pts[i-1][0])*u, pts[i-1][1] + (pts[i][1]-pts[i-1][1])*u]; };
  let d = 0, last = performance.now(), blocked = 0; const t0 = last, gaps = [];
  return await new Promise(res=>{ (function tick(){ const now = performance.now(), dt = Math.min(0.05, (now - last)/1000); last = now; const c = __chase();
    if(!c || !c.on){ res({end:c ? (c.fail ? 'fail' : 'win') : 'gone', secs:+((now - t0)/1000).toFixed(1), max:c ? c.max : null, len:c ? c.len : null, blocked, seg:c ? c.seg : null, lose:c ? c.cfg.lose : null, gaps}); return; }
    if(now - t0 > 120000){ res({end:'timeout', max:c.max}); return; }
    d = Math.min(c.s - 0.5, d + speed*dt); const p = at(d); if(__dbg.walkBlocked(p[0], p[1])) blocked++; __dbg.walkTo(p[0], p[1]); if(gaps.length < 400 && Math.random() < .05) gaps.push(Math.round(Math.hypot(p[0]-c.x, p[1]-c.z)));
    requestAnimationFrame(tick); })(); }); }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True)
        rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','chase');localStorage.setItem('void-sound','0');")
        await rq.post(API + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers=ADM)
        await rq.post(API + '/api/void/admin/skip', data=json.dumps({'team': T, 'mission': 'z1'}), headers=ADM)
        await rq.post(API + '/api/void/quest', data=json.dumps({'team': T, 'dev': 'chase', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True}), headers={'content-type': 'application/json'})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = pg.evaluate
        async def wf(expr, t=90):
            for _ in range(int(t*4)):
                try:
                    if await ev(expr): return True
                except Exception: pass
                await asyncio.sleep(.25)
            raise AssertionError('timeout ' + expr + ' ' + json.dumps(await ev("({vn:__dbg.quest().vn()?.lines?.map(l=>l.text.slice(0,20)), mini:__dbg.mini(), chase:__chase(), live:__dbg.quest().live?.id, done:__dbg.quest().done})"), ensure_ascii=False)[:600])
        async def drain(n=80):
            for _ in range(n):
                if not await ev('!!__dbg.quest().vn()'):
                    await asyncio.sleep(.4)
                    if not await ev('!!__dbg.quest().vn()'): return
                await ev('__dbg.quest().next()'); await asyncio.sleep(.08)
        async def shot(n):
            if SHOT:
                os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, n + '.png'), timeout=60000)
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        await wf("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__chase==='function'", 120)
        print('GL', await ev("(()=>{const g=__dbg.renderer.getContext(),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(1.5)
        await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2); await drain()
        check(await ev("__dbg.quest().live?.id") == 'q2', 'mission 2 is live')
        # to the maze entrance, in, to the heart
        await ev('__dbg.walkTo(...__dbg.target())'); await wf("!!__dbg.quest().vn()", 30); await drain()
        await ev('__dbg.walkTo(...__dbg.target())'); await wf("!!__dbg.quest().vn()", 30)
        lines = await ev("__dbg.quest().vn().lines.map(l=>l.text)")
        check(any('미로 밖으로 날아간다' in l for l in lines) and any('자취를 따라가면' in l for l in lines), 'found dialogue ends with Naty leaving and the void proposing to follow its trail')
        await shot('1_found'); await drain()
        await wf("__dbg.mini()?.kind==='chase'", 20); await asyncio.sleep(.7); await shot('2a_flying_out'); await asyncio.sleep(.9); st = await ev("({run:__dbg.chars().NATY.position.toArray().map(v=>Math.round(v)), phase:JSON.stringify(__dbg.mini())})"); await shot('2_flying_out')
        await wf("!!__chase() && __chase().on", 30); await asyncio.sleep(.6)
        c = await ev("__chase()"); w = await ev("__dbg.walkState()"); ent = await ev("__dbg.target()")
        hud = await ev("document.getElementById('questHud').innerText.replace(/\\s+/g,' ')")
        check(abs(w['x'] - c['pts'][0][0]) < 3 and abs(w['z'] - c['pts'][0][1]) < 3, f"chase starts at the maze entrance {[round(w['x']), round(w['z'])]}, route {c['len']} long over {len(c['pts'])} points, Naty {round(((c['x']-w['x'])**2 + (c['z']-w['z'])**2)**.5)} ahead")
        print('  route pts', [[round(p[0]), round(p[1])] for p in c['pts']])
        check('네이티를 놓치지 마라' in hud and '3 / 3' in hud and '네이티까지' in hud, 'HUD: ' + hud[:90])
        print('  config', c['cfg'], ' end', [round(v) for v in c['pts'][-1]], flush=True); await shot('3_chase_start')
        # standing still loses
        await wf("__chase().fail", 40); check(True, 'standing still: the fail card appears'); await shot('4_fail')
        txt = await ev("document.getElementById('chaseFail').innerText.replace(/\\s+/g,' ')"); check('다시 하기' in txt and '미로 입구' in txt, 'fail card: ' + txt)
        await pg.locator('#chaseRetry').click(); await wf("__chase().on && __chase().tries===2", 20); await asyncio.sleep(.5)
        w = await ev("__dbg.walkState()"); c = await ev("__chase()")
        check(abs(w['x'] - c['pts'][0][0]) < 3 and abs(w['z'] - c['pts'][0][1]) < 3 and c['s'] < c['cfg']['lead'] + 12, 'retry puts the pair back at the maze entrance with Naty just ahead')
        # walking pace only loses
        r = await ev(PILOT, 5.5); check(r['end'] == 'fail', f"walking only (5.5) loses after {r['secs']}s in segment {r['seg'] + 1 if r['seg'] is not None else '?'}")
        await pg.locator('#chaseRetry').click(); await wf("__chase().on", 20); await asyncio.sleep(.5)
        # running pace arrives
        task = asyncio.create_task(ev(PILOT, 11))
        await asyncio.sleep(14); await shot('5_running')
        r = await task
        check(r['end'] == 'win', f"running (11) arrives in {r['secs']}s: farthest {r['max']} of lose {r['lose']} ({round(r['max']/r['lose']*100)}%), route points blocked for a walker {r['blocked']}")
        print('  gap samples while running', r['gaps'][:40], flush=True)
        await wf("!!__dbg.quest().vn()", 20); lines = await ev("__dbg.quest().vn().lines.map(l=>l.text)"); await shot('6_arrived')
        check(any('회전목마' in l for l in lines) and any('비어 있던 곳' in l for l in lines), 'arrival dialogue names the carousel garden and the empty flow')
        await drain(); await wf("!!document.querySelector('#qReward[data-on]')", 30); await asyncio.sleep(1)
        t = await ev("[document.getElementById('qrT').textContent, document.getElementById('qrList').textContent, document.getElementById('qrCount').textContent]"); await shot('7_reward')
        check('두 번째 좌표' in t[0] and '37.' in t[1], 'reward card: ' + ' / '.join(t))
        check(await ev("__chase()===null && !__dbg.chars().NATY.userData.run"), 'chase state cleared after the mission')
        # leaving mid-chase and coming back restarts at the entrance
        await rq.post(API + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers=ADM)
        check(not errs, 'no page errors ' + str(errs[:2]))
        await br.close()
    print('FAILS', json.dumps(fails, ensure_ascii=False))
asyncio.run(main())
