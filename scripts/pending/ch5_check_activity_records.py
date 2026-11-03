import asyncio,json,re
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=['--enable-gpu']);ctx=await browser.new_context(viewport={'width':1280,'height':800},reduced_motion='reduce')
  await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','recordcheck');")
  async def post(path,data):return await ctx.request.post(API+'/api/void/'+path,data=data,headers={'X-Admin-Key':'0101'})
  await post('team_reset',{'team':12,'confirm':'AGAIN'});await post('admin/skip',{'team':12,'mission':'z1'})
  await post('quest',{'team':12,'dev':'recordcheck','tut':True,'act':1})
  mode='pending'
  async def route(r):
   q=r.request;res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer)
   st=await res.json()
   if mode!='ok':
    for sub in st.get('subs',[]):
     if sub.get('team')==12:
      sub['status']='pending';sub['splat']=None
      if mode=='error':sub['error']='스캔을 찾을 수 없습니다'
   await r.fulfill(status=res.status,body=json.dumps(st),content_type='application/json')
  await ctx.route(re.compile(r'.*/api/void/.*'),route)
  pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  for current in ['pending','error','ok']:
   mode=current
   await pg.goto(STATIC+'/chapter05/index.html?team=12',wait_until='load');await pg.wait_for_function('!!window.__activity',timeout=60000)
   assert await pg.evaluate('__activity().count')==(1 if current=='ok' else 0),current
   if current!='ok':assert not await pg.evaluate("__dbg.quest().open().includes('리코·제로')")
   print('OK campus '+current+' record count and mission lock',flush=True)
  # Posting the same record twice is idempotent; other activity ids cannot become records.
  st=await (await post('quest',{'team':12,'dev':'recordcheck','records':['q1','q4','q3','arbitrary']})).json()
  entry=next(v for v in st['quests']['12'].values() if v['dev']=='recordcheck');stamp=entry['records']['q1']
  assert set(entry['records'])=={'q1'}
  st=await (await post('quest',{'team':12,'dev':'recordcheck','records':['q1']})).json()
  entry=next(v for v in st['quests']['12'].values() if v['dev']=='recordcheck');assert entry['records']['q1']==stamp
  await pg.reload(wait_until='load');await pg.wait_for_function('!!window.__activity',timeout=60000)
  assert await pg.evaluate('__activity().count')==2
  assert 'q1' not in await pg.evaluate('__dbg.qdone()')
  await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('리코·제로')")
  await pg.wait_for_function("__dbg.quest().vn()?.lines[0].text.includes('서쪽 숲')")
  print('OK capture persists before mission acknowledgement and cannot double count',flush=True)
  st=await (await post('quest',{'team':12,'dev':'replacement'})).json()
  replacement=next(v for v in st['quests']['12'].values() if v['dev']=='replacement');assert replacement['records']['q1']==stamp
  st=await (await post('admin/quest',{'team':12,'letter':'a','done':[]})).json()
  assert not st['quests']['12']['a'].get('records')
  assert st['quests']['12']['b']['records']['q1']==stamp
  print('OK operator rewind clears only the selected tablet capture',flush=True)
  await post('team_reset',{'team':12,'confirm':'AGAIN'})
  await pg.reload(wait_until='load');await pg.wait_for_function('!!window.__activity',timeout=60000)
  assert await pg.evaluate('__activity().count')==0
  print('OK replacement tablet inherits captures; team reset clears them',flush=True)
  assert not errors,errors;await browser.close()
asyncio.run(main())
