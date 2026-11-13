# 2026-11-13 사용자 지시
#  ① 「돌아온 기록」이라는 말이 짜침 → 해결했다는 표시만: 「복구 완료」
#  ② 미션을 끝낸 놀이기구가 초록색으로 물드는 것(복구 구역 초록 발광) 삭제. 고르거나 가리킬 때의 밝아짐은 그대로
#  ③ 탐험에서 캐릭터를 나누지 않음: 제로·리코 고르는 창과 시점 고르는 창을 없애고, 섬에서는 「미션 시작하기」 하나로 시작
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
# ---- ① wording ----
rep('<small>RETURNED</small><h2>돌아온 기록</h2>', '<small>RESTORED</small><h2>복구 완료</h2>')
rep('아직 돌아온 기록이 없습니다.', '아직 복구한 곳이 없습니다.', 2)
rep("return W.id==='island' ? `<div class=\"twin\">돌아온 기록</div>`", "return W.id==='island' ? ''")
rep("'기록 돌아옴'", "'복구 완료'")
rep("(m.quest && !m.scans.length ? '✓ 미션으로 복구' : '✓ 돌아온 기록')", "'✓ 복구 완료'")
rep("t ? `ERICA ${t.name}에서 돌아온 기록` : '돌아온 기록'", "'복구 완료'")
rep("isl ? '돌아온 기록 ' : '복구 완료 '", "'복구 완료 '")
k1 = s.count('돌아온 기록'); s = s.replace('돌아온 기록', '복구 완료'); print('남은 「돌아온 기록」 치환', k1, '→', s.count('돌아온 기록'))
# ---- ② no green wash on a restored ride ----
rep("glow = (b.mission && RIDE[b.mission.id] ? RIDE[b.mission.id].pow : b.restored ? 1 : 0)*(0.10 + 0.14*g);", "glow = 0;   /* 2026-11-13 (user): a finished ride is not tinted green any more; the board shows what is done */")
# ---- ③ one walker, no picking ----
rep("if(name === PAIR && !HERO){ heroPick(()=> startWalk(name)); return; }   /* the first walk: choose who and how */", "if(name === PAIR && !HERO) heroSave('제로', true);   /* 2026-11-13 (user): the pair are one explorer, nobody is picked */")
rep("$('walkWho').hidden = name !== PAIR;", "$('walkWho').hidden = true;")
rep("$('walkName').textContent = name === PAIR ? HERO : name;", "$('walkName').textContent = name === PAIR ? '제로·리코' : name;")
rep("$('lWalk').onclick = ()=>{ renderWalkPick(); $('walkPick').dataset.on = '1'; };", "$('lWalk').onclick = ()=>{ if(walkerOpen(PAIR)) startWalk(PAIR); else toast(`탐험은 ${walkerWhy(PAIR)} 열립니다`); };")
rep("const gq = e.target.closest('[data-goquest]'); if(gq){ if(W.id !== 'island') setWorld('island'); renderWalkPick(); $('walkPick').dataset.on = '1'; return; }", "const gq = e.target.closest('[data-goquest]'); if(gq){ if(walkerOpen(PAIR)) startWalk(PAIR); else { if(W.id !== 'island') setWorld('island'); toast(`탐험은 ${walkerWhy(PAIR)} 열립니다`); } return; }")
rep("el.querySelector('b').textContent = `미션 ${n} ${resume ? '이어하기' : '시작하기'}`;", "el.querySelector('b').textContent = resume ? '미션 이어하기' : '미션 시작하기';")
rep('<button id="lWalk" class="island-only" type="button" hidden>탐험</button>', '<button id="lWalk" class="island-only" type="button" hidden>미션 시작하기</button>')
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
