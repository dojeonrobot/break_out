# 2026-11-13 사용자 지시
#  ① 환원 시뮬레이터에서 흐름을 따라가는 동안에는 바닥으로 퍼지는 파동(충격 고리)을 내지 않는다. 문양이 다 완성된 뒤에만.
#  ② 대사가 나오는 자리는 배경이 트인 곳에서: 배전선 뒤 자일로 장면이 나무에 절반 가려졌다 → 서는 자리를 고를 때 시야가 트인 방향을 찾는다(sceneSpot).
#     대상을 찾았을 때 서는 자리도 같은 방법으로.
#  ③ 미로에서 네이티를 찾았을 때 뒷모습이 아니라 앞모습(걷는 사람 쪽을 봄)
#  + 점검용 손잡이 __sliceWin
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
# ① shock rings only once the whole glyph is lit and its sweep has ended
rep("const q = ((t*0.45) + k*0.2) % 1; shock.visible = onK > 0.5; shock.scale.setScalar(1 + q*34);",
    "const q = ((t*0.45) + k*0.2) % 1, whole = SIM_LIT === 5 && !simFlyOn && SIM_REVEAL_T != null && t - SIM_REVEAL_T > Math.max(0, ...REVEALS.map(r=> r.delay + r.dur)) + 0.4; shock.visible = onK > 0.5 && whole;   /* 2026-11-13 (user): no waves while the flow is being followed, too bright; only when the glyph is whole */ shock.scale.setScalar(1 + q*34);")
# ② a clear view for a dialogue
rep("function yardDone(){",
    "/* where to stand for a dialogue with someone at (tx, tz): d away, on walkable ground, with nothing between and nothing close on either side of the view (user, 2026-11-13: half the screen was a tree). Tries the wanted side first. */\n"
    "const _vr = new THREE.Raycaster(), _vo = new THREE.Vector3(), _vd = new THREE.Vector3();\n"
    "function viewClear(x, z, tx, tz){ const y = groundY(x, z) + 1.6, a0 = Math.atan2(tx - x, tz - z), L = Math.hypot(tx - x, tz - z); islRoot.updateMatrixWorld();\n"
    "  for(const [da, far] of [[0, Math.max(0.5, L - 1.6)], [-0.42, 13], [0.42, 13], [-0.8, 7], [0.8, 7]]){ _vo.set(x, y, z); _vd.set(Math.sin(a0 + da), 0.04, Math.cos(a0 + da)).normalize(); _vr.set(_vo, _vd); _vr.near = 0.2; _vr.far = far;\n"
    "    const hits = _vr.intersectObject(islRoot, true); for(const h of hits){ let o = h.object, ch = false; for(let p = o; p; p = p.parent){ if(charGroups.includes(p) || p.isSkinnedMesh){ ch = true; break; } if(p.visible === false){ ch = true; break; } } if(!ch && !/^(park-visitors|queue-visitors|public-path|facility-spur)/.test(o.name || '')) return false; } }\n"
    "  return true; }\n"
    "function sceneSpot(tx, tz, d, wantA){ let fb = null; for(let k = 0; k < 16; k++){ const a = wantA + Math.ceil(k/2)*(Math.PI/8)*(k % 2 ? 1 : -1), x = tx + Math.sin(a)*d, z = tz + Math.cos(a)*d; if(walkBlocked(x, z)) continue; if(!fb) fb = [x, z]; let ok = false; try{ ok = viewClear(x, z, tx, tz); }catch(e){} if(ok) return [x, z]; } return fb || freeSpot(tx + Math.sin(wantA)*d, tz + Math.cos(wantA)*d); }\n"
    "function yardDone(){")
rep("if(walk && XYLO_HIDE){ const p = freeSpot(XYLO_HIDE[0] - Math.sin(XYLO_HIDE[2])*7, XYLO_HIDE[1] - Math.cos(XYLO_HIDE[2])*7);",
    "if(walk && XYLO_HIDE){ const p = sceneSpot(XYLO_HIDE[0], XYLO_HIDE[1], 7, XYLO_HIDE[2] + Math.PI);")
rep("for(let k = 0; k < 8; k++){ const a = k*Math.PI/4*(k % 2 ? 1 : -1), ca = Math.cos(a), sa = Math.sin(a), x = gx + (dx*ca - dz*sa)/d*4.5, z = gz + (dx*sa + dz*ca)/d*4.5; if(!walkBlocked(x, z)){ walk.x = x; walk.z = z; walk.snap = true; walk.imx = walk.imz = 0; break; } } }",
    "const sp = sceneSpot(gx, gz, 4.5, Math.atan2(dx, dz)); walk.x = sp[0]; walk.z = sp[1]; walk.snap = true; walk.imx = walk.imz = 0; }\n    else { let ok = true; try{ ok = viewClear(walk.x, walk.z, gx, gz); }catch(e){} if(!ok){ const sp = sceneSpot(gx, gz, Math.max(4.5, Math.min(7, d)), Math.atan2(dx, dz)); walk.x = sp[0]; walk.z = sp[1]; walk.snap = true; walk.imx = walk.imz = 0; } }")
# ③ Naty faces whoever walks up
rep("NATY.position.set(pk[0], pk[2] + Math.sin(t*1.4)*0.5, pk[1]); NATY.rotation.y = MAZE.rot;", "NATY.position.set(pk[0], pk[2] + Math.sin(t*1.4)*0.5, pk[1]); NATY.rotation.y = walk ? Math.atan2(walk.x - pk[0], walk.z - pk[1]) : MAZE.rot;   /* its face to the walker (user, 2026-11-13) */")
rep("window.__slice = ()=>", "window.__sliceWin = ()=>{ if(SLICE) SLICE.win(); };\nwindow.__slice = ()=>")
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
