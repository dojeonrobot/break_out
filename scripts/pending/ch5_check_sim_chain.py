# 2026-11-18: 인트로 표지(5초 유지), 미션 시작 카드 다섯 장, 스캔 뒤 시뮬레이터에서 두 구간이 이어서 복구되는지 본다.
# 로컬 서버 하나로 본다: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096, 정적 파일 포함)
# 사용: python ch5_check_sim_chain.py <그림 폴더> [intro|card|sim2|sim3 ...]
import asyncio, json, sys, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
OUT = sys.argv[1]; WHAT = sys.argv[2:] or ['intro', 'card', 'sim2', 'sim3']
ARGS = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
INIT = "localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','simch');localStorage.setItem('void-sound','0');"
ADMIN = "sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));sessionStorage.setItem('void-view','%d');" % T

async def ready(pg):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.simState"): return
        except Exception: pass
        await asyncio.sleep(.25)

async def intro(br):
    for name, vp in (('wide', {'width': 1366, 'height': 768}), ('tab', {'width': 1280, 'height': 800}), ('tall', {'width': 800, 'height': 1280})):
        ctx = await br.new_context(viewport=vp); await ctx.add_init_script(INIT)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        t0 = time.time(); await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        await asyncio.sleep(2.6); await pg.screenshot(path=os.path.join(OUT, f'intro_{name}.png'))
        await pg.mouse.click(400, 300)   # a tap must not skip the cover
        out = None
        for _ in range(200):
            if await pg.evaluate("document.getElementById('intro').classList.contains('out')"): out = await pg.evaluate("performance.now()"); break
            await asyncio.sleep(.1)
        print('intro', name, 'cover left at ms', out and round(out), 'errs', errs[:2])
        await ctx.close()

async def card(br):
    ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); await ctx.add_init_script(INIT)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{BASE}/chapter05/index.html?team={T}&world=island', wait_until='domcontentloaded', timeout=120000); await ready(pg); await asyncio.sleep(7)
    # the card's own markup (same string as missionCard()), filled for each mission
    data = [['q1', 1, '섬의 전원을 되살려라', '롤러코스터가 제일 잘 보이는 자리', 'xylo'], ['q2', 2, '네이티를 찾아라', '정문 동쪽 길', 'naty'], ['q4', 3, '바이킹을 다시 세워라', '정문 거리 동쪽 공사장', 'xylo'], ['q5', 4, '일루아의 흐름을 가리는 것', '관람차 언덕 아래 연구실', 'void'], ['q3', 5, '코덱스를 찾아라', '북쪽 해안, 눈이 빛나는 곳', 'codex']]
    for vp in ((1280, 800), (780, 360), (390, 800)):
        await pg.set_viewport_size({'width': vp[0], 'height': vp[1]})
        for q, n, t, h, who in data:
            await pg.evaluate("""([n,t,h,who])=>{ let el = document.getElementById('missionCard'); if(!el){ el = document.createElement('div'); el.id = 'missionCard'; el.innerHTML = '<div class="in"><div class="face"><b id="mcNo"></b><img id="mcWho" alt=""></div><div class="body"><small id="mcN"></small><h1 id="mcT"></h1><p id="mcH"></p><button type="button" id="mcGo"></button></div></div>'; document.body.appendChild(el); }
              mcN.textContent = 'MISSION ' + n; mcNo.textContent = n; mcWho.src = 'img/chars/' + who + '.png?v=20261028c'; mcT.textContent = t; mcH.textContent = h; mcGo.textContent = '미션 시작 · Space'; el.dataset.on = '1'; }""", [n, t, h, who])
            await asyncio.sleep(.9)
            if vp[0] == 1280 or q in ('q1', 'q5'): await pg.screenshot(path=os.path.join(OUT, f'card_{vp[0]}_{q}.png'))
            box = await pg.evaluate("(()=>{ const r = mcWho.getBoundingClientRect(), b = mcGo.getBoundingClientRect(); return {img:[Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)], btn:[Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)], vw:innerWidth, vh:innerHeight}; })()")
            print('card', vp, q, box)
    print('card errs', errs[:2]); await ctx.close()

async def sim(br, stage, tag):
    ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); rq = ctx.request
    await ctx.add_init_script(INIT + ADMIN)
    post = lambda path, body, adm=False: rq.post(BASE + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
    await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'simch', 'tut': True})
    r = await post('admin/stage', dict(stage, team=T), True); print(tag, 'stage', r.status)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000); await ready(pg); await asyncio.sleep(8)
    SNAP = """()=>{ const on = id=> !!document.getElementById(id) && !!document.getElementById(id).dataset.on; const s = __dbg.simState(), a = document.getElementById('admSkip');
      return {skip:a && !a.hidden ? a.innerText.replace(/\\s+/g, ' ') : '', void:on('voidVn'), vn:on('vn'), card:on('recDone'), sim:s.simOn, lit:s.lit, reveals:s.reveals}; }"""
    last = None; shots = 0
    for i in range(160):
        s = await pg.evaluate(SNAP); k = json.dumps(s, ensure_ascii=False)
        if k != last: print(tag, k); last = k
        if s['sim'] and s['reveals'] and not s['vn'] and not s['void']:
            for j in range(9): await asyncio.sleep(1.1); await pg.screenshot(path=os.path.join(OUT, f'{tag}_{j}.png'))
            shots = 9; break
        if s['skip'] and '스캔' in s['skip']: await pg.click('#admSkip'); await asyncio.sleep(1.2)
        elif s['card'] or s['void'] or s['vn']: await pg.keyboard.press('Space'); await asyncio.sleep(.6)
        else: await asyncio.sleep(.6)
    print(tag, 'shots', shots, 'errs', errs[:3]); await ctx.close()

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=ARGS)
        pg = await br.new_page(); print('renderer', await pg.evaluate("(()=>{ const g = document.createElement('canvas').getContext('webgl'); const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?'; })()")); await pg.close()
        if 'intro' in WHAT: await intro(br)
        if 'card' in WHAT: await card(br)
        if 'sim2' in WHAT: await sim(br, {'zones': ['z1'], 'done': ['q1', 'q2'], 'act': 1}, 'sim2')
        if 'sim3' in WHAT: await sim(br, {'zones': ['z1', 'z2'], 'done': ['q1', 'q2', 'q4', 'q5'], 'act': 2}, 'sim3')
        await br.close()
asyncio.run(main())
