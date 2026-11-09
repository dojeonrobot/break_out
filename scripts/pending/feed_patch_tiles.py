# 2026-11-09 밤 라운드 선택 타일 재디자인 (사용자: "아래로 늘리기만 하면 어떡하냐, 이쁘게").
# 서버가 형식마다 예시 사진 4장(covers)을 내려 주고, 타일은 사진 카드: 뉴스 2x2 모자이크 / 쇼츠 세로 띠 3장 / 스토리 흐린 사진 위 링 3개.
# 지금 라운드는 인스타 그라데이션 링, 끝난 라운드는 초록 체크, 잠긴 라운드는 흑백+자물쇠. 세로 가운데 정렬.
import io, sys
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


SP = ROOT + r'\server\ch5_feed_server.py'
s, s_crlf = opener(SP)
if "'covers'" not in s:
    B = [s]; r = make_r(B)
    r("""    res['progress'] = round_progress()""", """    res['progress'] = round_progress()
    res['covers'] = round_covers()""")
    r("""def round_progress():""", """def round_covers():
    \"\"\"라운드 타일용 예시 사진 4장씩(형식별). 사진 id만 보내며 글 내용·정답은 없다.\"\"\"
    out = {}
    for f in ROUNDS:
        ids = [p.get('thumbImageId') or p.get('imageId') for p in DB['posts'] if p.get('seed') and p.get('format') == f and (p.get('imageId') or p.get('thumbImageId'))]
        out[f] = ids[:4]
    return out


def round_progress():""")
    s = B[0]
    io.open(SP, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if s_crlf else s)

PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'rt-photo' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)

