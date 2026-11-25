"""2026-11-25 사용자: ① 엔딩에서 코덱스가 일루아를 돌려놓는 게 아니라 허락만 하고, 돌려놓는 건 아이들 ② 지하 연구실에서 환원 버튼을 누르는 연출
③ 다 끝난 뒤 섬 버튼은 「미션 시작하기」가 아니라 「섬 탐험하기」."""
import json, re, sys
p = 'C:/Users/dlgus/break_out/chapter05/index.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s
    c = s.count(a)
    if c != 1:
        sys.exit(f'match {c}: {a[:80]}')
    s = s.replace(a, b)

# ① STORY.actual: Codex gives permission; the children do it, in the lab
OLD = '"actual":[{"who": "코덱스", "text": "이제 일루아를 본래 자리로 돌려놓겠다. 너희가 찾아낸 흐름대로."}, {'
i = s.index(OLD) + len('"actual":')
arr, end = json.JSONDecoder().raw_decode(s, i)
assert arr[0]['text'].startswith('이제 일루아를 본래 자리로') and arr[1]['who'] == '자일로', arr[:2]
arr = [{"who": "코덱스", "text": "일루아를 돌려놓는 건 너희 몫이다. 허락하마."},
       {"who": "코덱스", "text": "너희가 찾아낸 흐름대로, 본래 자리로 돌려놓아라."},
       {"who": "자일로", "text": "연구실로 가죠. 시뮬레이션에서 확인한 대로, 조금씩입니다."}] + arr[2:]
s = s[:i] + json.dumps(arr, ensure_ascii=False) + s[end:]

# ② the lab launch button, reused for the real restoration
rep("function simLaunch(){ if(ffOn() || reduce) return Promise.resolve();",
    "STORY.restoreLaunch = [{who:'자일로', text:'코덱스가 허락했어요. 이번엔 시뮬레이션이 아니라 진짜 환원입니다.'}, {who:'자일로', img:'xylo_point', text:'가운데 환원 버튼을 눌러 주세요!'}];   /* 2026-11-25 (user): the children start the restoration in the lab, 코덱스 only allows it */\n"
    "function simLaunch(lines = STORY.simLaunch, label = '시뮬레이션 가동', noGlyph = true){ if(ffOn() || reduce) return Promise.resolve();")
rep("LR_NOGLYPH = true; labRoomOpen(false); const R = labRoom(); let b = $('lrLaunch'); if(!b){ b = document.createElement('button'); b.type = 'button'; b.id = 'lrLaunch'; b.innerHTML = '<i></i><b>시뮬레이션 가동</b>'; R.d.appendChild(b); }",
    "LR_NOGLYPH = noGlyph; labRoomOpen(false); const R = labRoom(); let b = $('lrLaunch'); if(!b){ b = document.createElement('button'); b.type = 'button'; b.id = 'lrLaunch'; R.d.appendChild(b); } b.innerHTML = `<i></i><b>${label}</b>`;")
rep("setTimeout(()=> say(STORY.simLaunch, ()=>{ b.dataset.on = '1';", "setTimeout(()=> say(lines, ()=>{ b.dataset.on = '1';")
rep("R.d.dataset.launch = '1'; $('lrSt0').textContent = '시뮬레이션 가동';", "R.d.dataset.launch = '1'; $('lrSt0').textContent = label;")

# restoreShow: no staff-raising by Codex; the lab button instead
rep("""  const arm = CODEX.userData.armR, a0 = arm.rotation.x, eye0 = caveEye.material.color.clone(); sfx('power');
  await new Promise(r=>{ const t0 = performance.now(), step = ()=>{ const k = Math.min(1, (performance.now() - t0)/1400), e = k*k*(3 - 2*k); arm.rotation.x = a0 - 2.7*e; caveEye.material.color.copy(eye0).lerp(new THREE.Color(0x9ff6ff), e); caveEye.scale.setScalar(1 + 0.35*e);
    F.flare.position.set(CODEX.position.x, CODEX.position.y + 3.4, CODEX.position.z); F.flare.scale.setScalar(1.5 + 3.5*e); F.flare.material.opacity = 0.75*e; if(k < 1) requestAnimationFrame(step); else r(); }; requestAnimationFrame(step); });
  await wait(700);""",
"""  const arm = CODEX.userData.armR, a0 = arm.rotation.x, eye0 = caveEye.material.color.clone();
  await simLaunch(STORY.restoreLaunch, '환원 시작', false);   /* 2026-11-25 (user): the children press the button in the underground lab */
  await wait(300);""")

# ③ after everything, the island button says 「섬 탐험하기」
rep("function questPillTick(){ const el = $('questPill'); if(!el) return; let q = null;",
    "function questPillTick(){ const lw = $('lWalk'); if(lw){ const t = RESTORED_LOCAL || !!myEntry().restored ? '섬 탐험하기' : '미션 시작하기'; if(lw.textContent !== t) lw.textContent = t; }   /* 2026-11-25 (user) */\n  const el = $('questPill'); if(!el) return; let q = null;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
