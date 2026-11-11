# 대본(docs/chapter05_script.md)의 대사 줄이 페이지(chapter05/index.html)에 글자 그대로 있는지 대조한다.
# 사용: python scripts/pending/ch5_script_diff.py [--all]   (기본: 미션 4 「동굴의 벽화」 구간은 건너뜀 — 게임을 새로 만들어야 하는 구간)
import re, sys, pathlib, difflib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[2]
sc = (ROOT / 'docs/chapter05_script.md').read_text(encoding='utf-8').split('\n')
pg = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8')
old = subprocess.run(['git', 'show', 'HEAD:docs/chapter05_script.md'], capture_output=True, cwd=ROOT).stdout.decode('utf-8')
cands = set()
for pat in (r'"((?:[^"\\\n]|\\.){6,260})"', r"'((?:[^'\\\n]|\\.){6,260})'", r'`([^`\n]{6,260})`'):
    cands |= set(re.findall(pat, pg))
cands = [c for c in cands if re.search('[가-힣]', c)]
sec = ''; rows = []; stats = {}
for i, l in enumerate(sc, 1):
    if l.startswith('## ') or l.startswith('### '): sec = l.strip('# ').strip()
    if '--all' not in sys.argv and sec.startswith('미션 4'): continue
    g = re.match(r'^\s*- \(지문\) (.+)$', l)
    m = re.match(r'^\s*(\d+)\. (.+)$', l) or re.match(r'^\s*- ([^:：(「]{1,14}): (.+)$', l)
    if not m and not g: continue
    who, t = ('지문', g.group(1)) if g else ('보이드', m.group(2)) if m.group(1).isdigit() else (m.group(1).strip(), m.group(2))
    t = re.sub(r'\([^)]*\)', '', t).strip()
    t = re.sub(r'^(보이드|자일로|리코|제로|코덱스): ', '', t)
    if len(t) < 6 or '{' in t: continue
    for p in [x.strip() for x in t.split(' / ')]:
        st = stats.setdefault(sec[:30], [0, 0]); st[0] += 1
        if any(q + p + q2 in pg for q, q2 in (('"', '"'), ("'", "'"), ('`', '`'), ('>', '<'))): st[1] += 1; continue   # exact line, not a substring of a longer one
        best = difflib.get_close_matches(p, cands, 1, 0.45)
        rows.append((sec[:16], i, who, p, best[0] if best else None, p in old))
for k, v in stats.items(): print(f'{v[1]:>3}/{v[0]:<3} {k}')
print()
for sec, i, who, p, b, o in rows:
    print(f"L{i} [{sec}] {who}{' (예전 대본에도 있던 줄)' if o else ''}\n   대본: {p}\n   화면: {b if b else '(비슷한 줄 없음)'}")
