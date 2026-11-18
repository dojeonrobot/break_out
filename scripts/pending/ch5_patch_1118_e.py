# 2026-11-18 묶음 3-3: 연구실 입구를 숨겨진 공간으로(평범한 옹벽이 열림, 들어가는 장면), 자일로 화면은 환원 시뮬레이터가 아닌 분석 모니터,
# 잔재 셋은 모양도 부수는 방법도 다르게(도는 약점 / 때 맞춰 치기 / 화살표 순서), 부수는 동안 아래 파란 버튼 상자는 숨김.
import io, json
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
def cut(a, b, new, keep_b=True):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j if keep_b else j + len(b):]
MARK = "</style></head><body>"
CSS = (
"#labRoom{position:fixed;inset:0;z-index:33;display:none;background:#05080f;color:#dbe9f5;-webkit-user-select:none;user-select:none}#labRoom[data-on]{display:block}"
"#labRoom .in{display:grid;grid-template-rows:auto minmax(0,1fr);gap:12px;height:100%;box-sizing:border-box;padding:18px 20px 212px}"
"#labRoom header{display:flex;align-items:baseline;gap:16px}#labRoom h1{margin:0;font:700 22px var(--sans)}#lrStat{font:500 14px var(--mono);color:#8cecff}#labRoom[data-noise] #lrStat{color:#ff7a6e}"
"#labRoom .wall{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);grid-template-rows:repeat(3,minmax(0,1fr));gap:12px;min-height:0}"
"#labRoom .mon{display:grid;grid-template-rows:auto minmax(0,1fr);gap:8px;min-height:0;padding:12px 14px;border-radius:12px;background:#0a1626;border:1px solid #1e3350}#labRoom .mon.map{grid-row:1 / -1}"
"#labRoom h2{margin:0;font:600 13px var(--sans);color:#9db7c9}#lrMap,#lrSig{width:100%;height:100%;display:block}"
"#lrMap .isl{fill:#0e2233;stroke:#2f5672;stroke-width:5}#lrMap .flow{fill:#8cecff;opacity:.9}#lrMap .zone{fill:#0a1626;stroke:#5d7f97;stroke-width:4}#lrMap .zone.on{fill:#8cecff;stroke:#dffaff}#lrMap text{fill:#9db7c9;font:500 30px var(--sans);text-anchor:middle}"
"#lrMap .noise{opacity:0}#lrMap .noise circle{fill:rgba(255,90,78,.3)}#lrMap .noise path{fill:none;stroke:#ff5a4e;stroke-width:7;stroke-linejoin:round}"
"#labRoom[data-noise] #lrMap .noise{opacity:1;animation:lrFlick .26s steps(2) infinite;animation-delay:var(--d)}#labRoom[data-calm] #lrMap .noise{animation:none;opacity:0;transition:opacity 2.2s ease-out}"
"#lrMap .sweep{fill:#dffaff;opacity:0}#labRoom[data-run] #lrMap .sweep{opacity:.85;animation:lrSweep 2.4s linear both}"
"#lrMap .ping{opacity:0}#labRoom[data-ping] #lrMap .ping{opacity:1}#lrMap .ping circle{fill:none;stroke:#ffd84a;stroke-width:7;transform-box:fill-box;transform-origin:center;animation:lrPing 1.4s ease-out infinite}#lrMap .ping .dot{fill:#ffd84a;stroke:none;animation:none}"
"#lrBars{display:grid;align-content:space-evenly;gap:6px}#lrBars .row{display:grid;grid-template-columns:86px minmax(0,1fr) 62px;align-items:center;gap:10px;font:500 13px var(--sans);color:#9db7c9}#lrBars .row.on{color:#dbe9f5}"
"#lrBars i{height:10px;border-radius:5px;background:#16233a;overflow:hidden}#lrBars b{display:block;height:100%;background:#3a5068;transform-origin:left;transform:scaleX(var(--w))}#lrBars .row.on b{background:#8cecff}#lrBars em{font-style:normal;font-size:12px}"
"#labRoom[data-noise] #lrBars .row.on b{background:#ff5a4e;animation:lrJit .34s steps(3) infinite}#labRoom[data-noise] #lrBars .row.on em{color:#ff7a6e}"
"#lrSig polyline{fill:none;stroke:#8cecff;stroke-width:2;vector-effect:non-scaling-stroke}#labRoom[data-noise] #lrSig polyline{stroke:#ff5a4e}"
"#lrLog{margin:0;padding:0;list-style:none;display:grid;align-content:start;gap:8px;font:500 13px var(--sans);color:#c3d6df}#lrLog b{display:inline-block;min-width:96px;color:#f3cc91}"
"@keyframes lrFlick{50%{opacity:.25}}@keyframes lrJit{0%{transform:scaleX(.9)}50%{transform:scaleX(.45)}100%{transform:scaleX(.7)}}@keyframes lrSweep{from{transform:translateX(0)}to{transform:translateX(1480px)}}@keyframes lrPing{from{transform:scale(.3);opacity:1}to{transform:scale(1.5);opacity:0}}"
"@media (max-width:700px),(max-height:520px){#labRoom .in{padding:12px 12px 170px}#labRoom .wall{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,1fr)}#labRoom .mon:not(.map){display:none}}"
"@media (prefers-reduced-motion:reduce){#labRoom *{animation:none!important}}"
"#remPlay{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(26px + env(safe-area-inset-bottom,0px));z-index:22;display:grid;gap:10px;width:min(560px,92vw);box-sizing:border-box;padding:14px 18px 16px;border-radius:18px;background:rgba(6,17,26,.92);color:#eaf7ff;box-shadow:0 10px 30px rgba(0,0,0,.35);touch-action:manipulation;-webkit-user-select:none;user-select:none}#remPlay[hidden]{display:none}"
"#remPlay .hd{display:flex;align-items:center;justify-content:space-between;gap:12px}#remPlay .hd b{font:700 18px var(--sans)}#rpPips{display:flex;gap:6px}#rpPips i{width:14px;height:14px;border-radius:50%;box-sizing:border-box;border:2px solid #ffe14a}#rpPips i.on{background:#ffe14a}"
"#remPlay p{margin:0;font:500 15px/1.5 var(--sans);color:#bfd6ea;word-break:keep-all}#remPlay kbd{display:inline-block;padding:1px 8px;border-radius:6px;border:1px solid #9ff6ff;color:#9ff6ff;font:600 13px var(--mono)}"
"#remPlay .bar{position:relative;height:30px;border-radius:8px;background:#16233a;overflow:hidden;cursor:pointer}#remPlay .bar .zn{position:absolute;top:0;bottom:0;background:#ffe14a}#remPlay .bar .mk{position:absolute;top:-2px;bottom:-2px;width:8px;margin-left:-4px;border-radius:4px;background:#fff;box-shadow:0 0 0 2px #06111a}"
"#remPlay .seq{display:flex;gap:8px;justify-content:center}#remPlay .seq i{display:grid;place-items:center;width:46px;height:46px;border-radius:10px;border:2px solid #3a5068;font:700 24px var(--sans);font-style:normal;color:#eaf7ff}#remPlay .seq i.ok{background:#ffe14a;border-color:#ffe14a;color:#06111a}#remPlay .seq i.now{border-color:#9ff6ff}"
"#remPlay .tm{height:6px;border-radius:3px;background:#16233a;overflow:hidden}#remPlay .tm b{display:block;height:100%;background:#9ff6ff;transform-origin:left}"
"#remPlay .keys{display:flex;gap:10px;justify-content:center}#remPlay .keys button{width:60px;height:56px;border-radius:12px;border:1px solid rgba(159,246,255,.5);background:#0f1d30;color:#eaf7ff;font:700 24px var(--sans);cursor:pointer}#remPlay .keys button:active{background:#17304e;transform:scale(.97)}"
"@media (pointer:fine){#remPlay .keys{display:none}}\n")
rep(MARK, CSS + MARK)

