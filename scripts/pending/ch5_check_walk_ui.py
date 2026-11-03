import asyncio,json,pathlib,re,statistics
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'walk-ui';OUT.mkdir(exist_ok=True)
STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
async def main():
 failures=[];report=[]
 def check(ok,msg):
  print(('OK ' if ok else 'FAIL ')+msg,flush=True)
  if not ok:failures.append(msg)
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=['--enable-gpu'])
  for name,w,h,touch in [('pc',1280,800,False),('tablet-small',800,600,True),('tablet-portrait',800,1280,True),('tablet-short',844,390,True)]:
   # Phones intentionally use the auxiliary role. Resize an active tablet to test a short play viewport.
   initial={'width':1280,'height':800} if name=='tablet-short' else {'width':w,'height':h}
   ctx=await browser.new_context(viewport=initial,screen=initial,has_touch=touch,is_mobile=False,device_scale_factor=1)
   await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','walkui');localStorage.setItem('void-mini-12',JSON.stringify({q:'q1',step:'station',pos:[0,258,0]}));")
   await ctx.request.post(API+'/api/void/team_reset',data={'team':12,'confirm':'AGAIN'},headers={'X-Admin-Key':'0101'})
   await ctx.request.post(API+'/api/void/admin/skip',data={'team':12,'mission':'z1'},headers={'X-Admin-Key':'0101'})
   await ctx.request.post(API+'/api/void/quest',data={'team':12,'dev':'walkui','done':[],'act':1,'tut':True})
   async def route(r):
    q=r.request;res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']})
    await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
   await ctx.route(re.compile(r'.*/api/void/.*'),route)
   pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
   await pg.goto(STATIC+'/chapter05/index.html?team=12&world=island',wait_until='load')
   await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
   await pg.evaluate('__dbg.tutEnd()');await asyncio.sleep(2)
   await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('\uB9AC\uCF54\u00B7\uC81C\uB85C')")
   await pg.wait_for_function('!!__dbg.walk()',timeout=30000)
   await pg.wait_for_function('!!__dbg.chars().ZERO.userData.model',timeout=30000)
   if name=='tablet-short': await pg.set_viewport_size({'width':w,'height':h})
   await asyncio.sleep(1)
   await pg.evaluate('()=>{for(let i=0;i<30&&__dbg.quest().vn();i++)__dbg.quest().next()}')
   for _ in range(3):
    if await pg.locator('#voidVn').is_visible(): await pg.locator('#voidNext').click()
   await asyncio.sleep(.5)
   metrics=await pg.evaluate('''()=>{const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,r:r.right,b:r.bottom,w:r.width,h:r.height}};const hud=['walkHud','questHud'].map(id=>({id,...rect(document.getElementById(id))}));const d=__dbg;d.camera.updateMatrixWorld();const chars=['ZERO','RICO'].map(n=>{const box=new d.THREE.Box3().setFromObject(d.chars()[n]);const p=box.getCenter(new d.THREE.Vector3()).project(d.camera);return {n,x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2}});return {hud,chars,buttons:['walkHelp','walkX'].map(id=>rect(document.getElementById(id))),overflow:document.documentElement.scrollWidth>innerWidth,walk:!!d.walk()}}''')
   report.append({'name':name,'layout':metrics})
   a,b=metrics['hud']
   check(metrics['walk'],name+' actual walk mode')
   check(all(q['x']>=0 and q['y']>=0 and q['r']<=w and q['b']<=h for q in metrics['hud']),name+' both HUD cards fully in viewport')
   check(a['x']>=b['r'] or b['x']>=a['r'] or a['y']>=b['b'] or b['y']>=a['b'],name+' HUD cards do not overlap')
   check(max(a['b'],b['b'])<h*.3,name+' top controls use less than 30% height')
   check(all(not(q['x']<=c['x']<=q['r'] and q['y']<=c['y']<=q['b']) for c in metrics['chars'] for q in metrics['hud']),name+' both character centers clear of HUD')
   check(all(q['h']>=44 and q['w']>=44 for q in metrics['buttons']),name+' 44px help and exit')
   check(not metrics['overflow'],name+' no overflow')
   await pg.screenshot(path=str(OUT/(name+'.png')))
   await pg.locator('#walkHelp').click();check(await pg.locator('#walkHint').is_visible(),name+' instructions expand');await pg.locator('#walkHelp').click()
   if name=='pc':
    await pg.evaluate('''()=>{const r=__dbg.renderer,orig=r.render;window.__frames=[];r.render=function(...args){if(__dbg.walk()){const w=__dbg.walk();__frames.push({t:performance.now(),shadow:r.shadowMap.needsUpdate,radius:Math.hypot(__dbg.camera.position.x-w.x,__dbg.camera.position.z-w.z)})}return orig.apply(this,args)}}''')
    pos=await pg.evaluate('({x:__dbg.walk().x,z:__dbg.walk().z,yaw:__dbg.walk().yaw})')
    await pg.keyboard.down('w');await asyncio.sleep(2);await pg.keyboard.up('w')
    after=await pg.evaluate('({x:__dbg.walk().x,z:__dbg.walk().z})')
    check(abs(after['x']-pos['x'])+abs(after['z']-pos['z'])>2,'PC input actually moves character')
    await pg.keyboard.down('a');await asyncio.sleep(2);await pg.keyboard.up('a')
    check(abs(await pg.evaluate('__dbg.walk().yaw')-pos['yaw'])>1,'PC input actually turns character')
    frames=await pg.evaluate('__frames');report[-1]['frames']=frames
    check(len(frames)>30,'PC rendered actual movement frames '+str(len(frames)))
    check(all(f['shadow'] for f in frames),'PC every walking frame refreshes shadows')
    check(max(f['radius'] for f in frames)-min(f['radius'] for f in frames)<.001,'PC camera distance remains stable while moving and turning')
    await pg.evaluate('__dbg.dlg.yard(false)');await asyncio.sleep(1)
    await pg.evaluate('()=>{const y=__dbg.yard();y.tiles=y.sol.map(r=>r.map(c=>new Set(c)));__dbg.yardPaint()}')
    check(await pg.locator('#ydSuccess').is_visible(),'breaker success status visible')
    check(await pg.locator('#ydMix').is_disabled(),'breaker locks shuffle on success')
    fx=await pg.evaluate("()=>[...document.querySelectorAll('#ydBoard button')].map(b=>({animation:getComputedStyle(b).animationName,delay:b.style.getPropertyValue('--power-delay')}))")
    check(len(fx)==20 and all(b['animation']=='power-arrive' for b in fx) and len(set(b['delay'] for b in fx))>2,'power wave travels through all 20 tiles')
    await pg.screenshot(path=str(OUT/'breaker-success.png'))
    await asyncio.sleep(2.7)
    check(await pg.locator('#ydContinue').is_visible(),'breaker success waits for player confirmation')
    await pg.locator('#ydContinue').click()
    await pg.wait_for_function("!document.getElementById('yardDlg').dataset.on",timeout=8000)
    check((await pg.evaluate('__dbg.miniCp()'))['step']=='station','breaker advances to station')
    await pg.evaluate('()=>{for(let i=0;i<30&&__dbg.quest().vn();i++)__dbg.quest().next()}')
    await pg.emulate_media(reduced_motion='reduce')
    await pg.evaluate('__dbg.dlg.yard(false);(()=>{const y=__dbg.yard();y.tiles=y.sol.map(r=>r.map(c=>new Set(c)));__dbg.yardPaint()})()')
    check(await pg.locator('#ydSuccess').is_visible() and await pg.locator('#ydBoard button').first.evaluate("e=>getComputedStyle(e).animationName")=='none','reduced motion keeps static success')
    await pg.evaluate('__dbg.stopWalk()');await asyncio.sleep(3)
    check(not await pg.locator('#yardDlg').is_visible(),'exit cancels pending success transition')
   check(not errors,name+' no JavaScript errors '+str(errors))
   await ctx.close()
  await browser.close()
 (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print('FAILS',failures,flush=True)
 assert not failures,failures
asyncio.run(main())
