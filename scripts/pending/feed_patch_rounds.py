# 2026-11-09 도로그램 3라운드(뉴스 → 쇼츠 → 스토리). 라운드마다 만들기 → 판별 → 정답 공개, 점수는 공개된 라운드 합산.
# 첫 화면 = 형식 타일 3개(지금 라운드만 열림, 끝난 라운드는 다시 보기, 다음 라운드는 잠김). 예제는 학생 화면에서 뺌. 한 번만 적용.
import io, sys
ROOT = r'C:\Users\dlgus\break_out'


def opener(path):
    t = io.open(path, encoding='utf-8', newline='').read()
    return t.replace('\r\n', '\n'), '\r\n' in t


def make_r(box):
    def r(old, new, cnt=1):
        n = box[0].count(old)
        if n != cnt:
            sys.exit(f'{n}≠{cnt}: {old[:90]}')
        box[0] = box[0].replace(old, new)
    return r


# ---------------- server ----------------
SP = ROOT + r'\server\ch5_feed_server.py'
s, s_crlf = opener(SP)
if 'ROUNDS' in s:
    sys.exit('서버: 이미 적용됨')
B = [s]; r = make_r(B)
r("PHASES = ['read', 'make', 'judge', 'reveal']\n",
  "PHASES = ['read', 'make', 'judge', 'reveal']\n"
  "ROUNDS = ['news', 'shorts', 'story']   # 2026-11-09: 라운드마다 한 형식 (뉴스 → 쇼츠 → 스토리), 라운드 안에서 만들기 → 판별 → 정답 공개\n")
r("MAX_POSTS_PER_TEAM = 3    # 조마다 스토리·기사·쇼츠 1개씩", "MAX_POSTS_PER_TEAM = 3    # 조마다 라운드당 1개 (뉴스·쇼츠·스토리)")
r("    return {'version': 1, 'phase': 'read', 'teamCount'", "    return {'version': 1, 'phase': 'read', 'round': ROUNDS[0], 'teamCount'")
r("    db.setdefault('teamCount', DEFAULT_TEAM_COUNT)\n    return db",
  "    db.setdefault('teamCount', DEFAULT_TEAM_COUNT)\n    db.setdefault('round', ROUNDS[0])\n    return db")
r("""def compute_scores():""", """def round_idx(fmt):
    return ROUNDS.index(fmt) if fmt in ROUNDS else 0


def post_revealed(p):
    \"\"\"그 형식의 라운드가 정답 공개까지 갔으면 공개된 것.\"\"\"
    i, cur = round_idx(p.get('format')), round_idx(DB.get('round'))
    return i < cur or (i == cur and DB['phase'] == 'reveal')


def post_open(p):
    \"\"\"다른 조 게시물은 그 라운드의 판별 시간부터 보인다.\"\"\"
    i, cur = round_idx(p.get('format')), round_idx(DB.get('round'))
    return i < cur or (i == cur and DB['phase'] in ('judge', 'reveal'))


def any_revealed():
    return round_idx(DB.get('round')) > 0 or DB['phase'] == 'reveal'


def compute_scores():""")
r("""        if p['status'] != 'approved' or p.get('seed'):   # 예제(운영실 자료)는 연습이라 점수에 안 넣음
            continue""", """        if p['status'] != 'approved' or p.get('seed') or not post_revealed(p):   # 예제는 점수 제외, 공개된 라운드만 합산
            continue""")
r("""        r['judgable'] = sum(1 for p in DB['posts'] if p['status'] == 'approved' and not p.get('seed') and p['team'] != r['team'])""",
  """        r['judgable'] = sum(1 for p in DB['posts'] if p['status'] == 'approved' and not p.get('seed') and p['team'] != r['team'] and post_revealed(p))""")
r("""    reveal = DB['phase'] == 'reveal'
    own = bool(team)""", """    reveal = post_revealed(p) if not p.get('seed') else DB['phase'] == 'reveal'
    own = bool(team)""")
