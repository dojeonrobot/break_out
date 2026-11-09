# 2026-11-09 도로그램 수업 운영 개편 (사용자):
#  - 조 선택 화면 새 디자인, 「선생님」 입구
#  - 운영자 로그인 = 모든 라운드·모든 게시물(예시·조 게시물·정답) 보기 + 상단 진행 막대(다음 단계, 제출·판별 현황)
#  - 라운드마다 예시 보기 → 만들기 → 판별 → 정답 공개. 예시 보기 때 그 형식 예시가 뜨고(바로 해설), 만들기가 시작되면 예시는 사라지고 만들기 화면으로
#  - 단계가 바뀌면 아이들 노트북·진행 화면이 지금 할 화면으로 따라감
# 한 번만 적용.
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


# ================= server =================
SP = ROOT + r'\server\ch5_feed_server.py'
s, s_crlf = opener(SP)
if "'progress'" in s:
    sys.exit('서버: 이미 적용됨')
B = [s]; r = make_r(B)
r("""    if p['status'] != 'approved' or p.get('seed'):   # 예제는 학생 화면에 보내지 않음 (2026-11-09)
        return False
    if team and p['team'] == team:""", """    if p['status'] != 'approved':
        return False
    if p.get('seed'):   # 예시는 그 라운드의 「예시 보기」 때만 (2026-11-09)
        return DB['phase'] == 'read' and p.get('format') == DB.get('round')
    if team and p['team'] == team:""")
r("""            if p.get('seed'):
                if DB['phase'] == 'reveal':
                    raise ValueError('정답 공개 중에는 판정을 바꿀 수 없습니다.')""", """            if p.get('seed'):
                if DB['phase'] != 'read' or p.get('format') != DB.get('round'):
                    raise ValueError('예시는 예시 보기 시간에만 골라 볼 수 있습니다.')""")
r("""    if admin or any_revealed():
        res['scores'] = compute_scores()""", """    res['progress'] = round_progress()
    if admin or any_revealed():
        res['scores'] = compute_scores()""")
r("""def compute_scores():""", """def round_progress():
    \"\"\"이번 라운드 현황(내용 없이 숫자만): 올린 조, 조마다 판별한 수, 조 게시물 수. 진행 화면·운영자 막대용.\"\"\"
    rd = DB.get('round')
    posts = [p for p in DB['posts'] if not p.get('seed') and p['status'] == 'approved' and p.get('format') == rd]
    ids = {p['id'] for p in posts}
    judged = {}
    for k in DB['judgments']:
        pid, t = k.rsplit(':', 1)
        if pid in ids:
            judged[t] = judged.get(t, 0) + 1
    return {'submitted': sorted({p['team'] for p in posts}), 'judged': judged, 'posts': len(posts),
            'seeds': sum(1 for p in DB['posts'] if p.get('seed') and p['status'] == 'approved' and p.get('format') == rd)}


def compute_scores():""")
r("""            out['answer'] = p.get('answer')   # 연습: 판정하자마자 해설이 열림""",
  """            sec = p.get('secret') or {}   # 연습: 판정하자마자 해설 + 어디서 들통나는지(기준)·쓴 수법까지 열림
            out['answer'] = dict(p.get('answer') or {}, tactic=sec.get('tactic') or '', criterion=sec.get('clueCriterion') or '')""")
s = B[0]

# ================= config =================
CP = ROOT + r'\chapter05\feed-config.js'
c, c_crlf = opener(CP)
B = [c]; r = make_r(B)
r("""    read:   { label: '자료 살펴보기', desc: '자료실을 읽고, 예제 게시물을 보고 진짜인지 가짜인지 골라 보세요. 고르면 바로 해설이 나옵니다. 점수에는 들어가지 않습니다.' },""",
  """    read:   { label: '예시 보기', desc: '이번 라운드 형식의 예시를 보고 진짜인지 가짜인지 골라 봅니다. 고르면 바로 해설이 나오고 점수에는 들어가지 않습니다.' },""")
