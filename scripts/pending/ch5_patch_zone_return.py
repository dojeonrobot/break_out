# 보이드의 기록 — 섬 구역이 돌아올 때 연출 보강 (docs/보이드의기록_구역복귀연출_요청.txt, 2026-11-03)
# 기구마다 자기 시계(멈춤 → 가속), 전구 아래→위 점등(높이 셰이더), 주변 점등 파동·간판 한 자씩, 연출 전용 시계(dt ≤ 1/20 s)와 단계 사슬,
# 카메라 도착 + 2프레임 + 셰이더 미리 컴파일 뒤 시작. 줄 위치가 바뀌었으면 assert로 멈춤.
import io
p = 'C:/Users/dlgus/break_out/chapter05/index.html'; s = io.open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s; c = s.count(a); assert c == n, (c, a[:100]); s = s.replace(a, b)

# --- canvas textures can be redrawn later; sign textures remember their text and how many letters are lit
rep("  run(); TEXTS.push(run); return t;\n}", "  run(); TEXTS.push(run); t.userData.redraw = run; return t;\n}")
rep("""function signTex(text, {w=512, h=128, bg='#1d2f55', fg='#ffd400', size=78, dots=false, weight=700}={}){
  return canvasTex(w, h, (g)=>{""", """function signTex(text, {w=512, h=128, bg='#1d2f55', fg='#ffd400', size=78, dots=false, weight=700}={}){
  const st = {text, k:null};   // k: letters lit from the left (null = the whole sign as usual) — a ride's name lights up letter by letter when it comes back
  const t = canvasTex(w, h, (g)=>{""")
rep("""    g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.fillText(text, w/2, h/2 + (asc - desc)/2);
    if(dots){ g.fillStyle = bg; for(let x=0;x<w;x+=7) g.fillRect(x,0,2,h); for(let y=0;y<h;y+=7) g.fillRect(0,y,w,2); }
  });
}""", """    g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    if(st.k == null) g.fillText(text, w/2, h/2 + (asc - desc)/2);
    else { const ch = [...text], tw = g.measureText(text).width; let x = w/2 - tw/2; g.textAlign = 'left';
      ch.forEach((c, i)=>{ const on = i < st.k; g.globalAlpha = on ? 1 : 0.28; g.shadowColor = on ? 'rgba(255,236,170,.95)' : 'transparent'; g.shadowBlur = on ? 12 : 0;
        g.fillText(c, x, h/2 + (asc - desc)/2); x += g.measureText(c).width; });
      g.globalAlpha = 1; g.shadowBlur = 0; g.shadowColor = 'transparent'; }
    if(dots){ g.fillStyle = bg; for(let x=0;x<w;x+=7) g.fillRect(x,0,2,h); for(let y=0;y<h;y+=7) g.fillRect(0,y,w,2); }
  });
  t.userData.sign = st; return t;
}""")

# --- ride power state and clocks, right after the island missions
rep("const MI = MISSIONS_I.map(m=>({...m, twin: TWIN[m.id] || null, scans: scansFor(m.id)}));\n",
"""const MI = MISSIONS_I.map(m=>({...m, twin: TWIN[m.id] || null, scans: scansFor(m.id)}));
// ---------- ride power (2026-11-03, 구역복귀연출 요청서) ----------
// A ride whose record has not come back stands still with its lights down. Each ride runs on its own clock RIDE[id].tau, advanced in updateI by
// speed s × dt (dt capped at 1/20 s), so it can stand still and then pick up speed. uLv/uPow drive the bulb shader (bulbMat): lit below uLv.
const RIDE = {}; MI.forEach(m=>{ RIDE[m.id] = {s:0, tau:0, pow:0, on:false, chain:null, U:{uLv:{value:-1e4}, uPow:{value:0}}}; });
let RIDE_PROBE = false, RIDE_READY = false;   // batchIsland runs the animations at fixed times: every ride must move then, or its moving parts get baked
function rideClock(id, from){ for(let i = from; i < islAnim.length; i++){ const f = islAnim[i]; islAnim[i] = t=> f(RIDE_PROBE ? t : RIDE[id].tau); } }
const GATE_SIGNS = {}, SIGNS = {};
""")

