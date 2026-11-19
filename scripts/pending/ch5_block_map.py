# 기구 하나의 걷기 막힘 지도를 그린다: 회색 = 막힌 칸(walkBlocked), 빨강 = 몸 높이(땅~3m)에 실제로 있는 기구 꼭짓점, 파랑 = 길.
#  막힌 칸이 실제 물체에서 얼마나 떨어져 있는지(가장 먼 거리, 3m 넘는 칸 수)도 적는다.  정적 서버 8097.
#  python ch5_block_map.py <결과 png> [기구 이름=롤러코스터] [여유 m=30]
import asyncio, sys, pathlib, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = sys.argv[1]; NAME = sys.argv[2] if len(sys.argv) > 2 else '롤러코스터'; PAD = int(sys.argv[3]) if len(sys.argv) > 3 else 30
HOOK = r"""
;window.__blk = (name, pad)=>{ const b = IB.find(x=> x.label && x.label.indexOf(name) >= 0); if(!b) return {err:IB.filter(x=> x.c === 'ride').map(x=> x.label)};
  islRoot.updateMatrixWorld(true); const bx = new THREE.Box3().setFromObject(b.mesh), x0 = Math.floor(bx.min.x) - pad, x1 = Math.ceil(bx.max.x) + pad, z0 = Math.floor(bx.min.z) - pad, z1 = Math.ceil(bx.max.z) + pad;
  const rows = []; for(let z = z0; z < z1; z++){ let r = ''; for(let x = x0; x < x1; x++) r += onPath(x + .5, z + .5) ? 'p' : walkBlocked(x + .5, z + .5) ? '#' : '.'; rows.push(r); }
  const pts = [], v = new THREE.Vector3(), M = new THREE.Matrix4();
  b.mesh.traverse(m=>{ if(!(m.isMesh || m.isInstancedMesh) || !m.visible || !m.geometry || !m.geometry.attributes.position) return; const pos = m.geometry.attributes.position, n = m.isInstancedMesh ? m.count : 1, st = Math.max(1, Math.floor(pos.count*n/60000));
    for(let k = 0; k < n; k++){ if(m.isInstancedMesh){ m.getMatrixAt(k, M); M.premultiply(m.matrixWorld); } else M.copy(m.matrixWorld);
      for(let i = 0; i < pos.count; i += st){ v.fromBufferAttribute(pos, i).applyMatrix4(M); const gy = groundY(v.x, v.z); if(v.y > gy + 0.3 && v.y < gy + 3) pts.push(Math.round(v.x*10)/10, Math.round(v.z*10)/10); } } });
  return {label:b.label, x0, z0, rows, pts, c:[b.cx, b.cz, b.r]}; };
"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        src = (ROOT / 'chapter05/index.html').read_text(encoding='utf-8'); i = src.rfind('</script>'); src = src[:i] + HOOK + src[i:]
        await pg.route('**/chapter05/index.html*', lambda rt: rt.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
        await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?world=island&team=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__blk === 'function' && typeof window.__dbg !== 'undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(8)
        d = await pg.evaluate(f"window.__blk({json.dumps(NAME)}, {PAD})"); await br.close()
    if 'err' in d: print('기구 이름:', d['err']); return
    rows = d['rows']; H = len(rows); W = len(rows[0]); S = 6; im = Image.new('RGB', (W*S, H*S), (244, 246, 240)); dr = ImageDraw.Draw(im)
    for z, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': dr.rectangle([x*S, z*S, x*S + S - 1, z*S + S - 1], fill=(150, 150, 150) if ch == '#' else (150, 190, 240))
    solid = set(); P = d['pts']
    for k in range(0, len(P), 2):
        px, pz = P[k] - d['x0'], P[k + 1] - d['z0']; dr.rectangle([px*S - 1, pz*S - 1, px*S + 1, pz*S + 1], fill=(210, 40, 40)); solid.add((int(px), int(pz)))
    for g in range(0, W, 10): dr.line([g*S, 0, g*S, H*S], fill=(225, 225, 225))
    for g in range(0, H, 10): dr.line([0, g*S, W*S, g*S], fill=(225, 225, 225))
    # 막힌 칸마다 가장 가까운 실제 물체까지 거리 (바깥과 맞닿은 테두리 칸만)
    free = lambda x, z: 0 <= x < W and 0 <= z < H and rows[z][x] != '#'
    edge = [(x, z) for z in range(H) for x in range(W) if rows[z][x] == '#' and any(free(x + a, z + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    sl = list(solid); far = []
    for x, z in edge:
        dm = min(((x - a)**2 + (z - b)**2) for a, b in sl)**.5 if sl else 99
        if dm > 3: far.append((round(dm, 1), x + d['x0'], z + d['z0'])); dr.rectangle([x*S, z*S, x*S + S - 1, z*S + S - 1], fill=(250, 200, 60))
    im.save(OUT); far.sort(reverse=True)
    print(d['label'], '중심·반지름', d['c'], '격자', W, 'x', H, '| 테두리 칸', len(edge), '| 물체에서 3m 넘게 떨어진 막힌 테두리 칸(노랑)', len(far), '| 가장 먼 것', far[:5], '| errs', errs[:2])
asyncio.run(main())
