# 2026-11-24 사용자: 「동굴 내부 불꽃이 너무 별로, 이쁘게」
#  동굴 횃불: 각진 원뿔 하나 → 돌 받침 + 감은 나무 자루 + 겹친 불꽃(바깥 주황·안쪽 노랑·흰 심지, 부드러운 빛 덩이) + 올라가는 불티, 바람에 흔들리듯 일렁임.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b):
    global s
    if s.count(a) != 1: sys.exit(f'anchor x{s.count(a)}: {a[:80]}')
    s = s.replace(a, b)
rep("const torches = [-90, -54, -18, 18, 54, 90].map(d=>{ const a = d*Math.PI/180, x = Math.sin(a)*R*0.93, z = -Math.cos(a)*R*0.93; add(sc, CYL(0.05*H, 0.07*H, 1.5*H, 6), mat(0x5a3e28), x, 0, z, false); const fl = add(sc, CONE(0.13*H, 0.4*H, 7), glowMat(0xffa53b), x, 1.5*H, z, false); const Lt = new THREE.PointLight(0xff9a3b, 1.7, 10*H); Lt.position.set(x*0.92, 1.9*H, z*0.92); sc.add(Lt); return [Lt, fl]; });",
    "const fireTex = (()=>{ const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), gr = x.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,246,214,1)'); gr.addColorStop(0.25, 'rgba(255,196,92,0.9)'); gr.addColorStop(0.6, 'rgba(255,110,30,0.35)'); gr.addColorStop(1, 'rgba(255,80,20,0)'); x.fillStyle = gr; x.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();\n"
    "  const flameGeo = (()=>{ const pts = []; for(let i = 0; i <= 12; i++){ const t = i/12; pts.push(new THREE.Vector2(Math.sin(Math.PI*Math.pow(t, 0.7))*(1 - t*0.35), t*2.4)); } return new THREE.LatheGeometry(pts, 14); })();   /* a teardrop, not a cone */\n"
    "  const torches = [-90, -54, -18, 18, 54, 90].map((d, n)=>{ const a = d*Math.PI/180, x = Math.sin(a)*R*0.93, z = -Math.cos(a)*R*0.93, tg = new THREE.Group(); tg.position.set(x, 0, z); sc.add(tg);   /* 2026-11-24 (user: 불꽃이 별로): stone foot, a wrapped wooden pole, a layered flame with a soft glow and rising sparks */\n"
    "    add(tg, CYL(0.2*H, 0.26*H, 0.22*H, 8), flat(0x5b5148), 0, 0, 0, false); add(tg, CYL(0.045*H, 0.06*H, 1.45*H, 7), mat(0x5a3e28), 0, 0.2*H, 0, false);\n"
    "    [0.95, 1.12, 1.29].forEach(y=> add(tg, CYL(0.07*H, 0.07*H, 0.05*H, 8), mat(0x8a6a45), 0, y*H, 0, false)); add(tg, CYL(0.11*H, 0.07*H, 0.16*H, 8), mat(0x3a2a1c), 0, 1.6*H, 0, false);\n"
    "    const fl = new THREE.Group(); fl.position.y = 1.74*H; tg.add(fl);\n"
    "    const outer = new THREE.Mesh(flameGeo, new THREE.MeshBasicMaterial({color:0xff7a22, transparent:true, opacity:0.85, depthWrite:false, blending:THREE.AdditiveBlending})); outer.scale.set(0.15*H, 0.22*H, 0.15*H); fl.add(outer);\n"
    "    const inner = new THREE.Mesh(flameGeo, new THREE.MeshBasicMaterial({color:0xffd36a, transparent:true, opacity:0.95, depthWrite:false, blending:THREE.AdditiveBlending})); inner.scale.set(0.09*H, 0.15*H, 0.09*H); fl.add(inner);\n"
    "    const core = new THREE.Mesh(flameGeo, new THREE.MeshBasicMaterial({color:0xfff4d6, transparent:true, opacity:0.9, depthWrite:false})); core.scale.set(0.04*H, 0.08*H, 0.04*H); fl.add(core);\n"
    "    const glow = new THREE.Sprite(new THREE.SpriteMaterial({map:fireTex, color:0xffb060, transparent:true, opacity:0.85, depthWrite:false, blending:THREE.AdditiveBlending})); glow.scale.setScalar(1.3*H); glow.position.y = 0.22*H; fl.add(glow);\n"
    "    const NS = 14, sp = new Float32Array(NS*3), sd = Array.from({length:NS}, ()=> ({p:Math.random(), x:(Math.random() - 0.5)*0.16*H, z:(Math.random() - 0.5)*0.16*H, v:0.5 + Math.random()*0.7}));\n"
    "    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3)); const sparks = new THREE.Points(sg, new THREE.PointsMaterial({size:0.06*H, map:fireTex, color:0xffc070, transparent:true, opacity:0.9, depthWrite:false, blending:THREE.AdditiveBlending})); fl.add(sparks);\n"
    "    const Lt = new THREE.PointLight(0xff9a3b, 1.7, 10*H); Lt.position.set(x*0.92, 1.95*H, z*0.92); sc.add(Lt);\n"
    "    return {Lt, fl, outer, inner, glow, sd, sp, sg, sparks, ph:n*1.7}; });")
rep("torches.forEach(([Lt, f], n)=>{ const k = 1.0 + Math.sin(t*9 + n*3)*0.2 + Math.sin(t*23 + n)*0.1; Lt.intensity = k*1.7; f.scale.setScalar(0.9 + (k - 1)); });",
    "torches.forEach((T, n)=>{ const p = t + T.ph, k = 1.0 + Math.sin(p*9)*0.12 + Math.sin(p*23)*0.06 + Math.sin(p*3.1)*0.08; T.Lt.intensity = k*1.7;\n"
    "        T.outer.scale.y = 0.22*H*(0.9 + (k - 1)*1.6); T.inner.scale.y = 0.15*H*(0.92 + (k - 1)*1.3); T.outer.rotation.z = Math.sin(p*4.3)*0.08; T.inner.rotation.z = Math.sin(p*5.1 + 1)*0.06; T.outer.rotation.y = p*1.4; T.glow.material.opacity = 0.7 + (k - 1)*0.9; T.glow.scale.setScalar(1.3*H*(0.95 + (k - 1)*0.5));\n"
    "        T.sd.forEach((q, j)=>{ q.p += dt*q.v*0.8; if(q.p > 1){ q.p -= 1; q.x = (Math.random() - 0.5)*0.16*H; q.z = (Math.random() - 0.5)*0.16*H; } T.sp[j*3] = q.x + Math.sin(p*3 + j)*0.05*H*q.p; T.sp[j*3 + 1] = 0.2*H + q.p*0.9*H; T.sp[j*3 + 2] = q.z; }); T.sg.attributes.position.needsUpdate = true; T.sparks.material.opacity = 0.9; });")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