r("""    if p['status'] != 'approved':
        return False
    if p.get('seed') or (team and p['team'] == team):
        return True
    # 다른 조 게시물은 판별 시간부터 보인다 (만드는 동안 새 글이 뜨면 조 게시물인 게 티 남)
    return DB['phase'] in ('judge', 'reveal')""", """    if p['status'] != 'approved' or p.get('seed'):   # 예제는 학생 화면에 보내지 않음 (2026-11-09)
        return False
    if team and p['team'] == team:
        return True
    # 다른 조 게시물은 그 라운드의 판별 시간부터 보인다 (만드는 동안 새 글이 뜨면 조 게시물인 게 티 남)
    return post_open(p)""")
r("""    res = {'version': DB['version'], 'phase': DB['phase'], 'teamCount'""", """    res = {'version': DB['version'], 'phase': DB['phase'], 'round': DB.get('round', ROUNDS[0]), 'rounds': ROUNDS, 'teamCount'""")
r("""    if admin or DB['phase'] == 'reveal':
        res['scores'] = compute_scores()""", """    if admin or any_revealed():
        res['scores'] = compute_scores()""")
r("""            if DB['phase'] != 'make':
                raise ValueError('지금은 게시글을 만드는 시간이 아닙니다.')
            pid = b.get('id')""", """            if DB['phase'] != 'make':
                raise ValueError('지금은 게시글을 만드는 시간이 아닙니다.')
            if fmt != DB.get('round'):
                raise ValueError('이번 라운드는 ' + {'news': '뉴스', 'story': '스토리', 'shorts': '쇼츠'}[DB.get('round', 'news')] + '만 만들 수 있습니다.')
            pid = b.get('id')""")
r("""            elif DB['phase'] != 'judge':
                raise ValueError('다른 조 게시물은 판별 시간에만 판별할 수 있습니다.')""", """            elif DB['phase'] != 'judge' or p.get('format') != DB.get('round'):
                raise ValueError('이번 라운드 게시물만 판별 시간에 판별할 수 있습니다.')""")
r("""    def admin_phase(self, b):
        if b.get('phase') not in PHASES:
            raise ValueError('없는 단계입니다.')
        with lock:
            DB['phase'] = b['phase']
            save_and_broadcast()
            self.send_json({'phase': DB['phase']})""", """    def admin_phase(self, b):
        if b.get('phase') not in PHASES:
            raise ValueError('없는 단계입니다.')
        if b.get('round') is not None and b.get('round') not in ROUNDS:
            raise ValueError('없는 라운드입니다.')
        with lock:
            DB['phase'] = b['phase']
            if b.get('round'):
                DB['round'] = b['round']
            save_and_broadcast()
            self.send_json({'phase': DB['phase'], 'round': DB['round']})""")
r("""            if not p or p.get('seed') or p['team'] != team:
                raise ValueError('지울 수 없는 게시물입니다.')""", """            if not p or p.get('seed') or p['team'] != team or p.get('format') != DB.get('round'):
                raise ValueError('지울 수 없는 게시물입니다.')""")
s = B[0]