r("""  // 가짜를 만들 때 쓰는 수법
  TACTICS: [""", """  // 형식마다 예시 보기 때 알려 주는 것 (2026-11-09): 확인할 곳 / 가짜가 숨는 곳 / 진짜의 특징. 예시 게시물 해설과 맞춰 씀
  FORMAT_GUIDE: {
    news: {
      look: ['언론사 계정: 자료실에 등록된 언론사인지, 인증 배지가 있는지, 아이디가 한 글자 다르지 않은지', '기자 이름과 인용: 누가 말했는지 이름·소속이 있는지', '기사 속 숫자·날짜: 자료실 숫자와 하나하나 대조'],
      fake: ['[단독] [속보] [긴급]을 단 사칭 언론사 (@doro_ilbo, @doroilbo_news)', '맞는 숫자 하나에 부풀린 숫자 섞기 (방문객 반토막, 드론 200대 추락)', '이름 없는 관계자·전문가의 말'],
      real: ['등록 언론사 + 기자 이름', '숫자가 자료실과 딱 맞음', '자극적이지 않은 평범한 소식이 오히려 진짜인 경우가 많음']
    },
    shorts: {
      look: ['채널: 가입일, 구독자에 비해 조회수가 지나치게 큰지', '영상을 찍은 날과 올린 날이 맞는지 ("방금"인데 3년 전 영상?)', '자막 속 "들었는데", "박사가 밝힌" 같은 말', 'AI 합성: 손가락·글자·그림자가 이상한지'],
      fake: ['옛날 영상을 지금 일처럼 올리기', '이름·소속 없는 가짜 전문가', '"직원 친구가 알려줌" 꿀팁', '챌린지·경품으로 이름·전화번호 모으기'],
      real: ['오래된 채널, 구독자와 조회수가 자연스러움', '직접 찍은 장면', '시간·높이·속도 같은 숫자가 자료실과 맞음']
    },
    story: {
      look: ['사진 찍은 시간과 올린 시간이 맞는지', '그 시간이 가능한지 (폐장 7시, 막배 7시 30분 뒤 밤 9시 불꽃놀이?)', '계정: 가입 며칠, 팔로워 몇 명인데 조회가 수만?', '"~래요", "친구한테 들음" 같은 건너 들은 말'],
      fake: ['없는 시간·지난 날짜로 바꾸기 (날짜 조작)', '공식인 척하는 이벤트·라이브 계정 (@doroland_event)', '양도·경품으로 연락처 모으기', '친구한테 들은 소문'],
      real: ['소소한 일상, 직접 겪은 일', '찍은 시간·올린 시간이 자연스럽게 이어짐', '작은 계정에 작은 조회수']
    }
  },

  // 가짜를 만들 때 쓰는 수법
  TACTICS: [""")
c = B[0]

# ================= page =================
PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'opBar' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)

# ---- CSS ----
r("""    .modal-box {""", """    /* 조 선택 (2026-11-09 새 디자인) */
    .tp { position: fixed; inset: 0; z-index: 60; overflow: auto; background: var(--bg); display: grid; place-items: center; padding: 32px 16px; }
    .tp[hidden] { display: none; }
    .tp::before { content: ""; position: fixed; inset: -20% -10% auto; height: 60vh; background: radial-gradient(60% 60% at 30% 40%, color-mix(in srgb, #d62976 16%, transparent), transparent 70%), radial-gradient(50% 60% at 75% 30%, color-mix(in srgb, #fa7e1e 14%, transparent), transparent 70%); pointer-events: none; }
    .tp-box { position: relative; width: min(820px, 100%); display: grid; gap: 28px; }
    .tp-head { text-align: center; display: grid; gap: 10px; justify-items: center; }
    .tp-logo { font-family: "Grand Hotel", cursive; font-size: 54px; line-height: 1; color: var(--ink); }
    .tp-head h2 { margin: 0; font-size: clamp(22px, 3vw, 30px); font-weight: 900; letter-spacing: -0.01em; word-break: keep-all; }
    .tp-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
    @media (max-width: 760px) { .tp-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
    @media (max-width: 520px) { .tp-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; } }
    .tp-team { position: relative; display: grid; justify-items: center; gap: 10px; padding: 20px 8px 16px; border-radius: 18px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; cursor: pointer; box-shadow: 0 1px 2px color-mix(in srgb, #262626 6%, transparent); transition: transform .18s cubic-bezier(.16,1,.3,1), box-shadow .18s, border-color .18s; }
    .tp-team .ring { width: clamp(64px, 9vw, 88px); aspect-ratio: 1; border-radius: 50%; padding: 3px; background: var(--ig-grad); }
    .tp-team .ring span { display: grid; place-items: center; width: 100%; height: 100%; border-radius: 50%; background: var(--surface); border: 3px solid var(--surface); font-size: clamp(26px, 3.4vw, 34px); font-weight: 900; font-variant-numeric: tabular-nums; }
    .tp-team b { font-size: 15px; }
    .tp-team em { position: absolute; top: 8px; right: 8px; font-style: normal; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 999px; background: var(--surface-2); color: var(--muted); }
    .tp-team:hover { transform: translateY(-3px); border-color: transparent; box-shadow: 0 10px 28px color-mix(in srgb, #d62976 18%, transparent); }
    .tp-team:active { transform: translateY(0) scale(.98); }
    .tp-team:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
    .tp-foot { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
    .tp-foot button { display: inline-flex; align-items: center; gap: 6px; min-height: 44px; padding: 0 16px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--muted); font: inherit; font-size: 14px; font-weight: 700; cursor: pointer; }
    .tp-foot button:hover { color: var(--ink); }
    @media (prefers-reduced-motion: no-preference) {
      .tp:not([hidden]) .tp-team { animation: tpIn .45s cubic-bezier(.16,1,.3,1) both; animation-delay: calc(var(--i) * 28ms); }
      @keyframes tpIn { from { opacity: 0; transform: translateY(10px); } }
    }
    /* 진행 막대: 운영자·진행 화면 */
    .opbar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin: 0 16px 18px; padding: 14px 16px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); }
    @media (min-width: 1024px) { .opbar { margin: 0 0 18px; } }
    .opbar .now { display: grid; gap: 2px; min-width: 0; }
    .opbar .now small { font-size: 12px; font-weight: 700; color: var(--muted); }
    .opbar .now b { font-size: 18px; }
    .opbar .prog { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; flex: 1; min-width: 220px; }
    .opbar .prog > span { font-size: 13px; font-weight: 700; margin-right: 4px; }
    .opbar .tm { display: grid; place-items: center; min-width: 30px; height: 30px; padding: 0 6px; border-radius: 999px; font-size: 12px; font-weight: 800; font-style: normal; background: var(--surface-2); color: var(--muted); }
    .opbar .tm.on { background: var(--real); color: #fff; }
    .opbar .tm.part { background: color-mix(in srgb, var(--real) 25%, var(--surface-2)); color: var(--ink); }
    .opbar .acts { display: flex; gap: 8px; margin-left: auto; flex-wrap: wrap; }
    .opbar .acts .btn { min-height: 40px; }
    body.screen .opbar .now b { font-size: 26px; } body.screen .opbar .tm { min-width: 40px; height: 40px; font-size: 15px; }
    .round-hint { margin: -4px 16px 14px; font-size: 14px; color: var(--muted); }
    @media (min-width: 1024px) { .round-hint { margin: -4px 0 14px; } }
    .make-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .make-head h2 { margin: 0; font-size: 20px; }
    .make-head .back { display: inline-flex; align-items: center; gap: 4px; min-height: 40px; padding: 0 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; font-weight: 700; cursor: pointer; }
    .modal-box {""")

