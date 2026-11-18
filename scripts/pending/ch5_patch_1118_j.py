# 2026-11-18 묶음 7 (사용자 실기 확인): 역 간판이 계단을 막음, 열차가 역에서 기다림, 탐지 기회 표시·Space 버그, 둘째 잔재가 너무 큼,
# 다시 들어왔을 때 하던 미션 카드, 미션 시작 버튼을 눈에 띄게.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
MARK = "</style></head><body>"
rep(MARK, "/* the mission pill is the one thing to press on the island: big, filled, breathing (user, 2026-11-18: it did not stand out) */"
    "#questPill{left:50%;right:auto;transform:translateX(-50%);bottom:calc(92px + env(safe-area-inset-bottom,0px));min-height:68px;padding:10px 26px 10px 30px;gap:18px;background:#9ff6ff;color:#06111a;font-size:21px;box-shadow:0 14px 30px -12px rgba(6,17,26,.7),0 0 0 6px rgba(159,246,255,.3);animation:qpBreath 1.8s ease-in-out infinite}"
    "#questPill small{font-size:13px;color:#16425a}#questPill i{font-size:26px;color:#06111a}#questPill:active{transform:translateX(-50%) scale(.98)}html.phone #questPill{bottom:calc(150px + env(safe-area-inset-bottom,0px));min-height:58px;font-size:17px}"
    "#islandActions>#questPill{left:auto;transform:none}#islandActions>#questPill:active{transform:scale(.98)}"
    "@keyframes qpBreath{50%{box-shadow:0 14px 30px -12px rgba(6,17,26,.7),0 0 0 14px rgba(159,246,255,.08)}}@media (prefers-reduced-motion:reduce){#questPill{animation:none}}"
    "#miniBox .dots .rd{display:grid;justify-items:center;gap:1px;padding:5px 14px;border-radius:10px;background:rgba(159,246,255,.12);white-space:nowrap}#miniBox .dots .rd em{font:600 11px var(--sans);font-style:normal;color:#9fd0e6}#miniBox .dots .rd b{font:700 20px/1.1 var(--sans);color:#fff;letter-spacing:.1em}#miniBox .dots .rd.ch b{color:#ffc247}#miniBox .dots .rd.ch.low b{color:#ff7a6e}\n" + MARK)

# 1. the station sign stood at the foot of the stairs: it goes beside them
old = "px + inx*17, G, pz + inz*17); { const sm = new THREE.MeshBasicMaterial({map:signTex('SKY LOOP'"
assert s.count(old) == 1
a = s.index("  const post = add(g, CYL(0.35, 0.4, 9, 8), mat(0x1d2f55),"); b = s.index("  STATION = {u:bu,", a)
seg = s[a:b]; n0 = seg.count("px + inx*17"); m0 = seg.count("pz + inz*17")
seg = seg.replace("px + inx*17", "SX").replace("pz + inz*17", "SZ")
seg = "  const SX = px + inx*15 + ux*7.5, SZ = pz + inz*15 + uz*7.5;   /* beside the stairs, not at their foot (user, 2026-11-18: it blocked the way up) */\n" + seg
s = s[:a] + seg + s[b:]; print("sign refs moved", n0, m0)

# 2. the train waits at the platform while the children are sent to board it
rep("TRAIN.mode = TRAIN.mode === 'ride' ? 'ride' : parkPowerOn() ? 'run' : 'stop';", "TRAIN.mode = TRAIN.mode === 'ride' ? 'ride' : TRAIN.wait ? 'stop' : parkPowerOn() ? 'run' : 'stop'; if(TRAIN.wait && typeof STATION !== 'undefined' && STATION) TRAIN.u = STATION.u;")
rep("  miniSave('rail', {got}); miniWalkTo(2, '숨겨진 잔재를 찾아라', '스카이 루프 역에서 열차 타기', STATION.spot, 7, remBoard); }", "  TRAIN.wait = true; if(TRAIN.mode !== 'ride'){ TRAIN.mode = 'stop'; TRAIN.u = STATION.u; }   /* waiting at the platform (user, 2026-11-18) */\n  miniSave('rail', {got}); miniWalkTo(2, '숨겨진 잔재를 찾아라', '스카이 루프 역에서 열차 타기', STATION.spot, 7, remBoard); }")
rep("    mini.phase = 'ride'; TRAIN.mode = 'ride'; TRAIN.u = ride.u; walk.ride = ride; walk.snap = true; $('walkPad').hidden = true;", "    mini.phase = 'ride'; TRAIN.wait = false; TRAIN.mode = 'ride'; TRAIN.u = ride.u; walk.ride = ride; walk.snap = true; $('walkPad').hidden = true;")
rep("remPulse(0); $('walkPad').hidden = false; TRAIN.mode = 'run'; TRAIN.u = STATION.u; miniSave('device-return'", "remPulse(0); $('walkPad').hidden = false; TRAIN.wait = false; TRAIN.mode = 'run'; TRAIN.u = STATION.u; miniSave('device-return'")