# ---- CSS: 옛 타일 규칙 전부 교체 ----
a = B[0].index('    .rounds { display: grid;')
b = B[0].index('    .round-head { display: flex;')
B[0] = B[0][:a] + """    /* 라운드 선택: 사진 카드 3장 (2026-11-09 재디자인) */
    #tab-feed:has(#rounds:not([hidden])) { min-height: calc(100dvh - 32px); display: grid; align-content: center; }
    .rounds { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; padding: 0 16px; max-width: 1180px; align-items: end; }
    @media (min-width: 1024px) { .rounds { padding: 0; } }
    @media (max-width: 760px) { .rounds { grid-template-columns: 1fr; align-items: stretch; } }
    .round-tile { position: relative; display: block; width: 100%; aspect-ratio: 4 / 5; max-height: min(560px, calc(100dvh - 250px)); padding: 0; border: 0; border-radius: 24px; overflow: hidden; background: #262626; color: #fff; font: inherit; text-align: left; cursor: pointer; box-shadow: rgba(0,0,0,.02) 0 0 0 1px, rgba(0,0,0,.04) 0 2px 6px, rgba(0,0,0,.1) 0 4px 8px; transition: transform .25s cubic-bezier(.16,1,.3,1), box-shadow .25s; }
    .round-tile:not(:disabled):hover { transform: translateY(-6px); box-shadow: rgba(0,0,0,.04) 0 2px 6px, rgba(0,0,0,.18) 0 24px 48px; }
    .round-tile:not(:disabled):active { transform: translateY(-2px) scale(.99); }
    .round-tile:focus-visible { outline: 3px solid var(--focus); outline-offset: 4px; }
    .round-tile:disabled { cursor: not-allowed; }
    .round-tile.now { transform: scale(1.03); box-shadow: 0 0 0 4px var(--surface), 0 0 0 7px #d62976, rgba(214,41,118,.25) 0 24px 48px; }
    .round-tile.now::before { content: ""; position: absolute; inset: -7px; border-radius: 30px; background: var(--ig-grad); z-index: -1; }
    .round-tile.now:not(:disabled):hover { transform: scale(1.03) translateY(-6px); }
    .rt-photo { position: absolute; inset: 0; display: grid; gap: 3px; background: #1c1c1c; }
    .rt-photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .rt-photo.news { grid-template-columns: 1fr 1fr; grid-template-rows: 1.25fr 1fr; } .rt-photo.news img:first-child { grid-column: 1 / -1; }
    .rt-photo.shorts { grid-template-columns: 1fr 1fr 1fr; }
    .rt-photo.story { display: block; } .rt-photo.story img { filter: blur(14px) brightness(.8); transform: scale(1.15); }
    .rt-rings { position: absolute; left: 0; right: 0; top: 24%; display: flex; justify-content: center; align-items: center; gap: 14px; }
    .rt-rings span { width: 22%; aspect-ratio: 1; border-radius: 50%; padding: 4px; background: var(--ig-grad); box-shadow: 0 10px 30px rgba(0,0,0,.35); }
    .rt-rings span:nth-child(2) { width: 30%; } .rt-rings span img { width: 100%; height: 100%; border-radius: 50%; border: 4px solid #fff; object-fit: cover; filter: none; transform: none; }
    .rt-play { position: absolute; left: 50%; top: 40%; transform: translate(-50%, -50%); width: 64px; height: 64px; border-radius: 50%; background: rgba(255,255,255,.92); color: #111; display: grid; place-items: center; box-shadow: 0 10px 30px rgba(0,0,0,.35); } .rt-play .icon { width: 28px; height: 28px; margin-left: 3px; }
    .rt-shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 45%, rgba(0,0,0,.82) 100%); }
    .rt-num { position: absolute; top: 16px; left: 16px; z-index: 2; display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 800; letter-spacing: .02em; padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,.94); color: #262626; }
    .rt-num .icon { width: 14px; height: 14px; }
    .rt-state { position: absolute; top: 16px; right: 16px; z-index: 2; display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 800; padding: 6px 12px; border-radius: 999px; background: rgba(0,0,0,.45); color: #fff; backdrop-filter: blur(6px); }
    .rt-state .dot { width: 8px; height: 8px; border-radius: 50%; background: #fff; }
    .round-tile.now .rt-state { background: #d62976; } .round-tile.now .rt-state .dot { animation: rtPulse 1.5s ease-out infinite; box-shadow: 0 0 0 0 rgba(255,255,255,.7); }
    .round-tile.past .rt-state { background: var(--real); } .round-tile.past .rt-state .icon { width: 14px; height: 14px; }
    @keyframes rtPulse { to { box-shadow: 0 0 0 8px transparent; } }
    .rt-body { position: absolute; left: 0; right: 0; bottom: 0; z-index: 2; display: grid; gap: 6px; padding: 0 22px 22px; }
    .rt-body b { font-size: clamp(30px, 3.2vw, 40px); line-height: 1.05; letter-spacing: -0.02em; font-weight: 900; text-shadow: 0 2px 12px rgba(0,0,0,.4); }
    .rt-body small { font-size: 14px; line-height: 1.45; color: rgba(255,255,255,.85); word-break: keep-all; }
    .rt-cta { display: inline-flex; align-items: center; gap: 4px; margin-top: 8px; width: fit-content; padding: 10px 16px; border-radius: 999px; background: #fff; color: #111; font-size: 14px; font-weight: 800; } .rt-cta .icon { width: 16px; height: 16px; }
    .round-tile.now .rt-cta { background: var(--blue); color: #fff; }
    .round-tile:disabled .rt-photo { filter: grayscale(1) brightness(.55); } .round-tile:disabled .rt-play { display: none; } .round-tile:disabled .rt-rings { top: 14%; opacity: .7; } .round-tile:has(.rt-photo.story):disabled .rt-lock { top: 56%; }
    .round-tile:disabled .rt-body small, .round-tile:disabled .rt-body b { color: rgba(255,255,255,.75); }
    .rt-lock { position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%); z-index: 2; display: grid; place-items: center; width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.3); color: #fff; backdrop-filter: blur(6px); } .rt-lock .icon { width: 30px; height: 30px; }
    @media (prefers-reduced-motion: reduce) { .round-tile { transition: none; } .round-tile:hover, .round-tile:active, .round-tile.now { transform: none; } .round-tile.now .rt-state .dot { animation: none; } }
    .home-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; flex-wrap: wrap; max-width: 1180px; margin: 0 16px 26px; }
    @media (min-width: 1024px) { .home-head { margin: 0 0 26px; } }
    .home-head small { display: block; font-size: 13px; font-weight: 700; color: var(--muted); margin-bottom: 6px; }
    .home-head h1 { margin: 0; font-size: clamp(26px, 3.2vw, 36px); line-height: 1.15; letter-spacing: -0.01em; font-weight: 900; word-break: keep-all; }
    .home-head p { margin: 8px 0 0; font-size: 15px; color: var(--muted); word-break: keep-all; max-width: 44em; }
    .home-head .btn { min-height: 48px; padding: 0 22px; font-size: 16px; border-radius: 12px; }
""" + B[0][b:]

