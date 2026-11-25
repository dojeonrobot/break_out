"""Dump STORY dialogue keys from chapter05/index.html into a text file (keys in page order).
python -I scripts/pending/ch5_dump_story.py <out.txt> [key-regex]"""
import json, re, sys
src = open('C:/Users/dlgus/break_out/chapter05/index.html', encoding='utf-8').read()
out = sys.argv[1]; pat = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
story = {}
dec = json.JSONDecoder()
for m in re.finditer(r'const STORY = |Object\.assign\(STORY, ', src):
    try:
        obj, _ = dec.raw_decode(src, m.end())
    except ValueError:
        print('skip non-JSON at line', src.count('\n', 0, m.start()) + 1, src[m.end():m.end() + 60].replace('\n', ' '))
        continue
    story.update(obj)
with open(out, 'w', encoding='utf-8') as f:
    for k, lines in story.items():
        if pat and not pat.search(k):
            continue
        f.write(f'## {k}\n')
        for L in lines:
            if isinstance(L, dict):
                f.write(f"{L.get('who') or '(서술)'}: {L.get('text', '')}\n")
            else:
                f.write(f'{L}\n')
        f.write('\n')
print(len(story), 'keys:', ' '.join(story))
# cave choices (미션 5 설득 선택지)
m = re.search(r'const CAVE_CHOICE = ', src)
if m:
    choices, _ = dec.raw_decode(src, m.end())
    with open(out, 'a', encoding='utf-8') as f:
        f.write('## CAVE_CHOICE (벽화마다 코덱스 질문 → 선택지 → 코덱스 반응)\n')
        for i, c in enumerate(choices, 1):
            f.write(f"\n[{i}] 코덱스: {c['q']}\n")
            for o in c['opts']:
                f.write(f"  {'(정답)' if o.get('ok') else '(오답)'} {o.get('who')}: {o.get('text')}\n      → 코덱스: {o.get('re')}\n")

