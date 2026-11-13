# 2026-11-13 batch7 화면 확인에서 남은 세 가지
#  ① 대사 자리(sceneSpot): 대상 뒤 배경까지 본다. 배전선 뒤 자일로 바로 뒤에 큰 나무가 화면을 채웠다 → 후보 자리마다 대상 너머가 얼마나 트였는지 점수를 매겨 가장 트인 자리를 고른다.
#  ② 미로에서 네이티를 찾았을 때: 너무 가까워 네이티가 화면 위로 잘렸다 → 한가운데 칸 안에서 3m 떨어진 자리에 서고 시선을 네이티 높이로 올린다.
#  ③ 흐름을 따라갈 때 흐름 머리의 빛이 화면을 하얗게 채우고 빠르게 깜빡였다 → 머리 빛을 작게, 깜빡임을 느리게.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
# ① openness behind the target decides between clear spots
rep("function sceneSpot(tx, tz, d, wantA){ let fb = null; for(let k = 0; k < 16; k++){ const a = wantA + Math.ceil(k/2)*(Math.PI/8)*(k % 2 ? 1 : -1), x = tx + Math.sin(a)*d, z = tz + Math.cos(a)*d; if(walkBlocked(x, z)) continue; if(!fb) fb = [x, z]; let ok = false; try{ ok = viewClear(x, z, tx, tz); }catch(e){} if(ok) return [x, z]; } return fb || freeSpot(tx + Math.sin(wantA)*d, tz + Math.cos(wantA)*d); }",
    "/* how open the backdrop is: the nearest thing behind the target inside the frame, in metres (capped at 60) */\n"
    "function viewDepth(x, z, tx, tz){ const y = groundY(x, z) + 1.7, a0 = Math.atan2(tx - x, tz - z), L = Math.hypot(tx - x, tz - z); let near = 60;\n"
    "  for(const da of [-0.36, -0.18, 0, 0.18, 0.36]) for(const up of [0.1, 0.32]){ _vo.set(x, y, z); _vd.set(Math.sin(a0 + da), up, Math.cos(a0 + da)).normalize(); _vr.set(_vo, _vd); _vr.near = L + 0.8; _vr.far = 60;\n"
    "    for(const h of _vr.intersectObject(islRoot, true)){ let ch = false; for(let p = h.object; p; p = p.parent){ if(charGroups.includes(p) || p.isSkinnedMesh || p.visible === false){ ch = true; break; } } if(ch) continue; if(h.distance < near) near = h.distance; break; } }\n"
    "  return near; }\n"
    "function sceneSpot(tx, tz, d, wantA){ let fb = null, best = null, bs = -1; for(let k = 0; k < 16; k++){ const a = wantA + Math.ceil(k/2)*(Math.PI/8)*(k % 2 ? 1 : -1), x = tx + Math.sin(a)*d, z = tz + Math.cos(a)*d; if(walkBlocked(x, z)) continue; if(!fb) fb = [x, z]; let ok = false, sc = 0; try{ ok = viewClear(x, z, tx, tz); if(ok) sc = viewDepth(x, z, tx, tz) - Math.ceil(k/2)*0.6; }catch(e){} if(ok && sc > bs){ bs = sc; best = [x, z]; if(sc > 45) break; } } return best || fb || freeSpot(tx + Math.sin(wantA)*d, tz + Math.cos(wantA)*d); }")
# ② Naty in frame when found
rep("  else walk.yaw = Math.atan2(tx - walk.x, tz - walk.z);\n  walk.pitch = -0.05;",
    "  else { if(q.mini === 'maze'){ const a0 = Math.atan2(walk.x - tx, walk.z - tz); for(let k = 0; k < 8; k++){ const a = a0 + Math.ceil(k/2)*(Math.PI/4)*(k % 2 ? 1 : -1), x = tx + Math.sin(a)*3, z = tz + Math.cos(a)*3; if(mazeHeart(x, z) && !walkBlocked(x, z)){ walk.x = x; walk.z = z; walk.snap = true; walk.imx = walk.imz = 0; break; } } }   /* 3 m from 네이티, still in the heart cell: at 1.5 m it was cut off by the top of the screen (2026-11-13) */\n    walk.yaw = Math.atan2(tx - walk.x, tz - walk.z); }\n  walk.pitch = q.mini === 'maze' ? 0.2 : -0.05;")
# ③ the head of the flow: small and steady
rep("r.head.scale.setScalar(r.head.userData.sz*(1 + 0.25*Math.sin(t*22)));", "r.head.scale.setScalar(r.head.userData.sz*0.4*(1 + 0.06*Math.sin(t*5)));   /* was full size with a 3.5 Hz flicker: it whited out the chase view (user, 2026-11-13) */")
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
