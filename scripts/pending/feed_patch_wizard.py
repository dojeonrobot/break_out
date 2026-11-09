# 2026-11-09 밤 도로그램 묶음 (사용자 요청 7건):
#  1 조 선택 뒤 첫 화면 빈 공간: 머리글(지금 라운드·할 일·바로 가기) + 타일이 화면 높이를 채움
#  2 만들기 화면 단계식(정하기 → 글 → 계정 → 확인·올리기), 선택 항목은 「더 채우기」로 접음
#  3 관리자가 진행 막대에서 단계를 골라 넘김
#  4 「운영자」「선생님」「주강사」 → 「관리자」
#  5 기사 카드: 언론사·기자 줄을 눈에 띄게, 목록 카드는 사진 위 검은 띠 대신 밝은 카드
#  6 예시: 인증 배지가 곧 진짜가 되지 않게 (인증 언론사의 가짜 3, 배지 없는 진짜 2, 인증 크리에이터의 가짜 스토리 1)
#  7 예시의 「연습·점수 없음」 문구 삭제
# 한 번만 적용.
import io, json, re, shutil, sys, os
ROOT = r'C:\Users\dlgus\break_out'


def opener(path):
    t = io.open(path, encoding='utf-8', newline='').read()
    return t.replace('\r\n', '\n'), '\r\n' in t


def make_r(box):
    def r(old, new, cnt=1):
        n = box[0].count(old)
        if n != cnt:
            sys.exit(f'{n}≠{cnt}: {old[:110]}')
        box[0] = box[0].replace(old, new)
    return r


PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'wizSteps' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)

# ---------- 4. 용어 ----------
lines = B[0].split('\n')
for i, l in enumerate(lines):
    if '연예인' in l:
        continue
    lines[i] = l.replace('선생님(운영자)', '관리자').replace('선생님', '관리자').replace('운영자', '관리자').replace('주강사만 사용합니다', '관리자만 사용합니다').replace('주강사', '관리자')
B[0] = '\n'.join(lines)

r(""".round-tile { position: relative; display: grid; grid-template-rows: 190px auto;""", """.round-tile { position: relative; display: grid; grid-template-rows: clamp(190px, calc(100dvh - 430px), 520px) auto;""")
r("""    .rt-lock { position: absolute; inset: 0 0 auto; height: 190px;""", """    .rt-lock { position: absolute; inset: 0 0 auto; height: clamp(190px, calc(100dvh - 430px), 520px);""")
# ---------- 7. 예시 연습 문구 ----------
r("""  if (p.seed) return `<div class="status-line st-seed">${ic('graduation-cap')}예시 · 연습 (점수 없음)</div>`;""", """  if (p.seed) return '';""")
r("""<p class="judge-q">${p.seed ? '이 글, 진짜일까요?' : '이 게시물은?'}</p>""", """<p class="judge-q">이 글, 진짜일까요?</p>""")
# ---------- 문구 손질 ----------
r("""<div><b>${me.correct} / ${me.judgable}</b>다른 조 게시물 중 맞힌 수</div><div><b>${me.fooled}</b>우리 가짜를 믿은 조</div><div><b>${rank}위</b>지금까지 합계 ${me.total}점</div>""",
  """<div><b>${me.correct} / ${me.judgable}</b>다른 조 글을 맞힌 수</div><div><b>${me.fooled}</b>우리 가짜에 속은 조</div><div><b>${rank}위</b>지금까지 ${me.total}점</div>""")
r("""<th class="num">맞힌 판별</th><th class="num">속인 조</th>""", """<th class="num">맞힌 수</th><th class="num">속인 조 수</th>""")
r("""<th>맞힌 판별</th><th>속인 조</th>""", """<th>맞힌 수</th><th>속인 조 수</th>""")
r("""${{ real: '진짜', fake: '가짜', unsure: '모르겠음' }[mine.verdict]}로 판정</span>""", """${{ real: '진짜라고 판정', fake: '가짜라고 판정', unsure: '모르겠음' }[mine.verdict]}</span>""")
r("""'진짜를 고르면 점수는 못 얻지만, 다른 조가 "조 글은 다 가짜"라고 넘겨짚지 못하게 합니다.' : '가짜를 진짜라고 믿은 조마다 1점을 얻습니다. 들킬 단서를 하나 꼭 남기세요.'""",
  """'진짜 글은 자료실 내용 그대로 씁니다. 진짜가 섞여 있어야 다른 조가 "조 글은 다 가짜"라고 넘겨짚지 못합니다.' : '우리 가짜에 속은 조 하나마다 1점입니다. 대신 다른 조가 찾아낼 수 있는 단서를 하나 남겨야 합니다.'""")
r("""const countsHTML = c => `<div class="counts"><span class="real"><b>${c.real}</b>진짜라고 한 조</span><span class="fake"><b>${c.fake}</b>가짜라고 한 조</span><span><b>${c.unsure}</b>모르겠음</span></div>`;""",
  """const countsHTML = c => `<div class="counts"><span class="real"><b>${c.real}</b>진짜라고 본 조</span><span class="fake"><b>${c.fake}</b>가짜라고 본 조</span><span><b>${c.unsure}</b>모르겠다고 한 조</span></div>`;""")
r("""'모르겠음으로 넘겼어요'""", """'모르겠다고 넘겼어요'""")

# ---------- 1. 첫 화면 ----------
r("""      <div class="rounds" id="rounds" role="group" aria-label="라운드"></div>""",
  """      <div class="home-head" id="homeHead" hidden></div>
      <div class="rounds" id="rounds" role="group" aria-label="라운드"></div>""")
