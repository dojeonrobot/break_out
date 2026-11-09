# 2026-11-09 도로그램 룩 개편 (사용자: "진짜 SNS 앱 느낌", 콘셉트 유지).
#  A. 라운드 선택 타일: 형식마다 실제 앱 모양(기사 지면 / 세로 쇼츠 / 스토리 링)이 보이는 큰 카드, 진행 상태 점
#  B. 상세 창 오른쪽: 확인하기 아이콘 바, 판정 세그먼트, 해설은 문장 단위 목록 + 들통나는 곳·수법 카드 + 수치 타일
# 한 번만 적용.
import io, sys
PP = r'C:\Users\dlgus\break_out\chapter05\feed.html'
h = io.open(PP, encoding='utf-8', newline='').read()
crlf = '\r\n' in h
h = h.replace('\r\n', '\n')
if 'rt-art' in h:
    sys.exit('이미 적용됨')
B = [h]


def r(old, new, cnt=1):
    n = B[0].count(old)
    if n != cnt:
        sys.exit(f'{n}≠{cnt}: {old[:100]}')
    B[0] = B[0].replace(old, new)


# ---------- A. 라운드 타일 CSS ----------
r("""    .round-tile { display: grid; gap: 14px; justify-items: start; text-align: left; padding: 22px 20px; min-height: 196px; border-radius: 16px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; cursor: pointer; transition: transform .15s ease, box-shadow .15s ease; }
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
    @media (prefers-reduced-motion: reduce) { .round-tile { transition: none; } .round-tile:hover, .round-tile:active { transform: none; } }""",
"""    .rounds { max-width: 1120px; gap: 20px; }
    .round-tile { position: relative; display: grid; grid-template-rows: 190px auto; text-align: left; padding: 0; border-radius: 22px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; cursor: pointer; overflow: hidden; box-shadow: 0 1px 2px color-mix(in srgb, #262626 6%, transparent); transition: transform .22s cubic-bezier(.16,1,.3,1), box-shadow .22s; }
    .round-tile:not(:disabled):hover { transform: translateY(-4px); box-shadow: 0 16px 36px color-mix(in srgb, #262626 14%, transparent); }
    .round-tile:not(:disabled):active { transform: translateY(0) scale(.99); }
    .round-tile:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
    .round-tile:disabled { cursor: not-allowed; }
    .round-tile:disabled .rt-art { filter: grayscale(1); opacity: .45; }
    .round-tile:disabled .rt-body b, .round-tile:disabled .rt-body small { color: var(--muted); }
    .round-tile.now { border-color: transparent; box-shadow: 0 0 0 2px var(--blue), 0 14px 34px color-mix(in srgb, var(--blue) 22%, transparent); }
    .rt-num { position: absolute; top: 14px; left: 14px; z-index: 2; font-size: 12px; font-weight: 800; letter-spacing: .02em; padding: 5px 10px; border-radius: 999px; background: rgba(255,255,255,.92); color: #262626; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
    .rt-lock { position: absolute; inset: 0 0 auto; height: 190px; z-index: 2; display: grid; place-items: center; color: #fff; }
    .rt-lock span { display: grid; place-items: center; width: 54px; height: 54px; border-radius: 50%; background: rgba(38,38,38,.75); backdrop-filter: blur(4px); }
    .rt-lock .icon { width: 24px; height: 24px; }
    .rt-art { position: relative; overflow: hidden; }
    .rt-body { display: grid; gap: 4px; padding: 16px 18px 18px; }
    .rt-body b { font-size: 24px; line-height: 1.2; letter-spacing: -0.01em; }
    .rt-body small { font-size: 13px; font-weight: 700; color: var(--muted); }
    .rt-st { display: inline-flex; align-items: center; gap: 7px; margin-top: 8px; font-size: 13px; font-weight: 700; color: var(--muted); }
    .rt-st .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--line); flex: none; }
    .round-tile.now .rt-st { color: var(--blue); } .round-tile.now .rt-st .dot { background: var(--blue); box-shadow: 0 0 0 0 color-mix(in srgb, var(--blue) 50%, transparent); animation: rtPulse 1.6s ease-out infinite; }
    .round-tile.past .rt-st { color: var(--real); } .round-tile.past .rt-st .dot { background: var(--real); }
    @keyframes rtPulse { to { box-shadow: 0 0 0 9px transparent; } }
    @media (prefers-reduced-motion: reduce) { .round-tile { transition: none; } .round-tile:hover, .round-tile:active { transform: none; } .round-tile.now .rt-st .dot { animation: none; } }
    /* 기사 지면 */
    .art-news { background: linear-gradient(180deg, #fff 0, #f3f4f6 100%); padding: 44px 22px 0; display: grid; gap: 9px; align-content: start; }
    .art-news .mh { height: 10px; width: 34%; border-radius: 3px; background: #d62976; }
    .art-news .hl { height: 15px; border-radius: 4px; background: #262626; } .art-news .hl.s { width: 72%; }
    .art-news .ph { margin-top: 4px; height: 84px; border-radius: 10px; background: linear-gradient(135deg, #0f766e, #134e4a 60%, #1e293b); position: relative; }
    .art-news .ph::after { content: ""; position: absolute; left: 10px; bottom: 10px; width: 46%; height: 8px; border-radius: 3px; background: rgba(255,255,255,.75); }
    .art-news .ln { height: 7px; border-radius: 3px; background: #c9ced6; } .art-news .ln.s { width: 60%; }
    /* 세로 쇼츠 */
    .art-shorts { background: #0f0f0f; display: grid; place-items: center; }
    .art-shorts .phone { width: 104px; height: 100%; margin-top: 30px; border-radius: 16px 16px 0 0; background: linear-gradient(160deg, #4f5bd5, #962fbf 45%, #d62976 80%, #fa7e1e); position: relative; box-shadow: 0 0 0 5px #262626, 0 18px 40px rgba(0,0,0,.6); }
    .art-shorts .phone::before { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, transparent 50%, rgba(0,0,0,.65)); border-radius: inherit; }
    .art-shorts .play { position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%); width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,.92); display: grid; place-items: center; color: #111; } .art-shorts .play .icon { width: 18px; height: 18px; margin-left: 2px; }
    .art-shorts .cap { position: absolute; left: 12px; right: 36px; bottom: 26px; height: 8px; border-radius: 3px; background: rgba(255,255,255,.9); } .art-shorts .cap.s { bottom: 12px; right: 56px; opacity: .6; }
    .art-shorts .acts { position: absolute; right: 8px; bottom: 10px; display: grid; gap: 7px; } .art-shorts .acts i { display: block; width: 14px; height: 14px; border-radius: 50%; background: rgba(255,255,255,.85); }
    /* 스토리 링 */
    .art-story { background: linear-gradient(180deg, #fff, #fafafa); display: flex; align-items: center; justify-content: center; gap: 14px; padding-top: 22px; }
    .art-story .ring { width: 62px; height: 62px; border-radius: 50%; padding: 3px; background: var(--ig-grad); }
    .art-story .ring span { display: block; width: 100%; height: 100%; border-radius: 50%; border: 3px solid #fff; background: var(--c, #0f766e); }
    .art-story .ring:nth-child(2) { width: 78px; height: 78px; } .art-story .ring.seen { background: #dbdbdb; }
    @media (prefers-color-scheme: dark) { .art-news { background: linear-gradient(180deg, #1a1a1a, #111); } .art-news .hl { background: #f5f5f5; } .art-news .ln { background: #3a3a3a; } .art-story { background: #111; } .art-story .ring span { border-color: #111; } .rt-num { background: rgba(38,38,38,.9); color: #f5f5f5; } }""")

