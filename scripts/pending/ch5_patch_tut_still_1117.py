# 2026-11-17 사용자 요청 묶음. 한 번만 적용.
#  ① 튜토리얼 「여기는 도로랜드 섬이야」~「하모니아 근처야」: 섬 3D로 넘어가지 않고 그림 두 장(img/tut_island.jpg, tut_harmonia.jpg; ch5_shot_tut_island.py로 찍음)
#  ② 「아래에 네 좌표도 떠」: 파란 화살표와 함께 좌표 카드 예시를 띄우고 짚는다
#  ③ 관리자 로그인 기기에서 보기 조가 이 태블릿 조와 다르면 막 연출의 시뮬레이터가 0/5로 비어 보였다 → 막을 시작할 때 보기를 이 조로
#  ④ 자일로(미션 1) 자리: 큰 나무 옆 풀밭 → 롤러코스터로 가는 길 위(나무가 없는 곳)
#  ⑤ 전원 연출: 높은 시점 뒤에 움직이는 기구 셋을 가까이에서 차례로 보여 주고 돌아온다
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# ① still pictures
rep("</style></head><body>", "#tutStill{position:fixed;inset:0;z-index:36;opacity:0;pointer-events:none;transition:opacity .45s ease;background:#2f86c8}#tutStill[data-on]{opacity:1;pointer-events:auto}#tutStill img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .45s ease}#tutStill img[data-on]{opacity:1}@media (prefers-reduced-motion:reduce){#tutStill,#tutStill img{transition:none}}</style></head><body>")
rep("function tutShow(){ tutSpotOff(); const st = TUT[tutStep];",
    "/* the island in the tutorial is two pictures, not the live 3D island (user, 2026-11-17: the first switch lagged badly; with the power out nothing moves there anyway) */\n"
    "const TUT_STILL = {home:'img/tut_island.jpg', harmonia:'img/tut_harmonia.jpg'};\n"
    "function tutStill(k){ let el = $('tutStill'); if(!el){ el = document.createElement('div'); el.id = 'tutStill'; el.setAttribute('aria-hidden', 'true'); el.innerHTML = Object.keys(TUT_STILL).map(n=> `<img data-k=\"${n}\" src=\"${TUT_STILL[n]}\" alt=\"\">`).join(''); document.body.appendChild(el); void el.offsetWidth; }\n"
    "  el.querySelectorAll('img').forEach(i=>{ if(i.dataset.k === k) i.dataset.on = '1'; else delete i.dataset.on; }); if(k) el.dataset.on = '1'; else delete el.dataset.on; }\n"
    "function tutShow(){ tutSpotOff(); const st = TUT[tutStep]; const still = st.world === 'island' && W.id !== 'island';")
rep("if(st.world && W.id !== st.world) tutWorld(st.world); voidShow(", "if(still) tutStill(tutStep === 12 ? 'harmonia' : 'home'); else { if(tutStep < 7 || $('tutStill')) tutStill(null); if(st.world && W.id !== st.world) tutWorld(st.world); } voidShow(")
rep("if(st.do) try{ st.do(); }catch(e){} }", "if(st.do && !still) try{ st.do(); }catch(e){} }")
rep("function tutEnd(){ tutSpotOff(); voidHide();", "function tutEnd(){ tutSpotOff(); voidHide(); try{ if($('tutStill')) tutStill(null); }catch(e){}")

# ② the coordinate card as an example
rep("function tutMePreview(on){",
    "function tutCoordDemo(on){ const el = $('meCoord'), m = MISSION_E.find(x=> x.id === 'z1'); if(!on){ if(follow){ try{ showMeCoord(); }catch(e){} } else el.hidden = true; return; } if(!m || m.lat == null) return;\n"
    "  const la = m.lat - 0.00027, ln = m.lng + 0.00029, sg = v=> `<b class=\"${v > 0 ? 'pos' : 'neg'}\">${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(6)}</b>`;   /* an example spot 40 m from the first record */\n"
    "  $('meCoordV').textContent = `${la.toFixed(6)}, ${ln.toFixed(6)}`; $('meCoordA').textContent = ''; $('meGoal').hidden = $('meDiff').hidden = false; $('meGoalV').textContent = coordText(m); $('meGoalN').textContent = '';\n"
    "  $('meDiffV').innerHTML = `${sg(m.lat - la)}, ${sg(m.lng - ln)}`; $('meDiffM').textContent = '북30m 서26m · 40m 남음'; $('meTrend').textContent = ''; el.hidden = false; }\n"
    "function tutMePreview(on){")