r("""    .rounds { max-width: 1120px; gap: 20px; }""", """    .rounds { max-width: 1180px; gap: 20px; }
    .home-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; max-width: 1180px; margin: 0 16px 20px; padding: 4px 0 0; }
    @media (min-width: 1024px) { .home-head { margin: 0 0 20px; } }
    .home-head small { display: block; font-size: 13px; font-weight: 700; color: var(--muted); margin-bottom: 6px; }
    .home-head h1 { margin: 0; font-size: clamp(26px, 3.2vw, 36px); line-height: 1.15; letter-spacing: -0.01em; font-weight: 900; word-break: keep-all; }
    .home-head p { margin: 8px 0 0; font-size: 15px; color: var(--muted); word-break: keep-all; max-width: 44em; }
    .home-head .btn { min-height: 48px; padding: 0 22px; font-size: 16px; border-radius: 12px; }
    .art-news { padding-top: 14%; } .art-news .ph { height: 38%; min-height: 84px; }
    .art-shorts .phone { width: 36%; min-width: 104px; max-width: 220px; margin-top: 12%; }
    .art-story { padding-top: 8%; } .art-story .ring { width: 26%; max-width: 110px; height: auto; aspect-ratio: 1; } .art-story .ring:nth-child(2) { width: 32%; max-width: 134px; }""")
r("""function renderFeed() {
  const d = S.data, home = !S.fmt;
  renderOpBar();
  $('#rounds').hidden = !home; $('#roundView').hidden = home;
  if (home) { renderRounds(); renderModal(); return; }""",
"""function renderHomeHead() {
  const d = S.data, box = $('#homeHead'), f = curRound(), L = ROUND_LABEL[f], i = roundIdx(f) + 1;
  if (isAdmin() || S.screen) { box.hidden = true; return; }
  const txt = { read: [`${i}라운드 ${L} · 예시 보기`, `예시 ${L}를 눌러 진짜인지 가짜인지 골라 보세요. 고르면 바로 해설이 나와요.`, `${L} 예시 보기`],
    make: [`${i}라운드 ${L} · 만들기`, `우리 조 ${L}를 ${d.minPosts || 2}~${d.maxPosts}개 만드는 시간이에요. 진짜로 할지 가짜로 할지 글마다 정해요.`, `우리 조 ${L} 만들기`],
    judge: [`${i}라운드 ${L} · 판별`, `다른 조가 올린 ${L}를 하나씩 눌러 진짜인지 가짜인지 판정해요.`, `${L} 판별하러 가기`],
    reveal: [`${i}라운드 ${L} · 정답 공개`, `정답과 각 조가 숨긴 단서, 지금까지 점수를 확인해요.`, `정답 보기`] }[d.phase];
  box.hidden = false;
  box.innerHTML = `<div><small>지금 할 일</small><h1>${esc(txt[0])}</h1><p>${esc(txt[1])}</p></div><button type="button" class="btn btn-primary" data-round="${f}">${esc(txt[2])}${ic('chevron-right')}</button>`;
}
function renderFeed() {
  const d = S.data, home = !S.fmt;
  renderOpBar();
  $('#rounds').hidden = !home; $('#roundView').hidden = home;
  if (home) { renderHomeHead(); renderRounds(); renderModal(); return; }
  $('#homeHead').hidden = true;""")

# ---------- 3. 단계 선택 ----------
r("""    ${adm ? `<div class="acts">${prev ? `<button type="button" class="btn btn-ghost" data-step="${prev.join(':')}">${ic('chevron-left')}이전</button>` : ''}""",
  """    ${adm ? `<div class="acts"><select class="input" data-stepsel aria-label="단계 바로 가기" style="width:auto;min-height:40px">${STEP_ORDER.map(([ph, f]) => `<option value="${ph}:${f}" ${ph === d.phase && f === d.round ? 'selected' : ''}>${esc(stepName(ph, f))}</option>`).join('')}</select>${prev ? `<button type="button" class="btn btn-ghost" data-step="${prev.join(':')}">${ic('chevron-left')}이전</button>` : ''}""")
r("""document.addEventListener('change', e => {""", """document.addEventListener('change', e => {
  const ss = e.target.closest('[data-stepsel]'); if (ss) { const v = ss.value; const [ph, f] = v.split(':'); if (!(ph === S.data.phase && f === S.data.round)) goStep(v); return; }""", 1) if B[0].count("document.addEventListener('change', e => {") == 1 else None
if "data-stepsel]'); if (ss)" not in B[0]:
    r("""$('#fClueKind').addEventListener('change',""", """document.addEventListener('change', e => { const ss = e.target.closest('[data-stepsel]'); if (!ss) return; const v = ss.value, [ph, f] = v.split(':'); if (!(ph === S.data.phase && f === S.data.round)) goStep(v); else renderOpBar(); });
$('#fClueKind').addEventListener('change',""")

# ---------- 5. 기사 카드 ----------
r("""    .nc { width: 100%; border: 0; background: none; text-align: left; color: var(--ink); padding: 14px 16px; border-bottom: 1px solid var(--line); display: grid; gap: 8px; }
    .nc:hover { background: var(--surface-2); } .nc:last-child { border-bottom: 0; }""",
  """    .nc { width: 100%; border: 1px solid var(--line); background: var(--surface); text-align: left; color: var(--ink); padding: 0 0 14px; border-radius: 14px; overflow: hidden; display: grid; gap: 8px; transition: transform .18s cubic-bezier(.16,1,.3,1), box-shadow .18s; }
    .nc:hover { transform: translateY(-2px); box-shadow: 0 10px 26px color-mix(in srgb, #262626 12%, transparent); }
    .nc .ni-title, .nc .ni-sub, .nc .ni-meta, .nc .ni-outlet { padding: 0 14px; }
    .ni-outlet { display: flex; align-items: center; gap: 8px; font-size: 13.5px; font-weight: 800; margin-top: 4px; }
    .ni-outlet .ol { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; color: #fff; font-family: "Noto Serif KR", serif; font-weight: 900; letter-spacing: -0.01em; }
    .ni-outlet .ol .vb { background: #fff; color: var(--outlet, #262626); margin-left: 1px; }
    .ni-outlet .rp { color: var(--muted); font-weight: 600; font-size: 12.5px; }
    .nc-thumb { border-radius: 0; }
    .round-list .news-list { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
    .nw-logo { font-size: 28px; }
    .nw-by { background: #f6f7f9; margin: 12px 18px 0; padding: 10px 14px; border-radius: 12px; border: 0; gap: 8px 12px; font-size: 13px; }
    .nw-by .rp { font-size: 14.5px; } .nw-by .rp .avatar { width: 30px; height: 30px; font-size: 12px; }
    .nw-by .outlet { display: inline-flex; align-items: center; gap: 6px; font-weight: 800; color: #111; } .nw-by .outlet .hd { font-weight: 500; color: #666; }
    .nw-by .sep { flex-basis: 100%; height: 0; }
    .post-media.light { background: #e9ecef; }
    @media (prefers-color-scheme: dark) { .nw-by { background: #1e1e1e; } .nw-by .outlet { color: #f5f5f5; } .post-media.light { background: #1a1a1a; } }""")
