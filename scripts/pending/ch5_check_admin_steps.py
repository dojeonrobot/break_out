# 관리자 건너뛰기 알약을 눌러 가며 단계 이름을 받아 적는다(미션 1~2). 사설 API 8096 + 정적 8097.
# python scripts/pending/ch5_check_admin_steps.py [그림 폴더]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 6
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','admstep');localStorage.setItem('void-sound','0');sessionStorage.setItem('void-admin','0101');sessionStorage.setItem('void-admin-at',String(Date.now()));")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'admstep', 'done': [], 'act': 1, 'tut': True, 'story': 3})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:300]))
        ev = pg.evaluate
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(2)
        seen = []; shot_yard = False
        for k in range(60):
            st = await ev("(()=>{ const b = document.getElementById('admSkip'); return {t: b && !b.hidden ? document.getElementById('admSkipT').textContent : '', done: __dbg.quest().done, yard: !!document.getElementById('yardDlg').dataset.on}; })()")
            if st['yard'] and SHOT and not shot_yard:
                await asyncio.sleep(1.5); os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, 'yard_big.png'), timeout=60000); shot_yard = True
                print('board', await ev("(()=>{ const r = document.getElementById('ydBoard').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), innerWidth, innerHeight, document.querySelector('#yardDlg .room').scrollHeight]; })()"))
            if st['t'] and (not seen or seen[-1] != st['t']): seen.append(st['t']); print(len(seen), st['t'], st['done'], flush=True)
            if 'q2' in st['done']: break
            if st['t']: await ev("document.getElementById('admSkip').click()")
            await asyncio.sleep(1.2)
        print('errors:', errs); await br.close()
asyncio.run(main())