# 3. detection: the counts are easy to read, and the Space that closes a dialogue is not a detection
rep("function remDots(){ const got = mini ? mini.got || [] : []; miniDots.innerHTML = [0, 1, 2].map(i=> `<i class=\"${got.includes(i) ? 'on' : ''}\">잔재 ${i + 1}</i>`).join('') + (ride && ride.rem ? `<i class=\"on\">기회 ${ride.life}</i>` : ''); }",
    "function remDots(){ const got = mini ? mini.got || [] : [], life = ride && ride.rem ? Math.max(0, Math.min(3, ride.life == null ? 3 : ride.life)) : null;\n  miniDots.innerHTML = `<span class=\"rd\"><em>찾은 잔재</em><b>${got.length} / 3</b></span>` + (life == null ? '' : `<span class=\"rd ch${life <= 1 ? ' low' : ''}\" aria-label=\"탐지 기회 ${life}\"><em>탐지 기회</em><b>${'●'.repeat(life)}${'○'.repeat(3 - life)}</b></span>`); }")
rep("  const press = go && (R.press || WALK_KEYS.Space), edge = !!press && !R.wasPress; R.wasPress = !!press;",
    "  /* the press is read even while a dialogue is open, so the Space that closes it (still held) is not taken as a new press; and nothing counts for half a second after a dialogue (user, 2026-11-18: 「다음」 cost a chance) */\n  const raw = !!(R.press || WALK_KEYS.Space), press = go && raw, edge = !!press && !R.wasPress && performance.now() - (typeof VN_CLOSED === 'number' ? VN_CLOSED : 0) > 500; R.wasPress = raw;")

# 4. the second remnant (the pylon) was taller than the view: shorter, and the camera frames each remnant by its own height
rep("  else if(kind === 1){ add(g, CYL(2.6, 3.3, 0.8, 8), mat(0x5d5f5a)); cy = 10.4; const lean = 0.1;\n    parts = [[2.0, 2.4, 3.2, 0.8], [1.5, 1.9, 3.0, 4.0], [1.0, 1.4, 2.6, 7.0]]",
    "  else if(kind === 1){ add(g, CYL(2.6, 3.3, 0.8, 8), mat(0x5d5f5a)); cy = 6.0; const lean = 0.1;   /* was 10.4 high: out of the picture (user, 2026-11-18) */\n    parts = [[2.0, 2.4, 1.9, 0.8], [1.5, 1.9, 1.7, 2.7], [1.0, 1.4, 1.3, 4.4]]")
rep("rings = [3.4, 6.2, 8.8].map((y, k)=>", "rings = [2.2, 3.7, 5.0].map((y, k)=>")
rep("tl = Math.hypot(tx, tz) || 1, gx = sp.x + tx/tl*9.5, gz = sp.z + tz/tl*9.5, sh =", "tl = Math.hypot(tx, tz) || 1, far = 9.5 + Math.max(0, (m.cy || 3.6) - 3.6)*1.3, gx = sp.x + tx/tl*far, gz = sp.z + tz/tl*far, sh =")
rep("_wt.set(sp.x, m.y0 + 3.3, sp.z); camera.lookAt(_wt); controls.target.copy(_wt);\n    w.mates.forEach((mt, i)=>{ const k = i ? 2.4 : -2.4,", "_wt.set(sp.x, m.y0 + Math.max(3.3, (m.cy || 3.6)*0.72), sp.z); camera.lookAt(_wt); controls.target.copy(_wt);\n    w.mates.forEach((mt, i)=>{ const k = i ? 2.4 : -2.4,")

# 5. coming back in the middle of an island mission: the page opens on the campus (as always), so it says what was being done and takes the child back there
rep("function missionCard(q0, ov){ const q = ov ? Object.assign({}, q0, ov) : q0; let auto = false;", "let MCARD_SKIP = false;\nfunction missionCard(q0, ov){ if(MCARD_SKIP && !ov){ MCARD_SKIP = false; return Promise.resolve(); } const q = ov ? Object.assign({}, q0, ov) : q0; let auto = false;")
rep("$('mcGo').textContent = matchMedia('(pointer:coarse)').matches ? '미션 시작' : '미션 시작 · Space';", "$('mcGo').textContent = (q.go || '미션 시작') + (matchMedia('(pointer:coarse)').matches ? '' : ' · Space'); if(q.label) $('mcN').textContent = q.label;")
rep("  setTimeout(()=>{ try{ maybeGuide(); actCheck(); }catch(e){} }, 1500);\n}", "  setTimeout(()=>{ try{ maybeGuide(); actCheck(); }catch(e){} }, 1500); setTimeout(()=>{ try{ resumeAsk(); }catch(e){} }, 3200);\n}\n"
    "/* 2026-11-18 (user): a child who left in the middle of an island mission lands on the campus when the page opens again. One card says which mission it was and goes back to it */\n"
    "let RESUME_ASKED = false;\nfunction resumeAsk(){ if(RESUME_ASKED || !TEAM || AUX || SCREEN || W.id !== 'erica' || intro || actBusy || actPending || vn || walk || $('voidVn').dataset.on || $('recDone').dataset.on || $('teamPick').dataset.on || document.body.classList.contains('admin')) return;\n"
    "  if(tutStep >= 0 && tutStep < 99) return; if(stepWorld() !== 'island') return; const q = dueQuest(); if(!q || actSeen() < q.act) return; RESUME_ASKED = true;\n"
    "  let cp = null; try{ cp = miniLoad(); }catch(e){} const mid = !!cp && cp.q === q.id, n = QUESTS.indexOf(q) + 1;\n"
    "  missionCard(q, {label:mid ? `MISSION ${n} · 하던 미션` : `MISSION ${n} · 다음 미션`, go:mid ? '이어서 하기' : '섬으로 가기', title0:mid ? null : q.title0}).then(async ()=>{ MCARD_SKIP = !mid; await goWorld('island'); await wait(300); if(!walk && !actBusy) startWalk(PAIR); }); }")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
