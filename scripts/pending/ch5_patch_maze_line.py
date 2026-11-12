# 2026-11-12 (사용자): 미로는 「네이티가 안으로 끌려 들어갔다」가 아니라 「이 미로 어딘가에 네이티가 있지 않을까?」 하고 찾는 것. 페이지와 대본을 같이 고친다.
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]
PAIRS = [('미로야. 네이티가 이 안으로 끌려 들어간 것 같아.', '미로야. 이 미로 어딘가에 네이티가 있지 않을까?'),
         ('저 울타리 안쪽에서 뭔가 깜빡여.', '여기 미로가 있네.'),
         ('들어가 보자!', '들어가서 찾아보자!')]
p = R / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
i = s.rindex('"mazeEntrance": ['); j = s.index(']', i); blk = s[i:j]
for a, b in PAIRS:
    assert blk.count(a) == 1, a; blk = blk.replace(a, b)
s = s[:i] + blk + s[j:]
a = "'미로 한가운데까지 가 보자. 네이티는 미로 안으로 끌려 들어갔어.'"; assert s.count(a) == 1; s = s.replace(a, "'이 미로 어딘가에 네이티가 있을지도 몰라. 한가운데까지 가 보자.'")
p.write_bytes(s.encode('utf-8'))
p = R / 'docs/chapter05_script.md'; s = p.read_bytes().decode('utf-8')
for a, b in PAIRS[:2]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
k = s.index('- 리코: 미로야. 이 미로 어딘가에'); k2 = s.index('- 제로: 들어가 보자!', k); assert k2 - k < 120; s = s[:k2] + '- 제로: 들어가서 찾아보자!' + s[k2 + len('- 제로: 들어가 보자!'):]
p.write_bytes(s.encode('utf-8')); print('ok')
