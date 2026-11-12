# 2막(두 번째 캠퍼스 기록 뒤) → 미션 3 「바이킹」으로 넘어가는 실제 아이 경로 점검. 사설 API 8096 + 정적 8097.
# 캠퍼스에서 시작 → 완료 카드·보이드 대사·섬 전환·대사를 Space로 넘김 → 걷기가 시작되면 미션 3이 열려 있고 자일로가 공사장에 있어야 한다.
# 사용: python scripts/pending/ch5_check_viking_act2.py [그림 폴더]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 8
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','vikact');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/viking_clear', {'team': T}, True)
        for z in ('z1', 'z2'): await post('admin/skip', {'team': T, 'mission': z}, True)
        await post('quest', {'team': T, 'dev': 'vikact', 'done': ['q1', 'q2'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((getattr(e,'stack',None) or str(e))[:700]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && typeof window.__vikQ==='function'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }")
        seen = []; ok = False
        for i in range(400):
            st = await pg.evaluate("({vn:document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : '', vd:document.getElementById('voidVn').dataset.on ? '보이드(안내): ' + document.getElementById('voidTxt').textContent : '', rd:document.getElementById('recDone').dataset.on ? '[카드] ' + document.getElementById('rdT').textContent : '', live:__dbg.quest().live?.id || null, walk:!!__dbg.quest().live})")
            for k in ('rd', 'vd', 'vn'):
                if st[k] and (not seen or seen[-1] != st[k]): seen.append(st[k])
            if st['live'] == 'q4' and not st['vn'] and not st['vd']:
                await asyncio.sleep(1.5)
                if not await pg.evaluate("!!document.getElementById('vn').dataset.on"): ok = True; break
            await pg.keyboard.press('Space'); await asyncio.sleep(.45)
            if SHOT and st['vn'].startswith('보이드: 자일로가 바이킹'):
                os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, 'act2_scene.png'), timeout=60000)
        print('\n'.join(seen))
        q = await pg.evaluate('__vikQ()'); d = ((q['spot'][3] - q['xylo'][0])**2 + (q['spot'][4] - q['xylo'][1])**2)**.5
        hud = await pg.evaluate("document.getElementById('questHud').innerText")
        print(('OK   ' if ok else 'FAIL ') + 'act 2 ends with mission 3 being walked'); print(('OK   ' if d < 1 else 'FAIL ') + f'자일로 is at the viking site when the walk starts (off by {d:.1f})'); print('hud', repr(hud))
        cast = await pg.evaluate("document.body.innerText.includes('연구실')"); print(('OK   ' if not any('연구실' in s or '잔재' in s for s in seen) else 'FAIL ') + 'no lab / remnant lines in act 2')
        if SHOT: await pg.screenshot(path=os.path.join(SHOT, 'act2_walk.png'), timeout=60000)
        print('errors:', errs); await br.close()
asyncio.run(main())
