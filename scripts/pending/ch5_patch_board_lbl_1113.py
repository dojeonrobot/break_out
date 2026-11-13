# 2026-11-13: 현황판 복구율을 다른 화면과 같은 기준(채운 기록 / 5, 한 칸 20%)으로, 건물 이름 버튼의 처음 상태를 꺼짐으로
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70]); s = s.replace(a, b)
rep('<button id="lLbl" aria-pressed="true">건물 이름</button>', '<button id="lLbl" aria-pressed="false">건물 이름</button>')
rep("let showLabels = true;   // building names", "let showLabels = false;   // building names")
i = s.index("$('board').classList.add('solo');"); j = s.index("return;\n  const cut = rows.findIndex(", i)
new = ("const bk = recordCount(), bT = GLYPH_ZONES.length; $('board').classList.add('solo'); $('bN').textContent = `${Math.round(bk/bT*100)}%`; $('bFill').style.width = `${bk/bT*100}%`;   /* the same count as everywhere else: filled records out of five, 20% each */\n"
       "  $('bRows').innerHTML = `<div class=\"bseg\" role=\"img\" aria-label=\"채운 기록 ${bk} / ${bT}\">${Array.from({length:bT}, (_, k)=> `<i class=\"${k < bk ? 'ok' : ''}\"></i>`).join('')}</div><p class=\"bcount\">채운 기록 <b>${bk}</b> / ${bT}</p>`; ")
s = s[:i] + new + s[j:]
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
