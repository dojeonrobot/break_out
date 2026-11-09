# 2026-11-09 도로그램 단서 규칙 (사용자 결정):
#  - 가짜의 단서는 다른 조가 확인할 수 있는 것만: 자료실 사실과 어긋남(사실 고르기 필수) / 등록 안 된 공식·언론사 계정 / 찍은 때가 올린 때보다 뒤 / 건너 들은 말투(본문에 그 표현이 있어야 함)
#  - 수법은 조별 배정 없이 자유 선택(선택 사항)
#  - 선생님 검토: 운영자 화면에 단서·사실이 보이고 「돌려보내기」(status returned + 메모) → 그 조 만들기 화면에 안내, 고쳐서 다시 올리면 approved
#  - 판별 중 상세 창은 「자료 대조」 패널을 기본으로 펼침
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
if "'returned'" in s:
    sys.exit('서버: 이미 적용됨')
B = [s]; r = make_r(B)
r("""            'secret': {'truth': 'real' if secret.get('truth') == 'real' else 'fake', 'tactic': clean_text(secret.get('tactic'), 30),
                       'clue': clean_text(secret.get('clue'), 200), 'clueCriterion': secret.get('clueCriterion')
                       if secret.get('clueCriterion') in CRITERIA else None},
        }""", """            'secret': {'truth': 'real' if secret.get('truth') == 'real' else 'fake', 'tactic': clean_text(secret.get('tactic'), 30),
                       'clue': clean_text(secret.get('clue'), 200), 'clueCriterion': secret.get('clueCriterion')
                       if secret.get('clueCriterion') in CRITERIA else None,
                       'clueKind': clean_text(secret.get('clueKind'), 40), 'fact': clean_text(secret.get('fact'), 300)},   # 2026-11-09: 확인 가능한 단서 종류와 어긋나게 쓴 자료실 사실
        }
        if post['secret']['truth'] == 'fake' and post['secret']['clueKind'] in ('cross', 'when-archive') and not post['secret']['fact']:
            raise ValueError('어긋나게 쓴 자료실 내용을 골라 주세요.')""")
r("""                old.update(post, **ai_meta, updatedAt=now_ms())""", """                old.update(post, **ai_meta, updatedAt=now_ms(), status='approved' if old.get('status') == 'returned' else old.get('status', 'approved'), note='')   # 돌려보낸 글을 고쳐 올리면 다시 올라감""")
r("""        if action not in ('hide', 'show'):
            raise ValueError('없는 동작입니다.')""", """        if action not in ('hide', 'show', 'return'):
            raise ValueError('없는 동작입니다.')""")
r("""            p['status'] = 'hidden' if action == 'hide' else 'approved'
            p['note'] = clean_text(b.get('note'), 120)""", """            if p.get('seed') and action == 'return':
                raise ValueError('예시는 돌려보낼 수 없습니다.')
            p['status'] = {'hide': 'hidden', 'show': 'approved', 'return': 'returned'}[action]
            p['note'] = clean_text(b.get('note'), 120)""")
# own posts visible whatever the status (so a returned post can be fixed); note goes to the owner and the admin
r("""    if p['status'] != 'approved':
        return False
    if p.get('seed'):   # 예시는 그 라운드의 「예시 보기」 때만 (2026-11-09)
        return DB['phase'] == 'read' and p.get('format') == DB.get('round')
    if team and p['team'] == team:
        return True""", """    if team and not p.get('seed') and p['team'] == team:
        return True   # 우리 조 글은 돌려보낸 것도 보인다 (고쳐서 다시 올리려고)
    if p['status'] != 'approved':
        return False
    if p.get('seed'):   # 예시는 그 라운드의 「예시 보기」 때만 (2026-11-09)
        return DB['phase'] == 'read' and p.get('format') == DB.get('round')""")
r("""    if own:
        out['mine'] = True
        out['secret'] = p.get('secret')""", """    if own:
        out['mine'] = True
        out['secret'] = p.get('secret')
        out['note'] = p.get('note') or ''""")
r("""    if admin:
        out.update(createdAt=p.get('createdAt'), seedKey=p.get('seedKey'))""", """    if admin:
        out.update(createdAt=p.get('createdAt'), seedKey=p.get('seedKey'), note=p.get('note') or '')""")