# ---------- 1. the lab entrance: an ordinary retaining wall at the foot of the hill; a slab sinks away when the lever in the box beside it is pulled ----------
GATE = r"""function labGateBuild(){ if(labGateBuild.o) return labGateBuild.o; const FX = FERRIS_X*K, FZ = FERRIS_Z*K, A = LABG.ang*Math.PI/180, ux = Math.cos(A), uz = Math.sin(A);
  /* 2026-11-18 (user): the old bunker with its 「출입금지」 doors and warning lamps gave the place away. Now it is a stretch of the hill's retaining wall
     and a meter box, like the webtoon (ch.4 ep.6): nothing marks it, and a slab of the wall sinks out of the way only when the lever is pulled */
  const g = new THREE.Group(); g.name = 'lab-gate'; g.userData.dynamic = true; g.position.set(FX + ux*76, G, FZ + uz*76); g.rotation.y = Math.atan2(ux, uz); islRoot.add(g);
  const stone = flat(C.cliff), cap = new THREE.MeshLambertMaterial({color:0x6f6a60}), steel = new THREE.MeshLambertMaterial({color:0x59616b}), dark = new THREE.MeshBasicMaterial({color:0x04070b});
  add(g, BOX(18, 8.4, 12), stone, 0, 0, -3, false); add(g, BOX(18.8, 0.7, 12.6), cap, 0, 8.4, -3, false);
  [-1, 1].forEach(sd=> add(g, BOX(1.5, 8.4, 1.3), cap, sd*8.4, 0, 3.2, false));
  add(g, BOX(5.6, 6.9, 0.2), dark, 0, 0, 3.0, false);
  const hall = add(g, new THREE.PlaneGeometry(5.4, 6.7), new THREE.MeshBasicMaterial({map:labHallTex(), transparent:true, opacity:0}), 0, 3.4, 3.12, false);
  const slab = add(g, BOX(5.8, 7.1, 0.5), stone, 0, 0, 3.2, false);
  add(g, BOX(1.5, 2.2, 0.7), steel, 5.4, 0.9, 3.3, false); add(g, BOX(1.7, 0.16, 0.9), cap, 5.4, 3.1, 3.3, false);
  const lever = new THREE.Group(); lever.position.set(6.25, 2.2, 3.5); g.add(lever); add(lever, BOX(0.16, 0.8, 0.16), new THREE.MeshLambertMaterial({color:0x2b2f36}), 0, 0, 0, false);
  const led = add(g, SPH(0.11, 8, 6), glowMat(0x58d68d, 0.9), 4.95, 2.75, 3.68, false);
  const st = {k:0, want:false, last:null}, ez = v=>{ v = Math.min(Math.max(v, 0), 1); return v*v*(3 - 2*v); };
  const pose = ()=>{ const a = ez(st.k); slab.position.y = -7.3*a; hall.material.opacity = ez((st.k - 0.35)/0.65); lever.rotation.x = 1.1*ez(st.k/0.25); led.material.color.set(st.k > 0.02 ? 0x8cecff : 0x58d68d); };
  islAnim.push(t=>{ if(typeof RIDE_PROBE !== 'undefined' && RIDE_PROBE) return; const dt = st.last == null ? 0 : Math.min(Math.max(t - st.last, 0), 0.05); st.last = t;
    if((st.want && st.k >= 1) || (!st.want && st.k <= 0)) return; st.k = Math.min(Math.max(st.k + (st.want ? dt/LABG.out : -dt/LABG.back), 0), 1); pose(); });
  pose();
  return labGateBuild.o = {g, st, spot:[FX + ux*90, FZ + uz*90], face:[ux, uz]}; }
/* going in: the camera stands before the wall, the slab sinks, the camera walks into the dark, and `inside` is shown under the black */
async function labEnter(lines, inside){ const o = labGateBuild(), g = o.g, [ux, uz] = o.face, wx = g.position.x, wz = g.position.z;
  if(ffOn() || reduce){ await new Promise(r=> fadeThrough('#05070c', ()=>{ inside && inside(); r(); })); return; }
  STAGED = true; controls.minDistance = 1;
  flyTo(new THREE.Vector3(wx + ux*22 - uz*7, G + 5.2, wz + uz*22 + ux*7), new THREE.Vector3(wx + ux*2, G + 3.4, wz + uz*2), 1400); await wait(1600);
  if(lines && lines.length) await new Promise(r=> say(lines.slice(0, 1), r));
  o.st.want = true; sfx('open'); await wait(LABG.out*1000 + 300);
  if(lines && lines.length > 1) await new Promise(r=> say(lines.slice(1), r));
  flyTo(new THREE.Vector3(wx + ux*5.5, G + 3.2, wz + uz*5.5), new THREE.Vector3(wx - ux*8, G + 2.0, wz - uz*8), 1500); await wait(1150);
  await new Promise(r=> fadeThrough('#05070c', ()=>{ inside && inside(); r(); })); await wait(300);
  o.st.want = false; STAGED = false; controls.minDistance = 40; }
"""
cut("function labGateBuild(){ if(labGateBuild.o) return labGateBuild.o;", "window.__labGate = ", GATE)
rep("const LABG = {ang:290, near:38, out:2.4, back:1.6};", "const LABG = {ang:290, near:38, out:2.0, back:1.2};")

