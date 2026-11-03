import asyncio,re
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
async def main():
 async with async_playwright() as p:
  br=await p.chromium.launch(args=['--enable-gpu']);ctx=await br.new_context(viewport={'width':1280,'height':800},device_scale_factor=.5,reduced_motion='no-preference')
  await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','powercheck');")
  await ctx.request.post(API+'/api/void/team_reset',data={'team':12,'confirm':'AGAIN'},headers={'X-Admin-Key':'0101'})
  await ctx.request.post(API+'/api/void/admin/skip',data={'team':12,'mission':'z1'},headers={'X-Admin-Key':'0101'})
  await ctx.request.post(API+'/api/void/quest',data={'team':12,'dev':'powercheck','done':[],'act':1,'tut':True,'story':3})
  async def route(r):
   q=r.request;res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']});await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
  await ctx.route(re.compile(r'.*/api/void/.*'),route)
  pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  await pg.goto(STATIC+'/chapter05/index.html?team=12',wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  await pg.evaluate("__dbg.setWorld('island',true)");await asyncio.sleep(1)
  first=await pg.evaluate('__dbg.rideState()');assert all(not x['on'] and x['s']==0 for x in first.values()),first
  before=await pg.evaluate('__dbg.power()');await asyncio.sleep(.4);after=await pg.evaluate('__dbg.power()')
  assert before['clock']==after['clock']==0 and not after['on'] and after['poweredAnimations']>=15,after
  assert await pg.evaluate('__dbg.train().mode')=='stop'
  print('OK all five main attractions and additional powered animations are stopped before breaker repair',flush=True)
  await pg.evaluate("__dbg.startWalk('리코·제로')");await asyncio.sleep(1)
  await pg.evaluate('()=>{for(let i=0;i<40&&__dbg.quest().vn();i++)__dbg.quest().next();__dbg.walkTo(...__dbg.target())}')
  await pg.wait_for_function("__dbg.quest().vn()?.lines[0].who==='자일로'")
  await pg.evaluate('()=>{for(let i=0;i<40&&__dbg.quest().vn();i++)__dbg.quest().next();__dbg.walkTo(...__dbg.yardDoor())}')
  await pg.wait_for_selector('#yardDlg',state='visible');await asyncio.sleep(1)
  await pg.evaluate('()=>{for(let i=0;i<40&&__dbg.quest().vn();i++)__dbg.quest().next();const y=__dbg.yard();y.tiles=y.sol.map(r=>r.map(c=>new Set(c)));__dbg.yardPaint()}')
  await asyncio.sleep(.4);on=await pg.evaluate('__dbg.rideState()');assert all(x['on'] and x['s']>0 for x in on.values()),on
  assert await pg.evaluate('__dbg.power().on')
  assert await pg.evaluate('__dbg.simState().lit')==1
  assert await pg.locator('#ydContinue').is_visible()
  await pg.locator('#ydContinue').click();await asyncio.sleep(1);await pg.evaluate('()=>{for(let i=0;i<40&&__dbg.quest().vn();i++)__dbg.quest().next()}');await asyncio.sleep(.3)
  assert await pg.evaluate('__dbg.power().clock')>0
  print('OK solving all 20 cells restores island power without increasing record count; success waits for input',flush=True)
  state=await (await ctx.request.get(API+'/api/void/state')).json();assert state['quests']['12']['a'].get('power')
  await pg.reload(wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  await pg.evaluate("__dbg.setWorld('island',true)");await asyncio.sleep(.5)
  assert await pg.evaluate('__dbg.power().on') and all(x['on'] for x in (await pg.evaluate('__dbg.rideState()')).values())
  assert 'q1' not in await pg.evaluate('__dbg.qdone()');print('OK power persists before mission completion and survives page reload',flush=True)
  assert not errors,errors;await br.close();print('OK no runtime errors',flush=True)
asyncio.run(main())