# ---------- A. 라운드 타일 markup ----------
r("""    return `<button type="button" class="round-tile${now ? ' now' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">
      <span class="rt-ic">${ic(open ? ROUND_ICON[f] : 'lock')}</span><span><small>${i + 1}라운드</small><b>${ROUND_LABEL[f]}</b></span><span class="rt-st">${st}</span></button>`;""",
"""    const art = f === 'news' ? `<div class="rt-art art-news"><i class="mh"></i><i class="hl"></i><i class="hl s"></i><i class="ph"></i><i class="ln"></i><i class="ln s"></i></div>`
      : f === 'shorts' ? `<div class="rt-art art-shorts"><div class="phone"><span class="play">${ic('play')}</span><i class="cap"></i><i class="cap s"></i><span class="acts"><i></i><i></i><i></i></span></div></div>`
      : `<div class="rt-art art-story"><span class="ring" style="--c:#0f766e"><span></span></span><span class="ring" style="--c:#d62976"><span></span></span><span class="ring seen" style="--c:#4b5563"><span></span></span></div>`;
    const sub = { news: '언론사가 기자 이름을 걸고 쓰는 기사', shorts: '60초 세로 영상, 썸네일과 자막', story: '24시간 뒤 사라지는 한 장 + 한 줄' }[f];
    return `<button type="button" class="round-tile${now ? ' now' : past ? ' past' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">
      <span class="rt-num">${i + 1}라운드</span>${art}${open ? '' : `<span class="rt-lock"><span>${ic('lock')}</span></span>`}
      <span class="rt-body"><b>${ROUND_LABEL[f]}</b><small>${sub}</small><span class="rt-st"><i class="dot"></i>${st}</span></span></button>`;""")