# ---------- 2. Xylo's screen: not the restoration simulator the child has already watched, but the analysis monitors behind it ----------
ROOM = r"""/* ---------- Xylo's lab screen (user, 2026-11-18): the restoration simulator has been running all along and the child has seen it, so the lab shows
   something else: a plan of the island with the flow, how steady each zone's flow is, the signal noise, and the earlier virtual tests ---------- */
let LABROOM = null;
function labRoom(){ if(LABROOM) return LABROOM; const d = document.createElement('div'); d.id = 'labRoom'; d.setAttribute('aria-hidden', 'true');
  d.innerHTML = '<div class="in"><header><h1>일루아 흐름 분석</h1><span id="lrStat"></span></header><div class="wall"><section class="mon map"><h2>섬 평면도</h2><svg id="lrMap" viewBox="-740 -740 1480 1480"></svg></section><section class="mon"><h2>구역별 흐름 안정도</h2><div id="lrBars"></div></section><section class="mon"><h2>신호 잡음</h2><svg id="lrSig" viewBox="0 0 300 80" preserveAspectRatio="none"><polyline points=""/></svg></section><section class="mon"><h2>가상 시험 기록</h2><ul id="lrLog"></ul></section></div></div>';
  document.body.appendChild(d); const R = LABROOM = {d, amp:0.08, iv:0, ph:0, on:[]};
  const lit = id=>{ const m = MI.find(x=> x.id === id); return !!m && zoneDone(m) && (!SIM_GATE[id] || zoneDone(MI.find(x=> x.id === SIM_GATE[id]))); };
  R.draw = ()=>{ const pts = [], P = p=> `${p[0].toFixed(0)},${p[1].toFixed(0)}`; for(let i = 0; i < 120; i++){ const a = i/120*Math.PI*2, r = islR(a); pts.push(`${(Math.cos(a)*r).toFixed(0)},${(Math.sin(a)*r).toFixed(0)}`); }
    const ids = GLYPH_ZONES.map(z=> z.id), on = R.on = ids.filter(lit), all = on.length === ids.length; let h = `<polygon class="isl" points="${pts.join(' ')}"/>`;
    GLYPH.forEach(pc=>{ const fin = pc.zone === 'final' || !!pc.after; if(fin ? !all : !on.includes(pc.zone)) return; h += `<polygon class="flow" points="${glyphOutline(glyphSlice(pc)).map(P).join(' ')}"/>`; });
    MI.forEach(m=>{ if(!m.b) return; h += `<circle class="zone${on.includes(m.id) ? ' on' : ''}" cx="${m.b.cx.toFixed(0)}" cy="${m.b.cz.toFixed(0)}" r="13"/><text x="${m.b.cx.toFixed(0)}" y="${(m.b.cz - 28).toFixed(0)}">${esc(m.name)}</text>`; });
    remSpots().forEach((sp, i)=>{ const x = sp.cx, z = sp.cz; h += `<g class="noise" style="--d:${(i*0.11).toFixed(2)}s"><circle cx="${x.toFixed(0)}" cy="${z.toFixed(0)}" r="${(REM_R*0.8).toFixed(0)}"/>` + [0, 1, 2, 3].map(k=>{ const a = k*1.57 + i, q = (r, t)=> `${(Math.cos(t)*r).toFixed(0)} ${(Math.sin(t)*r).toFixed(0)}`; return `<path d="M${x.toFixed(0)} ${z.toFixed(0)} l${q(44, a)} l${q(30, a + 1.2)} l${q(40, a - 0.7)}"/>`; }).join('') + '</g>'; });
    const f = MI.find(m=> m.id === 'dl-ferris'); if(f && f.b) h += `<g class="ping"><circle cx="${f.b.cx.toFixed(0)}" cy="${f.b.cz.toFixed(0)}" r="60"/><circle class="dot" cx="${f.b.cx.toFixed(0)}" cy="${f.b.cz.toFixed(0)}" r="13"/></g>`;
    $('lrMap').innerHTML = h + '<rect class="sweep" x="-740" y="-740" width="26" height="1480"/>';
    $('lrBars').innerHTML = ids.map(id=>{ const m = MI.find(x=> x.id === id), ok = on.includes(id); return `<div class="row${ok ? ' on' : ''}"><span>${esc(m.name)}</span><i><b style="--w:${ok ? 0.86 : 0.06}"></b></i><em>${ok ? '' : '기록 없음'}</em></div>`; }).join('');
    $('lrLog').innerHTML = '<li><b>한 번에 많이</b>시설 이상 반응</li><li><b>조금씩</b>이상 반응 감소</li>'; };
  R.tick = ()=>{ R.ph++; const n = 60; let t = ''; for(let i = 0; i <= n; i++){ const y = 40 + Math.sin(i*0.5 + R.ph*0.3)*6 + (Math.random() - 0.5)*72*R.amp; t += `${(i/n*300).toFixed(1)},${Math.max(4, Math.min(76, y)).toFixed(1)} `; } $('lrSig').firstChild.setAttribute('points', t); };
  return R; }
function labRoomNoise(on){ const R = labRoom(); R.amp = on ? 1 : 0.08; if(on) R.d.dataset.noise = '1'; else delete R.d.dataset.noise; $('lrStat').textContent = on ? '불안정한 흐름 감지' : (R.on.length ? '흐름 안정' : ''); R.d.querySelectorAll('#lrBars .row.on em').forEach(e=> e.textContent = on ? '불안정' : '안정'); }
function labRoomOpen(noise){ const R = labRoom(); R.draw(); delete R.d.dataset.ping; delete R.d.dataset.run; delete R.d.dataset.calm; labRoomNoise(!!noise); R.d.dataset.on = '1'; clearInterval(R.iv); R.iv = setInterval(R.tick, 90); R.tick(); }
const labRoomCalm = ()=> new Promise(r=>{ const R = labRoom(); if(reduce || ffOn()){ labRoomNoise(false); r(); return; } R.d.dataset.calm = '1'; sfx('powerdown'); const t0 = performance.now(), step = ()=>{ const k = Math.min(1, (performance.now() - t0)/2200); R.amp = 1 - 0.92*k; if(k < 1) requestAnimationFrame(step); else { labRoomNoise(false); delete R.d.dataset.calm; r(); } }; requestAnimationFrame(step); });
const labRoomRun = ()=> new Promise(r=>{ const R = labRoom(); $('lrStat').textContent = '다시 계산하는 중'; R.d.dataset.run = '1'; setTimeout(()=>{ delete R.d.dataset.run; $('lrStat').textContent = '계산 완료 · 흐름 안정'; $('lrLog').insertAdjacentHTML('beforeend', '<li><b>잔재 제거 뒤</b>흐름 안정</li>'); sfx('success'); r(); }, reduce || ffOn() ? 200 : 2600); });
function labRoomPing(){ labRoom().d.dataset.ping = '1'; $('lrStat').textContent = '관람차 근처에서 반응'; sfx('sparkle'); }
const labRoomClose = ()=> new Promise(r=> fadeThrough('#05070c', ()=>{ if(LABROOM){ clearInterval(LABROOM.iv); delete LABROOM.d.dataset.on; } r(); }));
window.__labRoom = ()=> LABROOM ? {on:!!LABROOM.d.dataset.on, noise:!!LABROOM.d.dataset.noise, ping:!!LABROOM.d.dataset.ping, lit:LABROOM.on.length, stat:$('lrStat').textContent} : null;
Object.assign(STORY, {labDoor:[{who:'', nar:true, text:'관람차 언덕 아래. 겉으로는 평범한 옹벽이다. 자일로가 옆에 있는 낡은 전기함의 손잡이를 내린다.'}, {who:'', nar:true, text:'벽 한쪽이 소리 없이 내려앉는다. 아래로 내려가는 계단이 보인다.'}, {who:'자일로', text:'여기는 아무에게도 알리지 않은 곳이에요. 따라오세요.'}]});
async function midCheck(q){ miniSave('mid'); actBusy = true; stopWalk(); await wait(300);
  await labEnter(STORY.labDoor, ()=> labRoomOpen(false));
  await sliceGame(ffOn() ? null : new Promise(r=> say(STORY.labGame, r))); if(ffOn()) await new Promise(r=> say(STORY.labGame, r)); await new Promise(r=> say(STORY.labGameDone, r));   /* the monitor is cleared first (user, 2026-11-13) */
  await wait(reduce ? 200 : 900);
  await new Promise(r=> say(STORY.midA, r)); await new Promise(r=> say(STORY.midA2, r)); labRoomNoise(true); sfx('powerdown'); await wait(reduce ? 400 : 2600);
  await new Promise(r=> say(STORY.midB, r)); await labRoomClose(); await wait(400);
  const cp = miniLoad() || {q:q.id}; cp.q = q.id; cp.step = 'rail'; cp.got = cp.got || []; delete cp.pos; try{ localStorage.setItem(MINI_KEY(), JSON.stringify(cp)); }catch(e){}
  actBusy = false; MCARD_NEXT = {title0:null, hint:'스카이 루프 역'}; startWalk(PAIR); }
"""
cut("async function midCheck(q){", "window.__rem = ", ROOM)
RERUN = r"""async function remRerun(){ const q = mini.q, D = STORY.remDone; actBusy = true; stopWalk(); await wait(300);
  /* 2026-11-18 (user): back in the lab the noise is still on the monitors, dies away on screen, the analysis runs again, and Xylo reads where the last record is */
  await labEnter(null, ()=> labRoomOpen(true)); await wait(reduce ? 300 : 1300);
  await labRoomCalm(); await new Promise(r=> say(D.slice(0, 1), r));
  await labRoomRun(); await new Promise(r=> say(D.slice(1, 2), r));
  labRoomPing(); await wait(reduce ? 200 : 900); await new Promise(r=> say(D.slice(2), r));
  await labRoomClose(); actBusy = false; questComplete(q); }"""