r("""    return {'submitted': sorted({p['team'] for p in posts}), 'judged': judged, 'posts': len(posts),""",
  """    returned = sorted({p['team'] for p in DB['posts'] if not p.get('seed') and p['status'] == 'returned' and p.get('format') == rd})
    return {'submitted': sorted({p['team'] for p in posts}), 'judged': judged, 'posts': len(posts), 'returned': returned,""")
s = B[0]

# ================= config =================
CP = ROOT + r'\chapter05\feed-config.js'
c, c_crlf = opener(CP)
B = [c]; r = make_r(B)
r("""  // 가짜를 만들 때 쓰는 수법
  TACTICS: [""", """  // 가짜가 들킬 단서의 종류 (2026-11-09): 다른 조가 자료실·계정 정보·본문에서 확인할 수 있는 것만 허용한다.
  // fact: true 면 어긋나게 쓴 자료실 내용을 고른다. check 는 본문 검사 종류.
  CLUE_KINDS: [
    { id: 'cross',        crit: 'cross',   fact: true,  label: '자료실 내용과 어긋나게 썼다', hint: '숫자·시간·사실 하나를 자료실과 다르게. 맞는 내용을 섞어 그럴듯하게 만들어도 그 하나는 자료실로 들통납니다.' },
    { id: 'who-unreg',    crit: 'who',     fact: false, label: '등록되지 않은 공식·언론사 계정으로 썼다', hint: '계정 종류를 공식 계정이나 언론사로 두고, 자료실 등록 계정(@doroland·@doroilbo·@seohaenews)과 다른 아이디를 씁니다. 한 글자 바꾸기도 됩니다.', check: 'unreg' },
    { id: 'who-young',    crit: 'who',     fact: false, label: '가입한 지 얼마 안 된 계정인데 조회수·팔로워가 지나치게 크다', hint: '가입한 때를 최근으로, 팔로워는 적게, 조회수·좋아요는 크게 씁니다.' },
    { id: 'when-archive', crit: 'when',    fact: true,  label: '자료실의 시간·날짜와 어긋나게 썼다', hint: '운영 시간(10~19시), 막배 7시 30분, 행사 날짜와 맞지 않는 때를 씁니다. 자료실에 없는 시간을 바꾸는 건 아무도 못 맞추니 안 됩니다.' },
    { id: 'when-photo',   crit: 'when',    fact: false, label: '사진·영상 찍은 때가 올린 때보다 뒤다', hint: '올린 때와 찍은 때를 둘 다 적고, 찍은 때를 더 뒤로 씁니다.', check: 'photo' },
    { id: 'witness-hear', crit: 'witness', fact: false, label: '직접 본 게 아니라 들은 이야기로 썼다', hint: '본문에 "들었는데", "~래요", "친구가" 같은 말이 들어가야 합니다. 판별하는 조가 직접 목격 버튼을 누르면 그 말이 형광펜으로 표시됩니다.', check: 'hear' }
  ],

  // 가짜를 만들 때 쓰는 수법 (포장 방식, 자유 선택)
  TACTICS: [""")
c = B[0]

# ================= page =================
PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'fClueKind' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)

# ---- 폼 HTML ----
r("""              <div id="fakeFields" class="mk-stack">
                <div class="field"><label for="fTactic">쓴 수법</label><select id="fTactic"></select><p class="small muted" id="tacticDesc" style="margin:0"></p></div>
                <div class="field"><div class="flabel">단서를 찾는 기준</div><div class="opt-row" id="optClueCrit"></div></div>
                <div class="field"><label for="fClue">숨긴 단서</label><textarea id="fClue" rows="3" placeholder="예: 공식 계정은 @doroland 인데 @dorolandd 로 썼다 / 매출을 386억이 아니라 193억이라고 썼다"></textarea></div>
              </div>""", """              <div id="fakeFields" class="mk-stack">
                <div class="field"><label for="fClueKind">들킬 단서 (다른 조가 확인할 수 있는 것 하나)</label><select id="fClueKind"></select><p class="small muted" id="clueKindHint" style="margin:0"></p></div>
                <div class="field" id="factField" hidden><label for="fFact">어긋나게 쓴 자료실 내용</label><select id="fFact"></select></div>
                <div class="field"><label for="fClue">어떻게 다르게 썼나요?</label><textarea id="fClue" rows="2" placeholder="예: 매출 386억을 193억이라고 썼다 / 막배가 7시 30분인데 밤 9시 불꽃놀이라고 썼다"></textarea></div>
                <div class="field"><label for="fTactic">포장 방식 (선택)</label><select id="fTactic"></select><p class="small muted" id="tacticDesc" style="margin:0"></p></div>
              </div>""")
