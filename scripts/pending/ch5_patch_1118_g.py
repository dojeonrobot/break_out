# 2026-11-18 묶음 5 (사용자: 코덱스 설득 뒤에는 시뮬레이터가 아니라 실제 도로랜드 섬에서 환원하는 장면): 동굴 앞 → 코덱스가 일루아를 돌려줌 → 실제 섬 위로 흐름이
# 원천에서 섬 끝까지 번짐 → 빛이 섬 전체로 고르게 퍼져 스며듦 → 네이티가 제 빛으로 → 스토리 영상.
import io, json
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
MARK = "</style></head><body>"
rep(MARK, "body.cine #bar,body.cine #worlds,body.cine #simBtn,body.cine #sndBtn,body.cine #questPill,body.cine #credit,body.cine #board,body.cine #panel,body.cine #restoreBtn,body.cine .lbl,body.cine #info,body.cine #callPill{display:none!important}"
    "#cineBars{position:fixed;inset:0;z-index:19;pointer-events:none;opacity:0;transition:opacity .6s;background:linear-gradient(180deg,#000 0,#000 7vh,transparent 7vh,transparent calc(100% - 7vh),#000 calc(100% - 7vh))}body.cine #cineBars{opacity:1}\n" + MARK)

def story_set(key, lines):
    global s
    tag = '"%s":' % key
    assert s.count(tag) >= 1, key
    i = s.rindex(tag); j = s.index("[", i); arr, end = json.JSONDecoder().raw_decode(s[j:]); s = s[:j] + json.dumps(lines, ensure_ascii=False) + s[j + end:]; return arr
old = story_set("ending", [
 {"who": "보이드", "text": "봐. 원천에서 섬 끝까지, 일루아가 제자리로 흐르고 있어."},
 {"who": "제로", "text": "잠깐…… 이 모양, 코덱스 문양이잖아?"},
 {"who": "코덱스", "text": "……몰랐다. 우리 종족은 대대로 이 문양을 써 왔다. 어디서 온 모양인지는 전해지지 않았다."},
 {"who": "리코", "text": "이 문양은 섬에 흐르던 일루아의 모양을 본떠 만든 거예요."},
 {"who": "보이드", "text": "캠퍼스에서 직접 찍은 기록까지 모였으니까 이 모양을 찾을 수 있었어. 한 자리라도 빠져 있었다면 끝까지 이어지지 않았을 거야."}])
print("ending had", len(old))
story_set("actual", [
 {"who": "코덱스", "text": "이제 진짜 일루아를 돌려주겠다. 너희가 찾아낸 자리로."},
 {"who": "자일로", "text": "시뮬레이션에서 확인한 대로, 조금씩입니다."}])

