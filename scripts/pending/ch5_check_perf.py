import asyncio, json
from playwright.async_api import async_playwright
JS = r"""async (label) => { const b = __dbg, r = b.renderer; const out = {label};
  // wrap render + islAnim + placeLabels for ~1.5 s
  let rT = 0, rN = 0, lT = 0; const render0 = r.render.bind(r); r.render = (sc, cam)=>{ const t0 = performance.now(); render0(sc, cam); rT += performance.now() - t0; rN++; };
  const anims = b.islAnim, orig = anims.slice(), cost = anims.map(()=> 0); for(let i = 0; i < anims.length; i++){ const f = orig[i]; anims[i] = t=>{ const t0 = performance.now(); f(t); cost[i] += performance.now() - t0; }; }
  const pl0 = b.placeLabels; 
  let frames = 0; const ft = []; let last = performance.now(); const t0 = performance.now(); await new Promise(res=>{ function tick(){ const n = performance.now(); ft.push(n - last); last = n; frames++; if(n - t0 < 1500) requestAnimationFrame(tick); else res(); } requestAnimationFrame(tick); });
  r.render = render0; for(let i = 0; i < anims.length; i++) anims[i] = orig[i];
  ft.sort((a, b)=> a - b); out.frames = frames; out.frameMs = {median:+ft[ft.length >> 1].toFixed(1), p90:+ft[Math.floor(ft.length*0.9)].toFixed(1)};
  out.renderCpuMs = +(rT/Math.max(1, rN)).toFixed(2);
  const per = cost.map((c, i)=> [+(c/frames).toFixed(3), orig[i].toString().replace(/\s+/g, ' ').slice(0, 70)]).sort((a, b)=> b[0] - a[0]);
  out.animTotalMs = +per.reduce((a, c)=> a + c[0], 0).toFixed(2); out.animTop = per.slice(0, 8); out.animN = anims.length;
  const i = r.info.render; out.calls = i.calls; out.tris = i.triangles;
  // label placement cost
  const tl = performance.now(); for(let k = 0; k < 10; k++) b.placeLabels(); out.placeLabelsMs = +((performance.now() - tl)/10).toFixed(2);
  return out; }"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--enable-gpu'])
        ctx = await br.new_context(viewport={'width':1152,'height':720}, device_scale_factor=1); await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load'); await pg.wait_for_timeout(9000)
        await pg.evaluate('__dbg.tutEnd()');await asyncio.sleep(1)
        await pg.evaluate("__dbg.quest().set(['q1','q2','q3']);__dbg.setWorld('island',true)");await asyncio.sleep(1)
        print(json.dumps(await pg.evaluate(JS, 'island overview'), ensure_ascii=False))
        # island, first-person near the ground (walk mode) 
        await pg.evaluate("() => { __dbg.setWorld('island',true);__dbg.startWalk('리코·제로'); }"); await pg.wait_for_timeout(2500)
        assert await pg.evaluate('!!__dbg.walk()')
        print(json.dumps(await pg.evaluate(JS, 'island walk'), ensure_ascii=False))
        await pg.evaluate("() => { __dbg.stopWalk(); __dbg.setWorld('erica', true); }"); await pg.wait_for_timeout(2500)
        print(json.dumps(await pg.evaluate(JS, 'campus'), ensure_ascii=False))
        # mesh buckets on the island: how far could a global merge go?
        print(json.dumps(await pg.evaluate("""(()=>{ const sig = m => { const M = m.material; return M.type + '|' + (M.color ? M.color.getHexString() : '') + '|' + (M.map ? 'map' : '') + '|' + (M.transparent ? 't' + M.opacity : '') + '|' + M.side + '|' + (M.emissive ? M.emissive.getHexString() : ''); };
          const buckets = {}; let n = 0, noUv = 0, multi = 0, kids = 0, dyn = 0, skinned = 0; const dynIn = o => { for(let p = o; p; p = p.parent) if(p.userData && p.userData.dynamic) return true; return false; };
          __dbg.islRoot.traverse(o=>{ if(!o.isMesh || o.isInstancedMesh) return; n++; if(o.isSkinnedMesh){ skinned++; return; } if(Array.isArray(o.material)){ multi++; return; } if(!o.geometry.attributes.uv) noUv++; if(o.children.length) kids++; if(dynIn(o)){ dyn++; return; } const k = sig(o); buckets[k] = (buckets[k] || 0) + 1; });
          const vals = Object.values(buckets).sort((a, b)=> b - a); return {meshes:n, skinned, multiMat:multi, noUv, withChildren:kids, dynamic:dyn, staticBuckets:vals.length, staticMeshes:vals.reduce((a, b)=> a + b, 0), top:vals.slice(0, 12)}; })()"""), ensure_ascii=False))
        print('errs', errs[:1]); assert not errs,errs; await br.close()
asyncio.run(main())
