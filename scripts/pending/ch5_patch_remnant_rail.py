# 2026-11-12 (사용자): 잔재는 도로랜드 외곽에 두고, 레일(스카이 루프)을 타고 돌며 찾는다. 레일 앞에서 미션(수색)을 시작한다.
#   연구실 측정 → (화면 전환) 스카이 루프 역 앞 → 역으로 걸어가 탑승 → 한 바퀴 도는 동안 보이드 신호가 강해지는 세 곳에서 「탐지」를 꾹 → 잔재가 땅에서 올라옴
#   → 열차가 멈추고 고리 해체 게임 → 다시 출발 → 세 개를 다 끄고 역에 돌아오면 연구실 시뮬레이션 재실행(화면 전환) → 마지막 좌표.
#   지나친 잔재는 다음 바퀴에 다시 온다. 걸어서 빨간 원 안을 뒤지던 수색(huntStart·huntTick)은 코드만 남고 쓰지 않는다.
import json, pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'remRideTick' not in s
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)

STORY = {'remRail': [dict(who='보이드', text='노이즈가 번지는 곳은 모두 섬 바깥쪽이야. 스카이 루프를 타고 돌면서 찾자.'),
                     dict(who='보이드', text='내 신호가 강해지면 「탐지」를 꾹 눌러 줘.'),
                     dict(who='제로', img='zero_brave', text='좋아, 출발!')]}
rep('const QUESTS = [\n', 'Object.assign(STORY, ' + json.dumps(STORY, ensure_ascii=False) + ');   /* 2026-11-12 잔재 수색을 스카이 루프 위에서 */\nconst QUESTS = [\n')

# where the remnants are: beside the track, on the outer side, a quarter lap apart
a = s.index('function remSpots(){ if(REM.spots) return REM.spots;'); b = s.index('function remBuild(){')
s = s[:a] + ("function remSpots(){ if(REM.spots) return REM.spots; buildStation(); const c = TRAIN.curve;   /* 2026-11-12 (user): on the island's outskirts, beside the Sky Loop */\n"
             "  REM.spots = [0.25, 0.5, 0.75].map((f, i)=>{ const u = (STATION.u + f) % 1, p = c.getPointAt(u), r = Math.hypot(p.x, p.z) || 1, d = 13 + i*2, x = p.x/r*(r + d), z = p.z/r*(r + d); return {x, z, u, kind:'외곽', cx:x, cz:z}; });\n"
             "  return REM.spots; }\n") + s[b:]

