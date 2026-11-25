"""보이드의 기록 반응형 점검: 기기 4종 x 주요 화면에서 겹침·화면 밖 UI를 찾고 스크린샷을 남긴다.
사용: python -I ch5_resp_sweep_1125.py <출력폴더> [프로필이름...]
서버: API 8096(VOID_STATIC=0, CH5_ADMIN_KEY=0101), 정적 8097(break_out 루트)
"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
ONLY = sys.argv[2:]
STATIC, API = 'http://127.0.0.1:8097', 'http://127.0.0.1:8096'
PROFILES = [('tabL', 1280, 800), ('tabP', 800, 1280), ('phoneP', 390, 844), ('phoneL', 844, 390)]

PROBE = r'''() => {
  const W=innerWidth,H=innerHeight, out={W,H,sw:document.documentElement.scrollWidth,off:[],ov:[]};
  const vis=e=>{const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<0.05)return false;
    for(let p=e.parentElement;p&&p!==document.body;p=p.parentElement){const q=getComputedStyle(p);if(q.display==='none'||q.visibility==='hidden'||+q.opacity<0.05)return false}
    const r=e.getBoundingClientRect();return r.width>2&&r.height>2};
  const name=e=>(e.id?'#'+e.id:e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):''));
  // 화면에 떠 있는 UI 덩어리: fixed 요소 + 그 바로 아래 자식
  const roots=[...document.body.querySelectorAll('*')].filter(e=>getComputedStyle(e).position==='fixed'&&vis(e)&&e.tagName!=='CANVAS');
  const full=e=>{const r=e.getBoundingClientRect();return r.width>=W*0.95&&r.height>=H*0.95};
  const boxes=[];
  for(const e of roots){
    const r=e.getBoundingClientRect();
    if(r.right>W+2||r.bottom>H+2||r.left<-2||r.top<-2){if(!full(e))out.off.push([name(e),Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)])}
    if(full(e)){ // 전체 화면 막: 안쪽 보이는 버튼·글 상자만
      e.querySelectorAll('button,.in,.box,p,h2,h3,img').forEach(c=>{if(!vis(c))return;const q=c.getBoundingClientRect();if(q.right>W+2||q.bottom>H+2||q.left<-2||q.top<-2)out.off.push([name(e)+' '+name(c),Math.round(q.left),Math.round(q.top),Math.round(q.right),Math.round(q.bottom)])});
      continue}
    if(roots.some(o=>o!==e&&o.contains(e)&&!full(o)))continue;
    boxes.push([name(e),r]);
  }
  for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
    const a=boxes[i][1],b=boxes[j][1];const ix=Math.min(a.right,b.right)-Math.max(a.left,b.left),iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
    if(ix>6&&iy>6)out.ov.push([boxes[i][0],boxes[j][0],Math.round(ix),Math.round(iy)])}
  out.ui=boxes.map(b=>[b[0],Math.round(b[1].left),Math.round(b[1].top),Math.round(b[1].width),Math.round(b[1].height)]);
  return out}'''

async def snap(pg, tag, rep):
    await asyncio.sleep(1.2)
    m = await pg.evaluate(PROBE)
    rep[tag] = m
    await pg.screenshot(path=str(OUT / f'{tag}.png'))
    print(tag, 'scrollW', m['sw'], '/', m['W'], '| off', m['off'][:6], '| overlap', m['ov'][:8], flush=True)

async def main():
    rep = {}; errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        for name, w, h in PROFILES:
            if ONLY and name not in ONLY: continue
            phone = min(w, h) <= 500
            ua = ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' if phone else
                  'Mozilla/5.0 (Linux; Android 14; SM-X526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36')
            ctx = await browser.new_context(viewport={'width': w, 'height': h}, screen={'width': w, 'height': h}, has_touch=True,
                                            is_mobile=phone, device_scale_factor=1, user_agent=ua)
            await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
            async def route(r):
                q = r.request
                res = await ctx.request.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer,
                                              headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
                await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
            await ctx.route(re.compile(r'.*/api/void/.*'), route)
            await ctx.request.post(API + '/api/void/team_reset', data={'team': 11, 'confirm': 'AGAIN'}, headers={'X-Admin-Key': '0101'})
            pg = await ctx.new_page()
            pg.on('pageerror', lambda e: errors.append(str(e)))
            # 1) 처음 열었을 때(조 선택)
            await pg.goto(STATIC + '/chapter05/index.html', wait_until='load')
            await asyncio.sleep(6)
            await snap(pg, f'{name}_01_start', rep)
            # 2) 조를 고르고 튜토리얼 대사
            await pg.goto(STATIC + '/chapter05/index.html?team=11', wait_until='load')
            await pg.wait_for_function('!!window.__dbg?.rideState', timeout=90000)
            await asyncio.sleep(5)
            await snap(pg, f'{name}_02_tut', rep)
            for k in range(3):
                await pg.mouse.click(w // 2, h // 2); await asyncio.sleep(1.5)
            await snap(pg, f'{name}_03_tut3', rep)
            # 3) 튜토리얼 끝난 캠퍼스
            await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(4)
            await snap(pg, f'{name}_04_campus', rep)
            # 4) 섬 전경
            await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(5)
            await snap(pg, f'{name}_05_island', rep)
            # 5) 탐험(걷기)
            try:
                await pg.evaluate('__dbg.startWalk()'); await asyncio.sleep(5)
                await snap(pg, f'{name}_06_walk', rep)
                await pg.evaluate('__dbg.stopWalk()'); await asyncio.sleep(2)
            except Exception as e:
                print('walk fail', e)
            await ctx.close()
        await browser.close()
    (OUT / 'report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('errors:', errors[:5])

asyncio.run(main())
