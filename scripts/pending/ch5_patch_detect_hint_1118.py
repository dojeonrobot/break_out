# 2026-11-18 (사용자): 미션 4 탐지 안내를 실제 조작에 맞춘다. 판정은 버튼을 처음 누른 순간 한 번이라 「꾹」이라고 하면 미리 누르고 있다가 기회만 잃는다.
# 탑승 대사(STORY.remRail) · 미션 이어하기 안내(STEP_LINE.rail) · 보이드의 '지금 할 일'(voidHelp q5) 세 곳. 판정과 기회 3회는 건드리지 않는다.  python ch5_patch_detect_hint_1118.py (한 번만)
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
OLD = "내 신호가 강해지면 「탐지」를 꾹 눌러 줘."
NEW = "화면에 ‘지금!’이 뜨면 「탐지」를 한 번 눌러 줘."
n = s.count(OLD); assert n == 3, n
for anchor in ('{"who": "보이드", "text": "' + OLD + '"}', "const STEP_LINE = {rail:'아일랜드 익스프레스를 타고 돌면서 찾자. " + OLD + "'", "`아일랜드 익스프레스를 타고 돌면서 찾자. " + OLD + " 지금 ${"):
    assert s.count(anchor) == 1, anchor
s = s.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("patched", n)
