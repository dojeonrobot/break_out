# 2026-11-11 섬 사람 캐릭터 다듬기: 둥근 몸·큰 머리·볼터치, 머리 모양 4종·치마·모자·어린이·풍선, 걸음 출렁임·고개 돌리기, 우측통행·비켜 걷기
# 사용: python ch5_patch_visitors.py            → chapter05/index.html 을 고침
#       python ch5_patch_visitors.py <사본경로>  → 원본은 두고 시험용 사본만 만듦
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
A = '// Shared visitor geometry keeps faces, clothes and a grounded stride affordable on tablets.\n'
B = '// Visitors share the final path network, with width-aware lanes and connected junctions.\n'
assert s.count(A) == 1 and s.count(B) == 1
a, b = s.index(A), s.index(B); assert a < b
NEW = r'''// Shared visitor geometry: rounded toy figures with hair, skirt, cap, child and balloon variants (2026-11-11).
// Variant parts are instanced only for the visitors that wear them, so the triangle count stays at the old level.
function visitorBatch(parent,count,prefix){
  const group=new THREE.Group();group.name=prefix;parent.add(group);
  const parts={},slots={},TAU=Math.PI*2;
  const skin=[0xf6d3b6,0xe2b48f,0xb57c5a,0xf3dcc6,0xd9a47c],hair=[0x2b211c,0x5a3524,0x1f1d27,0x9a6532,0x3a2a22,0xc79a55,0x77737a];
  const shirts=[0xe8785f,0x5b9bd5,0xf2c14e,0x6fb98f,0xa68ad6,0xf29cb0,0xf5efe0,0x3f6f8f,0xef9a4a,0x8fc7c4],pants=[0x3e4a5c,0x6b6257,0x2f5d7c,0x8a8f86,0xcdb991];
  const skirts=[0xf2c14e,0xe8785f,0x4f7fb5,0xf7f1e4,0x7a5ca8,0x5fa98a],shoes=[0x353941,0xf4f1ea,0x8a5a3c,0xd9534f],caps=[0xd9534f,0x2f5d7c,0xf5efe0,0xf2c14e,0x4f9a78],balloons=[0xff6b6b,0xffc93c,0x4dabf7,0x69db7c,0xda77f2,0xff922b];
  const traits=[];
  for(let i=0;i<count;i++){
    let h=Math.imul(i+17,2654435761)>>>0;const next=()=>{h=(Math.imul(h,1664525)+1013904223)>>>0;return (h>>>8)/16777216;},pick=a=>a[Math.floor(next()*a.length)];
    const kid=next()<.22,style=pick(['short','short','long','long','bun','cap']),skirt=(style==='long'||style==='bun')&&next()<.6,balloon=next()<(kid?.3:.05);
    traits.push({kid,style,skirt,balloon,size:(kid?.7:.94)+next()*(kid?.1:.14),head:kid?1.17:1,cadence:kid?7.4:6.1,
      skin:pick(skin),hair:pick(hair),shirt:pick(shirts),pants:pick(pants),shoe:pick(shoes),skirtColor:pick(skirts),cap:pick(caps),balloonColor:pick(balloons)});
  }
  const merge=gs=>mergeGeometries(gs.map(g=>g.index?g.toNonIndexed():g),false),lathe=(pts,seg)=>new THREE.LatheGeometry(pts.map(([x,y])=>new THREE.Vector2(x,y)),seg);
  // wear: which visitors get this part (default everyone); colour: trait key painted per instance
  const part=(key,geo,{color=0xffffff,shadow=false,material=null,wear=null,paint=null}={})=>{
    const members=traits.map((t,i)=>i).filter(i=>!wear||wear(traits[i])),slot=new Int32Array(count).fill(-1);members.forEach((i,n)=>slot[i]=n);
    const m=new THREE.InstancedMesh(geo,material||mat(color),Math.max(1,members.length));m.count=members.length;m.name=prefix+'-'+key;m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);m.castShadow=!PHONE&&shadow;m.frustumCulled=false;
    if(paint){const c=new THREE.Color();members.forEach((i,n)=>m.setColorAt(n,c.setHex(paint(traits[i]))));}
    group.add(m);parts[key]=m;slots[key]=slot;return m;};
  const crown=()=>new THREE.SphereGeometry(.72,10,4,0,TAU,0,Math.PI*.56).scale(1,1.03,.98).rotateX(-.2).translate(0,3.86,-.05);
  part('body',lathe([[.2,3.04],[.37,2.95],[.5,2.78],[.555,2.5],[.6,1.95],[.585,1.6],[.47,1.46],[.001,1.46]],10),{shadow:true,paint:t=>t.shirt});
  part('head',merge([SPH(.68,10,7).scale(1,1.03,.95).translate(0,3.72,0),SPH(.14,5,3).translate(-.66,3.66,0),SPH(.14,5,3).translate(.66,3.66,0),new THREE.CylinderGeometry(.2,.23,.34,6,1,true).translate(0,3.06,0)]),{shadow:true,paint:t=>t.skin});
  part('hair',crown(),{wear:t=>t.style!=='long',paint:t=>t.hair});
  // Longer hair is an open shell behind the face, so it needs both faces drawn.
  part('hairLong',merge([crown(),new THREE.SphereGeometry(.75,10,5,Math.PI*.84,Math.PI*1.32,Math.PI*.3,Math.PI*.6).scale(1,1.22,1).translate(0,3.64,-.03)]),{wear:t=>t.style==='long',paint:t=>t.hair,material:new THREE.MeshLambertMaterial({color:0xffffff,side:THREE.DoubleSide})});
  part('bun',merge([SPH(.27,7,5).translate(0,4.52,-.3),SPH(.1,5,3).scale(1.5,.5,1.5).translate(0,4.3,-.26)]),{wear:t=>t.style==='bun',paint:t=>t.hair});
  part('cap',merge([new THREE.SphereGeometry(.76,10,4,0,TAU,0,Math.PI*.5).scale(1,1.02,1).translate(0,3.93,-.03),new THREE.CylinderGeometry(.5,.5,.06,8).scale(1,1,1.1).translate(0,3.96,.6)]),{wear:t=>t.style==='cap',paint:t=>t.cap});
  part('eyes',merge([-.25,.25].map(x=>SPH(.09,5,4).scale(.9,1.3,.5).translate(x,3.68,.63))),{color:0x25272d});
  part('cheeks',merge([-.42,.42].map(x=>SPH(.11,5,3).scale(1,.62,.3).translate(x,3.5,.47))),{color:0xf2a39c});
  part('collar',new THREE.TorusGeometry(.25,.07,4,8).rotateX(Math.PI/2).translate(0,2.99,0),{color:0xf4eee0});
  part('skirt',lathe([[.5,1.82],[.56,1.7],[.66,1.45],[.76,1.14],[.74,1.08],[.001,1.08]],10),{shadow:true,wear:t=>t.skirt,paint:t=>t.skirtColor});
  part('balloon',merge([new THREE.CylinderGeometry(.016,.016,2.3,3,1,true).translate(0,1.15,0),SPH(.5,9,6).scale(1,1.18,1).translate(0,2.86,0),new THREE.ConeGeometry(.09,.14,5).translate(0,2.24,0)]),{wear:t=>t.balloon,paint:t=>t.balloonColor});
  for(const side of ['L','R']){
    part('leg'+side,new THREE.CylinderGeometry(.22,.18,1.3,7,1,true).translate(0,-.65,0),{shadow:true,paint:t=>t.skirt?t.skin:t.pants});
    part('shoe'+side,new THREE.SphereGeometry(.27,7,4).scale(1,.62,1.6),{paint:t=>t.shoe});
    part('arm'+side,merge([new THREE.CylinderGeometry(.19,.15,1.02,7,1,true).translate(0,-.51,0),SPH(.2,6,4)]),{paint:t=>t.shirt});
    part('hand'+side,SPH(.17,6,4).translate(0,-1.1,0),{paint:t=>t.skin});
  }
  const root=new THREE.Object3D(),local=new THREE.Object3D(),m=new THREE.Matrix4();root.rotation.order='YXZ';
  function set(i,x,y,z,yaw,time,moving,scale=.4){
    const T=traits[i],phase=time*T.cadence+i,stride=moving?Math.sin(phase)*(T.kid?.5:.43):0,size=scale*T.size;
    // Walkers rise a little on each step and lean into it; waiting guests sway and look around.
    root.position.set(x,y+(moving?Math.abs(Math.cos(phase))*.16*size:0),z);root.rotation.set(moving?.05:0,yaw,moving?Math.sin(phase)*.035:Math.sin(time*.8+i)*.012);root.scale.setScalar(size);root.updateMatrix();
    const put=(k,px=0,py=0,pz=0,rx=0,ry=0,rz=0,s=1)=>{local.position.set(px,py,pz);local.rotation.set(rx,ry,rz);local.scale.setScalar(s);local.updateMatrix();m.multiplyMatrices(root.matrix,local.matrix);parts[k].setMatrixAt(slots[k][i],m);};
    put('body');put('collar');if(T.skirt)put('skirt');
    const look=moving?Math.sin(time*.9+i*1.7)*.16:Math.sin(time*.45+i*2.3)*.5,hy=3*(1-T.head);
    for(const k of ['head','eyes','cheeks',T.style==='long'?'hairLong':'hair'])put(k,0,hy,0,0,look,0,T.head);
    if(T.style==='bun')put('bun',0,hy,0,0,look,0,T.head);else if(T.style==='cap')put('cap',0,hy,0,0,look,0,T.head);
    for(const [side,sign] of [['L',-1],['R',1]]){const a=stride*sign,hold=T.balloon&&sign>0,b=hold?-.5:-a*.9;
      // The supporting foot stays on the pavement; only the trailing foot lifts.
      const lift=Math.max(0,Math.sin(phase+(sign<0?Math.PI:0)))*.14*(moving?1:0);
      put('leg'+side,sign*.25,1.5,0,a);put('shoe'+side,sign*.25,.17+lift,-Math.sin(a)*1.3+.08);
      put('arm'+side,sign*.66,2.8,0,b,0,sign*.13);put('hand'+side,sign*.66,2.8,0,b,0,sign*.13);
      if(hold)put('balloon',sign*.66+.14,2.8-Math.cos(b)*1.1,-Math.sin(b)*1.1,moving?-.16:0,0,Math.sin(time*1.3+i)*.07);
    }
  }
  return {body:parts.body,head:parts.head,parts,traits,group,set,flush:()=>Object.values(parts).forEach(m=>m.instanceMatrix.needsUpdate=true)};
}
'''
s = s[:a] + NEW + s[b:]

