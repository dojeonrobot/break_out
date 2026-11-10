# 2026-11-10 관리자 대시보드 개편: 상단 타일 4개 제거, 조별 진행은 조당 한 줄, 제출 기록은 필터 있는 한 표, 오른쪽은 접이식 고정 칸.
import sys
S, p = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8', newline='').read(); assert '\r\n' not in s
a = s.index('function adminHTML(){'); b = s.index('\n// preview ticks apply at once')
new = open(S + '/adm_new.js', encoding='utf-8').read().rstrip('\n')
s = s[:a] + new + s[b:]
css_anchor = '.adm .crow input,.adm .crow .cin .mini{min-height:44px}'
assert s.count(css_anchor) == 1
s = s.replace(css_anchor, css_anchor + ' ' + open(S + '/adm_new.css', encoding='utf-8').read().strip())
h = "  const aa = e.target.closest('[data-aact]');\n  if(aa){ e.stopPropagation(); adminAct(aa.dataset.aact); return; }"
assert s.count(h) == 1
s = s.replace(h, "  const af = e.target.closest('[data-afilt]'); if(af){ e.stopPropagation(); ADM_FILTER = af.dataset.afilt; renderAdmin(); return; }\n" + h)
hd = '<div class="ah"><div><small>ADMIN</small><h2>보이드의 기록 관리자</h2></div>'
assert s.count(hd) == 1
s = s.replace(hd, '<div class="ah"><div><h2>보이드의 기록 관리자</h2></div>')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok', len(s))
