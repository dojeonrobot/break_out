# 2026-11-18: 조작 안내 카드와 같은 날 고친 것들을 학생 기기에서 확인한다.
#  A 노트북(1366x768): 자일로를 처음 찾아가는 구간에서 카드가 뜨는지, 떠 있는 동안 W로 못 걷는지, Space로 닫히는지, 「?」로 다시 열리는지, 두 번째 걷기에는 안 뜨는지
#    + 대사 「이전」에 포커스를 두고 Enter → 앞 대사로 가는지
#  B 태블릿(1280x800, 터치): 태블릿용 카드(화면 그림 + 조이스틱 자리), 「알겠어요」 탭으로 닫힘
#  C 미로 안에서 저장한 뒤 다시 열면 이어하기 카드 문장
#  D 폰(390x844): 알림과 보이드 버튼이 겹치지 않는지, 기록 패널을 펼쳤을 때 제출 버튼이 보이는지
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_check_ctrl_card.py <그림 폴더>
import asyncio, json, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); B = 'http://127.0.0.1:8096'; H = {'content-type': 'application/json'}; ADM = {**H, 'X-Admin-Key': '0101'}
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']; res = []
def ok(name, cond, note=''): res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(note) if note != '' else ''))
async def ready(pg):
    for _ in range(480):
        try:
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): return
        except Exception: pass
        await asyncio.sleep(.25)
