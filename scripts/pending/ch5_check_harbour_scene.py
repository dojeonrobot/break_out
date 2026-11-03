import asyncio,json,pathlib,re
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'harbour-scene';OUT.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as p:
  br=await p.chromium.launch(args=['--enable-gpu']);ctx=await br.new_context(viewport={'width':1440,'height':900},device_scale_factor=1)
  await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999')")
  await ctx.route('**/api/void/**',lambda r:r.abort())
  pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12',wait_until='load');await pg.wait_for_function('!!window.__dbg?.rideState',timeout=60000)
  await pg.evaluate("__dbg.tutEnd();__dbg.setWorld('island',true)");await asyncio.sleep(2)
  result=await pg.evaluate('''()=>{const d=__dbg,P=__parkPolish,H=P.state.harbour,T=d.THREE;const b=d.IB.find(b=>b.label==='도로랜드 퍼레이드'),p=b.mesh;let maxZ=-1e9,minZ=1e9,bad=0;
  for(let t=0;t<150;t+=.5){P.frame(t);p.updateMatrixWorld(true);for(const f of p.userData.audit.floats){const box=new T.Box3().setFromObject(f);maxZ=Math.max(maxZ,box.max.z);minZ=Math.min(minZ,box.min.z);if(box.max.z>H.entry.z-15)bad++;}}
  const saved=d.islRoot.userData.visitorAudit.positions.splice(0);const hinges=[];H.gate.traverse(o=>{if(o.name.startsWith('entrance-barrier-'))hinges.push(o)});const barriers=hinges.map(h=>{const samples=[];for(let t=0;t<12;t+=.25){h.userData.animate(t);samples.push({x:h.rotation.x,y:h.rotation.y,z:h.rotation.z})}return {name:h.name,xSpan:Math.max(...samples.map(s=>s.x))-Math.min(...samples.map(s=>s.x)),ySpan:Math.max(...samples.map(s=>s.y))-Math.min(...samples.map(s=>s.y)),zSpan:Math.max(...samples.map(s=>s.z))-Math.min(...samples.map(s=>s.z))}});
  d.islRoot.userData.visitorAudit.positions.push(...saved);const boundary=x=>x<=60?390:x>=130?490:390+(x-60)*100/70,crossings=[];for(const [r,points]of d.PATHS.entries())for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],sa=a[1]-boundary(a[0]),sb=b[1]-boundary(b[0]);if(sa*sb<0){const u=sa/(sa-sb),x=a[0]+(b[0]-a[0])*u;crossings.push({route:r,x,z:a[1]+(b[1]-a[1])*u})}}
  const v=d.islRoot.userData.visitorAudit,head=v.guests.parts.head;const m=new T.Matrix4(),a=new T.Vector3(),q=new T.Quaternion(),scale=new T.Vector3();let feet=Infinity;for(let i=0;i<32;i++){v.guests.parts.shoeL.getMatrixAt(i,m);m.decompose(a,q,scale);feet=Math.min(feet,a.y-.168*scale.y-d.groundY(a.x,a.z))}
  return {parade:{minZ,maxZ,bad},barriers,crossings,labels:d.IB.filter(b=>/항구|라군|정문/.test(b.label)).map(b=>b.label),gateScale:H.gate.scale.toArray(),visitors:{count:v.walkers.length,parts:Object.keys(v.guests.parts),feet},blockedWest:d.walkBlocked(-150,390),openGate:d.walkBlocked(0,390),device:d.device().spot,errors:[]};}''')
  (OUT/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
  assert not result['parade']['bad'],'parade crosses gate';assert result['parade']['minZ']>180,'parade crosses fountain';print('OK full parade cycle clears fountain and gate',flush=True)
  assert len(result['barriers'])==10 and all(b['xSpan']==b['ySpan']==0 and b['zSpan']>1.4 for b in result['barriers']);print('OK ten barriers pivot vertically at their side hinges',flush=True)
  assert result['labels'].count('항구')==1 and '키즈 라군' not in result['labels'];assert result['blockedWest'] and not result['openGate'];assert all(abs(c['x'])<20 for c in result['crossings']),result['crossings'];print('OK harbour unified, west bypass blocked, all path crossings use main gate',flush=True)
  assert result['visitors']['count']==640 and len(result['visitors']['parts'])>=14 and result['visitors']['feet']>=-.01;print('OK articulated crowd includes faces, hair, clothes, arms and grounded feet',flush=True)
  # Exhaustive reachability with the gate temporarily treated as closed: no harbour-to-park bypass.
  reach=await pg.evaluate('''()=>{const d=__dbg,step=3,X0=-630,Z0=-610,W=421,H=440,n=W*H,seen=new Uint8Array(n),idx=(x,z)=>Math.floor((z-Z0)/step)*W+Math.floor((x-X0)/step),start=idx(0,450),stack=[start];seen[start]=1;let crossed=false,count=0;while(stack.length){const k=stack.pop(),i=k%W,j=(k/W)|0,x=X0+i*step+1.5,z=Z0+j*step+1.5;count++;if(z<365){crossed=true;break;}for(const [a,b]of [[i-1,j],[i+1,j],[i,j-1],[i,j+1]]){if(a<0||a>=W||b<0||b>=H)continue;const key=b*W+a;if(seen[key])continue;const px=X0+a*step+1.5,pz=Z0+b*step+1.5;if(Math.abs(px)<24&&Math.abs(pz-390)<3)continue;if(d.walkBlocked(px,pz))continue;seen[key]=1;stack.push(key)}}return {crossed,count}}''')
  print('closed gate reach',reach,flush=True);assert not reach['crossed'];print('OK exhaustive harbour flood cannot enter park without the gate',flush=True)
  for name,pos,tgt in [('harbour',[-75,180,660],[-105,5,450]),('gate',[5,44,490],[0,24,390]),('people',[2,7,270],[7,5.2,252])]:
   await pg.evaluate('([p,t])=>{const d=__dbg;d.flyTo(new d.THREE.Vector3(...p),new d.THREE.Vector3(...t),1)}',[pos,tgt]);await asyncio.sleep(.4);await pg.screenshot(path=str(OUT/(name+'.png')))
  assert not errors,errors;print('OK no runtime errors',flush=True);await br.close()
asyncio.run(main())