# ---------------- page ----------------
PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'roundIdx' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)
# CSS: 첫 화면 라운드 타일 + 라운드 화면 머리
r("    .tray-wrap {", """    .rounds { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; padding: 8px 16px 0; max-width: 980px; }
    @media (min-width: 1024px) { .rounds { padding: 8px 0 0; } }
    @media (max-width: 640px) { .rounds { grid-template-columns: 1fr; } }
    .round-tile { display: grid; gap: 14px; justify-items: start; text-align: left; padding: 22px 20px; min-height: 196px; border-radius: 16px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; cursor: pointer; transition: transform .15s ease, box-shadow .15s ease; }
    .round-tile .rt-ic { display: grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; background: var(--surface-2); }
    .round-tile .rt-ic .icon { width: 26px; height: 26px; }
    .round-tile small { font-size: 13px; font-weight: 700; color: var(--muted); }
    .round-tile b { display: block; font-size: 26px; line-height: 1.2; margin-top: 2px; }
    .round-tile .rt-st { font-size: 13px; color: var(--muted); }
    .round-tile.now { border: 2px solid var(--blue); box-shadow: 0 6px 20px color-mix(in srgb, var(--blue) 18%, transparent); }
    .round-tile.now .rt-ic { background: var(--blue); color: var(--blue-ink); }
    .round-tile.now small, .round-tile.now .rt-st { color: var(--blue); }
    .round-tile:not(:disabled):hover { transform: translateY(-2px); }
    .round-tile:not(:disabled):active { transform: translateY(1px); }
    .round-tile:disabled { cursor: not-allowed; opacity: .45; background: var(--surface-2); }
    .round-tile:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
    @media (prefers-reduced-motion: reduce) { .round-tile { transition: none; } .round-tile:hover, .round-tile:active { transform: none; } }
    .round-head { display: flex; align-items: center; gap: 12px; margin: 0 16px 14px; flex-wrap: wrap; }
    @media (min-width: 1024px) { .round-head { margin: 0 0 14px; } }
    .round-head h2 { margin: 0; font-size: 22px; }
    .round-head .back { display: inline-flex; align-items: center; gap: 4px; min-height: 40px; padding: 0 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; font-weight: 700; cursor: pointer; }
    .round-head .btn { margin-left: auto; }
    .round-list { padding: 0 16px; }
    @media (min-width: 1024px) { .round-list { padding: 0; } }
    .round-list .tray { flex-wrap: wrap; }
    .tray-wrap {""")
# HTML: 홈 = 라운드 타일 / 라운드 화면
r("""      <div class="tray-wrap"><div class="tray-head"><i data-lucide="circle-dashed" class="icon"></i>스토리<span class="cnt" id="trayCnt"></span></div><div class="tray" id="tray"></div></div>
      <div class="filters" role="group" aria-label="게시물 거르기">""", """      <div class="rounds" id="rounds" role="group" aria-label="라운드"></div>
      <div id="roundView" hidden>
      <div class="round-head" id="roundHead"></div>
      <div class="filters" role="group" aria-label="게시물 거르기">""")
r("""      <div class="feed-split" id="feed"><div class="skeleton"></div><div class="skeleton"></div></div>
    </section>""", """      <div class="round-list" id="feed"><div class="skeleton"></div></div>
      </div>
    </section>""")
# 상태
r("const S = { team: null, screen: false, data: null, version: 0, tab: 'feed', filter: 'all',",
  "const S = { team: null, screen: false, data: null, version: 0, tab: 'feed', fmt: null, filter: 'all',")
r("""const truthOf = p =>""", """const ROUND_ORDER = ['news', 'shorts', 'story'], ROUND_LABEL = { news: '뉴스', shorts: '쇼츠', story: '스토리' }, ROUND_ICON = { news: 'newspaper', shorts: 'play', story: 'circle-dashed' };
const roundIdx = f => Math.max(0, ROUND_ORDER.indexOf(f));
const curRound = () => (S.data && S.data.round) || 'news';
/* 그 형식 라운드가 정답 공개까지 갔는지 (서버 post_revealed와 같은 규칙) */
const revealed = p => !!S.data && (roundIdx(p.format) < roundIdx(curRound()) || (p.format === curRound() && S.data.phase === 'reveal'));
const truthOf = p =>""")
# refresh: 라운드가 바뀌면 만들기 폼을 새 형식으로
r("""    const phaseChanged = S.data && S.data.phase !== d.phase;""", """    const phaseChanged = S.data && S.data.phase !== d.phase;
    const roundChanged = S.data && S.data.round !== d.round;""")
r("""    if (!S.form) resetForm();""", """    if (!S.form || (roundChanged && !S.editing)) resetForm();""")
r("""    if (phaseChanged && d.phase === 'judge' && S.tab !== 'admin') showTab('feed');""",
  """    if ((phaseChanged || roundChanged) && S.tab === 'feed' && S.fmt && S.fmt !== d.round) S.fmt = null;""")
# render
r("""  $$('[data-tab="score"]').forEach(b => b.hidden = d.phase !== 'reveal');""", """  $$('[data-tab="score"]').forEach(b => b.hidden = !d.scores);""")
r("""  if ((S.tab === 'score' && d.phase !== 'reveal') ||""", """  if ((S.tab === 'score' && !d.scores) ||""")
r("""  if (t === 'archive') renderArchive();""", """  if (t === 'archive') renderArchive();
  if (t === 'feed') { S.fmt = null; renderFeed(); icons(); }""")
