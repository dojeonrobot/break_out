# 2026-11-18 묶음 4 (사용자가 시안 그림을 보고 고른 안): 연구실 화면 = 방 뒤에서 본 모니터 벽, 연구실 입구 = 관람차 아래 기계실 장면(계단·블록 벽·철문·계기반·손잡이).
# 섬 바깥에는 언덕 발치의 표지 없는 지하 출입구 덮개만 둔다.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
def cut(a, b, new):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

# ---------- 1. CSS of the lab screen ----------
L = "#labRoom "
CSS = (
"#labRoom{--bezel:#0c1119;--scr:#081527;--ln:#1b3352;--ink:#dcebf7;--dim:#7f9bb3;--cy:#7fe9ff;--cy2:#2f8fd6;--warn:#ff5a4e;--amb:#ffc247;--ok:#58d6a4;--nk:0;position:fixed;inset:0;z-index:33;display:none;grid-template-rows:9vh minmax(0,1fr) 25vh;background:#04070d;color:var(--ink);-webkit-user-select:none;user-select:none;word-break:keep-all}#labRoom[data-on]{display:grid}"
"#labRoom .ceil{position:relative;background:linear-gradient(180deg,#02040a,#070d17)}#labRoom .ceil::before,#labRoom .ceil::after{content:'';position:absolute;bottom:22%;height:3px;width:20vw;border-radius:2px;background:#9fdcff;opacity:.5;box-shadow:0 0 26px 6px rgba(127,233,255,.3)}#labRoom .ceil::before{left:22vw}#labRoom .ceil::after{right:22vw}"
"#labRoom .back{position:relative;display:grid;min-height:0;background:linear-gradient(90deg,#03060b 0,#0a1422 11vw,#0a1422 calc(100% - 11vw),#03060b 100%)}"
"#labRoom .back::before,#labRoom .back::after{content:'';position:absolute;top:0;bottom:0;left:0;width:9vw;background:linear-gradient(90deg,#05090f,#0b1320);border-right:1px solid #152234}#labRoom .back::after{left:auto;right:0;transform:scaleX(-1)}"
"#labRoom .floor{position:relative;background:linear-gradient(180deg,#0a1626 0%,#060b13 34%,#03060a 100%);overflow:hidden}#labRoom .floor::before{content:'';position:absolute;left:12vw;right:12vw;top:0;height:46%;background:linear-gradient(180deg,rgba(127,233,255,.2),transparent);filter:blur(10px)}#labRoom[data-noise] .floor::before{background:linear-gradient(180deg,rgba(255,90,78,.2),transparent)}"
"#labRoom .desk2{position:absolute;left:16vw;right:16vw;top:34%;bottom:-2px;background:linear-gradient(180deg,#141d2b,#0a0f18);clip-path:polygon(5% 0,95% 0,100% 100%,0 100%);border-top:2px solid #26364c}"
"#labRoom .keys{position:absolute;left:14%;right:14%;top:16%;display:grid;grid-template-columns:repeat(26,1fr);gap:4px}#labRoom .keys i{height:5px;border-radius:2px;background:#1e2c40}#labRoom .keys i.on{background:var(--cy);box-shadow:0 0 8px var(--cy)}#labRoom .keys i.w{background:var(--amb)}#labRoom[data-noise] .keys i.on{background:var(--warn);box-shadow:0 0 8px var(--warn)}"
"#labRoom .wall{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr) minmax(0,1fr);gap:8px;padding:6px 12.5vw 8px;perspective:1500px;min-height:0}"
"#labRoom .col{display:grid;gap:8px;min-height:0}#labRoom .col.l,#labRoom .col.r{grid-template-rows:1fr 1fr 1fr}#labRoom .col.l{transform:rotateY(9deg);transform-origin:100% 50%}#labRoom .col.r{transform:rotateY(-9deg);transform-origin:0 50%}#labRoom .col.c{grid-template-rows:minmax(0,2.1fr) minmax(0,1fr)}"
"#labRoom .mon{position:relative;display:grid;grid-template-rows:auto minmax(0,1fr);min-height:0;border:4px solid var(--bezel);border-radius:6px;background:var(--scr);box-shadow:0 0 0 1px #1a2636,0 14px 30px -14px #000,inset 0 0 40px rgba(47,143,214,.1);overflow:hidden}"
"#labRoom .mon::after{content:'';position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 1px,transparent 1px 3px)}"
"#labRoom .mon h2{margin:0;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:4px 8px;font:600 11px var(--sans);color:var(--dim);border-bottom:1px solid var(--ln);background:rgba(11,26,46,.8)}#labRoom .mon h2 b{font:500 10px var(--mono);letter-spacing:.06em;color:var(--cy)}"
"#labRoom .body{position:relative;min-height:0;padding:6px 8px}#labRoom .body.np{padding:0}#labRoom .mon svg,#labRoom .mon canvas{display:block;width:100%;height:100%}"
"#labRoom .lst{font:600 10px var(--sans);padding:2px 8px;border-radius:999px;background:rgba(88,214,164,.14);color:var(--ok);white-space:nowrap}#labRoom[data-noise] .lst{background:rgba(255,90,78,.16);color:#ff8f85}#labRoom[data-ping] #lrSt0{background:rgba(255,194,71,.16);color:var(--amb)}"
"#lrMap .isl{fill:#0b2033;stroke:#2c5878;stroke-width:5}#lrMap .grid{stroke:rgba(127,233,255,.08);stroke-width:2}#lrMap .flow{fill:var(--cy);filter:drop-shadow(0 0 10px rgba(127,233,255,.8))}#lrMap .ghost{fill:#1a3650;opacity:.75}"
"#lrMap .z circle{fill:rgba(127,233,255,.16);stroke:var(--cy);stroke-width:3}#lrMap .z.off circle{fill:rgba(127,155,179,.08);stroke:#4d6a82;stroke-dasharray:8 8}#lrMap .z .dot{fill:var(--cy);stroke:none}#lrMap .z.off .dot{fill:#4d6a82}"
"#lrMap text{font:600 40px var(--sans);fill:#cfe3f2;text-anchor:middle;paint-order:stroke;stroke:#081527;stroke-width:9}#lrMap .z.off text{fill:#7f9bb3}"
"#lrMap .noise{opacity:var(--nk)}#lrMap .noise circle{fill:rgba(255,90,78,.22);stroke:var(--warn);stroke-width:3}#lrMap .noise path{fill:none;stroke:var(--warn);stroke-width:7;stroke-linejoin:round}#lrMap .noise text{fill:#ffb3ab;font-size:32px}#labRoom[data-noise] #lrMap .noise g{animation:lrFlick .26s steps(2) infinite}"
"#lrMap .ping{display:none}#labRoom[data-ping] #lrMap .ping{display:block}#lrMap .ping circle{fill:none;stroke:var(--amb);stroke-width:6;transform-box:fill-box;transform-origin:center;animation:lrPing 1.4s ease-out infinite}#lrMap .ping .dot{fill:var(--amb);stroke:none;animation:none}"
"#lrMap .sweep{fill:#dffaff;opacity:0}#labRoom[data-run] #lrMap .sweep{opacity:.8;animation:lrSweep 2.4s linear both}"
"#lrZl{display:grid;align-content:space-evenly;height:100%}#lrZl div{display:grid;grid-template-columns:8px minmax(0,1fr) auto;align-items:center;gap:6px;font:500 11px var(--sans)}#lrZl i{width:8px;height:8px;border-radius:50%;background:#33485e}#lrZl .ok i{background:var(--ok);box-shadow:0 0 8px var(--ok)}#lrZl .bad i{background:var(--warn);box-shadow:0 0 8px var(--warn)}"
"#lrZl em{font:500 10px var(--sans);font-style:normal;color:var(--dim)}#lrZl .ok em{color:var(--ok)}#lrZl .bad em{color:var(--warn)}#lrZl .off span{color:var(--dim)}"
"#lrBars{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;align-items:end;gap:8px;height:100%;padding-top:4px}#lrBars div{display:grid;grid-template-rows:minmax(0,1fr) auto;gap:4px;height:100%}"
"#lrBars u{align-self:end;display:block;border-radius:4px 4px 0 0;background:linear-gradient(180deg,var(--cy),var(--cy2));height:var(--h);transform-origin:50% 100%}#lrBars .off u{background:repeating-linear-gradient(45deg,#1c3148 0 5px,#12233a 5px 10px);height:14%}"
"#labRoom[data-noise] #lrBars .on u{background:linear-gradient(180deg,#ff8f85,var(--warn));animation:lrJit .5s steps(3) infinite;animation-delay:var(--d)}#lrBars span{font:500 9px var(--sans);color:var(--dim);text-align:center;white-space:nowrap}"
"#labRoom .feed{position:absolute;inset:0;background:#0a1626 url(img/tut_island.jpg) 50% 46%/118% auto no-repeat;filter:saturate(.55) hue-rotate(-8deg) brightness(.92)}#labRoom .feed::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,21,39,0),rgba(8,21,39,.55)),radial-gradient(ellipse at 50% 50%,transparent 50%,rgba(4,7,13,.7))}"
"#labRoom .tag{position:absolute;left:8px;bottom:6px;font:500 10px var(--sans);color:var(--cy);background:rgba(4,7,13,.7);padding:2px 6px;border-radius:4px}#labRoom .rec{position:absolute;right:8px;top:6px;display:flex;align-items:center;gap:5px;font:500 10px var(--mono);color:#ffb3ab}#labRoom .rec i{width:7px;height:7px;border-radius:50%;background:var(--warn);animation:lrFlick 1.2s steps(2) infinite}"
"#lrGz{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:6px;height:100%}#lrGz figure{margin:0;display:grid;grid-template-rows:minmax(0,1fr) auto;justify-items:center;min-height:0}#lrGz figcaption{font:500 10px var(--sans);color:var(--dim)}"
"#lrTl{display:grid;align-content:space-evenly;height:100%;gap:4px}#lrTl div{display:grid;grid-template-columns:74px minmax(0,1fr) 84px;align-items:center;gap:8px;font:500 11px var(--sans)}#lrTl span{color:var(--dim)}#lrTl u{display:block;height:12px;border-radius:6px;background:#13263c;position:relative;overflow:hidden}#lrTl u b{position:absolute;left:var(--a);width:var(--w);top:0;bottom:0;border-radius:6px;background:var(--c)}#lrTl em{font-style:normal}"
"@keyframes lrFlick{50%{opacity:.25}}@keyframes lrJit{0%{transform:scaleY(1)}50%{transform:scaleY(.5)}100%{transform:scaleY(.78)}}@keyframes lrSweep{from{transform:translateX(0)}to{transform:translateX(1400px)}}@keyframes lrPing{from{transform:scale(.3);opacity:1}to{transform:scale(1.5);opacity:0}}"
"@media (max-width:760px),(max-height:540px){#labRoom{grid-template-rows:4vh minmax(0,1fr) 12vh}#labRoom .wall{padding:4px 4vw 6px;gap:6px}#labRoom .col{gap:6px}#labRoom .col.l,#labRoom .col.r{grid-template-rows:1fr 1fr}#labRoom .col.l .mon:nth-child(3),#labRoom .col.r .mon:nth-child(3){display:none}#labRoom .col.c{grid-template-rows:minmax(0,1fr)}#labRoom .col.c .mon:nth-child(2){display:none}}"
"@media (max-width:560px){#labRoom .wall{grid-template-columns:minmax(0,1fr)}#labRoom .col.l,#labRoom .col.r{display:none}}"
"@media (prefers-reduced-motion:reduce){#labRoom *{animation:none!important}}"
)
cut("#labRoom{position:fixed;inset:0;z-index:33;display:none;background:#05080f", "#remPlay{position:fixed", CSS)

