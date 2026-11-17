# 2026-11-17 사용자: ① 기록이 돌아올 때 연출을 켠다 ② 미션(추격 등)을 하는 중에는 그것을 끝내기 전까지 다른 것을 못 하게. 한 번만 적용.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# ---- ① 기록 복귀 연출 ----
# 큰 화면·관리자 기기·조 없는 기기: 기록이 들어오는 순간. 조 태블릿: 막 연출 안에서(아래 arriveShow), 두 번 나오지 않게.
rep("const arriving = false;", "const arriving = !!(arrive && revealIds && revealIds.length) && (SCREEN || !TEAM || !!ADMIN_KEY);")
rep("function arriveFx(ids){\n  if(!ids.length) return; sfx('sparkle');", "function arriveFx(ids, force){\n  if(!ids.length) return; sfx('sparkle');")
rep("if(actBusy || vn || $('voidVn').dataset.on || $('recDone').dataset.on || walk) return;   // never during a dialogue, a scene or a walk (rideSync powers it up later)",
    "if(!force && (actBusy || vn || $('voidVn').dataset.on || $('recDone').dataset.on || walk)) return;   // never during a dialogue, a scene or a walk (rideSync powers it up later); an act calls it itself (force)")
rep("      ...powerSteps(m, ()=> w)];", "      ...(parkPowerOn() ? powerSteps(m, ()=> w) : [])];   /* no power, no lights and no motion: the ride only draws itself in (2026-11-17) */")
rep("  });\n  toast(zones.length === 1 ? `${zones[0].name} 구역의 기록이 돌아왔습니다` : `${zones.length}개 구역의 기록이 돌아왔습니다`);\n}",
    "  });\n  if(!force) toast(zones.length === 1 ? `${zones[0].name} 구역의 기록이 돌아왔습니다` : `${zones.length}개 구역의 기록이 돌아왔습니다`);\n}\n"
    "/* the act shows the record coming back on the island: light pillar, rings, the ride drawing itself in — and waits for it (user, 2026-11-17) */\n"
    "async function arriveShow(id){ const R = RIDE[id]; if(!R || reduce || W.id !== 'island' || simOn || ffOn()) return; try{ rideSet(id, false); arriveFx([id], true); }catch(e){ console.warn('arrive', e); return; }\n"
    "  const t0 = Date.now(); while(R.chain && Date.now() - t0 < 16000){ if(ffOn()){ rideSet(id, parkPowerOn()); return; } await new Promise(r=> setTimeout(r, 200)); } if(R.chain) rideSet(id, parkPowerOn()); await wait(500); }")
rep("  saveAct(n);\n  if(simOn) setSim(false); await wait(250);\n  await wait(250);\n  stageAt(ACT_STAGE[n], ACT_CAST[n]()); await wait(900);\n  say(ACT_STORY[n], ()=>{ actBusy = false; startWalk(ACT_WALKER[n]); });\n}",
    "  saveAct(n);\n  if(simOn) setSim(false); await wait(250);\n  await arriveShow(ACT_ZONE[n]);\n  await wait(250);\n  stageAt(ACT_STAGE[n], ACT_CAST[n]()); await wait(900);\n  say(ACT_STORY[n], ()=>{ actBusy = false; startWalk(ACT_WALKER[n]); });\n}")

# ---- ② 흐름 잠금: 미션을 걷는 중(끝내기 전)에는 나가기·Esc·캐릭터 바꾸기·보이드 안내 창이 끼지 않는다. 관리자 기기는 예외 ----
rep("function voidSay(text, ms=5200, pose='say'){ voidLast = text; if(tutStep >= 0 && tutStep < 99) return; if(voidWait) return; voidShow(text, pose, ms); }",
    "function flowHeld(){ try{ return !ADMIN_KEY && !!walk && !!questLive && !questDone(questLive); }catch(e){ return false; } }   /* a mission is being walked: nothing else until it is done (user, 2026-11-17) */\n"
    "function voidSay(text, ms=5200, pose='say', own){ voidLast = text; if(tutStep >= 0 && tutStep < 99) return; if(voidWait) return; if(!own && flowHeld()) return; voidShow(text, pose, ms); }")
rep("qPop('미션 이어하기'); voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say'); return true; }", "qPop('미션 이어하기'); voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); return true; }")
rep("$('walkX').onclick = ()=> stopWalk(true);", "$('walkX').onclick = ()=>{ if(flowHeld()){ toast('미션을 끝내면 나갈 수 있어요'); return; } stopWalk(true); };")
rep("if(e.key==='Escape'){ if(walk){ stopWalk(true); return; }", "if(e.key==='Escape'){ if(walk){ if(flowHeld()) return; stopWalk(true); return; }")
rep("$('walkWho').onclick = ()=>{ if(walk && walk.name === PAIR && !vn) heroPick(null); };", "$('walkWho').onclick = ()=>{ if(walk && walk.name === PAIR && !vn && !chase && !(mini && mini.kind !== 'chase' && !$('miniBox').hidden)) heroPick(null); };")
rep("c.last = now; if(c.over || vn) return;", "c.last = now; if(c.over || vn || $('voidVn').dataset.on) return;   /* nothing runs while a line covers the screen */")
rep("$('simBtn').onclick = ()=> setSim(!simOn);", "$('simBtn').onclick = ()=>{ if(actBusy || vn || $('voidVn').dataset.on) return; setSim(!simOn); };")
rep("setInterval(()=>{ try{ questPillTick(); }catch(e){}", "setInterval(()=>{ try{ questPillTick(); }catch(e){} try{ $('walkX').hidden = flowHeld(); }catch(e){}")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8'))
print('patched', len(s))
