# 2026-11-17 사용자: 지하 연구실 게임을 더 짜임새 있게 + 실패 조건·난이도, 제로·리코는 죄송해하는 태도, 「게임을 끝까지 깨야 지워진다」 설정.
#  세 판(STAGE 1~3, 판마다 목표·제한 시간·속도·보이드 얼굴 비율이 오름), 목숨 3개(보이드 얼굴을 베면 하나 잃음), 시간이 다 되거나 목숨이 없으면 게임 오버 → 그 판부터 다시.
#  또: 공중에 떠 있던 화살표 안내 글자(← 사파리 등)는 지금 배치와 맞지 않아 뺌(WELCOME만 남김). 한 번만 적용.
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# dialogue
rep("labGame:[{who:'자일로', text:'시뮬레이터를 켜 볼게요. ……어?'}, {who:'제로', text:'아, 그거요. 저번에 저희가 깔아 둔 게임이에요.'}, {who:'리코', text:'화면을 전부 덮어 버렸네. 저희가 치울게요.'}, {who:'보이드', text:'아이콘을 손가락으로 그어서 지워 줘. 내 얼굴은 베지 마.'}], labGameDone:[{who:'자일로', text:'됐어요. 이제 시뮬레이터가 보입니다.'}]});",
    "labGame:[{who:'자일로', text:'시뮬레이터를 켜 볼게요. ……어? 화면이 왜 이렇죠?'}, {who:'제로', text:'앗, 죄송해요! 저번에 저희가 깔아 둔 게임이에요.'}, {who:'리코', text:'이 게임은 끝까지 깨야만 지워져요. 죄송합니다, 저희가 빨리 다시 돌려놓을게요!'}, {who:'보이드', text:'아이콘을 그어서 지워 줘. 세 판을 모두 깨야 해. 내 얼굴은 베지 마.'}], labGameDone:[{who:'제로', text:'다 지웠어요! 정말 죄송했습니다.'}, {who:'자일로', text:'괜찮아요. 이제 시뮬레이터가 보입니다.'}]});")
# dialog markup (rebuilt when the old one is on the page)
rep("function sliceDlg(){ let d = $('sliceDlg'); if(d) return d; d = document.createElement('div');", "function sliceDlg(){ let d = $('sliceDlg'); if(d && d.querySelector('#slFail')) return d; if(d) d.remove(); d = document.createElement('div');")
rep("""d.innerHTML = '<div class="in"><div class="hd"><h1 id="slT">모니터 치우기</h1><p id="slP">아이콘을 그어서 베세요</p><b id="slN">0 / 30</b></div><canvas id="slCv" aria-hidden="true"></canvas></div>';""",
    """d.innerHTML = '<div class="in"><div class="hd"><h1 id="slT">게임 지우기</h1><span id="slStage"></span><span id="slLife" aria-label="목숨"></span><b id="slN">0 / 10</b><p id="slP">아이콘을 그어서 베세요</p><div id="slBar" aria-hidden="true"><i></i></div></div><div class="stg"><canvas id="slCv" aria-hidden="true"></canvas><div id="slFail" hidden><h2>게임 오버</h2><p id="slWhy"></p><button type="button" id="slRetry">다시 하기</button></div></div></div>';""")
# state and stages
rep("const d = sliceDlg(), cv = $('slCv'), g = cv.getContext('2d'), NEED = 30, COLS = 6, ROWS = 5,", "const d = sliceDlg(), cv = $('slCv'), g = cv.getContext('2d'), STG = [{need:10, time:28, gap:1.0, bad:0.12, v:1}, {need:12, time:26, gap:0.8, bad:0.2, v:1.12}, {need:14, time:24, gap:0.62, bad:0.28, v:1.25}], NEED = STG.reduce((a, b)=> a + b.need, 0), COLS = 6, ROWS = 5,")
rep("const S = SLICE = {n:0, items:[], halves:[], trail:[],", "const S = SLICE = {n:0, sn:0, stage:0, life:3, time:STG[0].time, hold:1.4, banner:'STAGE 1', failed:false, items:[], halves:[], trail:[],")
rep("const spawn = ()=>{ const bad = S.n > 3 && Math.random() < 0.16,", "const hud = ()=>{ const st = STG[S.stage]; $('slStage').textContent = `STAGE ${S.stage + 1} / ${STG.length}`; $('slLife').innerHTML = [0, 1, 2].map(i=> `<i class=\"${i < S.life ? 'on' : ''}\"></i>`).join(''); $('slN').textContent = `${Math.min(S.sn, st.need)} / ${st.need}`; $('slBar').firstChild.style.transform = `scaleX(${Math.max(0, Math.min(1, S.time/st.time)).toFixed(3)})`; $('slBar').classList.toggle('low', S.time < 8); };\n"
    "  const stageStart = k=>{ S.stage = k; S.sn = 0; S.n = STG.slice(0, k).reduce((a, b)=> a + b.need, 0); S.life = 3; S.time = STG[k].time; S.items = []; S.trail = []; S.spawn = 0.3; S.hold = 1.4; S.banner = `STAGE ${k + 1}`; S.failed = false; S.cover = Array.from({length:COLS*ROWS}, (_, i)=> i).slice(0, Math.round(COLS*ROWS*(1 - S.n/NEED))); $('slFail').hidden = true; $('slP').textContent = '아이콘을 그어서 베세요'; hud(); };\n"
    "  const fail = why=>{ if(S.done || S.failed) return; S.failed = true; S.items = []; S.down = false; $('slWhy').textContent = why; $('slFail').hidden = false; sfx('error'); setTimeout(()=>{ try{ $('slRetry').focus(); }catch(e){} }, 60); };\n"
    "  $('slRetry').onclick = ()=>{ sfx('tap'); stageStart(S.stage); };\n"
    "  const spawn = ()=>{ const st = STG[S.stage], bad = S.sn > 1 && Math.random() < st.bad,")