r("""            <table class="ad-table"><thead><tr><th>조</th><th>가짜 수법</th><th class="num">스토리</th>""",
  """            <table class="ad-table"><thead><tr><th>조</th><th>이번 라운드</th><th class="num">스토리</th>""")
r("""    .make-head {""", """    .returned-note { display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: 12px; background: var(--fake-bg); color: var(--fake); font-size: 14px; font-weight: 700; margin-bottom: 12px; word-break: keep-all; }
    .returned-note .icon { flex: none; margin-top: 2px; } .returned-note span { color: var(--ink); font-weight: 500; }
    .ad-post .clue { margin-top: 4px; padding: 8px 10px; border-radius: 8px; background: var(--surface-2); font-size: 12.5px; line-height: 1.5; word-break: keep-all; }
    .ad-post .clue b { color: var(--fake); } .ad-post.returned { outline: 2px solid var(--fake); }
    .make-head {""")

# ---- 상태·도우미 ----
r("""const teamTactic = t => C.TEAM_TACTICS[((t || 1) - 1) % C.TEAM_TACTICS.length];""",
  """const clueKind = id => (C.CLUE_KINDS || []).find(k => k.id === id) || null;""")
r("""  S.form = { format: first, tactic: teamTactic(S.team), clueCriterion: null, clue: '',""",
  """  S.form = { format: first, tactic: '', clueCriterion: null, clueKind: '', fact: '', clue: '',""")
r("""  const d = S.data, tac = C.TACTICS.find(x => x.id === teamTactic(S.team)) || C.TACTICS[0], mine = myPosts();
  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>${roundIdx(curRound()) + 1}라운드 <b>${ROUND_LABEL[curRound()]} 1개</b> (진짜/가짜 선택)</dd><dt>가짜 수법</dt><dd><b>${esc(tac.id)}</b> (${esc(tac.desc)})</dd><dt>규칙</dt><dd>실존 인물 금지 · 진짜는 자료실대로 · 가짜는 단서 하나 · 형식의 성격에 맞게</dd></dl>`;""",
  """  const d = S.data, mine = myPosts(), ret = mine.find(p => p.status === 'returned' && p.format === curRound());
  $('#missionCard').innerHTML = `<h2>${S.team}조 미션</h2><dl><dt>할 일</dt><dd>${roundIdx(curRound()) + 1}라운드 <b>${ROUND_LABEL[curRound()]} 1개</b> (진짜/가짜 선택)</dd><dt>규칙</dt><dd>진짜는 자료실대로 · 가짜는 자료실로 확인되는 단서 하나 · 실존 인물 금지 · 형식의 성격에 맞게</dd></dl>`;
  $('#makeHead').insertAdjacentHTML('afterend', '');
  const rn = $('#returnedNote'); if (rn) rn.remove();
  if (ret && S.editing !== ret.id) $('#makeHead').insertAdjacentHTML('afterend', `<div class="returned-note" id="returnedNote">${ic('undo-2')}<div>선생님이 돌려보냈어요. 단서를 고쳐서 다시 올려 주세요.${ret.note ? `<br><span>${esc(ret.note)}</span>` : ''}</div><button type="button" class="btn btn-primary" data-act="edit" data-id="${ret.id}" style="margin-left:auto">고치기</button></div>`);""")
r("""  const canMake = S.editing || !mine.some(p => p.format === curRound());""",
  """  const canMake = S.editing || !mine.some(p => p.format === curRound() && p.status !== 'returned');""")
r("""    <div><div class="t">${esc(C.FORMATS[p.format]?.label || '')} · ${esc(p.title || p.body || '(내용 없음)')}</div><div class="a"><span class="muted">${p.secret?.truth === 'real' ? '진짜' : '가짜'}</span>""",
  """    <div><div class="t">${esc(C.FORMATS[p.format]?.label || '')} · ${esc(p.title || p.body || '(내용 없음)')}</div><div class="a"><span class="muted">${p.secret?.truth === 'real' ? '진짜' : '가짜'}${p.status === 'returned' ? ' · <b style="color:var(--fake)">돌려보냄</b>' : ''}</span>""")