r("""    const st = adm ? (now ? STEP_LABEL[S.data.phase] + ' 중' : '') + `${now ? ' · ' : ''}예시 ${all.length - n} · 조 게시물 ${n}`
      : now ? '지금 라운드' : past ? `끝난 라운드 · 게시물 ${n}개` : '앞 라운드가 끝나면 열립니다';""",
"""    const st = adm ? (now ? STEP_LABEL[S.data.phase] + ' 중 · ' : '') + `예시 ${all.length - n} · 조 게시물 ${n}`
      : now ? `지금 진행 중 · ${STEP_LABEL[S.data.phase]}` : past ? `끝난 라운드 · 게시물 ${n}개` : `${i}라운드가 끝나면 열려요`;""")

# ---------- B. 상세 창 오른쪽 CSS ----------
r("""    .side-h { display: flex; align-items: center; gap: 8px; padding: 14px 14px 4px; font-weight: 800; font-size: 15px; } .side-h .icon { width: 18px; height: 18px; }""",
"""    .post-side { font-size: 15px; line-height: 1.55; }
    .side-h { display: flex; align-items: center; gap: 8px; padding: 16px 16px 6px; font-weight: 800; font-size: 13px; letter-spacing: .02em; color: var(--muted); text-transform: uppercase; } .side-h .icon { width: 16px; height: 16px; }""")
r("""    .verify { padding: 10px 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
    .vbtn { border: 1px solid var(--line); background: var(--surface-2); border-radius: 8px; padding: 7px 6px; font-size: 13px; font-weight: 600; display: flex; gap: 5px; align-items: center; justify-content: center; white-space: nowrap; }
    .vbtn[aria-expanded="true"] { background: var(--navy); color: var(--navy-ink); border-color: var(--navy); } .vbtn .icon { width: 15px; height: 15px; }
    .vpanel { margin: 0 12px 12px; padding: 12px 14px; background: var(--surface-2); border-radius: 8px; font-size: 14px; }""",
"""    .verify { padding: 4px 10px 12px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
    .vbtn { border: 0; background: transparent; border-radius: 12px; padding: 10px 4px 8px; font-size: 12px; font-weight: 700; display: grid; justify-items: center; gap: 6px; color: var(--ink); min-height: 64px; }
    .vbtn .icon { width: 24px; height: 24px; stroke-width: 1.75; }
    .vbtn:hover { background: var(--surface-2); }
    .vbtn[aria-expanded="true"] { background: var(--ink); color: var(--surface); }
    .vpanel { margin: 0 12px 12px; padding: 14px 16px; background: var(--surface-2); border-radius: 14px; font-size: 14px; }""")
