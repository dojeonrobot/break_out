# 탐험 캐릭터 고르기(제로·리코 중 한 명, 3인칭·1인칭) 점검. 사설 API 8096 + 정적 8097.
# python scripts/pending/ch5_check_hero_pick.py [그림 폴더]
#  1) 처음 걷기를 시작하면 고르는 창이 뜬다(걷기는 아직 시작 안 됨) → 리코·1인칭을 고르고 시작 → 리코 혼자, 1인칭, 두 캐릭터 모두 화면에 안 보임
#  2) 걷는 중 「캐릭터·시점」으로 제로·3인칭으로 바꾸면 그 자리에서 바뀐다(제로만 보임)
#  3) 걸을 때 캐릭터가 걷는 자리에 정확히 있다(뒤따라오는 지연 0)
#  4) 새로고침 뒤에는 묻지 않고 저장한 값으로 걷는다. 나가면 두 캐릭터가 다시 보인다
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 5
SHOT = sys.argv[1] if len(sys.argv) > 1 else None
fails = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg, flush=True)
    if not ok: fails.append(msg)
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        errs = []
        for name, vw, vh in [('tablet-land', 1180, 820), ('tablet-port', 820, 1180)]:
            ctx = await br.new_context(viewport={'width': vw, 'height': vh}, has_touch=True); rq = ctx.request
            async def route(r):
                q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','heropick');localStorage.setItem('void-sound','0');")
            post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
            await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
            await post('quest', {'team': T, 'dev': 'heropick', 'done': [], 'act': 1, 'tut': True, 'story': 3})
            pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append((getattr(e, 'stack', None) or str(e))[:300]))
            ev = pg.evaluate
            async def load(clear):
                await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
                for _ in range(480):
                    try:
                        if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && typeof window.__dbg.hero==='function'"): break
                    except Exception: pass
                    await asyncio.sleep(.25)
                if clear: await ev(f"localStorage.removeItem('void-hero-{T}')")
                await ev("()=>{ const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on; }"); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(2)
            async def shot(n):
                if SHOT:
                    os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, f'{name}_{n}.png'), timeout=60000)
            async def drain():
                for _ in range(60):
                    if not await ev('!!__dbg.quest().vn()'):
                        await asyncio.sleep(.4)
                        if not await ev('!!__dbg.quest().vn()'): return
                    await ev('__dbg.quest().next()'); await asyncio.sleep(.08)
            await load(True)
            pill = await ev("(()=>{const e=document.getElementById('questPill');return e&&!e.hidden})()")
            await ev("document.getElementById('questPill').click()") if pill else await ev("document.getElementById('lWalk').click()")
            await asyncio.sleep(1.2)
            h = await ev('__dbg.hero()'); check(h['open'] and h['mates'] is None, f'{name}: the first walk opens the picker and does not start yet {h}')
            box = await ev("(()=>{ const r = document.querySelector('#heroPick .in').getBoundingClientRect(), g = document.getElementById('hpGo').getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom), innerHeight, Math.round(g.height), [...document.querySelectorAll('#heroPick .view button')].map(b=> Math.round(b.getBoundingClientRect().height))]; })()")
            check(box[0] >= 0 and box[1] <= box[2] and box[3] >= 44, f'{name}: the picker fits the screen and the buttons are at least 44 px tall {box}')
            await shot('1_picker')
            check(await ev("document.getElementById('hpView').hidden"), f'{name}: no view choice (first person only)'); await pg.click('#hpWho [data-n="리코"]'); await asyncio.sleep(.3); await shot('2_picker_rico_fp')
            await pg.click('#hpGo'); await asyncio.sleep(2.5); await drain(); await asyncio.sleep(1)
            h = await ev('__dbg.hero()'); print(h)
            check(h['mates'] == ['리코'] and h['walkFp'] is True and all(not v for _, v in h['shown']), f'{name}: 리코 alone, first person, neither of the pair is drawn')
            check(await ev("document.getElementById('walkName').textContent") == '리코' and await ev("__dbg.quest().live?.id") == 'q1', f'{name}: the pill names 리코 and mission 1 is live')
            await shot('3_first_person')
            await pg.keyboard.down('KeyW'); await asyncio.sleep(1.5); await shot('3b_first_person_walking'); await pg.keyboard.up('KeyW')
            # switch while walking
            await pg.click('#walkWho'); await asyncio.sleep(.5); await pg.click('#hpWho [data-n="제로"]'); await pg.click('#hpGo'); await asyncio.sleep(1.2)
            h = await ev('__dbg.hero()'); print(h)
            check(h['mates'] == ['제로'] and h['walkFp'] is True and all(not v for _, v in h['shown']), f'{name}: switched to 제로, still first person')
            check(await ev("__dbg.quest().live?.id") == 'q1', f'{name}: the mission is still live after the switch')
            await shot('4_third_person')
            await pg.keyboard.down('KeyW'); lag = []
            for _ in range(12):
                await asyncio.sleep(.12); lag.append(await ev("(()=>{ const w = __dbg.walkState(), p = __dbg.chars().ZERO.position; return Math.hypot(p.x - w.x, p.z - w.z); })()"))
            await shot('4b_third_person_walking'); await pg.keyboard.up('KeyW')
            check(max(lag) < 0.05, f'{name}: while walking the explorer is exactly on the walk position (largest gap {max(lag):.3f})')
            # reload: no picker
            await load(False); await ev("__dbg.setWorld('island',true)"); await asyncio.sleep(1)
            await ev("(()=>{ const e=document.getElementById('questPill'); if(e && !e.hidden) e.click(); else document.getElementById('lWalk').click(); })()"); await asyncio.sleep(2.5); await drain()
            h = await ev('__dbg.hero()'); check(not h['open'] and h['mates'] == ['제로'], f'{name}: after a reload the saved choice is used, no picker {h}')
            await pg.click('#walkX'); await asyncio.sleep(1)
            h = await ev('__dbg.hero()'); check(all(v for _, v in h['shown']), f'{name}: after leaving the walk both are drawn again {h["shown"]}')
            await ctx.close()
        await br.close(); print('errors:', errs); check(not errs, 'no page errors'); print('FAILS', len(fails), fails)
asyncio.run(main())