# fillForm: clue kind select, fact select, tactic optional
r("""  $('#fTactic').innerHTML = C.TACTICS.map(t => `<option ${t.id === f.tactic ? 'selected' : ''}>${esc(t.id)}</option>`).join('');
  $('#tacticDesc').textContent = (C.TACTICS.find(t => t.id === f.tactic) || {}).desc || '';
  $('#optClueCrit').innerHTML = Object.entries(C.CRITERIA).map(([k, c]) => `<button type="button" class="opt" data-cluecrit="${k}" aria-pressed="${f.clueCriterion === k}">${c.label}</button>`).join('');""",
  """  $('#fTactic').innerHTML = `<option value="" ${f.tactic ? '' : 'selected'}>고르지 않음</option>` + C.TACTICS.map(t => `<option ${t.id === f.tactic ? 'selected' : ''}>${esc(t.id)}</option>`).join('');
  $('#tacticDesc').textContent = (C.TACTICS.find(t => t.id === f.tactic) || {}).desc || '';
  const ck = clueKind(f.clueKind);
  $('#fClueKind').innerHTML = `<option value="" ${ck ? '' : 'selected'}>단서 종류를 고르세요</option>` + C.CLUE_KINDS.map(k => `<option value="${k.id}" ${f.clueKind === k.id ? 'selected' : ''}>[${esc(C.CRITERIA[k.crit].label)}] ${esc(k.label)}</option>`).join('');
  $('#clueKindHint').textContent = ck ? ck.hint : '다른 조가 자료실·계정 정보·본문에서 확인할 수 있는 단서만 됩니다. 자료실에 없는 시간이나 숫자를 바꾸는 건 아무도 못 맞춥니다.';
  $('#factField').hidden = !(ck && ck.fact);
  $('#fFact').innerHTML = '<option value="">자료실 내용을 고르세요</option>' + C.FACTS.map(x => `<option ${f.fact === x ? 'selected' : ''}>${esc(x)}</option>`).join('');""")
r("""  else if (b.dataset.cluecrit) S.form.clueCriterion = b.dataset.cluecrit;
""", "")
r("""$('#fTactic').addEventListener('change', e => { S.form.tactic = e.target.value;""",
  """$('#fClueKind').addEventListener('change', e => { S.form.clueKind = e.target.value; const k = clueKind(e.target.value); S.form.clueCriterion = k ? k.crit : null; if (!(k && k.fact)) S.form.fact = ''; fillForm(); });
$('#fFact').addEventListener('change', e => { S.form.fact = e.target.value; });
$('#fTactic').addEventListener('change', e => { S.form.tactic = e.target.value;""")
r("""  S.form = { format: p.format, tactic: s.tactic || teamTactic(S.team), clueCriterion: s.clueCriterion, clue: s.truth === 'real' ? '' : (s.clue || ''),""",
  """  S.form = { format: p.format, tactic: s.tactic || '', clueCriterion: s.clueCriterion, clueKind: s.clueKind || '', fact: s.fact || '', clue: s.truth === 'real' ? '' : (s.clue || ''),""")
r("""  if (f.truth !== 'real' && (!f.clue.trim() || !f.clueCriterion)) { err.textContent = '가짜 게시물은 숨긴 단서와 그 단서를 찾는 기준을 꼭 적어 주세요.'; return; }""",
  """  if (f.truth !== 'real') { const k = clueKind(f.clueKind), allText = [f.title, f.subhead, f.body, f.quoteText].join('\\n');
    if (!k) { err.textContent = '가짜 게시물은 들킬 단서 종류를 골라 주세요.'; return; }
    if (k.fact && !f.fact) { err.textContent = '어긋나게 쓴 자료실 내용을 골라 주세요.'; return; }
    if (!f.clue.trim()) { err.textContent = '어떻게 다르게 썼는지 한 줄 적어 주세요.'; return; }
    if (k.check === 'hear' && !new RegExp(HEARSAY.source).test(allText)) { err.textContent = '들은 이야기 단서는 본문에 "들었는데", "~래요", "친구가" 같은 말이 있어야 합니다.'; return; }
    if (k.check === 'unreg' && !(f.kind === 'official' || f.kind === 'press')) { err.textContent = '이 단서는 계정 종류를 공식 계정이나 언론사로 두어야 합니다.'; return; }
    if (k.check === 'unreg' && f.handle && A.accounts.some(x => x.handle.replace(/^@/, '').toLowerCase() === f.handle.replace(/^@/, '').toLowerCase())) { err.textContent = '등록된 계정 아이디와 같습니다. 다른 아이디로 써야 합니다.'; return; }
    if (k.check === 'photo' && !(f.postedAt && f.photoTakenAt)) { err.textContent = '올린 때와 찍은 때를 둘 다 적어 주세요.'; return; } }""")
