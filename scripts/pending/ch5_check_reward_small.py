# 2026-11-18: 낮은 화면(667x375)에서 미션 완료 카드의 「다음 캠퍼스 기록 보기」 버튼이 화면 안에 있는지. ch5_flow_log.py 를 작은 창으로 돌려 미션 2 완료 카드에서 잰다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_check_reward_small.py <결과 폴더> [너비 높이]
import io, sys, pathlib
src = io.open(pathlib.Path(__file__).with_name('ch5_flow_log.py'), encoding='utf-8').read()
W, Hh = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (667, 375)
def rep(a, b):
    global src; assert src.count(a) == 1, a[:60]; src = src.replace(a, b)
rep("viewport={'width': 1280, 'height': 800}", "viewport={'width': %d, 'height': %d}" % (W, Hh))
rep("            elif s['reward']:\n",
    "            elif s['reward'] and '좌표' in s['reward']:\n"
    "                await asyncio.sleep(1.6); await shot('reward_small'); r = await pg.evaluate(\"(()=>{ const b = document.getElementById('qrMap').getBoundingClientRect(), c = document.querySelector('#qReward .in').getBoundingClientRect(); return {btn:[Math.round(b.top), Math.round(b.bottom)], card:[Math.round(c.top), Math.round(c.bottom)], H:innerHeight, W:innerWidth}; })()\")\n"
    "                okk = r['btn'][0] >= 0 and r['btn'][1] <= r['H']; print('REWARD_SMALL', 'PASS' if okk else 'FAIL', r); await pg.click('#qrMap'); await asyncio.sleep(1.5); print('CLICKED world', (await pg.evaluate(SNAP))['world']); break\n"
    "            elif s['reward']:\n")
sys.argv = [sys.argv[0], sys.argv[1], '3']
exec(compile(src, 'ch5_flow_log(reward small)', 'exec'))