RAIL = r'''/* ----- mission 4 on the rail (user, 2026-11-12): ride the Sky Loop and lock on where the void's signal peaks ----- */
const REM_WIN = 0.024, REM_FAR = 0.12, REM_LAP = 62;   /* lock-on window and the range of the signal, in laps; seconds for one lap */
function remDots(){ const got = mini ? mini.got || [] : []; miniDots.innerHTML = [0, 1, 2].map(i=> `<i class="${got.includes(i) ? 'on' : ''}">잔재 ${i + 1}</i>`).join(''); }
function remRail(){ buildStation(); remBuild(); const got = mini.got = mini.got || []; REM.models.forEach((m, i)=>{ if(got.includes(i) && m.state !== 2) remCollapse(m, true); });
  miniSave('rail', {got}); miniWalkTo(2, '숨겨진 잔재를 찾아라', '스카이 루프 역에서 열차 타기', STATION.spot, 7, remBoard); }
function remBoard(){ const w = walk; if(!w || !mini || mini.kind !== 'device' || ride) return; sfx('ride');
  say(STORY.remRail, ()=>{ if(!walk || !mini || mini.kind !== 'device' || ride) return;
    ride = {rem:true, q:mini.q, u:STATION.u, spots:remSpots().map((sp, i)=> ({i, u:sp.u, x:sp.x, z:sp.z, hold:0, wasIn:false})), press:false, pause:false, look:null, lookK:0, beepAt:0};
    mini.phase = 'ride'; TRAIN.mode = 'ride'; TRAIN.u = ride.u; walk.ride = ride; walk.snap = true; $('walkPad').hidden = true;
    miniGo.textContent = '탐지'; miniGo.disabled = false; miniDoneBtn.hidden = true; remDots(); miniBox.hidden = false; miniHud(2, '숨겨진 잔재를 찾아라', '보이드의 신호가 강해지는 곳 찾기'); }); }
function remRideNext(){ if(!ride || !mini) return null; const got = mini.got || []; let best = null, bd = 9; ride.spots.forEach(sp=>{ if(got.includes(sp.i)) return; const d = (sp.u - ride.u + 1) % 1; if(d < bd){ bd = d; best = sp; } }); return best; }
function remRideTick(now, dt){
  const w = walk, R = ride, c = TRAIN.curve; if(!R || !mini) return; dt *= R.boost || 1;
  const go = vn || REM.game || R.pause ? 0 : 1, got = mini.got || []; R.u = (R.u + dt/REM_LAP*go) % 1; TRAIN.u = R.u;
  const press = go && (R.press || WALK_KEYS.Space);
  let best = null, bd = 9; R.spots.forEach(sp=>{ if(got.includes(sp.i)) return; const d = ((R.u - sp.u + 1.5) % 1) - 0.5; if(Math.abs(d) < Math.abs(bd)){ bd = d; best = sp; } });
  const k = best ? Math.max(0, 1 - Math.abs(bd)/REM_FAR) : 0, inside = !!best && Math.abs(bd) < REM_WIN;
  if(go){ remPulse(k);
    if(k > 0){ const gap = Math.max(110, 1100*(1 - k)); if(now - R.beepAt > gap){ R.beepAt = now; sfx('tap'); } }
    R.spots.forEach(sp=>{ if(sp !== best || !inside){ if(sp.wasIn && !got.includes(sp.i) && sp === best && bd > 0){ qPop('지나쳤다'); if(!R.missSaid){ R.missSaid = true; say([{who:'리코', img:'rico_hmm', text:'지나쳤어. 괜찮아, 한 바퀴 더 돌면 다시 와.'}]); } } sp.wasIn = false; sp.hold = 0; } });
    if(inside){ best.wasIn = true; if(press){ best.hold += dt/1.0; if(best.hold >= 1){ best.hold = 0; best.wasIn = false; remRideFound(best); } } else best.hold = Math.max(0, best.hold - dt*0.6); }
    miniGo.classList.toggle('hot', inside); miniGo.style.setProperty('--p', inside ? Math.min(1, best.hold).toFixed(2) : 0);
    $('qhHint').textContent = !best ? '역으로 돌아가는 중' : inside ? (press ? '탐지 중! 꾹 누르고 있어요' : '지금! 「탐지」를 꾹 눌러요') : k > 0.45 ? `신호가 강해지고 있어요 · 남은 잔재 ${3 - got.length}` : `보이드의 신호가 강해지는 곳 찾기 · 남은 잔재 ${3 - got.length}`; }
  /* the camera rides behind the locomotive; while a remnant is being dismantled it turns to look at it */
  c.getPointAt(R.u, _rp); c.getPointAt((R.u + 0.004) % 1, _rq); const dx = _rq.x - _rp.x, dz = _rq.z - _rp.z, L = Math.hypot(dx, dz) || 1, ux = dx/L, uz = dz/L;
  _ct.set(_rp.x - ux*15, _rp.y + 12.5, _rp.z - uz*15); if(w.snap){ camera.position.copy(_ct); w.snap = false; } else camera.position.lerp(_ct, 1 - Math.pow(0.001, dt));   /* higher than the old ride camera: the cab must not fill the view */
  _wt.set(_rq.x + ux*26, _rq.y + 2, _rq.z + uz*26); R.lookK += ((R.look ? 1 : 0) - R.lookK)*(1 - Math.exp(-dt*3)); if(R.look && R.lookK > 0.001){ _rq.set(R.look.x, groundY(R.look.x, R.look.z) + 4, R.look.z); _wt.lerp(_rq, R.lookK); }
  camera.lookAt(_wt); controls.target.copy(_wt);
  const car = c.getPointAt((R.u - 0.0075 + 1) % 1); w.mates.forEach((m, i)=>{ m.g.position.set(car.x - uz*(i ? 1.3 : -1.3), car.y + 3.0, car.z + ux*(i ? 1.3 : -1.3)); m.g.rotation.y = Math.atan2(ux, uz); if(m.g.userData.legL) walkPose(m.g, 0, 1); });
  w.x = _rp.x; w.z = _rp.z;
  if(got.length >= 3 && go && Math.abs(((R.u - STATION.u + 1.5) % 1) - 0.5) < 0.004) remRideEnd();
}
function remRideFound(sp){ const R = ride, m = REM.models[sp.i]; if(!R || !m) return; R.pause = true; R.look = sp; miniGo.classList.remove('hot'); miniBox.hidden = true; remPulse(0); mini.phase = 'dig';
  m.g.visible = true; m.state = 1; sfx('open'); flash(); qPop('잔재 발견!');
  if(!m.beam) m.beam = add(m.g, new THREE.CylinderGeometry(0.9, 1.9, 34, 10, 1, true), glowMat(0xff5a4e, 0.3, true), 0, 17, 0, false); m.beam.visible = true;
  remTween(1300, k=>{ m.g.position.y = m.y0 - 7*(1 - k)*(1 - k); });
  setTimeout(()=>{ if(!mini || mini.kind !== 'device' || ride !== R) return; if(!(mini.got || []).length && !mini.firstSaid){ mini.firstSaid = true; say(STORY.remFirst, ()=> remGame(sp.i)); } else remGame(sp.i); }, reduce ? 200 : 1500); }
function remRideEnd(){ const R = ride; if(!R) return; ride = null; const w = walk; if(w){ w.ride = null; w.snap = true; w.x = STATION.spot[0]; w.z = STATION.spot[1]; w.pitch = w.fp ? -0.05 : -0.2; }
  miniGo.classList.remove('hot'); miniBox.hidden = true; remPulse(0); $('walkPad').hidden = false; TRAIN.mode = 'run'; TRAIN.u = STATION.u; miniSave('device-return', {got:mini.got || [0, 1, 2]});
  setTimeout(()=>{ if(mini && mini.kind === 'device') remRerun(); }, 600); }
function remBuild(){'''
rep('function remBuild(){', RAIL)

