# 2026-11-18 묶음 6 (전체 흐름 점검에서 찾은 것): 옛 기준 문장(빈 곳 개수·다섯 기록·시뮬레이터 표현) 정리, 미션 카드 위치 표기, 중복 안내 제거.
import io, re
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
log = []
def sub(a, b, need=1):
    global s
    c = s.count(a)
    log.append((c, a[:46]))
    assert c >= need, (c, a[:80])
    s = s.replace(a, b)
PAIRS = [
 # how many records are still empty is not said any more (user, 2026-11-18)
 ("아직 네 군데가 비어 있어. 얼른 나머지도 채우자!", "얼른 나머지 기록도 채우자!"),
 ("회전목마 뒤 정원의 흐름을 확인했어. 네이티가 멈췄던 자리 아래로 일루아가 이어지고 있었어.", "회전목마에서 롤러코스터까지 이어지는 흐름을 확인했어."),
 ("이제 비어 있는 기록은 하나뿐이야.", "네이티가 멈췄던 자리 아래로 일루아가 이어지고 있었구나."),
 ("이 섬의 다섯 곳의 기록이 누락돼서", "이 섬의 세 곳의 기록이 누락돼서"),
 # the lab shows an analysis screen, not the simulator; remnants are broken, not switched off
 ("지금까지 모은 기록으로 일루아의 흐름을 측정해 볼 거예요.", "지금까지 모은 기록으로 일루아의 흐름을 분석해 볼 거예요."),
 ("시뮬레이터를 켜 볼게요. ……또 이 게임이군요!", "분석 화면을 켜 볼게요. ……또 이 게임이군요!"),
 ("다시는 연구실 화면에 아무것도 깔지 마세요. 이제 시뮬레이터가 보입니다.", "다시는 연구실 화면에 아무것도 깔지 마세요. 이제 화면이 제대로 보입니다."),
 ("불안정한 흐름이 있어요. 섬 어딘가에서 무언가가 흐름을 어지럽히고 있습니다. 이대로면", "섬 어딘가에서 무언가가 흐름을 어지럽히고 있어요. 이대로면"),
 ("`신호 하나가 꺼졌어. 남은 건 ${left}개야.` : '마지막 신호까지 꺼졌어. 역으로 돌아가서 시뮬레이션을 다시 돌려 보자.'", "`잔재 하나를 부쉈어. 남은 건 ${left}개야.` : '마지막 잔재까지 부쉈어. 역으로 돌아가서 연구실에서 다시 확인하자.'"),
 ("`신호 하나가 꺼졌어. 남은 건 ${left}개야.` : '마지막 신호까지 꺼졌어. 연구실로 돌아가서 다시 돌려 보자.'", "`잔재 하나를 부쉈어. 남은 건 ${left}개야.` : '마지막 잔재까지 부쉈어. 연구실로 돌아가서 다시 확인하자.'"),
 ("mid:'연구실에서 시뮬레이션을 다시 보자.'", "mid:'관람차 아래 연구실로 가자.'"),
 ("'device-return':'연구실로 돌아가서 시뮬레이션을 다시 돌려 보자.'", "'device-return':'연구실로 돌아가서 흐름을 다시 확인하자.'"),
 ("'시뮬레이션이 다시 맞기 시작했어. 마지막 좌표에서 남은 기록 하나를 채우자.'", "'연구실에서 마지막 위치를 찾았어. 그 좌표에서 마지막 기록을 스캔하자.'"),
 # after Codex agrees there is no simulator step any more
 ("바로 시뮬레이터로 확인하고, 진짜 섬에 환원하자.", "이제 진짜 섬에 환원하자."),
 ("'코덱스가 환원을 허락했어. 시뮬레이터로 먼저 확인하고 진짜 일루아를 돌려주자.'", "'코덱스가 환원을 허락했어. 이제 진짜 섬에 일루아를 돌려주자.'"),
 ("'코덱스와 코덱스의 동굴로 가서 가상 시험을 통과하세요.'", "'코덱스의 동굴로 가서 코덱스를 설득하세요.'"),
 ("다섯 기록으로 원래 자리를 확인했습니다.<br>시뮬레이션을 어지럽히던 선대의 잔재는 해체했습니다.<br>원천에서 다섯 자리까지 조금씩 돌려보내는 시험에 성공했습니다.", "기록으로 원래 자리를 확인했습니다.<br>시뮬레이션을 어지럽히던 선대의 잔재는 부쉈습니다.<br>원천에서 섬 끝까지 조금씩 돌려보내는 시험에 성공했습니다."),
 ("'관람차 언덕 아래 출입금지 문'", "'관람차 언덕 아래'"),
 ("'관람차 언덕 아래 연구실 문'", "'관람차 언덕 아래'"),
]
for a, b in PAIRS: sub(a, b)
# the ending: the glyph was already noticed in act 3, so here Zero shows it to Codex
i = s.rindex('"ending":'); j = s.index("]", i)
seg = s[i:j]; assert "잠깐…… 이 모양, 코덱스 문양이잖아?" in seg
s = s[:i] + seg.replace("잠깐…… 이 모양, 코덱스 문양이잖아?", "코덱스, 보세요. 이 모양이 코덱스의 문양이에요!") + s[j:]
# mission card: the place line reads 「위치 : …」 (user, 2026-11-18); a card whose second line is an instruction passes plain:true
sub("$('mcH').textContent = q.hint || '';", "$('mcH').textContent = q.hint ? (q.plain ? q.hint : '위치 : ' + q.hint) : '';")
sub("await missionCard(q, {title0:null, hint:'알맞은 말을 골라 코덱스의 믿음을 얻으세요'});", "await missionCard(q, {title0:null, plain:true, hint:'알맞은 말을 골라 코덱스의 믿음을 얻으세요'});")
# after the lab the ride talk says the same thing the void pop said: once is enough
sub("missionCard(q, ov).then(()=>{ try{ voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); }catch(e){} }); return true; }", "missionCard(q, ov).then(()=>{ try{ if(st !== 'rail') voidSay(STEP_LINE[st] || STEP_LINE.found, 6000, 'say', true); }catch(e){} }); return true; }")
io.open(P, "w", encoding="utf-8", newline="").write(s)
for c, a in log: print(c, a)
left = [w for w in ("네 군데", "하나뿐", "다섯 곳", "다섯 기록", "다섯 자리", "측정해 볼", "신호 하나가 꺼졌", "시뮬레이터가 보입니다") if w in s]
print("still present:", left)
