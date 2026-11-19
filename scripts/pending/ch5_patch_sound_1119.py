# 2026-11-19 사용자: "음악이 없는데? 브금이나 대사 계속 나올 때 나오는 음이나 보이드 등장음이나"
#  잰 값: 배경음 최댓값 0.07, 효과음 0.02~0.07 (1.0이 최대) → 거의 안 들림. 전체 음량을 올리고(넘치지 않게 제한기), 대사 글자 소리와 보이드 등장음을 넣는다.
# 한 번만 적용: python scripts/pending/ch5_patch_sound_1119.py
import pathlib, sys
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = p.read_bytes().decode('utf-8').replace('\r\n', '\n'); n0 = len(s)
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:70])
    s = s.replace(a, b)
# 1) 제한기 + 효과음 음량
rep("SND.master.connect(c.destination);\n  SND.sfxGain = c.createGain(); SND.sfxGain.gain.value = .55;",
    "SND.lim = c.createDynamicsCompressor(); SND.lim.threshold.value = -9; SND.lim.knee.value = 8; SND.lim.ratio.value = 10; SND.lim.attack.value = .004; SND.lim.release.value = .2; SND.master.connect(SND.lim); SND.lim.connect(c.destination);   /* louder overall, the limiter keeps stacked notes from clipping (user, 2026-11-19: nothing was audible) */\n  SND.sfxGain = c.createGain(); SND.sfxGain.gain.value = 2.4;")
# 2) 배경음 음량
for a, b in (("skip:.35, bass:false, level:.32}", "skip:.35, bass:false, level:1.5}"), ("skip:.2,  bass:true,  level:.32}", "skip:.2,  bass:true,  level:1.5}"),
             ("level:.36, drone:true}", "level:1.4, drone:true}"), ("level:.3, pulse:true}", "level:1.2, pulse:true}")): rep(a, b)
# 3) 새 소리: 글자 소리(인물·보이드), 보이드 등장음
rep("  if(SND.log){ SND.log.push(name);", "  if(SND.log && name !== 'type' && name !== 'vtype'){ SND.log.push(name);")
rep("    case 'arrive':    SND.lastVoid = t;",
    "    case 'type':      tone({f:(SND.tf || 520) * (1 + Math.random()*.07), type:'triangle', dur:.045, g:.035}); break;   /* a line being typed: one soft tick every few letters, pitched by who speaks */\n"
    "    case 'vtype':     tone({f:1480 + Math.random()*260, type:'square', dur:.024, g:.011, lp:3200}); break;\n"
    "    case 'voidIn':    SND.lastVoid = t; [[76, 0], [83, .07], [88, .14], [95, .23]].forEach(([m, d], i)=> tone({f:midiHz(m), type:i === 3 ? 'sine' : 'triangle', t0:t + d, dur:i === 3 ? .55 : .14, g:i === 3 ? .07 : .09})); tone({f:300, f2:1500, type:'square', dur:.2, g:.02, lp:2600}); for(let i = 0; i < 4; i++) tone({f:2400 + Math.random()*2200, t0:t + .26 + i*.05, dur:.2, g:.03}); break;   /* Void's window opening */\n"
    "    case 'arrive':    SND.lastVoid = t;")
