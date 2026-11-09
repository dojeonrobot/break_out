# 2026-11-09 밤: 관리자는 학생과 같은 화면 + 추가 기능 (사용자). 진행 막대는 항상 위에 고정.
#  - 홈 머리글·타일 문구·힌트를 관리자도 학생과 같게. 다음 라운드 타일은 잠긴 모양 그대로지만 관리자는 눌러서 미리 볼 수 있음(「관리자 미리 보기」).
#  - 필터는 학생 칩 + 「예시」「조 게시물」 칩 추가.
#  - .opbar position: sticky.
import io, sys
PP = r'C:\Users\dlgus\break_out\chapter05\feed.html'
h = io.open(PP, encoding='utf-8', newline='').read(); crlf = '\r\n' in h; h = h.replace('\r\n', '\n')
if 'adm-peek' in h:
    sys.exit('이미 적용됨')
B = [h]
def r(old, new, cnt=1):
    n = B[0].count(old)
    if n != cnt: sys.exit(f'{n}≠{cnt}: {old[:110]}')
    B[0] = B[0].replace(old, new)

r("""    .opbar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin: 0 16px 18px; padding: 14px 16px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); }""",
  """    .opbar { position: sticky; top: 8px; z-index: 30; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin: 0 16px 18px; padding: 14px 16px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); box-shadow: rgba(0,0,0,.04) 0 2px 6px, rgba(0,0,0,.08) 0 6px 16px; }
    @media (max-width: 1023px) { .opbar { top: 58px; } }
    #tab-feed:has(#rounds:not([hidden])) .opbar { align-self: start; }
    .round-tile.adm-peek { cursor: pointer; } .round-tile.adm-peek .rt-photo { filter: grayscale(1) brightness(.55); }
    .round-tile.adm-peek .rt-cta { background: rgba(255,255,255,.18); color: #fff; border: 1px solid rgba(255,255,255,.35); }""")

r("""  if (isAdmin() || S.screen) { box.hidden = true; return; }""", """  if (S.screen) { box.hidden = true; return; }""")

r("""    const now = i === cur, past = i < cur, open = now || past || adm, all = (S.data.posts || []).filter(p => p.format === f && p.status === 'approved');
    const n = all.filter(p => !p.seed).length;
    const st = adm ? (now ? STEP_LABEL[S.data.phase] + ' 중 · ' : '') + `예시 ${all.length - n} · 조 게시물 ${n}`
      : now ? `지금 진행 중 · ${STEP_LABEL[S.data.phase]}` : past ? `끝난 라운드 · 게시물 ${n}개` : `${i}라운드가 끝나면 열려요`;""",
  """    const now = i === cur, past = i < cur, open = now || past, peek = adm && !open, all = (S.data.posts || []).filter(p => p.format === f && p.status === 'approved');
    const n = all.filter(p => !p.seed).length;""")
r("""    const cta = adm ? '전체 보기' : now ? { read: '예시 보기', make: '우리 조 만들기', judge: '판별하기', reveal: '정답 보기' }[S.data.phase] : past ? '다시 보기' : '';
    const state = adm ? st : now ? `<i class="dot"></i>${STEP_LABEL[S.data.phase]} 중` : past ? `${ic('check')}끝남 · 게시물 ${n}개` : '';
    return `<button type="button" class="round-tile${now ? ' now' : past ? ' past' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">""",
  """    const cta = now ? { read: '예시 보기', make: adm ? '조 게시물 보기' : '우리 조 만들기', judge: adm ? '게시물 보기' : '판별하기', reveal: '정답 보기' }[S.data.phase] : past ? '다시 보기' : peek ? '관리자 미리 보기' : '';
    const state = now ? `<i class="dot"></i>${STEP_LABEL[S.data.phase]} 중` : past ? `${ic('check')}끝남 · 게시물 ${n}개` : '';
    return `<button type="button" class="round-tile${now ? ' now' : past ? ' past' : peek ? ' adm-peek' : ''}" data-round="${f}" ${open || peek ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">""")
r("""      ${open ? '' : `<span class="rt-lock">${ic('lock')}</span>`}
      <span class="rt-body"><b>${ROUND_LABEL[f]}</b><small>${open ? sub : `${i}라운드가 끝나면 열려요`}</small>""",
  """      ${open ? '' : `<span class="rt-lock">${ic('lock')}</span>`}
      <span class="rt-body"><b>${ROUND_LABEL[f]}</b><small>${open ? sub : `${i}라운드가 끝나면 열려요`}</small>""")

# 힌트는 관리자도 학생 문구로(조 없는 경우 문구), 필터는 학생 칩 + 관리자 칩
r("""  const hint = adm || !now ? '' : d.phase === 'read'""", """  const hint = !now ? '' : d.phase === 'read'""")
r("""  const d = S.data, adm = isAdmin(), now = S.fmt === curRound(), chips = [['all', '전체']];
  if (adm) chips.push(['seed', '예시'], ['team', '조 게시물']);
  else {
    if (now && d.phase === 'judge') chips.push(['todo', '아직 판별 안 함']);
    if (d.posts.some(p => p.mine && p.format === S.fmt)) chips.push(['mine', '우리 조가 만든 것']);
  }""", """  const d = S.data, adm = isAdmin(), now = S.fmt === curRound(), chips = [['all', '전체']];
  if (!adm && now && d.phase === 'judge') chips.push(['todo', '아직 판별 안 함']);
  if (d.posts.some(p => p.mine && p.format === S.fmt)) chips.push(['mine', '우리 조가 만든 것']);
  if (adm) chips.push(['seed', '예시'], ['team', '조 게시물']);""")
h = B[0]
io.open(PP, 'w', encoding='utf-8', newline='').write(h.replace('\n', '\r\n') if crlf else h); print('ok')
