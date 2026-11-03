import asyncio,json,pathlib,re
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'script-revision';OUT.mkdir(exist_ok=True)
REPO=pathlib.Path('C:/Users/dlgus/break_out');STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
async def main():
 errors=[]
 source=(REPO/'chapter05/index.html').read_text(encoding='utf8')
 # Shorten only cinematic settling time; every dialogue and confirmation remains interactive.
 source=re.sub(r"const wait = ms => .*?;\nlet actBusy", "const wait=ms=>new Promise(r=>setTimeout(r,Math.min(ms,60)));\nlet actBusy",source)
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=['--enable-gpu']);ctx=await browser.new_context(viewport={'width':1280,'height':800},device_scale_factor=.75,reduced_motion='reduce')
  await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','storytest');")
  await ctx.request.post(API+'/api/void/team_reset',data={'team':12,'confirm':'AGAIN'},headers={'X-Admin-Key':'0101'})
  for mission in ['z1','z2']:await ctx.request.post(API+'/api/void/admin/skip',data={'team':12,'mission':mission},headers={'X-Admin-Key':'0101'})
  await ctx.request.post(API+'/api/void/quest',data={'team':12,'dev':'storytest','done':['q1'],'act':2,'tut':True,'story':2})
  reject_capture=False
  async def route(r):
   nonlocal reject_capture
   q=r.request
   if reject_capture and q.method=='POST' and q.url.endswith('/quest') and 'records' in (q.post_data or ''):
    reject_capture=False
    await r.fulfill(status=503,body=json.dumps({'error':'test unavailable'}),content_type='application/json');return
   res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']})
   await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
  await ctx.route(re.compile(r'.*/api/void/.*'),route);await ctx.route('**/chapter05/index.html*',lambda r:r.fulfill(body=source,content_type='text/html'))
  pg=await ctx.new_page();pg.on('pageerror',lambda e:(errors.append(str(e)),print('PAGEERROR',str(e),flush=True)))
  await pg.goto(STATIC+'/chapter05/index.html?team=12',wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  async def say_done():
   await pg.evaluate('()=>{for(let i=0;i<120&&__dbg.quest().vn();i++)__dbg.quest().next()}')
  async def drain_until(selector,timeout=25):
   for _ in range(timeout*10):
    if await pg.locator(selector).is_visible():return
    await say_done()
    if await pg.locator('#voidVn').is_visible():await pg.locator('#voidNext').click()
    await asyncio.sleep(.1)
   raise AssertionError('never appeared '+selector+' '+str(errors))
  assert await pg.evaluate('__dbg.tutState().len')==22;print('OK 22 tutorial beats',flush=True)
  await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('리코·제로')");await asyncio.sleep(1);await say_done()
  assert await pg.evaluate("__dbg.quest().live.id")=='q2'
  await pg.evaluate('()=>{const q=__dbg.quest();__dbg.walkTo(...q.target(q.live))}')
  await pg.wait_for_function("__dbg.quest().vn()?.lines[0].text.includes('울타리')")
  assert not await pg.locator('#miniBox').is_visible();print('OK maze entrance dialogue precedes exploration',flush=True)
  await say_done();await pg.evaluate('__dbg.walkTo(165,420)')
  await pg.wait_for_function("__dbg.quest().vn()?.lines[0].text.includes('찾았다')")
  assert not await pg.evaluate("!!__dbg.islRoot.getObjectByName('old-watercourse')");await say_done();await asyncio.sleep(.7)
  assert await pg.evaluate("__dbg.mini().phase")=='naty-shot';assert await pg.locator('#miniBox').is_visible()
  assert not await pg.evaluate('(()=>{const w=__dbg.walk();return __dbg.mazeInside(w.x,w.z)})()')
  assert await pg.evaluate('__activity().count')==3
  assert '기록 찍기' in await pg.evaluate('__activity().help')
  # Leave and resume before capture: the count must remain 3 and the pair stays outside.
  await pg.evaluate("__dbg.stopWalk();__dbg.startWalk('리코·제로')");await say_done();await asyncio.sleep(.3)
  assert await pg.evaluate('__activity().count')==3
  assert not await pg.evaluate('(()=>{const w=__dbg.walk();return __dbg.mazeInside(w.x,w.z)})()')
  reject_capture=True
  await pg.locator('#miniGo').click()
  await pg.wait_for_function("document.getElementById('qhHint').textContent.includes('저장하지 못했습니다')")
  assert await pg.evaluate('__activity().count')==3
  assert not await pg.locator('#miniGo').is_disabled()
  print('OK failed record save keeps count unchanged and allows retry',flush=True)
  await pg.locator('#miniGo').click();await say_done();await pg.wait_for_function('__activity().count===4')
  await say_done();await pg.wait_for_function('__dbg.mini().phase==="walk"')
  state=await (await ctx.request.get(API+'/api/void/state')).json()
  assert state['quests']['12']['a']['records'].get('q2')
  assert 'q2' not in state['quests']['12']['a']
  assert '연구실' in await pg.evaluate('__activity().help')
  print('OK maze only finds Naty; separate capture outside persists record 4 before lab completion',flush=True)
  await pg.evaluate('__dbg.walkTo(...__dbg.labDoor())');await drain_until('#labDlg');await asyncio.sleep(1);await say_done()
  assert await pg.locator('#lbMons svg').count()==1
  assert '선대' not in await pg.locator('#lbMons').inner_text()
  assert '설계도' not in await pg.locator('#labDlg').inner_text()
  await pg.screenshot(path=str(OUT/'analysis.png'))
  await pg.locator('#lbGo').click();await drain_until('#qReward');assert '네이티 발견' in await pg.locator('#qrT').inner_text()
  assert not await pg.locator('#qrList .z').count();assert 'q4' not in await pg.evaluate('__dbg.qdone()')
  print('OK lab uses captured fourth record and identifies only an anomaly, no device identity or blueprint',flush=True)
  await pg.locator('#qrMap').click();await asyncio.sleep(1);await say_done()
  assert await pg.evaluate('__dbg.quest().live.id')=='q4'
  await pg.evaluate('()=>{const q=__dbg.quest();__dbg.walkTo(...q.target(q.live))}');await drain_until('#deviceDlg');await say_done()
  await pg.locator('[data-part="2"]').click();assert await pg.evaluate('__dbg.device().mini.hits')==0
  await pg.locator('[data-part="0"]').click();assert await pg.evaluate('__dbg.miniCp().hits')==1
  await pg.evaluate("__dbg.stopWalk();__dbg.startWalk('리코·제로')");await asyncio.sleep(.4);await say_done()
  assert await pg.evaluate('__dbg.device().mini.hits')==1;print('OK single destruction game rejects unlit targets and resumes partial damage',flush=True)
  for key in ['1','2']:await pg.locator(f'[data-part="{key}"]').click()
  await say_done();assert await pg.evaluate('__dbg.device().mini.hits')==3
  assert await pg.locator('#dvCore').count()==0
  assert not await pg.evaluate('__dbg.device().model.flow.visible')
  await pg.screenshot(path=str(OUT/'destroyed.png'))
  await pg.locator('#dvContinue').click();await pg.evaluate('__dbg.walkTo(...__dbg.labDoor())');await drain_until('#qReward')
  assert '선대의 잔재 파괴' in await pg.locator('#qrT').inner_text();assert await pg.locator('#qrList .z').count()==1
  assert await pg.evaluate('__dbg.simState().lit')==4;print('OK three sequential lit parts collapse the remains, regroup unlocks record 3, total stays 4/5',flush=True)
  # Seed only the final campus record, retaining the completed island sequence.
  await pg.locator('#qrMap').click()
  await ctx.request.post(API+'/api/void/admin/skip',data={'team':12,'mission':'z3'},headers={'X-Admin-Key':'0101'})
  await ctx.request.post(API+'/api/void/quest',data={'team':12,'dev':'storytest','act':3})
  await pg.reload(wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('리코·제로')");await asyncio.sleep(1);await say_done()
  assert await pg.evaluate('__dbg.quest().live.id')=='q3'
  await pg.evaluate('()=>{const q=__dbg.quest();__dbg.walkTo(...q.target(q.live))}');await drain_until('#caveDlg');await asyncio.sleep(1);await say_done()
  for glyph in ['forest','valley','shore','cave','water','plaza']:
   await pg.locator(f'#cvTiles [data-g="{glyph}"]').click();await pg.locator(f'#cvMap [data-s="{glyph}"]').click()
  await asyncio.sleep(.7);await say_done();await pg.locator('#cvNext').click()
  assert await pg.locator('[data-set="dev"]').count()==0
  async def trial(order,amt):
   await pg.locator('#cvReset').click()
   for key in order:await pg.locator(f'[data-set="ord"] [data-v="{key}"]').click()
   await pg.locator(f'[data-set="amt"] [data-v="{amt}"]').click();await pg.locator('#cvGo').click();await asyncio.sleep(3.2);await say_done()
  await trial(['shore','forest','valley'],'big');assert await pg.locator('#cvWarn').inner_text()=='시설 이상 현상'
  await trial(['shore','forest','valley'],'small');assert await pg.locator('#cvWarn').inner_text()=='흐름이 이어지지 않음'
  await pg.evaluate("__dbg.stopWalk();__dbg.startWalk('리코·제로')");await asyncio.sleep(1.2);await say_done()
  assert await pg.locator('#cvLog li').count()==2;print('OK virtual trial log survives leaving and resuming',flush=True)
  await trial(['forest','valley','shore'],'small');assert await pg.evaluate('__dbg.caveS().phase')=='won'
  assert await pg.locator('#cvLog li').count()==3;await pg.screenshot(path=str(OUT/'trial.png'))
  print('OK only order and amount, amount failure first, full trial log and valid success',flush=True)
  await pg.locator('#cvNext').click();await drain_until('#simDone',40)
  assert await pg.locator('#simDoneX').inner_text()=='일루아 돌려주기';assert not await pg.locator('#cinema').is_visible()
  assert not await pg.evaluate("__dbg.quest().open().includes('자일로')")
  await pg.locator('#simDoneX').click();await say_done();await pg.wait_for_selector('#cinema',state='visible');await pg.locator('#cinemaSkip').click()
  assert await pg.locator('#cinemaEnd').is_visible();await asyncio.sleep(.5)
  state=await (await ctx.request.get(API+'/api/void/state')).json();assert state['quests']['12']['a'].get('restored')
  print('OK ending explicitly starts actual restoration; persisted completion unlocks free exploration',flush=True)
  assert not errors,errors
  await browser.close();print('OK no runtime errors through all revised stages',flush=True)
asyncio.run(main())
