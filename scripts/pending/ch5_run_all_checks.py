# 보이드의 기록 전체 점검: 점검 스크립트를 한 번에 하나씩 차례로 돌리고 결과를 한 파일에 모은다(무거운 작업은 겹치지 않게).
#  python -X utf8 scripts/pending/ch5_run_all_checks.py <결과 폴더> [어셈블리 STL]
#  two = 시험 서버(임시 폴더, 8096) + 정적 서버(8097) / one = 저장소 서버(8096, 파일도 서빙; 끝나면 server/data/ch5_void.json·vikings 지움)
import os, shutil, subprocess, sys, tempfile, time, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); PD = os.path.join(ROOT, 'scripts', 'pending'); OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
STL = sys.argv[2] if len(sys.argv) > 2 else None; S = lambda n: os.path.join(OUT, n)
TWO = [('ch5_check_1119', []), ('ch5_check_admin_stage', []), ('ch5_check_baked', []), ('ch5_check_reach', []), ('ch5_check_park_power', []), ('ch5_check_layout', []), ('ch5_check_place_names', []),
       ('ch5_check_reset_overlap', []), ('ch5_check_tut_spotlight', [S('tut')]), ('ch5_check_flowlock_tut', [S('flowlock')]), ('ch5_check_dialogue_lines', [S('lines')]), ('ch5_check_one_walker', [S('walker')]),
       ('ch5_check_reentry', []), ('ch5_check_snd_btn', [S('snd')]), ('ch5_check_lab_gate', [S('labgate')]), ('ch5_check_naty_chase', [S('chase')]), ('ch5_check_coords', [S('coords.png')]), ('ch5_check_found_gap', [S('gap')]),
       ('ch5_check_admin_steps', [S('admsteps')]), ('ch5_check_admin_mode', [])]   # lab_slice(옛 30개 기준)는 뺌: 연구실 게임은 batch_1118이 본다
if STL: TWO += [('ch5_check_viking_mission', [STL, S('viking')]), ('ch5_check_viking_assembly', [STL])]
ONE = [('ch5_flow_log', [S('flow')]), ('ch5_check_batch_1118', [S('b1118')]), ('ch5_check_cave_choice', [S('choice')]), ('ch5_check_ctrl_card', [S('ctrl')]), ('ch5_check_maze_solve', ['8096']),
       ('ch5_check_sfx', []), ('ch5_check_sim_chain', [S('simchain')]), ('ch5_check_reward_small', [S('reward')]), ('ch5_audit_blackout', ['8096', S('blackout')]), ('ch5_audit_paths', ['8096', S('paths.json')]),
       ('ch5_audit_walk', ['8096', S('walk.json')]), ('ch5_audit_ride_pass', [S('ridepass')]), ('ch5_audit_track', ['8096'])]
ENV = dict(os.environ, PYTHONUTF8='1', CH5_ADMIN_KEY='0101', VOID_PORT='8096')
def kill(p):
    if p and p.poll() is None: subprocess.call(['taskkill', '/T', '/F', '/PID', str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def run(mode, name, args):
    tmp = None; procs = []
    try:
        if mode == 'two':
            tmp = tempfile.mkdtemp(prefix='ch5srv_')
            for fn in ['ch5_void_server.py', 'ch5_void_pairs.json', 'spz2splat.py']:
                p = os.path.join(ROOT, 'server', fn)
                if os.path.exists(p): shutil.copy(p, tmp)
            procs.append(subprocess.Popen([sys.executable, 'ch5_void_server.py'], cwd=tmp, env=dict(ENV, VOID_STATIC='0'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            procs.append(subprocess.Popen([sys.executable, '-m', 'http.server', '8097', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        else:
            procs.append(subprocess.Popen([sys.executable, os.path.join('server', 'ch5_void_server.py')], cwd=ROOT, env=dict(ENV, VOID_STATIC='1'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(2.5); t0 = time.time(); log = open(S(name + '.log'), 'w', encoding='utf-8', errors='replace')
        c = subprocess.Popen([sys.executable, '-X', 'utf8', os.path.join(PD, name + '.py')] + args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
        try: code = c.wait(timeout=560)
        except subprocess.TimeoutExpired: kill(c); code = 'TIMEOUT'
        log.close(); return code, round(time.time() - t0)
    finally:
        for p in procs: kill(p)
        time.sleep(1.2)
        if tmp: shutil.rmtree(tmp, ignore_errors=True)
        if mode == 'one':
            f = os.path.join(ROOT, 'server', 'data', 'ch5_void.json')
            if os.path.exists(f): os.remove(f)
            shutil.rmtree(os.path.join(ROOT, 'server', 'data', 'vikings'), ignore_errors=True)
res = []; PICK = [x for x in os.environ.get('CH5_ONLY', '').split(',') if x]
for mode, lst in (('two', TWO), ('one', ONE)):
    for name, args in lst:
        if PICK and name not in PICK: continue
        code, sec = run(mode, name, args); txt = open(S(name + '.log'), encoding='utf-8', errors='replace').read()
        fails = [l.strip()[:200] for l in txt.splitlines() if l.strip().startswith('FAIL') or 'Traceback' in l or l.strip().startswith('NG ')]
        res.append({'name': name, 'code': code, 'sec': sec, 'ok': txt.count('\nOK ') + txt.startswith('OK '), 'fails': fails[:12], 'tail': txt.strip().splitlines()[-3:]})
        json.dump(res, open(S('_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(name, code, sec, len(fails), flush=True)
print('ALL DONE', len(res))