SCENE = r"""/* ---------- the restoration on the real island (user, 2026-11-18): after Codex agrees, no simulator. At the cave mouth Codex gives the Ilua back; over the real
   park the flow runs from the source to the ends of the island, then the light spreads evenly over the whole island and sinks in; Naty's light turns back ---------- */
const RESTORED_NATY = [{who:'', nar:true, text:'붉게 흔들리던 네이티의 빛이 천천히 제 빛으로 돌아온다.'}, {who:'제로', text:'네이티! 원래 빛으로 돌아왔어!'}, {who:'코덱스', text:'……일루아가 섬으로 돌아왔다.'}];
let RESTORE_FX = null, CINE_HOLD = false;
function restoreFxBuild(){ if(RESTORE_FX) return RESTORE_FX; const root = new THREE.Group(); root.name = 'restore-fx'; root.userData.dynamic = true; root.visible = false; sceneI.add(root);
  const Y = G + 2.2, glow = (c, op)=> new THREE.MeshBasicMaterial({color:c, transparent:true, opacity:op, depthTest:false, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, fog:false});
  const band = (secs, w)=>{ const pos = [], idx = []; secs.forEach((sc, i)=>{ const hw = sc.hw*w; pos.push(sc.c[0] + sc.n[0]*hw, Y, sc.c[1] + sc.n[1]*hw, sc.c[0] - sc.n[0]*hw, Y, sc.c[1] - sc.n[1]*hw); if(i){ const k = (i - 1)*2; idx.push(k, k + 2, k + 1, k + 1, k + 2, k + 3); } });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); return g; };
  /* every stretch is drawn from its northern end: the source is at the north, the flow runs down the island */
  const T0 = {top:0, eye:2.2, bot:4.6, thorn:7.4, bar:8.2}, DUR = {top:3.2, eye:3.0, bot:3.2, thorn:1.0, bar:1.4}, parts = [];
  GLYPH.forEach(pc=>{ let secs = glyphSlice(pc); if(secs[0].c[1] > secs[secs.length - 1].c[1]) secs = secs.slice().reverse();
    const kind = pc.zone === 'final' ? 'bar' : pc.after ? 'thorn' : pc.zone === 'dl-harmonia' ? 'eye' : (pc.zone === 'dl-safari' || pc.zone === 'dl-ferris') ? 'top' : 'bot';
    const core = new THREE.Mesh(band(secs, 0.46), glow(0x8feaff, 0)), halo = new THREE.Mesh(band(secs, 1.5), glow(0x3fb8ff, 0)); core.renderOrder = 12; halo.renderOrder = 11; root.add(halo, core);
    [core, halo].forEach(m=> m.geometry.setDrawRange(0, 0)); parts.push({core, halo, n:(secs.length - 1)*6, t0:T0[kind], dur:DUR[kind], zone:pc.after || pc.zone === 'final' ? null : pc.zone, end:secs[secs.length - 1].c}); });
  /* a column of light where each zone's stretch arrives */
  const cols = MI.filter(m=> m.b).map(m=>{ const p = parts.find(x=> x.zone === m.id), c = new THREE.Mesh(new THREE.CylinderGeometry(5, 9, 150, 16, 1, true).translate(0, 75, 0), glow(0x9ff6ff, 0)); c.position.set(m.b.cx, G, m.b.cz); c.renderOrder = 12; root.add(c); return {c, at:p ? p.t0 + p.dur : 9}; });
  /* the light that spreads over the whole island and sinks in */
  const N = 1500, mp = new Float32Array(N*3), seed = []; for(let i = 0; i < N; i++){ const a = Math.random()*Math.PI*2, r = islR(a)*Math.sqrt(Math.random())*0.96; seed.push([Math.cos(a)*r, Math.sin(a)*r, Math.random(), 0.6 + Math.random()*0.8]); }
  const mg = new THREE.BufferGeometry(); mg.setAttribute('position', new THREE.BufferAttribute(mp, 3)); const motes = new THREE.Points(mg, new THREE.PointsMaterial({map:sparkTex, color:0xbff6ff, size:20, sizeAttenuation:true, transparent:true, opacity:0, depthWrite:false, depthTest:false, blending:THREE.AdditiveBlending, fog:false})); motes.renderOrder = 13; motes.frustumCulled = false; root.add(motes);
  const wash = new THREE.Mesh(new THREE.CircleGeometry(620, 64).rotateX(-Math.PI/2), glow(0x6fdcff, 0)); wash.position.set(0, G + 3, 0); wash.renderOrder = 10; root.add(wash);
  const flare = new THREE.Sprite(new THREE.SpriteMaterial({map:sparkTex, color:0xdffaff, transparent:true, opacity:0, depthTest:false, depthWrite:false, blending:THREE.AdditiveBlending, fog:false})); flare.renderOrder = 14; root.add(flare);
  const F = RESTORE_FX = {root, parts, cols, motes, wash, flare, tau:0, phase:'idle', k:0,
    /* phase 'flow': tau runs the sweep; 'hold': everything lit, breathing; 'spread': k 0..1, the lines fade while the motes rise and sink */
    step(dt){ F.tau += dt; const t = F.tau, pulse = 0.82 + 0.18*Math.sin(t*2.4);
      if(F.phase === 'flow' || F.phase === 'hold'){ parts.forEach(p=>{ const u = Math.min(1, Math.max(0, (t - p.t0)/p.dur)), e = 1 - Math.pow(1 - u, 2), n = Math.floor(p.n*e/6)*6; p.core.geometry.setDrawRange(0, n); p.halo.geometry.setDrawRange(0, n); p.core.material.opacity = 0.42*pulse; p.halo.material.opacity = 0.13*pulse; });
        cols.forEach(o=>{ o.c.material.opacity = 0.2*Math.min(1, Math.max(0, (t - o.at)/0.9))*pulse; }); }
      if(F.phase === 'spread'){ const k = F.k = Math.min(1, F.k + dt/6.0), fade = 1 - Math.min(1, k/0.55), rise = Math.min(1, k/0.6), sink = Math.max(0, (k - 0.6)/0.4);
        parts.forEach(p=>{ p.core.material.opacity = 0.42*fade; p.halo.material.opacity = 0.13*fade + 0.16*Math.sin(Math.min(1, k/0.3)*Math.PI)*fade; }); cols.forEach(o=>{ o.c.material.opacity = 0.2*fade; o.c.scale.set(1 + k*2, 1 - 0.6*k, 1 + k*2); });
        for(let i = 0; i < N; i++){ const sd = seed[i], u = Math.min(1, Math.max(0, (rise - sd[2]*0.5)/0.5)); mp[i*3] = sd[0] + Math.sin(t*0.7 + i)*3; mp[i*3 + 1] = G + 4 + u*70*sd[3] - sink*sink*78*sd[3]; mp[i*3 + 2] = sd[1] + Math.cos(t*0.6 + i)*3; } mg.attributes.position.needsUpdate = true;
        motes.material.opacity = 0.7*Math.sin(Math.min(1, k/0.25)*Math.PI/2)*(1 - sink*sink); wash.material.opacity = 0.16*Math.sin(k*Math.PI); } },
    reset(){ F.tau = 0; F.k = 0; F.phase = 'idle'; parts.forEach(p=>{ p.core.geometry.setDrawRange(0, 0); p.halo.geometry.setDrawRange(0, 0); p.core.material.opacity = p.halo.material.opacity = 0; }); cols.forEach(o=>{ o.c.material.opacity = 0; o.c.scale.set(1, 1, 1); }); motes.material.opacity = 0; wash.material.opacity = 0; flare.material.opacity = 0; },
    end: Math.max(...parts.map(p=> p.t0 + p.dur)) };
  let last = null; islAnim.push(tt=>{ const dt = last == null ? 0 : Math.min(Math.max(tt - last, 0), 0.05); last = tt; if(root.visible && F.phase !== 'idle') F.step(dt); });   /* its own capped clock: the same on a slow tablet */
  return F; }
const NATY_OWN = {flame:0x8ab6ec, face:0xe6f1fb};
function natyHeal(ms){ const fm = NATY.userData.fm, face = NATY.userData.face.material, c0 = fm.color.clone(), f0 = face.color.clone(), c1 = new THREE.Color(NATY_OWN.flame), f1 = new THREE.Color(NATY_OWN.face);
  if(!ms){ fm.color.copy(c1); fm.emissive.copy(c1); face.color.copy(f1); return Promise.resolve(); }
  return new Promise(r=>{ const t0 = performance.now(), step = ()=>{ const k = Math.min(1, (performance.now() - t0)/ms); fm.color.copy(c0).lerp(c1, k); fm.emissive.copy(fm.color); face.color.copy(f0).lerp(f1, k); if(k < 1) requestAnimationFrame(step); else r(); }; requestAnimationFrame(step); }); }
async function restoreShow(){ actBusy = true; if(walk) stopWalk(); try{ sessionStorage.setItem(`void-simdone-${progTeam()}`, '1'); }catch(e){}
  await goWorld('island'); await wait(300); if(simOn) setSim(false);
  const talk = lines=> new Promise(r=> say(lines, r)), cut = f=> new Promise(r=> fadeThrough('#05070c', ()=>{ f(); setTimeout(r, 420); }));
  if(ffOn() || reduce){ await talk(STORY.actual); await talk(STORY.ending); await natyHeal(0); actBusy = false; playRestore(); return; }
  const F = restoreFxBuild(), cast = [XYLO, ZERO, CODEX, RICO, NATY], keep = cast.map(g=> ({g, p:g.position.clone(), r:g.rotation.y, v:g.visible})), hour0 = +$('hr').value;
  const cx = cave.position.x, cz = cave.position.z, fx = Math.sin(cave.rotation.y), fz = Math.cos(cave.rotation.y);   // the cave mouth looks this way, into the island
  const stage = ()=>{ cast.forEach((g, i)=>{ const side = (i - (cast.length - 1)/2)*3.4, x = cx + fx*30 - fz*side, z = cz + fz*30 + fx*side; g.position.set(x, groundY(x, z) + (g === NATY ? 3 : 0), z); g.rotation.y = Math.atan2(fx, fz); g.visible = true; });
    camera.position.set(cx + fx*44 + fz*3, G + 4.6, cz + fz*44 - fx*3); controls.target.set(cx + fx*30, G + 3.4, cz + fz*30); };
  document.body.classList.add('cine', 'cavestory'); STAGED = true; controls.minDistance = 1; fly = null;
  /* 1. the cave mouth at dusk: Codex gives the Ilua back */
  await cut(()=>{ CINE_HOLD = true; flowHour = 19.3; $('hr').value = 19.3; updateSun(); F.reset(); F.root.visible = true; stage(); }); await wait(900);
  await talk(STORY.actual);
  const arm = CODEX.userData.armR, a0 = arm.rotation.x, eye0 = caveEye.material.color.clone(); sfx('power');
  await new Promise(r=>{ const t0 = performance.now(), step = ()=>{ const k = Math.min(1, (performance.now() - t0)/1400), e = k*k*(3 - 2*k); arm.rotation.x = a0 - 2.7*e; caveEye.material.color.copy(eye0).lerp(new THREE.Color(0x9ff6ff), e); caveEye.scale.setScalar(1 + 0.35*e);
    F.flare.position.set(CODEX.position.x, CODEX.position.y + 3.4, CODEX.position.z); F.flare.scale.setScalar(1.5 + 3.5*e); F.flare.material.opacity = 0.75*e; if(k < 1) requestAnimationFrame(step); else r(); }; requestAnimationFrame(step); });
  await wait(700);
  /* 2. over the real park: the flow runs from the source down the island */
  const src = GLYPH[0].band.secs.reduce((a, b)=> b.c[1] < a.c[1] ? b : a).c;
  await cut(()=>{ F.flare.material.opacity = 0; camera.position.set(src[0] - 40, G + 260, src[1] - 330); controls.target.set(20, G, 60); F.tau = 0; F.phase = 'flow'; sfx('sparkle'); });
  flyTo(new THREE.Vector3(20, G + 900, 700), new THREE.Vector3(20, G, -30), (F.end + 0.6)*1000); await wait((F.end + 1.0)*1000); F.phase = 'hold'; sfx('success');
  await talk(STORY.ending);
  /* 3. the light spreads evenly over the whole island and sinks in */
  F.phase = 'spread'; sfx('power'); flyTo(new THREE.Vector3(-260, G + 520, 760), new THREE.Vector3(0, G, 20), 6200); await wait(6600);
  /* 4. back at the cave: Naty's own light */
  await cut(()=>{ F.reset(); F.root.visible = false; arm.rotation.x = a0; stage(); camera.position.set(NATY.position.x + fx*8.5 - fz*1.5, NATY.position.y + 1.6, NATY.position.z + fz*8.5 + fx*1.5); controls.target.set(NATY.position.x - fz*1.6, NATY.position.y + 0.6, NATY.position.z + fx*1.6); }); await wait(700);
  sfx('sparkle'); await natyHeal(2400); await wait(300); await talk(RESTORED_NATY);
  await cut(()=>{ keep.forEach(c=>{ c.g.position.copy(c.p); c.g.rotation.y = c.r; c.g.visible = c.v; }); caveEye.material.color.copy(eye0); caveEye.scale.setScalar(1); CINE_HOLD = false; flowHour = hour0; $('hr').value = hour0; updateSun();
    document.body.classList.remove('cine', 'cavestory'); STAGED = false; controls.minDistance = 40; camera.position.copy(HOME.pos); controls.target.copy(HOME.tgt); });
  actBusy = false; playRestore(); }
window.__restoreFx = ()=> RESTORE_FX ? {phase:RESTORE_FX.phase, tau:+RESTORE_FX.tau.toFixed(1), k:+RESTORE_FX.k.toFixed(2), on:RESTORE_FX.root.visible, cine:document.body.classList.contains('cine')} : null;
"""
a = s.index("async function restoreShow(){"); b = s.index("let restoreNext = null;", a)
s = s[:a] + SCENE + s[b:]
rep("<body>", '<body><div id="cineBars" aria-hidden="true"></div>', s.count("<body>")) if False else None
i = s.index('<div id="cinema" hidden>'); s = s[:i] + '<div id="cineBars" aria-hidden="true"></div>' + s[i:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