rep("function voidShow(text, pose='say', ms=0){ try{ sfx('void'); }catch(e){}", "function voidShow(text, pose='say', ms=0){ try{ sfx($('voidVn').dataset.on ? 'void' : 'voidIn'); }catch(e){}")
rep("voidTyping = setInterval(()=>{ k++; dlShow(p, text, k);", "voidTyping = setInterval(()=>{ k++; if(k % 3 === 1) try{ sfx('vtype'); }catch(e){} dlShow(p, text, k);")
rep("vn.typing = setInterval(()=>{ k++; dlShow(p, L.text, k);", "SND.tf = ({'자일로':340, '코덱스':235, '리코':640, '제로':500, '네이티':880})[L.who] || 520; vn.typing = setInterval(()=>{ k++; if(!L.nar && k % 3 === 1) sfx('type'); dlShow(p, L.text, k);")
# 4) 점프 (사용자 2026-11-19: "점프 좀 만들어줘 스페이스로"). Space가 다른 일(대사 넘기기·카드·미션 버튼·탐지)에 쓰이지 않았을 때만 뛴다.
rep("WALK_KEYS[e.code] = true; if(/^Arrow|^Key[WASDQE]$|^Space$/.test(e.code)) e.preventDefault(); });",
    "WALK_KEYS[e.code] = true; if(e.code === 'Space' && !e.repeat && !e.defaultPrevented) walkJump(); if(/^Arrow|^Key[WASDQE]$|^Space$/.test(e.code)) e.preventDefault(); });\n"
    "function walkJump(){ const w = walk; if(!w || w.ride || w.fly || w.jv != null) return; if(vn || CTRL || MCARD || $('voidVn').dataset.on || qRewardEl.dataset.on || $('heroPick').dataset.on || performance.now() - VN_CLOSED < 250) return; if(mini && !$('miniBox').hidden) return; w.jv = 7.6; w.jy = 0; sfx('jump'); }   /* Space jumps (user, 2026-11-19); walls stay walls, only the height changes */")
rep("  const lift = w.fly ? 1.2 + Math.sin(now/520)*0.35 : 0;",
    "  if(w.jv != null){ w.jy += w.jv*dt; w.jv -= 24*dt; if(w.jy <= 0){ w.jy = 0; w.jv = null; sfx('land'); } }\n  const lift = w.fly ? 1.2 + Math.sin(now/520)*0.35 : (w.jy || 0);")
rep("    case 'arrive':    SND.lastVoid = t;",
    "    case 'jump':      tone({f:300, f2:620, type:'triangle', dur:.16, g:.06}); break;\n    case 'land':      noise({f0:260, f1:120, dur:.09, g:.07, q:1}); break;\n    case 'arrive':    SND.lastVoid = t;")