# ---- HTML: 조 선택 ----
r("""  <div class="modal" id="teamModal" hidden>
    <div class="modal-box">
      <h2>우리 조를 골라 주세요</h2>
      <p class="muted small">이 노트북에서 판별하고 게시물을 올릴 조입니다.</p>
      <div class="team-grid" id="teamGrid"></div>
      <button class="btn btn-ghost" id="btnScreen" type="button"><i data-lucide="monitor" class="icon"></i>진행 화면으로 보기 (판별 안 함)</button>
    </div>
  </div>""", """  <div class="tp" id="teamModal" hidden role="dialog" aria-modal="true" aria-labelledby="tpTitle">
    <div class="tp-box">
      <div class="tp-head"><div class="tp-logo">Dorogram</div><h2 id="tpTitle">우리 조를 골라 주세요</h2></div>
      <div class="tp-grid" id="teamGrid"></div>
      <div class="tp-foot">
        <button id="btnScreen" type="button"><i data-lucide="monitor" class="icon"></i>진행 화면</button>
        <button id="btnTeacher" type="button"><i data-lucide="key-round" class="icon"></i>선생님</button>
      </div>
    </div>
  </div>""")
# ---- HTML: 진행 막대·라운드 안내·필터 ----
r("""      <div class="rounds" id="rounds" role="group" aria-label="라운드"></div>""",
  """      <div class="opbar" id="opBar" hidden></div>
      <div class="rounds" id="rounds" role="group" aria-label="라운드"></div>""")
r("""      <div class="round-head" id="roundHead"></div>
      <div class="filters" role="group" aria-label="게시물 거르기">
        <button class="chip" data-filter="all" aria-pressed="true">전체</button>
        <button class="chip" data-filter="todo" aria-pressed="false">아직 판별 안 함</button>
        <button class="chip" data-filter="mine" aria-pressed="false" hidden>우리 조가 만든 것</button>
        <span class="cnt" id="feedCnt"></span>
      </div>""", """      <div class="round-head" id="roundHead"></div>
      <p class="round-hint" id="roundHint" hidden></p>
      <div class="filters" id="filters" role="group" aria-label="게시물 거르기"></div>""")
r("""      <div class="mk-top">
        <div class="mission" id="missionCard"></div>""", """      <div class="make-head" id="makeHead"></div>
      <div class="mk-top">
        <div class="mission" id="missionCard"></div>""")

# ---- JS: 상태·도우미 ----
r("""const revealed = p => !!S.data && (""", """const isAdmin = () => !!(typeof AD !== 'undefined' && AD.key);
const STEP_ORDER = ROUND_ORDER.flatMap(f => ['read', 'make', 'judge', 'reveal'].map(k => [k, f]));
const STEP_LABEL = { read: '예시 보기', make: '만들기', judge: '판별', reveal: '정답 공개' };
const stepName = (k, f) => `${roundIdx(f) + 1}라운드 ${ROUND_LABEL[f]} · ${STEP_LABEL[k]}`;
const revealed = p => isAdmin() || !!S.data && (""")