r("""    .judge { border-top: 1px solid var(--line); padding: 12px; display: grid; gap: 10px; }
    .judge-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .vd { flex: 1; min-width: 88px; border: 1px solid var(--line); background: var(--surface); border-radius: 8px; padding: 8px 10px; font-weight: 700; }
    .vd[data-v="real"][aria-pressed="true"] { background: var(--real-bg); border-color: var(--real); color: var(--real); } .vd[data-v="fake"][aria-pressed="true"] { background: var(--fake-bg); border-color: var(--fake); color: var(--fake); } .vd[data-v="unsure"][aria-pressed="true"] { background: var(--unsure-bg); border-color: var(--unsure); }
    .crit { border: 0; background: var(--surface-2); border-radius: 999px; padding: 5px 12px; font-size: 13px; font-weight: 700; } .crit[aria-pressed="true"] { background: var(--navy); color: var(--navy-ink); }""",
"""    .judge { border-top: 1px solid var(--line); padding: 14px 16px 16px; display: grid; gap: 12px; }
    .judge-q { font-size: 16px; font-weight: 800; margin: 0; }
    .judge-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .judge-row.seg { gap: 0; padding: 4px; border-radius: 14px; background: var(--surface-2); }
    .vd { flex: 1; min-width: 0; border: 0; background: transparent; border-radius: 11px; padding: 11px 6px; font-weight: 800; font-size: 15px; display: grid; justify-items: center; gap: 4px; color: var(--muted); }
    .vd .icon { width: 22px; height: 22px; }
    .vd[aria-pressed="true"] { background: var(--surface); box-shadow: 0 1px 4px rgba(0,0,0,.12); }
    .vd[data-v="real"][aria-pressed="true"] { color: var(--real); } .vd[data-v="fake"][aria-pressed="true"] { color: var(--fake); } .vd[data-v="unsure"][aria-pressed="true"] { color: var(--ink); }
    .crit { border: 1px solid var(--line); background: var(--surface); border-radius: 999px; padding: 7px 13px; font-size: 13px; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; min-height: 36px; } .crit .icon { width: 15px; height: 15px; }
    .crit[aria-pressed="true"] { background: var(--ink); color: var(--surface); border-color: var(--ink); }
    .judge .btn-primary { width: 100%; min-height: 44px; font-size: 15px; border-radius: 10px; }""")
r("""    .answer { border-top: 1px solid var(--line); padding: 12px 16px; display: grid; gap: 6px; font-size: 14px; } .answer.real { background: var(--real-bg); } .answer.fake { background: var(--fake-bg); }
    .answer .big { font-size: 16px; font-weight: 800; }
    .counts { display: flex; gap: 12px; font-size: 13px; color: var(--muted); }""",
"""    .answer { border-top: 1px solid var(--line); display: grid; }
    .ans-head { display: flex; align-items: center; gap: 12px; padding: 16px; color: #fff; }
    .answer.real .ans-head { background: var(--real); } .answer.fake .ans-head { background: var(--fake); }
    .ans-head .mark { display: grid; place-items: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(255,255,255,.22); flex: none; } .ans-head .mark .icon { width: 24px; height: 24px; stroke-width: 2.5; }
    .ans-head b { display: block; font-size: 20px; line-height: 1.15; } .ans-head span { font-size: 13px; opacity: .9; }
    .ans-body { padding: 14px 16px 16px; display: grid; gap: 14px; }
    .ans-lead { margin: 0; font-size: 15px; font-weight: 800; line-height: 1.5; word-break: keep-all; }
    .ans-list { margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; }
    .ans-list li { display: grid; grid-template-columns: 22px 1fr; gap: 9px; font-size: 14.5px; line-height: 1.55; word-break: keep-all; }
    .ans-list li .icon { width: 20px; height: 20px; margin-top: 2px; } .answer.fake .ans-list .icon { color: var(--fake); } .answer.real .ans-list .icon { color: var(--real); }
    .ans-cards { display: grid; gap: 8px; }
    .ans-card { display: grid; grid-template-columns: 36px 1fr; gap: 10px; padding: 12px; border-radius: 12px; background: var(--surface-2); }
    .ans-card .ic { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 10px; background: var(--surface); } .ans-card .ic .icon { width: 18px; height: 18px; }
    .ans-card small { display: block; font-size: 11.5px; font-weight: 800; letter-spacing: .03em; color: var(--muted); }
    .ans-card b { display: block; font-size: 15px; margin: 1px 0 3px; }
    .ans-card p { margin: 0; font-size: 13px; line-height: 1.5; color: var(--muted); word-break: keep-all; }
    .counts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .counts span { display: grid; gap: 2px; padding: 10px 8px; border-radius: 12px; background: var(--surface-2); text-align: center; font-size: 12px; font-weight: 700; color: var(--muted); }
    .counts span b { font-size: 22px; line-height: 1; font-weight: 900; color: var(--ink); font-variant-numeric: tabular-nums; }
    .counts span.real b { color: var(--real); } .counts span.fake b { color: var(--fake); }""")
