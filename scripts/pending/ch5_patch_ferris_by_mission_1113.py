# 2026-11-13 (사용자: 「관람차쪽에서 작업하는게 섬 작업으로 완료되야 맞아」, 바이킹 미션은 원래 자리에 둠)
#  잔재 미션(q5) → 관람차 복구, 캠퍼스 기록 3(z3) → 사파리 복구. 2026-11-12의 「기록 3 = 관람차, 잔재 = 사파리」를 뒤집는다.
#  고치는 곳: 페이지(MISSIONS의 twin, MISSIONS_I의 quest, 막 3의 구역, record3 대사), 대본의 같은 대사, erica-twin/missions.json.
#  서버의 짝 파일(ch5_void_pairs.json)은 erica-twin 재빌드가 만든다 → server/로 복사해 voidrecord에 올리고 다시 시작.
#  3막 무대(ACT_STAGE[3])는 그대로 관람차 아래 연구실: 시뮬레이션을 돌리는 곳이기 때문.
import pathlib, json
R = pathlib.Path(__file__).resolve().parents[2]
P = R / 'chapter05/index.html'; s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)
rep('"twin":"dl-ferris","lat":37.293614', '"twin":"dl-safari","lat":37.293614')
rep("{id:'dl-safari',   name:'사파리',            ch:'챕터 1 · 신비한 초대',          brief:'섬에서 해당 자리의 기록을 채웁니다.', quest:'q5'},",
    "{id:'dl-safari',   name:'사파리',            ch:'챕터 1 · 신비한 초대',          brief:'사파리 아래에서 원천으로 이어지는 일루아 흐름을 확인하는 기록입니다.'},")
rep("{id:'dl-ferris',   name:'관람차',            ch:'챕터 4 · 구름 너머의 진실',     brief:'관람차 언덕 아래에서 해안으로 이어지는 흐름을 확인하는 기록입니다.'},",
    "{id:'dl-ferris',   name:'관람차',            ch:'챕터 4 · 구름 너머의 진실',     brief:'섬에서 해당 자리의 기록을 채웁니다.', quest:'q5'},   /* 2026-11-13 (user): the work round the wheel (lab, remnants) is what brings the wheel back; the last scan is the safari */")
rep("const ACT_ZONE = {1:'dl-harmonia', 2:'dl-carousel', 3:'dl-ferris'};", "const ACT_ZONE = {1:'dl-harmonia', 2:'dl-carousel', 3:'dl-safari'};")
OLD = '{"who": "보이드", "text": "관람차 언덕 주변의 흐름도 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어."}'
NEW = '{"who": "보이드", "text": "사파리 아래의 흐름도 확인했어. 원천에서 나온 일루아가 사파리 아래로 이어지고 있었어."}'
n = s.count(OLD); assert n == 1, n; s = s.replace(OLD, NEW)
P.write_bytes(s.encode('utf-8')); print('page ok', s.count('\r\n'))
sc = R / 'docs/chapter05_script.md'; t = sc.read_bytes().decode('utf-8'); a = '관람차 언덕 주변의 흐름도 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.'; print('script lines', t.count(a))
sc.write_bytes(t.replace(a, '사파리 아래의 흐름도 확인했어. 원천에서 나온 일루아가 사파리 아래로 이어지고 있었어.').encode('utf-8'))
m = pathlib.Path('C:/Users/dlgus/erica-twin/missions.json'); d = json.loads(m.read_text(encoding='utf-8'))
for x in d:
    if x['id'] == 'z3': x['twin'] = 'dl-safari'
m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n'); print('missions.json', [(x['id'], x['twin']) for x in d])
