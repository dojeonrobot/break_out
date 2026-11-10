# 2026-11-10 대사에서 장소 이름 제거(융합교육관만 허용, 전시대 → 건물 어딘가). 관리자가 기록 좌표를 바꿀 수 있으므로.
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8', newline='').read()
assert '\r\n' not in s
R = [
 ('"name":"융합교육관 전시대","building":1471504923,"radius":80,"indoor":true,"brief":"가져간 인형이나 3D 출력물을 한 바퀴 돌며 스캔해 기록을 채우세요. 층·위치는 확정 전입니다."',
  '"name":"융합교육관","place":true,"building":1471504923,"radius":80,"indoor":true,"brief":"융합교육관 건물 어딘가에 있는 물건을 한 바퀴 돌며 스캔해 기록을 채우세요."'),
 ('"name":"하냥이 벤치","building":367646452,"radius":50,"brief":"라이언스홀 앞 벤치의 하냥이를 옆에 앉아 스캔해 기록을 채우세요."',
  '"name":"캠퍼스 기록 2","building":367646452,"radius":50,"brief":"카드의 좌표가 가리키는 자리로 가서, 거기 있는 것을 한 바퀴 돌며 스캔해 기록을 채우세요."'),
 ('"name":"카카오데이터센터","building":1524278252,"radius":60,"brief":"데이터센터 앞 라이언·어피치 피규어를 스캔해 기록을 채우세요."',
  '"name":"캠퍼스 기록 3","building":1524278252,"radius":60,"brief":"카드의 좌표가 가리키는 자리로 가서, 거기 있는 것을 한 바퀴 돌며 스캔해 기록을 채우세요."'),
 ("const ZONE_OBJ = {z1:'가져온 물건', z2:'하냥이', z3:'라이언이랑 어피치'};   // what sits at each spot (said only on arrival)",
  "const ZONE_OBJ = {z1:'가져온 물건'};   // what sits at each spot (said only on arrival). 2026-11-10: z2·z3 are not named, the operator may move their coordinates (rain, a closed path), so the dialogue never says what or where"),
 ("const zoneName = m => { const i = MISSION_E.indexOf(m) + 1; return i < 1 ? m.name : zoneFound(m) ? `기록 ${i} · ${m.name}` : `기록 ${i}`; };",
  "const zoneName = m => { const i = MISSION_E.indexOf(m) + 1; return i < 1 ? m.name : zoneFound(m) && m.place ? `기록 ${i} · ${m.name}` : `기록 ${i}`; };   // only a fixed place (z1) shows its name"),
 ("voidSay(`여기야. 이 자리의 기록은 ${ZONE_OBJ[m.id] || '이것'}이야. 한 바퀴 돌면서 꼼꼼하게 찍어 줘.`, 9000, 'joy');",
  "voidSay(ZONE_OBJ[m.id] ? `여기야. 이 자리의 기록은 ${ZONE_OBJ[m.id]}이야. 한 바퀴 돌면서 꼼꼼하게 찍어 줘.` : '여기야. 이 자리에 있는 걸 한 바퀴 돌면서 꼼꼼하게 찍어 줘.', 9000, 'joy');"),
 ("await voidAsk('지금 할 일은 기록 1이야. 이 건물 전시대에 있는 물건을 Scaniverse로 한 바퀴 돌면서 찍어.');",
  "await voidAsk('지금 할 일은 기록 1이야. 이 건물 어딘가에 있는 물건을 Scaniverse로 한 바퀴 돌면서 찍어.');"),
 ('{t:"첫 번째 좌표는 37.295655, 126.838475야. 지금 네가 있는 융합교육관이야.",pose:\'say\',world:\'erica\',',
  '{t:()=>{ const z = campusZone(1); return `첫 번째 좌표는 ${z && z.lat != null ? coordText(z) : \'카드에 있는 좌표\'}야. 지금 네가 있는 융합교육관이야.`; },pose:\'say\',world:\'erica\','),
 ('{t:"첫 번째 기록은 이 건물 전시대에서 반응하고 있어. 전시대로 가 봐.",pose:\'say\',world:\'erica\'},',
  '{t:"첫 번째 기록은 이 건물 어딘가에서 반응하고 있어.",pose:\'say\',world:\'erica\'},'),
 ("names = ['서쪽 숲 가장자리','하냥이 벤치','미로 정원','카카오데이터센터'];",
  "names = ['서쪽 숲 가장자리','캠퍼스 기록 2','미로 정원','캠퍼스 기록 3'];"),
 ("['서쪽 숲 가장자리 · 섬 지도',`하냥이 벤치 · ${coordText(campusZone(2))}`,'미로 정원 · 섬 지도',`카카오데이터센터 · ${coordText(campusZone(3))}`]",
  "['서쪽 숲 가장자리 · 섬 지도',`캠퍼스 기록 2 · ${coordText(campusZone(2))}`,'미로 정원 · 섬 지도',`캠퍼스 기록 3 · ${coordText(campusZone(3))}`]"),
 ("$('rdP').textContent = `${z ? z.name : '이 구역'}의 누락된 기록을 채웠습니다.`;",
  "$('rdP').textContent = z && z.place ? `${z.name}의 누락된 기록을 채웠습니다.` : `${n}번째 캠퍼스 기록을 채웠습니다.`;"),
]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:60])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched', len(R))
