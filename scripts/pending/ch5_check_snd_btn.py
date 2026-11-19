# 2026-11-19: 소리 버튼이 어느 화면에서나 보이고 눌리는지(맨 위에 있는지) 확인한다: 캠퍼스·섬·걷기·대사 중·연구실 게임 창·미션 카드·관리자.
#  각 화면에서 버튼 한가운데의 맨 위 요소가 버튼인지(elementFromPoint), 누르면 꺼지고 다시 누르면 켜지는지 본다. 그림도 남긴다.  정적 서버 8097.
#  python ch5_check_snd_btn.py <그림 폴더>
import asyncio, sys, pathlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); res = []
def ok(name, cond, note=''): res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(note) if note != '' else ''))
HOOK = "\n;window.__go = n=>{ walkerOpen = ()=> true; startWalk(n); return !!walk; }; window.__pair = ()=> PAIR; window.__say = l=> say(l); window.__slice = ()=>{ sliceDlg().dataset.on = '1'; }; window.__sliceOff = ()=>{ delete sliceDlg().dataset.on; }; window.__card = ()=>{ try{ missionCard(QUESTS[0]); }catch(e){ return String(e); } return 1; };\n"
TOP = "(()=>{ const b = document.getElementById('sndBtn'), r = b.getBoundingClientRect(); if(!r.width) return {vis:false}; const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return {vis:true, top:!!e && (e === b || b.contains(e)), x:Math.round(r.left), y:Math.round(r.top), over:e ? (e.id || e.className || e.tagName) : null}; })()"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for dev, vp in (('pc', {'width': 1280, 'height': 800}), ('tab', {'width': 800, 'height': 1280}), ('tabland', {'width': 1280, 'height': 720})):
            pg = await br.new_page(viewport=vp); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
            src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
            await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
            await pg.add_init_script("localStorage.setItem('void-card-test','1');")
            await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=1', wait_until='domcontentloaded', timeout=120000)
            for _ in range(480):
                try:
                    if await pg.evaluate("typeof window.__go === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
                except Exception: pass
                await asyncio.sleep(.25)
            await asyncio.sleep(7)
            await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1.5)
            async def stage(name):
                await asyncio.sleep(.8); t = await pg.evaluate(TOP); ok(f'{dev} {name}: 보이고 맨 위', t.get('vis') and t.get('top'), t); await pg.screenshot(path=f'{OUT}/snd_{dev}_{name}.png')
            await stage('campus')
            a = await pg.evaluate("SND.on"); await pg.click('#sndBtn'); b = await pg.evaluate("SND.on"); await pg.click('#sndBtn'); c = await pg.evaluate("SND.on"); ok(f'{dev} 누르면 꺼지고 다시 켜짐', a and not b and c, [a, b, c])
            await pg.evaluate("__dbg.setWorld('island')"); await asyncio.sleep(3); await stage('island')
            await pg.evaluate("__go(__pair())"); await asyncio.sleep(2); await stage('walk')
            await pg.evaluate("__say([{who:'제로', text:'소리 버튼 확인용 대사야. 조금 길게 써 둘게.'}])"); await stage('dialogue'); await pg.keyboard.press('Space'); await asyncio.sleep(.3); await pg.keyboard.press('Space'); await asyncio.sleep(.5)
            await pg.evaluate("__card()"); await stage('card'); await asyncio.sleep(.8); await pg.keyboard.press('Space'); await asyncio.sleep(.6)
            await pg.evaluate("__slice()"); await stage('game'); await pg.evaluate("__sliceOff()")
            print(dev, 'errors:', errs[:2]); await pg.close()
        await br.close()
    bad = [n for n, c in res if not c]; print('\nFAIL', len(bad), '/', len(res), bad)
asyncio.run(main())
