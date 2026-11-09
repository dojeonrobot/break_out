# 2026-11-09 도로그램 첫 화면: 단계 표시·자료실 안내·예제 게시물 제거, 들어오면 조 선택 창부터. 한 번만 적용.
import io, sys
p = r'C:\Users\dlgus\break_out\chapter05\feed.html'
h = io.open(p, encoding='utf-8', newline='').read()
crlf = '\r\n' in h
h = h.replace('\r\n', '\n')


def r(old, new):
    global h
    n = h.count(old)
    if n != 1:
        sys.exit(f'{n}: {old[:70]}')
    h = h.replace(old, new)


r('    <div class="sb-phase"><span>지금 단계</span><b id="sbPhase">연결 중</b><p id="sbPhaseDesc"></p></div>\n', '')
r('      <span class="phase-pill" id="phasePill">연결 중</span>\n', '')
r('    <div class="phase-line"><b id="phaseTitle">불러오는 중</b><span class="muted small" id="phaseDesc"></span></div>\n\n', '')
r('      <div class="read-hint" id="readHint" hidden><i data-lucide="library-big" class="icon"></i><span>도로랜드를 잘 모르면 판별할 수 없습니다. 먼저 <b>자료실</b>(도로랜드 정리본)을 읽고 오세요.</span><button class="btn btn-primary" type="button" data-goto="archive">자료실 열기</button></div>\n', '')
r('        <button class="chip" data-filter="seed" aria-pressed="false" hidden>예제 자료</button>\n', '')
r("  es.onerror = () => { $('#phasePill').textContent = '다시 연결 중'; };\n", "")
r("    if (phaseChanged) { toast(C.PHASES[d.phase].label + ' 단계가 시작됐습니다.'); if (d.phase === 'judge' && S.tab !== 'admin') showTab('feed'); }",
  "    if (phaseChanged && d.phase === 'judge' && S.tab !== 'admin') showTab('feed');")
r("    $('#phasePill').textContent = '서버 연결 안 됨';\n", "")
r("""  const d = S.data, ph = C.PHASES[d.phase];
  $('#phasePill').textContent = ph.label; $('#phaseTitle').textContent = ph.label; $('#phaseDesc').textContent = ph.desc;
  $('#sbPhase').textContent = ph.label; $('#sbPhaseDesc').textContent = ph.desc;
""", "  const d = S.data;\n")
r("""  $('[data-filter="seed"]').hidden = !['judge', 'reveal'].includes(d.phase);
  $('#readHint').hidden = d.phase !== 'read' || load('dorogram-archive-seen') === '1';
""", "")
r("""  if (t === 'archive') { renderArchive(); store('dorogram-archive-seen', '1'); $('#readHint').hidden = true; }""",
  """  if (t === 'archive') renderArchive();""")
r("""  let posts = d.posts.filter(p => p.status === 'approved');
  if (S.filter === 'seed') posts = posts.filter(p => p.seed);
  else if (S.filter === 'mine')""", """  let posts = d.posts.filter(p => p.status === 'approved' && !p.seed);   /* 예제는 학생 화면에 띄우지 않음 (2026-11-09 사용자) */
  if (S.filter === 'mine')""")
r("""    posts = posts.filter(p => late ? (!p.seed || p.mine) : true);
""", "")
r("""  $('#feedCnt').textContent = `${d.phase === 'read' ? '예제' : late ? '판별할 게시물' : '게시물'} ${posts.length}개`;""",
  """  $('#feedCnt').textContent = `${late ? '판별할 게시물' : '게시물'} ${posts.length}개`;""")
r("""  let n = 10;
  try { const d = await api('/state'); n = d.teamCount || 10; } catch (e) {}
  renderTeamGrid(n);
  const q = new URLSearchParams(location.search);
  const saved = q.get('view') === 'screen' ? '0' : (q.get('team') || load('dorogram-team'));
  if (saved !== null && saved !== '' && +saved >= 0 && +saved <= n) setTeam(+saved, true);
  else { $('#teamModal').hidden = false; refresh(); }""",
"""  const q = new URLSearchParams(location.search);
  const fixed = q.get('view') === 'screen' ? '0' : q.get('team');   /* 주소에 조가 박혀 있을 때만 건너뜀 */
  renderTeamGrid(10);
  if (fixed === null || fixed === '') $('#teamModal').hidden = false;   /* 들어오면 먼저 조부터 고름 (2026-11-09 사용자) */
  let n = 10;
  try { const d = await api('/state'); n = d.teamCount || 10; } catch (e) {}
  renderTeamGrid(n);
  if (fixed !== null && fixed !== '' && +fixed >= 0 && +fixed <= n) setTeam(+fixed, true);
  else { $('#teamModal').hidden = false; refresh(); }""")
if crlf:
    h = h.replace('\n', '\r\n')
io.open(p, 'w', encoding='utf-8', newline='').write(h)
print('ok')
