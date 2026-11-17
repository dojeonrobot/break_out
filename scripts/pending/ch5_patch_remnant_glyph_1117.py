# 2026-11-17 사용자 요청 묶음 3. 한 번만 적용.
#  ① 시뮬레이터 문양: 가시(뾰족한 부분)는 기록마다 나오지 않고, 다섯 기록이 다 모인 마지막에 가운데 줄과 함께 그려진다
#  ② 잔재 탐지: 바로 옆을 지날 때 한 번 눌러야 한다. 엉뚱한 곳에서 누르거나 지나치면 기회가 줄고(3번), 다 쓰면 역에서 다시 출발. 찾을수록 열차가 빨라진다
#  ③ 「이게 선대의 장치야?」 → 「이게 선대들이 만든 장치의 잔재야?」
#  ④ 분수 광장의 분수를 큰길 옆으로 옮겨 정문~하모니아 길이 곧게 이어지게
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# ① thorns wait for the whole glyph
rep("""    const zoneT = {};
    GLYPH.forEach((pc, i)=>{
      const on = pc.zone === 'final' ? litIds.size === 5 : litIds.has(pc.zone);
      const rv = pc.zone === 'final' ? newLit.length > 0 : newLit.includes(pc.zone);
      const secs = glyphSlice(pc), len = Math.abs(secs[secs.length-1].s - secs[0].s), dur = Math.max(1.6, len/95);
      if(on){
        const start = pc.zone === 'final' ? Math.max(1.0, ...Object.values(zoneT)) + 0.6 : (pc.after && zoneT[pc.zone] != null ? zoneT[pc.zone] : startOf(pc.zone));
        vein(secs, len, rv, start, dur); zoneT[pc.zone] = start + dur;
      } else if(pc.zone !== 'final' && !glyphShort(pc)) ghost(pc, 7 + i*13);
    });""",
"""    const zoneT = {}; let finT = null;
    const isFin = pc=> pc.zone === 'final' || !!pc.after;   /* the thorns come with the last stroke, once all five records are in (user, 2026-11-17): a record alone draws one plain line */
    [false, true].forEach(late=> GLYPH.forEach((pc, i)=>{ const fin = isFin(pc); if(fin !== late) return;
      const on = fin ? litIds.size === 5 : litIds.has(pc.zone);
      const rv = fin ? newLit.length > 0 : newLit.includes(pc.zone);
      const secs = glyphSlice(pc), len = Math.abs(secs[secs.length-1].s - secs[0].s), dur = Math.max(1.6, len/95);
      if(on){
        if(fin && finT == null) finT = Math.max(1.0, ...Object.values(zoneT)) + 0.6;
        const start = fin ? finT : startOf(pc.zone);
        vein(secs, len, rv, start, dur); zoneT[fin ? 'final' : pc.zone] = Math.max(zoneT[fin ? 'final' : pc.zone] || 0, start + dur);
      } else if(!fin && !glyphShort(pc)) ghost(pc, 7 + i*13);
    }));""")
rep("if(SIM_LIT === 5) core(mouth.c[0], mouth.c[1], 9, 0x9ff6ff, newLit.length ? Math.max(1.0, ...Object.values(zoneT)) + 0.6 : -1);", "if(SIM_LIT === 5) core(mouth.c[0], mouth.c[1], 9, 0x9ff6ff, newLit.length ? (finT != null ? finT : 1.6) : -1);")

# ② detection
rep("const REM_WIN = 0.024, REM_FAR = 0.12, REM_LAP = 62;", "const REM_WIN = 0.014, REM_FAR = 0.12, REM_LAP = 62;   /* 2026-11-17: only right beside it */")
rep("spots:remSpots().map((sp, i)=> ({i, u:sp.u, x:sp.x, z:sp.z, hold:0, wasIn:false})), press:false,", "spots:remSpots().map((sp, i)=> ({i, u:sp.u, x:sp.x, z:sp.z, hold:0, wasIn:false})), life:3, press:false,")
rep("R.u = (R.u + dt/REM_LAP*go) % 1; TRAIN.u = R.u;\n  const press = go && (R.press || WALK_KEYS.Space);\n  let best = null, bd = 9; R.spots",
    "R.u = (R.u + dt/REM_LAP*go*(1 + 0.18*got.length)) % 1; TRAIN.u = R.u;   /* faster with every remnant found */\n  const press = go && (R.press || WALK_KEYS.Space), edge = !!press && !R.wasPress; R.wasPress = !!press;\n  let best = null, bd = 9; R.spots")
