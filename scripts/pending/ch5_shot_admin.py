# 관리자 대시보드 스크린샷(현재/수정 후 비교). 사설 API 8096 + 정적 8097. 6개 조 시드.
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; API='http://127.0.0.1:8096'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'adm_before'
SEED = '--seed' in sys.argv
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1366,'height':800})
        async def route(r):
            req=r.request; url=req.url.replace(STATIC,API)
            try:
                resp=await ctx.request.fetch(url,method=req.method,headers={k:v for k,v in req.headers.items() if k.lower() not in ('host','origin','referer')},data=req.post_data_buffer)
                await r.fulfill(status=resp.status,headers={'content-type':resp.headers.get('content-type','application/json')},body=await resp.body())
            except Exception as e: await r.fulfill(status=500,body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'),route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        H={'content-type':'application/json','X-Admin-Key':'0101'}; J={'content-type':'application/json'}
        if SEED:
            for t in range(1,7):
                for dev in ('a','b'):
                    done = ['q1','q2','q3'][: (t % 4)]
                    await ctx.request.post(API+'/api/void/quest',data=json.dumps({'team':t,'dev':f'tab{dev}{t}','done':done,'act':min(3,len(done)+1) if t%2 else len(done),'tut':True}),headers=J)
                for i, m in enumerate(['z1','z2','z3'][: (t % 3) + 1]):
                    sid = f'{t}{i}abcdefghijklm'[:16].ljust(16,'x')
                    r = await ctx.request.post(API+'/api/void/submit',data=json.dumps({'team':t,'scanId':sid,'mission':m,'note':'테스트'}),headers=J)
                    if r.status != 200: print('submit', t, m, r.status, await r.text())
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        pg.on('dialog',lambda d: asyncio.ensure_future(d.accept('0101')))
        await pg.goto(f'{STATIC}/chapter05/index.html',wait_until='domcontentloaded',timeout=120000)
        for i in range(120):
            if await pg.evaluate("typeof window.__dbg !== 'undefined'"): break
            await asyncio.sleep(0.5)
        await asyncio.sleep(3)
        await pg.evaluate("document.getElementById('adminBtn').click()"); await asyncio.sleep(4)
        if await pg.evaluate("document.getElementById('adminDlg').hidden"):
            await pg.evaluate("document.getElementById('adminBtn').click()"); await asyncio.sleep(3)
        h = await pg.evaluate("document.getElementById('adminBody').scrollHeight")
        print('adminBody scrollHeight', h, 'errors', errs[:3])
        async def shot(name): await pg.screenshot(path=name, timeout=120000)
        await shot(f'{OUT}.png')
        # tall view: scroll the dashboard body in viewport-sized steps and stitch
        from PIL import Image
        parts=[]; top=await pg.evaluate("document.getElementById('adminBody').getBoundingClientRect().top")
        step = 800 - int(top); y = 0; i = 0
        while True:
            await pg.evaluate(f"document.getElementById('adminBody').scrollTop={y}"); await asyncio.sleep(0.6)
            real = await pg.evaluate("document.getElementById('adminBody').scrollTop")
            nm = f'{OUT}_p{i}.png'; await shot(nm); parts.append((real, nm)); i += 1
            if real + step >= h or real < y: break
            y += step
        im = Image.new('RGB', (1366, int(top) + h + 10), 'white'); 
        for real, nm in parts:
            pic = Image.open(nm); im.paste(pic.crop((0, int(top), 1366, 800)), (0, int(top) + real))
        im.paste(Image.open(parts[0][1]).crop((0,0,1366,int(top))), (0,0)); im.save(f'{OUT}_full.png')
        await pg.set_viewport_size({'width':820,'height':1100}); await asyncio.sleep(1.5)
        h2 = await pg.evaluate("document.getElementById('adminBody').scrollHeight"); print('tablet 820 scrollHeight', h2)
        await pg.evaluate("document.getElementById('adminBody').scrollTop=0"); await shot(f'{OUT}_tablet.png')
        await b.close()
asyncio.run(main())
