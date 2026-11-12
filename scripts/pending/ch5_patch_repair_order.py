# 2026-11-12 (사용자 결정): 복구 순서 = 스캔 1 하모니아 → 스캔 2 회전목마(네이티가 멈춘 자리) → 연구실·잔재 미션 → 스캔 3 관람차.
#   사파리와 롤러코스터는 섬 미션으로 채워지는 두 자리(롤러코스터 = 미션 1 그대로, 사파리 = 미션 4 잔재 해체).
#   고치는 곳: 페이지(MISSIONS의 twin, MISSIONS_I의 quest, 막 2 무대, 대사), 대본, erica-twin/missions.json. 서버의 짝 파일은 erica-twin 재빌드가 만든다.
import pathlib, json
R = pathlib.Path(__file__).resolve().parents[2]
p = R / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep('"twin":"dl-ferris","lat":37.295565', '"twin":"dl-carousel","lat":37.295565')
rep('"twin":"dl-safari","lat":37.293614', '"twin":"dl-ferris","lat":37.293614')
rep("{id:'dl-safari',   name:'사파리',            ch:'챕터 1 · 신비한 초대',          brief:'사파리 주변과 원천 사이의 일루아 흐름을 확인하는 기록입니다.'},",
    "{id:'dl-safari',   name:'사파리',            ch:'챕터 1 · 신비한 초대',          brief:'섬에서 해당 자리의 기록을 채웁니다.', quest:'q5'},")
rep("{id:'dl-carousel', name:'회전목마', recordName:'미로 정원', ch:'챕터 3 · 잊혀진 시간 속으로',   brief:'섬에서 해당 자리의 기록을 채웁니다.', quest:'q2'},",
    "{id:'dl-carousel', name:'회전목마',          ch:'챕터 3 · 잊혀진 시간 속으로',   brief:'회전목마 뒤 정원 아래의 일루아 흐름을 확인하는 기록입니다.'},")
rep("const ACT_ZONE = {1:'dl-harmonia', 2:'dl-ferris', 3:'dl-safari'};", "const ACT_ZONE = {1:'dl-harmonia', 2:'dl-carousel', 3:'dl-ferris'};")
rep("const ACT_STAGE = {1:'dl-harmonia', 2:'dl-ferris', 3:'dl-ferris'};", "const ACT_STAGE = {1:'dl-harmonia', 2:'dl-carousel', 3:'dl-ferris'};")
PAIRS = [('이번에는 관람차 언덕 주변의 흐름을 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.', '회전목마 뒤 정원의 흐름을 확인했어. 네이티가 멈췄던 자리 아래로 일루아가 이어지고 있었어.'),
         ('사파리 주변의 흐름도 확인했어. 원천에서 나온 일루아가 사파리 아래로 이어지고 있었구나.', '관람차 언덕 주변의 흐름도 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.'),
         ('이 자리의 흐름을 기록했어. 흐름이 이어지는 쪽에서 트윈으로 이어진 캠퍼스 좌표도 찾았어.', '이 자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어. 거기서 기록을 채워야 해.')]
# the page keeps old copies of record2/record3 in the base STORY object (overwritten later): change the live ones (the last occurrence)
for a, b in PAIRS:
    i = s.rindex(a); s = s[:i] + b + s[i + len(a):]
p.write_bytes(s.encode('utf-8'))
p = R / 'docs/chapter05_script.md'; t = p.read_bytes().decode('utf-8')
def sub(a, b):
    global t
    assert t.count(a) == 1, (t.count(a), a[:40]); t = t.replace(a, b)
for a, b in PAIRS: sub(a, b)
sub('| 4 | 캠퍼스 | 하냥이 벤치 좌표에서 스캔 | 관람차 언덕 주변의 일루아 흐름 확인 | 2 / 5 (40%) |', '| 4 | 캠퍼스 | 두 번째 좌표에서 스캔 | 회전목마 뒤 정원(네이티가 멈춘 자리)의 일루아 흐름 확인 → 회전목마 복구 | (확정 필요) |')
sub('| 7 | 캠퍼스 | 카카오데이터센터의 라이언·어피치 스캔 | 사파리 주변과 원천 사이의 일루아 흐름 확인 |', '| 7 | 캠퍼스 | 마지막 좌표에서 스캔 | 관람차 언덕 주변의 일루아 흐름 확인 → 관람차 복구 |')
sub('두 번째 캠퍼스 기록 — 하냥이 벤치 ↔ 관람차 언덕 주변', '두 번째 캠퍼스 기록 ↔ 회전목마 뒤 정원 (2026-11-12 사용자: 네이티가 지나간 자리가 복구되므로 회전목마)')
sub('마지막 캠퍼스 기록 — 라이언·어피치 ↔ 사파리 주변', '마지막 캠퍼스 기록 ↔ 관람차 언덕 주변 (2026-11-12 사용자: 관람차는 연구실 미션 뒤에 복구)')
sub('1단계 「코덱스의 동굴로」 (마지막 캠퍼스 기록 복구와 사파리 장면 뒤)', '1단계 「코덱스의 동굴로」 (마지막 캠퍼스 기록 복구와 연구실 앞 장면 뒤)')
sub('- (확정 필요) 섬의 두 기록을 어디서 어떻게 채울지는 정하지 않았다.', '- (확정 필요) 섬 미션으로 채워지는 두 자리는 롤러코스터(미션 1)와 사파리(미션 4)로 두었다. 어떻게 채우는지 이야기는 정하지 않았다.')
p.write_bytes(t.encode('utf-8'))
m = pathlib.Path('C:/Users/dlgus/erica-twin/missions.json'); d = json.loads(m.read_text(encoding='utf-8'))
tw = {'z1': 'dl-harmonia', 'z2': 'dl-carousel', 'z3': 'dl-ferris'}
for x in d:
    if x['id'] in tw: x['twin'] = tw[x['id']]
m.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n'); print('ok')