r("""    <div class="nc-thumb">${img ? `<img src="${imgSrc(img)}" alt="" loading="lazy">` : `<span class="ph" style="background:linear-gradient(135deg, ${esc(a.color || '#4b5563')}, #111)">${ic('newspaper')}</span>`}<span class="ni-tag">${kindOf(a) === 'official' ? '공지' : '사회'}</span><span class="nc-outlet">${esc(a.name || '')}${vbadge(a)}</span></div>
    <div class="ni-title">""", """    <div class="nc-thumb">${img ? `<img src="${imgSrc(img)}" alt="" loading="lazy">` : `<span class="ph" style="background:linear-gradient(135deg, ${esc(a.color || '#4b5563')}, #111)">${ic('newspaper')}</span>`}<span class="ni-tag">${kindOf(a) === 'official' ? '공지' : '사회'}</span></div>
    <div class="ni-outlet" style="--outlet:${esc(a.color || '#262626')}"><span class="ol" style="background:${esc(a.color || '#262626')}">${esc(a.name || '')}${vbadge(a)}</span>${a.reporter ? `<span class="rp">${esc(a.reporter)} 기자</span>` : ''}</div>
    <div class="ni-title">""")
r("""    <div class="ni-meta"><span>${esc(a.name || '')}</span>${a.reporter ? `<span>· ${esc(a.reporter)} 기자</span>` : ''}${p.postedAt ? `<span>· ${esc(p.postedAt)}</span>` : ''}""",
  """    <div class="ni-meta">${p.postedAt ? `<span>${esc(p.postedAt)}</span>` : ''}""")
r("""      <div class="nw-by">${a.reporter ? `<span class="rp">${whoBtn(p, `<span class="avatar" style="background:${color}">${initials(a.reporter)}</span>${esc(a.reporter)} 기자`)}</span>` : (kind === 'official' ? `<span class="rp">${esc(a.name)}</span>` : '')}""",
  """      <div class="nw-by">${a.reporter ? `<span class="rp">${whoBtn(p, `<span class="avatar" style="background:${color}">${initials(a.reporter)}</span>${esc(a.reporter)} 기자`)}</span>` : (kind === 'official' ? `<span class="rp">${esc(a.name)}</span>` : '')}<span class="outlet">${esc(a.name || '')}${vbadge(a)}<span class="hd">${esc(a.handle || '')}</span></span>${kindChip(a)}<span class="sep"></span>""")
r("""    <div class="post-media${vert ? ' vert' : ''}">""", """    <div class="post-media${vert ? ' vert' : ''}${p.format === 'news' ? ' light' : ''}">""")

# ---------- 2. 만들기 단계식 ----------
r("""          <div class="igc-head">
            <button type="button" class="igc-cancel" id="btnCancelEdit" hidden>취소</button>
            <h2 id="igcTitle" style="grid-column:2">새 게시물 만들기</h2>
            <button type="submit" class="igc-share" id="btnSubmit">공유하기</button>
          </div>
          <div class="mk-body">""", """          <div class="igc-head">
            <button type="button" class="igc-cancel" id="btnCancelEdit" hidden>취소</button>
            <h2 id="igcTitle" style="grid-column:2">새 게시물 만들기</h2>
            <button type="submit" class="igc-share" id="btnSubmit" hidden>공유하기</button>
          </div>
          <ol class="wiz-steps" id="wizSteps" aria-label="만들기 단계"></ol>
          <div class="mk-body wiz">""")
r("""        </form>
      </div>
    </section>""", """          <div class="wiz-nav" id="wizNav"></div>
        </form>
      </div>
    </section>""")
