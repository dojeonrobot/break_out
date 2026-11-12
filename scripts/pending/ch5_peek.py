# 한 줄이 긴 chapter05/index.html에서 패턴 주변만 잘라 본다. 사용: python ch5_peek.py <정규식> [앞 글자 수] [뒤 글자 수] [최대 건수]
import re, sys, pathlib
s = pathlib.Path(__file__).resolve().parents[2].joinpath('chapter05/index.html').read_text(encoding='utf-8')
pat = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv) > 2 else 80; b = int(sys.argv[3]) if len(sys.argv) > 3 else 200; mx = int(sys.argv[4]) if len(sys.argv) > 4 else 40
ms = list(re.finditer(pat, s)); print(len(ms), 'hits')
for m in ms[:mx]:
    ln = s.count('\n', 0, m.start()) + 1
    print(f'--- L{ln} @{m.start()}: ' + s[max(0, m.start() - a):m.end() + b].replace('\n', '⏎'))
