# 2026-11-12 대본 반영(사용자 「반영해줘」): 「보이드」 버튼 도움말 세 줄을 대본 1절 문장 그대로.
#   네이티 발견 뒤(미션 2 끝, 캠퍼스 기록 2 전, 섬에서 누름) / 벽화를 읽는 중(동굴 단계) / 벽화를 다 읽은 뒤
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep(" return '누락된 내용을 모두 채웠어. 환원하기 전에 코덱스를 만나러 동굴로 가자.';\n}", " if(step==='cave')return '내 불빛으로 벽을 비춰 봐. 닳아서 비어 있는 장면이 아직 남아 있어.';\n return '누락된 내용을 모두 채웠어. 환원하기 전에 코덱스를 만나러 동굴로 가자.';\n}")
rep("await voidAsk('안전하게 돌아가는 방법을 찾았어. 이제 그 방법대로 진짜 일루아를 돌려줄 차례야.');openRestore();", "await voidAsk('코덱스가 환원을 허락했어. 시뮬레이터로 먼저 확인하고 진짜 일루아를 돌려주자.');openRestore();")
rep("await voidAsk(q?activityHelp(q):'ERICA 캠퍼스로 돌아가 카드에 안내된 다음 기록을 찍자.','idle');return;}", "await voidAsk(q?activityHelp(q):(QDONE.has('q2')&&!QDONE.has('q4')&&campusZone(2)&&!zoneMine(campusZone(2)))?'네이티의 빛이 가리킨 좌표를 카드에 띄워 뒀어. 그곳의 기록을 찍어 줘.':'ERICA 캠퍼스로 돌아가 카드에 안내된 다음 기록을 찍자.','idle');return;}")
P.write_bytes(s.encode('utf-8')); print('ok')
