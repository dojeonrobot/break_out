# 2026-11-10 대사 장소명 제거 점검: 조 태블릿에서 튜토리얼을 끝까지 넘기며 말풍선 글을 모으고, 융합교육관 외 장소 이름이 없는지, 좌표 문장이 살아 있는 값으로 나오는지 본다.
import asyncio, json, re
from playwright.async_api import async_playwright
STATIC='http://127.0.0.1:8097'; API='http://127.0.0.1:8096'
BAN = ['하냥이', '데이터센터', '전시대', '라이언스홀', '어피치']
fails=[]
def check(c, m): print(('OK   ' if c else 'FAIL ')+m); (None if c else fails.append(m))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-angle=swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':1280,'height':800})
        async def route(r):
            req=r.request; url=req.url.replace(STATIC,API)
            try:
                resp=await ctx.request.fetch(url,method=req.method,headers={k:v for k,v in req.headers.items() if k.lower() not in ('host','origin','referer')},data=req.post_data_buffer)
                await r.fulfill(status=resp.status,headers={'content-type':resp.headers.get('content-type','application/json')},body=await resp.body())
            except Exception as e: await r.fulfill(status=500,body=str(e))
        await ctx.route(re.compile(r'.*/api/void/.*'),route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        H={'content-type':'application/json','X-Admin-Key':'0101'}
        await ctx.request.post(API+'/api/void/team_reset',data=json.dumps({'team':9,'confirm':'AGAIN'}),headers=H)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(f'{STATIC}/chapter05/index.html?team=9',wait_until='domcontentloaded',timeout=120000)
        for i in range(120):
            if await pg.evaluate("typeof window.__dbg !== 'undefined'"): break
            await asyncio.sleep(0.5)
        for i in range(80):   # 인트로 카메라(약 5초) 뒤 maybeGuide가 튜토리얼을 연다
            vis = await pg.evaluate("(()=>{ const v=document.getElementById('voidVn'); if(!v) return false; const cs=getComputedStyle(v); return cs.display!=='none' && cs.visibility!=='hidden' && cs.opacity!=='0'; })()")
            if vis: break
            await asyncio.sleep(0.5)
        print('balloon visible after', i*0.5, 's'); await asyncio.sleep(1.5)
        lines=[]
        for i in range(30):
            txt = await pg.evaluate("(()=>{ const v=document.getElementById('voidVn'); return v && v.dataset.on ? v.innerText.replace(/\\s+/g,' ').trim() : ''; })()")
            if txt and (not lines or lines[-1] != txt): lines.append(txt)
            nxt = await pg.evaluate("(()=>{ const n=document.getElementById('voidNext'); if(!n || n.hidden || n.offsetParent===null) return false; n.click(); return true; })()")
            if not nxt: break
            await asyncio.sleep(1.2)
        print('tutorial lines', len(lines)); print('voidLog', await pg.evaluate("(window.__voidLog||[]).map(x=> x[1])"))
        for t in lines: print('  ', t[:110])
        allt = ' '.join(lines)
        check('37.295655, 126.838475' in allt and '융합교육관이야' in allt, 'coordinate line comes from the live coordinates')
        check('이 건물 어딘가에서 반응' in allt, 'tutorial says 건물 어딘가')
        bad=[bn for bn in BAN if bn in allt]
        check(not bad, f'tutorial names no place except 융합교육관: {bad}')
        body = await pg.evaluate("(()=>{ document.querySelectorAll('.lbl').forEach(l=> l.remove()); return document.body.innerText; })()")   # 3D 지도 건물 라벨은 실제 건물 이름이라 제외
        bad=[bn for bn in BAN if bn in body]
        check(not bad, f'tablet UI text (map labels excluded) names no place: {bad}')
        names = await pg.evaluate("(()=>{ return [...document.querySelectorAll('#list h4, #list .brow h4')].map(h=> h.textContent.trim()); })()")
        print('card names', names)
        check(any(n.startswith('기록 1') for n in names) and not any(bn in n for n in names for bn in BAN), 'record cards are numbered, no place names')
        check(not errs, f'no page errors {errs[:2]}')
        await b.close()
    print('FAILS', fails)
asyncio.run(main())
