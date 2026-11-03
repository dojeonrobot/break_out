import asyncio,json,pathlib,re
from playwright.async_api import async_playwright
REPO=pathlib.Path('C:/Users/dlgus/break_out');STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
OUT=pathlib.Path(__file__).resolve().parents[1]/'gate-progression';OUT.mkdir(exist_ok=True)
async def main():
 source=(REPO/'chapter05/index.html').read_text(encoding='utf8')
 source=re.sub(r'const wait = ms => .*?;\nlet actBusy','const wait=ms=>new Promise(r=>setTimeout(r,Math.min(ms,60)));\nlet actBusy',source)
 async with async_playwright() as p:
  br=await p.chromium.launch(args=['--enable-gpu']);ctx=await br.new_context(viewport={'width':1280,'height':800},device_scale_factor=.75,reduced_motion='reduce')
  await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','firsttablet');localStorage.setItem('void-mini-12',JSON.stringify({q:'q1',step:'station',pos:[0,258,0]}));")
  async def post(path,data):return await ctx.request.post(API+'/api/void/'+path,data=data,headers={'X-Admin-Key':'0101'})
  await post('team_reset',{'team':12,'confirm':'AGAIN'});await post('admin/skip',{'team':12,'mission':'z1'})
  for dev in ['firsttablet','secondtablet']:await post('quest',{'team':12,'dev':dev,'done':[],'act':1,'tut':True,'story':2})
  async def route(r):
   q=r.request;res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']});await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
  await ctx.route(re.compile(r'.*/api/void/.*'),route);await ctx.route('**/chapter05/index.html*',lambda r:r.fulfill(body=source,content_type='text/html'))
  pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  await pg.goto(STATIC+'/chapter05/index.html?team=12',wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  async def drain(selector,n=500):
   for _ in range(n):
    if await pg.locator(selector).is_visible():return
    await pg.evaluate('()=>{for(let i=0;i<80&&__dbg.quest().vn();i++)__dbg.quest().next()}')
    if await pg.locator('#voidVn').is_visible():await pg.locator('#voidNext').click()
    await asyncio.sleep(.1)
   raise AssertionError('missing '+selector+' '+str(errors))
  await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('리코·제로')");await asyncio.sleep(.6)
  await pg.evaluate('__dbg.walkTo(...__dbg.station().spot)');await drain('#rideDlg')
  assert '6개' not in await pg.locator('#rideDlg').inner_text()
  await pg.locator('#rideGo').click();await pg.evaluate('()=>{for(let i=0;i<20&&__dbg.quest().vn();i++)__dbg.quest().next()}')
  await pg.wait_for_function('!!__dbg.ride()');assert await pg.evaluate('__dbg.ride().spots.length')==4
  await pg.evaluate('__dbg.ride().press=true;__dbg.ride().boost=14')
  for _ in range(160):
   if not await pg.evaluate('!!__dbg.ride()'):break
   await asyncio.sleep(.5)
  else:raise AssertionError('train never completed marked record')
  await drain('#qReward');assert await pg.locator('#qReward').get_attribute('data-route')=='1'
  assert await pg.evaluate('__dbg.simState().lit')==1
  assert await pg.locator('#qrList .z').count()==4
  print('OK four coordinate cards leave actual records at 1/5',flush=True)
  await pg.locator('#qrMap').click();await pg.evaluate('()=>{for(let i=0;i<20&&__dbg.quest().vn();i++)__dbg.quest().next()}')
  await pg.evaluate('__dbg.walkTo(...__dbg.forestSpot())');await pg.wait_for_selector('#miniBox',state='visible')
  assert await pg.locator('#miniGo').inner_text()=='기록 찍기'
  assert await pg.evaluate('__dbg.simState().lit')==1
  await pg.locator('#miniGo').click();await drain('#qReward');assert '기다리는 중' not in await pg.locator('#qrS').inner_text()
  assert not await pg.locator('#qrMap').is_disabled();assert await pg.locator('#qrList').is_visible()
  assert await pg.evaluate('__dbg.simState().lit')==2;assert await pg.locator('#qrCount').inner_text()=='채운 기록 2 / 5'
  print('OK on-site forest capture completes at 2/5 and opens the next activity without waiting for the other tablet (independent tablets, 2026-10-30)',flush=True)
  # Completed teams preserve actual-restoration state when a replacement tablet joins.
  await post('quest',{'team':12,'dev':'firsttablet','done':['q1','q2','q4','q3'],'act':3,'story':3,'restored':True})
  state=await (await post('quest',{'team':12,'dev':'replacement'})).json()
  entry=next(v for v in state['quests']['12'].values() if v.get('dev')=='replacement')
  assert entry.get('records',{}).get('q1');assert entry.get('story')==3 and entry.get('restored') and all(k in entry for k in ['q1','q2','q4','q3'])
  print('OK replacement tablet inherits story revision and actual-restoration status',flush=True)
  # Exercise final modal layouts at desktop and tablet sizes without altering mission progress.
  await pg.evaluate("delete document.getElementById('qReward').dataset.on;__dbg.stopWalk();__dbg.dlg.lab(true)")
  for name,w,h in [('pc',1280,800),('tablet',800,600),('portrait',800,1280),('short',844,390)]:
   await pg.set_viewport_size({'width':w,'height':h});await asyncio.sleep(.15)
   result=await pg.evaluate("()=>{const a=[...document.querySelectorAll('#lbMons section')].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,r:r.right,y:r.y,b:r.bottom}});return {a,overflow:document.documentElement.scrollWidth>innerWidth}}")
   assert not result['overflow'] and all(x['x']>=0 and x['r']<=w for x in result['a']),result
   await pg.locator('#lbGo').scroll_into_view_if_needed();assert await pg.locator('#lbGo').is_visible()
   await pg.screenshot(path=str(OUT/(name+'-analysis.png')))
  print('OK analysis panel and continue action fit PC, tablet portrait/landscape and short viewports',flush=True)
  assert not errors,errors;await br.close();print('OK no runtime errors',flush=True)
asyncio.run(main())