# ---- 조 선택 ----
r("""function renderTeamGrid(n) {
  $('#teamGrid').innerHTML = Array.from({ length: n }, (_, i) => `<button type="button" aria-label="${i + 1}조" data-team="${i + 1}">${i + 1}</button>`).join('');
}""", """function renderTeamGrid(n) {
  const last = +load('dorogram-team') || 0;
  $('#teamGrid').innerHTML = Array.from({ length: n }, (_, i) => i + 1).map(t => `<button type="button" class="tp-team" style="--i:${t}" aria-label="${t}조" data-team="${t}">${t === last ? '<em>최근</em>' : ''}<span class="ring"><span>${t}</span></span><b>${t}조</b></button>`).join('');
}
/* 선생님(운영자): 조 없이 모든 라운드·게시물·정답을 본다 */
function enterAdmin(silent) {
  S.team = null; S.screen = false; document.body.classList.remove('screen'); document.body.classList.add('admin');
  $('#teamChipTxt').textContent = 'T'; $('#sbTeamAv').textContent = 'T'; $('#sbTeamTxt').textContent = '선생님';
  $('#teamModal').hidden = true; S.fmt = null; S.filter = 'all';
  showTab('feed'); refresh();
  if (!silent) toast('선생님 화면입니다. 모든 게시물과 정답이 보입니다.');
}
function leaveAdmin() {
  AD.key = null; AD.data = null; try { sessionStorage.removeItem('dorogram-admin'); } catch (e) {}
  document.body.classList.remove('admin'); S.fmt = null; showTab('feed'); $('#teamModal').hidden = false;
}""")
r("""  $('#btnScreen').onclick = () => setTeam(0);""", """  $('#btnScreen').onclick = () => setTeam(0);
  $('#btnTeacher').onclick = () => { $('#teamModal').hidden = true; showTab('admin'); };
  try { AD.key = sessionStorage.getItem('dorogram-admin'); } catch (e) {}""")
r("""  if (fixed === null || fixed === '') $('#teamModal').hidden = false;   /* 들어오면 먼저 조부터 고름 (2026-11-09 사용자) */""",
  """  if (AD.key) { renderTeamGrid(10); enterAdmin(true); return; }   /* 선생님 로그인이 남아 있으면 바로 선생님 화면 */
  if (fixed === null || fixed === '') $('#teamModal').hidden = false;   /* 들어오면 먼저 조부터 고름 (2026-11-09 사용자) */""")
r("""function setTeam(t, silent) {
  S.team = t || null; S.screen = t === 0;""", """function setTeam(t, silent) {
  S.team = t || null; S.screen = t === 0; document.body.classList.remove('admin');""")

# ---- refresh: 선생님은 운영자 상태, 단계가 바뀌면 지금 할 화면으로 ----
r("""    const d = await api('/state' + (S.team ? '?team=' + S.team : ''));""",
  """    const d = isAdmin() ? await adApi('/admin/state') : await api('/state' + (S.team ? '?team=' + S.team : ''));""")
r("""    if (roundChanged && S.fmt && S.fmt !== d.round) S.fmt = null;   /* 라운드가 넘어가면 첫 화면(타일)으로 */
    if (!S.form || (roundChanged && !S.editing)) resetForm();
    render();
""", """    if (!S.form || (roundChanged && !S.editing)) resetForm();
    if ((phaseChanged || roundChanged) && !isAdmin() && (S.team || S.screen) && ['feed', 'make'].includes(S.tab) && $('#teamModal').hidden) {
      /* 선생님이 단계를 넘기면 아이들 노트북·진행 화면이 지금 할 화면으로 따라감 */
      const say = { read: `${ROUND_LABEL[d.round]} 예시가 열렸어요`, make: `우리 조 ${ROUND_LABEL[d.round]}를 만들 시간이에요`, judge: `다른 조 ${ROUND_LABEL[d.round]}를 판별할 시간이에요`, reveal: '정답 공개!' }[d.phase];
      if (d.phase === 'make' && S.team) { S.fmt = d.round; showTab('make'); } else { showTab('feed'); S.fmt = d.round; S.filter = 'all'; }
      if (say) toast(say);
    }
    render();
""")
r("""  if (S.tab === 'admin' && AD.key) adRefresh();""", """  if (S.tab === 'admin' && AD.key) adRefresh();
  $$('[data-tab="make"]').forEach(b => b.hidden = true);   /* 만들기는 라운드 타일에서 들어감 */""")
r("""  $$('[data-tab="make"]').forEach(b => b.hidden = S.screen);
""", "")
r("""  if ((S.tab === 'score' && !d.scores) || (S.tab === 'make' && S.screen)) showTab('feed');""",
  """  if ((S.tab === 'score' && !d.scores) || (S.tab === 'make' && (S.screen || isAdmin() || !S.team || d.phase !== 'make'))) { showTab('feed'); S.fmt = d.round; }""")

