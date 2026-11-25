"""섬 렉 지점 측정(2026-11-25). 정적 서버 8097에서 chapter05/index.html을 연다.
사용: python -I ch5_perf_island_1125.py [cpu배율=1]
장면: 섬 전경 / 1인칭 걷기(광장) / 걷기(롤러코스터 근처) / 캠퍼스. 각 장면에서
프레임 간격·render CPU·islAnim 상위·placeLabels·드로우콜·삼각형·그림자 메시·전구 수를 잰다."""
import asyncio, json, sys
from playwright.async_api import async_playwright
CPU = float(sys.argv[1]) if len(sys.argv) > 1 else 1
JS = r"""async (label) => { const b = __dbg, r = b.renderer; const out = {label};
  let rT = 0, rN = 0, calls = 0, tris = 0; const render0 = r.render.bind(r);
  r.render = (sc, cam)=>{ const t0 = performance.now(); render0(sc, cam); rT += performance.now() - t0; rN++; calls += r.info.render.calls; tris += r.info.render.triangles; };
  const anims = b.islAnim, orig = anims.slice(), cost = anims.map(()=> 0);
  for(let i = 0; i < anims.length; i++){ const f = orig[i]; anims[i] = t=>{ const t0 = performance.now(); f(t); cost[i] += performance.now() - t0; }; }
  const longs = []; let po; try{ po = new PerformanceObserver(l=>{ for(const e of l.getEntries()) longs.push(Math.round(e.duration)); }); po.observe({type:'longtask'}); }catch(e){}
  let frames = 0; const ft = []; let last = performance.now(); const t0 = performance.now();
  await new Promise(res=>{ function tick(){ const n = performance.now(); ft.push(n - last); last = n; frames++; if(n - t0 < 3000) requestAnimationFrame(tick); else res(); } requestAnimationFrame(tick); });
  r.render = render0; for(let i = 0; i < anims.length; i++) anims[i] = orig[i]; if(po) po.disconnect();
  const tot = ft.reduce((a, c)=> a + c, 0); ft.sort((a, c)=> a - c);
  out.fps = +(frames / (tot/1000)).toFixed(1); out.frameMs = {med:+ft[ft.length >> 1].toFixed(1), p90:+ft[Math.floor(ft.length*0.9)].toFixed(1), max:+ft[ft.length-1].toFixed(1)};
  out.renders = rN; out.renderCpuMs = +(rT/Math.max(1, rN)).toFixed(2); out.callsPerRender = Math.round(calls/Math.max(1,rN)); out.trisPerRender = Math.round(tris/Math.max(1,rN));
  const per = cost.map((c, i)=> [+(c/frames).toFixed(3), orig[i].toString().replace(/\s+/g, ' ').slice(0, 90)]).sort((a, c)=> c[0] - a[0]);
  out.animMs = +per.reduce((a, c)=> a + c[0], 0).toFixed(2); out.animN = anims.length; out.animTop = per.slice(0, 8);
  out.longTasks = longs.slice(0, 10);
  out.programs = r.info.programs ? r.info.programs.length : null; out.geoms = r.info.memory.geometries; out.tex = r.info.memory.textures;
  out.pixelRatio = r.getPixelRatio(); out.shadowAuto = r.shadowMap.autoUpdate;
  out.labelsDom = document.querySelectorAll('.lbl, .label, [class*=lbl]').length; out.domAll = document.querySelectorAll('*').length;
  return out; }"""
SCENE = r"""(()=>{ const r = __dbg.renderer; let cast = 0, vis = 0, inst = 0, instN = 0, skinned = 0, transp = 0;
  const root = __dbg.islRoot || null; const sc = []; (root || {traverse(){}}).traverse(o=>{ if(!o.isMesh) return; if(!o.visible) return; vis++; if(o.castShadow) cast++; if(o.isInstancedMesh){ inst++; instN += o.count; } if(o.isSkinnedMesh) skinned++; const m = o.material; if(m && m.transparent) transp++; });
  const lights = []; (root || {traverse(){}}).traverse(o=>{ if(o.isLight) lights.push(o.type + (o.castShadow ? '*' : '')); });
  return {visMeshes:vis, castShadow:cast, instanced:inst, instances:instN, skinned, transparent:transp, lights:lights.length, lightTypes:[...new Set(lights)], shadowMapSize: (()=>{ let s = null; (root||{traverse(){}}).traverse(o=>{ if(o.isLight && o.castShadow && o.shadow) s = o.shadow.mapSize.x; }); return s; })()}; })()"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-unsafe-webgpu'])
        ctx = await br.new_context(viewport={'width':1366,'height':768}, device_scale_factor=1)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load', timeout=120000)
        for _ in range(60):
            if await pg.evaluate('typeof __dbg !== "undefined" && !!__dbg.renderer'): break
            await asyncio.sleep(1)
        print('GL', await pg.evaluate("(()=>{ const g = __dbg.renderer.getContext(); const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?'; })()"))
        if CPU > 1:
            cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU}); print('cpu x', CPU)
        await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(1)
        await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(4)
        print(json.dumps(await pg.evaluate(SCENE), ensure_ascii=False))
        print(json.dumps(await pg.evaluate(JS, 'island overview'), ensure_ascii=False))
        await pg.evaluate("() => { __dbg.startWalk('리코·제로'); }"); await asyncio.sleep(3)
        print('walk', await pg.evaluate('!!__dbg.walk()'))
        print(json.dumps(await pg.evaluate(JS, 'walk start (gate)'), ensure_ascii=False))
        await pg.evaluate("__dbg.walkTo(0, 120)"); await asyncio.sleep(2)
        print(json.dumps(await pg.evaluate(JS, 'walk plaza'), ensure_ascii=False))
        await pg.evaluate("__dbg.walkTo(-200, -120)"); await asyncio.sleep(2)
        print(json.dumps(await pg.evaluate(JS, 'walk west'), ensure_ascii=False))
        await pg.evaluate("() => { __dbg.stopWalk(); __dbg.setWorld('erica', true); }"); await asyncio.sleep(3)
        print(json.dumps(await pg.evaluate(JS, 'campus'), ensure_ascii=False))
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