rep("{ qPop('지나쳤다'); if(!R.missSaid){ R.missSaid = true; say([{who:'리코', img:'rico_hmm', text:'지나쳤어. 괜찮아, 한 바퀴 더 돌면 다시 와.'}]); } }", "{ remMiss('지나쳤다!'); }")
rep("    if(inside){ best.wasIn = true; if(press){ best.hold += dt/1.0; if(best.hold >= 1){ best.hold = 0; best.wasIn = false; remRideFound(best); } } else best.hold = Math.max(0, best.hold - dt*0.6); }\n    miniGo.classList.toggle('hot', inside); miniGo.style.setProperty('--p', inside ? Math.min(1, best.hold).toFixed(2) : 0);",
    "    if(inside){ best.wasIn = true; if(edge){ best.wasIn = false; remRideFound(best); } }\n    else if(edge && now - (R.missAt || 0) > 700){ R.missAt = now; remMiss('여기가 아니야!'); }   /* one press, right beside it; a press anywhere else costs a chance (user, 2026-11-17) */\n    miniGo.classList.toggle('hot', inside); miniGo.style.setProperty('--p', inside ? 1 : 0);")
rep("inside ? (press ? '탐지 중! 꾹 누르고 있어요' : '지금! 「탐지」를 꾹 눌러요') : k > 0.45 ? `신호가 강해지고 있어요 · 남은 잔재 ${3 - got.length}` : `보이드의 신호가 강해지는 곳 찾기 · 남은 잔재 ${3 - got.length}`; }",
    "inside ? '지금! 「탐지」' : k > 0.45 ? `신호가 강해지고 있어요 · 기회 ${R.life}` : `신호가 가장 강한 곳에서 「탐지」 · 기회 ${R.life}`; }")
rep("function remRideNext(){", "function remMiss(text){ const R = ride; if(!R || !R.rem) return; R.life = Math.max(0, (R.life == null ? 3 : R.life) - 1); qPop(text); sfx('error'); remDots(); if(R.life > 0) return;\n"
    "  R.pause = true; miniBox.hidden = true; remPulse(0); say([{who:'', nar:true, text:'탐지 기회를 모두 썼습니다. 역에서 다시 출발합니다.'}], ()=>{ if(ride !== R) return; R.u = STATION.u; TRAIN.u = R.u; R.life = 3; R.wasPress = false; R.spots.forEach(sp=>{ sp.wasIn = false; }); R.pause = false; miniBox.hidden = false; remDots(); if(walk) walk.snap = true; }); }\n"
    "function remRideNext(){")
rep("miniDots.innerHTML = [0, 1, 2].map(i=> `<i class=\"${got.includes(i) ? 'on' : ''}\">잔재 ${i + 1}</i>`).join(''); }", "miniDots.innerHTML = [0, 1, 2].map(i=> `<i class=\"${got.includes(i) ? 'on' : ''}\">잔재 ${i + 1}</i>`).join('') + (ride && ride.rem ? `<i class=\"on\">기회 ${ride.life}</i>` : ''); }")

# ③ wording
rep('"text": "찾았다! 이게 선대의 장치야?"', '"text": "찾았다! 이게 선대들이 만든 장치의 잔재야?"')

# ④ fountain beside the boulevard
rep("place(fountain, 0, 120); fountain.scale.setScalar(0.55);\npickable(fountain, {n:'분수 광장', c:'place', sub:'공통', cx:0, cz:120,", "place(fountain, -38, 120); fountain.scale.setScalar(0.55);   /* beside the boulevard: the way from the gate to Harmonia runs straight (user, 2026-11-17) */\npickable(fountain, {n:'분수 광장', c:'place', sub:'공통', cx:-38, cz:120,")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
D = ROOT / 'docs/chapter05_script.md'; d = D.read_bytes().decode('utf-8'); n = d.count('이게 선대의 장치야?'); D.write_bytes(d.replace('이게 선대의 장치야?', '이게 선대들이 만든 장치의 잔재야?').encode('utf-8'))
print('patched', len(s), 'script lines', n)