r("""  $('[data-filter="mine"]').hidden = S.screen || !(d.posts || []).some(p => p.mine);
""", "")
# ---- feedPosts / canJudge / badges ----
r("""  let posts = d.posts.filter(p => p.status === 'approved' && !p.seed && (!S.fmt || p.format === S.fmt));   /* 예제는 학생 화면에 띄우지 않음 (2026-11-09 사용자) */
  if (S.filter === 'mine') posts = posts.filter(p => p.mine);""", """  let posts = d.posts.filter(p => p.status === 'approved' && (!S.fmt || p.format === S.fmt));   /* 예시는 서버가 그 라운드 예시 보기 때만 보냄, 선생님은 전부 */
  if (S.filter === 'seed') posts = posts.filter(p => p.seed);
  else if (S.filter === 'team') posts = posts.filter(p => !p.seed);
  else if (S.filter === 'mine') posts = posts.filter(p => p.mine);""")
r("""  return !p.seed && ph === 'judge' && p.format === curRound();""",
  """  if (isAdmin() || p.format !== curRound()) return false;
  return p.seed ? ph === 'read' : ph === 'judge';""")
r("""  const mine = S.data.myJudgments[p.id], reveal = revealed(p);
  if (p.seed && p.answer)""", """  const mine = S.data.myJudgments[p.id], reveal = revealed(p);
  if (isAdmin()) { const t = truthOf(p); return `<span class="${cls} ts-${t}">${p.seed ? '예시' : (p.team || '?') + '조'} · ${t === 'real' ? '진짜' : '가짜'}</span>`; }
  if (p.seed && p.answer)""")
r("""  if (p.seed) return `<div class="status-line st-seed">${ic('graduation-cap')}예제 자료 · 연습용 (점수 없음)</div>`;""",
  """  if (p.seed) return `<div class="status-line st-seed">${ic('graduation-cap')}예시 · 연습 (점수 없음)</div>`;""")

