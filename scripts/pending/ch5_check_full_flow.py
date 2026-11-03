# mission checkpoints + building block, end to end on team 10 (child device): leave mid-mission in several ways, reload, resume via the pill
import asyncio, json, sys, re, os, base64
from playwright.async_api import async_playwright
TEAM = 10
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'
HERE = os.path.dirname(os.path.abspath(__file__)); SHOT = os.path.join(HERE, 'shots_resume'); os.makedirs(SHOT, exist_ok=True)
errs = []; fails = []
def say(*a): print(*a, flush=True)
def check(cond, msg):
    say(('OK   ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1280, 'height':800})
        async def route(r):
            req = r.request; url = req.url.replace(STATIC, API)
            try:
                resp = await ctx.request.fetch(url, method=req.method, headers={k:v for k, v in req.headers.items() if k.lower() not in ('host', 'origin', 'referer')}, data=req.post_data_buffer)
                await r.fulfill(status=resp.status, headers={'content-type': resp.headers.get('content-type', 'application/json')}, body=await resp.body())
            except Exception as e: await r.fulfill(status=500, body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team':TEAM, 'confirm':'AGAIN'}), headers={'content-type':'application/json', 'X-Admin-Key':'0101'})
        pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text[:120]) if m.type == 'error' and '404' not in m.text else None)
        async def load():
            await pg.goto(f'{STATIC}/chapter05/index.html?team={TEAM}', wait_until='domcontentloaded')
            for i in range(80):
                if await pg.evaluate("typeof window.__dbg !== 'undefined' && !!window.__dbg.miniCp"): break
                await asyncio.sleep(0.5)
            for i in range(40):
                if not await pg.evaluate("document.body.classList.contains('intro')"): break
                await asyncio.sleep(0.5)
            await asyncio.sleep(1.5)
        await load(); ev = pg.evaluate
        cdp = await ctx.new_cdp_session(pg)
        async def shot(n):
            r = await cdp.send('Page.captureScreenshot', {'format':'png'}); open(os.path.join(SHOT, n + '.png'), 'wb').write(base64.b64decode(r['data']))
        async def st(): return await ev("({w:__dbg.simState(), tut:__dbg.tutState().step, world:__dbg.tutState().world, vn:!!document.getElementById('vn').dataset.on, voidOn:!!document.getElementById('voidVn').dataset.on, voidTxt:document.getElementById('voidTxt').textContent.slice(0,30), rec:!!document.getElementById('recDone').dataset.on, qr:!!document.getElementById('qReward').dataset.on, yard:!!document.getElementById('yardDlg').dataset.on, lab:!!document.getElementById('labDlg').dataset.on, cave:!!document.getElementById('caveDlg').dataset.on, sim:!!document.getElementById('simDone').dataset.on, cinema:!document.getElementById('cinema').hidden, walk:__dbg.walkState(), qd:__dbg.qdone(), mini:__dbg.mini(), cp:__dbg.miniCp(), pill:!document.getElementById('questPill').hidden, pillT:document.getElementById('questPill').textContent})")
        async def space(n=1, gap=0.5):
            for i in range(n): await pg.keyboard.press('Space'); await asyncio.sleep(gap)
        async def drain(label, max_n=40, stop=None):
            for i in range(max_n):
                s = await st()
                if stop and stop(s): return s
                if s['vn'] or s['voidOn'] or s['rec'] or s['qr']: await space(1, 0.45)
                else: await asyncio.sleep(0.5)
            return await st()
        async def dclick(sel): await ev(f"document.querySelector({json.dumps(sel)}).click()")
        async def submit(z, scan):
            r = await ctx.request.post(API + '/api/void/submit', data=json.dumps({'team':TEAM, 'dev':'a', 'mission':z, 'scanId':scan}), headers={'content-type':'application/json'}); say('submit', z, r.status)
        async def resume_via_pill(tag):
            s = await drain('pill ' + tag, 20, lambda s: s['pill'])
            check(s['pill'], f'{tag}: pill shown ({s["pillT"]})'); check('이어하기' in s['pillT'], f'{tag}: pill says 이어하기')
            await dclick('#questPill'); await asyncio.sleep(1.8); s = await st()
            check(bool(s['walk']), f'{tag}: walking again'); return s

        # ---- the building grid ----
        g = await ev("(()=>{ const t0 = performance.now(); const g = __dbg.walkGrid(); return {ms:Math.round(performance.now()-t0), W:g.W, H:g.H, n:g.a.length}; })()"); say('grid', g)
        blocked_centers = await ev("""['대강당','스위트 스쿱','4D 시네마 돔','직원 숙소','등대','츄러스 하우스','범죄수사과 본부'].map(n=>{ const b = __dbg.IB.find(x=> x.label === n); return [n, b ? __dbg.walkBlocked(b.cx, b.cz) : null]; })""")
        say('building centres blocked', blocked_centers); check(all(v for _, v in blocked_centers), 'every building centre is blocked')
        open_spots = await ev("""[['분수 광장 가장자리', 12, 174], ['포시즌스 가든', 0, 369], ['정문 길', 0, 405], ['메인 스트리트 길', 0, 258]].map(([n, x, z])=> [n, __dbg.walkBlocked(x, z)])""")
        say('open spots', open_spots); check(not any(v for _, v in open_spots), 'plazas and the gate road stay free')
        pb = await ev("(()=>{ let n = 0; __dbg.pathSamples.forEach(([x, z])=>{ if(__dbg.walkBlocked(x, z)) n++; }); return [n, __dbg.pathSamples.length]; })()"); say('path samples blocked', pb); pgb = await ev("(()=>{ const g = __dbg.walkGrid(); let n = 0; __dbg.pathSamples.forEach(([x, z])=>{ const ix = Math.floor(x) - g.X0, iz = Math.floor(z) - g.Z0; if(g.a[iz*g.W + ix] === 1) n++; }); return n; })()"); say('grid-only path blocked', pgb); check(pgb == 0, 'the grid blocks no path sample')

        # ---- act 1 → mission 1 ----
        await ev("window.__dbg.tutEnd()"); await asyncio.sleep(1.5)
        await submit('z1', 'r1608968abcdefgh')
        s = await drain('act1', 90, lambda s: s['walk'] is not None); check(bool(s['walk']), 'act 1 walk started')
        await drain('intro', 30, lambda s: not s['vn'])
        t = await ev("__dbg.target()"); await ev(f"__dbg.walkTo({t[0]}, {t[1]})"); await asyncio.sleep(1.2)
        s = await drain('found', 40, lambda s: not s['vn'] and s['cp'] and s['cp']['step'] == 'yard'); await asyncio.sleep(0.5); s = await st()
        check(s['cp'] and s['cp']['step'] == 'yard', f"checkpoint after finding 자일로: {s['cp'] and s['cp']['step']}")
        await drain('void after found', 10, lambda s: not s['voidOn'])
        # leave with 나가기
        await dclick('#walkX'); await asyncio.sleep(1.2); s = await st()
        check(s['walk'] is None, 'left the walk'); check('저장' in s['voidTxt'] or s['voidOn'], f"void tells how to come back ({s['voidTxt']})"); await shot('01_left_after_found')
        await drain('void', 6, lambda s: not s['voidOn'])
        s = await resume_via_pill('resume→yard'); check(s['mini'] and s['mini']['kind'] == 'loop' and s['mini']['phase'] == 'walk', f"resumed at yard walk: {s['mini']}")
        pos_ok = s['cp'] and s['walk'] and abs(s['walk']['x'] - s['cp']['pos'][0]) < 2; check(bool(pos_ok), 'resumed at the saved spot')
        d = await ev("__dbg.yardDoor()"); await ev(f"__dbg.walkTo({d[0]}, {d[1]})"); await asyncio.sleep(2.5)
        s = await st(); check(s['yard'], 'yard opened'); await drain('yard say', 10, lambda s: not s['vn'])
        await ev("(()=>{ const y = __dbg.yard(); y.tiles = y.sol.map(r=> r.map(c=> new Set(c))); __dbg.yardPaint(); })()"); await asyncio.sleep(2.2)
        s = await st(); check(s['cp'] and s['cp']['step'] == 'station', f"checkpoint after the board: {s['cp'] and s['cp']['step']}")
        # leave with Esc in the middle of the dialogue, then RELOAD the page
        await pg.keyboard.press('Escape'); await asyncio.sleep(0.8); s = await st(); check(s['walk'] is None, 'Esc left the walk mid-dialogue')
        await load(); s = await st(); check(s['cp'] and s['cp']['step'] == 'station', 'checkpoint survives a reload'); check(s['world'] == 'erica', 'page starts on the campus as always')
        # the campus tab is where we are; the island tab must still be the lock-free one (an open mission → island)
        await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2)
        s = await resume_via_pill('reload→station'); check(s['mini'] and s['mini']['phase'] == 'walk' and (await ev("__dbg.station().spot"))[0] == s['mini']['target'][0], 'walking to the station')
        sp = await ev("__dbg.station().spot"); await ev(f"__dbg.walkTo({sp[0]}, {sp[1]})"); await asyncio.sleep(2)
        s = await drain('board say', 30, lambda s: not s['vn'] and ev is not None)
        for i in range(30):
            if await ev("!!document.getElementById('rideDlg').dataset.on"): break
            if await ev("!!document.getElementById('vn').dataset.on"): await pg.keyboard.press('Space')
            await asyncio.sleep(0.5)
        gd = await ev("!!document.getElementById('rideDlg').dataset.on"); check(gd, 'ride guide shown before the lap')
        await pg.keyboard.press('Space'); await asyncio.sleep(0.8); await drain('go say', 20, lambda s: not s['vn']); await asyncio.sleep(1)
        r = await ev("!!__dbg.ride()"); check(r, 'ride started')
        await ev("(()=>{ const r = __dbg.ride(); r.press = true; r.boost = 14; })()")
        for i in range(80):
            await asyncio.sleep(3)
            rr = await ev("(()=>{ const r = __dbg.ride(); return r ? {u:r.u.toFixed(3), done:r.spots.map(s=> s.done ? 1 : 0).join(''), lap:r.lap, press:r.press} : null; })()")
            if rr is None: break
            if i % 5 == 0: say('ride', rr)
        say('ride over', rr)
        s = await drain('ride say', 12, lambda s: not s['vn'])
        s = await drain('exit q1', 200, lambda s: s['qr']); say('after q1', {k:s[k] for k in ('qr','qd','world','vn','voidOn','walk')}, s['w']); check(s['qr'] and 'q1' in s['qd'], 'mission 1 complete'); check(s['cp'] is None, 'checkpoint cleared on completion')
        await space(1, 1.0); await drain('back', 10, lambda s: not s['voidOn'])

        # ---- act 2 → mission 2 ----
        await submit('z2', 'r2608968abcdefgh')
        s = await drain('act2', 120, lambda s: s['walk'] is not None and 'q1' in s['qd']); check(bool(s['walk']), 'act 2 walk started')
        await drain('intro2', 30, lambda s: not s['vn'])
        nh = await ev("__dbg.natyHide()"); await ev(f"__dbg.walkTo({nh[0]}, {nh[1]})"); await asyncio.sleep(1.5)
        s = await drain('found naty', 40, lambda s: not s['vn'] and s['cp'] and s['cp']['step'] == 'record'); await asyncio.sleep(0.5)
        s = await st(); check(s['cp'] and s['cp']['step'] == 'record', f"checkpoint at the maze heart: {s['cp'] and s['cp']['step']} (Space closing the dialogue must not press 기록)")
        # a world switch (as the void would do) mid-mission
        await ev("__dbg.setWorld('erica', true)"); await asyncio.sleep(1.5); s = await st(); check(s['walk'] is None, 'world switch ended the walk')
        await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(1.5)
        s = await resume_via_pill('world-switch→record'); check(s['mini'] and s['mini']['phase'] == 'record', 'back at the record step')
        await pg.click('#miniGo'); await asyncio.sleep(0.8); await drain('record say', 10, lambda s: not s['vn'])
        s = await st(); check(s['cp'] and s['cp']['step'] == 'lab', 'checkpoint lab')
        ld = await ev("__dbg.labDoor()"); await ev(f"__dbg.walkTo({ld[0]}, {ld[1]})"); await asyncio.sleep(2.5)
        s = await st(); check(s['lab'], 'lab opened'); await drain('lab say', 10, lambda s: not s['vn'])
        await ev("document.querySelector('#lbMons .mon:nth-child(1) .play').click()"); await asyncio.sleep(0.6); await ev("__dbg.labWin()"); await asyncio.sleep(0.6)
        s = await st(); check(s['cp'] and s['cp'].get('lab') == ['snake'], f"one game saved: {s['cp'] and s['cp'].get('lab')}")
        await dclick('#walkX'); await asyncio.sleep(1.5); await drain('void', 6, lambda s: not s['voidOn'])
        s = await resume_via_pill('leave in lab→lab')
        ld = await ev("__dbg.labDoor()"); await ev(f"__dbg.walkTo({ld[0]}, {ld[1]})"); await asyncio.sleep(2.5)
        await drain('lab say 2', 10, lambda s: not s['vn'])
        ok1 = await ev("document.querySelectorAll('#lbMons .mon.ok').length"); check(ok1 == 1, f'lab reopened with the beaten game kept ({ok1})'); await shot('02_lab_resumed')
        for g in (2, 3):
            await ev(f"document.querySelector('#lbMons .mon:nth-child({g}) .play').click()"); await asyncio.sleep(0.6); await ev("__dbg.labWin()"); await asyncio.sleep(0.5)
        await asyncio.sleep(1); await drain('lab done say', 20, lambda s: not s['vn'])
        for i in range(20):
            if await ev("!document.getElementById('lbGo').hidden && !document.getElementById('vn').dataset.on"): break
            if await ev("!!document.getElementById('vn').dataset.on"): await pg.keyboard.press('Space')
            await asyncio.sleep(0.5)
        await dclick('#lbGo'); await drain('lab give', 12, lambda s: not s['vn'])
        s = await drain('exit q2', 200, lambda s: s['qr']); check(s['qr'] and 'q2' in s['qd'], 'mission 2 complete')
        await space(1, 1.0); await drain('back2', 10, lambda s: not s['voidOn'])

        # ---- act 3 → cave ----
        await submit('z3', 'r3608968abcdefgh')
        s = await drain('act3', 110, lambda s: s['walk'] is not None)
        if not s['walk']: await ev("__dbg.startWalk('리코·제로')"); await asyncio.sleep(1.5); s = await st()
        check(bool(s['walk']), 'act 3 walk started'); await drain('intro3', 30, lambda s: not s['vn'])
        cm = await ev("__dbg.quest().CAVE_MOUTH"); await ev(f"__dbg.walkTo({cm[0]}, {cm[1]})"); await asyncio.sleep(1.5)
        s = await drain('found codex', 40, lambda s: s['cave']); check(s['cave'], 'cave opened'); qt = await ev("getComputedStyle(document.getElementById('qTmp')).display"); check(qt == 'none', f'임시 완료 button hidden on a child device ({qt})'); await drain('cave say', 12, lambda s: not s['vn'])
        for gid in ['forest', 'valley', 'shore', 'cave', 'water', 'plaza']:
            await dclick(f'#cvTiles [data-g="{gid}"]'); await dclick(f'#cvMap .slot[data-s="{gid}"]'); await asyncio.sleep(0.3)
        await asyncio.sleep(0.8); s = await st(); check(s['cp'] and s['cp'].get('decoded'), 'decoded wall saved')
        await drain('decoded say', 20, lambda s: not s['vn'])
        for i in range(20):
            if await ev("!document.getElementById('cvNext').hidden && !document.getElementById('vn').dataset.on"): break
            if await ev("!!document.getElementById('vn').dataset.on"): await pg.keyboard.press('Space')
            await asyncio.sleep(0.5)
        await dclick('#walkX'); await asyncio.sleep(1.5); await drain('void', 6, lambda s: not s['voidOn'])
        s = await resume_via_pill('leave in cave→cave'); await asyncio.sleep(2.5); await drain('cave resume say', 8, lambda s: not s['vn'])
        ph = await ev("document.getElementById('cvTest').hidden"); check(ph is False, 'cave reopened straight at the test'); await shot('03_cave_resumed')
        await dclick('#cvTest [data-set="dev"] [data-v="off"]'); await dclick('#cvTest [data-set="amt"] [data-v="small"]')
        for k in ['forest', 'valley', 'shore']: await dclick(f'#cvTest [data-set="ord"] [data-v="{k}"]')
        say('cave before go', await ev("({phase:typeof caveS, go:document.getElementById('cvGo').disabled, test:!document.getElementById('cvTest').hidden, picks:[...document.querySelectorAll('#cvTest .pick')].length, vn:!!document.getElementById('vn').dataset.on})"))
        await dclick('#cvGo')
        await pg.wait_for_function("__dbg.caveS()?.phase === 'won' && !document.getElementById('cvNext').hidden", timeout=30000)
        say('cave after go', await ev("({next:!document.getElementById('cvNext').hidden, nextT:document.getElementById('cvNext').textContent, log:[...document.querySelectorAll('#cvLog li')].map(l=> l.textContent).slice(0,2), vn:!!document.getElementById('vn').dataset.on})"))
        await dclick('#cvNext'); await drain('cave end say', 12, lambda s: not s['vn'])
        s = await drain('ending', 120, lambda s: s['sim'] or s['cinema']); check(s['sim'] or s['cinema'], 'ending reached'); check(s['cp'] is None, 'checkpoint cleared at the end')
        say('errors', errs); check(not errs, 'no page errors')
        say('FAILS', fails)
        await b.close()
        assert not fails, fails
asyncio.run(main())
