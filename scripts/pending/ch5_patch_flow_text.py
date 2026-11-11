# 2026-11-11 활동 흐름 점검에서 나온 어색한 곳 정리(사용자: 섬 기록 2·4는 아직 안 만든 구간이라 그대로, 그 밖의 이상한 부분 수정)
# 사용: python ch5_patch_flow_text.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s

def swap(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)

# 2막: 화면은 4 / 5인데 「두 개」
swap('기록이 두 개 모였으니', '기록이 네 개 모였으니')
# 미로는 관람차가 아니라 정문 옆에 있다
swap('관람차 뒤쪽 길', '정문 옆 길', 7)
# 미션 4: 잔재는 미션 3에서 「계산을 어지럽히는 것」으로 정리됐고, 연구실에서 양 시험은 하지 않는다. 「조금씩」의 근거는 미션 1의 전원 장면.
swap('선대의 잔재는 부쉈다고 들었다', '선대의 잔재는 해체했다고 들었다')
swap('그대로 두면 일루아를 돌려줘도 다시 끌려가니까요', '그대로 두면 시뮬레이션을 믿을 수 없으니까요')
swap('자일로의 시험 기록에서 한꺼번에 많이 보냈을 때 기구가 제멋대로 움직였잖아', '전원이 한꺼번에 들어왔을 때 일루아가 크게 흔들렸잖아')
swap('흐름을 가로채던 잔재도 이미 없앴어', '계산을 어지럽히던 잔재도 이미 없앴어')
swap('연구실에서 봤던 반응이야. 한 번에 보내는 양을 다시 봐', '전원이 한꺼번에 들어왔을 때와 같은 반응이야. 한 번에 보내는 양을 다시 봐')
swap('흐름을 방해하던 선대의 잔재는 제거했습니다', '시뮬레이션을 어지럽히던 선대의 잔재는 해체했습니다')
swap('선대의 잔재 제거 완료', '선대의 잔재 해체 완료')
# 안내 상자: 「MISSION 1 / 3」은 단계였다 → 라벨 「미션 N」 + 단계 a / b, 미션 1의 분모는 처음부터 4
swap("$('qhT').textContent = q.title; $('qhHint').textContent = q.hint; $('qhStep').textContent = '1 / 3';",
     "$('qhT').textContent = q.title0 || q.title; $('qhHint').textContent = q.hint; $('qhStep').previousSibling.textContent = `미션 ${QUESTS.indexOf(q) + 1} `; $('qhStep').textContent = q.mini === 'loop' ? '1 / 4' : '1 / 3';")
# 미션 3: 잔재 이야기가 나오기 전에는 제목에 잔재를 쓰지 않는다(중간 점검 뒤 miniHud가 원래 제목으로 바꾼다)
swap("title:'숨겨진 잔재를 찾아라', hint:'관람차 언덕 아래 연구실'", "title:'숨겨진 잔재를 찾아라', title0:'지금까지의 기록을 확인하라', hint:'관람차 언덕 아래 연구실'")
# 알림: 처음 열릴 때만 「시점이 열렸습니다」, 환원 뒤에는 남은 미션이 없다
swap("if(opened.length) setTimeout(()=> toast(`${opened.join('·')} 시점이 열렸습니다. 도로랜드 섬에서 다음 미션을 이어가세요`), 1200);",
     "if(opened.length) setTimeout(()=> toast(QDONE.has('q3') ? '환원을 마쳤습니다. 이제 여러 시점으로 섬을 자유롭게 탐험할 수 있어요' : QDONE.size ? '도로랜드 섬에서 다음 미션을 이어가세요' : `${opened.join('·')} 시점이 열렸습니다. 도로랜드 섬에서 다음 미션을 이어가세요`), 1200);")
# 예비 배전선 성공 버튼: 터치 기기에서는 「탭」
swap("$('voidNext').textContent = matchMedia('(pointer:coarse)').matches ? '탭 ▸ 다음' : 'Space ▸ 다음';",
     "$('voidNext').textContent = matchMedia('(pointer:coarse)').matches ? '탭 ▸ 다음' : 'Space ▸ 다음'; $('ydContinue').textContent = matchMedia('(pointer:coarse)').matches ? '탭 ▸ 계속' : 'Space ▸ 계속';")
# 시뮬레이터 머리: 「채운 기록 4 / 5」 옆에 「4 / 5」가 또 나왔다
swap("`채운 기록 ${SIM_LIT} / 5`", "'누락 기록 수집 중'")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
