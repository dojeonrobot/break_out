# 2026-11-19: ① 걷는 중 Space = 점프(높이가 올랐다가 0으로) ② 걷는 중 화면을 눌러도 아무것도 선택되지 않음 ③ 걷지 않을 때는 전처럼 선택됨
#  ④ 섬 시작 시간 12시 ⑤ 대사 글자 소리·보이드 등장음이 실제로 남(SND.log)  ⑥ 페이지 오류 없음.   정적 서버 8097.  python ch5_check_1119.py
import asyncio, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; res = []
def ok(name, cond, note=''): res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(note) if note != '' else ''))
HOOK = "\n;window.__w = ()=> walk ? {jy:walk.jy || 0, jv:walk.jv, x:walk.x, z:walk.z, cy:camera.position.y} : null; window.__sel = ()=> selected; window.__go = n=>{ try{ walkerOpen = ()=> true; startWalk(n); }catch(e){ return String(e); } return !!walk; }; window.__say = (l)=> say(l); window.__vs = t=> voidShow(t); window.__vh = ()=> voidHide(); window.__pair = ()=> PAIR; window.__info = ()=> !document.getElementById('info').classList.contains('off');\n"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&team=1&admin=0', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__w === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        ok('섬 시작 시간 12시 근처', abs(float(await pg.evaluate("document.getElementById('hr').value")) - 12) < 0.6, await pg.evaluate("document.getElementById('hr').value"))
        await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()"); await asyncio.sleep(1.5)
        # 걷지 않을 때 화면 누르면 선택됨(가운데 하모니아 쪽)
        hit = -1; await pg.evaluate("(()=>{ try{ __dbg.setWorld('island'); }catch(e){} })()"); await asyncio.sleep(4)
        for (x, y) in [(a, b) for b in range(260, 620, 40) for a in range(380, 940, 40)]:
            await pg.mouse.click(x, y); await asyncio.sleep(.4); hit = await pg.evaluate("__sel()")
            if hit >= 0: break
        ok('걷지 않을 때는 화면을 누르면 선택됨', hit >= 0, hit); await pg.keyboard.press('Escape'); await asyncio.sleep(.3)
        await pg.evaluate("SND.log = []")
        r = await pg.evaluate("(()=>{ try{ __dbg.startWalk(); }catch(e){} return !!__w() || __go(__pair()); })()"); await asyncio.sleep(1.5)
        w0 = await pg.evaluate("__w()"); ok('걷기 시작', w0 is not None, r)
        if w0:
            for (x, y) in ((640, 400), (600, 380), (680, 420), (640, 340), (400, 420), (900, 380)):
                await pg.mouse.click(x, y); await asyncio.sleep(.25)
            ok('걷는 중 화면을 눌러도 선택 없음', (await pg.evaluate("__sel()")) < 0 and not await pg.evaluate("__info()"), await pg.evaluate("[__sel(), __info()]"))
            await pg.keyboard.press('Space'); hs = []
            for _ in range(14): await asyncio.sleep(.06); hs.append((await pg.evaluate("__w()"))['jy'])
            await asyncio.sleep(.6); end = await pg.evaluate("__w()")
            ok('Space로 뜀(가장 높이 %.2f m)' % max(hs), max(hs) > 0.7, [round(h, 2) for h in hs]); ok('다시 땅에 내려옴', end['jy'] == 0 and end['jv'] is None, end)
            lg = await pg.evaluate("SND.log.slice()"); ok('점프·착지 소리', 'jump' in lg and 'land' in lg, lg)
            # 대사 중 Space는 대사를 넘기고 뛰지 않는다
            await pg.evaluate("__say([{who:'제로', text:'점프 시험 대사 첫째 줄이야. 조금 길게 써 둘게.'}, {who:'리코', text:'둘째 줄.'}])"); await asyncio.sleep(.25)
            await pg.keyboard.press('Space'); await asyncio.sleep(.15); j = await pg.evaluate("__w()"); ok('대사 중 Space는 뛰지 않음', (j['jy'] or 0) == 0 and j['jv'] is None, j)
            for _ in range(4): await pg.keyboard.press('Space'); await asyncio.sleep(.4)
        await pg.evaluate("__vh(); SND.log = []; window.__n = {type:0, vtype:0}; const o = window.sfx; ")
        print('errors:', errs[:3]); ok('페이지 오류 없음', not errs, errs[:2]); await br.close()
    bad = [n for n, c in res if not c]; print('\nFAIL', len(bad), '/', len(res), bad)
asyncio.run(main())
