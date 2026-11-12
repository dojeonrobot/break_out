# 2026-11-12 (사용자): 3인칭 캐릭터 떨림이 실기기에서 여전하다 → 3인칭을 없애고 1인칭으로 시작한다. 캐릭터 고르기(제로·리코)는 남긴다.
#   또: 자일로를 찾았을 때 캐릭터가 자일로와 완전히 겹쳐 섰다 → 찾은 인물 앞 4.5 거리로 물러나 마주 본다(1인칭에서는 인물 몸속에 카메라가 들어가지 않게).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep("if(o && PAIR_NAMES.includes(o.n)){ HERO = o.n; FPV = !!o.fp; } }catch(e){} return HERO; }", "if(o && PAIR_NAMES.includes(o.n)){ HERO = o.n; FPV = true; } }catch(e){} return HERO; }   /* first person only (user, 2026-11-12: the third-person shake stayed on the tablets) */")
rep("function heroSave(n, fp){ HERO = n; FPV = !!fp;", "function heroSave(n, fp){ HERO = n; FPV = true;")
rep("heroSel = {n:HERO || '제로', fp:FPV}; heroCb = cb || null;", "heroSel = {n:HERO || '제로', fp:true}; heroCb = cb || null;")
rep('<div class="view" id="hpView" role="group" aria-label="시점"></div>', '<div class="view" id="hpView" role="group" aria-label="시점" hidden></div>')
rep('<button type="button" id="walkWho" hidden>캐릭터·시점</button>', '<button type="button" id="walkWho" hidden>캐릭터</button>')
rep("startWalk:(n)=>{ if(n === PAIR && !heroLoad()) heroSave('제로', false); startWalk(n); },", "startWalk:(n)=>{ if(n === PAIR && !heroLoad()) heroSave('제로', true); startWalk(n); },")
rep("  const tg = q.id === 'q1' ? XYLO : q.id === 'q3' ? CODEX : null; if(tg) tg.rotation.y = Math.atan2(walk.x - tg.position.x, walk.z - tg.position.z);   // the one found turns to the walker\n  walk.yaw = Math.atan2(tx - walk.x, tz - walk.z); walk.pitch = -0.05;",
    "  const tg = q.id === 'q1' || q.id === 'q4' ? XYLO : q.id === 'q3' ? CODEX : null;\n"
    "  if(tg){ const gx = tg.position.x, gz = tg.position.z; let dx = walk.x - gx, dz = walk.z - gz, d = Math.hypot(dx, dz);   /* never inside the one who was found: step back to 4.5 and face them (user, 2026-11-12) */\n"
    "    if(d < 4.5){ if(d < 0.05){ dx = Math.sin(tg.rotation.y); dz = Math.cos(tg.rotation.y); d = 1; } for(let k = 0; k < 8; k++){ const a = k*Math.PI/4*(k % 2 ? 1 : -1), ca = Math.cos(a), sa = Math.sin(a), x = gx + (dx*ca - dz*sa)/d*4.5, z = gz + (dx*sa + dz*ca)/d*4.5; if(!walkBlocked(x, z)){ walk.x = x; walk.z = z; walk.snap = true; walk.imx = walk.imz = 0; break; } } }\n"
    "    tg.rotation.y = Math.atan2(walk.x - gx, walk.z - gz); walk.yaw = Math.atan2(gx - walk.x, gz - walk.z); }   // the one found turns to the walker\n"
    "  else walk.yaw = Math.atan2(tx - walk.x, tz - walk.z);\n  walk.pitch = -0.05;")
P.write_bytes(s.encode('utf-8')); print('ok')
