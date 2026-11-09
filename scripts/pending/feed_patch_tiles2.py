# 2026-11-09 밤 5: 타일 그림을 매체답게 (사용자: 뉴스·쇼츠 특성이 안 보임).
#  뉴스 = 기울어진 신문 1면(제호·빨간 탭·큰 제목·사진·단 글) / 쇼츠 = 세로 폰 화면(Shorts 마크·오른쪽 ♥💬↗·자막·채널) 두 대 / 스토리 = 그대로.
#  서버 covers 는 {img, title, name} 객체로.
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
if "'name': (p.get('author')" not in s:
    B = [s]; r = make_r(B)
    r("""        ids = [p.get('thumbImageId') or p.get('imageId') for p in DB['posts'] if p.get('seed') and p.get('format') == f and (p.get('imageId') or p.get('thumbImageId'))]
        out[f] = ids[:4]""", """        items = [{'img': p.get('thumbImageId') or p.get('imageId'), 'title': (p.get('thumbTitle') or p.get('title') or (p.get('body') or '').split('\\n')[0])[:60],
                  'name': (p.get('author') or {}).get('name', '')}
                 for p in DB['posts'] if p.get('seed') and p.get('format') == f and (p.get('imageId') or p.get('thumbImageId'))]
        out[f] = items[:4]""")
    s = B[0]
    io.open(SP, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if s_crlf else s)

PP = ROOT + r'\chapter05\feed.html'
h, h_crlf = opener(PP)
if 'rt-paper' in h:
    sys.exit('페이지: 이미 적용됨')
B = [h]; r = make_r(B)
r("""    .rt-photo.news { grid-template-columns: 1fr 1fr; grid-template-rows: 1.25fr 1fr; } .rt-photo.news img:first-child { grid-column: 1 / -1; }
    .rt-photo.shorts { grid-template-columns: 1fr 1fr 1fr; }""",
"""    /* 뉴스: 신문 1면 */
    .rt-paper-bg { position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 0%, #3b4252 0%, #1f2430 60%, #15181f 100%); }
    .rt-paper { position: absolute; left: 50%; top: 52px; width: 82%; transform: translateX(-50%) rotate(-3deg); background: #fbfaf6; color: #111; border-radius: 6px; padding: 12px 14px 14px; box-shadow: 0 24px 50px rgba(0,0,0,.5), 0 2px 0 #e7e3d8; display: grid; gap: 8px; font-family: "Noto Serif KR", serif; }
    .rt-paper .mast { display: flex; align-items: baseline; justify-content: space-between; border-bottom: 3px double #333; padding-bottom: 6px; }
    .rt-paper .mast b { font-size: 20px; font-weight: 900; letter-spacing: -.03em; } .rt-paper .mast span { font-family: var(--sans); font-size: 9px; color: #777; }
    .rt-paper .tabs { display: flex; gap: 8px; font-family: var(--sans); font-size: 9px; color: #888; border-bottom: 1px solid #ddd; padding-bottom: 5px; } .rt-paper .tabs b { color: #c8102e; }
    .rt-paper .hl { font-size: 15px; line-height: 1.35; font-weight: 800; letter-spacing: -.02em; word-break: keep-all; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .rt-paper img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block; border-radius: 2px; }
    .rt-paper .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; } .rt-paper .cols i { display: block; height: 5px; border-radius: 2px; background: #cfcbc1; margin-bottom: 4px; } .rt-paper .cols i:last-child { width: 60%; }
    .round-tile:disabled .rt-paper { filter: grayscale(1) brightness(.75); }
    /* 쇼츠: 세로 폰 화면 */
    .rt-shorts-bg { position: absolute; inset: 0; background: #0f0f0f; }
    .rt-phone { position: absolute; top: 46px; width: 54%; aspect-ratio: 9 / 16; border-radius: 22px; overflow: hidden; background: #222; box-shadow: 0 0 0 4px #2a2a2a, 0 24px 50px rgba(0,0,0,.6); }
    .rt-phone.main { left: 50%; transform: translateX(-32%); z-index: 1; } .rt-phone.back { left: 50%; transform: translateX(-108%) scale(.86); top: 70px; opacity: .55; filter: brightness(.7); }
    .rt-phone img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .rt-phone .ov { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.35), transparent 25%, transparent 55%, rgba(0,0,0,.75)); }
    .rt-phone .logo { position: absolute; top: 10px; left: 10px; display: inline-flex; align-items: center; gap: 4px; color: #fff; font-size: 11px; font-weight: 900; letter-spacing: -.01em; } .rt-phone .logo i { display: grid; place-items: center; width: 16px; height: 16px; border-radius: 4px; background: #ff0033; } .rt-phone .logo .icon { width: 10px; height: 10px; color: #fff; }
    .rt-phone .acts { position: absolute; right: 8px; bottom: 54px; display: grid; gap: 10px; justify-items: center; color: #fff; font-size: 8px; font-weight: 700; } .rt-phone .acts .icon { width: 20px; height: 20px; filter: drop-shadow(0 1px 2px rgba(0,0,0,.5)); }
    .rt-phone .cap { position: absolute; left: 10px; right: 40px; bottom: 12px; color: #fff; display: grid; gap: 5px; }
    .rt-phone .cap .ch { display: flex; align-items: center; gap: 6px; font-size: 9.5px; font-weight: 700; } .rt-phone .cap .ch i { width: 16px; height: 16px; border-radius: 50%; background: var(--ig-grad); display: inline-block; }
    .rt-phone .cap .tx { font-size: 10px; line-height: 1.3; word-break: keep-all; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-weight: 600; }
    .rt-phone .bar { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: rgba(255,255,255,.3); } .rt-phone .bar::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 42%; background: #ff0033; }
    .round-tile:disabled .rt-phone { filter: grayscale(1) brightness(.6); }""")
