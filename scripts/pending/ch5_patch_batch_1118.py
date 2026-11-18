# 2026-11-18 (사용자 요청 묶음): 자일로·리코 대사, 게임 지우기 난이도·등장 범위·놓치면 목숨, 게임 화면으로 하는 설명,
# 미션 4 중간 전환을 미션 카드로, 회전목마 방향과 말 모양, 잔재 부수는 동안 신호 테두리 끔.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)

# ---------- 1. dialogue ----------
rep("""labGame:[{who:'자일로', text:'시뮬레이터를 켜 볼게요. ……어? 화면이 왜 이렇죠?'}, {who:'제로', text:'앗, 죄송해요! 저번에 저희가 깔아 둔 게임이에요.'}, {who:'리코', text:'이 게임은 끝까지 깨야만 지워져요. 죄송합니다, 저희가 빨리 다시 돌려놓을게요!'}, {who:'보이드', text:'아이콘을 그어서 지워 줘. 세 판을 모두 깨야 해. 내 얼굴은 베지 마.'}], labGameDone:[{who:'제로', text:'다 지웠어요! 정말 죄송했습니다.'}, {who:'자일로', text:'괜찮아요. 이제 시뮬레이터가 보입니다.'}]""",
    """labGame:[{who:'자일로', text:'시뮬레이터를 켜 볼게요. ……또 이 게임이군요! 제로, 리코. 두 사람이 깔아 놓은 거죠?', img:'xylo_oops'}, {who:'제로', text:'앗…… 네. 저번에 저희가 깔아 둔 게임이에요. 죄송해요!', img:'zero_oops'}, {who:'자일로', text:'두 사람이 이렇게 만들었으니, 빨리 원래대로 돌려놓으세요!', img:'xylo_point'}, {who:'리코', text:'이 게임은 끝까지 깨야만 지워져요. 얼른 지울게요!', img:'rico_oops'}], labGameDone:[{who:'제로', text:'다 지웠어요! 정말 죄송했습니다.'}, {who:'자일로', text:'다시는 연구실 화면에 아무것도 깔지 마세요. 이제 시뮬레이터가 보입니다.'}]""")
rep('"저쪽 흐름은 왜 저렇게 흔들려요?"', '"저기 빨갛게 불안정한 흐름들이 있는데, 왜 저런 거예요?"')
rep('잔재를 찾아서 꺼 주세요.', '잔재를 찾아서 부숴 주세요.')

# ---------- 2. the monitor game: harder, the whole screen is used, a missed icon costs a life ----------
rep("STG = [{need:10, time:28, gap:1.0, bad:0.12, v:1}, {need:12, time:26, gap:0.8, bad:0.2, v:1.12}, {need:14, time:24, gap:0.62, bad:0.28, v:1.25}]",
    "STG = [{need:12, time:26, gap:0.9, bad:0.15, v:1}, {need:15, time:26, gap:0.7, bad:0.22, v:1.12}, {need:18, time:26, gap:0.55, bad:0.3, v:1.25}]")
old_spawn = s[s.index("  const spawn = ()=>{ const st = STG[S.stage], bad = S.sn > 1"):s.index("  const glyph = (it, half)=>{")]
new_spawn = """  /* 2026-11-18 (user): not only the bottom strip. Tossed from below up to any height, thrown in from either side, dropped from the top */
  const spawn = ()=>{ const st = STG[S.stage], bad = S.sn > 1 && Math.random() < st.bad, GV = S.h*1.9*st.v, m = Math.random(), r = (bad ? 44 : 40)*S.k; let x, y, vx, vy;
    if(m < 0.45){ x = S.w*(0.12 + Math.random()*0.76); y = S.h + 50*S.k; vy = -Math.sqrt(2*GV*S.h*(0.34 + Math.random()*0.6)); vx = (S.w/2 - x)*0.5 + (Math.random() - 0.5)*S.w*0.3; }
    else if(m < 0.8){ const sd = Math.random() < 0.5 ? -1 : 1; x = sd < 0 ? -50*S.k : S.w + 50*S.k; y = S.h*(0.3 + Math.random()*0.45); vx = -sd*S.w*(0.42 + Math.random()*0.3); vy = -Math.sqrt(2*GV*S.h*(0.06 + Math.random()*0.22)); }
    else { x = S.w*(0.15 + Math.random()*0.7); y = -50*S.k; vy = S.h*(0.05 + Math.random()*0.2); vx = (Math.random() - 0.5)*S.w*0.3; }
    S.items.push({x, y, vx, vy, r, rot:Math.random()*6, vr:(Math.random() - 0.5)*5, bad, c:COL[Math.floor(Math.random()*COL.length)], shape:Math.floor(Math.random()*4)}); };
  const miss = ()=>{ if(S.done || S.failed) return; S.life--; S.shake = 0.25; S.msg = 1.2; $('slP').textContent = '놓쳤어요! 목숨이 줄었어요'; sfx('error'); hud(); if(S.life <= 0) fail('목숨을 모두 잃었어요'); };
"""
rep(old_spawn, new_spawn)
rep("if(S.life <= 0){ fail('보이드를 세 번 벴어요'); return; }", "if(S.life <= 0){ fail('목숨을 모두 잃었어요'); return; }")
rep("S.items = S.items.filter(it=> !it.dead && it.y < H2 + 90*k);", "S.items = S.items.filter(it=>{ if(it.dead) return false; if(it.y < H2 + 90*k || it.vy < 0) return true; if(!it.bad) miss(); return false; }); if(S.failed) S.items = [];")

