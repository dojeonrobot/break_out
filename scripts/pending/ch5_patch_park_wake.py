"""2026-11-04 사용자: 예비 배전선을 다 이었을 때 도로랜드 놀이기구가 움직이는 효과.
성공 직후에는 전원을 붙들어 두고(PARK_HOLD), 「계속」을 누르면 카메라가 공중으로 올라가 섬을 보여 주는 동안
정비동에서 빛 고리가 퍼지고 전구가 아래부터 켜지며 놀이기구가 천천히 출발해 속도를 낸다(PARK_WAKE, 약 6초) → 자일로 대사."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'chapter05', 'index.html')
h = io.open(P, encoding='utf-8', newline='').read().replace('\r\n', '\n')
assert 'PARK_WAKE' not in h, 'already patched'
def rep(a, b, cnt=1):
    global h
    assert h.count(a) == cnt, (a[:70], h.count(a)); h = h.replace(a, b)
rep('var POWER_TEAM=0,PARK_T=0,PARK_ON=false;', 'var POWER_TEAM=0,PARK_T=0,PARK_ON=false,PARK_HOLD=false,PARK_WAKE=null;')
rep("function parkPowerOn(){if(RIDE_PROBE||", "function parkPowerOn(){if(PARK_HOLD&&!RIDE_PROBE)return false;if(RIDE_PROBE||")
rep("function restoreParkPower(){POWER_TEAM=TEAM;TRAIN.lit=true;TRAIN.mode='run';rideSync();",
    "function restoreParkPower(hold){POWER_TEAM=TEAM;PARK_HOLD=!!hold;if(!hold){TRAIN.lit=true;TRAIN.mode='run';}rideSync();")
rep("sfx('success');restoreParkPower();miniSave('station');", "sfx('success');restoreParkPower(true);miniSave('station');")
rep("  setTimeout(()=> say(STORY.yardDone,\n    ()=> miniWalkTo(3, '스카이 루프 역으로', '선로 아래 계단', STATION.spot, 9, rideBoard)), 700); }",
    "  setTimeout(()=> parkWake(()=> say(STORY.yardDone,\n    ()=> miniWalkTo(3, '스카이 루프 역으로', '선로 아래 계단', STATION.spot, 9, rideBoard))), 700); }\n" + r'''// ---------- the park wakes up (2026-11-04): seen from above, a ring of light runs out from the service yard, the bulbs come on from the
// ground up and every ride starts slowly and picks up speed. Its own clock (dt capped at 1/20 s), so a slow tablet plays it slower, never skips it.
function parkWake(done){
  const go = ()=>{ PARK_HOLD = false; TRAIN.lit = true; TRAIN.mode = 'run'; rideSync(); };
  if(!PARK_HOLD || reduce || !walk){ go(); done(); return; }
  const src = new THREE.Vector3(walk.x, G, walk.z), ctr = new THREE.Vector3(10, G, 30);
  go();
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1, 0.5, 8, 128).rotateX(Math.PI/2), glowMat(0xffe27a, 0.9, true)); ring.material.depthWrite = false; ring.position.set(src.x, G + 1.5, src.z); ring.renderOrder = 9; sceneI.add(ring);
  PARK_WAKE = {k:0, dur:6.2, sp:0, src, ctr, ring, done, p0:camera.position.clone(), t0:controls.target.clone()};
  MI.forEach(m=>{ const R = RIDE[m.id]; if(R){ R.s = 0; R.U.uLv.value = G - 6; } }); PARK_U.uLv.value = G - 6; sfx('power');
}
const _pwP = new THREE.Vector3(), _pwT = new THREE.Vector3();
function parkWakeTick(dt){
  const w = PARK_WAKE; if(!w) return; w.k += Math.min(dt, 1/20); const k = w.k, sm = x=>{ x = Math.min(1, Math.max(0, x)); return x*x*(3 - 2*x); };
  w.sp = sm((k - 1.4)/3.2);
  const lv = G - 6 + sm((k - 0.7)/2.6)*160; PARK_U.uLv.value = lv;
  MI.forEach(m=>{ const R = RIDE[m.id]; if(R && R.on){ R.s = w.sp; R.U.uLv.value = lv; } });
  const rk = Math.min(1, k/3.4); w.ring.scale.setScalar(1 + rk*720); w.ring.material.opacity = 0.9*(1 - rk)*(1 - rk);
  if(k >= w.dur){ sceneI.remove(w.ring); w.ring.geometry.dispose(); w.ring.material.dispose(); PARK_WAKE = null;
    PARK_U.uLv.value = 1e4; MI.forEach(m=>{ const R = RIDE[m.id]; if(R && R.on){ R.s = 1; R.U.uLv.value = 1e4; } }); if(walk) walk.snap = true; w.done(); }
}
function parkWakeCam(){   /* after the walk camera each frame: rise to a high view of the island, hold, come back down behind the pair */
  const w = PARK_WAKE; if(!w) return; const k = w.k, sm = x=>{ x = Math.min(1, Math.max(0, x)); return x*x*(3 - 2*x); };
  const up = sm(k/1.6)*(1 - sm((k - (w.dur - 1.1))/1.1)), a = 0.6 + k*0.07;
  _pwT.copy(w.src).lerp(w.ctr, 0.55); _pwP.set(_pwT.x + Math.sin(a)*430, G + 300, _pwT.z + Math.cos(a)*430);
  camera.position.lerp(_pwP, up); _pwT.lerpVectors(controls.target, _pwT, up); camera.lookAt(_pwT); controls.target.copy(_pwT);
}''')
rep("  PARK_ON=parkPowerOn();if(PARK_ON)PARK_T+=dtF;else PARK_T=0;", "  parkWakeTick(dtF);PARK_ON=parkPowerOn();if(PARK_ON)PARK_T+=dtF*(PARK_WAKE?PARK_WAKE.sp:1);else PARK_T=0;")
rep("  camera.lookAt(_wt); controls.target.copy(_wt);\n  questNav(); questTick();", "  camera.lookAt(_wt); controls.target.copy(_wt); if(PARK_WAKE) parkWakeCam();\n  questNav(); questTick();")
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('patched')
