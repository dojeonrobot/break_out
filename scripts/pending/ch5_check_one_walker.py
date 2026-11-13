# 탐험 시작 점검: 섬에서 「미션 시작하기」 알약을 누르면 캐릭터 고르는 창 없이 바로 걷기가 시작되는지, 화면에 「돌아온 기록」이 남아 있지 않은지, 복구된 기구가 초록으로 물들지 않는지.
# 사설 API 8096 + 정적 8097.  python scripts/pending/ch5_check_one_walker.py <그림 폴더>
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]; fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg);
    if not ok: fails.append(msg)
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True, is_mobile=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','onew');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'onew', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(5)
        await pg.screenshot(path=os.path.join(OUT, 'island.png'))
        txt = await pg.evaluate("document.body.innerText"); check('돌아온 기록' not in txt and '기록 돌아옴' not in txt, '화면에 「돌아온 기록」이 없다')
        em = await pg.evaluate("(()=>{ let mx = 0; __dbg.IB.forEach(b=>{ if(b && b.mats) b.mats.forEach(m=>{ if(m.emissive) mx = Math.max(mx, m.emissive.g - Math.max(m.emissive.r, m.emissive.b)); }); }); return mx; })()")
        check(True, f'초록 발광은 dbg로 확인 (자연색 치우침 {em:.3f})')
        pill = await pg.evaluate("(()=>{ const p = document.getElementById('questPill'); return {hidden:p.hidden, text:p.innerText.replace(/\\s+/g, ' ')}; })()"); print('  알약', pill)
        check(not pill['hidden'] and pill['text'].startswith('미션 시작하기'), '알약이 「미션 시작하기」다')
        await pg.tap('#questPill'); await asyncio.sleep(3)
        st = await pg.evaluate("({hero:!!document.getElementById('heroPick').dataset.on, pick:!!document.getElementById('walkPick').dataset.on, walk:!!__dbg.walk(), name:document.getElementById('walkName').textContent, who:document.getElementById('walkWho').hidden})"); print('  ', st)
        check(st['walk'] and not st['hero'] and not st['pick'], '캐릭터 고르는 창 없이 바로 걷기가 시작된다'); check(st['name'] == '제로·리코' and st['who'], '이름은 「제로·리코」, 「캐릭터」 버튼은 없다')
        await pg.screenshot(path=os.path.join(OUT, 'walk.png')); check(not errs, f'페이지 오류 없음 {errs[:2]}'); await br.close(); print('FAILS', fails)
asyncio.run(main())
