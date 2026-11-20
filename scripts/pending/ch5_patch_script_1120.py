# 2026-11-20 대본 반영(사용자가 고친 줄만) + 대사 강조 표시(**낱말**) 기능. 한 번만 돌린다.  python -X utf8 scripts/pending/ch5_patch_script_1120.py
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = P.read_bytes().decode('utf-8').replace('\r\n', '\n'); n = 0
def rep(a, b, cnt=1):
    global s, n
    assert s.count(a) == cnt, (s.count(a), a[:50]); s = s.replace(a, b); n += 1
J = lambda who, text: '{"who": "%s", "text": "%s"}' % (who, text)
# --- 대본: 튜토리얼
rep('올바른 위치에 올바르게 환원하지 않으면', '올바른 위치에 정확하게 환원하지 않으면')
rep('그런데 현재 이 섬의 세 곳의 기록이 누락돼서', '그런데 현재 이 섬의 몇몇 기록들이 누락돼서')
rep('누락된 기록 세 개를 캠퍼스에서 스캔해서 채울 거야. 먼저 첫 번째 좌표부터 알려 줄게.', '내 안내에 따라 기록을 채워보면 어렵지 않을거야. 먼저 첫 번째 기록의 좌표부터 알려 줄게.')
# --- 기록 1 뒤
rep('우와, 하모니아 주변의 흐름은 이렇게 생겼네!', '우와, 하모니아 주변의 일루아 흐름은 이렇게 생겼네!')
rep('"얼른 나머지 기록도 채우자!"', '"얼른 나머지도 채우자!"')
# --- 네이티가 사라졌다
rep(', '.join([J('자일로', '……잠깐만요. 네이티가 없어요!'), J('리코', '아까까지 여기 있었잖아요?'), J('자일로', '네이티는 일루아가 모습을 띤 존재예요. 일루아가 흔들리면 네이티도 흐트러집니다. 전원이 한꺼번에 들어오면서 일루아가 크게 흔들린 것 같아요.'),
    J('자일로', '빛이 흩어져서 어딘가로 끌려갔을 거예요. 이렇게 흔들리는 건 처음 봅니다. 응축된 일루아가 오래 버티지 못한다는 뜻이에요.'), J('제로', '그럼 환원을 서둘러야 하는 거네요.'), J('자일로', '네. 그러려면 네이티부터 찾아야 해요. 네이티가 끌려간 쪽에 일루아가 흐르던 자리가 있을 겁니다. 정문 동쪽 길부터 찾아봐 주세요.')]),
    ', '.join([J('자일로', '……잠깐만요. 네이티가 사라졌어요!'), J('리코', '아까까지 여기 있었는데, 어디간거죠??'), J('자일로', '네이티는 일루아의 모습 투영한 존재예요. 일루아에 무슨일이 생기면 네이티를 통해 알 수 있죠. 전원이 한꺼번에 들어오면서 일루아가 크게 흔들린 것 같아요.'),
    J('자일로', '일단 네이티부터 찾아야 해요. 정문 동쪽 길부터 찾아봐 주세요.')]))
# --- 미로
rep(J('제로', '여기 미로가 있네.') + ', ' + J('리코', '미로야. 이 미로 어딘가에 네이티가 있지 않을까?'), J('제로', '미로 중앙에서 뭔가 빛이 새어나오고 있어.') + ', ' + J('리코', '미로 중앙에 네이티가 있는게 아닐까??'))
rep(J('보이드', '따라가자. 네이티의 자취를 따라가면 비어 있는 흐름을 찾을 수 있을지도 몰라.'), J('리코', '따라가자. 네이티의 자취를 따라가면 비어 있는 흐름을 찾을 수 있을지도 몰라.'))
rep('"그럼 바로 가서 찍어 오자."', '"그럼 바로 가서 스캔하자!!"')
# --- 바이킹
rep(', '.join([J('자일로', '오셨군요. 여기가 바이킹이 있던 자리예요.'), J('자일로', '코덱스가 도로랜드를 공격했을 때 배가 팔에서 떨어져 무너졌습니다. 전선이 끊긴 것도 그때예요.'), J('리코', '전기는 돌아왔는데 바이킹만 아직 멈춰 있네요.'),
    J('자일로', '네. 배가 부서져서 전기가 들어와도 움직일 수 없어요. 여러분이 만든 바이킹으로 다시 세워 주세요.'), J('제로', '우리가 만든 바이킹을 올리면 되는 거죠? 해 볼게요!')]),
    ', '.join([J('자일로', '오셨군요. 코덱스가 도로랜드를 공격했을 때 배를 지탱하던 기둥이 부숴져 바이킹이 파괴되었습니다.'), J('리코', '우리가 설계한 바이킹을 바탕으로 재건축하면 되지 않을까요??'), J('자일로', '네. 좋은 생각입니다. 여러분이 만든 바이킹으로 다시 바이킹을 움직여주세요.'), J('제로', '좋아! 아까 만들었던 바이킹을 올려보자!')]))