cut("async function remRerun(){", "questComplete(q); }", RERUN, keep_b=False)
# the lines that called the lab screen "the simulation run so far"
def story_set(key, lines):
    global s
    tag = '"%s":' % key
    assert s.count(tag) >= 1, key
    i = s.rindex(tag); j = s.index("[", i); arr, end = json.JSONDecoder().raw_decode(s[j:]); s = s[:j] + json.dumps(lines, ensure_ascii=False) + s[j + end:]; return arr
print("midA was", story_set("midA", [{"who": "자일로", "text": "환원 시뮬레이터가 돌아가는 동안 여기서는 흐름을 구역별로 나눠 분석하고 있었어요."}]))
print("deviceFound was", story_set("deviceFound", [{"who": "자일로", "text": "기록 두 개가 들어왔군요. 연구실에서 흐름을 자세히 분석해 보죠."}]))
old = story_set("remFirst", [{"who": "제로", "text": "찾았다! 이게 선대들이 만든 장치의 잔재야?"}, {"who": "보이드", "text": "응. 오래돼서 거의 다 망가졌는데, 신호를 내는 심장 부분만 아직 돌고 있어. 이게 자일로의 분석을 흐트러뜨려."}, {"who": "보이드", "text": "잔재마다 생김새도 부수는 방법도 달라. 화면 아래 안내를 보고 때를 맞춰 눌러."}])
print("remFirst was", [l["text"][:30] for l in old])