rep("vy = -S.h*(1.05 + Math.random()*0.25);", "vy = -S.h*(1.05 + Math.random()*0.25)*Math.sqrt(STG[S.stage].v);")
# cutting: lives, stage goals
rep("    if(it.bad){ S.n = Math.max(0, S.n - 2); for(let i = 0; i < 2 && S.cover.length < COLS*ROWS; i++){ const free = Array.from({length:COLS*ROWS}, (_, k)=> k).filter(k=> !S.cover.includes(k)); S.cover.push(free[Math.floor(Math.random()*free.length)]); }\n      S.shake = 0.35; S.msg = 1.4; $('slP').textContent = '보이드는 베면 안 돼요!'; sfx('error'); }",
    "    if(it.bad){ S.life--; S.shake = 0.35; S.msg = 1.4; $('slP').textContent = '보이드는 베면 안 돼요!'; sfx('error'); hud(); if(S.life <= 0){ fail('보이드를 세 번 벴어요'); return; } }")
rep("    else { S.n++; if(S.cover.length) S.cover.splice(Math.floor(Math.random()*S.cover.length), 1);", "    else { S.n++; S.sn++; while(S.cover.length > Math.round(COLS*ROWS*(1 - S.n/NEED))) S.cover.splice(Math.floor(Math.random()*S.cover.length), 1);")
rep("    $('slN').textContent = `${Math.min(S.n, NEED)} / ${NEED}`; if(S.n >= NEED && !S.done) win(); };", "    hud(); if(S.sn >= STG[S.stage].need && !S.done){ if(S.stage + 1 < STG.length){ sfx('success'); stageStart(S.stage + 1); } else win(); } };")
rep("const move = e=>{ if(!S.down || S.done ||", "const move = e=>{ if(!S.down || S.done || S.failed || S.hold > 0 ||")
rep("  S.win = ()=>{ if(!S.done){ S.n = NEED; $('slN').textContent = `${NEED} / ${NEED}`; win(); } };", "  S.win = ()=>{ if(!S.done){ S.failed = false; $('slFail').hidden = true; S.stage = STG.length - 1; S.n = NEED; S.sn = STG[S.stage].need; hud(); win(); } };")
# the loop: banner hold, timer, per-stage spawn
rep("    if(!S.done){ S.spawn -= dt; if(S.spawn <= 0){ const many = S.n > 12 ? 3 : S.n > 5 ? 2 : 1; for(let i = 0; i < 1 + Math.floor(Math.random()*many); i++) spawn(); S.spawn = (reduce ? 1.3 : 0.95) - Math.min(0.4, S.n*0.014); } }",
    "    if(S.hold > 0) S.hold -= dt;\n"
    "    else if(!S.done && !S.failed){ const st = STG[S.stage]; S.time -= dt; if(S.time <= 0){ S.time = 0; hud(); fail('시간이 다 됐어요'); } else { if(Math.floor(S.time*4) !== S.tq){ S.tq = Math.floor(S.time*4); hud(); }\n"
    "      S.spawn -= dt; if(S.spawn <= 0){ const many = S.stage + 1; for(let i = 0; i < 1 + Math.floor(Math.random()*many); i++) spawn(); S.spawn = (reduce ? st.gap*1.35 : st.gap); } } }")
