# 2026-11-09 (사용자): 조당 라운드마다 게시물 2~3개(조 4명·노트북 2대), 조 선택에서 「진행 화면」 버튼 삭제(판별 안 하는 선택지 없음; ?view=screen 주소만 프로젝터용으로 남김).
import io, sys
ROOT = r'C:\Users\dlgus\break_out'


def opener(path):
    t = io.open(path, encoding='utf-8', newline='').read()
    return t.replace('\r\n', '\n'), '\r\n' in t


def make_r(box):
    def r(old, new, cnt=1):
        n = box[0].count(old)
        if n != cnt:
            sys.exit(f'{n}≠{cnt}: {old[:100]}')
        box[0] = box[0].replace(old, new)
    return r


SP = ROOT + r'\server\ch5_feed_server.py'
s, s_crlf = opener(SP)
if 'POSTS_PER_ROUND' in s:
    sys.exit('서버: 이미 적용됨')
B = [s]; r = make_r(B)
r("MAX_POSTS_PER_TEAM = 3    # 조마다 라운드당 1개 (뉴스·쇼츠·스토리)",
  "POSTS_PER_ROUND = 3       # 조마다 라운드(형식)당 최대 3개, 2개 이상 올리면 끝낸 것으로 봄 (2026-11-09: 조 4명·노트북 2대)\nMIN_POSTS_PER_ROUND = 2\nMAX_POSTS_PER_TEAM = POSTS_PER_ROUND * 3")
r("""                if any(p['format'] == fmt and p['id'] != pid for p in DB['posts'] if p['team'] == team):
                    raise ValueError('그 형식은 이미 다른 글로 올렸습니다.')
""", "")
r("""                active = [p for p in DB['posts'] if p['team'] == team]
                if len(active) >= MAX_POSTS_PER_TEAM:
                    raise ValueError(f'게시글은 조마다 {MAX_POSTS_PER_TEAM}개까지 올릴 수 있습니다.')
                if any(p['format'] == fmt for p in active):
                    raise ValueError({'news': '기사', 'story': '스토리', 'shorts': '쇼츠'}[fmt] + '는 이미 올렸습니다. 다른 형식을 만들거나 올린 글을 고쳐 주세요.')""",
"""                active = [p for p in DB['posts'] if p['team'] == team and p['format'] == fmt]
                if len(active) >= POSTS_PER_ROUND:
                    raise ValueError(f'이번 라운드 게시글은 조마다 {POSTS_PER_ROUND}개까지 올릴 수 있습니다. 올린 글을 고치거나 지우고 다시 올려 주세요.')""")
r("""           'aiEnabled': bool(GEMINI_KEY), 'maxPosts': MAX_POSTS_PER_TEAM}""",
  """           'aiEnabled': bool(GEMINI_KEY), 'maxPosts': POSTS_PER_ROUND, 'minPosts': MIN_POSTS_PER_ROUND}""")
r("""    return {'submitted': sorted({p['team'] for p in posts}), 'judged': judged, 'posts': len(posts), 'returned': returned,""",
  """    counts = {}
    for p in posts:
        counts[str(p['team'])] = counts.get(str(p['team']), 0) + 1
    return {'submitted': sorted({p['team'] for p in posts if counts[str(p['team'])] >= MIN_POSTS_PER_ROUND}), 'counts': counts, 'judged': judged, 'posts': len(posts), 'returned': returned,""")
s = B[0]

PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'minPosts' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)
r("""        <button id="btnScreen" type="button"><i data-lucide="monitor" class="icon"></i>진행 화면</button>
""", "")
r("""  $('#btnScreen').onclick = () => setTeam(0);
""", "")
r("""  else if (d.phase === 'make') { const ret = pr.returned || []; prog = `<span>올린 조 ${pr.submitted.length} / ${n}${ret.length ? ` · 돌려보냄 ${ret.length}` : ''}</span>` + teams.map(t => `<i class="tm${ret.includes(t) ? ' ret' : pr.submitted.includes(t) ? ' on' : ''}" title="${ret.includes(t) ? '돌려보냄' : pr.submitted.includes(t) ? '올림' : '아직'}">${t}</i>`).join(''); }""",
  """  else if (d.phase === 'make') { const ret = pr.returned || [], cnt = pr.counts || {}; prog = `<span>${d.minPosts || 2}개 이상 올린 조 ${pr.submitted.length} / ${n}${ret.length ? ` · 돌려보냄 ${ret.length}` : ''}</span>` + teams.map(t => { const k = cnt[t] || 0; return `<i class="tm${ret.includes(t) ? ' ret' : pr.submitted.includes(t) ? ' on' : k ? ' part' : ''}" title="${t}조 ${k}개${ret.includes(t) ? ' · 돌려보냄' : ''}">${t}${k ? `<small>${k}</small>` : ''}</i>`; }).join(''); }""")
r("""    .opbar .tm { display: grid; place-items: center;""", """    .opbar .tm small { font-size: 9px; font-weight: 800; line-height: 1; opacity: .85; }
    .opbar .tm { display: grid; grid-auto-flow: column; gap: 2px; align-items: center; justify-content: center;""")
r("""  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>${roundIdx(curRound()) + 1}라운드 <b>${ROUND_LABEL[curRound()]} 1개</b> (진짜/가짜 선택)</dd>""",
  """  const cur = mine.filter(p => p.format === curRound() && p.status !== 'returned').length;
  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>${roundIdx(curRound()) + 1}라운드 <b>${ROUND_LABEL[curRound()]} ${d.minPosts || 2}~${d.maxPosts}개</b> (글마다 진짜/가짜 선택) · 지금 <b>${cur}개</b></dd>""")
r("""  $('#myPosts').innerHTML = mine.length ? `<div class="flabel small">우리 조 게시물 ${mine.length} / ${d.maxPosts}</div>` + mine.map(p =>""",
  """  $('#myPosts').innerHTML = mine.length ? `<div class="flabel small">우리 조 게시물 · 이번 라운드 ${cur} / ${d.maxPosts}</div>` + mine.map(p =>""")
r("""  const canMake = S.editing || !mine.some(p => p.format === curRound() && p.status !== 'returned');""",
  """  const canMake = S.editing || cur < d.maxPosts;""")
r("""  $('#makeClosed').innerHTML = `<b>이번 라운드 ${ROUND_LABEL[curRound()]}를 올렸습니다.</b><p class="muted small">위 목록에서 보기, 고치기, 지우기를 할 수 있습니다. 판별 시간이 되면 다른 조 ${ROUND_LABEL[curRound()]}가 열립니다.</p>`;""",
  """  $('#makeClosed').innerHTML = `<b>이번 라운드 ${ROUND_LABEL[curRound()]} ${d.maxPosts}개를 다 올렸습니다.</b><p class="muted small">위 목록에서 보기, 고치기, 지우기를 할 수 있습니다. 판별 시간이 되면 다른 조 ${ROUND_LABEL[curRound()]}가 열립니다.</p>`;""")
r("""  if (phase === 'judge' && S.data && S.data.progress) { const pr = S.data.progress, n = S.data.teamCount, miss = n - pr.submitted.length, ret = (pr.returned || []).length;
    if (miss || ret) warn = `\\n\\n아직 안 올린 조 ${miss}${ret ? `, 돌려보낸 글 ${ret}` : ''}. 지금 넘기면 그 조는 이번 라운드 글 없이 판별만 합니다.`; }""",
  """  if (phase === 'judge' && S.data && S.data.progress) { const pr = S.data.progress, n = S.data.teamCount, miss = n - pr.submitted.length, ret = (pr.returned || []).length;
    if (miss || ret) warn = `\\n\\n${S.data.minPosts || 2}개를 못 채운 조 ${miss}${ret ? `, 돌려보낸 글 ${ret}` : ''}. 지금 넘기면 그 조는 올린 글만으로 판별에 들어갑니다.`; }""")
h = B[0]
for path, text, crlf in ((SP, s, s_crlf), (PP, h, h_crlf)):
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
print('ok')