# ---------- 3. how to play, shown on the game screen itself (user: text alone does not explain it) ----------
rep("""<button type="button" id="slRetry">다시 하기</button></div></div></div>';""", """<button type="button" id="slRetry">다시 하기</button></div><button type="button" id="slTut" hidden></button></div></div>';""")
rep("  stageStart(0); draw(); }); }", """  const TUT = [(matchMedia('(pointer:coarse)').matches ? '아이콘이 날아오면 손가락으로 그어서 베세요' : '아이콘이 날아오면 마우스를 누른 채 그어서 베세요'), '보이드 얼굴은 베면 안 돼요. 베면 목숨이 하나 줄어요', '아이콘을 놓쳐도 목숨이 줄어요. 시간 안에 정해진 개수를 베면 다음 판이에요'];
  const tutShow = ()=>{ $('slP').textContent = TUT[S.tut]; $('slTut').hidden = false; $('slTut').textContent = S.tut < TUT.length - 1 ? '다음' : '시작'; $('slLife').classList.toggle('pt', S.tut > 0); $('slBar').classList.toggle('pt', S.tut === 2); };
  const tutNext = ()=>{ if(S.tut == null) return; sfx('tap'); if(S.tut < TUT.length - 1){ S.tut++; S.tt = 0; tutShow(); return; } S.tut = null; $('slTut').hidden = true; $('slLife').classList.remove('pt'); $('slBar').classList.remove('pt'); removeEventListener('keydown', tutKey, true); stageStart(0); };
  const tutKey = e=>{ if(S.tut != null && (e.code === 'Space' || e.code === 'Enter')){ e.preventDefault(); e.stopPropagation(); tutNext(); } };
  $('slTut').onclick = tutNext; addEventListener('keydown', tutKey, true);
  stageStart(0); S.tut = 0; S.tt = 0; S.banner = ''; tutShow(); draw(); }); }""")
rep("  const draw = ()=>{ const now = performance.now(), dt = Math.min(0.05, (now - S.last)/1000); S.last = now; S.t += dt; const W2 = S.w, H2 = S.h, k = S.k, G2 = H2*1.9;\n",
    "  const draw = ()=>{ const now = performance.now(), dt = Math.min(0.05, (now - S.last)/1000); S.last = now; S.t += dt; const W2 = S.w, H2 = S.h, k = S.k, G2 = H2*1.9; if(S.tut != null){ S.hold = 1.4; S.tt += dt; }\n")
