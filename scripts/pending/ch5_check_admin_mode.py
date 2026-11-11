# admin-mode matrix on team 3 tablet "a" (nothing done), while team 3 tablet "b" finished record 1 + mission 1, and team 2 finished records 1-2.
# For each admin step: no completion card / act on tablet a, tablet a's server entry gains no act/quest, record 2 coordinates stay locked on a.
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; API='http://127.0.0.1:8096'; FILE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
fails = []
def check(c, m): print(('OK   ' if c else 'FAIL ') + m); (None if c else fails.append(m))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1280,'height':800})
        async def route(r):
            req=r.request; url=req.url.replace(STATIC,API)
            try:
                resp=await ctx.request.fetch(url, method=req.method, headers={k:v for k,v in req.headers.items() if k.lower() not in ('host','origin','referer')}, data=req.post_data_buffer)
                await r.fulfill(status=resp.status, headers={'content-type':resp.headers.get('content-type','application/json')}, body=await resp.body())
            except Exception as e: await r.fulfill(status=500, body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        H={'content-type':'application/json','X-Admin-Key':'0101'}; J={'content-type':'application/json'}
        for t in (2, 3): await ctx.request.post(API+'/api/void/team_reset', data=json.dumps({'team':t,'confirm':'AGAIN'}), headers=H)
        await ctx.request.post(API+'/api/void/admin/skip', data=json.dumps({'team':2,'mission':'z1'}), headers=H)
        await ctx.request.post(API+'/api/void/admin/skip', data=json.dumps({'team':2,'mission':'z2'}), headers=H)
        # team 3 tablet b: registered, finished mission 1 (its record 1 counts for the team, as tablets share scans)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); ev=pg.evaluate
        pg.on('dialog', lambda d: asyncio.ensure_future(d.accept('0101')))
        await pg.goto(f'{STATIC}/chapter05/{FILE}?team=3', wait_until='domcontentloaded')
        for i in range(80):
            if await ev("typeof window.__dbg !== 'undefined'"): break
            await asyncio.sleep(0.5)
        await asyncio.sleep(4); await ev("__dbg.tutEnd()"); await asyncio.sleep(2.5)
        # tablet b joins AFTER this tablet registered (a tablet joining later inherits the team's furthest progress by design, set_quests 2026-10-27)
        await ctx.request.post(API+'/api/void/quest', data=json.dumps({'team':3,'dev':'tabletb','done':['q1'],'act':1,'tut':True}), headers=J); await asyncio.sleep(9)
        ST = """(()=>{ const t = __dbg.tutState(); return {rec:!!document.getElementById('recDone').dataset.on, busy:__dbg.simState().busy, qd:__dbg.qdone(), z2locked:(t.locked.find(x=> x[0] === 'z2') || [])[1], skip:__dbg.skipWhat ? __dbg.skipWhat() : null}; })()"""
        async def server_a():
            j = await (await ctx.request.get(API+'/api/void/state')).json(); q = j['quests'].get('3', {})
            return {k:{kk:vv for kk, vv in v.items() if kk not in ('seen',)} for k, v in q.items()}
        base = await ev(ST); print('start', base); sa0 = await server_a(); print('server', sa0)
        mine0 = [k for k, v in sa0.items() if v.get('dev') != 'tabletb']
        async def step(name, js, wait=3):
            await ev(js); await asyncio.sleep(wait); s = await ev(ST); sa = await server_a()
            a = {k: v for k, v in sa.items() if v.get('dev') != 'tabletb'}
            check(not s['rec'] and not s['busy'], f'{name}: no completion card / act ({s})')
            check(s['z2locked'] is True, f'{name}: record 2 coordinates stay locked on this tablet')
            check(not any(v.get('act') or any(k.startswith('q') for k in v) for v in a.values()), f'{name}: this tablet gained no act/mission on the server ({a})')
            return s
        await step('관리자 로그인', "document.getElementById('adminBtn').click()", 4)
        await step('보기: 모든 조', "(()=>{ const sel = document.querySelector('[data-aview]'); if(sel){ sel.value = '0'; sel.dispatchEvent(new Event('change', {bubbles:true})); } })()")
        await step('보기: 2조', "(()=>{ const sel = document.querySelector('[data-aview]'); if(sel){ sel.value = '2'; sel.dispatchEvent(new Event('change', {bubbles:true})); } })()")
        s = await step('관리자 창 닫기', "(()=>{ document.getElementById('adminDlg').hidden = true; document.body.classList.remove('admin'); })()", 5)
        check(s['skip'] and '기록 1' in s['skip'], f'admin skip offers this team\'s record 1 ({s["skip"]})')
        await step('섬으로 이동', "__dbg.setWorld('island', true)", 3)
        await step('캠퍼스로', "__dbg.setWorld('erica', true)", 3)
        # notice reaches this tablet while logged in
        await ctx.request.post(API+'/api/void/admin/notice', data=json.dumps({'text':'관리자 모드 공지 점검'}), headers=H); await asyncio.sleep(16)
        txt = await ev("document.getElementById('voidTxt').textContent + ' | ' + (document.getElementById('noticeBar') ? document.getElementById('noticeBar').textContent : '')")
        check('공지 점검' in txt, f'notice reaches a team tablet logged in as admin ({txt[:60]})')
        await ctx.request.post(API+'/api/void/admin/notice', data=json.dumps({'text':''}), headers=H)
        await step('로그아웃', "(()=>{ const b = document.querySelector('[data-aact=\"logout\"]'); if(b) b.click(); })()", 4)
        # auto logout after 30 min: age the login and wait one tick
        await ev("document.getElementById('adminBtn').click()"); await asyncio.sleep(3); await ev("(()=>{ document.getElementById('adminDlg').hidden = true; document.body.classList.remove('admin'); sessionStorage.setItem('void-admin-at', String(Date.now() - 31*60*1000)); })()"); await asyncio.sleep(1.5)
        k = await ev("({key:!!sessionStorage.getItem('void-admin'), pill:!document.getElementById('admSkip').hidden})"); check(not k['key'] and not k['pill'], f'admin login ends by itself after 30 min on a team tablet ({k})')
        print('errs', errs); print('FAILS', fails); await b.close()
asyncio.run(main())
