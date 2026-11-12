# 2026-11-12 (사용자): 연구실 측정 설명은 「흐름이 꺾인다」가 아니라 「불안정한 흐름이 존재한다」. 페이지와 대본을 같이 고친다.
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]
PAIRS = [('왜 저기로 꺾여요? 기록에는 저런 길이 없는데.', '저쪽 흐름은 왜 저렇게 흔들려요?'),
         ('계산이 틀어지고 있어요. 섬 어딘가에서 무언가가 측정값을 어지럽히고 있습니다. 이대로면 다섯 기록을 다 모아도 시뮬레이션을 믿을 수 없어요.',
          '불안정한 흐름이 있어요. 섬 어딘가에서 무언가가 흐름을 어지럽히고 있습니다. 이대로면 다섯 기록을 다 모아도 시뮬레이션을 믿을 수 없어요.')]
for f in ['chapter05/index.html', 'docs/chapter05_script.md']:
    p = R / f; s = p.read_bytes().decode('utf-8')
    for a, b in PAIRS:
        assert s.count(a) == 1, (f, a[:20], s.count(a)); s = s.replace(a, b)
    if f.endswith('.md'):
        a = '- (시뮬레이터) 흐름 몇 줄기가 섬의 엉뚱한 곳으로 휘어 들어가다가 지지직 끊긴다. 휘는 자리 세 곳에 붉은 노이즈가 번진다. 다시 돌려도 매번 다른 곳으로 꺾인다.'
        assert s.count(a) == 1; s = s.replace(a, '- (시뮬레이터) 흐름 몇 줄기가 불안정하게 흔들리다가 지지직 끊긴다. 흔들리는 자리 세 곳에 붉은 노이즈가 번진다.')
    p.write_bytes(s.encode('utf-8'))
print('ok')