r("""    .make-wrap { display: block; }""", """    .make-wrap { display: block; }
    .wiz-steps { list-style: none; margin: 0; padding: 12px 16px 0; display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; counter-reset: w; }
    .wiz-steps li { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 10px; font-size: 14px; font-weight: 700; color: var(--muted); background: var(--surface-2); cursor: pointer; }
    .wiz-steps li i { display: grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; background: var(--surface); color: var(--ink); font-style: normal; font-size: 12px; font-weight: 800; flex: none; }
    .wiz-steps li[aria-current="step"] { background: var(--ink); color: var(--surface); } .wiz-steps li[aria-current="step"] i { background: var(--surface); color: var(--ink); }
    .wiz-steps li.done i { background: var(--real); color: #fff; }
    .mk-body.wiz { display: block; }
    .mk-body.wiz .mk-col { display: none; border-left: 0; max-width: 760px; margin: 0 auto; padding: 18px 20px 8px; gap: 14px; }
    .mk-body.wiz .mk-col[data-on="1"] { display: flex; }
    .mk-body.wiz .mk-col.mk-check { max-width: 1040px; display: none; grid-template-columns: 300px 1fr; gap: 20px; align-items: start; } .mk-body.wiz .mk-col.mk-check[data-on="1"] { display: grid; }
    .mk-body.wiz .mk-h { font-size: 16px; }
    .mk-more { border: 1px dashed var(--line); border-radius: 12px; padding: 0 14px; } .mk-more > summary { cursor: pointer; padding: 12px 0; font-weight: 700; font-size: 14px; color: var(--muted); list-style: none; display: flex; align-items: center; gap: 8px; } .mk-more > summary::-webkit-details-marker { display: none; }
    .mk-more > summary .chev { margin-left: auto; transition: transform .2s; } .mk-more[open] > summary .chev { transform: rotate(180deg); }
    .mk-more > .inner { display: grid; gap: 10px; padding: 0 0 14px; }
    .mk-more.need { border-color: var(--blue); } .mk-more.need > summary { color: var(--blue); }
    .wiz-nav { display: flex; justify-content: space-between; gap: 10px; padding: 14px 20px 18px; border-top: 1px solid var(--line); background: var(--surface); }
    .mk-body.wiz { overflow: auto; min-height: 0; } .mk-body.wiz .mk-col { overflow: visible; min-height: 0; }
    .wiz-nav .btn { min-height: 46px; padding: 0 22px; font-size: 15px; border-radius: 12px; }
    .wiz-nav .grow { flex: 1; }
    @media (max-width: 760px) { .wiz-steps { grid-template-columns: repeat(2, 1fr); } .mk-body.wiz .mk-col.mk-check[data-on="1"] { grid-template-columns: 1fr; } }""")
# 포맷 선택 줄은 라운드가 정하므로 숨김
r("""              <div class="opt-row" id="optFormat"></div>""", """              <div class="opt-row" id="optFormat" hidden></div>""")
# 단계 로직
r("""function renderMake() {""", """/* 만들기 단계 (2026-11-09): 정하기 → 글 → 계정 → 확인·올리기. 선택 항목은 「더 채우기」로 접고, 단서가 그 항목을 쓰면 자동으로 펼친다 */
const WIZ = [['secret', '정하기'], ['write', '글 쓰기'], ['account', '계정'], ['check', '확인하고 올리기']];
function wizInit() {
  if (wizInit.done) return; wizInit.done = true;
  const cols = $$('.mk-body .mk-col'); if (cols.length < 4) return;
  cols[0].dataset.wstep = 'check'; cols[0].classList.add('mk-check'); cols[1].dataset.wstep = 'write'; cols[2].dataset.wstep = 'account'; cols[3].dataset.wstep = 'secret';
  const more = (host, id, title, ids) => { const d = document.createElement('details'); d.className = 'mk-more'; d.id = id;
    d.innerHTML = `<summary>${ic('plus')}${title}${ic('chevron-down', 'chev')}</summary><div class="inner"></div>`; const inner = d.querySelector('.inner');
    ids.forEach(sel => { const el = typeof sel === 'string' ? $(sel) : sel; if (el) inner.appendChild(el); }); host.appendChild(d); };
  // 글: 필수는 제목·부제·본문·사진, 나머지는 접음
  const photoH = $$('.mk-h', cols[1]).find(x => x.textContent.includes('사진'));
  const posted = $('#fPosted').closest('.igc-row'), taken = $('#fTaken').closest('.igc-row'), place = $('#fPlace').closest('.igc-row');
  more(cols[1], 'moreWrite', '더 채우기 (선택): 인용·숫자·태그·위치·투표·음악·올린 때·찍은 때', ['#newsExtra', '#tagsField', place, '#pollField', '#musicField', posted, taken, '#extraRow']);
  if (photoH) cols[1].insertBefore(photoH, $('#moreWrite')), cols[1].insertBefore($('#dropZone'), $('#moreWrite')), cols[1].insertBefore($('#fFile'), $('#moreWrite'));
  // 계정: 필수는 종류·이름·아이디·기자·색, 나머지는 접음
  const grid = $('.mk-grid', cols[2]); const opt = document.createElement('div'); opt.className = 'mk-grid';
  ['#fJoined', '#fFollowers', '#fPostsCount', '#fBio', '#fLikes', '#fViews', '#fCommentCount'].forEach(id => { const f = $(id).closest('.field'); if (f) opt.appendChild(f); });
  more(cols[2], 'moreAccount', '더 채우기 (선택): 가입한 때·팔로워·게시물 수·소개·좋아요·조회수·댓글 수', [opt]);
  // 썸네일·내 글 목록은 확인 단계로
  const th = $$('.mk-h', cols[2]).find(x => x.textContent.includes('썸네일')); const wrap = document.createElement('div'); wrap.style.cssText = 'display:grid;gap:10px;align-content:start';
  if (th) wrap.appendChild(th); wrap.appendChild($('#thumbFields')); cols[0].appendChild(wrap);
  $('#mkTop').appendChild($('#myPosts'));
  // 비밀 칸 머리 문구
  const sh = $('.mk-h', cols[3]); if (sh) sh.innerHTML = `${ic('lock-keyhole')}이 글을 진짜로 만들까요, 가짜로 만들까요? <span class="small muted" style="font-weight:400">다른 조에게는 정답 공개 때만 보입니다</span>`;
  $('#wizSteps').addEventListener('click', e => { const li = e.target.closest('li[data-w]'); if (li) wizGo(li.dataset.w); });
  $('#wizNav').addEventListener('click', e => { const b = e.target.closest('[data-wnav]'); if (!b) return; const i = WIZ.findIndex(w => w[0] === S.wstep);
    if (b.dataset.wnav === 'next') { if (wizCheck(S.wstep)) wizGo(WIZ[Math.min(i + 1, WIZ.length - 1)][0]); } else wizGo(WIZ[Math.max(i - 1, 0)][0]); });
}
function wizCheck(step) {
  const f = S.form, err = $('#formErr'); err.textContent = '';
  if (step === 'secret' && f.truth !== 'real') { const k = clueKind(f.clueKind);
    if (!k) { err.textContent = '들킬 단서 종류를 골라 주세요.'; return false; }
    if (k.fact && !f.fact) { err.textContent = '어긋나게 쓴 자료실 내용을 골라 주세요.'; return false; }
    if (!f.clue.trim()) { err.textContent = '어떻게 다르게 쓸지 한 줄 적어 주세요.'; return false; } }
  if (step === 'secret' && f.truth === 'real' && !f.basis) { err.textContent = '근거가 될 자료실 내용을 골라 주세요.'; return false; }
  if (step === 'write') { if (!f.body.trim() && !f.title.trim()) { err.textContent = '글을 써 주세요.'; return false; }
    if (f.format === 'news' && !f.title.trim()) { err.textContent = '기사 제목을 써 주세요.'; return false; }
    if (f.format === 'news' && paras(f.body).length < 2) { err.textContent = '기사는 문단을 2개 이상(빈 줄로 나눠) 써 주세요.'; return false; } }
  if (step === 'account' && !f.name.trim()) { err.textContent = C.FORMATS[f.format].authorLabel + '을(를) 써 주세요.'; return false; }
  return true;
}
function wizGo(step) { S.wstep = step; $('#formErr').textContent = ''; renderWiz(); $('#makeWrap').scrollIntoView({ block: 'start', behavior: 'smooth' }); }
function renderWiz() {
  wizInit(); if (!S.wstep) S.wstep = 'secret';
  const i = WIZ.findIndex(w => w[0] === S.wstep), f = S.form || {}, k = clueKind(f.clueKind);
  $('#wizSteps').innerHTML = WIZ.map(([id, l], j) => `<li data-w="${id}" class="${j < i ? 'done' : ''}" ${id === S.wstep ? 'aria-current="step"' : ''}><i>${j < i ? ic('check') : j + 1}</i>${l}</li>`).join('');
  $$('.mk-body .mk-col').forEach(c => c.dataset.on = c.dataset.wstep === S.wstep ? '1' : '0');
  $('#btnSubmit').hidden = S.wstep !== 'check';
  const needW = k && k.check === 'photo', needA = k && k.id === 'who-young';
  const mw = $('#moreWrite'), ma = $('#moreAccount');
  if (mw) { mw.classList.toggle('need', !!needW); if (needW) mw.open = true; }
  if (ma) { ma.classList.toggle('need', !!needA); if (needA) ma.open = true; }
  const tip = S.wstep === 'write' && needW ? '이 단서는 「더 채우기」의 올린 때·찍은 때를 둘 다 적어야 합니다.' : S.wstep === 'account' && needA ? '이 단서는 「더 채우기」의 가입한 때·팔로워·조회수를 적어야 합니다.' : S.wstep === 'write' && k && k.check === 'hear' ? '본문에 "들었는데", "~래요", "친구가" 같은 말을 넣으세요.' : S.wstep === 'account' && k && k.check === 'unreg' ? '계정 종류를 공식 계정이나 언론사로 두고, 등록 계정과 다른 아이디를 쓰세요.' : '';
  $('#wizNav').innerHTML = `${i > 0 ? `<button type="button" class="btn btn-ghost" data-wnav="prev">${ic('chevron-left')}이전</button>` : '<span></span>'}<span class="grow small muted" style="align-self:center;text-align:center">${esc(tip)}</span>${i < WIZ.length - 1 ? `<button type="button" class="btn btn-primary" data-wnav="next">다음: ${WIZ[i + 1][1]}${ic('chevron-right')}</button>` : `<button type="submit" class="btn btn-primary">${ic('send')}${S.editing ? '고친 내용 올리기' : '올리기'}</button>`}`;
}
function renderMake() {""")
r("""  if (canMake) fillForm();
}""", """  if (canMake) { fillForm(); renderWiz(); }
}""")
r("""      <div class="mk-top">
        <div class="mission" id="missionCard"></div>""", """      <div class="mk-top" id="mkTop">
        <div class="mission" id="missionCard"></div>""")
