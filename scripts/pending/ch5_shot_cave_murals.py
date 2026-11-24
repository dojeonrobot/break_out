# 동굴 앞 장면 → 벽화 다섯 점을 차례로 찍는다(대사 창이 뜬 화면 + 대사 창을 숨긴 화면). 선택지는 맞는 답을 고른다.
#  로컬 서버 8096(CH5_ADMIN_KEY=0101, VOID_STATIC=1).  python ch5_shot_cave_murals.py <그림 폴더> [너비 높이]
import asyncio, json, sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
BASE = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
VW, VH = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else tuple(int(v) for v in os.environ.get('CH5_SIZE', '1280x800').split('x'))   # CH5_SIZE=800x1280 when run through the runner
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': VW, 'height': VH}); rq = ctx.request
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','cvm');localStorage.setItem('void-sound','0');localStorage.setItem('void-card-test','1');")
        post = lambda path, body, adm=False: rq.post(BASE + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('quest', {'team': T, 'dev': 'cvm', 'tut': True})
        await post('admin/stage', {'team': T, 'zones': ['z1', 'z2', 'z3'], 'done': ['q1', 'q2', 'q4', 'q5'], 'act': 3}, True)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.goto(f'{BASE}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        print('gl', await ev("(()=>{ const g = document.createElement('canvas').getContext('webgl'); const d = g.getExtension('WEBGL_debug_renderer_info'); return d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : '?'; })()"))
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2.5)
        await ev("(()=>{ const f = __t['()=>{ const q = QUESTS.find(x=> x.id === \"q3\"); startWalk(PAIR); const c = codexWait(); walk.x = c[0] + 5; walk.z = c[1] + 5; walk.yaw = Math.atan2(c[0] - walk.x, c[1] - walk.z); walk.snap = true; questLive = q; }']; f(); })()")
        await asyncio.sleep(2)
        # the same path the child takes: found at the cave mouth
        await ev("(()=>{ const f = __t['()=>{ const q = QUESTS.find(x=> x.id === \"q3\"); natyBeside(); say(QUEST_FOUND.q3(walk.name), ()=> miniStart(q)); }']; f(); })()")
        VN = "document.getElementById('vn').dataset.on ? document.getElementById('vnName').textContent + ': ' + document.getElementById('vnText').textContent : ''"
        said = []; shot = set(); n = 0
        async def snap(name, clean=False):
            await asyncio.sleep(1.6)
            if clean: await ev("document.body.classList.add('__clean')"); await ev("(()=>{ if(!document.getElementById('__cs')){ const s = document.createElement('style'); s.id = '__cs'; s.textContent = 'body.__clean #vn, body.__clean #choiceDlg, body.__clean #voidVn{visibility:hidden!important}'; document.head.appendChild(s); } })()")
            await pg.screenshot(path=os.path.join(OUT, name)); print('shot', name)
            if clean: await ev("document.body.classList.remove('__clean')")
        for i in range(1400):
            if await ev("!!document.getElementById('missionCard') && !!document.getElementById('missionCard').dataset.on"):
                await asyncio.sleep(.8); await pg.keyboard.press('Space'); await asyncio.sleep(.6); continue
            st = await ev("__cave().room ? __cave().room.focus : -1")
            c = await ev("__choice()")
            if c:
                if ('c', st) not in shot: shot.add(('c', st)); await snap(f'choice_{st}.png'); await snap(f'mural_{st}_clean.png', True)
                ok = await ev(f"__choiceOk({json.dumps(c['q'], ensure_ascii=False)})"); await pg.keyboard.press(f'Digit{ok + 1}'); await asyncio.sleep(.5); continue
            t = await ev(VN)
            if t:
                if not said or said[-1] != t: said.append(t); n += 1
                if ('m', st) not in shot and st >= 0 and '보이드' not in t[:4]: shot.add(('m', st)); await snap(f'say_{st}.png')
                if 'NATY' not in shot and '네이티! 왜 그래' in t: shot.add('NATY'); await snap('mouth_shake.png')
                if 'MOUTH' not in shot and '또 너희냐' in t: shot.add('MOUTH'); await snap('mouth_found.png')
                await ev('__dbg.quest().next()'); await asyncio.sleep(.15); continue
            if await ev("!!window.__dbg && __dbg.restoreState && __dbg.restoreState() && __dbg.restoreState().on"): break
            if any('일루아를 돌려주겠다' in x for x in said[-2:]): break
            await asyncio.sleep(.3)
        print('\n'.join(said)); print('errs', errs[:3]); await br.close()
asyncio.run(main())