# --- the five ride blocks run on their ride clock
for var, rid in [('safari', 'dl-safari'), ('harmonia', 'dl-harmonia'), ('carousel', 'dl-carousel'), ('ferris', 'dl-ferris'), ('coaster', 'dl-coaster')]:
    rep(f"\nconst {var} = new THREE.Group();\n", f"\nconst _rk_{var} = islAnim.length;   // ride clock: every animation built from here to place() below runs on RIDE['{rid}'].tau\nconst {var} = new THREE.Group();\n")
rep("\nplace(safari, -300/K, -200/K);", "\nrideClock('dl-safari', _rk_safari);\nplace(safari, -300/K, -200/K);")
rep("\nplace(harmonia, 0, 67/K);", "\nrideClock('dl-harmonia', _rk_harmonia);\nplace(harmonia, 0, 67/K);")
rep("\nplace(carousel, 135, 100);", "\nrideClock('dl-carousel', _rk_carousel);\nplace(carousel, 135, 100);")
rep("\nplace(ferris, FERRIS_X, FERRIS_Z, -0.55);", "\nrideClock('dl-ferris', _rk_ferris);\nplace(ferris, FERRIS_X, FERRIS_Z, -0.55);")
rep("\nplace(coaster, -200, 190);", "\nrideClock('dl-coaster', _rk_coaster);\nplace(coaster, -200, 190);")

# --- the carousel's gate arch registers its sign
rep("""    add(g, new THREE.PlaneGeometry(12.6, 1.5), new THREE.MeshBasicMaterial({map:signTex(name, {bg:'#9a6b45', fg:'#fff7d6', size:64, w:512, h:70}), side:THREE.DoubleSide}), 0, 6.75, 0.4, false);""",
"""    const stx = signTex(name, {bg:'#9a6b45', fg:'#fff7d6', size:64, w:512, h:70}); GATE_SIGNS[name] = stx;
    add(g, new THREE.PlaneGeometry(12.6, 1.5), new THREE.MeshBasicMaterial({map:stx, side:THREE.DoubleSide}), 0, 6.75, 0.4, false);""")

# --- batchIsland must see every ride moving
rep("  const snaps = [0, 2.71, 5.33, 8.9, 13.7, 21.3, 34.1, 47.9, 63.2, 78.5, 96.4, 117.7].map(t=>{ islAnim.forEach(f=> f(t)); return snap(); });",
    "  RIDE_PROBE = true;\n  const snaps = [0, 2.71, 5.33, 8.9, 13.7, 21.3, 34.1, 47.9, 63.2, 78.5, 96.4, 117.7].map(t=>{ islAnim.forEach(f=> f(t)); return snap(); });\n  RIDE_PROBE = false;")
rep("f(!/[?&]nobatch/.test(location.search)) batchIsland();   // ?nobatch=1 keeps every mesh separate (overlap audit)",
    "f(!/[?&]nobatch/.test(location.search)) batchIsland();   // ?nobatch=1 keeps every mesh separate (overlap audit)\nrideInit();   // after batching: the bulb shader goes on the merged materials")

# --- the sweep's clipped clones keep the bulb shader
rep("const cl = mats.map(mt=>{ const c = mt.clone(); c.clippingPlanes = planes; c.clipShadows = true; c.clipIntersection = false; return c; });",
    "const cl = mats.map(mt=>{ const c = mt.clone(); c.clippingPlanes = planes; c.clipShadows = true; c.clipIntersection = false; if(mt.userData.bulb){ c.onBeforeCompile = mt.onBeforeCompile; c.customProgramCacheKey = mt.customProgramCacheKey; } return c; });")

# --- updateI: the frame's dt (capped) moves the ride clocks and the effect chains; the restored glow follows the ride's power
rep("function updateI(now, zoneK){\n  const t = now/1000;\n  islAnim.forEach(f=> f(t));",
    "function updateI(now, zoneK){\n  const t = now/1000;\n  const dtF = Math.min(1/20, Math.max(0, t - FX_T)); FX_T = t;   // effect time: a stalled frame plays on slower, it never jumps ahead\n  for(const id in RIDE){ const R = RIDE[id]; R.tau += R.s*dtF; }\n  fxStep(dtF);\n  islAnim.forEach(f=> f(t));")
