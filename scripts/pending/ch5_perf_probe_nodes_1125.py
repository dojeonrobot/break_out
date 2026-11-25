"""섬 노드 수·작은 메시 주인·행렬 갱신 비용(2026-11-25). 정적 서버 8097 필요."""
import asyncio, json
from playwright.async_api import async_playwright
J = r"""(()=>{ let n=0, mesh=0, auto=0, small={}, names={}; __dbg.islRoot.traverse(o=>{ n++; if(o.matrixAutoUpdate) auto++; if(o.isMesh && !o.isInstancedMesh && o.visible){ mesh++; const g=o.geometry; const t=(g.index?g.index.count:g.attributes.position.count)/3; if(t<300){ let p=o; while(p && p.userData.i===undefined) p=p.parent; const k=(p&&p.name)||(p?('i'+p.userData.i):'none'); small[k]=(small[k]||0)+1; const gk=g.type+'|'+o.material.type+(o.material.transparent?'|T':''); names[gk]=(names[gk]||0)+1; } } });
 const top=Object.entries(small).sort((a,b)=>b[1]-a[1]).slice(0,15); const gt=Object.entries(names).sort((a,b)=>b[1]-a[1]).slice(0,10);
 const t0=performance.now(); for(let i=0;i<20;i++) __dbg.islRoot.updateMatrixWorld(); const um=(performance.now()-t0)/20;
 let sn=0; __dbg.islRoot.traverse(()=>sn++);
 return {islNodes:n, sceneNodes:sn, matrixAuto:auto, visMesh:mesh, smallByGroup:top, smallTypes:gt, updateMatrixWorldMs:+um.toFixed(2)}; })()"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
        ctx = await br.new_context(viewport={'width':1366,'height':768}); await ctx.add_init_script("localStorage.setItem('void-reset','9999999999999');")
        pg = await ctx.new_page(); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto('http://127.0.0.1:8097/chapter05/index.html?team=12&world=island', wait_until='load', timeout=120000)
        for _ in range(60):
            if await pg.evaluate('typeof __dbg !== "undefined" && !!__dbg.renderer'): break
            await asyncio.sleep(1)
        await pg.evaluate('__dbg.tutEnd()'); await asyncio.sleep(1); await pg.evaluate("__dbg.setWorld('island',true)"); await asyncio.sleep(4)
        print(json.dumps(await pg.evaluate(J), ensure_ascii=False))
        await br.close()
asyncio.run(main())