rep("if(on === tutMeOn) return; tutMeOn = on;", "if(on === tutMeOn) return; tutMeOn = on; try{ tutCoordDemo(on); if(on) setTimeout(()=>{ if(tutMeOn) tutSpot($('meCoord')); }, 120); }catch(e){}")

# ③ admin-login tablet: the act plays in this tablet's own team view
rep("async function playAct(n){\n  voidHist = []; actBusy = true;",
    "async function playAct(n){\n  if(ADMIN_KEY && TEAM && VIEW_ADMIN !== TEAM){ VIEW_ADMIN = TEAM; try{ sessionStorage.setItem('void-view', String(TEAM)); }catch(e){} try{ rescan(); }catch(e){} }   /* another team's view showed the simulator empty (2026-11-17) */\n  voidHist = []; actBusy = true;")

# ④ 자일로 on the path to the coaster
rep("XYLO_HIDE = freeSpot(cx + Math.cos(a)*rr, cz + Math.sin(a)*rr); XYLO_HIDE.push(Math.atan2(cx - XYLO_HIDE[0], cz - XYLO_HIDE[1]));",
    "{ let best = null, bd = 1e9; for(const [px, pz] of pathSamples){ const d = Math.hypot(px - cx, pz - cz); if(d > rr - 8 && d < bd){ bd = d; best = [px, pz]; } }   /* on the path that leads to the coaster: the lawn spot stood beside a big tree (user, 2026-11-17) */\n"
    "      XYLO_HIDE = best ? [best[0], best[1]] : freeSpot(cx + Math.cos(a)*rr, cz + Math.sin(a)*rr); XYLO_HIDE.push(Math.atan2(0 - XYLO_HIDE[0], 128 - XYLO_HIDE[1])); }")

# ⑤ the power-on scene visits moving rides
rep("PARK_WAKE = {k:0, dur:6.2, sp:0, src, ctr, ring, done, p0:camera.position.clone(), t0:controls.target.clone()};",
    "const tour = ['하모니아', '갤럭시 스윙', '매직 티컵'].map(l=> IB.find(b=> b && b.label === l)).filter(Boolean).map((b, i)=> ({x:b.cx, z:b.cz, D:(b.r || 24)*1.1 + 55, H:26 + (b.r || 24)*0.35, a:0.5 + i*1.9}));   /* seen close up, running (user, 2026-11-17) */\n"
    "  PARK_WAKE = {k:0, dur:6.2 + tour.length*2.8, sp:0, src, ctr, ring, done, tour, dt:0, cp:null, ct:null, p0:camera.position.clone(), t0:controls.target.clone()};")
rep("const w = PARK_WAKE; if(!w) return; w.k += Math.min(dt, 1/20); const k = w.k,", "const w = PARK_WAKE; if(!w) return; w.dt = Math.min(dt, 1/20); w.k += w.dt; const k = w.k,")
rep("  const up = sm(k/1.6)*(1 - sm((k - (w.dur - 1.1))/1.1)), a = 0.6 + k*0.07;\n  _pwT.copy(w.src).lerp(w.ctr, 0.55); _pwP.set(_pwT.x + Math.sin(a)*430, G + 300, _pwT.z + Math.cos(a)*430);\n",
    "  const up = sm(k/1.6)*(1 - sm((k - (w.dur - 1.1))/1.1)), a = 0.6 + k*0.07;\n  _pwT.copy(w.src).lerp(w.ctr, 0.55); _pwP.set(_pwT.x + Math.sin(a)*430, G + 300, _pwT.z + Math.cos(a)*430);\n"
    "  { const hi = 5.1, n = w.tour ? w.tour.length : 0; if(n && k > hi - 0.5){ const i = Math.min(n - 1, Math.max(0, Math.floor((k - hi)/2.8))), sp = w.tour[i], aa = sp.a + (k - hi - i*2.8)*0.14; _pwP.set(sp.x + Math.sin(aa)*sp.D, G + sp.H, sp.z + Math.cos(aa)*sp.D); _pwT.set(sp.x, G + 12, sp.z); }\n"
    "    if(!w.cp){ w.cp = _pwP.clone(); w.ct = _pwT.clone(); } const f = 1 - Math.exp(-w.dt*3.4); w.cp.lerp(_pwP, f); w.ct.lerp(_pwT, f); _pwP.copy(w.cp); _pwT.copy(w.ct); }\n")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('patched', len(s))