# 새 글 시작·수정 시작 때 첫 단계로
r("""  S.editing = null;
}
function renderMake() {""", """  S.editing = null; S.wstep = 'secret';
}
function renderMake() {""") if B[0].count("  S.editing = null;\n}\nfunction renderMake() {") == 1 else None
if "S.wstep = 'secret';\n}" not in B[0]:
    r("""    quoteText: '', quoteWho: '', stat1L: '', stat1V: '', stat2L: '', stat2V: '' };
  S.editing = null;""", """    quoteText: '', quoteWho: '', stat1L: '', stat1V: '', stat2L: '', stat2V: '' };
  S.editing = null; S.wstep = 'secret';""")
r("""  const f = S.form, err = $('#formErr'); err.textContent = '';
  if (!f.name.trim())""", """  const f = S.form, err = $('#formErr'); err.textContent = '';
  for (const [st] of WIZ) { if (st !== 'check' && !wizCheck(st)) { wizGo(st); return; } }
  if (!f.name.trim())""")
h = B[0]

# ---------- 6. 예시 ----------
SEED = ROOT + r'\server\ch5_seed.json'
seeds = json.load(open(SEED, encoding='utf-8'))
ids = {s['id'] for s in seeds}
IMG = ROOT + r'\server\seed_images'
NEW = []
if 'n-wheel120' not in ids:
    NEW += [
    {"id": "n-wheel120", "format": "news", "author": {"name": "도로일보", "handle": "@doroilbo", "kind": "press", "verified": True, "joined": "2009.07", "followers": "8.7만", "posts": "41,208", "bio": "도로랜드와 항구 도시 소식을 가장 빠르게.", "color": "#0f766e", "reporter": "서하늘"},
     "title": "도로랜드 관람차 120m로 증축 완료… 국내 최고 높이 등극", "subhead": "캐빈 48개로 늘려 한 바퀴 20분… 운영실 \"15주년 선물\"",
     "body": "도로랜드의 상징인 관람차가 높이 120m로 증축을 마치고 이번 주말 다시 문을 연다. 기존보다 32m 높아져 국내에서 가장 높은 관람차가 됐다.\n\n캐빈도 36개에서 48개로 늘었고, 한 바퀴 도는 시간은 20분으로 길어졌다. 운영실은 \"내년 15주년을 앞둔 선물\"이라고 설명했다.\n\n야간 조명 1만 2천 개는 예정대로 내년 5월 5일에 켜진다.",
     "quote": {"text": "꼭대기에서는 항구 너머 산까지 보입니다.", "who": "도로랜드 운영실"}, "stats": [{"label": "관람차 높이", "value": "120m"}, {"label": "캐빈", "value": "48개"}],
     "tags": "", "place": "도로랜드", "postedAt": "4시간 전", "editedAt": "", "photoTakenAt": "어제", "views": "6.4만", "commentCount": 318,
     "comments": [{"name": "관람차덕후", "text": "88m 아니었어요? 언제 공사했지", "likes": 210, "time": "3시간 전"}, {"name": "항구주민", "text": "공사하는 거 본 적 없는데…", "likes": 142, "time": "2시간 전"}],
     "images": {"main": "ferris wheel at an amusement park by the sea, daytime, tall structure, photo"},
     "secret": {"truth": "fake", "tactic": "숫자 부풀리기", "clue": "자료실에 관람차는 높이 88m, 캐빈 36개, 한 바퀴 14분. 증축 소식은 자료실 어디에도 없음.", "clueCriterion": "cross", "clueKind": "cross", "fact": "관람차: 높이 88m, 캐빈 36개, 한 바퀴 14분. 밤 8시 이후 운행 안 함"},
     "answer": {"truth": "fake", "explain": "가짜입니다. 도로일보의 진짜 계정(@doroilbo, 인증 배지)이 맞지만, 자료실에 관람차는 높이 88m·캐빈 36개·한 바퀴 14분으로 나와 있고 증축 소식은 어디에도 없습니다. 등록 언론사도 틀린 숫자를 낼 수 있으니 인증 배지만 믿지 말고 숫자는 자료실과 대조해야 합니다."}},
    {"id": "n-anniv-now", "format": "news", "author": {"name": "서해바다신문", "handle": "@seohaenews", "kind": "press", "verified": True, "joined": "2011.03", "followers": "4.2만", "posts": "18,210", "bio": "서해안 항구 도시의 지역 신문. 바다·항구·섬 소식을 전합니다.", "color": "#1d4ed8", "reporter": "정해솔"},
     "title": "도로랜드 개장 15주년 기념식 내일 오전 10시 항구 광장서… 관람차 조명 쇼도 첫 점등", "subhead": "시장·운영실장 참석, 시민 1,000명 초청",
     "body": "도로랜드 개장 15주년 기념식이 내일 오전 10시 항구 광장에서 열린다. 운영실은 시민 1,000명을 초청해 기념 공연과 관람차 조명 쇼 첫 점등을 함께 진행한다고 밝혔다.\n\n기념식 뒤에는 15주년 기념 입장권 할인도 시작된다. 어른 54,000원인 입장권을 당일 한정 반값에 판다.",
     "quote": {"text": "15년을 함께한 시민들께 감사하는 자리입니다.", "who": "도로랜드 운영실장"}, "stats": [{"label": "기념식", "value": "내일 10시"}, {"label": "초청", "value": "1,000명"}],
     "tags": "", "place": "항구 광장", "postedAt": "어제", "editedAt": "", "photoTakenAt": "", "views": "2.8만", "commentCount": 96,
     "comments": [{"name": "달력보는사람", "text": "15주년 내년 5월 아니에요?", "likes": 188, "time": "어제"}],
     "images": {"main": "festival stage being set up at a harbour square, bunting, morning light, photo"},
     "secret": {"truth": "fake", "tactic": "날짜 조작", "clue": "자료실: 개장은 5월 5일, 내년 5월 5일이 15주년. 지금은 10월이라 15주년 기념식이 내일일 수 없음. 조명 쇼도 내년 5월 5일 예정.", "clueCriterion": "when", "clueKind": "when-archive", "fact": "개장: 5월 5일 개장. 내년 5월 5일이 개장 15주년"},
     "answer": {"truth": "fake", "explain": "가짜입니다. 서해바다신문의 진짜 계정이지만 날짜가 틀렸습니다. 자료실에 개장일은 5월 5일이고 15주년은 내년 5월 5일인데, 지금은 10월입니다. 관람차 조명 쇼도 운영실 입장에 내년 5월 5일 예정이라고 되어 있습니다. 인증 배지가 있어도 날짜는 자료실 연표와 맞춰 봐야 합니다."}},
    {"id": "n-fastpass", "format": "news", "author": {"name": "도로일보", "handle": "@doroilbo", "kind": "press", "verified": True, "joined": "2009.07", "followers": "8.7만", "posts": "41,211", "bio": "도로랜드와 항구 도시 소식을 가장 빠르게.", "color": "#0f766e", "reporter": "한바다"},
     "title": "[단독] 도로랜드, 다음 달부터 '프리패스' 도입… 관계자 \"내부 결정 끝났다\"", "subhead": "3만 원 더 내면 모든 기구 줄 안 서… 일반 관람객 대기 시간 늘어날 듯",
     "body": "도로랜드가 다음 달부터 줄을 서지 않고 놀이기구를 타는 '프리패스'를 도입하는 것으로 알려졌다. 도로랜드 사정에 밝은 한 관계자는 \"내부 결정은 이미 끝났고 발표만 남았다\"고 전했다.\n\n프리패스는 입장권에 3만 원을 더 내면 모든 기구의 우선 탑승 줄을 이용하는 방식이다. 일반 관람객의 대기 시간은 지금보다 길어질 전망이다.",
     "quote": {"text": "내부 결정은 이미 끝났고 발표만 남았다.", "who": "도로랜드 사정에 밝은 관계자"}, "stats": [{"label": "추가 요금", "value": "3만 원"}],
     "tags": "", "place": "", "postedAt": "6시간 전", "editedAt": "", "photoTakenAt": "", "views": "9.1만", "commentCount": 540,
     "comments": [{"name": "줄서는아빠", "text": "이러면 일반 줄은 더 길어지는 거 아님?", "likes": 420, "time": "5시간 전"}, {"name": "운영실", "text": "우선탑승권·프리패스 도입 계획은 없습니다.", "likes": 610, "time": "4시간 전"}],
     "images": {"main": "long queue of visitors at an amusement park ride entrance, overcast day, photo"},
     "secret": {"truth": "fake", "tactic": "가짜 전문가", "clue": "이름 없는 '관계자' 말뿐이고, 자료실 운영실 입장에 '우선탑승권·프리패스 같은 줄 안 서는 제도는 없음'이라고 되어 있음.", "clueCriterion": "cross", "clueKind": "cross", "fact": "운영실 입장: 내년 입장권 요금은 동결(지난달 발표). 우선탑승권·프리패스 같은 줄 안 서는 제도는 없음."},
     "answer": {"truth": "fake", "explain": "가짜입니다. 등록 언론사 도로일보의 기사이지만 근거가 이름도 소속도 없는 '관계자' 한 사람뿐입니다. 자료실 운영실 입장에는 우선탑승권·프리패스 같은 줄 안 서는 제도는 없다고 분명히 적혀 있습니다. 인증 배지와 [단독]이 붙어도 출처 없는 말은 사실이 아닐 수 있습니다."}},
    {"id": "n-ferry-guide", "format": "news", "author": {"name": "섬여행 노트", "handle": "@island_note", "kind": "creator", "verified": False, "joined": "2018.05", "followers": "8,400", "posts": "612", "bio": "섬 여행 정보를 정리하는 개인 채널. 도로랜드는 1년에 열 번쯤 갑니다.", "color": "#7c3aed", "reporter": ""},
     "title": "도로랜드 가는 배 시간표 총정리: 매시 정각 출발, 25분, 막배는 7시 30분", "subhead": "주말은 30분 간격… 섬에서 나오는 배는 매시 30분",
     "body": "도로랜드에 처음 가는 분들이 가장 많이 묻는 게 배 시간이다. 항구에서 섬으로 가는 배는 오전 9시부터 오후 6시까지 매시 정각에 출발하고, 주말에는 30분 간격으로 늘어난다.\n\n섬에서 항구로 돌아오는 배는 오전 10시 30분부터 매시 30분에 있고, 막배는 오후 7시 30분이다. 배는 도로1호와 도로2호 두 척이 번갈아 다니며 한 번에 520명이 타고 25분 걸린다.\n\n막배를 놓치면 섬에서 나올 방법이 없으니 7시쯤에는 선착장 쪽으로 움직이는 게 좋다.",
     "quote": None, "stats": [{"label": "소요 시간", "value": "25분"}, {"label": "막배", "value": "7시 30분"}],
     "tags": "", "place": "도로랜드 선착장", "postedAt": "3일 전", "editedAt": "", "photoTakenAt": "지난 주말", "views": "1.9만", "commentCount": 73,
     "comments": [{"name": "첫방문", "text": "정리 감사해요 주말 30분 간격 몰랐음", "likes": 95, "time": "3일 전"}],
     "images": {"main": "white passenger ferry leaving a small harbour toward an island, clear sky, photo"},
     "secret": {"truth": "real", "tactic": "", "clue": "배 시간·소요 시간·막배·척수·정원이 자료실 배 정보와 모두 맞음. 오래된 개인 채널.", "clueCriterion": "cross", "clueKind": "", "fact": "배 섬 → 항구: 오전 10시 30분 ~ 오후 7시 30분, 매시 30분. 막배 7시 30분"},
     "answer": {"truth": "real", "explain": "진짜입니다. 인증 배지가 없는 개인 채널이지만 2018년부터 꾸준히 쓴 계정이고, 배 출발 시간·주말 간격·소요 시간 25분·막배 7시 30분·배 2척 520명이 자료실 배 정보와 모두 맞습니다. 배지가 없다고 가짜인 것은 아닙니다. 내용을 자료실과 대조하면 됩니다."}},
    {"id": "n-coaster-why", "format": "news", "author": {"name": "놀이기구 리뷰어", "handle": "@ride_review", "kind": "creator", "verified": False, "joined": "2017.09", "followers": "2.3만", "posts": "1,048", "bio": "전국 놀이기구를 타 보고 기록합니다.", "color": "#ea580c", "reporter": ""},
     "title": "도로랜드 롤러코스터 정점에서 바다가 보이는 이유… 최고 높이 42m, 시속 92km", "subhead": "섬 가장자리에 세운 덕에 꼭대기에서 수평선이 보인다",
     "body": "도로랜드 롤러코스터는 최고 높이 42m, 최고 속도 시속 92km다. 숫자만 보면 국내 다른 코스터와 비슷하지만, 정점에서 바다가 보인다는 점이 다르다.\n\n이유는 위치다. 코스터가 섬 가장자리에 세워져 있어 꼭대기에 올라가면 가리는 건물 없이 수평선이 보인다. 내려올 때는 바다 쪽으로 떨어지는 느낌이 나서 체감 속도가 더 빠르다.\n\n맨 앞자리는 대기 줄이 따로 있으니 시간이 넉넉할 때 타는 걸 추천한다.",
     "quote": None, "stats": [{"label": "최고 높이", "value": "42m"}, {"label": "최고 속도", "value": "시속 92km"}],
     "tags": "", "place": "도로랜드", "postedAt": "5일 전", "editedAt": "", "photoTakenAt": "지난달", "views": "3.3만", "commentCount": 120,
     "comments": [{"name": "앞자리파", "text": "앞자리 줄 따로 있는 거 꿀팁", "likes": 77, "time": "5일 전"}],
     "images": {"main": "roller coaster track on a cliff edge above the sea, riders at the top, sunny day, photo"},
     "secret": {"truth": "real", "tactic": "", "clue": "최고 높이 42m·시속 92km·정점에서 바다가 보임이 자료실 놀이기구 정보와 맞음.", "clueCriterion": "cross", "clueKind": "", "fact": "롤러코스터: 최고 높이 42m, 최고 속도 시속 92km, 정점에서 바다가 보임"},
     "answer": {"truth": "real", "explain": "진짜입니다. 배지 없는 개인 채널이지만 2017년부터 활동했고, 최고 높이 42m·시속 92km·정점에서 바다가 보인다는 내용이 자료실 놀이기구 정보와 맞습니다. 숫자가 자료실과 맞으면 배지가 없어도 믿을 수 있습니다."}},
    {"id": "t-guy-free", "format": "story", "author": {"name": "롤코타는남자", "handle": "@coaster_guy", "kind": "creator", "verified": True, "joined": "2017.02", "followers": "112만", "posts": "2,310", "bio": "놀이기구 리뷰 채널", "color": "#dc2626"},
     "title": "", "body": "친구가 그러는데 내일 사파리 기린 투어 무료래요 🦒\n\n저도 들은 얘기라 확실하진 않은데 일단 공유!! 내일 가서 확인해 볼게요",
     "slides": [{"img": "main", "text": "친구가 그러는데 내일 사파리 기린 투어 무료래요 🦒", "time": "40분 전"}, {"img": None, "text": "저도 들은 얘기라 확실하진 않은데 일단 공유!! 내일 가서 확인해 볼게요", "sticker": {"type": "question", "text": "아는 사람?"}, "time": "39분 전"}],
     "tags": "", "place": "", "postedAt": "40분 전", "photoTakenAt": "지난달", "likes": "", "views": "21만",
     "images": {"main": "giraffe leaning toward a safari jeep window at a zoo park, vertical photo"},
     "secret": {"truth": "fake", "tactic": "들은 이야기", "clue": "'친구가 그러는데', '들은 얘기'라고 본인이 밝힘. 자료실 운영실 입장에 @doroland 외의 무료 개방 안내는 운영실과 관계없다고 되어 있음.", "clueCriterion": "witness", "clueKind": "witness-hear", "fact": ""},
     "answer": {"truth": "fake", "explain": "믿을 수 없습니다. 인증 배지가 있는 유명 크리에이터지만 본인이 '친구가 그러는데', '들은 얘기'라고 쓴 건너 들은 말입니다. 자료실 운영실 입장에는 @doroland 밖에서 전해지는 무료 개방 안내는 운영실과 관계없다고 되어 있습니다. 인증 배지는 그 사람이 진짜라는 뜻이지, 그 사람이 들은 소문이 사실이라는 뜻은 아닙니다."}},
    ]
    copies = {'n-wheel120': 'n-light-main.jpg', 'n-anniv-now': 'n-drone-main.jpg', 'n-fastpass': 'n-price-main.jpg', 'n-ferry-guide': 'n-3y-main.jpg', 'n-coaster-why': 'n-6y-main.jpg', 't-guy-free': 't-viking-main.jpg'}
    for s in NEW:
        src = os.path.join(IMG, copies[s['id']]); dst = os.path.join(IMG, s['id'] + '-main.jpg')
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
    seeds.extend(NEW)
    with open(SEED, 'w', encoding='utf-8') as f:
        json.dump(seeds, f, ensure_ascii=False, indent=1)

