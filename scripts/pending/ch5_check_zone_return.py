# 섬 구역 복귀 연출 점검 (2026-11-03): 기구 5개 각각 __dbg.sweep → 단계(ready·draw·hush·bulbs·run·wake) 시작/끝이 한 번씩, 순서 동일,
# 느린 프레임(0.3 s, 그리고 1 s 끊김 섞기)에서도 같은 순서·건너뛰기 없음, 끝나면 기구 on·속도 1·간판 전부 켜짐, 페이지 오류 0.
# 사설 서버 8096(VOID_STATIC=0) + 정적 8097(저장소 루트) 필요. 사용: python ch5_check_zone_return.py [--lag] [--shots]
import asyncio, base64, json, os, re, sys
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; TEAM = 11
HERE = os.path.dirname(os.path.abspath(__file__)); SHOT = os.path.join(HERE, 'shots_zone_return'); os.makedirs(SHOT, exist_ok=True)
LAG = '--lag' in sys.argv; SHOTS = '--shots' in sys.argv
RIDES = ['dl-carousel', 'dl-ferris', 'dl-coaster', 'dl-safari', 'dl-harmonia']
for x in sys.argv:
    if x.startswith('--only='): RIDES = x[7:].split(',')
ORDER = ['ready', 'draw', 'hush', 'bulbs', 'run', 'wake']
fails = []
def check(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1280, 'height':800})
        async def route(r):
            req = r.request; url = req.url.replace(STATIC, API)
            try:
                resp = await ctx.request.fetch(url, method=req.method, headers={k:v for k, v in req.headers.items() if k.lower() not in ('host', 'origin', 'referer')}, data=req.post_data_buffer)
                await r.fulfill(status=resp.status, headers={'content-type':resp.headers.get('content-type', 'application/json')}, body=await resp.body())
            except Exception as e: await r.fulfill(status=500, body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team':TEAM, 'confirm':'AGAIN'}), headers={'content-type':'application/json', 'X-Admin-Key':'0101'})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); ev = pg.evaluate
        cerr = []; pg.on('console', lambda m: cerr.append(m.text) if m.type == 'error' else None)
        cdp = await ctx.new_cdp_session(pg)
        async def shot(n):
            if not SHOTS: return
            r = await cdp.send('Page.captureScreenshot', {'format':'png'}); open(os.path.join(SHOT, n + '.png'), 'wb').write(base64.b64decode(r['data']))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={TEAM}', wait_until='domcontentloaded')
        for i in range(120):
            if await ev("typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            await asyncio.sleep(0.5)
        await asyncio.sleep(4); await ev("__dbg.tutEnd()"); await asyncio.sleep(2)
        await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
        st = await ev("__dbg.rideState()"); print('start', json.dumps(st, ensure_ascii=False))
        check(all(not v['on'] and v['s'] == 0 for v in st.values()), 'fresh team: every ride off and still')
        check(all((v['bulbs'] or 0) > 0 for v in st.values()), 'every ride has bulb materials ' + str({k:v['bulbs'] for k, v in st.items()}))
        check(sum(v['signs'] for v in st.values()) >= 4, 'name signs registered ' + str({k:v['signs'] for k, v in st.items()}))
        tau0 = {k:v['tau'] for k, v in st.items()}; await asyncio.sleep(2); st2 = await ev("__dbg.rideState()")
        check(all(st2[k]['tau'] == tau0[k] for k in tau0), 'an off ride does not move (tau frozen)')
        if LAG:   # every frame 300 ms, every 7th frame 1 s
            await ev("(()=>{ let n = 0; __dbg.islAnim.push(()=>{ const ms = (++n % 7 === 0) ? 1000 : 300, e = performance.now() + ms; while(performance.now() < e); }); })()")
        orders = {}
        for rid in RIDES:
            await ev("__dbg.fxClear()")
            ok = await ev(f"__dbg.sweep('{rid}')"); check(ok, f'{rid}: chain started')
            seen = set(); limit = 600 if LAG else 240; midshot = False
            for i in range(limit):
                await asyncio.sleep(1)
                lg = await ev("__dbg.fxlog()")
                steps = [(x['n'], x['ev']) for x in lg if x['c'].endswith(rid)]
                for n in ORDER:
                    if (n, 'start') in steps and n not in seen:
                        seen.add(n)
                        if n in ('bulbs', 'run', 'wake'): await shot(f'{rid}_{n}{"_lag" if LAG else ""}')
                if not midshot and any(x['n'] == 'wake-fx' and x['c'].endswith(rid) for x in lg) and await ev(f"__dbg.rideState()['{rid}'].tau") > 3.2: midshot = True; await shot(f'{rid}_wakemid{"_lag" if LAG else ""}')
                if ('wake', 'end') in steps: break
            lg = await ev("__dbg.fxlog()"); seq = [(x['n'], x['ev']) for x in lg if x['c'].endswith(rid) and x['n'] in ORDER + ['wait']]
            orders[rid] = [n for n, e in seq if e == 'start' and n != 'wait']
            exp = []
            for n in ORDER: exp += [(n, 'start'), (n, 'end')]
            got = [x for x in seq if x[0] != 'wait']
            check(got == exp, f'{rid}: every stage starts and ends once, in order ({[n + ":" + e for n, e in got]})')
            check(not any(x['ev'] == 'cut' for x in lg), f'{rid}: nothing cut')
            await asyncio.sleep(1.5); s3 = (await ev("__dbg.rideState()"))[rid]
            check(s3['on'] and s3['s'] == 1 and s3['pow'] == 1 and s3['chain'] is None, f'{rid}: on, full speed, chain finished ({s3})')
            ta = s3['tau']; await asyncio.sleep(1.5); tb = (await ev("__dbg.rideState()"))[rid]['tau']
            check(tb > ta, f'{rid}: moving after power-up (tau {ta} → {tb})')
            if SHOTS: await asyncio.sleep(1); await shot(f'{rid}_after{"_lag" if LAG else ""}')
        check(len(set(map(tuple, orders.values()))) == 1, 'same stage order for all five rides')
        print('page errors', errs); print('console errors', cerr[:8])
        check(not errs, 'no page errors')
        print('FAILS', fails); await b.close()
asyncio.run(main())
