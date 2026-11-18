# 2026-11-18 (사용자): 플라잉 카펫·바이킹 공사장을 학생 시점에서 직접 걸어 들어가 본다(검사 영역의 통과 칸 수만으로 뚫렸다고 보지 않기).
#  ① 정문에서 걸어서 닿는 칸을 1m 격자로 구하고(걷기와 같은 walkBlocked), 기구 안쪽(반지름의 0.75)에서 닿는 칸과 가장 깊은 칸까지의 경로를 뽑는다.
#  ② 그 경로를 실제 키 입력(W)으로 걷는다. 방향만 경로 쪽으로 돌려 주고 이동·충돌은 페이지의 걷기 그대로다.
#  ③ 1인칭 화면(안쪽에 처음 든 순간, 가장 깊은 곳)과 위에서 본 그림(걸은 자리에 빨간 점)을 남긴다.
# 로컬 서버: CH5_ADMIN_KEY=0101 python server/ch5_void_server.py (8096).  python ch5_walk_into_rides.py <그림 폴더> [기구 이름,...]
import asyncio, sys, os, json, math, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); RIDES = sys.argv[2].split(',') if len(sys.argv) > 2 else ['플라잉 카펫', '바이킹']
ROOT = pathlib.Path(__file__).resolve().parents[2]; HOOK = "const tutWorld = goWorld;"
T = 11
GPU = ['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']
REACH = r"""()=>{ const b = __dbg, g = b.walkGrid(), W = g.W, H = g.H, X0 = g.X0, Z0 = g.Z0, blk = new Uint8Array(W*H), par = new Int32Array(W*H).fill(-2);
  for(let j = 0; j < H; j++) for(let i = 0; i < W; i++) blk[j*W + i] = b.walkBlocked(X0 + i + .5, Z0 + j + .5) ? 1 : 0;
  let s = -1; for(let d = 0; d < 40 && s < 0; d++){ const i = Math.floor(0 - X0), j = Math.floor(400 - d - Z0); if(!blk[j*W + i]) s = j*W + i; }
  const q = new Int32Array(W*H); let h = 0, t = 0; q[t++] = s; par[s] = -1;
  while(h < t){ const c = q[h++], i = c % W, j = (c - i)/W; for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1]]){ const ni = i + di, nj = j + dj; if(ni < 0 || nj < 0 || ni >= W || nj >= H) continue; const n = nj*W + ni; if(blk[n] || par[n] !== -2) continue; par[n] = c; q[t++] = n; } }
  window.__reach = {W, H, X0, Z0, blk, par, start:[X0 + (s % W) + .5, Z0 + Math.floor(s/W) + .5]}; return {W, H, reached:t, start:window.__reach.start}; }"""
RIDE = r"""(label)=>{ const b = __dbg, R = window.__reach, {W, H, X0, Z0, blk, par} = R, e = b.IB.find(x=> x.label === label); if(!e) return null;
  const r = e.r || 20, rin = Math.max(6, r*0.75), win = Math.ceil(r + 14), rows = []; let all = 0, free = 0, reach = 0, deep = -1, dd = 1e9; const inner = [];
  for(let dz = -win; dz <= win; dz++){ let row = ''; for(let dx = -win; dx <= win; dx++){ const i = Math.floor(e.cx + dx) - X0, j = Math.floor(e.cz + dz) - Z0, c = j*W + i, x = X0 + i + .5, z = Z0 + j + .5, d = Math.hypot(x - e.cx, z - e.cz), inn = d <= rin;
      const bl = blk[c], rc = par[c] !== -2; if(inn){ all++; if(!bl){ free++; if(rc){ reach++; inner.push([x, z]); if(d < dd){ dd = d; deep = c; } } } }
      row += bl ? (inn ? '#' : 'x') : rc ? (inn ? 'R' : 'o') : (inn ? 'F' : '.'); } rows.push(row); }
  const path = []; for(let c = deep; c >= 0; c = par[c]){ const x = X0 + (c % W) + .5, z = Z0 + Math.floor(c/W) + .5; path.push([x, z]); if(Math.hypot(x - e.cx, z - e.cz) > r + 12) break; }
  path.reverse(); return {label, cx:e.cx, cz:e.cz, r, rin, win, all, free, reach, deep:dd === 1e9 ? null : +dd.toFixed(1), path, rows, inner}; }"""
