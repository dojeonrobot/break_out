# 미로 한가운데 네이티 표현 시안: 지금 모습과 시안 A·B·C를 같은 세 시점(가까이·위에서·미로 입구)에서 찍어 한 장으로 묶는다.
# 페이지 소스는 건드리지 않고 실행 중인 장면에 효과를 얹어 찍는다. 시험 서버(8096)·정적 서버(8097)를 스스로 띄우고 끈다.
# python -X utf8 scripts/pending/ch5_shot_naty_fx.py <그림 폴더>
import asyncio, json, re, sys, os, shutil, subprocess, tempfile, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')).replace('\\', '/')
STATIC = 'http://127.0.0.1:8097'; API = 'http://127.0.0.1:8096'; ADM = {'content-type': 'application/json', 'X-Admin-Key': '0101'}; T = 9; OUT = sys.argv[1]
FX = r"""(kind)=>{ const T = __dbg.THREE, N = __dbg.chars().NATY, bm = N.userData.beam, root = N.parent, pk = N.userData.park, G = __dbg.groundY(pk[0], pk[1]);
  if(window.__fx){ window.__fx.parent.remove(window.__fx); window.__fx = null; }
  N.traverse(o=>{ if(o.isMesh) o.onBeforeRender = ()=>{}; });
  bm.children.forEach(c=> c.visible = kind === 'cur');
  if(kind === 'cur') return 'cur';
  let seed = 7; const rnd = ()=>{ seed = (seed*16807) % 2147483647; return seed/2147483647; };
  const cv = document.createElement('canvas'); cv.width = cv.height = 128; const x = cv.getContext('2d'), gr = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.35, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 128, 128);
  const tex = new T.CanvasTexture(cv), g = new T.Group(); g.position.set(pk[0], G, pk[1]); root.add(g); window.__fx = g;
  const spr = (c, op, s, px, py, pz, add = true)=>{ const m = new T.Sprite(new T.SpriteMaterial({map:tex, color:c, transparent:true, opacity:op, depthWrite:false, fog:false, blending:add ? T.AdditiveBlending : T.NormalBlending})); m.scale.set(s, s, 1); m.position.set(px, py, pz); m.renderOrder = 7; g.add(m); return m; };
  const flat = (c, op, r, add = true)=>{ const m = new T.Mesh(new T.CircleGeometry(r, 40).rotateX(-Math.PI/2), new T.MeshBasicMaterial({map:tex, color:c, transparent:true, opacity:op, depthWrite:false, blending:add ? T.AdditiveBlending : T.NormalBlending})); m.position.y = 0.5; m.renderOrder = 6; g.add(m); return m; };
  const ny = pk[2] - G + 1.2;
  if(kind === 'A'){   /* 흔들리는 불씨: 네이티의 빛이 새어 나가 불씨처럼 흩어져 올라간다 */
    spr(0xff4a30, .4, 6.5, 0, ny, 0); flat(0xff5a30, .42, 5.5);
    for(let i = 0; i < 70; i++){ const h = Math.pow(rnd(), 1.4)*17, a = rnd()*6.283, r = (0.6 + h*0.16)*rnd() + 0.4, k = 1 - h/18; spr(rnd() < .5 ? 0xff6a30 : 0xff3a28, .3 + .5*k, 0.35 + rnd()*0.75*k + .15, Math.cos(a)*r, ny - 2 + h, Math.sin(a)*r); }
  }
  if(kind === 'B'){   /* 갈라지는 빛: 몸이 여러 겹으로 어긋나 보이고 바닥에 붉은 금이 번진다 */
    [[-1.5, 1.18, .3], [1.3, .88, .26], [0.4, 1.3, .16]].forEach(([dx, sx, op], i)=>{ const c = N.clone(true); c.traverse(o=>{ if(o.isMesh){ o.material = new T.MeshBasicMaterial({color:i === 2 ? 0xff8a78 : 0xf0382a, transparent:true, opacity:op + .14, depthWrite:false}); o.renderOrder = 7; } });
      c.position.set(dx*Math.cos(N.rotation.y), pk[2] - G + (i - 1)*0.5, -dx*Math.sin(N.rotation.y)); c.rotation.y = N.rotation.y; c.scale.copy(N.scale); c.scale.x *= sx; g.add(c); });
    const pos = [], rib = (x0, z0, x1, z1, w)=>{ const dx = x1 - x0, dz = z1 - z0, l = Math.hypot(dx, dz) || 1, nx = -dz/l*w, nz = dx/l*w; pos.push(x0 + nx, 0, z0 + nz, x0 - nx, 0, z0 - nz, x1 + nx*.6, 0, z1 + nz*.6, x0 - nx, 0, z0 - nz, x1 - nx*.6, 0, z1 - nz*.6, x1 + nx*.6, 0, z1 + nz*.6); };
    const crack = (x0, z0, a, len, w, d)=>{ let px = x0, pz = z0; const n = 5; for(let i = 0; i < n; i++){ a += (rnd() - .5)*1.1; const s = len/n, qx = px + Math.cos(a)*s, qz = pz + Math.sin(a)*s; rib(px, pz, qx, qz, w*(1 - i/n*.7)); if(d && rnd() < .55) crack(qx, qz, a + (rnd() < .5 ? .9 : -.9), len*.45, w*.6, 0); px = qx; pz = qz; } };
    for(let i = 0; i < 9; i++) crack(0, 0, i/9*6.283 + rnd()*.4, 4.2 + rnd()*2.6, 0.2, 1);
    const cg = new T.BufferGeometry(); cg.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); const cm = new T.Mesh(cg, new T.MeshBasicMaterial({color:0xff5040, transparent:true, opacity:.95, depthWrite:false, side:T.DoubleSide})); cm.position.y = 0.52; cm.renderOrder = 6; g.add(cm);
    flat(0xff4030, .5, 6.5); spr(0xff5040, .4, 10, 0, ny, 0);
    [[5, .2, 1.25], [9.5, .13, 1.5], [14, .07, 1.8]].forEach(([up, op, sc])=>{ const c = N.clone(true); c.traverse(o=>{ if(o.isMesh){ o.material = new T.MeshBasicMaterial({color:0xff5a48, transparent:true, opacity:op, depthWrite:false, blending:T.AdditiveBlending}); o.renderOrder = 7; } }); c.position.set(0, pk[2] - G + up, 0); c.rotation.y = N.rotation.y; c.scale.copy(N.scale).multiplyScalar(sc); g.add(c); });
  }
  if(kind === 'C'){   /* 꺼져 가는 빛: 빛이 바래 희미해지고 검붉은 연기가 피어오른다 */
    const fm = N.userData.fm; N.traverse(o=>{ if(o.isMesh && o.material === fm) o.onBeforeRender = ()=>{ fm.color.set(0x6a4a4e); fm.emissive.set(0x8a2a22); fm.emissiveIntensity = .28; }; });
    flat(0x1a0c10, .7, 6.5, false); spr(0xff3a2a, .3, 5, 0, ny, 0);
    for(let i = 0; i < 46; i++){ const h = Math.pow(rnd(), 1.1)*19, a = rnd()*6.283, r = (0.3 + h*0.11)*rnd(), k = 1 - h/20; spr(rnd() < .3 ? 0x5a2228 : 0x2a1a22, .16 + .3*k, 2.2 + h*0.28 + rnd()*1.2, Math.cos(a)*r + h*0.07, ny - 1 + h, Math.sin(a)*r, false); }
    for(let i = 0; i < 9; i++){ const h = rnd()*7, a = rnd()*6.283; spr(0xff5a3a, .7, 0.3 + rnd()*.3, Math.cos(a)*1.2, ny - 1 + h, Math.sin(a)*1.2); }
  }
  g.traverse(o=>{ o.userData.dynamic = true; o.castShadow = false; }); return kind; }"""