# ---- markup ----
r("""    const art = f === 'news' ? `<div class="rt-art art-news"><i class="mh"></i><i class="hl"></i><i class="hl s"></i><i class="ph"></i><i class="ln"></i><i class="ln s"></i></div>`
      : f === 'shorts' ? `<div class="rt-art art-shorts"><div class="phone"><span class="play">${ic('play')}</span><i class="cap"></i><i class="cap s"></i><span class="acts"><i></i><i></i><i></i></span></div></div>`
      : `<div class="rt-art art-story"><span class="ring" style="--c:#0f766e"><span></span></span><span class="ring" style="--c:#d62976"><span></span></span><span class="ring seen" style="--c:#4b5563"><span></span></span></div>`;
    const sub = { news: '언론사가 기자 이름을 걸고 쓰는 기사', shorts: '60초 세로 영상, 썸네일과 자막', story: '24시간 뒤 사라지는 한 장 + 한 줄' }[f];
    return `<button type="button" class="round-tile${now ? ' now' : past ? ' past' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">
      <span class="rt-num">${i + 1}라운드</span>${art}${open ? '' : `<span class="rt-lock"><span>${ic('lock')}</span></span>`}
      <span class="rt-body"><b>${ROUND_LABEL[f]}</b><small>${sub}</small><span class="rt-st"><i class="dot"></i>${st}</span></span></button>`;""",
"""    const cv = ((S.data.covers || {})[f] || []).map(id => `<img src="${imgSrc(id)}" alt="" loading="lazy">`);
    const art = f === 'news' ? `<span class="rt-photo news">${cv.slice(0, 3).join('')}</span>`
      : f === 'shorts' ? `<span class="rt-photo shorts">${cv.slice(0, 3).join('')}</span><span class="rt-play">${ic('play')}</span>`
      : `<span class="rt-photo story">${cv[0] || ''}</span><span class="rt-rings">${cv.slice(1, 4).map(x => `<span>${x}</span>`).join('')}</span>`;
    const sub = { news: '언론사가 기자 이름을 걸고 쓰는 기사', shorts: '60초 세로 영상, 썸네일과 자막', story: '24시간 뒤 사라지는 한 장과 한 줄' }[f];
    const cta = adm ? '전체 보기' : now ? { read: '예시 보기', make: '우리 조 만들기', judge: '판별하기', reveal: '정답 보기' }[S.data.phase] : past ? '다시 보기' : '';
    const state = adm ? st : now ? `<i class="dot"></i>${STEP_LABEL[S.data.phase]} 중` : past ? `${ic('check')}끝남 · 게시물 ${n}개` : '';
    return `<button type="button" class="round-tile${now ? ' now' : past ? ' past' : ''}" data-round="${f}" ${open ? '' : 'disabled'} aria-label="${i + 1}라운드 ${ROUND_LABEL[f]}${open ? '' : ' (잠김)'}">
      ${art}<span class="rt-shade"></span>
      <span class="rt-num">${ic(ROUND_ICON[f])}${i + 1}라운드</span>${state ? `<span class="rt-state">${state}</span>` : ''}
      ${open ? '' : `<span class="rt-lock">${ic('lock')}</span>`}
      <span class="rt-body"><b>${ROUND_LABEL[f]}</b><small>${open ? sub : `${i}라운드가 끝나면 열려요`}</small>${cta ? `<span class="rt-cta">${cta}${ic('arrow-right')}</span>` : ''}</span></button>`;""")
# 머리글의 바로 가기 버튼은 타일 CTA와 겹치므로 제거
r("""  box.innerHTML = `<div><small>지금 할 일</small><h1>${esc(txt[0])}</h1><p>${esc(txt[1])}</p></div><button type="button" class="btn btn-primary" data-round="${f}">${esc(txt[2])}${ic('chevron-right')}</button>`;""",
  """  box.innerHTML = `<div><small>지금 할 일</small><h1>${esc(txt[0])}</h1><p>${esc(txt[1])}</p></div>`;""")
h = B[0]
io.open(PP, 'w', encoding='utf-8', newline='').write(h.replace('\n', '\r\n') if h_crlf else h)
print('ok')