# ---------- 2. the lab screen itself ----------
ROOM = r"""let LABROOM = null;
function labRoom(){ if(LABROOM) return LABROOM; const d = document.createElement('div'); d.id = 'labRoom'; d.setAttribute('aria-hidden', 'true');
  const mon = (t, tag, body, cls='')=> `<section class="mon"><h2>${t}${tag}</h2><div class="body${cls}">${body}</div></section>`, lamp = (id, t)=> `<span class="lst" id="${id}">${t}</span>`;
  d.innerHTML = '<div class="ceil"></div><div class="back"><div class="wall"><div class="col l">'
    + mon('구역 상태', '<b>ZONE</b>', '<div id="lrZl"></div>') + mon('구역별 흐름 세기', lamp('lrSt1', '안정'), '<div id="lrBars"></div>') + mon('안정도 계기', '<b>GAUGE</b>', '<div id="lrGz"></div>')
    + '</div><div class="col c">' + mon('섬 평면도 · 일루아 흐름', lamp('lrSt0', '흐름 안정'), '<svg id="lrMap" viewBox="-700 -680 1400 1360" preserveAspectRatio="xMidYMid meet"></svg>') + mon('가상 시험 기록', '<b>TEST LOG</b>', '<div id="lrTl"></div>')
    + '</div><div class="col r">' + mon('섬 전경', '<b>CAM 01</b>', '<div class="feed"></div><span class="rec"><i></i>LIVE</span><span class="tag">도로랜드 섬</span>', ' np') + mon('신호 파형', lamp('lrSt2', '잡음 낮음'), '<svg id="lrWave" viewBox="0 0 300 100" preserveAspectRatio="none"></svg>') + mon('잡음 분포', '<b>NOISE MAP</b>', '<canvas id="lrHeat" width="300" height="170"></canvas>', ' np')
    + '</div></div></div><div class="floor"><div class="desk2"><div class="keys" id="lrKeys"></div></div></div>';
  document.body.appendChild(d); $('lrKeys').innerHTML = Array.from({length:78}, (_, i)=> `<i class="${(i*7) % 11 === 0 ? 'on' : (i*5) % 23 === 0 ? 'w' : ''}"></i>`).join('');
  const R = LABROOM = {d, k:0, iv:0, ph:0, on:[], tests:[]}, ids = GLYPH_ZONES.map(z=> z.id), zone = id=> MI.find(x=> x.id === id);
  const lit = id=>{ const m = zone(id); return !!m && zoneDone(m) && (!SIM_GATE[id] || zoneDone(zone(SIM_GATE[id]))); };
  const outline = (f)=>{ for(let i = 0; i <= 80; i++){ const a = i/80*Math.PI*2, r = islR(a); f(Math.cos(a)*r, Math.sin(a)*r, i); } };
  R.draw = ()=>{ const P = p=> `${p[0].toFixed(0)},${p[1].toFixed(0)}`, on = R.on = ids.filter(lit), all = on.length === ids.length; let h = '';
    for(let x = -700; x <= 700; x += 100) h += `<line class="grid" x1="${x}" y1="-680" x2="${x}" y2="680"/>`; for(let y = -600; y <= 600; y += 100) h += `<line class="grid" x1="-700" y1="${y}" x2="700" y2="${y}"/>`;
    const pts = []; outline((x, z)=> pts.push(`${x.toFixed(0)},${z.toFixed(0)}`)); h += `<polygon class="isl" points="${pts.join(' ')}"/>`;
    GLYPH.forEach(pc=>{ const fin = pc.zone === 'final' || !!pc.after, yes = fin ? all : on.includes(pc.zone); if(fin && !yes) return; h += `<polygon class="${yes ? 'flow' : 'ghost'}" points="${glyphOutline(glyphSlice(pc)).map(P).join(' ')}"/>`; });
    MI.forEach(m=>{ if(!m.b) return; const x = m.b.cx.toFixed(0), z = m.b.cz; h += `<g class="z${on.includes(m.id) ? '' : ' off'}"><circle cx="${x}" cy="${z.toFixed(0)}" r="46"/><circle class="dot" cx="${x}" cy="${z.toFixed(0)}" r="11"/><text x="${x}" y="${(z - 62).toFixed(0)}">${esc(m.name)}</text></g>`; });
    h += '<g class="noise">' + remSpots().map((sp, i)=>{ const x = sp.cx*0.82, z = sp.cz*0.82, q = (r, t)=> `${(Math.cos(t)*r).toFixed(0)} ${(Math.sin(t)*r).toFixed(0)}`;
      return `<g style="animation-delay:${(i*0.09).toFixed(2)}s"><circle cx="${x.toFixed(0)}" cy="${z.toFixed(0)}" r="74"/>` + [0, 1, 2, 3, 4].map(j=>{ const a = j*1.256 + i; return `<path d="M${x.toFixed(0)} ${z.toFixed(0)} l${q(52, a)} l${q(34, a + 1.2)} l${q(46, a - 0.7)}"/>`; }).join('') + `<text x="${x.toFixed(0)}" y="${(z + 116).toFixed(0)}">잡음</text></g>`; }).join('') + '</g>';
    const f = zone('dl-ferris'); if(f && f.b) h += `<g class="ping"><circle cx="${f.b.cx.toFixed(0)}" cy="${f.b.cz.toFixed(0)}" r="74"/><circle cx="${f.b.cx.toFixed(0)}" cy="${f.b.cz.toFixed(0)}" r="112" opacity=".5"/><circle class="dot" cx="${f.b.cx.toFixed(0)}" cy="${f.b.cz.toFixed(0)}" r="14"/></g>`;
    $('lrMap').innerHTML = h + '<rect class="sweep" x="-700" y="-680" width="26" height="1360"/>';
    $('lrBars').innerHTML = ids.map((id, i)=> `<div class="${on.includes(id) ? 'on' : 'off'}"><u style="--h:${[78, 84, 73, 80, 76][i % 5]}%;--d:${(i*0.13).toFixed(2)}s"></u><span>${esc(zone(id).name)}</span></div>`).join('');
    R.tests = [['한 번에 많이', 4, 62, '#ff5a4e', '시설 이상 반응'], ['조금씩', 22, 54, '#58d6a4', '이상 반응 감소']]; R.log(); };
  R.log = ()=>{ $('lrTl').innerHTML = R.tests.map(([n, a, w, c, r])=> `<div><span>${n}</span><u><b style="--a:${a}%;--w:${w}%;--c:${c}"></b></u><em>${r}</em></div>`).join(''); };
  R.list = bad=>{ $('lrZl').innerHTML = ids.map(id=>{ const ok = R.on.includes(id), c = !ok ? 'off' : bad ? 'bad' : 'ok'; return `<div class="${c}"><i></i><span>${esc(zone(id).name)}</span><em>${!ok ? '기록 없음' : bad ? '불안정' : '안정'}</em></div>`; }).join(''); };
  /* k: how much noise there is, 0..1. The dials, the noise map and the wave follow it, so the noise can die away on screen */
  R.level = k=>{ R.k = k; d.style.setProperty('--nk', k.toFixed(3));
    $('lrGz').innerHTML = [['흐름', 0.82 - 0.48*k, v=> v < 0.5], ['잡음', 0.12 + 0.78*k, v=> v > 0.5], ['원천', 0.7, ()=> false]].map(([n, v, bad])=>{ const a = Math.PI*(1 - v), x = 50 + Math.cos(a)*34, y = 52 - Math.sin(a)*34, c = bad(v) ? '#ff5a4e' : '#7fe9ff';
      return `<figure><svg viewBox="0 0 100 62"><path d="M12 52 A38 38 0 0 1 88 52" fill="none" stroke="#16304a" stroke-width="9" stroke-linecap="round"/><path d="M12 52 A38 38 0 0 1 88 52" fill="none" stroke="${c}" stroke-width="9" stroke-linecap="round" stroke-dasharray="${(v*119.4).toFixed(1)} 200"/><line x1="50" y1="52" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#dcebf7" stroke-width="3" stroke-linecap="round"/><circle cx="50" cy="52" r="4.5" fill="#dcebf7"/></svg><figcaption>${n}</figcaption></figure>`; }).join('');
    const cv = $('lrHeat'), g = cv.getContext('2d'), W = cv.width, H = cv.height, sc = Math.min(W, H)/1500, X = x=> W/2 + x*sc*1.25, Y = z=> H/2 + z*sc;
    const blob = (x, y, r, c0, c1)=>{ const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, c0); gr.addColorStop(1, c1); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); };
    const path = ()=>{ g.beginPath(); outline((x, z, i)=> i ? g.lineTo(X(x), Y(z)) : g.moveTo(X(x), Y(z))); g.closePath(); };
    g.fillStyle = '#081a2c'; g.fillRect(0, 0, W, H); g.save(); path(); g.clip(); g.fillStyle = '#0d3050'; g.fillRect(0, 0, W, H);
    R.on.forEach(id=>{ const m = zone(id); if(m && m.b) blob(X(m.b.cx), Y(m.b.cz), 54, 'rgba(60,170,210,.5)', 'rgba(60,170,210,0)'); });
    if(k > 0.01) remSpots().forEach(sp=>{ const x = X(sp.cx*0.82), y = Y(sp.cz*0.82); blob(x, y, 46, `rgba(255,196,71,${(0.95*k).toFixed(2)})`, 'rgba(255,90,78,0)'); blob(x, y, 22, `rgba(255,70,60,${k.toFixed(2)})`, 'rgba(255,90,78,0)'); });
    g.restore(); g.strokeStyle = 'rgba(127,233,255,.5)'; g.lineWidth = 1.5; path(); g.stroke(); };
  R.tick = ()=>{ R.ph++; const n = 90, k = R.k, c = k > 0.5 ? '#ff5a4e' : '#7fe9ff'; let p = '', grid = ''; for(let y = 20; y < 100; y += 20) grid += `<line x1="0" y1="${y}" x2="300" y2="${y}" stroke="rgba(127,233,255,.1)" vector-effect="non-scaling-stroke"/>`;
    for(let i = 0; i <= n; i++){ const y = 50 + Math.sin(i*0.32 + R.ph*0.25)*10 + Math.sin(i*0.11 + R.ph*0.08)*7 + (Math.random() - 0.5)*(6 + 68*k); p += `${i ? 'L' : 'M'}${(i/n*300).toFixed(1)} ${Math.max(6, Math.min(94, y)).toFixed(1)} `; }
    $('lrWave').innerHTML = grid + `<path d="${p} L300 100 L0 100 Z" fill="${c}" opacity=".12"/><path d="${p}" fill="none" stroke="${c}" stroke-width="2" vector-effect="non-scaling-stroke"/>`; };
  return R; }
function labRoomNoise(on){ const R = labRoom(); if(on) R.d.dataset.noise = '1'; else delete R.d.dataset.noise; R.level(on ? 1 : 0); R.list(!!on); $('lrSt0').textContent = on ? '불안정한 흐름 감지' : '흐름 안정'; $('lrSt1').textContent = on ? '불안정' : '안정'; $('lrSt2').textContent = on ? '잡음 높음' : '잡음 낮음'; }
function labRoomOpen(noise){ const R = labRoom(); R.draw(); delete R.d.dataset.ping; delete R.d.dataset.run; labRoomNoise(!!noise); R.d.dataset.on = '1'; clearInterval(R.iv); R.iv = setInterval(R.tick, 110); R.tick(); }
const labRoomCalm = ()=> new Promise(r=>{ const R = labRoom(); if(reduce || ffOn()){ labRoomNoise(false); r(); return; } sfx('powerdown'); const t0 = performance.now(), step = ()=>{ const k = Math.min(1, (performance.now() - t0)/2400); R.level((1 - k)*(1 - k)); if(k < 1) requestAnimationFrame(step); else { labRoomNoise(false); r(); } }; requestAnimationFrame(step); });
const labRoomRun = ()=> new Promise(r=>{ const R = labRoom(); $('lrSt0').textContent = '다시 계산하는 중'; R.d.dataset.run = '1'; setTimeout(()=>{ delete R.d.dataset.run; $('lrSt0').textContent = '계산 완료 · 흐름 안정'; R.tests.push(['잔재 제거 뒤', 48, 46, '#7fe9ff', '흐름 안정']); R.log(); sfx('success'); r(); }, reduce || ffOn() ? 200 : 2600); });
function labRoomPing(){ labRoom().d.dataset.ping = '1'; $('lrSt0').textContent = '관람차 근처에서 반응'; sfx('sparkle'); }
const labRoomClose = ()=> new Promise(r=> fadeThrough('#05070c', ()=>{ if(LABROOM){ clearInterval(LABROOM.iv); delete LABROOM.d.dataset.on; } r(); }));
window.__labRoom = ()=> LABROOM ? {on:!!LABROOM.d.dataset.on, noise:!!LABROOM.d.dataset.noise, ping:!!LABROOM.d.dataset.ping, lit:LABROOM.on.length, stat:$('lrSt0').textContent, k:+LABROOM.k.toFixed(2), tests:LABROOM.tests.length} : null;
"""
cut("let LABROOM = null;", "Object.assign(STORY, {labDoor:", ROOM)
a = s.index("Object.assign(STORY, {labDoor:"); b = s.index("\n", a)
s = s[:a] + "Object.assign(STORY, {labDoor:[{who:'', nar:true, text:'관람차 아래로 내려가는 계단 끝. 철골과 톱니 사이에 낡은 기계실 문이 하나 있다.'}, {who:'', nar:true, text:'자일로가 계기반 옆 손잡이를 내리자 톱니가 돌고, 철문이 옆으로 밀려 들어간다.'}, {who:'자일로', text:'여기는 아무에게도 알리지 않은 곳이에요. 따라오세요.'}]});" + s[b:]