r("""    .side-who { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-bottom: 1px solid var(--line); font-size: 13px; }""",
  """    .side-who { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-bottom: 1px solid var(--line); font-size: 13px; }
    .side-who .avatar { width: 40px; height: 40px; font-size: 16px; }""")

# ---------- B. 상세 창 markup ----------
r("""  const vbtn = (v, l) => `<button type="button" class="vd" data-act="verdict" data-id="${p.id}" data-v="${v}" aria-pressed="${dft.verdict === v}">${l}</button>`;
  const crits = Object.entries(C.CRITERIA).map(([k, c]) => `<button type="button" class="crit" data-act="crit" data-id="${p.id}" data-c="${k}" aria-pressed="${dft.criterion === k}">${c.label}</button>`).join('');
  return `<div class="judge">${mine ? `<div class="done-judge"><span class="muted">우리 조 판정</span>${verdictBadge(mine.verdict)}</div>` : ''}
    <div class="judge-row">${vbtn('real', '진짜')}${vbtn('fake', '가짜')}${vbtn('unsure', '모르겠음')}</div>
    <div class="flabel">어떤 기준으로 판단했나요?</div><div class="judge-row">${crits}</div>""",
"""  const vbtn = (v, l, i) => `<button type="button" class="vd" data-act="verdict" data-id="${p.id}" data-v="${v}" aria-pressed="${dft.verdict === v}">${ic(i)}${l}</button>`;
  const crits = Object.entries(C.CRITERIA).map(([k, c]) => `<button type="button" class="crit" data-act="crit" data-id="${p.id}" data-c="${k}" aria-pressed="${dft.criterion === k}">${ic(c.icon)}${c.label}</button>`).join('');
  return `<div class="judge">${mine ? `<div class="done-judge"><span class="muted">우리 조 판정</span>${verdictBadge(mine.verdict)}</div>` : `<p class="judge-q">${p.seed ? '이 글, 진짜일까요?' : '이 게시물은?'}</p>`}
    <div class="judge-row seg">${vbtn('real', '진짜', 'circle-check')}${vbtn('fake', '가짜', 'circle-x')}${vbtn('unsure', '모르겠음', 'circle-help')}</div>
    <div class="flabel">어디서 알아챘나요?</div><div class="judge-row">${crits}</div>""")
