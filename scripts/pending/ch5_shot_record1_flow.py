# 기록 1 제출(관리자 건너뛰기) 뒤 실제 흐름을 0.7초마다 찍는다: 완료 카드 → 보이드 → 시뮬레이터 → 섬(하모니아 복구 연출) → 1막.
#  python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_record1_flow.py <그림 폴더>
import asyncio, sys, os, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); T = 9
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); rq = ctx.request
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');localStorage.setItem('void-dev','rf1');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'rf1', 'tut': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8').replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.goto(f'http://127.0.0.1:8096/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9)
        await ev("(()=>{ const e = document.getElementById('teamPick'); if(e) delete e.dataset.on; })()")
        await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        n = 0; last = ''
        for k in range(110):
            st = await ev("""(()=>{ const on = id=> !!(document.getElementById(id) && document.getElementById(id).dataset.on); const t = __t;
              return {world:t['W'].id, sim:!!t['simOn'], vn:on('vn') ? document.getElementById('vnText').textContent.slice(0, 30) : '', voidv:on('voidVn') ? document.getElementById('voidTxt').textContent.slice(0, 30) : '', rec:on('recDone'), walk:!!t['walk'],
                chain:Object.entries(__dbg.rideState()).filter(([k, v])=> v.chain).map(([k, v])=> k + ':' + v.chain).join(' '), power:t['parkPowerOn']()}; })()""")
            line = json.dumps(st, ensure_ascii=False)
            if k % 1 == 0: await pg.screenshot(path=os.path.join(OUT, f'r_{k:03d}.png'))
            if line != last: print(f'{k:03d}', line); last = line
            if st['walk']: break
            # advance only the dialogues (cards wait 1.2 s so the effect shows)
            if st['rec'] and k % 3 == 2: await pg.keyboard.press('Space')
            elif st['voidv'] and k % 3 == 2: await pg.keyboard.press('Space')
            elif st['vn'] and k % 3 == 2: await ev('__dbg.quest().next()')
            await asyncio.sleep(.7)
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
