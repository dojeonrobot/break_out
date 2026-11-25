"""2026-11-25 노션 「scan break」 체크 필요 1~6번(태블릿 겹침) 재현·측정.
사용: python -I ch5_check_tablet_1125.py <출력폴더> [프로필...]
서버: API 8096(VOID_STATIC=0, CH5_ADMIN_KEY=0101), 정적 8097(break_out 루트)
프로필: tabL 1280x690(갤럭시 탭 가로 크롬, 주소창 뺀 높이), tabP 800x1170(세로), phoneP 390x760, phoneL 844x340
"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
ONLY = sys.argv[2:]
STATIC, API = 'http://127.0.0.1:8097', 'http://127.0.0.1:8096'
ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
PROFILES = [('desk', 1920, 1000), ('tabL', 1280, 690), ('tabP', 800, 1170), ('phoneP', 390, 760), ('phoneL', 844, 340)]
T = 4
Z1 = (37.295655, 126.838475)
UA_TAB = 'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
UA_PHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'

OV = r'''(pairs) => { const R = s => { const e = document.querySelector(s); if(!e) return null; const st = getComputedStyle(e); if(st.display==='none'||st.visibility==='hidden') return null; const r = e.getBoundingClientRect(); return r.width>1&&r.height>1 ? r : null; };
  return pairs.map(([a, b]) => { const p = R(a), q = R(b); if(!p || !q) return [a, b, 'n/a']; const ix = Math.min(p.right, q.right) - Math.max(p.left, q.left), iy = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top); return [a, b, ix > 0 && iy > 0 ? `OVERLAP ${Math.round(ix)}x${Math.round(iy)}` : 'ok']; }); }'''

async def wait_dbg(pg):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): return
        except Exception: pass
        await asyncio.sleep(.25)

async def run(p, name, w, h):
    phone = min(w, h) <= 500
    br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
    res = {}
    async def mkctx(admin=False, geo=None):
        ctx = await br.new_context(viewport={'width': w, 'height': h}, screen={'width': w, 'height': h}, has_touch=True, is_mobile=phone,
                                   device_scale_factor=1, user_agent=UA_PHONE if phone else UA_TAB,
                                   geolocation=geo, permissions=['geolocation'] if geo else [])
        init = "localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','tab');localStorage.setItem('void-sound','0');"
        if admin: init += "sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));"
        await ctx.add_init_script(init)
        async def route(r):
            q = r.request
            rs = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer,
                                         headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=rs.status, body=await rs.body(), headers={'content-type': rs.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        return ctx
    post = lambda ctx, path, body, adm=False: ctx.request.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})

    # 1) 튜토리얼 대사 + 단계 카드: ‹ 이전 vs 카드
    ctx = await mkctx(geo={'latitude': Z1[0] + 0.0002, 'longitude': Z1[1] - 0.0013})
    await post(ctx, 'team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    await wait_dbg(pg); await asyncio.sleep(4)
    for i in range(80):
        has = await pg.evaluate("(()=>{const c=document.getElementById('voidCard');return !!c&&c.children.length>0&&!!document.getElementById('voidVn').dataset.on})()")
        if has: break
        await pg.keyboard.press('Space'); await asyncio.sleep(.7)
    await asyncio.sleep(2.5)
    await pg.evaluate("document.getElementById('tutPrev').hidden=false")
    res['1_prev_vs_card'] = await pg.evaluate(OV, [['#tutPrev', '#voidCard'], ['#voidNext', '#voidCard'], ['#tutDots', '#voidCard']])
    await pg.screenshot(path=str(OUT / f'{name}_1_tutcard.png'))
    # 2) 튜토리얼 끝 → 캠퍼스, 보이드 도움 버튼 vs 패널
    await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(4)
    res['2_help_vs_panel'] = await pg.evaluate(OV, [['#restoreBtn', '#panel'], ['#restoreBtn', '#bar'], ['#worlds', '#panel'], ['#worlds', '#board']])
    await pg.screenshot(path=str(OUT / f'{name}_2_campus.png'))
    # 3·4) 내 위치(GPS) + 8조 위치 겹침, 좌표 카드 vs 하단 막대·패널
    await post(ctx, 'pos', {'team': 8, 'lat': Z1[0] + 0.0002, 'lng': Z1[1] - 0.0013, 'acc': 12})
    try:
        await pg.click('#lMe', timeout=4000)
    except Exception as e:
        res['3_err'] = str(e)[:80]
    await asyncio.sleep(9)
    res['3_labels'] = await pg.evaluate(r'''()=>{ const ms=[...document.querySelectorAll('.mk.team')].filter(e=>getComputedStyle(e).display!=='none'); return ms.map(e=>{const r=e.getBoundingClientRect(); const top=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return [e.textContent, Math.round(r.left), Math.round(r.top), Math.round(r.width), top===e||e.contains(top) ? 'on top' : 'COVERED']}); }''')
    res['4_coord'] = await pg.evaluate(OV, [['#meCoord', '#bar'], ['#meCoord', '#panel'], ['#meCoord', '#restoreBtn'], ['#bar', '#restoreBtn']])
    await pg.screenshot(path=str(OUT / f'{name}_3_gps.png'))
    # 5) 섬 걷기: 달리기·점프 버튼
    await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(4)
    try:
        # 헤드리스 크롬은 pointer:fine이라 터치 버튼이 숨으므로 점검에서만 보이게 한다
        await pg.add_style_tag(content='#walkPad:not([hidden]){display:block!important}body #walkRun:not([hidden]),body #walkJump:not([hidden]){display:flex!important}')
        await pg.evaluate('__dbg.startWalk()'); await asyncio.sleep(4); await pg.evaluate("['walkRun','walkJump','walkPad'].forEach(i=>{const e=document.getElementById(i);if(e)e.hidden=false})"); await asyncio.sleep(.8)
        res['5_walk'] = await pg.evaluate(r'''()=>['walkRun','walkJump','walkPad'].map(id=>{const e=document.getElementById(id);if(!e||getComputedStyle(e).display==='none')return [id,'hidden'];const r=e.getBoundingClientRect();return [id,Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)]})''')
        await pg.screenshot(path=str(OUT / f'{name}_5_walk.png'))
        await pg.click('#walkRun', timeout=3000); await asyncio.sleep(.6)
        await pg.screenshot(path=str(OUT / f'{name}_5_walk_on.png'))
        await pg.evaluate('__dbg.stopWalk()')
    except Exception as e:
        res['5_err'] = str(e)[:120]
    res['errs'] = errs[:3]
    await ctx.close()
    # 6) 환원 시뮬레이터 + 관리자 건너뛰기 알약
    ctx = await mkctx(admin=True)
    pg = await ctx.new_page()
    await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
    await wait_dbg(pg); await asyncio.sleep(3)
    await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(2)
    await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(3)
    await pg.evaluate('__dbg.setSim(true)'); await asyncio.sleep(5)
    await pg.evaluate("(()=>{const a=document.getElementById('admSkip');a.hidden=false;document.getElementById('admSkipT').textContent='연출 건너뛰기';})()")
    await asyncio.sleep(.5)
    res['6_skip_vs_hud'] = await pg.evaluate(OV, [['#admSkip', '#simHud'], ['#admSkip', '#worlds'], ['#admSkip', '#sndBtn'], ['#admSkip', '#adminBtn']])
    await pg.screenshot(path=str(OUT / f'{name}_6_sim.png'))
    await ctx.close(); await br.close()
    return res

async def main():
    allres = {}
    async with async_playwright() as p:
        for name, w, h in PROFILES:
            if ONLY and name not in ONLY: continue
            r = await run(p, name, w, h); allres[name] = r
            print(name, json.dumps(r, ensure_ascii=False), flush=True)
    (OUT / 'result.json').write_text(json.dumps(allres, ensure_ascii=False, indent=1), encoding='utf-8')

asyncio.run(main())