# ---------- 3. the entrance: outside only an unmarked cellar hatch at the foot of the hill; the way in is a scene of its own under the wheel ----------
GATE = r"""function labGateBuild(){ if(labGateBuild.o) return labGateBuild.o; const FX = FERRIS_X*K, FZ = FERRIS_Z*K, A = LABG.ang*Math.PI/180, ux = Math.cos(A), uz = Math.sin(A);
  /* 2026-11-18 (user, from the mock-ups): nothing here says "lab". At the foot of the hill there is only a low cellar hatch with no sign; the way in is played as a
     scene under the wheel (labSet), like the webtoon (ch.4 ep.6) */
  const g = new THREE.Group(); g.name = 'lab-gate'; g.userData.dynamic = true; g.position.set(FX + ux*79, G, FZ + uz*79); g.rotation.y = Math.atan2(ux, uz); islRoot.add(g);
  const conc = new THREE.MeshLambertMaterial({color:0x7c817c}), hatch = new THREE.MeshLambertMaterial({color:0x55605a}), dark = new THREE.MeshLambertMaterial({color:0x2c322f});
  [-1, 1].forEach(sd=> add(g, BOX(0.5, 2.3, 6.2), conc, sd*2.2, 0, 2.9, false)); add(g, BOX(4.9, 2.5, 0.6), conc, 0, 0, -0.1, false);
  const lid = new THREE.Group(); lid.position.set(0, 1.25, 2.9); lid.rotation.x = 0.36; g.add(lid);
  [-1, 1].forEach(sd=>{ add(lid, new THREE.BoxGeometry(1.92, 0.16, 6.4), hatch, sd*0.99, 0, 0, false); add(lid, new THREE.BoxGeometry(0.1, 0.12, 0.9), dark, sd*0.3, 0.14, 1.6, false); });
  add(lid, new THREE.BoxGeometry(0.06, 0.18, 6.4), dark, 0, 0, 0, false);
  return labGateBuild.o = {g, st:{k:0}, spot:[FX + ux*91, FZ + uz*91], face:[ux, uz]}; }
/* ---------- the machine level under the wheel: stairs down on the left, a block wall, a steel door with a mesh window, the control cabinet, the lever and its gears.
   Pulling the lever turns the gears and the door slides into the wall; behind it a ladder and a cold light ---------- */
let LABSET = null, labKeep = null;
function labSet(){ if(LABSET) return LABSET; const scene = new THREE.Scene(), k = Math.max(0.2, 14*(ZERO.scale.y || 0.15)/3.9), S = new THREE.Group(); S.scale.setScalar(k); scene.add(S);
  scene.background = new THREE.Color(0x05080d); scene.fog = new THREE.Fog(0x05080d, 22*k, 48*k);
  const lam = c=> new THREE.MeshLambertMaterial({color:c}), fl = c=> new THREE.MeshLambertMaterial({color:c, flatShading:true}), bas = c=> new THREE.MeshBasicMaterial({color:c});
  const put = (p, g, m, x=0, y=0, z=0)=>{ const o = new THREE.Mesh(g, m); o.position.set(x, y, z); p.add(o); return o; };
  const B = (w, h, d)=> new THREE.BoxGeometry(w, h, d), C = (a, b, h, n=14)=> new THREE.CylinderGeometry(a, b, h, n);
  const tex = (w, h, draw, rx=1, ry=1)=>{ const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); return t; };
  const DX = 2.4, DW = 2.6, DH = 4.6;
  put(S, new THREE.PlaneGeometry(54, 36).rotateX(-Math.PI/2), new THREE.MeshLambertMaterial({map:tex(256, 256, (g, w, h)=>{ g.fillStyle = '#2a323d'; g.fillRect(0, 0, w, h); g.strokeStyle = '#161b22'; g.lineWidth = 6; g.strokeRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,.03)'; g.fillRect(8, 8, w - 16, 60); }, 9, 6)}), 0, 0, 9);
  const wall = new THREE.MeshLambertMaterial({map:tex(512, 256, (g, w, h)=>{ g.fillStyle = '#8b939c'; g.fillRect(0, 0, w, h); g.strokeStyle = '#5f6770'; g.lineWidth = 5; for(let r = 0; r < 4; r++){ const y = r*64; g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); for(let c = 0; c < 4; c++){ const x = c*128 + (r % 2 ? 64 : 0); g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 64); g.stroke(); } } g.fillStyle = 'rgba(0,0,0,.06)'; for(let i = 0; i < 40; i++) g.fillRect((i*97) % w, (i*53) % h, 30, 8); }, 5, 2)});
  put(S, B(DX - DW/2 + 15, 7.6, 0.8), wall, (DX - DW/2 - 15)/2, 3.8, 0); put(S, B(15, 7.6, 0.8), wall, DX + DW/2 + 7.5, 3.8, 0); put(S, B(DW, 7.6 - DH, 0.8), wall, DX, DH + (7.6 - DH)/2, 0);
  const corr = new THREE.MeshLambertMaterial({map:tex(64, 64, (g, w, h)=>{ g.fillStyle = '#6d757e'; g.fillRect(0, 0, w, h); g.fillStyle = '#4c545d'; for(let x = 0; x < w; x += 16) g.fillRect(x, 0, 7, h); }, 14, 1)});
  [[(DX - DW/2 - 15)/2, DX - DW/2 + 15], [DX + DW/2 + 7.5, 15]].forEach(([x, w])=> put(S, B(w, 1.5, 0.12), corr, x, 0.75, 0.46)); put(S, B(40, 0.5, 1.6), lam(0x59616b), 0, 7.85, 0.2);
  S.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([[7.6, 7.4], [7.3, 6.3], [7.7, 5.4], [7.2, 4.5], [7.5, 3.7], [7.1, 2.9]].map(([x, y])=> new THREE.Vector3(x, y, 0.42))), new THREE.LineBasicMaterial({color:0x2a2f36})));
  const frame = lam(0x4a525c); put(S, B(0.3, DH + 0.3, 1.0), frame, DX - DW/2 - 0.15, (DH + 0.3)/2, 0.05); put(S, B(0.3, DH + 0.3, 1.0), frame, DX + DW/2 + 0.15, (DH + 0.3)/2, 0.05); put(S, B(DW + 0.6, 0.3, 1.0), frame, DX, DH + 0.15, 0.05);
  const door = put(S, B(DW, DH, 0.24), new THREE.MeshLambertMaterial({map:tex(256, 512, (g, w, h)=>{ g.fillStyle = '#7b848d'; g.fillRect(0, 0, w, h); g.strokeStyle = '#5a626b'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, h - 20); g.fillStyle = '#1b2026'; g.fillRect(70, 70, 116, 110); g.strokeStyle = '#59616a'; g.lineWidth = 2; for(let i = 0; i <= 116; i += 12){ g.beginPath(); g.moveTo(70 + i, 70); g.lineTo(70 + i, 180); g.stroke(); } for(let i = 0; i <= 110; i += 12){ g.beginPath(); g.moveTo(70, 70 + i); g.lineTo(186, 70 + i); g.stroke(); } g.fillStyle = '#3d444c'; g.fillRect(196, 250, 22, 70); g.fillStyle = 'rgba(120,70,30,.25)'; g.fillRect(14, 420, 228, 80); })}), DX, DH/2, 0.12);
  put(S, B(1.5, 0.48, 0.08), new THREE.MeshBasicMaterial({map:tex(256, 80, (g, w, h)=>{ g.fillStyle = '#e9ecef'; g.fillRect(0, 0, w, h); g.strokeStyle = '#c8362e'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8); g.fillStyle = '#c8362e'; g.font = '700 46px "IBM Plex Sans KR","Malgun Gothic",sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('출입금지', w/2, h/2 + 2); })}), DX, DH + 0.85, 0.45);
  put(S, B(DW, DH, 0.1), bas(0x020406), DX, DH/2, -0.5);
  { const lad = new THREE.Group(); lad.position.set(DX - 0.4, 0, -0.3); S.add(lad); [-0.35, 0.35].forEach(x=> put(lad, B(0.08, DH, 0.08), bas(0x1f3a52), x, DH/2, 0)); for(let y = 0.4; y < DH; y += 0.5) put(lad, B(0.7, 0.06, 0.06), bas(0x2c5878), 0, y, 0);
    put(S, new THREE.PlaneGeometry(DW, DH*0.7), new THREE.MeshBasicMaterial({map:tex(64, 128, (g, w, h)=>{ const gr = g.createLinearGradient(0, h, 0, 0); gr.addColorStop(0, 'rgba(127,233,255,.85)'); gr.addColorStop(1, 'rgba(127,233,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }), transparent:true, depthWrite:false}), DX, DH*0.35, -0.42); }
  const pan = new THREE.MeshLambertMaterial({map:tex(256, 256, (g, w, h)=>{ g.fillStyle = '#3b434c'; g.fillRect(0, 0, w, h); g.strokeStyle = '#22272e'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8);
    [[58, 56], [198, 56]].forEach(([x, y])=>{ g.fillStyle = '#d9d4c2'; g.beginPath(); g.arc(x, y, 30, 0, 7); g.fill(); g.strokeStyle = '#22272e'; g.lineWidth = 4; g.stroke(); g.beginPath(); g.moveTo(x, y); g.lineTo(x + 16, y - 18); g.stroke(); });
    for(let r = 0; r < 3; r++) for(let c = 0; c < 8; c++){ g.fillStyle = (r*8 + c) % 5 === 0 ? '#c8362e' : (r*8 + c) % 7 === 0 ? '#58d68d' : '#1c2127'; g.fillRect(22 + c*27, 110 + r*30, 18, 20); }
    [[60, 222], [128, 222], [196, 222]].forEach(([x, y])=>{ g.fillStyle = '#1c2127'; g.beginPath(); g.arc(x, y, 14, 0, 7); g.fill(); }); })}), side = lam(0x2f363e);
  put(S, B(1.9, 2.3, 0.5), [side, side, side, side, pan, side], DX - DW/2 - 1.6, 2.35, 0.62);
  [-0.5, 0, 0.5].forEach((dx, i)=>{ const c = new THREE.CatmullRomCurve3([new THREE.Vector3(DX - DW/2 - 1.6 + dx, 1.2, 0.7), new THREE.Vector3(DX - DW/2 - 1.6 + dx*1.6, 0.5, 1.0 + i*0.2), new THREE.Vector3(DX - DW/2 - 2.4 + dx*2, 0.06, 1.5 + i*0.3), new THREE.Vector3(DX - DW/2 - 4 + dx, 0.06, 1.3)]); put(S, new THREE.TubeGeometry(c, 20, 0.05, 6), lam(0x15191e)); });
  const mech = new THREE.Group(); mech.position.set(DX - DW/2 - 0.42, 2.6, 0.5); S.add(mech); put(mech, B(0.5, 1.5, 0.16), lam(0x343b43));
  const gears = [[0, 0.42, 0.24], [0.12, -0.2, 0.17]].map(([x, y, r])=>{ const gg = put(mech, C(r, r, 0.08, 12).rotateX(Math.PI/2), lam(0x8a6a3a), x, y, 0.12); for(let j = 0; j < 8; j++){ const a = j/8*Math.PI*2; put(gg, B(0.07, 0.07, 0.08), lam(0x8a6a3a), Math.cos(a)*r, Math.sin(a)*r, 0); } return gg; });
  const lever = new THREE.Group(); lever.position.set(-0.06, -0.45, 0.16); mech.add(lever); put(lever, C(0.035, 0.035, 0.6, 6).translate(0, 0.3, 0), lam(0x1c2127)); put(lever, new THREE.SphereGeometry(0.08, 8, 6), lam(0xc8362e), 0, 0.62, 0);
  { const st = new THREE.Group(); st.position.set(-8.4, 0, 1.4); S.add(st); const N = 13; for(let i = 0; i < N; i++) put(st, B(4.4, 0.36, 0.62), lam(i % 2 ? 0x3a424c : 0x424a55), 0, 0.18 + i*0.36, -i*0.62 + 6.4);
    [-2.25, 2.25].forEach(x=>{ const r = put(st, B(0.09, 0.09, 9.6), lam(0x232830), x, 3.6, 2.7); r.rotation.x = Math.atan2(0.36, 0.62); for(let i = 0; i < N; i += 2) put(st, B(0.07, 1.25, 0.07), lam(0x232830), x, 0.36 + i*0.36 + 0.62, -i*0.62 + 6.4); });
    put(st, B(5.2, 0.3, 3.4), lam(0x2c333c), 0, N*0.36, -N*0.62 + 5.0); }
  const steel = fl(0x1d232b); for(let x = -14; x <= 14; x += 7) put(S, B(0.6, 0.9, 30), steel, x, 9.1, 10); for(let z = 2; z <= 20; z += 6) put(S, B(40, 0.5, 0.6), steel, 0, 9.4, z);
  [[-4, 0.3], [9, -0.25]].forEach(([x, r])=>{ put(S, B(0.5, 12, 0.5), steel, x, 5, 3.2).rotation.z = r; });
  const big = new THREE.Group(); big.position.set(-2.5, 9.0, 0.9); S.add(big); put(big, C(2.1, 2.1, 0.4, 20).rotateX(Math.PI/2), fl(0x2a313a)); for(let j = 0; j < 14; j++){ const a = j/14*Math.PI*2; put(big, B(0.5, 0.5, 0.4), fl(0x2a313a), Math.cos(a)*2.2, Math.sin(a)*2.2, 0).rotation.z = a; } put(big, C(0.5, 0.5, 5, 10).rotateX(Math.PI/2), fl(0x353d47), 0, 0, 2);
  put(S, B(1.5, 1.2, 1.5), lam(0x4b3f33), 11, 0.6, 1.6); put(S, B(1.1, 0.9, 1.1), lam(0x55483a), 11.2, 1.65, 1.5).rotation.y = 0.3; put(S, C(0.55, 0.55, 1.3, 14), lam(0x2f5a63), 9.4, 0.65, 1.4);
  scene.add(new THREE.HemisphereLight(0x8fb4d8, 0x10141a, 0.62));
  const lamp = new THREE.SpotLight(0xffe2b0, 36*k*k, 18*k, 0.85, 0.6, 1.4); lamp.position.set((DX - 1.2)*k, 7.2*k, 2.6*k); lamp.target.position.set((DX - 0.4)*k, 0, 2.2*k); scene.add(lamp, lamp.target);
  put(S, B(0.5, 0.25, 0.5), lam(0x2a3038), DX - 1.2, 7.45, 1.2); put(S, new THREE.SphereGeometry(0.2, 10, 8), bas(0xffe9c2), DX - 1.2, 7.2, 1.2);
  const moon = new THREE.DirectionalLight(0x6f93c9, 0.55); moon.position.set(-14, 16, 14); scene.add(moon);
  const inner = new THREE.PointLight(0x7fe9ff, 0, 12*k, 1.6); inner.position.set(DX*k, 1.6*k, 0.9*k); scene.add(inner);
  const V = {wide:[[4.6, 4.4, 16.5], [-0.8, 3.0, 0]], near:[[DX + 1.6, 3.6, 11.5], [DX - 0.8, 2.8, 0]], in:[[DX + 0.1, 2.5, 5.6], [DX, 2.3, -1]]};
  const R = LABSET = {scene, story:true, k, open:0, want:0, last:null, cam:null,
    spots:[[XYLO, DX - DW/2 - 3.5, 2.3, Math.PI - 1.0], [ZERO, DX + 2.6, 3.4, Math.PI + 0.35], [RICO, DX + 4.1, 3.9, Math.PI + 0.5]],
    pose(){ door.position.x = DX + R.open*(DW + 0.05); door.position.z = R.open > 0.02 ? -0.18 : 0.12; gears.forEach((g, i)=> g.rotation.z = R.open*(i ? -5 : 4)); lever.rotation.z = -0.7 + Math.min(1, R.open*4)*1.4; inner.intensity = R.open*7*k*k; },
    reset(){ R.open = R.want = 0; R.cam = null; R.pose(); R.view('wide', 0); },
    view(name, ms){ const [p, t] = V[name], to = {p:new THREE.Vector3(...p).multiplyScalar(k), t:new THREE.Vector3(...t).multiplyScalar(k)}; if(!ms){ camera.position.copy(to.p); controls.target.copy(to.t); R.cam = null; return; } R.cam = {p0:camera.position.clone(), t0:controls.target.clone(), ...to, s:performance.now(), ms}; },
    update(t){ const dt = R.last == null ? 0 : Math.min(Math.max(t - R.last, 0), 0.05); R.last = t; if(R.open !== R.want){ R.open = R.want > R.open ? Math.min(R.want, R.open + dt/1.8) : Math.max(R.want, R.open - dt/1.2); R.pose(); }
      if(R.cam){ const c = R.cam, u = Math.min(1, (performance.now() - c.s)/c.ms), e = u*u*(3 - 2*u); camera.position.lerpVectors(c.p0, c.p, e); controls.target.lerpVectors(c.t0, c.t, e); if(u >= 1) R.cam = null; } } };
  R.pose(); return R; }
function labSetEnter(){ const room = labSet(), cast = room.spots.map(sp=> sp[0]);
  labKeep = {near:camera.near, fov:camera.fov, min:controls.minDistance, max:controls.maxDistance, en:controls.enabled, pos:camera.position.clone(), tgt:controls.target.clone(), cast:cast.map(g=> ({g, parent:g.parent, p:g.position.clone(), r:g.rotation.y, v:g.visible}))};
  room.spots.forEach(([g, x, z, r])=>{ room.scene.add(g); g.position.set(x*room.k, 0, z*room.k); g.rotation.y = r; g.visible = true; });
  camera.near = 0.1; camera.fov = 42; camera.updateProjectionMatrix(); controls.minDistance = 0.1; controls.maxDistance = 2000; controls.enabled = false; fly = null;
  room.reset(); inside = room; document.body.classList.add('cavestory'); return room; }
function labSetLeave(){ if(!labKeep) return; const q = labKeep; labKeep = null; q.cast.forEach(c=>{ if(c.parent) c.parent.add(c.g); c.g.position.copy(c.p); c.g.rotation.y = c.r; c.g.visible = c.v; });
  if(inside === LABSET) inside = null; camera.near = q.near; camera.fov = q.fov; camera.updateProjectionMatrix(); controls.minDistance = q.min; controls.maxDistance = q.max; controls.enabled = q.en; camera.position.copy(q.pos); controls.target.copy(q.tgt);
  document.body.classList.remove('cavestory'); if(walk) walk.snap = true; }
/* going in: fade to the machine level, the lever is pulled and the door slides away, the camera walks in, and `then` runs under the black */
async function labEnter(lines, then){
  if(ffOn() || reduce){ await new Promise(r=> fadeThrough('#05070c', ()=>{ then && then(); r(); })); return; }
  let room = null; await new Promise(r=> fadeThrough('#05070c', ()=>{ room = labSetEnter(); r(); })); await wait(1200);
  if(lines && lines.length) await new Promise(r=> say(lines.slice(0, 1), r));
  room.view('near', 1300); await wait(700); room.want = 1; sfx('open'); await wait(2200);
  if(lines && lines.length > 1) await new Promise(r=> say(lines.slice(1), r));
  room.view('in', 1500); await wait(1150);
  await new Promise(r=> fadeThrough('#05070c', ()=>{ labSetLeave(); then && then(); r(); })); await wait(300); }
window.__labSet = ()=> LABSET ? {on:inside === LABSET, open:+LABSET.open.toFixed(2), k:+LABSET.k.toFixed(3)} : null;
"""
cut("function labGateBuild(){ if(labGateBuild.o) return labGateBuild.o;", "window.__labGate = ", GATE)
rep("window.__labGate = ()=>{ const o = labGateBuild(); return {k:+o.st.k.toFixed(3), visible:o.g.visible,", "window.__labGate = ()=>{ const o = labGateBuild(); return {k:0, visible:o.g.visible,")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