r("""    const art = f === 'news' ? `<span class="rt-photo news">${cv.slice(0, 3).join('')}</span>`
      : f === 'shorts' ? `<span class="rt-photo shorts">${cv.slice(0, 3).join('')}</span><span class="rt-play">${ic('play')}</span>`
      : `<span class="rt-photo story">${cv[0] || ''}</span><span class="rt-rings">${cv.slice(1, 4).map(x => `<span>${x}</span>`).join('')}</span>`;""",
"""    const cvo = ((S.data.covers || {})[f] || []).map(x => typeof x === 'string' ? { img: x, title: '', name: '' } : x);
    const im = o => o && o.img ? `<img src="${imgSrc(o.img)}" alt="" loading="lazy">` : '';
    const art = f === 'news' ? `<span class="rt-paper-bg"></span><span class="rt-paper"><span class="mast"><b>${esc(cvo[0]?.name || '도로일보')}</b><span>${new Date().getFullYear()}.${String(new Date().getMonth() + 1).padStart(2, '0')}</span></span><span class="tabs"><span>정치</span><span>경제</span><b>사회</b><span>문화</span><span>지역</span></span><span class="hl">${esc(cvo[0]?.title || '')}</span>${im(cvo[0])}<span class="cols"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span></span></span>`
      : f === 'shorts' ? `<span class="rt-shorts-bg"></span><span class="rt-phone back">${im(cvo[1])}<span class="ov"></span></span><span class="rt-phone main">${im(cvo[0])}<span class="ov"></span><span class="logo"><i>${ic('play')}</i>Shorts</span><span class="acts">${ic('heart')}<span>12만</span>${ic('message-circle')}<span>1.2천</span>${ic('send')}<span>공유</span></span><span class="cap"><span class="ch"><i></i>${esc(cvo[0]?.name || '')}</span><span class="tx">${esc(cvo[0]?.title || '')}</span></span><span class="bar"></span></span>`
      : `<span class="rt-photo story">${im(cvo[0])}</span><span class="rt-rings">${cvo.slice(1, 4).map(x => `<span>${im(x)}</span>`).join('')}</span>`;""")
r("""    .round-tile:disabled .rt-photo { filter: grayscale(1) brightness(.55); } .round-tile:disabled .rt-play { display: none; }""",
  """    .round-tile:disabled .rt-photo { filter: grayscale(1) brightness(.55); }""")
h = B[0]
io.open(PP, 'w', encoding='utf-8', newline='').write(h.replace('\n', '\r\n') if h_crlf else h)
print('ok')