rep("    if(S.hold > 0 && S.banner && !S.done){", """    if(S.tut != null){ const u = S.tt % 2.6, cx = W2/2, cy = H2*0.5, R = 62*k; g.fillStyle = 'rgba(5,8,15,.5)'; g.fillRect(0, 0, W2, H2);
      const finger = (x, y)=>{ g.beginPath(); g.arc(x, y, 20*k, 0, 6.3); g.fillStyle = 'rgba(255,255,255,.92)'; g.fill(); g.lineWidth = 4*k; g.strokeStyle = '#8cecff'; g.stroke(); };
      const swipe = p=>{ const ax = cx - W2*0.2, ay = cy + H2*0.2, bx = cx + W2*0.2, by = cy - H2*0.2, x = ax + (bx - ax)*p, y = ay + (by - ay)*p; g.lineCap = 'round'; g.lineWidth = 10*k; g.strokeStyle = 'rgba(140,236,255,.9)'; g.beginPath(); g.moveTo(ax + (bx - ax)*Math.max(0, p - 0.45), ay + (by - ay)*Math.max(0, p - 0.45)); g.lineTo(x, y); g.stroke(); finger(x, y); };
      if(S.tut === 0){ const p = Math.min(1, Math.max(0, (u - 0.5)/0.8)), q = Math.max(0, p - 0.5)*2, it = {x:cx, y:cy, r:R, rot:-0.785, bad:false, c:COL[4], shape:3};
        if(q > 0){ const o = q*70*k; glyph({...it, x:cx - o*0.7, y:cy - o*0.7}, -1); glyph({...it, x:cx + o*0.7, y:cy + o*0.7}, 1); } else glyph(it, 0); if(u > 0.3 && u < 1.9) swipe(p); }
      else if(S.tut === 1){ glyph({x:cx, y:cy, r:R*1.15, rot:0, bad:true}, 0); const a = 0.6 + 0.4*Math.sin(S.tt*6); g.globalAlpha = a; g.lineWidth = 12*k; g.strokeStyle = '#ff5a4e'; g.beginPath(); g.arc(cx, cy, R*1.75, 0, 6.3); g.moveTo(cx - R*1.24, cy - R*1.24); g.lineTo(cx + R*1.24, cy + R*1.24); g.stroke(); g.globalAlpha = 1; }
      else { const p = Math.min(1, u/1.6), y = H2*0.45 + p*p*H2*0.7; glyph({x:cx, y, r:R, rot:p*3, bad:false, c:COL[1], shape:0}, 0); g.fillStyle = '#ff7a6e'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `800 ${Math.round(64*k)}px sans-serif`; if(p > 0.75) g.fillText('목숨 -1', cx, H2*0.8); }
    }
    if(S.hold > 0 && S.banner && !S.done){""")
rep("  $('slRetry').onclick = ()=>{ sfx('tap'); stageStart(S.stage); };", "  $('slRetry').onclick = ()=>{ sfx('tap'); stageStart(S.stage); };\n  const stage0 = stageStart;")
CSS = ("#slTut{position:absolute;right:20px;bottom:20px;min-height:58px;padding:0 40px;border:0;border-radius:999px;background:#8cecff;color:#061426;font:800 20px var(--sans);cursor:pointer}#slTut[hidden]{display:none}#slTut:active{transform:scale(.97)}"
       "#slLife.pt,#slBar.pt{outline:3px solid #ffd400;outline-offset:5px;border-radius:8px}")
MARK = "</style></head><body>"
rep(MARK, CSS + "\n" + MARK)

# ---------- 4. mission 4, lab -> remnants: a mission card, not the 「미션 이어하기」 pop ----------
rep("let MCARD = null, MCARD_R = null;", "let MCARD = null, MCARD_R = null, MCARD_NEXT = null;")
rep("function missionCard(q){ let auto = false;", "function missionCard(q0, ov){ const q = ov ? Object.assign({}, q0, ov) : q0; let auto = false;")
rep("$('mcN').textContent = `MISSION ${QUESTS.indexOf(q) + 1}`; $('mcNo').textContent = QUESTS.indexOf(q) + 1;", "$('mcN').textContent = `MISSION ${QUESTS.indexOf(q0) + 1}`; $('mcNo').textContent = QUESTS.indexOf(q0) + 1;")
rep("  qPop('미션 이어하기'); voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); return true; }",
    "  if(MCARD_NEXT){ const ov = MCARD_NEXT; MCARD_NEXT = null; missionCard(q, ov).then(()=>{ try{ voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); }catch(e){} }); return true; }   /* a new stretch of the mission opens with its card (user, 2026-11-18) */\n  qPop('미션 이어하기'); voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); return true; }")
rep("  actBusy = false; startWalk(PAIR); }\nwindow.__rem = ", "  actBusy = false; MCARD_NEXT = {title0:null, hint:'스카이 루프 역'}; startWalk(PAIR); }\nwindow.__rem = ")

