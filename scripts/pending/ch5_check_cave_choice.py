# 2026-11-18: 동굴 = 코덱스 설득. 미션 카드 → 벽화마다 선택지 → 첫 바퀴는 일부러 틀리게 골라 다시 묻는지 보고, 둘째 바퀴에 맞게 골라 끝나는지 본다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_check_cave_choice.py <그림 폴더>
import asyncio, json, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800}); rq = ctx.request
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','cvc');localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');")
        post = lambda path, body, adm=False: rq.post(BASE + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'cvc', 'tut': True})
        r = await post('admin/stage', {'team': T, 'zones': ['z1', 'z2', 'z3'], 'done': ['q1', 'q2', 'q4', 'q5'], 'act': 3}, True); print('stage', r.status)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2.5)
        await ev("(()=>{ const f = __t['()=>{ const q = QUESTS.find(x=> x.id === \"q3\"); startWalk(PAIR); questLive = q; mini = {q, kind:\"cave\"}; caveStory(q); }']; f(); })()")
        VN = "document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''"
        said = []; picks = 0; cards = 0; trusts = []; done = None
        for i in range(900):
            if await ev("!!document.getElementById('missionCard') && !!document.getElementById('missionCard').dataset.on"):
                cards += 1; txt = await ev("document.getElementById('missionCard').innerText.replace(/\\s+/g, ' ')"); print('mission card:', txt); await asyncio.sleep(1.0); await pg.screenshot(path=os.path.join(OUT, 'cave_card.png')); await pg.keyboard.press('Space'); await asyncio.sleep(.6); continue
            c = await ev("__choice()")
            if c:
                picks += 1; trusts.append(c['trust']); k = picks - 1
                opts = await ev("__t.CAVE_CHOICE.map(c=> c.opts.findIndex(o=> o.ok))")
                good = opts[k % 4]; pick = good if (picks > 4 or k % 4 == 0) else (good + 1) % 3   # first round: only the first answer right (1 of 4), second round: all right
                await asyncio.sleep(.8)
                if picks in (1, 2): await pg.screenshot(path=os.path.join(OUT, f'cave_choice_{picks}.png'))
                await pg.keyboard.press(f'Digit{pick + 1}'); await asyncio.sleep(.5); continue
            t = await ev(VN)
            if t:
                if not said or said[-1] != t: said.append(t)
                await ev('__dbg.quest().next()'); await asyncio.sleep(.12); continue
            if await ev("!!document.getElementById('simDone').dataset.on || __dbg.simState().simOn"): done = 'simulator after the cave'; break
            await asyncio.sleep(.35)
        print('cards', cards, 'choices asked', picks, 'trust shown', trusts, 'end', done)
        print('retry line', [t for t in said if '아직은' in t or '다시 보면서' in t][:2]); print('last', said[-4:]); print('errs', errs[:3]); await br.close()
asyncio.run(main())