VIEW = r"""(v)=>{ const T = __dbg.THREE, N = __dbg.chars().NATY, pk = N.userData.park, G = __dbg.groundY(pk[0], pk[1]), ry = N.rotation.y, C = new T.Vector3(pk[0], pk[2] + 3.4, pk[1]); __dbg.controls.minDistance = 0.5;
  if(v === 'near') __dbg.flyTo(new T.Vector3(pk[0] + Math.sin(ry)*12, G + 11, pk[1] + Math.cos(ry)*12), C, 10);
  if(v === 'top') __dbg.flyTo(new T.Vector3(pk[0] + 6, G + 62, pk[1] + 46), new T.Vector3(pk[0], G + 2, pk[1]), 10);
  if(v === 'gate') __dbg.flyTo(new T.Vector3(155, __dbg.groundY(155, 362) + 1.6, 362), new T.Vector3(pk[0], G + 8, pk[1]), 10); }"""
async def run():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width': 1180, 'height': 820}); rq = ctx.request
        async def route(r):
            q = r.request; res = await rq.fetch(q.url.replace(STATIC, API), method=q.method, data=q.post_data_buffer, headers={k: v for k, v in q.headers.items() if k not in ['host', 'origin', 'referer']})
            await r.fulfill(status=res.status, body=await res.body(), headers={'content-type': res.headers.get('content-type', 'application/json')})
        await ctx.route(re.compile(r'.*/api/void/.*'), route)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','beam');localStorage.setItem('void-sound','0');")
        post = lambda path, body, adm=False: rq.post(API + '/api/void/' + path, data=json.dumps(body), headers=ADM if adm else {'content-type': 'application/json'})
        await post('team_reset', {'team': T, 'confirm': 'AGAIN'}, True); await post('admin/skip', {'team': T, 'mission': 'z1'}, True)
        await post('quest', {'team': T, 'dev': 'beam', 'done': ['q1'], 'act': 1, 'tut': True, 'story': 3, 'power': True})
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(f'{STATIC}/chapter05/index.html?team={T}', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        print('renderer', await pg.evaluate("(()=>{const c=document.createElement('canvas').getContext('webgl');const e=c.getExtension('WEBGL_debug_renderer_info');return e?c.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'})()"), flush=True)
        await asyncio.sleep(3); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(4)
        await pg.evaluate("()=>{ const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }")
        print('naty', await pg.evaluate("(()=>{ const n = __dbg.chars().NATY; return {park:n.userData.park, beam:!!n.userData.beam}; })()"), flush=True)
        for kind in KINDS:
            print('fx', await pg.evaluate(FX, kind), flush=True)
            for v in ('near', 'top', 'gate'):
                await pg.evaluate(VIEW, v); await asyncio.sleep(1.8)
                await pg.screenshot(path=os.path.join(OUT, f'{kind}_{v}.png'), timeout=60000)
        print('errors:', errs[:3], flush=True); await br.close()
def sheet():
    from PIL import Image, ImageDraw, ImageFont
    W, H, pad, lab = 590, 410, 14, 54; f = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 26); fs = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 19)
    rows = [('cur', '지금', '붉은 기둥 + 도는 화살 뿔 + 바닥 고리'), ('A', '시안 A · 흩어지는 불씨', '네이티의 빛이 새어 나가 불씨처럼 올라감'), ('B', '시안 B · 갈라지는 빛', '몸이 여러 겹으로 어긋나고 바닥에 붉은 금'), ('C', '시안 C · 꺼져 가는 빛', '빛이 바래고 검붉은 연기가 피어오름')]
    cols = [('near', '가까이'), ('top', '위에서 (미로 안 시점)'), ('gate', '미로 입구에서')]
    im = Image.new('RGB', (pad + (W + pad)*3, 40 + (H + lab + pad)*4), '#ffffff'); d = ImageDraw.Draw(im)
    for c, (v, cn) in enumerate(cols): d.text((pad + c*(W + pad), 8), cn, font=fs, fill='#55606a')
    for r, (k, name, desc) in enumerate(rows):
        y = 40 + r*(H + lab + pad); d.text((pad, y + 8), name, font=f, fill='#14202a'); d.text((pad + d.textlength(name, font=f) + 18, y + 15), desc, font=fs, fill='#55606a')
        for c, (v, _) in enumerate(cols): im.paste(Image.open(os.path.join(OUT, f'{k}_{v}.png')).convert('RGB').resize((W, H), Image.LANCZOS), (pad + c*(W + pad), y + lab))
    im.save(os.path.join(OUT, 'naty_fx_sheet.png')); print('sheet', im.size)
def main():
    tmp = tempfile.mkdtemp(prefix='ch5srv_')
    for fn in ['ch5_void_server.py', 'ch5_void_pairs.json', 'spz2splat.py']:
        p = os.path.join(ROOT, 'server', fn)
        if os.path.exists(p): shutil.copy(p, tmp)
    env = dict(os.environ, VOID_PORT='8096', VOID_STATIC='0', CH5_ADMIN_KEY='0101', PYTHONUTF8='1')
    a = subprocess.Popen([sys.executable, 'ch5_void_server.py'], cwd=tmp, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    b = subprocess.Popen([sys.executable, '-m', 'http.server', '8097', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2.5); asyncio.run(run())
    finally:
        a.kill(); b.kill(); time.sleep(.5); shutil.rmtree(tmp, ignore_errors=True)
    if len(KINDS) == 4: sheet()
KINDS = sys.argv[2].split(',') if len(sys.argv) > 2 else ['cur', 'A', 'B', 'C']   # 'cur'만 주면 지금 페이지 모습만 찍는다
main()