# ---------- 5. carousel: the horses face the way they travel, and look like horses ----------
a = s.index("    add(h, CYL(0.25,0.25,16,6), mat(C.gold), 0, -4, 0);\n    const col = [0xffffff, 0xffd9e6, 0xd9ecff, 0xfff1c2][i%4];")
b = s.index("    if(i%3) rider(h, 0, 2.8, -0.6, i, 0.8, 0);")
HORSE = """    add(h, CYL(0.25,0.25,16,6), mat(C.gold), 0, -4, 0);
    /* 2026-11-18 (user): a horse, not a box. Barrel body, arched neck, long head with ears, mane and tail, legs in mid-gallop, a saddle cloth */
    const col = [0xffffff, 0xffd9e6, 0xd9ecff, 0xfff1c2][i%4], hair = [0xc98a3c, 0xb0567a, 0x4a78b8, 0xa87a2a][i%4], cm = mat(col), hm = mat(hair);
    const body = add(h, CYL(1.25,1.35,4.2,12), cm, 0, 1.25, -2.1); body.rotation.x = Math.PI/2;
    add(h, SPH(1.3,12,10), cm, 0, 1.25, 2.0); add(h, SPH(1.4,12,10), cm, 0, 1.25, -2.0);
    const nk = new THREE.Group(); nk.position.set(0, 1.9, 2.3); nk.rotation.x = 0.6; h.add(nk);
    add(nk, CYL(0.62,0.95,2.6,10), cm); add(nk, BOX(0.34,2.7,0.55), hm, 0, 0.1, -0.9);
    const hd = new THREE.Group(); hd.position.set(0, 2.5, 0); hd.rotation.x = 1.15; nk.add(hd);
    add(hd, CYL(0.5,0.8,2.0,10), cm, 0, -0.3, 0); add(hd, SPH(0.5,10,8), cm, 0, 1.7, 0); add(hd, BOX(0.34,0.6,0.5), hm, 0, -0.1, -0.8);
    [-1, 1].forEach(sd=>{ const ear = add(hd, CONE(0.22,0.75,6), cm, sd*0.38, 0.1, -0.6); ear.rotation.x = -Math.PI/2; add(hd, SPH(0.13,8,6), mat(0x2a2320), sd*0.62, 0.6, -0.2, false); });
    const tl = new THREE.Group(); tl.position.set(0, 1.9, -3.1); tl.rotation.x = -2.5; h.add(tl); add(tl, CONE(0.5,2.6,8), hm);
    [[-0.6, 1.7, -0.55, 0.95], [0.6, 1.7, -0.75, 1.1], [-0.65, -1.8, 0.5, 0.5], [0.65, -1.8, 0.3, 0.35]].forEach(([x, z, a1, a2])=>{ const up = new THREE.Group(); up.position.set(x, 0.8, z); up.rotation.x = a1; h.add(up);
      add(up, CYL(0.38,0.28,1.7,8), cm, 0, -1.7, 0); const lo = new THREE.Group(); lo.position.set(0, -1.7, 0); lo.rotation.x = a2; up.add(lo); add(lo, CYL(0.26,0.2,1.3,8), cm, 0, -1.3, 0); add(lo, CYL(0.27,0.32,0.4,8), mat(0x3a2f2a), 0, -1.7, 0); });
    const cloth = add(h, CYL(1.42,1.46,2.1,12), mat(0xe2574c), 0, 1.25, -1.3); cloth.rotation.x = Math.PI/2; add(h, BOX(1.5,0.35,1.5), mat(0x8a4a2c), 0, 2.55, -0.9);
"""
s = s[:a] + HORSE + s[b:]
rep("islAnim.push(t=>{ spin.rotation.y = t*0.25; horses.forEach(", "islAnim.push(t=>{ spin.rotation.y = -t*0.25;   /* the horses face +tangent: the deck has to turn this way or they run backwards (user, 2026-11-18) */ horses.forEach(")

# ---------- 6. breaking a remnant: the detection signal round the screen is off ----------
rep("function remGame(i){ const m = REM.models[i]; remDlg(); mini.phase = 'game';", "function remGame(i){ const m = REM.models[i]; remDlg(); mini.phase = 'game'; remPulse(0);")
io.open(P, "w", encoding="utf-8", newline="").write(s)

M = "C:/Users/dlgus/break_out/docs/chapter05_script.md"
t = io.open(M, encoding="utf-8", newline="").read()
for a, b in (("- 리코: 저쪽 흐름은 왜 저렇게 흔들려요?", "- 리코: 저기 빨갛게 불안정한 흐름들이 있는데, 왜 저런 거예요?"), ("- 자일로: 잔재를 찾아서 꺼 주세요.", "- 자일로: 잔재를 찾아서 부숴 주세요.")):
    assert t.count(a) == 1, a
    t = t.replace(a, b)
io.open(M, "w", encoding="utf-8", newline="").write(t)
print("ok")
