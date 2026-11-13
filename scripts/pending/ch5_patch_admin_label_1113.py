# 2026-11-13 관리자 버튼의 「로그인 중」 표시를 「관리자 모드」로. 사용자가 로그인이 진행 중이라 안 넘어가는 것으로 읽었다(실제 뜻: 이 기기에 관리자로 로그인되어 있음).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8')
old = "#adminBtn::after{content:' 로그인 중'}"
assert s.count(old) == 1
P.write_bytes(s.replace(old, "#adminBtn::after{content:' 관리자 모드'}").encode('utf-8')); print('ok')