async def open_team(br, T, dev, zones, done, act, extra='', **ctxkw):
    ctx = await br.new_context(**ctxkw); rq = ctx.request
    await rq.post(B + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers=ADM)
    await rq.post(B + '/api/void/quest', data=json.dumps({'team': T, 'dev': dev, 'tut': True}), headers=H)
    await rq.post(B + '/api/void/admin/stage', data=json.dumps({'team': T, 'zones': zones, 'done': done, 'act': act}), headers=ADM)
    await ctx.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','%s');localStorage.setItem('void-card-test','1');%s" % (dev, extra))
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'{B}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000); await ready(pg); await asyncio.sleep(8); return ctx, pg, errs
ON = "(id=> !!document.getElementById(id) && !!document.getElementById(id).dataset.on)"
async def to_ctrl(pg):   # 섬으로 가서 걷기 시작, 대사·미션 카드는 학생처럼 넘기고 조작 안내 카드가 뜰 때까지
    await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3); await pg.evaluate("__dbg.startWalk('리코·제로')")
    for _ in range(60):
        await asyncio.sleep(.5)
        if await pg.evaluate(ON + "('ctrlCard')"): return True
        if await pg.evaluate("document.querySelectorAll('#vn[data-on],#voidVn[data-on],#heroPick[data-on]').length"): await pg.keyboard.press('Space')
    return False
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU)
        # ---- A 노트북
        ctx, pg, errs = await open_team(br, 10, 'cka', ['z1'], [], 1, viewport={'width': 1366, 'height': 768})
        ok('A 노트북: 자일로 찾아가는 구간에서 조작 안내 카드', await to_ctrl(pg)); await asyncio.sleep(1); await pg.screenshot(path=f'{OUT}/A_laptop_card.jpg', type='jpeg', quality=85)
        box = await pg.evaluate("(()=>{ const r = document.querySelector('#ctrlCard .in').getBoundingClientRect(), g = document.getElementById('ccGo').getBoundingClientRect(), k = document.querySelector('#ctrlCard .kb').getBoundingClientRect(); return {in:[r.top, r.bottom, r.left, r.right], go:[g.top, g.bottom], kb:[k.left, k.right], hi:[...document.querySelectorAll('#ctrlCard .k.walk')].map(e=> e.textContent).join(''), run:[...document.querySelectorAll('#ctrlCard .k.run')].map(e=> e.textContent).join(''), W:innerWidth, H:innerHeight}; })()")
        ok('A 카드·버튼이 화면 안', box['in'][0] >= 0 and box['go'][1] <= box['H'] and box['kb'][0] >= box['in'][2] and box['kb'][1] <= box['in'][3], box)
        ok('A 표시된 키 = W A S D + 방향키, Shift', set(box['hi']) == set('WASD◀▶▲▼') and box['run'] == 'Shift', (box['hi'], box['run']))
        p0 = await pg.evaluate("(()=>{ const w = __dbg.walk(); return [w.x, w.z]; })()"); await pg.keyboard.down('KeyW'); await asyncio.sleep(1.2); await pg.keyboard.up('KeyW'); p1 = await pg.evaluate("(()=>{ const w = __dbg.walk(); return [w.x, w.z]; })()")
        ok('A 카드가 떠 있는 동안 걷지 못함', p0 == p1, (p0, p1))
        await pg.keyboard.press('Space'); await asyncio.sleep(.6); ok('A Space로 닫힘', not await pg.evaluate(ON + "('ctrlCard')"))
        await pg.keyboard.down('KeyW'); await asyncio.sleep(1.2); await pg.keyboard.up('KeyW'); p2 = await pg.evaluate("(()=>{ const w = __dbg.walk(); return [w.x, w.z]; })()"); ok('A 닫은 뒤 W로 걸음', p2 != p1, (p1, p2))
        await pg.click('#walkHelp'); await asyncio.sleep(.8); ok('A 「?」로 다시 열림', await pg.evaluate(ON + "('ctrlCard')")); await asyncio.sleep(.4); await pg.keyboard.press('Enter'); await asyncio.sleep(.5); ok('A Enter로 닫힘', not await pg.evaluate(ON + "('ctrlCard')"))
        # 대사 「이전」 + Enter
        await pg.evaluate("__dbg.say([{who:'제로', text:'첫째 줄.'}, {who:'리코', text:'둘째 줄.'}, {who:'제로', text:'셋째 줄.'}])"); await asyncio.sleep(.6); await pg.keyboard.press('Space'); await asyncio.sleep(.2); await pg.keyboard.press('Space'); await asyncio.sleep(.8)
        t2 = await pg.evaluate("document.getElementById('vnText').textContent"); await pg.focus('#vnPrev'); await pg.keyboard.press('Enter'); await asyncio.sleep(.8); t1 = await pg.evaluate("document.getElementById('vnText').textContent")
        ok('A 대사 「이전」에 포커스 + Enter → 앞 대사', ('둘째' in t2 and '첫째' in t1) or ('셋째' in t2 and '둘째' in t1), (t2, t1))
        await pg.click('#vnPrev', force=True) if False else None
        for _ in range(8): await pg.keyboard.press('Space'); await asyncio.sleep(.25)
        ok('A Space로 끝까지 넘어감', not await pg.evaluate(ON + "('vn')"))
        await pg.evaluate("__dbg.stopWalk()"); await asyncio.sleep(1); await pg.evaluate("__dbg.startWalk('리코·제로')"); again = False
        for _ in range(12):
            await asyncio.sleep(.5); again = again or await pg.evaluate(ON + "('ctrlCard')")
            if await pg.evaluate("document.querySelectorAll('#vn[data-on],#voidVn[data-on]').length"): await pg.keyboard.press('Space')
        ok('A 두 번째 걷기에는 다시 뜨지 않음', not again); ok('A 페이지 오류 없음', not errs, errs[:2]); await ctx.close()
        # ---- B 태블릿
        ctx, pg, errs = await open_team(br, 9, 'ckb', ['z1'], [], 1, viewport={'width': 1280, 'height': 800}, has_touch=True, is_mobile=True, user_agent='Mozilla/5.0 (Linux; Android 14; SM-X516B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36')
        coarse = await pg.evaluate("matchMedia('(pointer:coarse)').matches"); shown = await to_ctrl(pg); await asyncio.sleep(1.2); await pg.screenshot(path=f'{OUT}/B_tablet_card.jpg', type='jpeg', quality=85)
        tb = await pg.evaluate("(()=>{ const t = document.querySelector('#ctrlCard .tab'), g = document.getElementById('ccGo'); if(!t) return null; const r = t.getBoundingClientRect(), b = g.getBoundingClientRect(); return {tab:[r.width, r.height], go:[b.top, b.bottom, b.height], H:innerHeight, kb:!!document.querySelector('#ctrlCard .kb'), bg:getComputedStyle(t).backgroundImage.slice(0, 60)}; })()")
        ok('B 태블릿: 터치 기기로 인식 + 카드 뜸', coarse and shown, coarse); ok('B 태블릿용 그림(키보드 아님), 버튼 화면 안·44px 이상', bool(tb) and not tb['kb'] and tb['go'][1] <= tb['H'] and tb['go'][2] >= 44, tb)
        await asyncio.sleep(.3); await pg.tap('#ccGo'); await asyncio.sleep(.6); ok('B 「알겠어요」 탭으로 닫힘', not await pg.evaluate(ON + "('ctrlCard')")); ok('B 페이지 오류 없음', not errs, errs[:2]); await ctx.close()
        # ---- C 미로 이어하기 카드
        ctx, pg, errs = await open_team(br, 8, 'ckc', ['z1'], ['q1'], 1, extra="localStorage.setItem('void-mini-8', JSON.stringify({q:'q2', step:'maze', pos:[155, 380, 0]}));", viewport={'width': 1280, 'height': 800})
        txt = ''
        for _ in range(40):
            await asyncio.sleep(.5); txt = await pg.evaluate("(()=>{ const e = document.getElementById('missionCard'); return e && e.dataset.on ? e.innerText.replace(/\\s+/g, ' ') : ''; })()")
            if txt: break
            if await pg.evaluate("document.querySelectorAll('#voidVn[data-on],#recDone[data-on]').length"): await pg.keyboard.press('Space')
        await pg.screenshot(path=f'{OUT}/C_maze_resume.jpg', type='jpeg', quality=85); ok('C 미로 안에서 이어하기 카드가 미로를 말함', '미로' in txt and '정문 동쪽 길' not in txt, txt); await ctx.close()
        # ---- D 폰
        ctx, pg, errs = await open_team(br, 7, 'ckd', [], [], 0, viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
        await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1.5)
        d = await pg.evaluate("(()=>{ const p = document.getElementById('panel'); if(p.classList.contains('closed')) document.getElementById('toggle').click(); return 1; })()"); await asyncio.sleep(1)
        await pg.evaluate("(()=>{ const t = document.getElementById('toast'); t.textContent = '위치 사용이 꺼져 있습니다'; t.classList.add('on'); })()"); await asyncio.sleep(.5); await pg.screenshot(path=f'{OUT}/D_phone.jpg', type='jpeg', quality=85)
        ph = await pg.evaluate("(()=>{ const R = e=>{ if(!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; }; const p = document.getElementById('panel'), sc = p.querySelector('.scroll'), sb = p.querySelector('.cardsub button[type=submit]'), rb = document.getElementById('restoreBtn'); return {panel:R(p), scroll:R(sc), submit:R(sb), toast:R(document.getElementById('toast')), restore:rb && getComputedStyle(rb).display !== 'none' ? R(rb) : null, aux:document.body.className}; })()")
        print('   ', ph)
        if ph['submit'] and ph['scroll']: ok('D 폰: 패널을 펼치면 스캔 제출 버튼이 보임(스크롤 없이)', ph['submit'][3] <= ph['scroll'][3] and ph['submit'][1] >= ph['scroll'][1], (ph['submit'], ph['scroll']))
        else: ok('D 폰: 스캔 입력 카드가 있음', False, ph)
        if ph['restore']: ok('D 폰: 알림이 보이드 버튼과 겹치지 않음', ph['toast'][3] <= ph['restore'][1] or ph['toast'][1] >= ph['restore'][3] or ph['toast'][0] >= ph['restore'][2], (ph['toast'], ph['restore']))
        else: print('    보이드 버튼이 이 상태에서는 안 보임: 알림 위치만 기록', ph['toast'])
        ok('D 알림이 패널 아래', ph['toast'][1] >= ph['panel'][3], (ph['toast'], ph['panel'])); await ctx.close(); await br.close()
    bad = [n for n, c in res if not c]; print('\nFAIL', len(bad), '/', len(res), bad)
asyncio.run(main())
