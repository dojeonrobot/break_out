# 2026-11-19 밤: ① 롤러코스터 복구 연출 2초 짧게, 회전목마 1초 길게 ② 관리자 「시점 이동」 이름을 번호 + 장소 + 그 조 태블릿이 열렸을 때 하게 되는 일로
#  ③ 미션 카드 윗줄이 한글일 때(「다음 할 일」 등) 고정폭 글꼴·넓은 자간이라 깨져 보이던 것.  한 번만 적용: python scripts/pending/ch5_patch_1119c.py
import pathlib, re
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
rep("dur = m.id === 'dl-coaster' ? 3.8 : mode === 'rise' ? 2.6 : 3.0;", "dur = m.id === 'dl-coaster' ? 1.8 : m.id === 'dl-carousel' ? 4.0 : mode === 'rise' ? 2.6 : 3.0;   /* the coaster 2 s shorter, the carousel 1 s longer (user, 2026-11-19) */")
NAMES = [('튜토리얼 직후 (기록 1 찍기 전)', '① 캠퍼스 · 기록 1 스캔하기 (튜토리얼은 끝난 상태)'), ('기록 1 제출 직후 (1막 시작)', '② 기록 1 제출 직후 · 섬에서 하모니아 흐름 보기'), ('미션 1 시작 전', '③ 섬 · 미션 1 자일로 찾아가 전원 복구'), ('미션 2 시작 전', '④ 섬 · 미션 2 미로에서 네이티 찾기'),
         ('기록 2 찍기 전', '⑤ 캠퍼스 · 기록 2 스캔하기'), ('기록 2 제출 직후 (2막 시작)', '⑥ 기록 2 제출 직후 · 섬에서 회전목마 흐름 보기'), ('미션 3 시작 전', '⑦ 섬 · 미션 3 바이킹 모델 올리기'), ('미션 4 시작 전', '⑧ 섬 · 미션 4 연구실 게임과 잔재 찾기'),
         ('기록 3 찍기 전', '⑨ 캠퍼스 · 기록 3 스캔하기'), ('기록 3 제출 직후 (3막 시작)', '⑩ 기록 3 제출 직후 · 섬에서 문양 완성 보기'), ('미션 5 시작 전', '⑪ 섬 · 미션 5 동굴에서 코덱스 설득'), ('미션 5 끝 (환원 직전)', '⑫ 섬 · 환원 장면과 엔딩 영상')]
for a, b in NAMES: rep("['" + a + "', [", "['" + b + "', [")
rep("  if(!confirm(`${team}조를 「${g[0]}」 시점으로 옮깁니다.\\n", "  if(!confirm(`${team}조를 아래 시점으로 옮깁니다.\\n\\n${g[0]}\\n\\n")
# 미션 카드 윗줄: 한글이면 본문 글꼴
i = s.index("function missionCard(q0, ov){"); j = s.index("$('mcN').text", i); k = s.index(";", j)
print('mcN line:', s[j:k + 1][:200])
rep("#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}", "#missionCard small.ko{font:700 clamp(17px,2.2vw,22px)/1.3 var(--sans);letter-spacing:0;word-break:keep-all}\n#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}")
s = s[:k + 1] + " $('mcN').classList.toggle('ko', /[가-힣]/.test($('mcN').textContent));" + s[k + 1:]
p.write_bytes(s.encode('utf-8'))
c = pathlib.Path(__file__).with_name('ch5_check_admin_stage.py'); t = c.read_text(encoding='utf-8')
for a, b in NAMES: t = t.replace("'" + a + "'", "'" + b + "'")
c.write_text(t, encoding='utf-8'); print('ok')
