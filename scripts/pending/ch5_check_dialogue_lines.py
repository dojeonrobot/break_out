# 대사 줄바꿈 점검: 페이지의 모든 대사를 실제 대사 창에 넣어 보고, 문장이 한 줄에 들어가는지·글자 크기·쉼표에서 나눈 문장을 화면 크기별로 잰다.
# 사설 API 8096 + 정적 8097. python scripts/pending/ch5_check_dialogue_lines.py [shot_dir]
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; SHOT = sys.argv[1] if len(sys.argv) > 1 else None
JS = r"""async()=>{
 const texts = {vn:[], void:[]}; const seen = new Set();
 for(const k in __STORYREF){ for(const L of __STORYREF[k]||[]){ if(L && L.text && !seen.has('v'+L.text)){ seen.add('v'+L.text); texts.vn.push([L.text, !!L.nar]); } } }
 for(const t of __TUTREF){ const x = typeof t.t === 'function' ? t.t() : t.t; texts.void.push(x); }
 for(const m of document.documentElement.innerHTML.matchAll(/void(?:Ask|Say)\('([^']{6,})'/g)) if(!seen.has('o'+m[1])){ seen.add('o'+m[1]); texts.void.push(m[1]); }
 const run = (boxId, pId, list)=>{ const el = document.getElementById(boxId), p = document.getElementById(pId); el.dataset.on = '1'; const out = {n:0, sentences:0, fit:0, wrapped:[], commaSplit:[], minSize:99, shrunk:0, lines:{}, base:0, avail:0};
   for(const item of list){ const text = Array.isArray(item) ? item[0] : item; p.classList.toggle('nar', Array.isArray(item) && item[1]); p._dl = null; dlShow(p, text, 1e9);
     const d = p._dl, base = parseFloat(getComputedStyle(p).fontSize); out.n++; out.avail = p.clientWidth; const orig = dlSplit(text).length; out.sentences += orig;
     const fs = d.size || (p.style.fontSize = '', parseFloat(getComputedStyle(p).fontSize)); out.base = Math.max(out.base, parseFloat(getComputedStyle(p).fontSize)); if(d.size){ out.shrunk++; out.minSize = Math.min(out.minSize, d.size); }
     dlShow(p, text, 1e9); let ok = true; for(const c of p.children){ const lh = parseFloat(getComputedStyle(c).lineHeight) || c.offsetHeight; if(c.offsetHeight > lh*1.5 || c.offsetWidth > p.clientWidth + 1) ok = false; }
     if(ok) out.fit++; else out.wrapped.push(text.slice(0, 40)); if(d.parts.length > orig) out.commaSplit.push(text.slice(0, 46)); out.lines[d.parts.length] = (out.lines[d.parts.length]||0) + 1; }
   p.classList.remove('nar'); delete el.dataset.on; return out; };
 return {vn:run('vn', 'vnText', texts.vn), void:run('voidVn', 'voidTxt', texts.void)}; }"""
SHOW = r"""([box, pid, who, text])=>{ const el = document.getElementById(box), p = document.getElementById(pid); el.dataset.on = '1'; if(who !== null){ document.getElementById('vnName').textContent = who; document.getElementById('vnName').hidden = false; const im = document.getElementById('vnImg'); im.src = 'img/chars/xylo_talk.png'; im.hidden = false; } p._dl = null; dlShow(p, text, 1e9); }"""
async def main():
    fails = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, w, h, touch in [('laptop', 1366, 768, False), ('tablet-land', 1180, 820, True), ('tablet-port', 820, 1180, True), ('phone-land', 780, 360, True)]:
            ctx = await br.new_context(viewport={'width': w, 'height': h}, has_touch=touch)
            async def route(r):
                q = r.request; res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            src = open(os.path.join(os.path.dirname(__file__), '..', '..', 'chapter05', 'index.html'), encoding='utf-8').read()
            src = src.replace('const ACT_STORY=', 'window.__STORYREF = STORY; window.__TUTREF = []; const ACT_STORY=', 1).replace('// a taste of 내 시점 during the tutorial', 'window.__TUTREF = TUT;\n// a taste of 내 시점 during the tutorial', 1).replace('function vnNext(){', 'window.dlShow = dlShow; window.dlSplit = dlSplit;\nfunction vnNext(){', 1)
            await ctx.route('**/chapter05/index.html*', lambda r: r.fulfill(body=src, content_type='text/html'))
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto(STATIC + '/chapter05/index.html?team=9', wait_until='domcontentloaded', timeout=120000)
            for _ in range(200):
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.tutEnd && typeof dlShow==='function'"): break
                await asyncio.sleep(.5)
            await pg.evaluate("__dbg.tutEnd(); const tp=document.getElementById('teamPick'); if(tp) delete tp.dataset.on;"); await asyncio.sleep(1)
            r = await pg.evaluate(JS)
            for k in ('vn', 'void'):
                o = r[k]; print(f"{name} {k}: 대사 {o['n']} · 문장 {o['sentences']} · 한 줄에 들어간 대사 {o['fit']}/{o['n']} · 줄인 대사 {o['shrunk']} (가장 작은 글자 {o['minSize'] if o['shrunk'] else '-'}px, 기본 {o['base']}px, 폭 {o['avail']}px) · 쉼표에서 나눈 대사 {len(o['commaSplit'])} · 줄 수 분포 {o['lines']}", flush=True)
                if o['wrapped']: fails.append((name, k, o['wrapped'][:5]))
                for t in o['commaSplit'][:6]: print('    쉼표 분할:', t)
            if SHOT:
                os.makedirs(SHOT, exist_ok=True)
                await pg.evaluate(SHOW, ['vn', 'vnText', '자일로', '네. 그러려면 네이티부터 찾아야 해요. 네이티가 끌려간 쪽에 일루아가 흐르던 자리가 있을 겁니다. 관람차 뒤쪽 길부터 찾아봐 주세요.']); await asyncio.sleep(.5); await pg.screenshot(path=os.path.join(SHOT, name + '_vn.png'), timeout=60000)
                await pg.evaluate("delete document.getElementById('vn').dataset.on")
                await pg.evaluate(SHOW, ['voidVn', 'voidTxt', None, '거듭된 연구로 인해 일루아는 흐름을 잃고 방황하고 있어. 섬을 살리려면, 일루아를 섬에 돌려줘야 해. 즉, 환원이 필요한거지.']); await asyncio.sleep(.5); await pg.screenshot(path=os.path.join(SHOT, name + '_void.png'), timeout=60000)
            if errs: fails.append((name, 'pageerror', errs[:3]))
            await ctx.close()
        await br.close()
    print('FAILS', fails)
asyncio.run(main())
