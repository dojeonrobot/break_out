# 연구실 모니터 벽 시안: 지금 화면과 시안 A(실제 섬 화면 바탕)·B(입체 홀로그램)를 평소·잡음 두 상태로 찍는다. 페이지 소스는 건드리지 않는다.
# 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096, 저장소 파일도 서빙).  python -X utf8 scripts/pending/ch5_shot_lab_mock.py <그림 폴더>
import asyncio, sys, os, pathlib, base64, io
from playwright.async_api import async_playwright
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
BASE = r"""
#labRoom.lrmk .mon{border:5px solid #090d14;border-radius:9px;box-shadow:0 0 0 1px #24344a,0 0 0 2px #05080d,0 18px 34px -12px #000,0 0 34px -6px rgba(63,170,230,.35),inset 0 0 46px rgba(47,143,214,.16)}
#labRoom.lrmk .mon::before{content:'';position:absolute;inset:0;z-index:3;pointer-events:none;background:linear-gradient(128deg,rgba(255,255,255,.07) 0,rgba(255,255,255,0) 26%),radial-gradient(ellipse at 50% 50%,transparent 58%,rgba(2,5,10,.55))}
#labRoom.lrmk .mon h2{padding:6px 10px 6px 12px;font:700 12.5px var(--sans);color:#cfe6f6;background:linear-gradient(180deg,rgba(18,44,74,.95),rgba(10,26,46,.9));border-bottom:1px solid #2a5078;position:relative}
#labRoom.lrmk .mon h2::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--cy);box-shadow:0 0 10px var(--cy)}
#labRoom.lrmk[data-noise] .mon h2::before{background:var(--warn);box-shadow:0 0 10px var(--warn)}
#labRoom.lrmk .mon h2 b{font:600 10.5px var(--mono);letter-spacing:.1em}
#labRoom.lrmk .lst{font-size:11px;padding:3px 10px;box-shadow:0 0 12px -2px currentColor}
#labRoom.lrmk #lrBars{display:flex;align-items:flex-end;gap:8%;height:100%;padding:4px 4% 0}
#labRoom.lrmk #lrBars>div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;height:100%;gap:4px}
#labRoom.lrmk #lrBars u{display:block;height:var(--h);min-height:0;border-radius:2px;text-decoration:none;background:repeating-linear-gradient(0deg,#7fe9ff 0 5px,transparent 5px 8px);filter:drop-shadow(0 0 6px rgba(127,233,255,.8));opacity:1}
#labRoom.lrmk #lrBars .off u{height:14%;background:repeating-linear-gradient(0deg,#27405c 0 5px,transparent 5px 8px);filter:none}
#labRoom.lrmk[data-noise] #lrBars .on u{background:repeating-linear-gradient(0deg,#ff6a5e 0 5px,transparent 5px 8px);filter:drop-shadow(0 0 6px rgba(255,90,78,.9))}
#labRoom.lrmk #lrBars span{font:600 10.5px var(--sans);color:#a9c4da;text-align:center;white-space:nowrap}
#labRoom.lrmk #lrGz svg{filter:drop-shadow(0 0 5px rgba(127,233,255,.55))}
#labRoom.lrmk #lrGz figcaption{font:600 11px var(--sans);color:#a9c4da}
#labRoom.lrmk #lrWave{filter:drop-shadow(0 0 5px rgba(127,233,255,.7))}
#labRoom.lrmk[data-noise] #lrWave{filter:drop-shadow(0 0 5px rgba(255,90,78,.8))}
#labRoom.lrmk #lrZl>div{display:flex;align-items:center;gap:8px;padding:3px 0;font:600 12px var(--sans)}
#labRoom.lrmk #lrZl span{flex:1}
#labRoom.lrmk #lrZl em{font-style:normal;font:600 11px var(--sans)}
#labRoom.lrmk #lrTl>div{font-size:12.5px}
#labRoom.lrmk .wall{gap:11px}#labRoom.lrmk .col{gap:11px}
#labRoom.lrmk .back{background:linear-gradient(90deg,#03060b 0,#0b1626 11vw,#0d1a2c 50%,#0b1626 calc(100% - 11vw),#03060b 100%)}
#labRoom.lrmk .back>.wall::before{content:'';position:absolute;inset:-2% 9vw;z-index:-1;background:radial-gradient(ellipse at 50% 40%,rgba(63,170,230,.16),transparent 62%)}
"""
A = BASE + r"""
#labRoom.lrmk .col.c .mon:first-child .body{padding:0;background:#061220}
#labRoom.lrmk .col.c .mon:first-child .body::before{content:'';position:absolute;inset:0;background:var(--top) 50% 50%/contain no-repeat;filter:saturate(.5) brightness(.62) contrast(1.15) hue-rotate(-6deg)}
#labRoom.lrmk .col.c .mon:first-child .body::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,40,80,.28),rgba(6,18,32,.38));pointer-events:none}
#labRoom.lrmk #lrMap{position:relative;z-index:1}
#labRoom.lrmk #lrMap .isl{fill:none!important;stroke:#7fe9ff;stroke-width:5;filter:drop-shadow(0 0 10px #7fe9ff)}
#labRoom.lrmk #lrMap .grid{stroke:rgba(127,233,255,.13)}
#labRoom.lrmk #lrMap .flow{fill:rgba(127,233,255,.6);stroke:#d6fbff;stroke-width:4;filter:drop-shadow(0 0 14px #7fe9ff)}
#labRoom.lrmk #lrMap .ghost{fill:rgba(127,233,255,.1);stroke:rgba(127,233,255,.45);stroke-width:3;stroke-dasharray:14 10}
#labRoom.lrmk #lrMap .z text{font-size:34px;font-weight:700;fill:#fff;paint-order:stroke;stroke:#04101c;stroke-width:9px}
#labRoom.lrmk #lrMap .z circle{stroke:#7fe9ff;stroke-width:4;fill:rgba(127,233,255,.16)}
#labRoom.lrmk .col.r .mon:nth-child(3) .body{background:linear-gradient(rgba(5,18,34,.66),rgba(5,18,34,.66)),var(--top) 50% 50%/66.1% 90.7% no-repeat #050d18}
#labRoom.lrmk #lrHeat{mix-blend-mode:screen;opacity:.92}
#labRoom.lrmk #lrZl>div{padding:1px 0}
#labRoom.lrmk #lrZl i{width:40px!important;height:21px!important;border-radius:4px!important;flex:none;background:var(--top) no-repeat!important;background-size:1100% auto!important;border:1px solid #2f5d86;box-shadow:none!important;filter:saturate(.7) brightness(.85)}
#labRoom.lrmk #lrZl .off i{filter:grayscale(1) brightness(.45)}
"""
B = BASE + r"""
#labRoom.lrmk .mon{background:radial-gradient(ellipse at 50% 0,#0c2744,#050d18 70%)}
#labRoom.lrmk .col.c .mon:first-child .body{padding:0;perspective:780px;overflow:hidden;background:radial-gradient(ellipse at 50% 100%,rgba(63,170,230,.3),transparent 60%)}
#labRoom.lrmk .holo{position:absolute;left:8%;right:8%;top:-6%;bottom:-2%;transform:rotateX(54deg);transform-style:preserve-3d}
#labRoom.lrmk .holo::before{content:'';position:absolute;inset:0;background:var(--top) 50% 50%/contain no-repeat;filter:grayscale(1) brightness(.5) contrast(1.5) sepia(1) hue-rotate(165deg) saturate(2.6);mask:radial-gradient(ellipse at 50% 50%,#000 52%,transparent 70%);-webkit-mask:radial-gradient(ellipse at 50% 50%,#000 52%,transparent 70%)}
#labRoom.lrmk .holo::after{content:'';position:absolute;inset:-8%;background:repeating-linear-gradient(0deg,rgba(127,233,255,.16) 0 1px,transparent 1px 7.14%),repeating-linear-gradient(90deg,rgba(127,233,255,.16) 0 1px,transparent 1px 7.14%);border:1px solid rgba(127,233,255,.5);border-radius:50%;mask:radial-gradient(circle,#000 58%,transparent 72%)}
#labRoom.lrmk .holo #lrMap{position:absolute;inset:0;z-index:1}
#labRoom.lrmk #lrMap .isl{fill:rgba(40,120,190,.12)!important;stroke:#7fe9ff;stroke-width:6;filter:drop-shadow(0 0 14px #7fe9ff)}
#labRoom.lrmk #lrMap .grid{display:none}
#labRoom.lrmk #lrMap .flow{fill:rgba(127,233,255,.7);stroke:#e2fdff;stroke-width:4;filter:drop-shadow(0 0 18px #7fe9ff)}
#labRoom.lrmk #lrMap .ghost{fill:none;stroke:rgba(127,233,255,.5);stroke-width:3;stroke-dasharray:14 10}
#labRoom.lrmk #lrMap .z text{display:none}
#labRoom.lrmk .beam{position:absolute;width:10px;height:26%;margin-left:-5px;transform-origin:50% 100%;transform:translateY(-100%) rotateX(-90deg);background:linear-gradient(0deg,rgba(127,233,255,.95),rgba(127,233,255,0));box-shadow:0 0 16px rgba(127,233,255,.8)}
#labRoom.lrmk .beam.off{background:linear-gradient(0deg,rgba(120,150,180,.5),transparent);box-shadow:none;height:12%}
#labRoom.lrmk .beam b{position:absolute;left:50%;bottom:104%;transform:translateX(-50%);white-space:nowrap;font:700 12px var(--sans);color:#fff;background:rgba(4,16,28,.82);border:1px solid #3d7fae;border-radius:5px;padding:2px 7px}
#labRoom.lrmk[data-noise] .beam:not(.off){background:linear-gradient(0deg,rgba(255,90,78,.95),rgba(255,90,78,0));box-shadow:0 0 16px rgba(255,90,78,.8)}
#labRoom.lrmk .col.r .mon:nth-child(3) .body{background:linear-gradient(rgba(5,18,34,.66),rgba(5,18,34,.66)),var(--top) 50% 50%/66.1% 90.7% no-repeat #050d18}
#labRoom.lrmk #lrHeat{mix-blend-mode:screen;opacity:.92}
#labRoom.lrmk #lrZl i{width:10px!important;height:10px!important}
"""
JS = r"""([kind, css, top])=>{ const d = document.getElementById('labRoom'); let st = document.getElementById('mkStyle'); if(!st){ st = document.createElement('style'); st.id = 'mkStyle'; document.head.appendChild(st); }
  st.textContent = css; d.classList.toggle('lrmk', kind !== 'cur'); d.style.setProperty('--top', `url(${top})`);
  const map = document.getElementById('lrMap'), body = map.closest('.body'); let h = body.querySelector('.holo'); if(h){ body.appendChild(map); h.remove(); }
  document.querySelectorAll('#lrZl i').forEach(i=> i.style.backgroundPosition = '');
  const MI = __t.MI, ids = __t.GLYPH_ZONES.map(z=> z.id);
  if(kind === 'A') document.querySelectorAll('#lrZl>div').forEach((row, k)=>{ const m = MI.find(x=> x.id === ids[k]); if(m && m.b) row.querySelector('i').style.backgroundPosition = `${((m.b.cx + 700)/1400*100).toFixed(1)}% ${((m.b.cz + 680)/1360*100).toFixed(1)}%`; });
  if(kind === 'B'){ h = document.createElement('div'); h.className = 'holo'; body.appendChild(h); h.appendChild(map); const r = h.getBoundingClientRect();
    const W = h.clientWidth, H = h.clientHeight, s = Math.min(W/1400, H/1360);
    ids.forEach(id=>{ const m = MI.find(x=> x.id === id); if(!m || !m.b) return; const b = document.createElement('div'); b.className = 'beam' + (__t.LABROOM.on.includes(id) ? '' : ' off'); b.style.left = (W/2 + m.b.cx*s) + 'px'; b.style.top = (H/2 + m.b.cz*s) + 'px'; b.innerHTML = `<b>${m.name}</b>`; h.appendChild(b); }); }
  return kind; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1366, 'height': 768}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src; src = src.replace(HOOK, HOOK + " window.__t = new Proxy({}, {get:(_, k)=> eval(String(k))});")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?world=island', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__t"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(9); ev = pg.evaluate; await pg.add_style_tag(content='#teamPick{display:none!important}')
        try: await ev("__dbg.setDemo(['dl-harmonia','dl-carousel','dl-coaster'], true)")
        except Exception as e: print('setDemo', str(e)[:100])
        print('renderer', await ev("(()=>{const c=document.createElement('canvas').getContext('webgl');const e=c.getExtension('WEBGL_debug_renderer_info');return e?c.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"))
        # 위에서 본 섬(평면도 바탕) 찍기: 화면 요소를 숨기고 곧게 내려다본 뒤, 세계 좌표 사각형이 화면 어디에 오는지 재서 그만큼 자른다
        await ev("(()=>{ const c = __t; c.controls.minDistance = 1; c.controls.maxDistance = 9000; c.camera.position.set(0, 2500, 1); c.controls.target.set(0, 0, 0); c.controls.update(); c.camera.lookAt(0, 0, 0); })()"); await asyncio.sleep(2.5)
        rect = await ev("(()=>{ const T = __dbg.THREE, c = __t.camera, P = (x, z)=>{ const v = new T.Vector3(x, __t.G, z).project(c); return [(v.x + 1)/2*innerWidth, (1 - v.y)/2*innerHeight]; }; return [P(-700, -680), P(700, 680)]; })()")
        await ev("()=>{ const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE'){ e.dataset.hid = e.style.visibility; e.style.visibility = 'hidden'; } }); }")
        await asyncio.sleep(.5); raw = await pg.screenshot(type='png'); print('top rect', rect)
        await ev("()=>{ document.querySelectorAll('[data-hid]').forEach(e=>{ e.style.visibility = e.dataset.hid; delete e.dataset.hid; }); }")
        im = Image.open(io.BytesIO(raw)).convert('RGB'); (x0, y0), (x1, y1) = rect; box = (round(min(x0, x1)), round(min(y0, y1)), round(max(x0, x1)), round(max(y0, y1))); im = im.crop(box).resize((900, round(900*1360/1400)), Image.LANCZOS); im.save(os.path.join(OUT, 'island_top.jpg'), quality=88)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84); top = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
        shot = lambda n: pg.screenshot(path=f'{OUT}/{n}.jpg', type='jpeg', quality=90)
        try: await ev("(()=>{ __t['zoneDone = ()=> true']; })()")   # 시안은 기록이 다 들어온 상태로 본다(이 세션 안에서만)
        except Exception as e: print('lit', str(e)[:120])
        await ev("__t.labRoomOpen(false)"); await asyncio.sleep(.9); print('on', await ev("__t.LABROOM.on.length"))
        for kind, css in (('cur', ''), ('A', A), ('B', B)):
            await ev("__t.labRoomNoise(false)"); print('mock', await ev(JS, [kind, css, top])); await asyncio.sleep(.8); await shot(f'{kind}_calm')
            await ev("__t.labRoomNoise(true)"); await asyncio.sleep(.7); await shot(f'{kind}_noise')
        print('errs', errs[:4]); await br.close()
asyncio.run(main())