# ---------- 3. three remnants, three shapes, three ways to break them ----------
BUILD = r"""function remBuild(){ if(REM.models.length) return; remSpots().forEach((s, i)=>{
  const g = new THREE.Group(); g.name = 'remnant-' + i; g.userData.dynamic = true; const y0 = groundY(s.x, s.z) - 0.2; g.position.set(s.x, y0 - 7, s.z); g.visible = false; islRoot.add(g);
  /* 2026-11-18 (user): each remnant looks different. 0 a collector with three slabs, 1 a leaning pylon wound with coils, 2 a squat claw gripping the ground */
  const kind = i % 3, tone = k=> mat(k % 2 ? 0x6e7570 : 0x7b7264), ringM = ()=> mat(0x9aa0a6); let parts, core, rings, cy;
  if(kind === 0){ add(g, CYL(3.2, 3.8, 0.8, 10), mat(0x5d5f5a)); cy = 3.6;
    parts = [[-1.6, 0.8, -0.6, 0.25], [1.5, 0.9, 0.4, -0.3], [0, 1.1, 1.4, 0.1]].map(([x, y, z, r], k)=>{ const p = add(g, BOX(2.2, 2, 1.6), tone(k), x, y, z); p.rotation.z = r; return p; });
    core = add(g, new THREE.IcosahedronGeometry(0.9, 0), glowMat(0xff6a4e, 0.9), 0, cy, 0, false);
    rings = [2.4, 1.9, 1.4].map((r, k)=>{ const m = add(g, new THREE.TorusGeometry(r, 0.13, 6, 28), ringM(), 0, cy, 0, false); m.rotation.x = Math.PI/2 + k*0.5; return m; }); }
  else if(kind === 1){ add(g, CYL(2.6, 3.3, 0.8, 8), mat(0x5d5f5a)); cy = 10.4; const lean = 0.1;
    parts = [[2.0, 2.4, 3.2, 0.8], [1.5, 1.9, 3.0, 4.0], [1.0, 1.4, 2.6, 7.0]].map(([rt, rb, h, y], k)=>{ const p = add(g, CYL(rt, rb, h, 6), tone(k), -y*lean, y, 0); p.rotation.z = lean; return p; });
    core = add(g, new THREE.OctahedronGeometry(1.05, 0), glowMat(0xff6a4e, 0.9), -cy*lean, cy, 0, false);
    rings = [3.4, 6.2, 8.8].map((y, k)=>{ const m = add(g, new THREE.TorusGeometry(2.5 - k*0.5, 0.15, 6, 24), ringM(), -y*lean, y, 0, false); m.rotation.x = Math.PI/2; return m; }); }
  else { add(g, CYL(4.4, 4.9, 0.6, 10), mat(0x5d5f5a)); cy = 2.5;
    parts = [0, 1, 2, 3].map(k=>{ const a = k*Math.PI/2 + 0.4, p = add(g, BOX(1.2, 3.6, 1.2), tone(k), Math.cos(a)*3.3, 0.5, Math.sin(a)*3.3); p.rotation.set(Math.sin(a)*0.55, 0, -Math.cos(a)*0.55); return p; });
    core = add(g, new THREE.DodecahedronGeometry(1.0, 0), glowMat(0xff6a4e, 0.9), 0, cy, 0, false);
    rings = [0, 1, 2].map(k=>{ const m = add(g, new THREE.TorusGeometry(1.8 + k*0.9, 0.14, 6, 28), ringM(), 0, 0.9 + k*0.2, 0, false); m.rotation.x = Math.PI/2; return m; }); }
  REM.models.push({g, parts, core, rings, s, y0, state:0, kind, cy}); });
"""
cut("function remBuild(){ if(REM.models.length) return; remSpots().forEach((s, i)=>{", "  islAnim.push(t=> REM.models.forEach((m, i)=>{ if(m.state !== 1) return;", BUILD)

