# team 2 has record 1 done; a team 3 tablet logs in as admin (view = all), closes the admin window -> team 3 must NOT get record 1 / act 1
import asyncio, json, re, sys, time
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; API='http://127.0.0.1:8096'; FILE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1280,'height':800})
        async def route(r):
            req=r.request; url=req.url.replace(STATIC,API)
            try:
                resp=await ctx.request.fetch(url, method=req.method, headers={k:v for k,v in req.headers.items() if k.lower() not in ('host','origin','referer')}, data=req.post_data_buffer)
                await r.fulfill(status=resp.status, headers={'content-type':resp.headers.get('content-type','application/json')}, body=await resp.body())
            except Exception as e: await r.fulfill(status=500, body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        H={'content-type':'application/json','X-Admin-Key':'0101'}
        for t in (2, 3): await ctx.request.post(API+'/api/void/team_reset', data=json.dumps({'team':t,'confirm':'AGAIN'}), headers=H)
        await ctx.request.post(API+'/api/void/admin/skip', data=json.dumps({'team':2,'mission':'z1'}), headers=H)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); ev=pg.evaluate
        pg.on('dialog', lambda d: asyncio.ensure_future(d.accept('0101')))
        await pg.goto(f'{STATIC}/chapter05/{FILE}?team=3', wait_until='domcontentloaded')
        for i in range(80):
            if await ev("typeof window.__dbg !== 'undefined'"): break
            await asyncio.sleep(0.5)
        await asyncio.sleep(4); await ev("__dbg.tutEnd()"); await asyncio.sleep(2)
        ST = "({rec:!!document.getElementById('recDone').dataset.on, busy:__dbg.simState().busy, voidOn:!!document.getElementById('voidVn').dataset.on, cards:document.getElementById('cV').textContent + '/' + document.getElementById('cR').textContent})"
        print('before admin', await ev(ST))
        await ev("document.getElementById('adminBtn').click()"); await asyncio.sleep(3)
        print('admin open', await ev(ST))
        await ev("document.querySelector('[data-aact=\"close\"], #adminDlg .x, #adminDlg [data-aact=logout]') && 0"); 
        await ev("(()=>{ document.getElementById('adminDlg').hidden = true; document.body.classList.remove('admin'); })()")   # close the window (what the close button does)
        await asyncio.sleep(5); s = await ev(ST); print('admin closed', s)
        r = await ctx.request.get(API+'/api/void/state'); j = await r.json(); q3 = j['quests'].get('3'); subs3 = [x for x in j['subs'] if x['team'] == 3]
        print('server team 3 quests', q3, 'subs', len(subs3))
        leak = s['rec'] or s['busy'] or (q3 and any((isinstance(v, dict) and v.get('act')) for v in q3.values()))
        print('LEAK' if leak else 'NO LEAK', 'errs', errs); await b.close()
asyncio.run(main())