r("""      secret: f.truth === 'real' ? { truth: 'real', tactic: '', clue: f.basis, clueCriterion: 'cross' } : { truth: 'fake', tactic: f.tactic, clue: f.clue, clueCriterion: f.clueCriterion } });""",
  """      secret: f.truth === 'real' ? { truth: 'real', tactic: '', clue: f.basis, clueCriterion: 'cross', clueKind: '', fact: f.basis } : { truth: 'fake', tactic: f.tactic, clue: f.clue, clueCriterion: f.clueCriterion, clueKind: f.clueKind, fact: f.fact } });""")
r("""    toast(S.editing ? '고친 내용을 올렸습니다.' : '올렸습니다. 다른 조에게는 판별 시간부터 보입니다.');""",
  """    toast(S.editing ? '고친 내용을 올렸습니다. 선생님이 다시 봅니다.' : '올렸습니다. 선생님 확인을 거쳐 판별 시간에 다른 조에게 보입니다.');""")

# ---- 운영자 표: 조별 이번 라운드 상태 ----
r("""    return `<tr><td><b>${t}조</b></td><td>${esc(teamTactic(t))}</td><td class="num">${has('story')}</td>""",
  """    const cur = teamPosts.find(p => p.team === t && p.format === d.round), curSt = !cur ? '<span class="muted">아직</span>' : cur.status === 'returned' ? '<b style="color:var(--fake)">돌려보냄</b>' : `<span class="ad-b ${truthOf(cur)}">${truthOf(cur) === 'real' ? '진짜' : '가짜'}</span>`;
    return `<tr><td><b>${t}조</b></td><td>${curSt}</td><td class="num">${has('story')}</td>""")
# ---- 운영자 게시물 행: 단서·사실·돌려보내기 ----
r("""        <div class="t">${esc(p.title || p.body || '')}</div><div class="m">${p.secret?.clue ? '단서: ' + esc(p.secret.clue) + ' · ' : ''}판별 진짜 ${c.real} · 가짜 ${c.fake}</div></div>
      <div><button class="btn btn-ghost" data-addel="${p.id}" style="color:var(--fake)">삭제</button></div></div>`; };""",
  """        <div class="t">${esc(p.title || p.body || '')}</div>${clueBox(p)}<div class="m">판별 진짜 ${c.real} · 가짜 ${c.fake}${p.status === 'returned' ? ` · <b style="color:var(--fake)">돌려보냄</b>${p.note ? ': ' + esc(p.note) : ''}` : ''}</div></div>
      <div style="display:grid;gap:6px">${p.seed || p.status === 'returned' ? '' : `<button class="btn btn-ghost" data-adreturn="${p.id}">돌려보내기</button>`}<button class="btn btn-ghost" data-addel="${p.id}" style="color:var(--fake)">삭제</button></div></div>`; };""")
