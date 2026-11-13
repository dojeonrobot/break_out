# 초기화 뒤 대사 겹침 점검. 섬에서 막 대사(캐릭터 대사 창)가 떠 있는 채로 ① 전체 초기화 ② 관리자 조 초기화 ③ 「처음부터」(서버 호출만)를 하고,
# 조를 다시 고른 뒤 대사 창이 둘 이상 동시에 떠 있는 순간이 있는지 본다. 사설 API 8096 + 정적 8097.
import asyncio, json, re, sys
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9
SNAP = """()=>{ const on = id=> !!document.getElementById(id) && !!document.getElementById(id).dataset.on; const tx = id=> (document.getElementById(id) || {}).innerText || '';
  return {void:on('voidVn') ? tx('voidTxt').slice(0, 26) : '', vn:on('vn') ? (tx('vnName') + ':' + tx('vnText')).slice(0, 26) : '', card:on('recDone'), pick:on('teamPick'), tut:__dbg.tutState().step, world:__dbg.tutState().world, busy:__dbg.simState().busy, walk:__dbg.simState().walk, lbl:document.getElementById('lLbl').getAttribute('aria-pressed')}; }"""
fails = []
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for mode in ('전체 초기화', '관리자 조 초기화'):
            ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
            async def route(r):
                q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            await ctx.add_init_script("localStorage.setItem('void-dev','ovl');localStorage.setItem('void-sound','0'); if(!localStorage.getItem('void-reset')) localStorage.setItem('void-reset', String(Date.now()));")
            post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
            await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
            await post('quest', {'team': T, 'dev': 'ovl', 'done': [], 'act': 0, 'tut': True})
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160])); loads = []; pg.on('load', lambda: loads.append(1))
            await pg.goto(f'{STATIC}/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
            async def ready():
                for _ in range(480):
                    try:
                        if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): return
                    except Exception: pass
                    await asyncio.sleep(.25)
            async def pick():
                for _ in range(40):
                    try:
                        if await pg.evaluate("!!document.getElementById('teamPick').dataset.on"): break
                    except Exception: pass
                    await asyncio.sleep(.5)
                await pg.evaluate("(t)=>{ const b = document.querySelector(`#tpGrid [data-t=\"${t}\"]`); if(b) b.click(); }", T)
            await ready(); await pick()
            # 1막: 카드 → 보이드 대사 → 섬 → 캐릭터 대사 창이 뜰 때까지 넘긴다
            st = {}
            for _ in range(160):
                st = await pg.evaluate(SNAP)
                if st['vn'] and st['world'] == 'island': break
                await pg.keyboard.press('Space'); await asyncio.sleep(.5)
            print(f'== {mode}: 초기화 직전', json.dumps(st, ensure_ascii=False))
            if not st.get('vn'): fails.append(mode + ': 캐릭터 대사 창까지 못 감')
            n0 = len(loads)
            if mode == '전체 초기화': await post('admin/reset', {'confirm': 'RESET', 'hide': []}, True)
            else: await post('admin/quest', {'team': T, 'clear': True}, True)
            for _ in range(80):
                if len(loads) > n0: break
                await asyncio.sleep(.5)
            print('   다시 열림:', len(loads) > n0)
            if len(loads) == n0: fails.append(mode + ': 페이지가 새로 열리지 않음')
            await ready()
            if mode == '전체 초기화': await pick()
            both = 0; seen = []
            for _ in range(30):
                try: s = await pg.evaluate(SNAP)
                except Exception: await asyncio.sleep(.5); continue
                if s['void'] and s['vn']: both += 1
                k = json.dumps(s, ensure_ascii=False)
                if not seen or seen[-1] != k: seen.append(k)
                await asyncio.sleep(.5)
            print('   끝 상태', seen[-1][:230]); print('   두 대사 창이 같이 뜬 횟수', both, 'errs', errs[:2])
            if both: fails.append(mode + ': 대사 창 겹침')
            await ctx.close()
        await br.close(); print('FAILS', fails)
asyncio.run(main())
