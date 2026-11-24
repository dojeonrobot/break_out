# 2026-11-24 사용자: 「복구 이펙트 근데 옆에 막 불이 왜 들어오는 거임? 그 일루아 이펙트를 넣어야지」 「일루아 들어갈 때 다른 곳이 색칠된 것처럼 보이는 버그」
#  구역 복귀 연출(arriveFx): 기구가 그려진 뒤의 전구 켜기·주변 물결(wake, 주변 간판·바닥 색칠)을 빼고, 일루아가 둘레에서 소용돌이치며 모여 기구 아래로 스며드는 장면으로.
#  전원이 있으면 스며든 뒤 기구가 조용히 움직이기 시작한다(주변 불을 켜지 않음).
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

rep("      {n:'ready', start(r){ sw = rideSweep(m, 0.35); w = buildWake(m);",
    "      {n:'ready', start(r){ sw = rideSweep(m, 0.35); w = null;   /* no wake: it tinted the ground and signs around the ride (user, 2026-11-24) */")
rep("      ...(parkPowerOn() ? powerSteps(m, ()=> w) : [])];   /* no power, no lights and no motion: the ride only draws itself in (2026-11-17) */",
    "      {n:'illua', start(r){ r.side.push(illuaSettle(m, r.clock)); }, tick:k=> k >= 3.5,   /* 일루아 gathers round the ride and sinks into it (user, 2026-11-24) */\n"
    "        end(){ if(parkPowerOn()) rideSet(m.id, true); }}];   /* with power the ride just starts; nothing else lights up */")
FN = r'''
/* 일루아 settling into a zone: cyan streams spiral in from round the ride, sink into its foot, and leave a soft glow on the ground under it only (user, 2026-11-24) */
function illuaSettle(m, k0){ const b = m.b, R = (b.r || 24), g = new THREE.Group(); g.position.set(b.cx, G, b.cz); g.userData.dynamic = true; sceneI.add(g);
  const n = Math.round(260/(1 + fxTier())), pts = new Float32Array(n*3), sd = Array.from({length:n}, ()=> ({a:Math.random()*6.283, r:R*(1.6 + Math.random()*1.4), h:3 + Math.random()*22, d:Math.random()*0.9, s:0.8 + Math.random()*0.5}));
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pts, 3));
  const pm = new THREE.PointsMaterial({size:9, map:sparkTex, color:0x9ff6ff, transparent:true, opacity:0, depthWrite:false, blending:THREE.AdditiveBlending, sizeAttenuation:true}); const pc = new THREE.Points(pg, pm); pc.renderOrder = 11; g.add(pc);
  const disc = add(g, new THREE.CircleGeometry(R*1.05, 48).rotateX(-Math.PI/2), glowMat(0x7fe9ff, 0, true), 0, 0.25, 0, false); disc.material.depthWrite = false; disc.renderOrder = 9;
  sfx('sparkle');
  return c=>{ const k = c - k0; if(c < 0 || k > 3.6){ sceneI.remove(g); pg.dispose(); pm.dispose(); disc.geometry.dispose(); disc.material.dispose(); return false; }
    for(let j = 0; j < n; j++){ const q = sd[j], t = Math.min(1, Math.max(0, (k - q.d)/(1.7*q.s))), e = t*t*(3 - 2*t), a = q.a + e*3.4, rr = q.r*(1 - e) + R*0.12*e;
      pts[j*3] = Math.cos(a)*rr; pts[j*3 + 1] = t <= 0 ? -60 : q.h*(1 - e) + 0.6; pts[j*3 + 2] = Math.sin(a)*rr; }
    pg.attributes.position.needsUpdate = true; pm.opacity = 0.95*Math.min(1, k/0.3)*Math.max(0, 1 - Math.max(0, k - 2.4)/0.8);
    disc.material.opacity = 0.5*Math.min(1, Math.max(0, k - 1.2)/0.8)*Math.max(0, 1 - Math.max(0, k - 2.6)/1.0); };
}
'''
rep("function arriveFx(ids, force){", FN + "function arriveFx(ids, force){")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
