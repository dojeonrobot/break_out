import asyncio, json, pathlib, re, tempfile
from playwright.async_api import async_playwright

OUT = pathlib.Path(tempfile.mkdtemp(prefix='ch5-layout-'))
OUT.mkdir(exist_ok=True)
STATIC, API = 'http://127.0.0.1:8097', 'http://127.0.0.1:8096'

async def main():
    print('Screenshots and results:', OUT, flush=True)
    results, errors, failures = [], [], []
    def check(ok, detail):
        print(('OK ' if ok else 'FAIL ') + detail, flush=True)
        if not ok: failures.append(detail)
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, w, h in [('tablet-landscape',1280,800),('tablet-portrait',800,1280),('phone-portrait',390,844),('phone-landscape',844,390)]:
            ctx = await browser.new_context(viewport={'width':w,'height':h},screen={'width':w,'height':h},has_touch=True,is_mobile=min(w,h)<=500,device_scale_factor=1)
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
            async def route(r):
                q=r.request
                res=await ctx.request.fetch(q.url.replace(STATIC,API),method=q.method,data=q.post_data_buffer,headers={k:v for k,v in q.headers.items() if k not in ['host','origin','referer']})
                await r.fulfill(status=res.status,body=await res.body(),headers={'content-type':res.headers.get('content-type','application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'),route)
            await ctx.request.post(API+'/api/void/team_reset',data={'team':12,'confirm':'AGAIN'},headers={'X-Admin-Key':'0101'})
            pg=await ctx.new_page()
            pg.on('pageerror',lambda e:errors.append(str(e)))
            await pg.goto(STATIC+'/chapter05/index.html?team=12&world=island',wait_until='load')
            await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
            await pg.evaluate('__dbg.tutEnd()')
            await asyncio.sleep(3)
            await pg.evaluate("__dbg.setWorld('island',true)")
            await asyncio.sleep(2)
            metrics=await pg.evaluate('''() => {
                const rect=id=>{const r=document.getElementById(id).getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height}};
                const d=__dbg, c=d.camera; c.updateMatrixWorld();
                const coast=Array.from({length:200},(_,i)=>{const a=i/200*Math.PI*2,r=d.K*(400+40*Math.sin(3*a+1)+25*Math.sin(5*a+2)+15*Math.sin(9*a));const v=new d.THREE.Vector3(Math.cos(a)*r,d.G,Math.sin(a)*r).project(c);return [v.x,v.y]});
                return {name:'',size:[innerWidth,innerHeight],fov:c.fov,help:rect('restoreBtn'),sim:rect('simBtn'),panel:rect('panel'),coast:{x:Math.max(...coast.map(p=>Math.abs(p[0]))),y:Math.max(...coast.map(p=>Math.abs(p[1])))},overflow:document.documentElement.scrollWidth>innerWidth};
            }''')
            metrics['name']=name
            gap=metrics['sim']['y']-metrics['help']['bottom']
            check(gap>=8,name+f' action gap {gap:.1f}px')
            check(not metrics['overflow'],name+' no page overflow')
            check(metrics['coast']['x']<=1 and metrics['coast']['y']<=1,name+' island coast inside viewport '+str(metrics['coast']))
            check(metrics['help']['h']>=44 and metrics['sim']['h']>=44,name+' touch targets at least 44px')
            await pg.screenshot(path=str(OUT/(name+'.png')))
            if name.startswith('tablet'):
                stack=await pg.evaluate('''()=>{const q=document.getElementById('questPill'),c=document.getElementById('callPill'),oldQ=q.hidden,oldC=c.dataset.on;q.hidden=false;c.dataset.on='1';const boxes=[...document.querySelectorAll('#islandActions>button')].map(e=>{const r=e.getBoundingClientRect();return {id:e.id,top:r.top,bottom:r.bottom,height:r.height}}).filter(r=>r.height);q.hidden=oldQ;if(oldC===undefined)delete c.dataset.on;else c.dataset.on=oldC;return boxes}''')
                check(all(stack[i]['top']-stack[i-1]['bottom']>=8 for i in range(1,len(stack))),name+' call and resume actions keep their gaps')
                await pg.evaluate('__dbg.dlg.lab(false)')
                await asyncio.sleep(1)
                for state in ['ready','complete']:
                    if state=='complete': await pg.evaluate('__dbg.dlg.lab(true)')
                    cards=await pg.evaluate('''()=>[...document.querySelectorAll('#lbMons .mon')].map(m=>{const r=m.getBoundingClientRect(),b=m.querySelector('.play').getBoundingClientRect(),st=m.querySelector('.st');return {name:m.dataset.g,width:r.width,scroll:m.scrollWidth,client:m.clientWidth,button:b.width?{left:b.left-r.left,right:r.right-b.right,height:b.height}:null,hint:st.textContent,hintWidth:st.clientWidth,hintScroll:st.scrollWidth}})''')
                    for c in cards:
                        check(c['scroll']<=c['client']+1 and c['hintScroll']<=c['hintWidth']+1,name+' lab '+state+' '+c['name']+' fits')
                        if c['button']: check(c['button']['left']>=0 and c['button']['right']>=0 and c['button']['height']>=44,name+' lab button fully visible '+c['name'])
                    await pg.screenshot(path=str(OUT/(name+'-lab-'+state+'.png')))
                await pg.evaluate("delete document.getElementById('labDlg').dataset.on")
            if name=='tablet-landscape':
                bars=await pg.evaluate('''()=>{const d=__dbg,bars=[];d.islRoot.traverse(o=>{if(/^entrance-barrier-[0-9]+$/.test(o.name))bars.push(o)});return {count:bars.length,dynamic:bars.every(b=>b.userData.dynamic),changed:bars.map(b=>{const rotations=[];for(let t=0;t<14;t+=.25){b.userData.animate(t);rotations.push(b.rotation.z)}return Math.max(...rotations)-Math.min(...rotations)>.1}),audit:d.bakedAudit()}}''')
                check(bars['count']==10 and bars['dynamic'] and sum(bars['changed'])>=6,'10 entrance barriers stay dynamic and swing (a bar with a visitor frozen beside it stays open in this probe) '+str(sum(bars['changed'])))
                check(not bars['audit'],'baked audit has no false gangway warning '+str(bars['audit']))
                metrics['bars']=bars
                # Check computed colors in both themes, including inverse marker badges.
                contrasts=await pg.evaluate('''()=>{const lum=c=>{const v=c.match(/[\\d.]+/g).slice(0,3).map(Number).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return v[0]*.2126+v[1]*.7152+v[2]*.0722};const host=document.createElement('div');host.innerHTML='<button class="mk ok">완료 <em>복구됨</em></button><span class="st ok">완료</span>';document.body.append(host);const out=[];for(const theme of ['light','dark']){document.documentElement.dataset.theme=theme;for(const e of host.querySelectorAll('.mk,em,.st')){const s=getComputedStyle(e),a=lum(s.color),b=lum(s.backgroundColor);out.push({theme,tag:e.className||e.tagName,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)})}}host.remove();document.documentElement.dataset.theme='light';return out}''')
                check(all(c['ratio']>=4.5 for c in contrasts),'completed labels pass 4.5:1 contrast '+json.dumps(contrasts))
                metrics['contrast']=contrasts
                await pg.evaluate("__dbg.setWorld('island',true);__dbg.camera.position.x+=50")
                before=await pg.evaluate('({p:__dbg.camera.position.toArray(),t:__dbg.controls.target.toArray()})')
                await pg.set_viewport_size({'width':800,'height':1280})
                after=await pg.evaluate('({p:__dbg.camera.position.toArray(),t:__dbg.controls.target.toArray(),fov:__dbg.camera.fov})')
                check(max(abs(x-y) for x,y in zip(before['p'],after['p']))<.1 and before['t']==after['t'],'orientation change preserves camera position and target')
            results.append(metrics)
            await ctx.close()
        await browser.close()
    check(not errors,'no page errors '+str(errors))
    (OUT/'checks.json').write_text(json.dumps({'results':results,'errors':errors,'failures':failures},ensure_ascii=False,indent=2),encoding='utf-8')
    assert not failures, failures

asyncio.run(main())
