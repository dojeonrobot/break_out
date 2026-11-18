# 2026-11-18 점검에서 찾은 문구 세 가지(사용자: 찾은 것 쭉 수정).  python ch5_patch_checkup_1118.py (한 번만)
#  A 미션 3 완료 카드의 다음 버튼이 「미션 4 · 숨겨진 잔재를 찾아라」로 잔재를 먼저 알림 → 찾아가는 구간은 목적지 문구(GO_TO: 「연구실로 가기」)로.
#  B 미션 4 완료 카드에서 자일로가 「마지막 캠퍼스 좌표입니다」 → 캠퍼스 이야기는 보이드만(미션 2 카드와 같은 틀).
#  C 네이티 장면의 해설 줄에 이름표 「네이티」가 뜸 → 해설 줄은 초상화만 두고 이름표를 숨김, 해설 표시가 빠진 두 줄에 표시 추가.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
def rep(a, b, n=1):
    global s; assert s.count(a) == n, (s.count(a), a[:70]); s = s.replace(a, b)
rep("$('qrMap').textContent=ready?(nextIsl(q)?`미션 ${QUESTS.indexOf(q)+2} · ${nextIsl(q).title}`:'다음 캠퍼스 기록 보기')",
    "$('qrMap').textContent=ready?(nextIsl(q)?(GO_TO[nextIsl(q).id]?GO_TO[nextIsl(q).id][0]:`미션 ${QUESTS.indexOf(q)+2} · ${nextIsl(q).title}`):'다음 캠퍼스 기록 보기')")
rep(" q5:{card:{who:'자일로',img:'xylo_talk',text:'마지막 캠퍼스 좌표입니다. 서둘러 주세요.'}}};", " q5:{card:{who:'보이드',img:'void',text:'캠퍼스로 가자. 마지막 기록을 채우러!'}}};")
rep("$('vnName').textContent = L.who || ''; $('vnName').hidden = !L.who;", "$('vnName').textContent = L.nar ? '' : L.who || ''; $('vnName').hidden = !L.who || !!L.nar;   /* a narration line keeps the portrait, not the name tag */")
rep('"text": "연구실 구석의 네이티가 다시 한번 크게 흩어졌다가 모인다.", "img": "naty_red"}', '"text": "연구실 구석의 네이티가 다시 한번 크게 흩어졌다가 모인다.", "img": "naty_red", "nar": true}')
rep('"text": "네이티의 빛은 여전히 붉게 흔들린다.", "img": "naty_red"}', '"text": "네이티의 빛은 여전히 붉게 흔들린다.", "img": "naty_red", "nar": true}')
io.open(P, "w", encoding="utf-8", newline="").write(s); print("patched")
