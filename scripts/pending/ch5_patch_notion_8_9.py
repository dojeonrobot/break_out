"""노션 scan break 8·9번 (2026-11-25).
8: 보이드 대사 초상화를 조금 위로 — 대사 창 뒤에 숨는 잘린 선은 그대로 창 위쪽에 두고, 몸을 더 보여 준다(보이드만).
9: 복구 현황판이 100%일 때 제목·「펼치기」가 두 줄로 내려옴 → 한 줄 고정, 자리가 모자라면 숫자를 줄인다."""
import sys
p = 'C:/Users/dlgus/break_out/chapter05/index.html'
s = open(p, encoding='utf-8', newline='').read()
MARK = '</style></head><body>'
CSS = ('/* notion scan break 8·9 (2026-11-25) */'
       '@media (min-height:481px){#vn[data-speaker="보이드"] img{bottom:calc(118px - .28*min(74vh,620px));clip-path:inset(0 0 28% 0)}}'
       '#board .bh .x{white-space:nowrap}#board .bh h2{word-break:keep-all}'
       '#board .bh>div:first-child{min-width:0}'
       '#board .bh .acts{flex-shrink:0}'
       '#board.closed{width:max-content;max-width:calc(100vw - 32px)}'
       '#board.closed .bh h2{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}')
if 'notion scan break 8·9' in s:
    sys.exit('already patched')
if s.count(MARK) != 1:
    sys.exit('marker count %d' % s.count(MARK))
# the body's second <style> block holds later #board rules, so append at its end (first block would lose)
b2 = s.index('<style>', s.index(MARK))
end = s.index('</style>', b2)
line_start = s.rfind('\n', 0, end) + 1
s = s[:line_start] + CSS + '\n' + s[line_start:]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
