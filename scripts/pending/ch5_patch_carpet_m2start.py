# 2026-11-12 (사용자)
#  1) 「입구 쪽 도로랜드 벽이랑 놀이기구가 겹친다」: 플라잉 카펫 터가 정문 오른쪽 탑·꽃 담장에 바짝 붙어 있었다 → 동쪽으로 9, 북쪽으로 6 옮김((110,375) → (119,369)), 들어가는 길 끝점도 같이.
#  2) 「미로로 가는 길이 너무 빙 돌아간다」: 미션 2가 정비동 문(롤러코스터 서쪽)에서 시작해 코스터를 돌아가야 했다(직선 590, 걸어서 795~977).
#     전원 연출이 끝나면 자일로 옆에서 대화하고 거기서 미션 2를 시작한다(자일로가 「네이티가 없어요」라고 말하는 장면과도 맞다).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70]); s = s.replace(old, new)
rep("place(carpetRide, 110/K, 375/K, 0.3);", "place(carpetRide, 119/K, 369/K, 0.3);   /* 2026-11-12: off the gate tower and the garden wall */")
rep("pickable(carpetRide, {n:'플라잉 카펫', c:'ride', sub:'스윙 라이드', cx:110/K, cz:375/K,", "pickable(carpetRide, {n:'플라잉 카펫', c:'ride', sub:'스윙 라이드', cx:119/K, cz:369/K,")
rep("PATHS[24]=[[85,380],[100,398],[108,404]];", "PATHS[24]=[[85,380],[97,385],[106,386]];")
rep("yard = null; TRAIN.lit = true; });", "yard = null; TRAIN.lit = true;\n"
    "    if(walk && XYLO_HIDE){ const p = freeSpot(XYLO_HIDE[0] - Math.sin(XYLO_HIDE[2])*7, XYLO_HIDE[1] - Math.cos(XYLO_HIDE[2])*7); walk.x = p[0]; walk.z = p[1]; walk.yaw = Math.atan2(XYLO_HIDE[0] - p[0], XYLO_HIDE[1] - p[1]); walk.snap = true; walk.imx = walk.imz = 0;\n"
    "      XYLO.rotation.y = Math.atan2(p[0] - XYLO_HIDE[0], p[1] - XYLO_HIDE[1]); } });   /* back beside 자일로 for his lines; mission 2 starts here, not behind the coaster (user, 2026-11-12) */")
P.write_bytes(s.encode('utf-8')); print('ok')