# ---- 첫 화면 타일 / 라운드 화면 / 진행 막대 ----
r("""function renderRounds() {
  const cur = roundIdx(curRound());
  $('#rounds').innerHTML = ROUND_ORDER.map((f, i) => {
    const now = i === cur, past = i < cur, n = (S.data.posts || []).filter(p => p.format === f && p.status === 'approved' && !p.seed).length;
    const st = now ? '지금 라운드' : past ? `끝난 라운드 · 게시물 ${n}개` : '앞 라운드가 끝나면 열립니다';
    return `<button type="button" class="round-tile${now ? ' now' : ''}" data-round="${f}" ${now || past ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${now || past ? '' : ' (잠김)'}">
      <span class="rt-ic">${ic(now || past ? ROUND_ICON[f] : 'lock')}</span><span><small>${i + 1}라운드</small><b>${ROUND_LABEL[f]}</b></span><span class="rt-st">${st}</span></button>`;
  }).join('');
}""", """function renderRounds() {
  const cur = roundIdx(curRound()), adm = isAdmin();
  $('#rounds').innerHTML = ROUND_ORDER.map((f, i) => {
    const now = i === cur, past = i < cur, open = now || past || adm, all = (S.data.posts || []).filter(p => p.format === f && p.status === 'approved');
    const n = all.filter(p => !p.seed).length;
    const st = adm ? (now ? STEP_LABEL[S.data.phase] + ' 중' : '') + `${now ? ' · ' : ''}예시 ${all.length - n} · 조 게시물 ${n}`
      : now ? '지금 라운드' : past ? `끝난 라운드 · 게시물 ${n}개` : '앞 라운드가 끝나면 열립니다';
    return `<button type="button" class="round-tile${now ? ' now' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">
      <span class="rt-ic">${ic(open ? ROUND_ICON[f] : 'lock')}</span><span><small>${i + 1}라운드</small><b>${ROUND_LABEL[f]}</b></span><span class="rt-st">${st}</span></button>`;
  }).join('');
}
/* 진행 막대: 선생님(다음 단계 버튼 포함)과 진행 화면에만. 이번 라운드에 올린 조·판별 끝낸 조를 번호로 보여 줌 */
function renderOpBar() {
  const box = $('#opBar'), d = S.data, adm = isAdmin();
  if (!adm && !S.screen) { box.hidden = true; return; }
  const pr = d.progress || { submitted: [], judged: {}, posts: 0, seeds: 0 }, n = d.teamCount, teams = Array.from({ length: n }, (_, i) => i + 1);
  let prog = '';
  if (d.phase === 'read') prog = `<span>예시 ${pr.seeds}개</span>`;
  else if (d.phase === 'make') prog = `<span>올린 조 ${pr.submitted.length} / ${n}</span>` + teams.map(t => `<i class="tm${pr.submitted.includes(t) ? ' on' : ''}">${t}</i>`).join('');
  else if (d.phase === 'judge') { const need = t => pr.posts - (pr.submitted.includes(t) ? 1 : 0), done = t => (pr.judged[t] || 0) >= need(t) && need(t) > 0;
    prog = `<span>판별 끝낸 조 ${teams.filter(done).length} / ${n}</span>` + teams.map(t => `<i class="tm${done(t) ? ' on' : (pr.judged[t] ? ' part' : '')}" title="${t}조 ${pr.judged[t] || 0} / ${need(t)}">${t}</i>`).join(''); }
  else if (d.scores) prog = `<span>순위</span>` + d.scores.slice(0, 3).map((r, i) => `<i class="tm on">${i + 1}위 ${r.team}조</i>`).join('');
  const k = STEP_ORDER.findIndex(([ph, f]) => ph === d.phase && f === d.round), next = STEP_ORDER[k + 1], prev = STEP_ORDER[k - 1];
  box.hidden = false;
  box.innerHTML = `<div class="now"><small>${adm ? '선생님 화면' : '진행 화면'}</small><b>${stepName(d.phase, d.round)}</b></div><div class="prog">${prog}</div>
    ${adm ? `<div class="acts">${prev ? `<button type="button" class="btn btn-ghost" data-step="${prev.join(':')}">${ic('chevron-left')}이전</button>` : ''}
      ${next ? `<button type="button" class="btn btn-primary" data-step="${next.join(':')}">다음: ${esc(stepName(...next))}${ic('chevron-right')}</button>` : ''}
      <button type="button" class="btn btn-ghost" data-act="leave-admin">선생님 화면 끝내기</button></div>` : ''}`;
}
async function goStep(spec) {
  const [phase, round] = spec.split(':');
  if (!confirm(`모든 노트북이 「${stepName(phase, round)}」 화면으로 바뀝니다. 넘길까요?`)) return;
  try { await adApi('/admin/phase', { phase, round }); await refresh(); toast(stepName(phase, round)); } catch (e) { toast(e.message); }
}
function renderFilters(posts) {
  const d = S.data, adm = isAdmin(), now = S.fmt === curRound(), chips = [['all', '전체']];
  if (adm) chips.push(['seed', '예시'], ['team', '조 게시물']);
  else {
    if (now && d.phase === 'judge') chips.push(['todo', '아직 판별 안 함']);
    if (d.posts.some(p => p.mine && p.format === S.fmt)) chips.push(['mine', '우리 조가 만든 것']);
  }
  if (!chips.some(c => c[0] === S.filter)) S.filter = 'all';
  $('#filters').innerHTML = (chips.length > 1 ? chips.map(([k, l]) => `<button type="button" class="chip" data-filter="${k}" aria-pressed="${S.filter === k}">${l}</button>`).join('') : '')
    + `<span class="cnt">${posts.length}개</span>`;
}""")
r("""function renderFeed() {
  const d = S.data, home = !S.fmt;
  $('#rounds').hidden = !home; $('#roundView').hidden = home;
  if (home) { renderRounds(); renderModal(); return; }
  const f = S.fmt, now = f === curRound(), posts = feedPosts(), judging = now && d.phase === 'judge';
  const canMakeNow = now && d.phase === 'make' && !S.screen && S.team;
  $('#roundHead').innerHTML = `<button type="button" class="back" data-act="home">${ic('chevron-left')}처음으로</button><h2>${roundIdx(f) + 1}라운드 · ${ROUND_LABEL[f]}</h2>${canMakeNow ? `<button type="button" class="btn btn-primary" data-goto="make">${ic('square-plus')}우리 조 ${ROUND_LABEL[f]} 만들기</button>` : ''}`;
  const empty = S.filter === 'todo' ? '다 판별했습니다.' : S.filter === 'mine' ? '우리 조가 만든 게시물이 없습니다.' : now && d.phase !== 'judge' && d.phase !== 'reveal' ? '다른 조 게시물은 판별 시간에 보입니다.' : '아직 게시물이 없습니다.';
  $('#feedCnt').textContent = `${judging ? '판별할 게시물' : '게시물'} ${posts.length}개`;""", """function renderFeed() {
  const d = S.data, home = !S.fmt;
  renderOpBar();
  $('#rounds').hidden = !home; $('#roundView').hidden = home;
  if (home) { renderRounds(); renderModal(); return; }
  const f = S.fmt, now = f === curRound(), posts = feedPosts(), adm = isAdmin(), L = ROUND_LABEL[f];
  const canMakeNow = now && d.phase === 'make' && !S.screen && S.team;
  $('#roundHead').innerHTML = `<button type="button" class="back" data-act="home">${ic('chevron-left')}처음으로</button><h2>${roundIdx(f) + 1}라운드 · ${L}</h2>${canMakeNow ? `<button type="button" class="btn btn-primary" data-goto="make">${ic('square-plus')}우리 조 ${L} 만들기</button>` : ''}`;
  const left = posts.filter(p => canJudge(p) && !d.myJudgments[p.id]).length;
  const hint = adm || !now ? '' : d.phase === 'read' ? `예시 ${L}를 눌러 진짜인지 가짜인지 골라 보세요. 고르면 바로 해설이 나와요.`
    : d.phase === 'make' ? (S.team ? `우리 조 ${L}를 만들 시간이에요.` : `조마다 ${L}를 만들고 있어요.`)
    : d.phase === 'judge' ? (S.team ? `다른 조 ${L}를 눌러 판별하세요. 남은 것 ${left}개` : `다른 조 ${L}를 판별하는 시간이에요.`) : '';
  $('#roundHint').hidden = !hint; $('#roundHint').textContent = hint;
  renderFilters(posts);
  const empty = S.filter === 'todo' ? '다 판별했습니다.' : S.filter === 'mine' ? '우리 조가 만든 게시물이 없습니다.' : now && d.phase === 'make' ? '다른 조 게시물은 판별 시간에 보입니다.' : '아직 게시물이 없습니다.';""")