rep("const hi = (i===hovered || i===selected) ? 0.22 : 0, glow = b.restored ? 0.10 + 0.14*g : 0;",
    "const hi = (i===hovered || i===selected) ? 0.22 : 0, glow = (b.mission && RIDE[b.mission.id] ? RIDE[b.mission.id].pow : b.restored ? 1 : 0)*(0.10 + 0.14*g);")

# --- the debug sweep and arriveFx: replaced by the chain version
old_dbg = s[s.index("window.__dbg && (window.__dbg.sweep = (id, at=0.2)=>{"):]
old_dbg = old_dbg[:old_dbg.index("\n") + 1]
rep(old_dbg, "")
a0 = s.index("// A record coming back, seen in the park (not the simulator)"); a1 = s.index("// preview records on/off (this device only; stored in localStorage 'void-demo')")
s = s[:a0] + r"""// ---------- effect chains on their own clock (2026-11-03, 구역복귀연출 요청서 3절) ----------
// A chain is a list of steps; a step starts only when the one before has finished on screen. Chains advance by the frame's dt capped at 1/20 s
// (fxStep, called from updateI), so a device that stalls plays slower instead of skipping a stage. FXLOG keeps every step's start and end.
let FX_T = 0;
const FXR = new Set(), FXLOG = [];
function fxLog(r, n, ev){ FXLOG.push({c:r.name, n, ev, k:+r.clock.toFixed(2)}); if(FXLOG.length > 400) FXLOG.shift(); }
function fxChain(name, steps){ const r = {name, steps, i:-1, k:0, clock:0, side:[], dead:false}; FXR.add(r); fxNext(r); return r; }
function fxNext(r){
  const s0 = r.steps[r.i]; if(s0){ try{ s0.end && s0.end(r); }catch(e){ console.error(e); } fxLog(r, s0.n, 'end'); }
  r.i++; r.k = 0; const st = r.steps[r.i];
  if(!st){ fxKill(r, true); return; }
  fxLog(r, st.n, 'start'); try{ st.start && st.start(r); }catch(e){ console.error(e); }
}
function fxKill(r, done){
  if(r.dead) return; r.dead = true; FXR.delete(r);
  if(!done){ const st = r.steps[r.i]; try{ st && st.end && st.end(r); }catch(e){} fxLog(r, st ? st.n : '-', 'cut'); }
  r.side.forEach(f=>{ try{ f(-1); }catch(e){} }); r.side = []; if(r.onEnd) r.onEnd(done);
}
function fxStep(dt){
  FXR.forEach(r=>{
    const st = r.steps[r.i]; if(!st || r.dead) return;
    if(st.gate && !st.gate(r)) return;
    r.k += dt; r.clock += dt;
    r.side = r.side.filter(f=> f(r.clock) !== false);
    let fin = true; try{ fin = st.tick ? !!st.tick(r.k, r) : r.k >= (st.dur || 0); }catch(e){ console.error(e); }
    if(fin) fxNext(r);
  });
}
// shaders first: the clipped clones of the sweep and the new wake materials compile before the effect clock starts (a weak device stalls here, not mid-effect)
function fxCompile(r){ let fired = false; const done = ()=>{ if(!fired){ fired = true; r.ok = true; } };
  try{ if(renderer.compileAsync) renderer.compileAsync(sceneI, camera).then(done, done); else { renderer.compile(sceneI, camera); done(); } }catch(e){ done(); }
  setTimeout(done, 5000); }   // a safety only: a compile promise that never settles must not leave the ride dark
const fxFree = ()=> W.id === 'island' && !fly && !intro && !simOn && !actBusy && !vn && !walk && !$('voidVn').dataset.on && !$('recDone').dataset.on;
const fxTier = ()=> typeof perfTier === 'number' ? perfTier : 0;

// bulbs: the ride's light materials, lit from the ground up to uLv with a bright edge (uPow) where the light is climbing
function bulbMat(mt, U){
  const c = mt.clone(); c.userData.bulb = true;
  c.onBeforeCompile = sh=>{ sh.uniforms.uLv = U.uLv; sh.uniforms.uPow = U.uPow;
    sh.vertexShader = 'varying float vBy;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      vec4 bwp = vec4(transformed, 1.0);
      #ifdef USE_INSTANCING
      bwp = instanceMatrix * bwp;
      #endif
      vBy = (modelMatrix * bwp).y;`);
    sh.fragmentShader = 'uniform float uLv; uniform float uPow; varying float vBy;\n' + sh.fragmentShader.replace('#include <dithering_fragment>', `#include <dithering_fragment>
      float bOn = smoothstep(uLv + 1.4, uLv - 1.4, vBy);
      float bEdge = exp(-pow((vBy - uLv) / 1.8, 2.0)) * uPow;
      gl_FragColor.rgb = gl_FragColor.rgb * mix(0.3, 1.0, bOn) + vec3(1.0, 0.93, 0.75) * bEdge * 0.7;`); };
  c.customProgramCacheKey = ()=> 'bulbY1'; return c;
}
const ARCH_TEXT = /^(SAFARI|HARMONIA|TIMBER EXPRESS)/;
function rideInit(){
  MI.forEach(m=>{ const R = RIDE[m.id], root = m.b && m.b.mesh; if(!root) return; const cache = new Map(); R.bulbs = 0; SIGNS[m.id] = [];
    root.traverse(o=>{ if(!(o.isMesh || o.isInstancedMesh) || Array.isArray(o.material) || !o.material) return; const mt = o.material, sg = mt.map && mt.map.userData && mt.map.userData.sign;
      if(sg){ if(ARCH_TEXT.test(sg.text) && !SIGNS[m.id].includes(mt.map)) SIGNS[m.id].push(mt.map); return; }
      if(mt.type !== 'MeshBasicMaterial') return;
      let c = cache.get(mt); if(!c){ c = bulbMat(mt, R.U); cache.set(mt, c); } if(o.userData.mat === mt) o.userData.mat = c; o.material = c; R.bulbs++; });
    const gs = GATE_SIGNS[m.b.label] || GATE_SIGNS[m.name]; if(gs) SIGNS[m.id].push(gs);
    rideSet(m.id, !isVoid(m)); });
  RIDE_READY = true;
}
function signsLit(id, f){ (SIGNS[id] || []).forEach(t=>{ const st = t.userData.sign, n = [...st.text].length, k = f >= 1 ? null : Math.floor(f*n + 1e-6); if(st.k === k) return; st.k = k; t.userData.redraw(); }); }
function rideSet(id, on){ const R = RIDE[id]; if(!R) return; if(R.chain){ const c = R.chain; R.chain = null; fxKill(c, false); }
  R.on = on; R.s = on ? 1 : 0; R.pow = on ? 1 : 0; R.U.uLv.value = on ? 1e4 : -1e4; R.U.uPow.value = 0; signsLit(id, on ? 1 : 0); }
// a record that came back while no arrival effect could play (another screen, a dialogue, a walk, the simulator, the page loading it later):
// the ride powers up the next time the island is free — never "just on"
function rideSync(){
  if(!RIDE_READY) return;
  MI.forEach(m=>{ const R = RIDE[m.id]; if(!R || !m.b) return; const on = !isVoid(m);
    if(!on){ if(R.on || R.chain) rideSet(m.id, false); return; }
    if(R.on || R.chain) return;
    if(reduce) rideSet(m.id, true); else ridePowerQuiet(m); });
}
// how fast a ride turns while it starts (0 → 1): the coaster lurches then pulls away, the wheel moves one gondola at a time, the rest ease in
const RUN_SFX = {'dl-carousel':'organ', 'dl-ferris':'wheel', 'dl-coaster':'chain', 'dl-safari':'engine', 'dl-harmonia':'fountain'};
const RUN_D = id=> id === 'dl-ferris' ? 4.2 : 3.0;
function rideSpeed(id, p){ const D = RUN_D(id), e = x=> x <= 0 ? 0 : x >= 1 ? 1 : x*x*(3 - 2*x);
  if(id === 'dl-coaster') return p < 0.22 ? 1.6 : p < 0.75 ? 0 : e((p - 0.75)/(D - 0.75));
  if(id === 'dl-ferris') return p < 2.4 ? 0.9*Math.pow(Math.sin(Math.PI*p/0.8), 2) : e((p - 2.4)/(D - 2.4));
  return e(p/D); }
// the zone wakes round the ride: a ring runs out over the ground and the path tiles, the lamps and the fence line light in order of distance
function buildWake(m){
  const b = m.b, cx = b.cx, cz = b.cz, R0 = (b.r || 24), RW = Math.min(260, R0*1.6 + 60), stride = 1 + fxTier(), P = [];
  const push = (x, y, z, kind)=>{ const d = Math.hypot(x - cx, z - cz); if(d < RW) P.push([x, y, z, d, kind]); };
  (islRoot.userData.lamps || []).forEach(([x, z, hx, hy, hz])=> push(hx, hy, hz, 1));
  pathSamples.forEach(([x, z], i)=>{ if(i % stride === 0) push(x, G + 0.5, z, 0); });
  for(let i=0;i<48;i+=stride){ const a = i/48*Math.PI*2; push(cx + Math.cos(a)*(R0 + 9), G + 1.2, cz + Math.sin(a)*(R0 + 9), 2); }
  const n = P.length, pos = new Float32Array(n*3), aD = new Float32Array(n), aK = new Float32Array(n);
  P.forEach((q, i)=>{ pos[i*3] = q[0]; pos[i*3+1] = q[1]; pos[i*3+2] = q[2]; aD[i] = q[3]; aK[i] = q[4]; });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aD', new THREE.BufferAttribute(aD, 1)); g.setAttribute('aK', new THREE.BufferAttribute(aK, 1));
  const U = {uR:{value:-50}, uFade:{value:1}, uMap:{value:sparkTex}, uScale:{value:renderer.getPixelRatio()*innerHeight/2}};
  const mt = new THREE.ShaderMaterial({uniforms:U, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, fog:false,
    vertexShader:`attribute float aD; attribute float aK; uniform float uR; uniform float uFade; uniform float uScale; varying float vA; varying vec3 vC;
      void main(){ float x = uR - aD; float on = clamp(x / 6.0, 0.0, 1.0); float burst = exp(-max(x, 0.0) / 22.0); bool lamp = aK > 0.5 && aK < 1.5;
        float hold = lamp ? 0.55 : 0.12; vA = on * (burst * 0.9 + hold) * uFade;
        vC = lamp ? vec3(1.0, 0.86, 0.55) : aK > 1.5 ? vec3(1.0, 0.95, 0.7) : vec3(0.62, 0.9, 1.0);
        float sz = (lamp ? 7.0 : 4.0) * (0.6 + burst * 1.2);
        vec4 mv = modelViewMatrix * vec4(position, 1.0); gl_PointSize = vA > 0.001 ? sz * uScale / max(1.0, -mv.z) : 0.0; gl_Position = projectionMatrix * mv; }`,
    fragmentShader:`uniform sampler2D uMap; varying float vA; varying vec3 vC; void main(){ vec4 t = texture2D(uMap, gl_PointCoord); gl_FragColor = vec4(vC * t.rgb, t.a * vA); }`});
  const pts = new THREE.Points(g, mt); pts.frustumCulled = false; pts.renderOrder = 11; sceneI.add(pts);
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.94, 1, 96).rotateX(-Math.PI/2), new THREE.MeshBasicMaterial({color:0x9fe6ff, transparent:true, opacity:0, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, fog:false}));
  ring.position.set(cx, G + 0.6, cz); ring.scale.setScalar(0.01); ring.renderOrder = 11; sceneI.add(ring);
  let gone = false;
  return {U, RW, n, ring, dispose(){ if(gone) return; gone = true; sceneI.remove(pts); sceneI.remove(ring); g.dispose(); mt.dispose(); ring.geometry.dispose(); ring.material.dispose(); }};
}
function wakeStart(r, m, w){
  if(!w) { r.wakeDone = true; return true; }
  sfx('wake'); const k0 = r.clock, speed = 55, end = w.RW/speed;
  r.side.push(c=>{ if(c < 0){ w.dispose(); return false; }
    const k = c - k0, rad = k*speed;
    w.U.uR.value = rad; w.ring.scale.setScalar(Math.max(0.01, Math.min(rad, w.RW))); w.ring.material.opacity = 0.75*Math.max(0, 1 - rad/w.RW);
    signsLit(m.id, Math.min(1, k/Math.max(1.2, end*0.8)));
    const fade = Math.max(0, (k - end - 1.2)/1.6); w.U.uFade.value = 1 - Math.min(1, fade);
    if(fade >= 1){ signsLit(m.id, 1); r.wakeDone = true; w.dispose(); return false; } });
  fxLog(r, 'wake-fx', 'start'); return true;
}
// the power-up after the ride is drawn: a beat of silence, the bulbs climb, the ride starts moving, the zone wakes round it
function powerSteps(m, wake){
  const id = m.id, R = RIDE[id], b = m.b, y0 = b.y0 ?? G, top = y0 + (b.h || 40) + 4;
  return [
    {n:'hush', tick:k=> k >= 0.45},
    {n:'bulbs', start(){ sfx('bulbs'); R.U.uPow.value = 1; },
      tick(k){ const e = Math.min(1, k/1.7); R.U.uLv.value = y0 - 2 + (top - y0 + 4)*e; R.pow = e; return k >= 1.7; },
      end(){ R.U.uLv.value = 1e4; R.U.uPow.value = 0; R.pow = 1; }},
    {n:'run', start(){ sfx(RUN_SFX[id] || 'power'); },
      tick(k, r){ R.s = rideSpeed(id, k); if(k >= 0.8 && !r.waked) r.waked = wakeStart(r, m, wake()); return k >= RUN_D(id); },
      end(){ R.s = 1; }},
    {n:'wake', tick(k, r){ if(!r.waked) r.waked = wakeStart(r, m, wake()); return !!r.wakeDone; }, end(){ R.on = true; signsLit(id, 1); }}
  ];
}
function ridePowerQuiet(m){
  const R = RIDE[m.id]; let w = null;
  const steps = [{n:'ready', start(r){ w = buildWake(m); r.side.push(c=>{ if(c < 0){ w.dispose(); return false; } }); r.ok = false; r.f = 0; fxCompile(r); },
      gate:r=> fxFree() && (++r.f > 2) && r.ok, tick:()=> true},
    ...powerSteps(m, ()=> w)];
  R.chain = fxChain('power:' + m.id, steps); const me = R.chain; me.onEnd = ()=>{ if(R.chain === me) R.chain = null; };
}
// A record coming back, seen in the park (not the simulator): a beam from the sky over the zone, a shock ring on the ground, sparks rising,
// the ride drawing itself in (rideSweep) and the camera moving to watch it — then the power-up (powerSteps). One chain per zone.
function arriveFx(ids){
  if(!ids.length) return; sfx('sparkle');
  if(W.id !== 'island'){ const zs = ids.map(id=> MI.find(m=> m.id === id)).filter(Boolean); if(zs.length) toast(`${zs.map(z=> z.name).join('·')} 구역의 기록이 돌아왔습니다`); return; }   // never switch the screen on its own (user): on the campus the void says it, the island shows it when the child goes there
  if(simOn) return;   // the vein sweep is the arrival there
  const zones = ids.map(id=> MI.find(m=> m.id === id)).filter(m=> m && m.b);
  if(actBusy || vn || $('voidVn').dataset.on || $('recDone').dataset.on || walk) return;   // never during a dialogue, a scene or a walk (rideSync powers it up later)
  if(reduce){ zones.forEach(m=> rideSet(m.id, true)); toast(zones.length === 1 ? `${zones[0].name} 구역의 기록이 돌아왔습니다` : `${zones.length}개 구역의 기록이 돌아왔습니다`); return; }
  if(zones.length === 1){ const b = zones[0].b, R = (b.r || 24); flyTo(new THREE.Vector3(b.cx + R*2.6 + 90, 150 + R*1.6, b.cz + R*3.2 + 140), new THREE.Vector3(b.cx, G + 12, b.cz), 1300); }
  else flyTo(HOME.pos.clone(), HOME.tgt.clone(), 1300);
  const many = zones.length > 1, tier = fxTier();
  zones.forEach((m, i)=>{
    rideSet(m.id, false);
    const RD = RIDE[m.id], b = m.b, R = (b.r || 24), g = new THREE.Group(); g.position.set(b.cx, G, b.cz); g.visible = false; sceneI.add(g);
    const beam = add(g, CYL(R*0.3, R*0.75, 480, 20), glowMat(0x7fd9ff, 0, true), 0, 0, 0, false); beam.material.depthWrite = false; beam.renderOrder = 10;
    const beam2 = add(g, CYL(R*0.08, R*0.2, 480, 12), glowMat(0xffffff, 0, true), 0, 0, 0, false); beam2.material.depthWrite = false; beam2.renderOrder = 10;
    const rings = [0, 1, 2].map(j=>{ const r = add(g, new THREE.TorusGeometry(1, 0.035, 8, 72).rotateX(Math.PI/2), new THREE.MeshBasicMaterial({color:j ? 0x2aa7ff : 0xffffff, transparent:true, opacity:0.95, depthWrite:false, depthTest:false}), 0, 4 + j*0.3, 0, false); r.renderOrder = 10; r.visible = false; return r; });
    const flash = new THREE.Sprite(new THREE.SpriteMaterial({map:sparkTex, color:0xffffff, transparent:true, opacity:0, depthTest:false, depthWrite:false, blending:THREE.AdditiveBlending})); flash.position.y = 14; flash.renderOrder = 11; g.add(flash);
    const n = Math.round((many ? 60 : 160)/(1 + tier)), pts = new Float32Array(n*3), seeds = Array.from({length:n}, ()=> ({a:Math.random()*6.283, r:R*(0.3 + Math.random()*0.9), v:22 + Math.random()*40, w:1.2 + Math.random()*2.2, d:Math.random()*1.6}));
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pts, 3));
    const pm = new THREE.PointsMaterial({size:3.2, map:sparkTex, color:0x2aa7ff, transparent:true, opacity:0.95, depthWrite:false, sizeAttenuation:true}); const pc = new THREE.Points(pg, pm); pc.renderOrder = 11; g.add(pc);
    const life = 5.2; let sw = null, w = null;
    const beamSide = k0=> c=>{ if(c < 0) return false; const k = c - k0; if(k > life){ g.visible = false; return false; }
      beam.material.opacity = 0.32*Math.min(1, k/0.35)*Math.max(0, 1 - (k - 0.35)/2.8); beam2.material.opacity = beam.material.opacity*1.4; beam.scale.set(1 + k*0.35, 1, 1 + k*0.35); beam.rotation.y = k*0.6;
      rings.forEach((r, j)=>{ const rk = (k - j*0.7)/2.2; r.visible = rk > 0 && rk < 1; if(!r.visible) return; const ee = 1 - Math.pow(1 - rk, 3); r.scale.setScalar(1 + ee*R*3); r.material.opacity = 0.95*(1 - rk*rk); });
      flash.scale.setScalar(R*1.2 + k*R*3); flash.material.opacity = 0.7*Math.max(0, 1 - k/0.7);
      for(let j=0;j<n;j++){ const sd = seeds[j], kk = Math.max(0, k - sd.d), a = sd.a + kk*sd.w, rr = sd.r*(1 - kk*0.12); pts[j*3] = Math.cos(a)*rr; pts[j*3+1] = kk > 0 ? 1 + sd.v*kk : -50; pts[j*3+2] = Math.sin(a)*rr; }
      pg.attributes.position.needsUpdate = true; pm.opacity = 0.95*Math.max(0, 1 - k/life); };
    const steps = [
      {n:'ready', start(r){ sw = rideSweep(m, 0.35); w = buildWake(m);
          r.side.push(c=>{ if(c >= 0) return; if(sw) sw.end(); if(w) w.dispose(); sceneI.remove(g); pg.dispose(); pm.dispose(); return false; });
          r.ok = false; r.f = 0; fxCompile(r); },
        gate:r=> !fly && !intro && (++r.f > 2) && r.ok, tick:()=> true},
      {n:'wait', tick:k=> k >= i*(many ? 1.1 : 0)},
      {n:'draw', start(r){ g.visible = true; const fl = $('arrFlash'); fl.classList.remove('on'); void fl.offsetWidth; fl.classList.add('on'); r.side.push(beamSide(r.clock)); },
        tick(k){ if(sw) sw.tick(k); return k >= (sw ? sw.until : 1.2); }, end(){ if(sw) sw.end(); }},
      ...powerSteps(m, ()=> w)];
    RD.chain = fxChain('arrive:' + m.id, steps); const me = RD.chain; me.onEnd = ()=>{ if(RD.chain === me) RD.chain = null; };
  });
  toast(zones.length === 1 ? `${zones[0].name} 구역의 기록이 돌아왔습니다` : `${zones.length}개 구역의 기록이 돌아왔습니다`);
}
window.__dbg && Object.assign(window.__dbg, {
  sweep:(id)=>{ const m = MI.find(x=> x.id === id); if(!m || !m.b) return null; rideSet(id, false); arriveFx([id]); return !!RIDE[id].chain; },
  fxlog:()=> FXLOG.slice(), fxClear:()=>{ FXLOG.length = 0; },
  rideState:()=> Object.fromEntries(Object.entries(RIDE).map(([k, R])=> [k, {on:R.on, s:+R.s.toFixed(2), tau:+R.tau.toFixed(2), pow:+R.pow.toFixed(2), chain:R.chain ? R.chain.name + ':' + (R.chain.steps[R.chain.i] || {}).n : null, bulbs:R.bulbs, signs:(SIGNS[k] || []).length}])),
  rideSet:(id, on)=> rideSet(id, on)});
""" + s[a1:]

