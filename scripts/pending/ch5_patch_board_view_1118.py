# 2026-11-18 (사용자): 아일랜드 익스프레스 탑승 대사의 배경을 고친다. 계단 발치에서 계단을 마주 보고 서서 회색 계단이 화면 절반을 가렸다.
# 대사 전에 승강장이 트여 보이는 자리(sceneSpot, 계단 옆으로 비켜 선 20 거리)로 옮기고 승강장을 올려다보게 한다.  python ch5_patch_board_view_1118.py (한 번만)
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
a = "function remBoard(){ const w = walk; if(!w || !mini || mini.kind !== 'device' || ride) return; sfx('ride');\n"
assert s.count(a) == 1
b = a[:-1] + " if(STATION){ const b = STATION.board, sp = sceneSpot(b[0], b[1], 20, Math.atan2(-b[0], -b[1]) + BOARD_VIEW.side); w.x = sp[0]; w.z = sp[1]; w.yaw = Math.atan2(b[0] - sp[0], b[1] - sp[1]); w.pitch = BOARD_VIEW.pitch; w.snap = true; w.imx = w.imz = 0; }   /* an open view of the platform for the boarding lines, not the foot of the stairs (user, 2026-11-18) */\n"
s = s.replace(a, "const BOARD_VIEW = {side:-0.85, pitch:0.1};\n" + b)   # side 음수 = 간판 반대쪽(간판 기둥이 화면을 가리지 않는 쪽)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("patched")