r("""    return `<div class="ad-post${p.status === 'hidden' ? ' hidden' : ''}">""", """    return `<div class="ad-post${p.status === 'hidden' ? ' hidden' : ''}${p.status === 'returned' ? ' returned' : ''}">""")
r("""async function adRefresh() {""", """/* 선생님 검토용: 이 글이 어디서 들통나는지 한눈에 */
function clueBox(p) {
  const s = p.secret || {}; if (p.seed) return '';
  if (s.truth === 'real') return `<div class="clue">진짜 · 근거: ${esc(s.clue || s.fact || '-')}</div>`;
  const k = clueKind(s.clueKind), cr = s.clueCriterion ? C.CRITERIA[s.clueCriterion] : null;
  return `<div class="clue"><b>${cr ? esc(cr.label) : '기준 없음'}</b>${k ? ' · ' + esc(k.label) : ''}${s.fact ? `<br>어긋난 자료실 내용: ${esc(s.fact)}` : ''}<br>설명: ${esc(s.clue || '-')}${s.tactic ? ` · 포장: ${esc(s.tactic)}` : ''}${!k && s.truth === 'fake' ? '<br><b>확인할 수 없는 단서일 수 있음. 내용을 보고 돌려보낼지 정하세요.</b>' : ''}</div>`;
}
async function adRefresh() {""")
r("""  const ph = e.target.closest('[data-adphase]'), tg = e.target.closest('[data-adtoggle]'), tc = e.target.closest('[data-adteams]'), dl = e.target.closest('[data-addel]');""",
  """  const rb = e.target.closest('[data-adreturn]');
  if (rb) { const note = prompt('그 조에 보일 한 줄 (예: 바꾼 시간이 자료실에 없어요. 막배 시간처럼 자료실에 있는 걸로 바꿔 주세요)', ''); if (note === null) return;
    try { await adApi('/admin/moderate', { postId: rb.dataset.adreturn, action: 'return', note }); toast('돌려보냈습니다.'); await adRefresh(); } catch (x) { toast(x.message); } return; }
  const ph = e.target.closest('[data-adphase]'), tg = e.target.closest('[data-adtoggle]'), tc = e.target.closest('[data-adteams]'), dl = e.target.closest('[data-addel]');""")

# ---- 진행 막대: 돌려보낸 조, 다음 단계 확인 문구 ----
r("""  else if (d.phase === 'make') prog = `<span>올린 조 ${pr.submitted.length} / ${n}</span>` + teams.map(t => `<i class="tm${pr.submitted.includes(t) ? ' on' : ''}">${t}</i>`).join('');""",
  """  else if (d.phase === 'make') { const ret = pr.returned || []; prog = `<span>올린 조 ${pr.submitted.length} / ${n}${ret.length ? ` · 돌려보냄 ${ret.length}` : ''}</span>` + teams.map(t => `<i class="tm${ret.includes(t) ? ' ret' : pr.submitted.includes(t) ? ' on' : ''}" title="${ret.includes(t) ? '돌려보냄' : pr.submitted.includes(t) ? '올림' : '아직'}">${t}</i>`).join(''); }""")
r("""    .opbar .tm.part {""", """    .opbar .tm.ret { background: var(--fake); color: #fff; }
    .opbar .tm.part {""")
r("""  if (!confirm(`모든 노트북이 「${stepName(phase, round)}」 화면으로 바뀝니다. 넘길까요?`)) return;""",
  """  let warn = '';
  if (phase === 'judge' && S.data && S.data.progress) { const pr = S.data.progress, n = S.data.teamCount, miss = n - pr.submitted.length, ret = (pr.returned || []).length;
    if (miss || ret) warn = `\\n\\n아직 안 올린 조 ${miss}${ret ? `, 돌려보낸 글 ${ret}` : ''}. 지금 넘기면 그 조는 이번 라운드 글 없이 판별만 합니다.`; }
  if (!confirm(`모든 노트북이 「${stepName(phase, round)}」 화면으로 바뀝니다.${warn}\\n넘길까요?`)) return;""")

# ---- 판별 중엔 자료 대조 패널 기본 펼침 ----
r("""  const open = S.open[p.id], own = !!p.mine, a = p.author || {}, f = C.FORMATS[p.format] || {};""",
  """  const open = S.open[p.id] === undefined && canJudge(p) && !S.data.myJudgments[p.id] ? 'cross' : S.open[p.id], own = !!p.mine, a = p.author || {}, f = C.FORMATS[p.format] || {};""")

# ---- 자기 글 상태 줄: 돌려보냄 ----
r("""  if (!p.mine || revealed(p)) return '';
  const s = p.secret || {};""", """  if (!p.mine || revealed(p)) return '';
  const s = p.secret || {};
  if (p.status === 'returned') return `<div class="status-line st-pending">${ic('undo-2')}선생님이 돌려보냄${p.note ? ' · ' + esc(p.note) : ''}</div>`;""")

h = B[0]
for path, text, crlf in ((SP, s, s_crlf), (CP, c, c_crlf), (PP, h, h_crlf)):
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n') if crlf else text)
print('ok')