# --- rescan: rides follow the records (after arriveFx has claimed the ones it animates)
rep("  if(arriving) arriveFx(revealIds.filter(id=> MI.some(m=> m.id === id && zoneDone(m))));\n",
    "  if(arriving) arriveFx(revealIds.filter(id=> MI.some(m=> m.id === id && zoneDone(m))));\n  try{ rideSync(); }catch(e){ if(!(e instanceof ReferenceError)) throw e; }   // the rides are set up after batching, below the first rescan\n")

# --- sounds (WebAudio, no files)
rep("    case 'powerdown': tone({f:320, f2:60, type:'sawtooth', dur:.7, g:.14, lp:900}); break;",
"""    case 'powerdown': tone({f:320, f2:60, type:'sawtooth', dur:.7, g:.14, lp:900}); break;
    case 'bulbs':     for(let i = 0; i < 8; i++) tone({f:520*Math.pow(1.09, i*1.6), type:'square', t0:t + i*.2, dur:.09, g:.035, lp:2400}); tone({f:110, f2:220, type:'sawtooth', dur:1.6, a:.3, g:.05, lp:500}); break;
    case 'organ':     [0, 4, 7, 12].forEach((sv, i)=> tone({f:midiHz(60 + sv), type:'square', t0:t + i*.18, dur:1.4 - i*.18, a:.06, g:.045, lp:1800})); [0, 4, 7].forEach(sv=> tone({f:midiHz(48 + sv), type:'triangle', t0:t + .72, a:.1, dur:1.6, g:.06})); break;
    case 'chain':     noise({f0:140, f1:90, dur:.3, g:.25, q:1.2}); tone({f:70, f2:40, type:'sawtooth', dur:.25, g:.12, lp:300}); for(let i = 0; i < 12; i++) noise({t0:t + .8 + i*.12, f0:1800, f1:2200, dur:.05, g:.08, q:6}); break;
    case 'wheel':     for(let i = 0; i < 3; i++){ noise({t0:t + i*.8, f0:600, f1:400, dur:.12, g:.08, q:3}); tone({f:880 + i*110, type:'triangle', t0:t + i*.8 + .05, dur:.5, g:.06}); } break;
    case 'engine':    tone({f:55, f2:110, type:'sawtooth', dur:1.8, a:.2, g:.1, lp:400}); tone({f:82, f2:165, type:'square', dur:1.8, a:.3, g:.04, lp:300}); tone({f:660, type:'triangle', t0:t + .1, dur:.18, g:.06}); tone({f:660, type:'triangle', t0:t + .32, dur:.18, g:.06}); break;
    case 'fountain':  noise({f0:400, f1:3000, dur:1.8, a:.4, g:.1, q:.6}); [784, 988, 1175].forEach((f, i)=> tone({f, t0:t + .5 + i*.15, dur:.9, g:.05})); break;
    case 'wake':      for(let i = 0; i < 5; i++) tone({f:900 + i*180, t0:t + i*.16, a:.05, dur:.7, g:.035}); break;""")

io.open(p, 'w', encoding='utf-8', newline='').write(s); print('zone return patch ok')
