# 2026-11-24 사용자 실기:
#  1) 「연구실 도착하면 문구 나올 때 연구실 문이 확실하게 보이게」: 도착 대사 동안 언덕 발치 출입구 덮개를 정면에서 보는 자리(덮개에서 13 바깥)로 옮겨 그쪽을 본다.
#  2) 「기차 타고 할 때 조용한 음악이면 어캄」: 아일랜드 익스프레스를 타는 동안은 신나는 곡(rail, 장조 138bpm, 베이스 쿵쿵 없음). 잔재를 부수는 동안은 지금처럼 tense.
#  3) 「기차 효과음 통통통 없애고 기차음으로」: 열차를 타는 동안 tense의 낮은 베이스 펄스 대신 칙칙폭폭(잡음 묶음 4박) + 출발 기적 소리.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

# 1. lab arrival view
rep("  walk.pitch = q.mini === 'maze' ? 0.2 : -0.05; $('questHud').hidden = true; qNavHide();\n  qPop(q.pop || '발견!');",
    "  if(q.id === 'q5'){ const o = labGateBuild(), gx = o.g.position.x, gz = o.g.position.z; let px = gx + o.face[0]*13, pz = gz + o.face[1]*13; if(walkBlocked(px, pz)) [px, pz] = freeSpot(px, pz);   /* the hatch in full view while 자일로 speaks (user, 2026-11-24) */\n"
    "    walk.x = px; walk.z = pz; walk.yaw = Math.atan2(gx - px, gz - pz); walk.snap = true; walk.imx = walk.imz = 0; }\n"
    "  walk.pitch = q.mini === 'maze' ? 0.2 : q.id === 'q5' ? -0.16 : -0.05; $('questHud').hidden = true; qNavHide();\n  qPop(q.pop || '발견!');")

# 2. rail music
rep("  sim:    {bpm:112,", "  rail:   {bpm:138, base:50, chords:[[0,4,7],[7,11,14],[9,12,16],[5,9,12]],              div:4, pad:'triangle', lp:1700, padG:.03, arpG:.05, arpType:'square',   skip:.08, bass:false, level:1.25, chug:true},   /* riding the Island Express: bright and moving, with the train's chuff (user, 2026-11-24) */\n  sim:    {bpm:112,")
rep("  try{ if(typeof REM !== 'undefined' && (REM.game || (walk && walk.ride && walk.ride.rem))) return 'tense'; }catch(e){}",
    "  try{ if(typeof REM !== 'undefined' && REM.game) return 'tense'; if(walk && walk.ride) return 'rail'; }catch(e){}")
# chuff on the beat while the rail tune plays
rep("    if(S.bass && inBar % (2 * S.div) === 0)",
    "    if(S.chug){ const b4 = inBar % S.div === 0, acc = inBar % (2 * S.div) === 0; if(b4 || inBar % S.div === 2) noise({f0:acc ? 2600 : 1900, f1:acc ? 700 : 600, t0, a:.004, dur:b4 ? .16 : .09, g:acc ? .11 : b4 ? .08 : .05, q:.9, dest:SND.bgmGain}); }   /* 칙-칙-폭-폭 */\n"
    "    if(S.bass && inBar % (2 * S.div) === 0)")
# whistle
rep("    case 'ride':", "    case 'whistle':   [[784, 0], [988, 0], [784, .5], [988, .5]].forEach(([f, d])=> tone({f, f2:f*0.985, type:'triangle', t0:t + d, a:.04, dur:.42, g:.09, lp:2600})); noise({f0:3000, f1:1500, t0:t, dur:.95, g:.03, q:2}); break;   /* the train's two-note whistle, twice */\n    case 'ride':")
rep("function remBoard(){ const w = walk; if(!w || !mini || mini.kind !== 'device' || ride) return; sfx('ride');",
    "function remBoard(){ const w = walk; if(!w || !mini || mini.kind !== 'device' || ride) return; sfx('whistle');")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
