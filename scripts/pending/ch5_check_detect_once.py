# 2026-11-18: 미션 4 탐지 안내 확인. ch5_flow_log.py 를 그대로 가져와 잔재 찾기만 건너뛰지 않고 실제로 탄다.
#  ① 탑승 대사에 새 문장이 뜨는지(그림) ② 안내가 「지금! 「탐지」」일 때 버튼을 한 번 눌러 잔재 부수기가 시작되고 기회가 줄지 않는지.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_check_detect_once.py <결과 폴더>   (미션 4 시작 단계 7부터 돈다)
import io, sys, pathlib
src = io.open(pathlib.Path(__file__).with_name('ch5_flow_log.py'), encoding='utf-8').read()
def rep(a, b):
    global src; assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
rep("'바이킹 올리기', '잔재 찾기', ", "'바이킹 올리기', ")
rep("SHOT_SAY = ('됐다! 우리가 만든', '잘 움직이네요')", "SHOT_SAY = ('뜨면 「탐지」',)")
rep("            elif s['skip'] and any(k in s['skip'] for k in STEP_SKIPS):",
    "            elif '지금! 「탐지」' in s['hud'] and not last.get('pressed'):\n"
    "                last['pressed'] = 1; w('DETECT', '안내가 지금! → 한 번 누름 | 누르기 전: ' + s['mini']); await pg.hover('#miniGo'); await pg.mouse.down(); await asyncio.sleep(HOLD); await pg.mouse.up(); await asyncio.sleep(6.0)\n"   # 누름은 프레임마다 읽는다: 누르고 떼기를 같은 순간에 보내면(click) 못 읽는다
    "                s2 = await pg.evaluate(SNAP); w('DETECT', f\"누른 뒤: 부수기 시작={bool(s2['rem'])} vn={s2['vn'][:40]} mini={s2['mini']}\"); await shot('after_press')\n"
    "                print('DETECT_RESULT', bool(s2['rem']) or '찾았다' in s2['vn'] or s2['mini'] == '', '| before', s['mini'], '| after', s2['mini']); break\n"
    "            elif s['mini'].startswith('찾은 잔재') and s['walk']: await asyncio.sleep(.05)\n"
    "            elif s['skip'] and any(k in s['skip'] for k in STEP_SKIPS):")
HOLD = float(sys.argv[2]) if len(sys.argv) > 2 else 0.12   # 누르고 있는 시간(초)
sys.argv = [sys.argv[0], sys.argv[1], '7']
exec(compile(src, 'ch5_flow_log(detect)', 'exec'))