GAME = r"""/* ---------- breaking a remnant (user, 2026-11-18): a different game for each, all on timing. 0: hit the weak point as it swings to the front (Space or tap it);
   1: stop the marker inside the yellow band (Space or tap the bar); 2: press the arrows in the order shown before the time runs out.
   The blue button box at the bottom is for the ride only: it is hidden while a remnant is being broken. ---------- */
function remPlayEl(){ let el = $('remPlay'); if(el) return el; el = document.createElement('div'); el.id = 'remPlay'; el.hidden = true; el.setAttribute('role', 'group'); el.setAttribute('aria-label', '잔재 부수기');
  el.innerHTML = '<div class="hd"><b id="rpT"></b><span id="rpPips" aria-hidden="true"></span></div><p id="rpP"></p><div id="rpBody"></div>'; document.body.appendChild(el);
  el.addEventListener('pointerdown', e=>{ const G2 = REM.game; if(!G2 || G2.done) return; const k = e.target.closest('.keys button'); if(k){ e.preventDefault(); remKey(k.dataset.k); return; } if(G2.kind !== 2){ e.preventDefault(); remTap(); } }); return el; }
const REM_ARROW = {Up:'↑', Down:'↓', Left:'←', Right:'→'}, REM_TOUCH = ()=> matchMedia('(pointer:coarse)').matches;
function remPips(){ const G2 = REM.game; if(!G2) return; $('rpPips').innerHTML = Array.from({length:G2.need}, (_, k)=> `<i class="${k < G2.hits ? 'on' : ''}"></i>`).join(''); }
function remSay(t){ $('rpP').innerHTML = t; }
function remHit(G2, m){ const now = performance.now(); G2.hits++; G2.shake = now + 260; sfx('chain'); remDebris(m.core.getWorldPosition(new THREE.Vector3()), 7); remPips();
  const gone = Math.floor(G2.hits/G2.need*m.rings.length); m.rings.forEach((r, k)=>{ if(k < gone) r.visible = false; });
  if(G2.hits >= G2.need){ G2.done = true; cancelAnimationFrame(G2.raf); if(m.weak) m.weak.visible = false; remAimEl().hidden = true; remPlayEl().hidden = true; miniBox.hidden = true; miniGo.classList.remove('hot'); G2.shake = now + 700; flash(); sfx('success'); remDebris(new THREE.Vector3(m.g.position.x, m.y0 + m.cy, m.g.position.z), 26); qPop('부서졌다!'); setTimeout(()=> remFinish(G2.i), reduce ? 200 : 1100); return true; }
  return false; }
function remGame(i){ const m = REM.models[i], kind = m.kind || 0, el = remPlayEl(); remDlg(); mini.phase = 'game'; remPulse(0); miniBox.hidden = true; miniGo.classList.remove('hot'); if(m.beam) m.beam.visible = false;   /* the finding beam would wash the device out */
  const G2 = REM.game = {i, kind, hits:0, need:kind === 0 ? 6 : kind === 1 ? 5 : 3, ang:Math.random()*6.28, sp:reduce ? 1.1 : 1.7, boost:0, shake:0, tapAt:0, last:performance.now(), done:false, front:false};
  $('rpT').textContent = ['약점 치기', '때 맞춰 치기', '순서대로 누르기'][kind]; remPips(); el.hidden = false; sfx('open');
  if(kind === 0){ $('rpBody').innerHTML = ''; remSay(REM_TOUCH() ? '노란 약점이 앞으로 올 때 약점을 누르세요' : '노란 약점이 앞으로 올 때 <kbd>Space</kbd>');
    if(!m.weak){ m.weak = add(m.g, SPH(0.55, 12, 10), glowMat(0xffe14a, 0.99), 0, m.cy, 0, false); m.weak.userData.dynamic = true; } m.weak.visible = true;
    const aim = remAimEl(), wp = new THREE.Vector3();
    const loop = ()=>{ if(REM.game !== G2 || G2.done){ aim.hidden = true; return; } const now = performance.now(), dt = Math.min(0.05, (now - G2.last)/1000); G2.last = now;
      G2.ang = (G2.ang + G2.sp*(1 + G2.hits*0.16)*(G2.boost > now ? 1.7 : 1)*dt) % (Math.PI*2); const r = 2.7; m.weak.position.set(Math.cos(G2.ang)*r, m.cy + Math.sin(G2.ang*2)*0.7, Math.sin(G2.ang)*r);
      m.weak.getWorldPosition(wp); const cx = m.g.position.x, cz = m.g.position.z, cd = Math.hypot(camera.position.x - cx, camera.position.z - cz) || 1;
      G2.front = ((wp.x - cx)*(camera.position.x - cx) + (wp.z - cz)*(camera.position.z - cz))/(r*cd) > 0.25; m.weak.material.opacity = G2.front ? 0.99 : 0.22; m.weak.scale.setScalar(G2.front ? 1 + 0.25*Math.sin(now/90) : 0.6);
      wp.project(camera); aim.hidden = !G2.front || !!vn; aim.style.transform = `translate(${((wp.x + 1)/2*innerWidth).toFixed(0)}px, ${((1 - wp.y)/2*innerHeight).toFixed(0)}px) translate(-50%, -50%)`;
      G2.raf = requestAnimationFrame(loop); }; loop(); }
  else if(kind === 1){ $('rpBody').innerHTML = '<div class="bar"><div class="zn"></div><div class="mk"></div></div>'; remSay(REM_TOUCH() ? '흰 표시가 노란 칸에 들어올 때 막대를 누르세요' : '흰 표시가 노란 칸에 들어올 때 <kbd>Space</kbd>');
    const zn = el.querySelector('.zn'), mk = el.querySelector('.mk'); G2.pos = 0; G2.dir = 1; const zone = ()=>{ G2.zw = Math.max(0.1, 0.24 - G2.hits*0.03); G2.zc = 0.14 + Math.random()*0.72; zn.style.left = ((G2.zc - G2.zw/2)*100).toFixed(1) + '%'; zn.style.width = (G2.zw*100).toFixed(1) + '%'; }; G2.zone = zone; zone();
    const loop = ()=>{ if(REM.game !== G2 || G2.done) return; const now = performance.now(), dt = Math.min(0.05, (now - G2.last)/1000); G2.last = now;
      G2.pos += G2.dir*dt*(reduce ? 0.55 : 0.85 + G2.hits*0.16)*(G2.boost > now ? 1.5 : 1); if(G2.pos > 1){ G2.pos = 1; G2.dir = -1; } if(G2.pos < 0){ G2.pos = 0; G2.dir = 1; }
      G2.front = Math.abs(G2.pos - G2.zc) <= G2.zw/2; mk.style.left = (G2.pos*100).toFixed(1) + '%'; m.core.scale.setScalar(G2.front ? 1.5 : 1);
      G2.raf = requestAnimationFrame(loop); }; loop(); }
  else { const round = ()=>{ const n = 4 + G2.hits, ks = Object.keys(REM_ARROW); G2.seq = Array.from({length:n}, ()=> ks[Math.floor(Math.random()*4)]); G2.at = 0; G2.t0 = performance.now(); G2.limit = (reduce ? 9 : 5.5) + n*0.4;
      $('rpBody').innerHTML = `<div class="seq">${G2.seq.map((k, j)=> `<i class="${j === 0 ? 'now' : ''}">${REM_ARROW[k]}</i>`).join('')}</div><div class="tm"><b></b></div><div class="keys">${['Left', 'Up', 'Down', 'Right'].map(k=> `<button type="button" data-k="${k}" aria-label="${REM_ARROW[k]}">${REM_ARROW[k]}</button>`).join('')}</div>`; };
    G2.round = round; remSay(REM_TOUCH() ? '시간 안에 화살표를 순서대로 누르세요' : '시간 안에 <kbd>←↑↓→</kbd> 화살표 키를 순서대로'); round();
    const loop = ()=>{ if(REM.game !== G2 || G2.done) return; const now = performance.now(), k = 1 - (now - G2.t0)/1000/G2.limit; G2.last = now; const b = el.querySelector('.tm b'); if(b) b.style.transform = `scaleX(${Math.max(0, k).toFixed(3)})`;
      if(k <= 0 && !vn){ sfx('error'); remSay('시간이 다 됐어. 처음부터 다시!'); round(); }
      G2.raf = requestAnimationFrame(loop); }; loop(); } }
function remTap(){ const G2 = REM.game; if(!G2 || G2.done || vn || G2.kind === 2) return; const m = REM.models[G2.i], now = performance.now(); if(now - G2.tapAt < 170) return; G2.tapAt = now;
  if(!G2.front){ G2.boost = now + 800; sfx('error'); remSay(G2.kind === 0 ? '빗나갔어. 약점이 앞으로 돌아올 때 쳐' : '빗나갔어. 노란 칸에 들어올 때 쳐'); return; }
  if(remHit(G2, m)) return; remSay(`금이 갔어! 남은 타격 ${G2.need - G2.hits}`);
  if(G2.kind === 0) G2.ang += Math.PI*(0.7 + Math.random()*0.5); else G2.zone(); }
function remKey(k){ const G2 = REM.game; if(!G2 || G2.done || vn || G2.kind !== 2) return; const m = REM.models[G2.i], el = remPlayEl(), cells = el.querySelectorAll('.seq i');
  if(G2.seq[G2.at] !== k){ sfx('error'); remSay('틀렸어. 처음부터 다시!'); G2.round(); return; }
  cells[G2.at].className = 'ok'; G2.at++; sfx('tap'); if(cells[G2.at]) cells[G2.at].className = 'now';
  if(G2.at >= G2.seq.length){ if(remHit(G2, m)) return; remSay(`금이 갔어! 남은 차례 ${G2.need - G2.hits}`); G2.round(); } }
addEventListener('keydown', e=>{ const G2 = REM.game; if(!G2 || G2.done || vn) return;
  if(e.code === 'Space'){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat && G2.kind !== 2) remTap(); }
  else if(G2.kind === 2 && /^Arrow/.test(e.code)){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) remKey(e.code.slice(5)); } }, true);
window.__remWin = ()=>{ const G2 = REM.game; if(G2 && !G2.done){ G2.hits = G2.need - 1; remHit(G2, REM.models[G2.i]); } }; window.__remGame = ()=>{ const G2 = REM.game; return G2 ? {kind:G2.kind, hits:G2.hits, need:G2.need, front:G2.front, seq:G2.seq, at:G2.at, pos:G2.pos, zc:G2.zc, zw:G2.zw, done:G2.done} : null; };
"""
cut("function remGame(i){ const m = REM.models[i]; remDlg(); mini.phase = 'game'; remPulse(0);", "miniGo.addEventListener('click', ()=>{ if(REM.game && !REM.game.done) remTap(); });", GAME)
# the old pip writer drew into the hidden box
a = "function remPips(){ const G2 = REM.game; miniDots.innerHTML = G2 ? `<i class=\"on\">타격 ${G2.hits} / ${G2.need}</i>` : ''; }"
rep(a, "")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
