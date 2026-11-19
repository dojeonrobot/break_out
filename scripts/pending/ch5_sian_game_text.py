# 시안: 연구실 게임 설명 글을 크게(A = 게임 화면 위쪽 큰 띠, B = 게임 화면 아래 큰 자막). 실제 화면에 CSS만 입혀 찍는다(페이지는 안 고침).
# 사설 API 8096 + 정적 8097.  python ch5_sian_game_text.py <그림 폴더> [게임 이름]
import asyncio, json, re, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]; NAME = sys.argv[2] if len(sys.argv) > 2 else '아이콘 베기'
BASE = "#sliceDlg .in{position:relative}#sliceDlg .in p#slP{position:absolute;left:50%;transform:translateX(-50%);z-index:3;pointer-events:none;white-space:nowrap;font-size:30px;font-weight:800;line-height:1.3;color:#fff;background:rgba(6,17,26,.86);border:2px solid #8cecff;padding:14px 30px;border-radius:16px;word-break:keep-all}#sliceDlg .in h1{font-size:30px}"
VAR = {'A': BASE + "#sliceDlg .in p#slP{top:118px}", 'B': BASE + "#sliceDlg .in p#slP{bottom:34px}"}
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','slc');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True)
        for z in ('z1', 'z2'): await post('admin/skip', {'team': T, 'mission': z}, True)
        await post('quest', {'team': T, 'dev': 'slc', 'done': ['q1', 'q2', 'q4'], 'act': 2, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4); await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2); await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
        async def drain():
            for _ in range(60):
                if not await ev("!!document.getElementById('vn').dataset.on"):
                    await asyncio.sleep(.4)
                    if not await ev("!!document.getElementById('vn').dataset.on"): return
                    continue
                await ev('__dbg.quest().next()'); await asyncio.sleep(.1)
        await drain(); tg = await ev('__dbg.target()'); await ev("([x, z])=> __dbg.walkTo(x, z + 3)", tg)
        for _ in range(80):
            await drain()
            if await ev("!!document.getElementById('sliceDlg') && !!document.getElementById('sliceDlg').dataset.on"): break
            await asyncio.sleep(.4)
        await asyncio.sleep(1.2); await ev("(n)=>{ const h = document.querySelector('#sliceDlg h1'); if(h) h.textContent = n; }", NAME)
        if NAME == 'bg':   # 2026-11-19 배경 시안 A·B·C와 깬 뒤 창이 걷히는 장면
            for _ in range(4):
                await ev("(()=>{ const b = document.getElementById('slTut'); if(b && !b.hidden) b.click(); })()"); await asyncio.sleep(.5)
            for k in ('A', 'B', 'C'):
                await ev("(()=>{ document.querySelector('#sliceDlg h1').textContent = '아이콘 베기'; const r = document.getElementById('slRetry'); if(r) r.click(); })()")
                await ev(f"__sliceBg('{k}')"); await asyncio.sleep(2.0); await pg.screenshot(path=os.path.join(OUT, f'bg_{k}.png')); print('shot', k)
            await ev('__sliceWin()'); await asyncio.sleep(1.5); await pg.screenshot(path=os.path.join(OUT, 'bg_win_fade.png')); await asyncio.sleep(1.2); await pg.screenshot(path=os.path.join(OUT, 'bg_win_after.png')); await br.close(); return
        for k, css in VAR.items():
            await ev("(c)=>{ let s = document.getElementById('sianCss'); if(!s){ s = document.createElement('style'); s.id = 'sianCss'; document.head.appendChild(s); } s.textContent = c; }", css)
            await asyncio.sleep(.5); await pg.screenshot(path=os.path.join(OUT, f'sian_{k}.png')); print('shot', k)
        await br.close()
asyncio.run(main())