rep("    S.items.forEach(it=>{ it.vy += G2*dt;", "    const GV = G2*STG[S.stage].v; S.items.forEach(it=>{ it.vy += GV*dt;")
rep("    if(S.trail.length > 1){ g.lineCap = 'round';", "    if(S.hold > 0 && S.banner && !S.done){ const a = Math.min(1, S.hold/0.3, (1.4 - S.hold)/0.2); g.globalAlpha = Math.max(0, a); g.fillStyle = 'rgba(5,8,15,.55)'; g.fillRect(0, H2*0.36, W2, H2*0.28); g.fillStyle = '#8cecff'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `800 ${Math.round(84*k)}px sans-serif`; g.fillText(S.banner, W2/2, H2*0.47); g.fillStyle = '#eaf7ff'; g.font = `600 ${Math.round(28*k)}px sans-serif`; g.fillText(`아이콘 ${STG[S.stage].need}개 · ${STG[S.stage].time}초`, W2/2, H2*0.57); g.globalAlpha = 1; }\n"
    "    if(S.trail.length > 1){ g.lineCap = 'round';")
rep("  draw(); }); }\nwindow.__sliceWin", "  stageStart(0); draw(); }); }\nwindow.__sliceWin")
rep("window.__slice = ()=> SLICE ? {n:SLICE.n,", "window.__slice = ()=> SLICE ? {stage:SLICE.stage, sn:SLICE.sn, life:SLICE.life, time:+SLICE.time.toFixed(1), failed:SLICE.failed, hold:SLICE.hold > 0, n:SLICE.n,")
CSS = ("#sliceDlg .hd{grid-template-columns:auto auto auto 1fr auto;align-items:center;gap:8px 18px}#sliceDlg h1{font-size:26px}"
       "#slStage{font:800 15px var(--mono);letter-spacing:.14em;color:#061426;background:#8cecff;padding:5px 12px;border-radius:999px;white-space:nowrap}"
       "#slLife{display:flex;gap:6px}#slLife i{width:18px;height:18px;border-radius:50%;border:2px solid #ff7a6e;box-sizing:border-box}#slLife i.on{background:#ff5a4e;border-color:#ff5a4e}"
       "#sliceDlg b#slN{justify-self:end;font-size:30px}#sliceDlg p#slP{grid-column:1 / -1;grid-row:auto;font-size:17px}"
       "#slBar{grid-column:1 / -1;height:10px;border-radius:5px;background:#16233a;overflow:hidden}#slBar i{display:block;height:100%;background:#8cecff;transform-origin:left;transition:transform .25s linear}#slBar.low i{background:#ff5a4e}"
       "#sliceDlg .stg{position:relative;min-height:0}#sliceDlg .stg #slCv{position:absolute;inset:0;box-sizing:border-box}"
       "#slFail{position:absolute;inset:0;display:grid;place-content:center;justify-items:center;gap:14px;border-radius:14px;background:rgba(5,8,15,.86);color:#eaf7ff;text-align:center}#slFail[hidden]{display:none}"
       "#slFail h2{margin:0;font:800 clamp(36px,6vw,60px)/1.1 var(--sans);color:#ff7a6e}#slFail p{font-size:20px;color:#dbe7f5}"
       "#slFail button{min-height:58px;padding:0 40px;border:0;border-radius:999px;background:#8cecff;color:#061426;font:800 20px var(--sans);cursor:pointer}#slFail button:active{transform:scale(.97)}"
       "@media (max-width:640px){#sliceDlg .hd{grid-template-columns:auto 1fr auto}#sliceDlg h1{display:none}}")
k = s.find("</style></head><body>"); assert s[:k].count('{') == s[:k].count('}')
rep("</style></head><body>", CSS + "</style></head><body>")
# floating arrow signs: only the greeting stays
rep("const S = [['WELCOME!', '#7fd7ff'], ['← 사파리', '#ff9fcf'], ['하모니아 ↑', '#7fd7ff'], ['회전목마 →', '#ff9fcf']];", "const S = [['WELCOME!', '#7fd7ff']];   /* the arrow signs pointed the wrong way after the layout changed (user, 2026-11-17) */")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
D = ROOT / 'docs/chapter05_script.md'; d = D.read_bytes().decode('utf-8'); n = 0
for a, b in [('아, 그거요. 저번에 저희가 깔아 둔 게임이에요.', '앗, 죄송해요! 저번에 저희가 깔아 둔 게임이에요.'), ('화면을 전부 덮어 버렸네. 저희가 치울게요.', '이 게임은 끝까지 깨야만 지워져요. 죄송합니다, 저희가 빨리 다시 돌려놓을게요!')]:
    if a in d: d = d.replace(a, b); n += 1
D.write_bytes(d.encode('utf-8')); print('patched', len(s), 'script lines', n)
