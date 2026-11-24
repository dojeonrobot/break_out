# 구역 복귀 연출(arriveShow)을 시간 순으로 찍는다. 기본은 기록 1 직후(정전, 하모니아).
#  python -X utf8 scripts/pending/ch5_with_servers.py scripts/pending/ch5_shot_arrive_fx.py <그림 폴더> [구역 라벨=하모니아] [power=0|1]
import asyncio, sys, os, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); LABEL = sys.argv[2] if len(sys.argv) > 2 else '하모니아'; POWER = (sys.argv[3] if len(sys.argv) > 3 else '0') == '1'
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1280, 'height': 800})
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8').replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await ev("typeof window.__dbg!=='undefined' && !!window.__t && !!__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        await ev("(()=>{ for(const id of ['teamPick','intro']){ const e = document.getElementById(id); if(e){ e.style.display='none'; delete e.dataset.on; } } })()")
        await ev("__dbg.setWorld('island', true)"); await asyncio.sleep(2)
        info = await ev(f"""(()=>{{ const t = __t, m = t['MI'].find(x=> x.name === {json.dumps(LABEL)} || (x.b && x.b.label === {json.dumps(LABEL)})); if(!m) return {{err:'no zone', names:t['MI'].map(x=> x.name)}};
           {'t["PARK_ON"] = true; t["PARK_HOLD"] = false;' if POWER else ''} return {{id:m.id, name:m.name, power:t['parkPowerOn']()}}; }})()""")
        print('zone', info)
        if 'id' not in info: await br.close(); return
        await ev(f"(()=>{{ __t['arriveShow']({json.dumps(info['id'])}); }})()")
        t = 0
        for k in range(26):
            await asyncio.sleep(.6); t += .6
            st = await ev("(()=>{ const R = __dbg.rideState(); return Object.entries(R).filter(([k, v])=> v.chain).map(([k, v])=> k + ':' + v.chain).join(' '); })()")
            await pg.screenshot(path=os.path.join(OUT, f'fx_{k:02d}.png')); print(f'{t:4.1f}s', st)
        print('fxlog', (await ev("__dbg.fxlog()"))[-20:]); print('errs', errs[:3])
        await br.close()
asyncio.run(main())
