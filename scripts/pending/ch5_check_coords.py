# 2026-11-09 관리자 「기록 좌표」 점검. 사설 API 8096(VOID_STATIC=0, CH5_ADMIN_KEY=0101, 데이터는 스크래치) + 정적 8097(저장소 루트).
# 관리자 기기: 카드 기본값 = 페이지 값, 한 칸에 "위도, 경도" 붙여넣기 → 두 칸, 저장 → 서버 coords, 조 태블릿 카드 좌표가 바뀜, 기본값으로 → 원래대로.
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'
fails = []
def check(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
DEF = {'z1': (37.295655, 126.838475), 'z2': (37.295565, 126.840878), 'z3': (37.293614, 126.831854)}
NEW = (37.296123, 126.839001)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800})
        async def route(r):
            req = r.request; url = req.url.replace(STATIC, API)
            try:
                resp = await ctx.request.fetch(url, method=req.method, headers={k: v for k, v in req.headers.items() if k.lower() not in ('host', 'origin', 'referer')}, data=req.post_data_buffer)
                await r.fulfill(status=resp.status, headers={'content-type': resp.headers.get('content-type', 'application/json')}, body=await resp.body())
            except Exception as e: await r.fulfill(status=500, body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        H = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
        await ctx.request.post(API + '/api/void/admin/coords', data=json.dumps({'mission': 'z1', 'clear': True}), headers=H)
        await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team': 4, 'confirm': 'AGAIN'}), headers=H)

        async def open_page(q):
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('dialog', lambda d: asyncio.ensure_future(d.accept('0101')))
            await pg.goto(f'{STATIC}/chapter05/index.html{q}', wait_until='domcontentloaded', timeout=120000)
            for i in range(120):
                if await pg.evaluate("typeof window.__dbg !== 'undefined'"): break
                await asyncio.sleep(0.5)
            return pg, errs

        # team tablet (team 4) past the tutorial: record 1 card with its coordinates
        kid, kerr = await open_page('?team=4')
        await asyncio.sleep(4); await kid.evaluate("__dbg.tutEnd()"); await asyncio.sleep(3)
        body = await kid.evaluate("document.body.innerText")
        check(f'{DEF["z1"][0]:.6f}, {DEF["z1"][1]:.6f}' in body, 'tablet shows the default record 1 coordinates')

        # admin device
        adm, aerr = await open_page('')
        await asyncio.sleep(4)
        await adm.evaluate("document.getElementById('adminBtn').click()"); await asyncio.sleep(4)
        if await adm.evaluate("document.getElementById('adminDlg').hidden"):
            await adm.evaluate("document.getElementById('adminBtn').click()"); await asyncio.sleep(3)
        vals = await adm.evaluate("Object.fromEntries([...document.querySelectorAll('input[data-keep^=\"cl\"]')].map(i=> [i.dataset.keep, i.value]))")
        print('inputs', vals)
        # 2026-11-10: 기록 좌표 칸이 접이식(details)이라 먼저 펼친다
        await adm.evaluate("(()=>{ const d=document.querySelector('details[data-ad=\"coords\"]'); if(d && !d.open) d.querySelector('summary').click(); })()"); await asyncio.sleep(0.5)
        for k, (la, ln) in DEF.items():
            check(vals.get('clat-' + k) == f'{la:.6f}' and vals.get('clng-' + k) == f'{ln:.6f}', f'{k} inputs hold the default {la}, {ln}')
        # paste "lat, lng" into the latitude box
        lat = adm.locator('input[data-keep="clat-z1"]')
        await lat.fill(f'{NEW[0]}, {NEW[1]}'); await asyncio.sleep(0.3)
        v = await adm.evaluate("[document.querySelector('[data-keep=\"clat-z1\"]').value, document.querySelector('[data-keep=\"clng-z1\"]').value]")
        check(v == [str(NEW[0]), str(NEW[1])], f'pasting "lat, lng" fills both boxes ({v})')
        # a state poll re-render must keep the typed value
        await ctx.request.post(API + '/api/void/admin/auto', data=json.dumps({'auto': True}), headers=H); await asyncio.sleep(17)   # bumps the version → dashboard re-renders
        v2 = await adm.evaluate("document.querySelector('[data-keep=\"clat-z1\"]').value")
        check(v2 == str(NEW[0]), f'typed value survives a re-render ({v2})')
        await adm.locator('[data-csave="z1"]').click(); await asyncio.sleep(2)
        st = await (await ctx.request.get(API + '/api/void/state')).json()
        c = st.get('coords', {}).get('z1')
        check(c and abs(c['lat'] - NEW[0]) < 1e-7 and abs(c['lng'] - NEW[1]) < 1e-7, f'server keeps z1 = {c}')
        check(await adm.locator('[data-cdef="z1"]').count() == 1, 'changed record shows 「기본값으로」')
        await adm.screenshot(path=sys.argv[1] if len(sys.argv) > 1 else 'coords_admin.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 800}, timeout=60000)

        await asyncio.sleep(17)   # tablet poll
        body = await kid.evaluate("document.body.innerText")
        check(f'{NEW[0]:.6f}, {NEW[1]:.6f}' in body, 'tablet card now shows the new coordinates')
        check(f'{DEF["z1"][0]:.6f}, {DEF["z1"][1]:.6f}' not in body, 'old coordinates gone from the tablet')
        ls = await kid.evaluate("localStorage.getItem('void-coords')")
        check(ls and 'z1' in ls, f'tablet remembers it ({ls})')

        # bad input
        await adm.locator('input[data-keep="clat-z2"]').fill('abc'); await adm.locator('[data-csave="z2"]').click(); await asyncio.sleep(1.5)
        st = await (await ctx.request.get(API + '/api/void/state')).json()
        check('z2' not in st.get('coords', {}), 'non-number latitude is not saved')

        await adm.locator('[data-cdef="z1"]').click(); await asyncio.sleep(2)
        st = await (await ctx.request.get(API + '/api/void/state')).json()
        check('z1' not in st.get('coords', {}), 'default restored on the server')
        v3 = await adm.evaluate("document.querySelector('[data-keep=\"clat-z1\"]').value")
        check(v3 == f'{DEF["z1"][0]:.6f}', f'admin box back to default ({v3})')
        await asyncio.sleep(17)
        body = await kid.evaluate("document.body.innerText")
        check(f'{DEF["z1"][0]:.6f}, {DEF["z1"][1]:.6f}' in body, 'tablet back to the default coordinates')
        check(not kerr and not aerr, f'no page errors ({kerr[:2]} {aerr[:2]})')
        await b.close()
    print('FAILS', len(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
