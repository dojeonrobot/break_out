# 2026-11-11 ① 섬을 걸어 다니던 보이드 로봇 삭제(사용자) ② 리코·제로 움직임 자연스럽게(사용자: 너무 이상하게 움직임)
#   탐험: 출발·정지에 가속/감속, 캐릭터가 자기 자리로 부드럽게 따라오고 가는 방향을 바라봄(옆걸음·뒷걸음 없음), 걸음 폭은 속도에 비례, 멈출 때 자세가 튀지 않고 숨쉬기 유지
#   산책: 다리 속도를 이동 속도에 맞춤(발 미끄러짐 제거), 끝에서 돌아설 때 천천히 돌아섬
# 사용: python ch5_patch_pair_motion.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s

def swap(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# ---- ① Void no longer walks behind the pair: off the character list, no stroll animation ----
a = s.index("  {g:VOID, s:0.15, n:'보이드', desc:"); b = s.index("\n", a)
assert s[a:b].rstrip().endswith('},'), s[a:b][-40:]
s = s[:a] + s[b+1:]
swap("""  VOID.position.set(-6.6, G + 0.2 + Math.abs(Math.sin(t*5))*0.12, zw - dirw*1.8); VOID.rotation.y = dirw > 0 ? 0 : Math.PI; VOID.userData.legs.forEach((l,i)=> l.rotation.x = Math.sin(t*5 + i*Math.PI)*0.5);
  VOID.userData.ring.material.opacity = 0.3 + 0.25*Math.sin(t*3);
  const blink = (t % 4) < 0.12 ? 0.15 : 1; VOID.userData.eyes.forEach(e=> e.scale.y = blink);
""", "")
swap("  // Rico and Zero stroll round the plaza side by side, Void hovering just behind them\n", "  // Rico and Zero stroll round the plaza side by side (the Void robot no longer follows them: user, 2026-11-11)\n")

# ---- ② plaza stroll: stride matches ground speed (124 units per 55.6 s = 2.23 u/s -> 2.0 rad/s), a slow about-turn at each end ----
swap("""  if(!STAGED) [[RICO, -6], [ZERO, -7.3]].forEach(([p, x])=>{ p.position.set(x, G, zw); p.rotation.y = dirw > 0 ? 0 : Math.PI; walkPose(p, t, 5); });
""", """  const turnU = sw > 1.5 ? sw - 2 : sw, turnE = u=>{ const k = Math.max(0, Math.min(1, u/0.05 + 0.5)); return k*k*(3 - 2*k); };
  const strollYaw = Math.abs(turnU) < 0.025 ? Math.PI + Math.PI*turnE(turnU) : Math.abs(sw - 1) < 0.025 ? Math.PI*turnE(sw - 1) : dirw > 0 ? 0 : Math.PI;
  if(!STAGED) [[RICO, -6], [ZERO, -7.3]].forEach(([p, x], i)=>{ p.position.set(x, G, zw); p.rotation.y = strollYaw; p.userData.swayT = t + i*1.7; walkPose(p, t + i*0.35, 2.0); });
""")
# the idle sway runs on its own clock, so a character that has stopped keeps breathing
swap("  const r = p.userData.rig, s = Math.sin(t*speed), c = Math.cos(t*speed), w = t*1.3;", "  const r = p.userData.rig, s = Math.sin(t*speed), c = Math.cos(t*speed), w = (p.userData.swayT ?? t)*1.3;")

# ---- ② exploring: eased input, each character follows its slot and faces where it is going ----
swap("""  let mx = fwd - walkPad.dz*hold, mz = strafe + walkPad.dx*hold; const len = Math.hypot(mx, mz); if(len > 1){ mx /= len; mz /= len; }
""", """  let mx = fwd - walkPad.dz*hold, mz = strafe + walkPad.dx*hold; const len = Math.hypot(mx, mz); if(len > 1){ mx /= len; mz /= len; }
  { const ek = 1 - Math.exp(-dt*(len ? 9 : 13)); w.imx = (w.imx || 0) + (mx - (w.imx || 0))*ek; w.imz = (w.imz || 0) + (mz - (w.imz || 0))*ek; if(Math.hypot(w.imx, w.imz) < 0.02){ w.imx = 0; w.imz = 0; } mx = w.imx; mz = w.imz; }   /* ease in and out of a walk */
""")
swap("""    m.g.position.set(px, characterGroundY(px, pz) + lift, pz); m.g.rotation.y = w.yaw; if(m.g.userData.legL) walkPose(m.g, moving ? w.bob*0.9 : 0, 1); }); miniTick(now, moving);
""", """    const u = m.g.userData, far = u.fx == null || w.snap || Math.hypot(px - u.fx, pz - u.fz) > 6 || dt <= 0;
    if(far){ u.fx = px; u.fz = pz; u.fyaw = w.yaw; u.fv = 0; }
    else { const fk = 1 - Math.exp(-dt*(inMaze ? 20 : 11)), ox = u.fx, oz = u.fz; u.fx += (px - u.fx)*fk; u.fz += (pz - u.fz)*fk;
      if(inMaze && mazeBlocked(u.fx, u.fz)){ u.fx = px; u.fz = pz; }
      const vx = (u.fx - ox)/dt, vz = (u.fz - oz)/dt, v = Math.hypot(vx, vz); u.fv += (v - u.fv)*(1 - Math.exp(-dt*10));
      const want = v > 0.9 ? Math.atan2(vx, vz) : w.yaw; u.fyaw += Math.atan2(Math.sin(want - u.fyaw), Math.cos(want - u.fyaw))*(1 - Math.exp(-dt*(v > 0.9 ? 7 : 5)));
      u.fph = (u.fph || 0) + v*dt*0.9; }
    m.g.position.set(u.fx, characterGroundY(u.fx, u.fz) + lift, u.fz); m.g.rotation.y = u.fyaw;
    if(u.rig && !w.fly){ u.walkedAt = islT; u.swayT = now/1000 + i*1.7; u.walkK = Math.min(1.2, u.fv/5); u.walkT = u.fph || 0; rigPose(m.g, u.walkT, 1, u.walkK); }
    else if(u.legL) walkPose(m.g, moving ? w.bob*0.9 : 0, 1); }); miniTick(now, moving);
""")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
