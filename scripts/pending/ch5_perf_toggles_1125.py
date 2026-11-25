"""섬 렉 원인 분해(2026-11-25): 같은 시점에서 하나씩 끄고 render CPU·드로우콜이 얼마나 주는지 잰다.
사용: python -I ch5_perf_toggles_1125.py [cpu배율=1]   (정적 서버 8097 필요)"""
import asyncio, json, sys
from playwright.async_api import async_playwright
CPU = float(sys.argv[1]) if len(sys.argv) > 1 else 1
MEASURE = r"""async (label) => { const r = __dbg.renderer; let rT = 0, rN = 0, calls = 0; const r0 = r.render.bind(r);
  r.render = (sc, cam)=>{ const t0 = performance.now(); r0(sc, cam); rT += performance.now() - t0; rN++; calls += r.info.render.calls; };
  let n = 0; const t0 = performance.now(); await new Promise(res=>{ (function k(){ n++; if(performance.now() - t0 < 2500) requestAnimationFrame(k); else res(); })(); });
  r.render = r0; const el = performance.now() - t0;
  return {label, fps:+(n/(el/1000)).toFixed(1), renderCpuMs:+(rT/Math.max(1,rN)).toFixed(2), calls:Math.round(calls/Math.max(1,rN))}; }"""
CLASSIFY = r"""(()=>{ const root = __dbg.renderer && window.__t ? null : null; const sc = __dbg.camera ? null : null;
  const out = {byGroup:{}, culledOff:0, inFrustum:0, total:0, small:0}; const cam = __dbg.camera || null; return out; })()"""
TOG = {
 'hide visitors (InstancedMesh people)': "(()=>{ const L=[]; __dbg.renderer; window.__h=[]; (__dbg.islRoot).traverse(o=>{ if(o.isInstancedMesh && /visitor|guest|walker|people|queue|crowd/i.test(o.name||'')){ o.visible=false; __h.push(o); } }); return __h.length; })()",
 'restore': "(()=>{ (window.__h||[]).forEach(o=>o.visible=true); window.__h=[]; return 0; })()",
 'hide transparent': "(()=>{ window.__h=[]; __dbg.islRoot.traverse(o=>{ if(o.isMesh && o.visible && o.material && o.material.transparent){ o.visible=false; __h.push(o);} }); return __h.length; })()",
 'hide non-merged small meshes(<300 tris)': "(()=>{ window.__h=[]; __dbg.islRoot.traverse(o=>{ if(o.isMesh && !o.isInstancedMesh && o.visible && o.geometry && ((o.geometry.index?o.geometry.index.count:o.geometry.attributes.position.count)/3)<300){ o.visible=false; __h.push(o);} }); return __h.length; })()",
 'hide all instanced': "(()=>{ window.__h=[]; __dbg.islRoot.traverse(o=>{ if(o.isInstancedMesh && o.visible){ o.visible=false; __h.push(o);} }); return __h.length; })()",
 'hide meshes farther than 250 from camera': "(()=>{ window.__h=[]; const c=__dbg.camera.position, v=new __dbg.THREE.Vector3(); __dbg.islRoot.traverse(o=>{ if(o.isMesh && o.visible && !o.isInstancedMesh){ if(!o.geometry.boundingSphere) o.geometry.computeBoundingSphere(); v.copy(o.geometry.boundingSphere.center).applyMatrix4(o.matrixWorld); const rad=o.geometry.boundingSphere.radius*o.matrixWorld.getMaxScaleOnAxis(); if(v.distanceTo(c)-rad>250){ o.visible=false; __h.push(o);} } }); return __h.length; })()",
}
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width':1366,'height':768}, device_scale_factor=1)
        await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load', timeout=120000)
        for _ in range(60):
            if await pg.evaluate('typeof __dbg !== "undefined" && !!__dbg.renderer'): break
            await asyncio.sleep(1)
        print('dbg keys', await pg.evaluate("Object.keys(__dbg).filter(k=>/cam|THREE|isl|scene|walk/i.test(k)).join(',')"))
        await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(1)
        await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(4)
        if CPU > 1:
            cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU}); print('cpu x', CPU)
        print(json.dumps(await pg.evaluate(MEASURE, 'base overview')))
        # first-person-ish: low camera inside plaza
        has_cam = await pg.evaluate("!!__dbg.camera && !!__dbg.THREE")
        print('has camera/THREE', has_cam)
        for name, js in TOG.items():
            if name == 'restore': continue
            try:
                k = await pg.evaluate(js)
                print(json.dumps(await pg.evaluate(MEASURE, f'{name} [{k}]'), ensure_ascii=False))
            except Exception as e:
                print(name, 'ERR', str(e)[:120])
            await pg.evaluate(TOG['restore'])
        # far plane/pixel ratio
        if has_cam:
            print(json.dumps(await pg.evaluate("(()=>{ const c=__dbg.camera; return {far:c.far, near:c.near, fov:c.fov}; })()")))
        # low camera view (ground, near plaza) to see culling at eye level
        try:
            await pg.evaluate("(()=>{ const c=__dbg.camera; c.position.set(0, 3, 300); c.lookAt(0, 3, 0); })()")
            print(json.dumps(await pg.evaluate(MEASURE, 'eye-level camera (0,3,300) looking north')))
        except Exception as e: print('eye ERR', str(e)[:120])
        print('errs', errs[:3]); await br.close()
asyncio.run(main())
