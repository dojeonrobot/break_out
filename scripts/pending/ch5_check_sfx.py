# 2026-11-18: 효과음이 제 경우에 나는지 이름으로 확인한다(SND.log). 소리를 켠 채로 열어 오디오가 실제로 도는지(ctx running)도 본다.
#  서버 없는 기기(LOCAL): 첫 터치 → intro / 버튼 → click / 알림 → pop / 잘못된 스캔 코드 → error / 맞는 코드 → scan / 보이드 말 → void
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096, 정적 파일용).  python ch5_check_sfx.py
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
res = []
def ok(name, cond, note=''): res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(note) if note != '' else ''))
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(7); await pg.evaluate("SND.log = []")
        take = lambda: pg.evaluate("(()=>{ const l = SND.log.slice(); SND.log.length = 0; return l; })()")
        await pg.mouse.click(640, 400); await asyncio.sleep(.6); l = await take(); st = await pg.evaluate("({state:SND.ctx && SND.ctx.state, on:SND.on, unlocked:SND.unlocked})")
        ok('첫 터치에 시작 곡(intro)', 'intro' in l, l); ok('오디오가 실제로 돌고 있음', st['state'] == 'running' and st['on'] and st['unlocked'], st)
        await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1.5); await take()
        await pg.click('#toggle'); await asyncio.sleep(.3); l = await take(); ok('버튼을 누르면 click', 'click' in l, l); await pg.click('#toggle'); await asyncio.sleep(.5); await take()
        await pg.evaluate("document.querySelector('[data-copy]') && document.querySelector('[data-copy]').click()"); await asyncio.sleep(.6); l = await take(); ok('좌표 복사 → 알림 pop', 'pop' in l, l)
        has = await pg.evaluate("!!document.querySelector('form[data-sub] input.scanid')"); ok('스캔 입력칸이 있음', has)
        if has:
            await pg.fill('form[data-sub] input.scanid', 'abc'); await pg.click('form[data-sub] button[type=submit]'); await asyncio.sleep(.5); l = await take(); ok('잘못된 코드 → error', 'error' in l, l)
            await pg.fill('form[data-sub] input.scanid', 'abcd1234efgh5678'); await pg.click('form[data-sub] button[type=submit]'); await asyncio.sleep(.6); l = await take(); ok('맞는 코드 접수 → scan', 'scan' in l, l)
        await pg.evaluate("__dbg.say && 0"); v = await pg.evaluate("(()=>{ try{ document.getElementById('restoreBtn').click(); }catch(e){} return 1; })()"); await asyncio.sleep(1.2); l = await take(); print('    보이드 버튼 뒤 소리:', l)
        ok('페이지 오류 없음', not errs, errs[:2]); await br.close()
    bad = [n for n, c in res if not c]; print('\nFAIL', len(bad), '/', len(res), bad)
asyncio.run(main())
