# 왼쪽 카드(보이드의 기록)·오른쪽 현황판(기록 복구 현황) 시안: 버튼 모양 A/B × 열림/접힘.
# 실제 페이지 위에 시안 HTML·CSS를 끼워 화면 위쪽을 찍음. 사설 API 8096 + 정적 8097. 인자: 출력 폴더
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]

BTNS = '#board #bMin,#panel #toggle'
BASE_CSS = f"""
{BTNS}{{position:absolute;top:10px;right:10px;font-size:0!important;cursor:pointer;color:var(--fg);padding:0!important;min-width:0;min-height:0;grid-row:auto;grid-column:auto}}
#board #bMin::before,#board #bMin::after,#panel #toggle::before,#panel #toggle::after{{content:'';position:absolute;left:50%;top:50%;width:12px;height:2px;margin:-1px 0 0 -6px;border-radius:1px;background:currentColor}}
#board #bMin::after,#panel #toggle::after{{display:none;transform:rotate(90deg)}}
#board.closed #bMin::after,#panel.closed #toggle::after{{display:block}}
#panel{{position:fixed}} #panel .ph{{position:relative;padding-right:54px!important}}
#board .bh{{padding-right:54px!important}}
#board .bh .acts{{padding-top:0!important}}
#board.closed .bh small,#board.closed #bN{{display:none}}
#board.closed .bh{{padding-bottom:14px}}
#panel.closed #pSub,#panel.closed #iluaBox{{display:none!important}}
#panel.closed{{width:max-content!important}}
.recs{{margin-top:10px;display:flex;flex-direction:column;gap:6px}}
.rec{{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:center;padding:6px 8px;border-radius:10px;background:color-mix(in srgb,var(--restored,#1a9a5a) 8%,transparent)}}
.rec .th{{width:40px;height:40px;border-radius:8px;overflow:hidden;background:#cfd8d3}}
.rec .th img{{width:100%;height:100%;object-fit:cover;display:block}}
.rec h4{{margin:0;font-size:13.5px;font-weight:600}}
.rec p{{margin:2px 0 0;font-size:12px;color:var(--muted)}}
"""
BTN = {
 'A': BTNS.replace(',', ',') + "{width:32px;height:32px;border-radius:8px;border:1px solid color-mix(in srgb,currentColor 28%,transparent)!important;background:#fff!important;box-shadow:0 1px 2px rgba(20,30,40,.08)}",
 'B': BTNS + "{width:32px;height:32px;border-radius:50%;border:0!important;background:color-mix(in srgb,currentColor 10%,transparent)!important}",
}
HEAD = '<div><small>SCAN BREAK</small><h2>기록 복구 현황</h2></div><div class="acts"><b id="bN">67%</b></div><button id="bMin" type="button" aria-label="접기"></button>'
ROWS = ('<div class="bseg"><i class="ok"></i><i class="ok"></i><i></i></div>'
        '<div class="recs">'
        '<div class="rec"><span class="th"><img src="img/intro/cut1.jpg" alt=""></span><div><h4>기록 1 · 융합교육관</h4><p>하모니아 복구</p></div></div>'
        '<div class="rec"><span class="th"><img src="img/intro/cut2.jpg" alt=""></span><div><h4>기록 2</h4><p>회전목마 복구</p></div></div>'
        '</div>')

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True, is_mobile=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','brd');localStorage.setItem('void-sound','0');localStorage.removeItem('void-board');localStorage.removeItem('void-panel');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'brd', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page()
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4)
        shots = {}
        for k in ['A', 'B']:
            for closed in [False, True]:
                hgt = await pg.evaluate("""([css, head, rows, closed])=>{
                  let st = document.getElementById('sianCss'); if(!st){ st = document.createElement('style'); st.id = 'sianCss'; document.head.appendChild(st); }
                  st.textContent = css; const b = document.getElementById('board'), p = document.getElementById('panel');
                  const h = b.querySelector('.bh').cloneNode(false); h.innerHTML = head; b.querySelector('.bh').replaceWith(h);
                  const r = document.getElementById('bRows').cloneNode(false); r.innerHTML = rows; document.getElementById('bRows').replaceWith(r);
                  b.classList.add('solo'); b.classList.toggle('closed', closed); p.classList.toggle('closed', closed);
                  const t = document.getElementById('toggle'); t.textContent = ''; t.setAttribute('aria-label', closed ? '펼치기' : '접기');
                  return Math.max(b.getBoundingClientRect().bottom, closed ? p.getBoundingClientRect().bottom : 0); }""", [BASE_CSS + BTN[k], HEAD, ROWS, closed])
                await asyncio.sleep(.6)
                p = os.path.join(OUT, f'sian_{k}_{"closed" if closed else "open"}.png')
                await pg.screenshot(path=p, clip={'x': 0, 'y': 0, 'width': 1180, 'height': min(820, int(hgt) + 16)}); shots[(k, closed)] = p
        await br.close()
    ims = {key: Image.open(p).convert('RGB') for key, p in shots.items()}
    sc = 0.62; ims = {key: im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS) for key, im in ims.items()}
    fb = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 22); fr = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 16)
    W = max(im.width for im in ims.values()) + 60; H = sum(im.height + 40 for im in ims.values()) + 2 * 44 + 20
    sheet = Image.new('RGB', (W, H), (236, 240, 244)); d = ImageDraw.Draw(sheet); y = 20
    for k, name in [('A', 'A안  흰 네모 버튼(테두리)'), ('B', 'B안  회색 동그라미 버튼')]:
        d.text((30, y), name, fill=(20, 28, 38), font=fb); y += 44
        for closed, cap in [(False, '펼쳤을 때'), (True, '접었을 때')]:
            d.text((30, y), cap, fill=(90, 100, 110), font=fr); y += 24
            im = ims[(k, closed)]; sheet.paste(im, (30, y)); y += im.height + 16
    sheet = sheet.crop((0, 0, W, y + 10)); sheet.save(os.path.join(OUT, '현황판_시안.png')); print('saved')
asyncio.run(main())
