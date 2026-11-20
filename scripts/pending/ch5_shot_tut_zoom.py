# 튜토리얼 13 → 14번째 단계(하모니아 그림 → 캠퍼스 건물 줌인)와 「지금 위치!」 짚기 화면을 찍는다.
# 시험 서버(8096)와 정적 서버(8097)를 스스로 띄우고 끝나면 끈다. python -X utf8 scripts/pending/ch5_shot_tut_zoom.py <그림 폴더>
import asyncio, json, re, sys, os, shutil, subprocess, tempfile, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')).replace('\\', '/')
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; SHOT = sys.argv[1]; T = 8
async def run():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1366, 'height': 768})
        async def route(r):
            q = r.request; res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-sound','0');")
        await ctx.request.post(API + '/api/void/team_reset', data=json.dumps({'team': T, 'confirm': 'AGAIN'}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(STATIC + '/chapter05/index.html', wait_until='domcontentloaded', timeout=120000)
        for _ in range(240):
            if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd && !!document.getElementById('teamPick').dataset.on"): break
            await asyncio.sleep(.5)
        print('renderer', await pg.evaluate("(()=>{const c=document.createElement('canvas').getContext('webgl');const e=c.getExtension('WEBGL_debug_renderer_info');return e?c.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#tpGrid button')].find(b=>b.textContent.trim().startsWith('%d조'));b.click()}" % T)
        for _ in range(60):
            if await pg.evaluate("__dbg.tutState().step>=0"): break
            await asyncio.sleep(.5)
        os.makedirs(SHOT, exist_ok=True)
        async def shot(n): await pg.screenshot(path=os.path.join(SHOT, n + '.png'), timeout=60000)
        for _ in range(40):
            step = await pg.evaluate("__dbg.tutState().step")
            if step >= 99 or step < 0: break
            txt = await pg.evaluate("document.getElementById('voidTxt').textContent")
            if step == 12:
                await asyncio.sleep(1.2); await shot('z0_harmonia')
                await pg.evaluate("document.getElementById('voidNext').click()")
                t0 = time.time()
                for i, at in enumerate([0.12, 0.7, 1.2, 1.7, 2.6]):
                    await asyncio.sleep(max(0, at - (time.time() - t0))); await shot('z%d_%.1fs' % (i + 1, time.time() - t0))
                print('step14', await pg.evaluate("document.getElementById('voidTxt').textContent"), flush=True)
                continue
            if 'ERICA 캠퍼스야' in txt or '한 바퀴 빙' in txt or '링크 복사' in txt:
                await asyncio.sleep(2.6); await shot('em_%d' % step); print('em', step, await pg.evaluate("[...document.querySelectorAll('#voidTxt .dlem')].map(e=> e.textContent + ':' + getComputedStyle(e).color)"), '| raw **', '**' in txt, flush=True)
            if '파란 화살표' in txt:
                await asyncio.sleep(2.2); await shot('me_label')
                print('label', await pg.evaluate("(()=>{const s=document.getElementById('tutSpot');return s&&s.querySelector('b')?s.querySelector('b').textContent:''})()"), flush=True)
            await asyncio.sleep(.9)
            await pg.evaluate("document.getElementById('voidNext').click()"); await asyncio.sleep(.4)
        print('errors:', errs, flush=True)
        await br.close()
def main():
    tmp = tempfile.mkdtemp(prefix='ch5srv_')
    for f in ['ch5_void_server.py', 'ch5_void_pairs.json', 'spz2splat.py']:
        p = os.path.join(ROOT, 'server', f)
        if os.path.exists(p): shutil.copy(p, tmp)
    env = dict(os.environ, VOID_PORT='8096', VOID_STATIC='0', CH5_ADMIN_KEY='0101', PYTHONUTF8='1')
    a = subprocess.Popen([sys.executable, 'ch5_void_server.py'], cwd=tmp, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    b = subprocess.Popen([sys.executable, '-m', 'http.server', '8097', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2.5); asyncio.run(run())
    finally:
        a.kill(); b.kill(); time.sleep(.5); shutil.rmtree(tmp, ignore_errors=True)
main()