def swap(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)

# keep-right lanes: opposite flows separate where the path is wide enough
swap('walkers.push({legs,total,phase:rand()*total,lane:(rand()-.5)*1.5});', 'walkers.push({legs,total,phase:rand()*total,lane:.18+rand()*.57});')
# step aside (to the walker's own lane side) instead of walking through someone: neighbours come from a small grid of last positions
swap('''  const o=new THREE.Object3D();
  let vFrame=0;
  islAnim.push(t=>{
    if(!walkers.length)init(); vFrame++; const half=vFrame&1;
''', '''  const o=new THREE.Object3D(),near=new Map(),nearNext=new Int16Array(NW),nearKey=(cx,cz)=>((cx+4096)<<13)|(cz+4096);
  let vFrame=0;
  islAnim.push(t=>{
    if(!walkers.length)init(); vFrame++; const half=vFrame&1;
    near.clear();for(let j=0;j<positions.length;j++){const p=positions[j];if(!p)continue;const k=nearKey(Math.floor(p[0]),Math.floor(p[1]));nearNext[j]=near.has(k)?near.get(k):-1;near.set(k,j);}
''')
swap('''      let x=l.a.x+dx*u-dz/len*off,z=l.a.z+dz*u+dx/len*off;
''', '''      let x=l.a.x+dx*u-dz/len*off,z=l.a.z+dz*u+dx/len*off;
      if(clock>=l.start+l.wait){let push=0;const cx=Math.floor(x),cz=Math.floor(z);
        for(let ax=-1;ax<=1;ax++)for(let az=-1;az<=1;az++)for(let j=near.get(nearKey(cx+ax,cz+az))??-1;j>=0;j=nearNext[j]){if(j>=i)continue;const q=positions[j],d=Math.hypot(q[0]-x,q[1]-z);if(d<.62)push=Math.max(push,.62-d);}
        if(push){push=Math.min(.4,push);x-=dz/len*push;z+=dx/len*push;}}
''')
# seated riders: same face language (larger eyes, cheeks instead of nose and mouth bar)
swap('add(g,SPH(.055,6,5),mat(0x25272b),side*.16,2.07,.41).scale.z=.4;', 'add(g,SPH(.07,6,5),mat(0x25272b),side*.17,2.05,.415).scale.set(.9,1.3,.45);add(g,SPH(.085,6,4),mat(0xf2a39c),side*.29,1.9,.335).scale.set(1,.62,.3);')
swap('add(g,SPH(.065,6,5),skin,0,1.96,.45);add(g,BOX(.15,.025,.03),mat(0x956654),0,1.83,.43,false);', '')
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