# ---- 클릭: 타일·처음으로·다음 단계·선생님 끝내기·필터 ----
r("""  const rt = e.target.closest('[data-round]'); if (rt && !rt.disabled) { S.fmt = rt.dataset.round;""",
  """  const st = e.target.closest('[data-step]'); if (st) { goStep(st.dataset.step); return; }
  if (e.target.closest('[data-act="leave-admin"]')) { leaveAdmin(); return; }
  const fc = e.target.closest('#filters [data-filter]'); if (fc) { S.filter = fc.dataset.filter; renderFeed(); icons(); return; }
  const rt0 = e.target.closest('[data-round]');
  if (rt0 && !rt0.disabled && !isAdmin() && S.team && rt0.dataset.round === curRound() && S.data.phase === 'make') { S.fmt = curRound(); showTab('make'); return; }
  const rt = e.target.closest('[data-round]'); if (rt && !rt.disabled) { S.fmt = rt.dataset.round;""")
r("""$$('[data-filter]').forEach(b => b.onclick = () => { S.filter = b.dataset.filter; $$('[data-filter]').forEach(x => x.setAttribute('aria-pressed', x === b)); renderFeed(); icons(); });""", "")
r("""  const g = e.target.closest('[data-goto]'); if (g) { showTab(g.dataset.goto); return; }""",
  """  const g = e.target.closest('[data-goto]'); if (g) { const keep = S.fmt; showTab(g.dataset.goto); if (g.dataset.goto === 'make') S.fmt = keep; return; }""")

# ---- 만들기: 라운드 머리, 미리 쓰기 안내 삭제 ----
r("""  $('#makeNotice').hidden = d.phase === 'make';
  $('#makeNotice').innerHTML = `미리 써 볼 수는 있고, <b>공유하기</b>는 선생님이 만들기 시간을 열면 됩니다.`;""",
  """  $('#makeNotice').hidden = true;
  $('#makeHead').innerHTML = `<button type="button" class="back" data-act="home-make">${ic('chevron-left')}처음으로</button><h2>${roundIdx(curRound()) + 1}라운드 · 우리 조 ${ROUND_LABEL[curRound()]} 만들기</h2>`;""")
r("""  if (e.target.closest('[data-act="home"]')) {""", """  if (e.target.closest('[data-act="home-make"]')) { showTab('feed'); return; }
  if (e.target.closest('[data-act="home"]')) {""")

# ---- 운영자 로그인 → 선생님 화면, 진행 단계 12칸 ----
r("""  try { AD.data = await adApi('/admin/state'); try { sessionStorage.setItem('dorogram-admin', AD.key); } catch (e) {} $('#adPwErr').textContent = ''; adShow(); }""",
  """  try { AD.data = await adApi('/admin/state'); try { sessionStorage.setItem('dorogram-admin', AD.key); } catch (e) {} $('#adPwErr').textContent = ''; $('#adPw').value = ''; enterAdmin(); }""")
r("""  const RSTEP = { make: '만들기', judge: '판별', reveal: '정답 공개' };
  $('#adPhases').innerHTML = `<button class="ad-phase" data-adphase="read:news" aria-pressed="${d.phase === 'read'}"><b>시작 전</b><span>조를 고르고 자료실을 읽는 시간</span></button>`
    + ROUND_ORDER.map((f, i) => ['make', 'judge', 'reveal'].map(k => `<button class="ad-phase" data-adphase="${k}:${f}" aria-pressed="${d.phase === k && d.round === f}"><b>${i + 1}라운드 ${ROUND_LABEL[f]} · ${RSTEP[k]}</b><span>${k === 'make' ? `조마다 ${ROUND_LABEL[f]} 1개` : k === 'judge' ? `다른 조 ${ROUND_LABEL[f]} 판별` : '정답·점수 공개 (점수는 누적)'}</span></button>`).join('')).join('');""",
  """  const SDESC = { read: f => `예시 ${ROUND_LABEL[f]}로 연습 (바로 해설)`, make: f => `조마다 ${ROUND_LABEL[f]} 1개`, judge: f => `다른 조 ${ROUND_LABEL[f]} 판별`, reveal: () => '정답·점수 공개 (점수는 누적)' };
  $('#adPhases').innerHTML = STEP_ORDER.map(([k, f]) => `<button class="ad-phase" data-adphase="${k}:${f}" aria-pressed="${d.phase === k && d.round === f}"><b>${stepName(k, f)}</b><span>${SDESC[k](f)}</span></button>`).join('');""")
