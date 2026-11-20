# 시험 서버(8096, 저장소 data는 안 건드리는 임시 폴더)와 정적 서버(8097)를 띄운 채 다른 점검 스크립트를 돌리고, 끝나면 둘 다 끈다.
# python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_check_naty_chase.py <인자...>
import os, shutil, subprocess, sys, tempfile, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
tmp = tempfile.mkdtemp(prefix='ch5srv_')
for fn in ['ch5_void_server.py', 'ch5_void_pairs.json', 'spz2splat.py']:
    p = os.path.join(ROOT, 'server', fn)
    if os.path.exists(p): shutil.copy(p, tmp)
env = dict(os.environ, VOID_PORT='8096', VOID_STATIC='0', CH5_ADMIN_KEY='0101', PYTHONUTF8='1')
a = subprocess.Popen([sys.executable, 'ch5_void_server.py'], cwd=tmp, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
b = subprocess.Popen([sys.executable, '-m', 'http.server', '8097', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(2.5)
    code = subprocess.call([sys.executable, '-X', 'utf8'] + sys.argv[1:], cwd=ROOT)
finally:
    a.kill(); b.kill(); time.sleep(.5); shutil.rmtree(tmp, ignore_errors=True)
sys.exit(code)
