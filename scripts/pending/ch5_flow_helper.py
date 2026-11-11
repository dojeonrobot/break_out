import asyncio, json, re, os
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; API='http://127.0.0.1:8096'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'shots')
class H:
    def __init__(s,team=11,w=1366,h=768,touch=False,reset=True,gpu=False,dpr=1,init='',page='index.html'):
        s.team,s.w,s.h,s.touch,s.reset,s.gpu,s.dpr,s.init=team,w,h,touch,reset,gpu,dpr,init; s.page=page; s.errs=[]; s.bad=[]
    async def __aenter__(s):
        s.p=await async_playwright().start()
        s.b=await s.p.chromium.launch(args=['--use-gl=angle','--use-angle=d3d11','--ignore-gpu-blocklist'])
        s.ctx=await s.b.new_context(viewport={'width':s.w,'height':s.h},has_touch=s.touch,device_scale_factor=s.dpr)
        ctx=s.ctx
        async def route(r):
            q=r.request
            try:
                res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k.lower() not in ('host','origin','referer')})
                await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
            except Exception as e: await r.fulfill(status=500,body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'),route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');"+s.init)
        if s.reset: await ctx.request.post(API+'/api/void/team_reset',data=json.dumps({'team':s.team,'confirm':'AGAIN'}),headers={'content-type':'application/json','X-Admin-Key':'0101'})
        s.pg=await ctx.new_page(); pg=s.pg; pg.set_default_timeout(150000)
        pg.on('pageerror',lambda e:s.errs.append('pageerror: '+str(e)[:300]))
        pg.on('console',lambda m:s.errs.append('console.'+m.type+': '+m.text[:200]) if m.type=='error' and '404' not in m.text else None)
        pg.on('response',lambda r:s.bad.append(str(r.status)+' '+r.url[-70:]) if r.status>=400 else None)
        await s.load(); return s
    async def load(s,q=''):
        pg=s.pg
        await pg.goto(STATIC+'/chapter05/'+s.page+f'?team={s.team}{q}',wait_until='domcontentloaded',timeout=120000)
        for i in range(200):
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd"): break
            await asyncio.sleep(.5)
        for i in range(60):
            if not await pg.evaluate("document.body.classList.contains('intro')"): break
            await asyncio.sleep(.5)
        await asyncio.sleep(1.5)
    async def ev(s,js,arg=None): return await s.pg.evaluate(js,arg)
    async def shot(s,name,clip=None): await s.pg.screenshot(path=os.path.join(OUT,name+'.png'),clip=clip)
    async def __aexit__(s,*a):
        await s.b.close(); await s.p.stop()
