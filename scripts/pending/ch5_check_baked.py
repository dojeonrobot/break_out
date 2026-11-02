import asyncio, json
from playwright.async_api import async_playwright
STEPS = [
 ('기본 상태에서 10초', "()=>{}"),
 ('스카이 루프 운행', "()=>{ const T = __dbg.train(); T.mode = 'run'; T.lit = true; }"),
 ('미션 전부 끝 + 복구 미리보기', "()=>{ try{ __dbg.setDemo(__dbg.IB.filter(b=> b.c !== 'char').map(b=> 'x'), true); }catch(e){} }"),
 ('시뮬레이터 켬', "()=> __dbg.setSim(true)"),
 ('시뮬레이터 끔', "()=> __dbg.setSim(false)"),
 ('밤 20시', "()=>{ const h = document.getElementById('hr'); h.value = 20; h.dispatchEvent(new Event('input')); }"),
 ('2분 더 흐름(여객선 한 주기)', "()=>{}"),
 ('아침 7시', "()=>{ const h = document.getElementById('hr'); h.value = 7; h.dispatchEvent(new Event('input')); }"),
]
async def run():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = await br.new_context(viewport={'width':1152,'height':720}); await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load'); await pg.wait_for_timeout(9000)
        print('baked pieces', await pg.evaluate("__dbg.bakedAudit ? 'ok' : 'none'"))
        seen = set()
        for name, js in STEPS:
            await pg.evaluate(js); await pg.wait_for_timeout(10000 if name.startswith('기본') else 125000 if name.startswith('2분') else 4000)
            r = await pg.evaluate("__dbg.bakedAudit()")
            new = [x for x in r if x[0] not in seen]
            for x in r: seen.add(x[0])
            print(f'== {name}: 새로 걸린 것 {len(new)}')
            for x in new[:25]: print('  ', x)
        print('errs', errs[:2]); await br.close()
asyncio.run(run())