# after a remnant is dismantled on the rail: the train goes on
rep("  if(REM.rings[i]){ miniRoot.remove(REM.rings[i]); REM.rings[i] = null; } const left = 3 - got.length;",
    "  if(REM.rings[i]){ miniRoot.remove(REM.rings[i]); REM.rings[i] = null; } const left = 3 - got.length; if(m.beam) m.beam.visible = false;\n"
    "  if(ride && ride.rem){ const R = ride; remDots(); say([{who:'보이드', text: left ? `신호 하나가 꺼졌어. 남은 건 ${left}개야.` : '마지막 신호까지 꺼졌어. 역으로 돌아가서 시뮬레이션을 다시 돌려 보자.'}], ()=>{ if(!mini || ride !== R) return; mini.phase = 'ride'; R.pause = false; R.look = null; miniBox.hidden = false; }); return; }")
rep("if(w.ride){ rideTick(now, dt); questNav(); return; }", "if(w.ride){ (w.ride.rem ? remRideTick : rideTick)(now, dt); questNav(); return; }")
rep("function miniTarget(){ if(!mini) return null; if(mini.kind === 'chase') return chase ? [chase.x, chase.z] : null;",
    "function miniTarget(){ if(!mini) return null; if(mini.kind === 'chase') return chase ? [chase.x, chase.z] : null; if(mini.kind === 'device' && ride && ride.rem){ const sp = remRideNext(); return sp ? [sp.x, sp.z] : STATION.spot; }")