# feedPosts: 지금 연 라운드 형식만
r("""  const d = S.data, late = ['judge', 'reveal'].includes(d.phase);
  let posts = d.posts.filter(p => p.status === 'approved' && !p.seed);""", """  const d = S.data;
  let posts = d.posts.filter(p => p.status === 'approved' && !p.seed && (!S.fmt || p.format === S.fmt));""")
r("""  return p.seed ? ph !== 'reveal' : ph === 'judge';""", """  return !p.seed && ph === 'judge' && p.format === curRound();""")
r("""  const mine = S.data.myJudgments[p.id], reveal = S.data.phase === 'reveal';""", """  const mine = S.data.myJudgments[p.id], reveal = revealed(p);""")
# renderFeed: 홈 타일 / 라운드 화면
r("""function renderFeed() {
  const d = S.data, posts = feedPosts();
  const stories = posts.filter(p => p.format === 'story'), shorts = posts.filter(p => p.format === 'shorts'), news = posts.filter(p => p.format === 'news');
  const late = ['judge', 'reveal'].includes(d.phase);
  const empty = S.filter === 'todo' ? '다 판별했습니다.' : S.filter === 'mine' ? '우리 조가 만든 게시물이 없습니다.' : late ? '아직 다른 조 게시물이 없습니다.' : '아직 게시물이 없습니다.';
  $('#trayCnt').textContent = stories.length ? stories.length : '';
  $('#tray').innerHTML = stories.length ? stories.map(trayHTML).join('') : `<div class="tray-empty">${empty}</div>`;
  $('#feedCnt').textContent = `${late ? '판별할 게시물' : '게시물'} ${posts.length}개`;
  $('#feed').innerHTML = `
    <section class="shorts-panel" aria-label="쇼츠"><div class="sp-head"><span class="sp-logo">${ic('play')}</span>쇼츠<span class="cnt">${shorts.length}</span></div>
      ${shorts.length ? `<div class="shorts-grid">${shorts.map(tileHTML).join('')}</div>` : `<div class="panel-empty">${empty}</div>`}</section>
    <section class="news-panel" aria-label="뉴스"><div class="np-head">${ic('newspaper')}도로랜드 뉴스<span class="cnt">${news.length}</span></div>
      <div class="news-list">${news.length ? news.map(newsItemHTML).join('') : `<div class="panel-empty">${empty}</div>`}</div></section>`;
  renderModal();
}""", """/* 첫 화면: 라운드 타일 3개(뉴스 → 쇼츠 → 스토리). 지금 라운드만 열리고, 끝난 라운드는 다시 볼 수 있고, 다음 라운드는 잠김 (2026-11-09 사용자) */
function renderRounds() {
  const cur = roundIdx(curRound());
  $('#rounds').innerHTML = ROUND_ORDER.map((f, i) => {
    const now = i === cur, past = i < cur, n = (S.data.posts || []).filter(p => p.format === f && p.status === 'approved' && !p.seed).length;
    const st = now ? '지금 라운드' : past ? `끝난 라운드 · 게시물 ${n}개` : '앞 라운드가 끝나면 열립니다';
    return `<button type="button" class="round-tile${now ? ' now' : ''}" data-round="${f}" ${now || past ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${now || past ? '' : ' (잠김)'}">
      <span class="rt-ic">${ic(now || past ? ROUND_ICON[f] : 'lock')}</span><span><small>${i + 1}라운드</small><b>${ROUND_LABEL[f]}</b></span><span class="rt-st">${st}</span></button>`;
  }).join('');
}
function renderFeed() {
  const d = S.data, home = !S.fmt;
  $('#rounds').hidden = !home; $('#roundView').hidden = home;
  if (home) { renderRounds(); renderModal(); return; }
  const f = S.fmt, now = f === curRound(), posts = feedPosts(), judging = now && d.phase === 'judge';
  const canMakeNow = now && d.phase === 'make' && !S.screen && S.team;
  $('#roundHead').innerHTML = `<button type="button" class="back" data-act="home">${ic('chevron-left')}처음으로</button><h2>${roundIdx(f) + 1}라운드 · ${ROUND_LABEL[f]}</h2>${canMakeNow ? `<button type="button" class="btn btn-primary" data-goto="make">${ic('square-plus')}우리 조 ${ROUND_LABEL[f]} 만들기</button>` : ''}`;
  const empty = S.filter === 'todo' ? '다 판별했습니다.' : S.filter === 'mine' ? '우리 조가 만든 게시물이 없습니다.' : now && d.phase !== 'judge' && d.phase !== 'reveal' ? '다른 조 게시물은 판별 시간에 보입니다.' : '아직 게시물이 없습니다.';
  $('#feedCnt').textContent = `${judging ? '판별할 게시물' : '게시물'} ${posts.length}개`;
  $('#feed').innerHTML = !posts.length ? `<div class="panel-empty">${empty}</div>`
    : f === 'story' ? `<div class="tray">${posts.map(trayHTML).join('')}</div>`
    : f === 'shorts' ? `<div class="shorts-grid">${posts.map(tileHTML).join('')}</div>`
    : `<div class="news-list">${posts.map(newsItemHTML).join('')}</div>`;
  renderModal();
}""")
r("""  if (d.phase !== 'reveal') { box.hidden = true; return; }""", """  if (d.phase !== 'reveal' || S.fmt !== curRound()) { box.hidden = true; return; }""")
r("""  box.innerHTML = `<div class="twist"><h2>정답 공개</h2>""", """  box.innerHTML = `<div class="twist"><h2>${roundIdx(curRound()) + 1}라운드 정답 공개</h2>""")
r("""<div><b>${rank}위</b>합계 ${me.total}점</div></div>` : ''}
    <p style="margin:12px 0 0;font-size:14px">게시물을 누르면 정답과 각 조가 숨긴 단서가 보입니다. "섬이 사라졌다" 기사 3개는 모두 진짜였습니다. 3년마다 같은 시기에 같은 일이 일어났고, 원인은 아직 아무도 모릅니다. 드론쇼·팝업·아기 기린 같은 평범한 소식이 진짜였고, 자극적인 속보일수록 가짜가 많았습니다.</p></div>`;""",
  """<div><b>${rank}위</b>지금까지 합계 ${me.total}점</div></div>` : ''}
    <p style="margin:12px 0 0;font-size:14px">게시물을 누르면 정답과 각 조가 숨긴 단서가 보입니다.</p></div>`;""")