rep("'방향키로 걷기 · Shift 달리기 · 화면 끌어 둘러보기'", "'방향키로 걷기 · Shift 달리기 · Space 점프 · 화면 끌어 둘러보기'")
# (조작 안내 카드에 점프를 그려 넣는 것은 하지 않았다: 화면 디자인 변경이라 사용자가 정하면 따로 한다. 연구실 게임 10% 완화(STG)와 vtype 음량은 이 패치 뒤 직접 고쳤다.)
# 5) 걷는 중·장면 중에는 화면을 눌러도 아무것도 고르지 않는다 (사용자 2026-11-19: "퀘스트 도중에 화면 클릭하면 융합교육관이 왜 뜨는 거임? 아무 일 없게 막아놔")
rep("if(inside) insideClick(e); else { const i=pick(e); select(i, i>=0 && !walk); } }", "if(walk || actBusy || STAGED){ /* nothing is picked while walking or in a scene */ } else if(inside) insideClick(e); else { const i=pick(e); select(i, i>=0 && !walk); } }")
rep("  if(e.pointerType!=='mouse' || e.buttons || inside) return;\n  const i = pick(e);", "  if(e.pointerType!=='mouse' || e.buttons || inside) return;\n  if(walk){ if(hovered !== -1){ hovered = -1; renderer.domElement.style.cursor = ''; paint(); } return; }\n  const i = pick(e);")
# 6) 섬의 처음 시간은 가장 밝은 한낮 (사용자 2026-11-19: "제일 밝을 때로 맨 처음 설정"). 그 뒤로는 전처럼 흐른다.
rep("let flowHour = QS.get('hour') ? +QS.get('hour') : (new Date().getHours() + new Date().getMinutes()/60);", "let flowHour = QS.get('hour') ? +QS.get('hour') : 12;   /* the island opens at its brightest (user, 2026-11-19); it used to open at the real clock, so an afternoon class began in a dim park */")
# 7) 롤러코스터 둘레 (사용자 2026-11-19: "최소 3미터는 떨어져 있는데도 접근이 안 됨"). 볼록 껍질은 8m 높이의 선로까지 넣어 북쪽 9m·모서리 10m 넘게 빈 땅을 막았다.
#    몸 높이(땅에서 0.3~2.5m)에 실제로 있는 꼭짓점만 모아, 5m 안쪽 틈은 메우고 바깥 윤곽은 그대로 따르는 모양으로 막는다.
rep("    IB.forEach(b=>{ if(b.c !== 'ride' || !b.mesh || ELEVATED.has(b.label)) return; const base = groundY(b.cx, b.cz), pts = [];",
    "    const TIGHT = new Set(['롤러코스터']);   /* a long open ride: its convex hull also took the ground beside it (user, 2026-11-19) */\n"
    "    const tightFill = b=>{ const R = 5, P = []; let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;\n"
    "      b.mesh.traverse(m=>{ if(!(m.isMesh || m.isInstancedMesh) || !m.visible || !m.geometry || !m.geometry.attributes.position) return; const pos = m.geometry.attributes.position, n = m.isInstancedMesh ? m.count : 1;\n"
    "        for(let k = 0; k < n; k++){ if(m.isInstancedMesh){ m.getMatrixAt(k, _wgM); _wgM.premultiply(m.matrixWorld); } else _wgM.copy(m.matrixWorld);\n"
    "          for(let i = 0; i < pos.count; i++){ va.fromBufferAttribute(pos, i).applyMatrix4(_wgM); const gy = groundY(va.x, va.z); if(va.y > gy + 0.3 && va.y < gy + 2.5){ const px = Math.floor(va.x), pz = Math.floor(va.z); P.push(px, pz); if(px < x0) x0 = px; if(px > x1) x1 = px; if(pz < z0) z0 = pz; if(pz > z1) z1 = pz; } } } });\n"
    "      if(P.length < 6) return false; const ox = x0 - R - 2, oz = z0 - R - 2, w = x1 - x0 + 2*R + 5, h = z1 - z0 + 2*R + 5, fat = new Uint8Array(w*h), out = new Uint8Array(w*h), disc = [];\n"
    "      for(let dz = -R; dz <= R; dz++) for(let dx = -R; dx <= R; dx++) if(dx*dx + dz*dz <= R*R) disc.push(dx, dz);\n"
    "      for(let i = 0; i < P.length; i += 2){ const cx = P[i] - ox, cz = P[i + 1] - oz; if(fat[cz*w + cx] === 2) continue; fat[cz*w + cx] = 2; for(let d = 0; d < disc.length; d += 2){ const j = (cz + disc[d + 1])*w + cx + disc[d]; if(!fat[j]) fat[j] = 1; } }\n"
    "      const st = []; const put = i=>{ if(!fat[i] && !out[i]){ out[i] = 1; st.push(i); } }; for(let x = 0; x < w; x++){ put(x); put((h - 1)*w + x); } for(let z = 0; z < h; z++){ put(z*w); put(z*w + w - 1); }\n"
    "      while(st.length){ const i = st.pop(), x = i % w; if(x > 0) put(i - 1); if(x < w - 1) put(i + 1); if(i >= w) put(i - w); if(i + w < w*h) put(i + w); }\n"
    "      for(let z = R; z < h - R; z++) for(let x = R; x < w - R; x++){ let near = false; for(let d = 0; d < disc.length && !near; d += 2) if(out[(z + disc[d + 1])*w + x + disc[d]]) near = true; if(!near && inb(x + ox, z + oz)) a[at(x + ox, z + oz)] = 1; }\n"
    "      return true; };\n"
    "    IB.forEach(b=>{ if(b.c !== 'ride' || !b.mesh || ELEVATED.has(b.label)) return; if(TIGHT.has(b.label) && tightFill(b)) return; const base = groundY(b.cx, b.cz), pts = [];")
assert '\r' not in s
p.write_bytes(s.encode('utf-8')); print('patched', n0, '->', len(s))