# ---- 형식별 안내 카드 + 예시 해설 보강 ----
r("""    .round-hint {""", """    .guide { margin: 0 16px 18px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); }
    @media (min-width: 1024px) { .guide { margin: 0 0 18px; } }
    .guide > summary { display: flex; align-items: center; gap: 8px; padding: 14px 16px; cursor: pointer; font-weight: 800; font-size: 16px; list-style: none; }
    .guide > summary::-webkit-details-marker { display: none; }
    .guide > summary .chev { margin-left: auto; transition: transform .2s; } .guide[open] > summary .chev { transform: rotate(180deg); }
    .guide-cols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 0 16px 16px; }
    @media (max-width: 900px) { .guide-cols { grid-template-columns: 1fr; } }
    .guide-col { border-radius: 10px; padding: 12px 14px; background: var(--surface-2); }
    .guide-col.fake { background: var(--fake-bg); } .guide-col.real { background: var(--real-bg); }
    .guide-col h4 { margin: 0 0 8px; font-size: 14px; } .guide-col.fake h4 { color: var(--fake); } .guide-col.real h4 { color: var(--real); }
    .guide-col ul { margin: 0; padding-left: 18px; display: grid; gap: 6px; font-size: 14px; line-height: 1.55; word-break: keep-all; }
    .ans-meta { display: grid; gap: 6px; margin-top: 8px; padding-top: 8px; border-top: 1px dashed color-mix(in srgb, currentColor 30%, transparent); font-size: 13.5px; line-height: 1.5; }
    .round-hint {""")
r("""      <p class="round-hint" id="roundHint" hidden></p>""", """      <p class="round-hint" id="roundHint" hidden></p>
      <div id="guideBox"></div>""")
r("""      <div class="mk-top">
        <div class="mission" id="missionCard"></div>""", """      <div id="makeGuide"></div>
      <div class="mk-top">
        <div class="mission" id="missionCard"></div>""")
r("""function renderFilters(posts) {""", """/* 형식별 안내: 확인할 곳 / 가짜가 숨는 곳 / 진짜의 특징 (예시 보기 때 펼침, 만들기 때 접힘) */
function guideHTML(f, open) {
  const g = (C.FORMAT_GUIDE || {})[f]; if (!g) return '';
  const col = (cls, t, list) => `<div class="guide-col ${cls}"><h4>${t}</h4><ul>${list.map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>`;
  return `<details class="guide"${open ? ' open' : ''}><summary>${ic('lightbulb')}${ROUND_LABEL[f]}에서 진짜·가짜 가려내기${ic('chevron-down', 'chev')}</summary>
    <div class="guide-cols">${col('', '확인할 곳', g.look)}${col('fake', '가짜가 숨는 곳', g.fake)}${col('real', '진짜의 특징', g.real)}</div></details>`;
}
function renderFilters(posts) {""")
r("""  $('#roundHint').hidden = !hint; $('#roundHint').textContent = hint;""",
  """  $('#roundHint').hidden = !hint; $('#roundHint').textContent = hint;
  $('#guideBox').innerHTML = (now && d.phase === 'read') || adm ? guideHTML(f, now && d.phase === 'read') : '';""")
r("""  $('#makeHead').innerHTML =""", """  $('#makeGuide').innerHTML = guideHTML(curRound(), false);
  $('#makeHead').innerHTML =""")
r("""  if (p.seed && p.answer) return `<div class="answer ${p.answer.truth}">${result(p.answer.truth)}<div>${verdictBadge(p.answer.truth)} <b>해설</b></div><div>${esc(p.answer.explain)}</div>${p.counts ? countsHTML(p.counts) : ''}</div>`;""",
  """  if (p.seed && p.answer) { const a = p.answer, cr = C.CRITERIA[a.criterion], tc = C.TACTICS.find(x => x.id === a.tactic);
    const meta = (cr ? `<div><b>${a.truth === 'fake' ? '들통나는 곳' : '진짜인 근거'}</b> ${esc(cr.label)}: ${esc(cr.hint)}</div>` : '') + (tc ? `<div><b>쓴 수법</b> ${esc(tc.id)}: ${esc(tc.desc)}</div>` : '');
    return `<div class="answer ${a.truth}">${result(a.truth)}<div>${verdictBadge(a.truth)} <b>해설</b></div><div>${esc(a.explain)}</div>${meta ? `<div class="ans-meta">${meta}</div>` : ''}${p.counts ? countsHTML(p.counts) : ''}</div>`; }""")
h = B[0]

for path, text, crlf in ((SP, s, s_crlf), (CP, c, c_crlf), (PP, h, h_crlf)):
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
print('ok')
