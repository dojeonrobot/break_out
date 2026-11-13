# 2026-11-13 대사 자리 고르기 다시 씀. 재 보니 batch7·8의 viewClear는 거의 모든 자리에서 "막힘"이라 첫 후보로 떨어졌고(자일로 뒤 나무 그대로), 후보 하나에 0.27초가 들었다.
#  → 시선 3개(가운데·좌·우)로 "가장 가까이 걸리는 것까지의 거리"를 점수로 삼는다. 가운데 시선이 대상보다 앞에서 걸리면 0점. 후보 12곳 중 점수가 가장 높은 자리.
#  + 흐름을 따라가는 시점을 더 높이(비스듬한 각에서 빛이 겹쳐 화면이 하얗게 떴다). + 점검 손잡이 __scene
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
a = s.index("function viewClear(x, z, tx, tz){"); b = s.index("function yardDone(){"); assert 0 < a < b and b - a < 6000
s = s[:a] + (
    "function viewScore(x, z, tx, tz){ const y = groundY(x, z) + 1.7, a0 = Math.atan2(tx - x, tz - z), L = Math.hypot(tx - x, tz - z); let near = 60; islRoot.updateMatrixWorld();\n"
    "  for(const da of [0, -0.28, 0.28]){ _vo.set(x, y, z); _vd.set(Math.sin(a0 + da), 0.14, Math.cos(a0 + da)).normalize(); _vr.set(_vo, _vd); _vr.near = 0.3; _vr.far = 60;\n"
    "    for(const h of _vr.intersectObject(islRoot, true)){ let skip = /^(park-visitors|queue-visitors|public-path|facility-spur)/.test(h.object.name || ''); for(let p = h.object; p && !skip; p = p.parent){ if(charGroups.includes(p) || p.isSkinnedMesh || p.visible === false) skip = true; } if(skip) continue; if(da === 0 && h.distance < L + 0.5) return 0; if(h.distance < near) near = h.distance; break; } }\n"
    "  return near; }\n"
    "function viewClear(x, z, tx, tz){ return viewScore(x, z, tx, tz) >= 14; }\n"
    "function sceneSpot(tx, tz, d, wantA){ let fb = null, best = null, bs = 0; for(let k = 0; k < 12; k++){ const a = wantA + Math.ceil(k/2)*(Math.PI/6)*(k % 2 ? 1 : -1), x = tx + Math.sin(a)*d, z = tz + Math.cos(a)*d; if(walkBlocked(x, z)) continue; if(!fb) fb = [x, z]; let sc = 0; try{ sc = viewScore(x, z, tx, tz) - Math.ceil(k/2)*0.5; }catch(e){} if(sc > bs){ bs = sc; best = [x, z]; if(sc > 40) break; } } return best || fb || freeSpot(tx + Math.sin(wantA)*d, tz + Math.cos(wantA)*d); }\n"
) + s[b:]
rep("window.__scene = {clear:viewClear, depth:viewDepth, spot:sceneSpot,", "window.__scene = {clear:viewClear, depth:viewScore, spot:sceneSpot,")
rep("_sfB.copy(_sfA).addScaledVector(_sfD, -270); _sfB.y += 185;", "_sfB.copy(_sfA).addScaledVector(_sfD, -330); _sfB.y += 430;   /* higher (was 185): at a grazing angle the glow layers stacked into a white screen (user, 2026-11-13) */")
rep("  VEIN_U.uPulse.value += ((simFlyOn ? 0 : 1) - VEIN_U.uPulse.value)*0.1;", "  VEIN_U.uPulse.value += ((simFlyOn ? 0 : 1) - VEIN_U.uPulse.value)*0.1; if(bloomPass) bloomPass.strength += ((simFlyOn ? 0.08 : 0.6) - bloomPass.strength)*0.1;   /* the chase view sits close to the light: bloom nearly off while it runs (user, 2026-11-13) */")
assert 'viewDepth' not in s
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
