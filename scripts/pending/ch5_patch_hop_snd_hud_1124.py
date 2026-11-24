# 2026-11-24 사용자 실기:
#  1) 「점프로 풀 무더기 같은 거 넘을 수 있게」: 덤불(인스턴스 ICO/12면체)은 걷기 격자에 2(점프로 넘을 수 있음)로 표시, 뛰는 동안(WALK_HOP)만 통과.
#  2) 「미로에 이상한 효과음 띠룽… 없애」: 미로에서 네이티 가까이 가면 반복되던 natyWob 소리 삭제. 동굴 앞 흔들림 연출의 소리도 natyWob 대신 낮은 울림(dark).
#  3) 「겹치는 문제」: 걷는 화면 오른쪽 위 패널(제로·리코 · ? · 나가기, 높이 54) 밑에 소리·관리자 버튼이 붙어 겹침 → 버튼을 78px로 내림.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

# 1. hop over bushes
rep("const g = m.geometry; if(!g || !g.attributes.position) return; if(!g.boundingBox) g.computeBoundingBox(); const lb = g.boundingBox, ly = (lb.min.y + lb.max.y)/2;",
    "const g = m.geometry; if(!g || !g.attributes.position) return; if(!g.boundingBox) g.computeBoundingBox(); const lb = g.boundingBox, ly = (lb.min.y + lb.max.y)/2, hop = /^(Icosahedron|Dodecahedron)Geometry$/.test(g.type);   /* bushes: a jump clears them (user, 2026-11-24) */")
rep("pv.set(lb.min.x + (lb.max.x - lb.min.x)*u, ly, lb.min.z + (lb.max.z - lb.min.z)*v).applyMatrix4(_wgM); if(inb(pv.x, pv.z)) a[at(pv.x, pv.z)] = 1; } } }); }",
    "pv.set(lb.min.x + (lb.max.x - lb.min.x)*u, ly, lb.min.z + (lb.max.z - lb.min.z)*v).applyMatrix4(_wgM); if(inb(pv.x, pv.z)){ const c = at(pv.x, pv.z); if(!hop) a[c] = 1; else if(!a[c]) a[c] = 2; } } } }); }")
rep("    for(let i = 0; i < a.length; i++) if(!seen[i]) a[i] = 1;\n    const path = new Uint8Array(Wd*Hd);",
    "    for(let i = 0; i < a.length; i++) if(!seen[i] && a[i] !== 2) a[i] = 1;\n    const path = new Uint8Array(Wd*Hd);")
rep("function gridBlocked(x, z){ const i = gridCell(x, z); return i >= 0 && WGRID.a[i] === 1; }",
    "let WALK_HOP = false;   /* true while the explorer is in the air: cells marked 2 (bushes) let it through */\nfunction gridBlocked(x, z){ const i = gridCell(x, z); if(i < 0) return false; const v = WGRID.a[i]; return v === 1 || (v === 2 && !WALK_HOP); }")
rep("    if(!walkBlocked(w.x + dx, w.z + dz)){ w.x += dx; w.z += dz; } else if(!walkBlocked(w.x + dx, w.z)) w.x += dx; else if(!walkBlocked(w.x, w.z + dz)) w.z += dz;\n",
    "    WALK_HOP = w.jv != null && w.jy > 0.25;\n    if(!walkBlocked(w.x + dx, w.z + dz)){ w.x += dx; w.z += dz; } else if(!walkBlocked(w.x + dx, w.z)) w.x += dx; else if(!walkBlocked(w.x, w.z + dz)) w.z += dz;\n    WALK_HOP = false;\n")

# 2. no wobble sound in the maze; a low rumble at the cave mouth instead
rep(" if(walk && NATY.visible !== false){ const nd = Math.hypot(walk.x - pk[0], walk.z - pk[1]), nw = performance.now(); if(nd < 30 && nw - (NATY.userData.wobAt || 0) > 900 + nd*45){ NATY.userData.wobAt = nw; try{ sfx('natyWob'); }catch(e){} } }   /* the closer, the faster its unsteady pulse sounds (user, 2026-11-20) */",
    "   /* the unsteady pulse sound near 네이티 in the maze was removed (user, 2026-11-24: 이상한 효과음) */")
rep("if(k - NATY_SHAKE.snd > 0.85){ NATY_SHAKE.snd = k; try{ sfx('natyWob'); }catch(e){} }", "if(k - NATY_SHAKE.snd > 2.2){ NATY_SHAKE.snd = k; try{ sfx('dark'); }catch(e){} }")

# 3. walk HUD vs sound/admin buttons
rep("body.walk #adminBtn{display:flex!important;top:calc(64px + env(safe-area-inset-top,0px))!important;", "body.walk #adminBtn{display:flex!important;top:calc(78px + env(safe-area-inset-top,0px))!important;")
rep("body.walk #sndBtn{top:calc(64px + env(safe-area-inset-top,0px))!important;", "body.walk #sndBtn{top:calc(78px + env(safe-area-inset-top,0px))!important;")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