# ---------- config 문구 ----------
CP = ROOT + r'\chapter05\feed-config.js'
c, c_crlf = opener(CP)
c = c.replace("    read:   { label: '예시 보기', desc: '이번 라운드 형식의 예시를 보고 진짜인지 가짜인지 골라 봅니다. 고르면 바로 해설이 나오고 점수에는 들어가지 않습니다.' },",
              "    read:   { label: '예시 보기', desc: '이번 라운드 형식의 예시를 보고 진짜인지 가짜인지 골라 봅니다. 고르면 바로 해설이 나옵니다.' },")
c = c.replace('// 진행 단계 (운영자 탭에서 넘김)', '// 진행 단계 (관리자가 넘김)')
c = c.replace("      real: ['등록 언론사 + 기자 이름', '숫자가 자료실과 딱 맞음', '자극적이지 않은 평범한 소식이 오히려 진짜인 경우가 많음']",
              "      real: ['숫자·날짜가 자료실과 딱 맞음', '배지 없는 개인 채널도 내용이 자료실과 맞으면 진짜', '자극적이지 않은 평범한 소식이 오히려 진짜인 경우가 많음']")
c = c.replace("      fake: ['[단독] [속보] [긴급]을 단 사칭 언론사 (@doro_ilbo, @doroilbo_news)', '맞는 숫자 하나에 부풀린 숫자 섞기 (방문객 반토막, 드론 200대 추락)', '이름 없는 관계자·전문가의 말'],",
              "      fake: ['[단독] [속보] [긴급]을 단 사칭 언론사 (@doro_ilbo, @doroilbo_news)', '맞는 숫자 하나에 부풀린 숫자 섞기 (방문객 반토막, 관람차 120m)', '이름 없는 관계자·전문가의 말', '인증 배지가 있는 진짜 언론사도 틀린 숫자·날짜를 낼 수 있음'],")

for path, text, crlf in ((PP, h, h_crlf), (CP, c, c_crlf)):
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
print('ok', len(NEW), '예시 추가')
