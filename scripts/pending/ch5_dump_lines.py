# 페이지가 실제로 쓰는 대사·문구 표(STORY 최종값, 튜토리얼, 미션 카드, 목적지 문구, 단계 안내, 동굴 선택지)를 실행 상태에서 꺼내 JSON으로 적는다.
#  STORY는 여러 줄에서 덮어쓰므로 소스를 읽지 않고 실행 뒤 값을 본다.  정적 서버 8097.  python ch5_dump_lines.py <결과 json>
import asyncio, sys, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]
NAMES = ['STORY', 'TUT', 'MCARDS', 'GO_TO', 'STEP_LINE', 'CAVE_CHOICE', 'QUEST_FOUND', 'QUEST_INTRO', 'MISSIONS', 'MISSIONS_I', 'QUEST_DONE', 'QUEST_NEXT', 'MCARD_NEXT', 'CAVE', 'CAVE_SCENES', 'MURALS', 'REM_SAY', 'CHASE_SAY', 'ACTS', 'ACT']
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>')
        hook = "\n;window.__dump = ()=>{ const o = {}; " + ' '.join(f"try{{ o.{n} = {n}; }}catch(e){{}}" for n in NAMES) + " return JSON.stringify(o, (k, v)=> typeof v === 'function' ? 'FN ' + String(v).slice(0, 700) : v); };\n"
        src = src[:i] + hook + src[i:]
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dump === 'function' && typeof window.__dbg !== 'undefined'"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(3)
        d = json.loads(await pg.evaluate("window.__dump()")); pathlib.Path(sys.argv[1]).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
        print({k: (len(v) if hasattr(v, '__len__') else 1) for k, v in d.items()}, 'errs', errs[:2]); await br.close()
asyncio.run(main())