r("""function answerHTML(p) {
  const mine = S.data.myJudgments[p.id];
  const result = t => mine ? `<div class="big">${mine.verdict === t ? '맞혔습니다!' : mine.verdict === 'unsure' ? '모르겠음으로 넘겼습니다' : '틀렸습니다'}</div>` : '';
  if (p.seed && p.answer) { const a = p.answer, cr = C.CRITERIA[a.criterion], tc = C.TACTICS.find(x => x.id === a.tactic);
    const meta = (cr ? `<div><b>${a.truth === 'fake' ? '들통나는 곳' : '진짜인 근거'}</b> ${esc(cr.label)}: ${esc(cr.hint)}</div>` : '') + (tc ? `<div><b>쓴 수법</b> ${esc(tc.id)}: ${esc(tc.desc)}</div>` : '');
    return `<div class="answer ${a.truth}">${result(a.truth)}<div>${verdictBadge(a.truth)} <b>해설</b></div><div>${esc(a.explain)}</div>${meta ? `<div class="ans-meta">${meta}</div>` : ''}${p.counts ? countsHTML(p.counts) : ''}</div>`; }
  if (revealed(p) && p.secret) { const s = p.secret; return `<div class="answer ${s.truth}">${result(s.truth)}<div>${verdictBadge(s.truth)} <b>${p.team}조가 만든 ${s.truth === 'fake' ? '가짜' : '진짜'}</b></div>
      ${s.tactic ? `<div><b>쓴 수법</b> ${esc(s.tactic)}</div>` : ''}${s.clue ? `<div><b>${s.truth === 'real' ? '근거가 된 자료실 내용' : '숨긴 단서'}</b>${s.truth !== 'real' && s.clueCriterion ? ` (${C.CRITERIA[s.clueCriterion].label})` : ''} ${esc(s.clue)}</div>` : ''}${p.counts ? countsHTML(p.counts) : ''}</div>`; }
  return '';
}
const countsHTML = c => `<div class="counts"><span>진짜라고 한 조 ${c.real}</span><span>가짜라고 한 조 ${c.fake}</span><span>모르겠음 ${c.unsure}</span></div>`;""",
"""/* 해설: 긴 글을 문장 단위로 쪼개 목록으로. 첫 문장("가짜입니다." 같은 판정)은 머리띠가 대신하므로 뺀다 */
const sentences = t => String(t || '').replace(/\\s+/g, ' ').split(/(?<=[.!?])\\s+(?=[^\\s])/).map(s => s.trim()).filter(Boolean);
function answerHTML(p) {
  const mine = S.data.myJudgments[p.id];
  const head = (truth, who) => { const hit = mine ? (mine.verdict === truth ? '맞혔어요!' : mine.verdict === 'unsure' ? '모르겠음으로 넘겼어요' : '틀렸어요') : '';
    return `<div class="ans-head"><span class="mark">${ic(truth === 'fake' ? 'x' : 'check')}</span><div><b>${hit || (truth === 'fake' ? '가짜' : '진짜')}</b><span>${hit ? `정답은 <strong>${truth === 'fake' ? '가짜' : '진짜'}</strong> · ` : ''}${who}</span></div></div>`; };
  const card = (icon, label, title, desc) => `<div class="ans-card"><span class="ic">${ic(icon)}</span><div><small>${label}</small><b>${esc(title)}</b>${desc ? `<p>${esc(desc)}</p>` : ''}</div></div>`;
  if (p.seed && p.answer) { const a = p.answer, cr = C.CRITERIA[a.criterion], tc = C.TACTICS.find(x => x.id === a.tactic);
    let ss = sentences(a.explain); if (ss.length > 1 && /^(가짜|진짜|믿기 어렵)/.test(ss[0]) && ss[0].length < 16) ss = ss.slice(1);
    return `<div class="answer ${a.truth}">${head(a.truth, '예시 해설')}<div class="ans-body">
      <ul class="ans-list">${ss.map(s => `<li>${ic(a.truth === 'fake' ? 'search-x' : 'badge-check')}<span>${esc(s)}</span></li>`).join('')}</ul>
      ${cr || tc ? `<div class="ans-cards">${cr ? card(cr.icon, a.truth === 'fake' ? '들통나는 곳' : '진짜인 근거', cr.label, cr.hint) : ''}${tc ? card('drama', '쓴 수법', tc.id, tc.desc) : ''}</div>` : ''}
      ${p.counts ? countsHTML(p.counts) : ''}</div></div>`; }
  if (revealed(p) && p.secret) { const s = p.secret, cr = s.clueCriterion ? C.CRITERIA[s.clueCriterion] : null;
    return `<div class="answer ${s.truth}">${head(s.truth, `${p.team}조가 만든 ${s.truth === 'fake' ? '가짜' : '진짜'}`)}<div class="ans-body">
      <div class="ans-cards">${s.clue ? card(cr ? cr.icon : 'files', s.truth === 'real' ? '근거가 된 자료실 내용' : `숨긴 단서${cr ? ` · ${cr.label}` : ''}`, s.clue, '') : ''}${s.tactic ? card('drama', '쓴 수법', s.tactic, (C.TACTICS.find(x => x.id === s.tactic) || {}).desc) : ''}</div>
      ${p.counts ? countsHTML(p.counts) : ''}</div></div>`; }
  return '';
}
const countsHTML = c => `<div class="counts"><span class="real"><b>${c.real}</b>진짜라고 한 조</span><span class="fake"><b>${c.fake}</b>가짜라고 한 조</span><span><b>${c.unsure}</b>모르겠음</span></div>`;""")

h = B[0]
io.open(PP, 'w', encoding='utf-8', newline='').write(h.replace('\n', '\r\n') if crlf else h)
print('ok')