DRIVE = r"""(pts)=>{ const w = __dbg.walk(); if(!w) return false; const D = window.__drv = {pts, i:0, trace:[], done:false, stuck:0, lx:w.x, lz:w.z};
  D.t = setInterval(()=>{ const w = __dbg.walk(); if(!w || D.done){ clearInterval(D.t); return; } const p = D.pts[D.i], dx = p[0] - w.x, dz = p[1] - w.z, d = Math.hypot(dx, dz);
    D.trace.push([+w.x.toFixed(2), +w.z.toFixed(2)]); if(d < 0.45){ D.i++; D.stuck = 0; if(D.i >= D.pts.length) D.done = true; return; }
    w.yaw = Math.atan2(dx, dz); w.pitch = -0.12;   /* forward = (sin yaw, cos yaw) */
    if(Math.hypot(w.x - D.lx, w.z - D.lz) < 0.01) D.stuck++; else D.stuck = 0; D.lx = w.x; D.lz = w.z; if(D.stuck > 180) D.done = 'stuck'; }, 16); return true; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=GPU); pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))   # 조를 고른 학생 기기(관리자 아님), 진행 없음(정전·바이킹 공사장 상태)
        await pg.request.post('http://127.0.0.1:8096/api/void/quest', data=json.dumps({'team': T, 'dev': 'wlk', 'tut': True}), headers={'content-type': 'application/json'})
        await pg.request.post('http://127.0.0.1:8096/api/void/admin/stage', data=json.dumps({'team': T, 'zones': ['z1'], 'done': [], 'act': 1}), headers={'content-type': 'application/json', 'X-Admin-Key': '0101'})   # 기록 1 완료·1막 뒤: 학생이 처음 섬을 걷는 시점(정전, 바이킹 공사장)
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); assert HOOK in src; src = src.replace(HOOK, HOOK + " window.__cap = {camera, controls, G, scene};")
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');localStorage.setItem('void-reset','9999999999999');localStorage.setItem('void-dev','wlk');")
        await pg.goto('http://127.0.0.1:8096/chapter05/index.html?team=%d' % T, wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState && !!window.__cap"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
        print('renderer', await pg.evaluate("(()=>{ const g = document.createElement('canvas').getContext('webgl'), e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?'; })()"))
        print('reach', await pg.evaluate(REACH)); report = []
        for label in RIDES:
            r = await pg.evaluate(RIDE, label)
            if not r: print('없음', label); continue
            print(f"\n== {label}: 중심 ({r['cx']:.0f},{r['cz']:.0f}) 반지름 {r['r']:.0f} · 안쪽(0.75) {r['all']}칸 중 설 수 있는 칸 {r['free']}, 그중 정문에서 걸어서 닿는 칸 {r['reach']} · 가장 깊은 곳은 중심에서 {r['deep']}m")
            col = {'#': (200, 60, 50), 'x': (120, 60, 55), 'R': (60, 200, 90), 'o': (235, 235, 235), 'F': (250, 210, 60), '.': (150, 150, 150)}; rows = r['rows']
            im = Image.new('RGB', (len(rows[0]), len(rows))); px = im.load()
            for j, row in enumerate(rows):
                for i, ch in enumerate(row): px[i, j] = col[ch]
            rec = {'label': label, 'all': r['all'], 'free': r['free'], 'reach': r['reach'], 'deep': r['deep']}
            if r['reach'] and len(r['path']) > 1:
                pts = r['path']; await pg.evaluate("__dbg.startWalk('리코·제로')"); await asyncio.sleep(2.5)
                for _ in range(30):   # 걷기를 시작하면 뜨는 대사·카드를 학생처럼 Space로 넘긴다(떠 있는 동안은 못 걷는다)
                    if not await pg.evaluate("document.querySelectorAll('[data-on]').length"): break
                    await pg.keyboard.press('Space'); await asyncio.sleep(.5)
                print('   걷기 시작 상태', await pg.evaluate("(()=>({walk:!!__dbg.walk(), hero:__dbg.hero(), on:[...document.querySelectorAll('[data-on]')].map(e=> e.id), tut:__dbg.tutState(), sim:__dbg.simState()}))()"))
                await pg.evaluate("([x,z])=> __dbg.walkTo(x, z)", pts[0]); await asyncio.sleep(.5); await pg.evaluate(DRIVE, pts[1:]); await pg.keyboard.down('KeyW')
                shot_in = False; t0 = asyncio.get_event_loop().time(); mind = 1e9
                while asyncio.get_event_loop().time() - t0 < 90:
                    st = await pg.evaluate("(()=>{ const w = __dbg.walk(), D = window.__drv; return {x:w.x, z:w.z, done:D.done, i:D.i}; })()"); d = math.hypot(st['x'] - r['cx'], st['z'] - r['cz']); mind = min(mind, d)
                    if not shot_in and d <= r['rin']: shot_in = True; rec['enter'] = [round(st['x'], 1), round(st['z'], 1)]; await pg.screenshot(path=f"{OUT}/{label}_1_안쪽에 든 순간.jpg", type='jpeg', quality=82)
                    if st['done']: break
                    await asyncio.sleep(.05)
                await pg.keyboard.up('KeyW'); await asyncio.sleep(.6); await pg.screenshot(path=f"{OUT}/{label}_2_가장 깊은 곳.jpg", type='jpeg', quality=82)
                tr = await pg.evaluate("window.__drv.trace"); end = await pg.evaluate("(()=>{ const w = __dbg.walk(); return [w.x, w.z, window.__drv.done]; })()")
                rec.update(walked=len(tr), start=pts[0], end=[round(end[0], 1), round(end[1], 1)], result=str(end[2]), min_dist=round(mind, 1))
                print(f"   키로 걸음: ({pts[0][0]:.0f},{pts[0][1]:.0f}) → ({end[0]:.0f},{end[1]:.0f}) 결과 {end[2]} · 중심까지 가장 가까이 {mind:.1f}m · 안쪽 경계를 넘은 자리 {rec.get('enter')}")
                for (x, z) in tr[::6]:
                    i, j = int(x - (r['cx'] - r['win'])), int(z - (r['cz'] - r['win']))
                    if 0 <= i < im.width and 0 <= j < im.height: px[i, j] = (40, 90, 255)
                await pg.evaluate("__dbg.stopWalk()"); await asyncio.sleep(1)
                await pg.evaluate("""([tr, cx, cz, win])=>{ const c = __cap, T = __dbg.THREE, grp = new T.Group(); grp.name = '__trace'; const m = new T.MeshBasicMaterial({color:0xff2020}), geo = new T.SphereGeometry(0.7, 8, 6);
                  tr.forEach((p, k)=>{ if(k % 5) return; const s = new T.Mesh(geo, m); s.position.set(p[0], __dbg.groundY(p[0], p[1]) + 2.2, p[1]); grp.add(s); }); c.scene.add(grp);
                  document.querySelectorAll('body *').forEach(e=>{ const cv = document.querySelector('canvas'); if(!e.contains(cv) && e !== cv) e.style.setProperty('visibility', 'hidden', 'important'); });
                  c.controls.minDistance = 1; c.camera.position.set(cx, c.G + win*2.3, cz + 0.5); c.controls.target.set(cx, c.G, cz); c.controls.update(); c.camera.lookAt(cx, c.G, cz); }""", [tr, r['cx'], r['cz'], r['win']])
                await asyncio.sleep(2); await pg.screenshot(path=f"{OUT}/{label}_3_위에서 본 걸은 자리.jpg", type='jpeg', quality=85)
                await pg.evaluate("(()=>{ const g = __cap.scene.getObjectByName('__trace'); if(g) __cap.scene.remove(g); document.querySelectorAll('body *').forEach(e=> e.style.removeProperty('visibility')); })()")
            im.resize((im.width*6, im.height*6), Image.NEAREST).save(f"{OUT}/{label}_0_지도.png"); report.append(rec)
        json.dump(report, open(f"{OUT}/walk_into.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('\nerrs', errs[:3]); await br.close()
asyncio.run(main())
