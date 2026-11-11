# 튜토리얼 짚기 연출 점검: 조를 고르고 튜토리얼을 넘기며 14·18·20·22번째 단계에서 밝게 남는 영역이 대상과 맞는지, 화면 안에 있는지, 대사 창에 가리지 않는지 잰다.
# 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_tut_spotlight.py [shot_dir]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; SHOT = sys.argv[1] if len(sys.argv) > 1 else None; T = 8
STATE = r"""()=>{ const s = document.getElementById('tutSpot'), z = document.querySelector('.tut-zoom'), box = document.querySelector('#voidVn .box').getBoundingClientRect();
 if(!s || s.hidden || !z) return {on:false};
 const r = s.getBoundingClientRect(), t = z.getBoundingClientRect(), tag = s.querySelector('b').getBoundingClientRect(), ov = (a, b)=> a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
 return {on:true, target:(z.id ? '#' + z.id : '.' + z.className.split(' ')[0]), rect:[Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], follows:Math.abs(r.left - (t.left - 8)) < 2 && Math.abs(r.top - (t.top - 8)) < 2,
  inView:r.left >= -8 && r.top >= -8 && r.right <= innerWidth + 8 && r.bottom <= innerHeight + 8, tagInView:tag.left >= 0 && tag.top >= 0 && tag.right <= innerWidth && tag.bottom <= innerHeight, underDialogue:ov(t, box), tagUnderDialogue:ov(tag, box), opacity:+getComputedStyle(s).opacity}; }"""
async def main():
    fails = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, w, h, touch in [('laptop', 1366, 768, False), ('tablet-land', 1180, 820, True), ('tablet-port', 820, 1180, True)]:
            ctx = await br.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
            async def route(r):
                q = r.request; res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');")
            await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto(STATIC + '/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
            for _ in range(240):
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd && !!document.getElementById('teamPick').dataset.on"): break
                await asyncio.sleep(.5)
            await pg.evaluate("()=>{const b=[...document.querySelectorAll('#tpGrid button')].find(b=>b.textContent.trim().startsWith('%d조'));b.click()}" % T)
            for _ in range(60):
                if await pg.evaluate("__dbg.tutState().step>=0"): break
                await asyncio.sleep(.5)
            seen = {}
            for _ in range(40):
                step = await pg.evaluate("__dbg.tutState().step")
                if step >= 99 or step < 0: break
                await asyncio.sleep(1.3); st = await pg.evaluate(STATE); seen[step + 1] = st
                if st['on']:
                    print(name, 'step', step + 1, json.dumps(st, ensure_ascii=False), flush=True)
                    if not (st['follows'] and st['inView'] and st['tagInView'] and not st['underDialogue'] and not st['tagUnderDialogue'] and st['opacity'] > .9): fails.append((name, step + 1, st))
                    if SHOT:
                        os.makedirs(SHOT, exist_ok=True); await pg.screenshot(path=os.path.join(SHOT, f'{name}_step{step + 1}.png'), timeout=60000)
                await pg.evaluate("document.getElementById('voidNext').click()"); await asyncio.sleep(.4)
            on = sorted(k for k, v in seen.items() if v['on'])
            print(name, '짚은 단계', on, '끝난 뒤 남음', await pg.evaluate("!!document.querySelector('.tut-zoom') || (document.getElementById('tutSpot') && !document.getElementById('tutSpot').hidden)"), errs, flush=True)
            if on != [14, 18, 20, 22]: fails.append((name, 'steps', on))
            if errs: fails.append((name, 'pageerror', errs[:2]))
            await ctx.close()
        await br.close()
    print('FAILS', json.dumps(fails, ensure_ascii=False))
asyncio.run(main())
