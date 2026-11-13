# 관리자 기기(조 태블릿에 관리자 로그인)에서 「건너뛰기」로 기록 1 스캔을 넘긴 뒤 1막 시뮬레이터에 흐름이 켜지는지 본다. 사설 API 8096 + 정적 8097.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1] if len(sys.argv) > 1 else None
SNAP = """()=>{ const on = id=> !!document.getElementById(id) && !!document.getElementById(id).dataset.on; const tx = id=> (document.getElementById(id) || {}).innerText || ''; const s = __dbg.simState(), a = document.getElementById('admSkip');
  return {skip:a && !a.hidden ? a.innerText.replace(/\\s+/g, ' ') : '', void:on('voidVn') ? tx('voidTxt').slice(0, 20) : '', vn:on('vn') ? tx('vnText').slice(0, 20) : '', card:on('recDone'), sim:s.simOn, lit:s.lit, reveals:s.reveals, world:__dbg.tutState().world, hud:(document.getElementById('simHud') || document.getElementById('simBar') || {innerText:''}).innerText.replace(/\\s+/g, ' ').slice(0, 60)}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        view = sys.argv[2] if len(sys.argv) > 2 else str(T)
        await ctx.add_init_script(f"localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','admsk');localStorage.setItem('void-sound','0');sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));sessionStorage.setItem('void-view','{view}');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'admsk', 'tut': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(4); seen = []; shot = False
        for i in range(90):
            s = await pg.evaluate(SNAP); k = json.dumps(s, ensure_ascii=False)
            if not seen or seen[-1] != k: seen.append(k); print(k[:260])
            if s['sim'] and s['vn'] and not shot and OUT: os.makedirs(OUT, exist_ok=True); await asyncio.sleep(1.5); await pg.screenshot(path=os.path.join(OUT, f'sim_view{view}.png')); shot = True; break
            if s['skip'] and '스캔' in s['skip']: await pg.click('#admSkip'); await asyncio.sleep(1.2)
            elif s['card'] or s['void'] or s['vn']: await pg.keyboard.press('Space'); await asyncio.sleep(.6)
            else: await asyncio.sleep(.6)
        print('view', view, 'errs', errs[:2]); await br.close()
asyncio.run(main())