r("""  if (S.data.phase === 'reveal' && p.secret) { const s = p.secret;""", """  if (revealed(p) && p.secret) { const s = p.secret;""")
r("""  if (!p.mine || S.data.phase === 'reveal') return '';""", """  if (!p.mine || revealed(p)) return '';""")
r("""${own || S.data.phase === 'reveal' ? `""", """${own || revealed(p) ? `""")
# 만들기: 이번 라운드 형식만
r("""  const done = new Set(myPosts().map(p => p.format)), first = ['story', 'shorts', 'news'].find(f => !done.has(f)) || 'story';""",
  """  const first = curRound();   /* 이번 라운드 형식만 만든다 */""")
r("""  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>스토리·쇼츠·기사 <b>1개씩</b> (각각 진짜/가짜 선택)</dd>""",
  """  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>${roundIdx(curRound()) + 1}라운드 <b>${ROUND_LABEL[curRound()]} 1개</b> (진짜/가짜 선택)</dd>""")
r("""  const canMake = S.editing || mine.length < d.maxPosts;""", """  const canMake = S.editing || !mine.some(p => p.format === curRound());""")
r("""  $('#makeClosed').innerHTML = `<b>스토리·쇼츠·기사를 모두 올렸습니다.</b><p class="muted small">홈의 "우리 조가 만든 것"에서 보기, 고치기, 지우기를 할 수 있습니다.</p>`;""",
  """  $('#makeClosed').innerHTML = `<b>이번 라운드 ${ROUND_LABEL[curRound()]}를 올렸습니다.</b><p class="muted small">위 목록에서 보기, 고치기, 지우기를 할 수 있습니다. 판별 시간이 되면 다른 조 ${ROUND_LABEL[curRound()]}가 열립니다.</p>`;""")
