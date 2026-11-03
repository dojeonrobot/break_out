import asyncio,json,pathlib,re,math
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'maze-view';OUT.mkdir(exist_ok=True)
REPO=pathlib.Path('C:/Users/dlgus/break_out');STATIC='http://127.0.0.1:8097';API='http://127.0.0.1:8096'
async def main():
 failures=[];report=[]
 def check(ok,msg):
  print(('OK ' if ok else 'FAIL ')+msg,flush=True)
  if not ok:failures.append(msg)
 source=(REPO/'chapter05/index.html').read_text(encoding='utf8')
 source=source.replace('function tick(now){','function tick(now){ if(window.__pauseScene) return;')
 source=source.replace('const BAKED = [];',"const BAKED = []; window.__motion={get keys(){return WALK_KEYS;},step:(now)=>{updateI(now,1);walkTick(now);camera.updateMatrixWorld();sceneI.updateMatrixWorld(true);},resume:()=>requestAnimationFrame(tick),render:()=>renderer.render(sceneI,camera)};")
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=['--enable-gpu'])
  for name,w,h,touch in [('pc',1280,800,False),('tablet',800,600,True),('portrait',800,1280,True),('short',844,390,True)]:
   initial={'width':1280,'height':800} if name=='short' else {'width':w,'height':h}
   ctx=await browser.new_context(viewport=initial,screen=initial,has_touch=touch,device_scale_factor=1)
   await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','mazeview');")
   await ctx.request.post(API+'/api/void/team_reset',data={'team':12,'confirm':'AGAIN'},headers={'X-Admin-Key':'0101'})
   for mission in ['z1','z2']:await ctx.request.post(API+'/api/void/admin/skip',data={'team':12,'mission':mission},headers={'X-Admin-Key':'0101'})
   await ctx.request.post(API+'/api/void/quest',data={'team':12,'dev':'mazeview','done':['q1'],'act':2,'tut':True})
   async def route(r):
    q=r.request;res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']})
    await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
   await ctx.route(re.compile(r'.*/api/void/.*'),route)
   await ctx.route('**/chapter05/index.html*',lambda r:r.fulfill(body=source,content_type='text/html'))
   pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
   await pg.goto(STATIC+'/chapter05/index.html?team=12&world=island',wait_until='load')
   await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
   await pg.evaluate('__dbg.tutEnd()');await asyncio.sleep(2)
   await pg.evaluate("__dbg.setWorld('island',true);__dbg.startWalk('\uB9AC\uCF54\u00B7\uC81C\uB85C')")
   await pg.wait_for_function('!!__dbg.walk() && !!__dbg.chars().ZERO.userData.model',timeout=30000)
   if name=='short':await pg.set_viewport_size({'width':w,'height':h})
   await asyncio.sleep(1)
   await pg.evaluate('()=>{for(let i=0;i<30&&__dbg.quest().vn();i++)__dbg.quest().next()}')
   for _ in range(3):
    if await pg.locator('#voidVn').is_visible():await pg.locator('#voidNext').click()
   check(await pg.evaluate("__dbg.quest().live?.id==='q2'"),name+' actual maze mission')
   await pg.evaluate('window.__pauseScene=true');await asyncio.sleep(.1)
   result=await pg.evaluate('''()=>{const d=__dbg,w=d.walk(),M=d.maze(),m=__motion;let now=performance.now();w.last=now;const coord=(i,j)=>{const x=-M.S/2+(j+.5)*M.cell,z=-M.S/2+(i+.5)*M.cell;return [M.cx+x*Math.cos(M.rot)+z*Math.sin(M.rot),M.cz-x*Math.sin(M.rot)+z*Math.cos(M.rot)]};let [i,j]=M.ent,route=[[i,j]];while(M.dist[i][j]>0){const nb=[[i-1,j,!M.H[i][j]],[i+1,j,!M.H[i+1][j]],[i,j-1,!M.V[i][j]],[i,j+1,!M.V[i][j+1]]].find(([a,b,o])=>o&&a>=0&&b>=0&&a<M.n&&b<M.n&&M.dist[a][b]===M.dist[i][j]-1);[i,j]=nb;route.push([i,j])}const start=coord(...route[0]);w.x=start[0];w.z=start[1];w.snap=true;const samples=[];let blocked=0;const sample=()=>{samples.push({radius:Math.hypot(d.camera.position.x-w.x,d.camera.position.z-w.z),height:d.camera.position.y-d.groundY(w.x,w.z),pitch:w.camPitch,fov:d.camera.fov,inside:d.mazeInside(w.x,w.z),cp:d.camera.position.toArray()})};for(let k=1;k<route.length;k++){const [x,z]=coord(...route[k]);m.keys.KeyW=true;let n=0;while(Math.hypot(x-w.x,z-w.z)>.12&&n++<160){w.yaw=Math.atan2(x-w.x,z-w.z);now+=1000/60;m.step(now);sample();if(d.quest().vn())break;}if(n>=160)blocked++;m.keys.KeyW=false;if(d.quest().vn())break;}m.render();return {samples,blocked,cells:route.length,position:[w.x,w.z],hasTrace:!!d.islRoot.getObjectByName('old-watercourse'),clip:M.clip.constant}}''')
   report.append({'name':name,'motion':result})
   samples=result['samples']
   check(len(samples)>100 and result['blocked']==0,name+' walks maze corridors and turns without getting stuck')
   for key in ['radius','height','pitch','fov']:
    spread=max(x[key] for x in samples)-min(x[key] for x in samples)
    check(spread<.0001,name+' fixed '+key+' spread '+str(round(spread,8)))
   check(result['hasTrace'],name+' old watercourse replaces orb')
   await pg.wait_for_function("document.getElementById('vn').dataset.speaker==='네이티'",timeout=5000)
   await pg.locator('#vnImg').evaluate('e=>e.decode()')
   await asyncio.sleep(.6)
   await pg.evaluate('()=>{if(__dbg.quest().vn()?.typing)__dbg.quest().next()}')
   metrics=await pg.evaluate('''()=>{const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,r:r.right,b:r.bottom,w:r.width,h:r.height}};const im=document.getElementById('vnImg');return {image:rect(im),box:rect(document.querySelector('#vn .box')),text:rect(document.getElementById('vnText')),clip:getComputedStyle(im).clipPath,copy:document.getElementById('vnText').textContent,scroll:document.documentElement.scrollWidth}}''')
   report[-1]['dialog']=metrics
   check(metrics['clip']=='none' and all(r['x']>=0 and r['y']>=0 and r['r']<=w and r['b']<=h for r in [metrics['image'],metrics['box'],metrics['text']]),name+' whole Naty portrait and dialogue within viewport')
   check(metrics['image']['b']<=metrics['box']['y']+1,name+' portrait does not overlap text box')
   check('물길 흔적' in metrics['copy'] and '구슬' not in metrics['copy'],name+' discovery explains the watercourse')
   await pg.screenshot(path=str(OUT/(name+'-naty.png')))
   await pg.evaluate('()=>{for(let i=0;i<30&&__dbg.quest().vn();i++)__dbg.quest().next();__motion.render()}')
   await asyncio.sleep(.5)
   await pg.screenshot(path=str(OUT/(name+'-watercourse.png')))
   check(await pg.locator('#qhT').inner_text()=='옛 물길 터 기록',name+' recording objective names discovery')
   await pg.evaluate('__dbg.stopWalk()')
   check(await pg.evaluate('__dbg.maze().clip.constant')==1e6,name+' leaving restores hedges')
   check(not errors,name+' no JavaScript errors '+str(errors))
   await ctx.close()
  await browser.close()
 (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print('FAILS',failures,flush=True);assert not failures,failures
asyncio.run(main())