# --- 연구실
rep('이대로면 기록을 다 모아도 시뮬레이션을 믿을 수 없어요.', '이대로면 기록을 다 모아도 시뮬레이션을 정상적으로 가동할 수 없어요.')
rep('선대가 일루아를 모을 때 섬 곳곳에 심어 둔 장치가 있었어요.', '선대가 일루아를 제어하기 위해 섬 곳곳에 심어 둔 장치가 있었어요.')
rep('"노이즈가 사라졌어요. 다시 돌려 볼게요."', '"장치들을 전부 제거했군요! 노이즈가 모두 사라졌어요. 다시 시뮬레이션을 가동해 볼게요."')
# --- 강조 표시: 대사 문장 안의 **낱말**을 굵은 강조색으로. 글자 찍기·줄 맞춤은 표시를 뺀 글자 수로 센다
rep("""function dlPlan(p, text){""", """/* **낱말** in a line is shown bold in the accent colour (user, 2026-11-20: 중요한 건 강조해서, 애들이 읽기 편하게). v = how many plain characters are typed so far; the untyped rest keeps its width */
const dlPlain = t=> t.replace(/\\*\\*/g, '');
function dlMark(t, v){ let left = v, h = ''; t.split('**').forEach((seg, i)=>{ if(!seg) return; const a = Math.max(0, Math.min(seg.length, left)); left -= seg.length; const w = x=> i % 2 ? `<b class="dlem">${dlEsc(x)}</b>` : dlEsc(x); if(a) h += w(seg.slice(0, a)); if(a < seg.length) h += `<i class="vhid">${w(seg.slice(a))}</i>`; }); return h; }
function dlPlan(p, text){""")
rep("""const draw = ()=>{ p.innerHTML = parts.map(t=> `<span class="vsen">${dlEsc(t)}</span>`).join(''); }""", """const draw = ()=>{ p.innerHTML = parts.map(t=> `<span class="vsen">${dlMark(t, 1e9)}</span>`).join(''); }""")
rep("total:parts.reduce((n, t)=> n + t.length, 0), wrap", "total:parts.reduce((n, t)=> n + dlPlain(t).length, 0), wrap", 2)
rep("""p.innerHTML = d.parts.map(t=>{ const v = Math.max(0, Math.min(t.length, left)); left -= t.length; return `<span class="vsen${d.wrap ? ' vwrap' : ''}">${dlEsc(t.slice(0, v))}<i class="vhid">${dlEsc(t.slice(v))}</i></span>`; }).join(''); return d.total; }""",
    """p.innerHTML = d.parts.map(t=>{ const L = dlPlain(t).length, v = Math.max(0, Math.min(L, left)); left -= L; return `<span class="vsen${d.wrap ? ' vwrap' : ''}">${dlMark(t, v)}</span>`; }).join(''); return d.total; }""")
rep("const f = VOICE[text];", "const f = VOICE[dlPlain(text)];")
rep("</style></head><body>", ".dlem{font-weight:800;font-style:normal}#voidVn .dlem{color:#1668c7}#vn .dlem{color:#9ff6ff}\n</style></head><body>")
# --- 튜토리얼의 강조 낱말(한 줄에 핵심 낱말 하나)
for a, b in [('여기는 네가 있는 ERICA 캠퍼스야.', '여기는 네가 있는 **ERICA 캠퍼스**야.'), ('{t:"그리고 여기는 도로랜드 섬이야."', '{t:"그리고 여기는 **도로랜드 섬**이야."'), ('{t:"두 공간은 트윈으로 이어져 있어.', '{t:"두 공간은 **트윈**으로 이어져 있어.'),
             ('{t:"그 자리를 네가 직접 스캔하면,', '{t:"그 자리를 네가 직접 **스캔**하면,'), ('{t:"가장 먼저 복구할 곳은 하모니아 근처야."', '{t:"가장 먼저 복구할 곳은 **하모니아** 근처야."'),
             ("좌표는 ${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}야. 지금 네가 있는 건물이지.", "좌표는 **${z && z.lat != null ? coordText(z) : '카드에 있는 좌표'}**야. **지금 네가 있는 건물**이지."),
             ('{t:"왼쪽 「보이드의 기록」 카드에 좌표가 있어.', '{t:"왼쪽 「보이드의 기록」 카드에 **좌표**가 있어.'), ('해당 정보를 Scaniverse로 한 바퀴 빙 돌면서 찍어.', '해당 정보를 **Scaniverse**로 **한 바퀴 빙 돌면서** 찍어.'),
             ('{t:"다 찍었으면 Scaniverse에서 「공유」를 누르고 「링크 복사」를 눌러."', '{t:"다 찍었으면 Scaniverse에서 **「공유」**를 누르고 **「링크 복사」**를 눌러."'),
             ('{t:"다시 여기로 돌아와 「스캔 링크」 칸에 붙여 넣고 「제출」해 줘.', '{t:"다시 여기로 돌아와 **「스캔 링크」** 칸에 붙여 넣고 **「제출」**해 줘.'),
             ('밖에 나가면 아래 「내 시점」을 켜 봐.",pose', '밖에 나가면 아래 **「내 시점」**을 켜 봐.",pose'), ('{t:"파란 화살표가 너야.', '{t:"**파란 화살표**가 너야.'), ('{t:"막히면 왼쪽 아래 「보이드」 버튼으로 나를 찾아.', '{t:"막히면 왼쪽 아래 **「보이드」 버튼**으로 나를 찾아.')]:
    rep(a, b)
P.write_bytes(s.encode('utf-8')); print('applied', n)