r("""  $('#makeNotice').innerHTML = `<b>지금은 「${esc(C.PHASES[d.phase].label)}」 단계입니다.</b> 미리 써 볼 수는 있고, <b>공유하기</b>는 주강사가 「게시물 만들기」를 시작하면 열립니다.`;""",
  """  $('#makeNotice').innerHTML = `미리 써 볼 수는 있고, <b>공유하기</b>는 선생님이 만들기 시간을 열면 됩니다.`;""")
r("""${d.phase === 'make' ? `<button type="button" data-act="edit" data-id="${p.id}">고치기</button>""",
  """${d.phase === 'make' && p.format === curRound() ? `<button type="button" data-act="edit" data-id="${p.id}">고치기</button>""")
r("""  const f = S.form, fmt = C.FORMATS[f.format], d = S.data, done = new Set(myPosts().filter(p => p.id !== S.editing).map(p => p.format));""",
  """  const f = S.form, fmt = C.FORMATS[f.format], d = S.data, done = new Set(ROUND_ORDER.filter(k => k !== curRound()));   /* 이번 라운드 형식만 고를 수 있음 */""")
r("""${done.has(k) ? 'disabled title="이미 올렸습니다"' : ''}>${ic(v.icon)}${v.label}${done.has(k) ? ' ✓' : ''}</button>""",
  """${done.has(k) ? 'disabled title="이번 라운드 형식이 아닙니다"' : ''}>${ic(v.icon)}${v.label}</button>""")
# 운영자: 라운드 × 단계
r("""  $('#adPhases').innerHTML = Object.entries(C.PHASES).map(([k, ph]) => `<button class="ad-phase" data-adphase="${k}" aria-pressed="${d.phase === k}"><b>${ph.label}</b><span>${esc(ph.desc)}</span></button>`).join('');""",
  """  const RSTEP = { make: '만들기', judge: '판별', reveal: '정답 공개' };
  $('#adPhases').innerHTML = `<button class="ad-phase" data-adphase="read:news" aria-pressed="${d.phase === 'read'}"><b>시작 전</b><span>조를 고르고 자료실을 읽는 시간</span></button>`
    + ROUND_ORDER.map((f, i) => ['make', 'judge', 'reveal'].map(k => `<button class="ad-phase" data-adphase="${k}:${f}" aria-pressed="${d.phase === k && d.round === f}"><b>${i + 1}라운드 ${ROUND_LABEL[f]} · ${RSTEP[k]}</b><span>${k === 'make' ? `조마다 ${ROUND_LABEL[f]} 1개` : k === 'judge' ? `다른 조 ${ROUND_LABEL[f]} 판별` : '정답·점수 공개 (점수는 누적)'}</span></button>`).join('')).join('');""")
r("""    if (ph) await adApi('/admin/phase', { phase: ph.dataset.adphase });""", """    if (ph) { const [phase, round] = ph.dataset.adphase.split(':'); await adApi('/admin/phase', { phase, round }); }""")
r("""  const g = e.target.closest('[data-goto]'); if (g) { showTab(g.dataset.goto); return; }""",
  """  const rt = e.target.closest('[data-round]'); if (rt && !rt.disabled) { S.fmt = rt.dataset.round; S.filter = 'all'; $$('[data-filter]').forEach(x => x.setAttribute('aria-pressed', x.dataset.filter === 'all')); renderTwist(); renderFeed(); icons(); window.scrollTo({ top: 0 }); return; }
  if (e.target.closest('[data-act="home"]')) { S.fmt = null; renderTwist(); renderFeed(); icons(); return; }
  const g = e.target.closest('[data-goto]'); if (g) { showTab(g.dataset.goto); return; }""")
h = B[0]

for path, text, crlf in ((SP, s, s_crlf), (PP, h, h_crlf)):
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
print('ok')