rep("function rideEnd(done){ const R = ride; if(!R) return; ride = null;", "function rideEnd(done){ const R = ride; if(!R) return; ride = null; if(R.rem){ remPulse(0); if(walk) $('walkPad').hidden = false; }")
# the lab measurement leads to the station (a cut, the station is far from the lab), and the checkpoint steps
rep("cp.q = q.id; cp.step = 'hunt'; cp.got = cp.got || [];", "cp.q = q.id; cp.step = 'rail'; cp.got = cp.got || []; delete cp.pos;")
rep("if(st==='device-return'){remBuild();remBack();}else if(st==='hunt')huntStart();else{midCheck(q);return true;}}",
    "if(st==='device-return'){ remBuild(); REM.models.forEach(m=>{ if(m.state !== 2) remCollapse(m, true); }); setTimeout(()=>{ if(mini && mini.kind === 'device') remRerun(); }, 900); }\n"
    "    else if(st==='hunt' || st==='rail'){ buildStation(); const sp = STATION.spot, L = Math.hypot(sp[0], sp[1]) || 1, p = freeSpot(sp[0] - sp[0]/L*16, sp[1] - sp[1]/L*16); if(!cp.pos || Math.hypot(w.x - sp[0], w.z - sp[1]) > 60){ w.x = p[0]; w.z = p[1]; w.yaw = Math.atan2(sp[0] - p[0], sp[1] - p[1]); w.snap = true; } remRail(); st === 'hunt' && (cp.step = 'rail'); }\n"
    "    else{midCheck(q);return true;}}")
rep("const STEP_LINE = {vik:", "const STEP_LINE = {rail:'스카이 루프를 타고 돌면서 찾자. 내 신호가 강해지면 「탐지」를 꾹 눌러 줘.', vik:")
rep("step==='hunt'?`내 탐지 소리가 빨라지는 쪽으로 가 봐. 잔재는 눈에 안 띄게 숨겨져 있어. 지금 ${3-((m?.got||cp?.got||[]).length)}개 남았어.`:", "(step==='hunt'||step==='rail')?`스카이 루프를 타고 돌면서 찾자. 내 신호가 강해지면 「탐지」를 꾹 눌러 줘. 지금 ${3-((m?.got||cp?.got||[]).length)}개 남았어.`:")
rep("step==='device-return'?'잔재 세 개를 모두 없앴어. 연구실로 돌아가서 시뮬레이션을 다시 돌려 보자.':", "step==='device-return'?'잔재 세 개를 모두 없앴어. 시뮬레이션을 다시 돌려 보자.':")
# admin steps and the debug handle
rep("  if(mini.kind === 'device' && mini.phase === 'hunt'){ const got = mini.got || [], i = remSpots()",
    "  if(mini.kind === 'device' && ride && ride.rem){ const sp = remRideNext(); return ride.pause ? null : sp ? {t:`잔재 찾기 · 남은 ${3 - (mini.got || []).length}`, run:()=>{ ride.u = sp.u; remRideFound(sp); }} : {t:'역으로 돌아가기', run:()=> remRideEnd()}; }\n"
    "  if(mini.kind === 'device' && mini.phase === 'hunt'){ const got = mini.got || [], i = remSpots()")
rep("game:REM.game ? {ring:REM.game.ring, a:REM.game.a, done:REM.game.done} : null, noise:!!SIM_NOISE});",
    "game:REM.game ? {ring:REM.game.ring, a:REM.game.a, done:REM.game.done} : null, noise:!!SIM_NOISE, station:STATION ? STATION.spot : null, ride:ride && ride.rem ? {u:+ride.u.toFixed(4), pause:ride.pause, next:(remRideNext() || {}).i} : null, edge:REM.spots ? REM.spots.map(sp=> Math.round(Math.hypot(sp.x, sp.z))) : null});\n"
    "window.__remBoost = k=>{ if(ride) ride.boost = k; };")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8')); print('ok')
