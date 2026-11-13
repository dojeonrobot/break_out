# 정전 감사: 전원이 꺼진 상태(조 선택, 미션 1 전)에서 ① 움직이는 물체 ② 빛나는 재질(전원과 무관하게 켜져 있는 것) ③ 탑승객을 시설별로 센다.
# python scripts/pending/ch5_audit_blackout.py <포트> [그림 폴더]
import asyncio, sys, json, os
from playwright.async_api import async_playwright
PORT = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
JS0 = r"""() => { const b = __dbg; b.islRoot.updateMatrixWorld(true); const A = window.__bo = {objs:[], snaps:[]}; b.islRoot.traverse(o=>{ if(!o.isInstancedMesh && !o.isSkinnedMesh) A.objs.push(o); });
  A.snap = ()=> A.snaps.push(A.objs.map(o=> o.matrixWorld.elements.slice(12, 15).concat(o.matrixWorld.elements.slice(0, 3)))); A.snap(); return {power:b.power(), n:A.objs.length}; }"""
JS1 = r"""() => { const b = __dbg, T = b.THREE, A = window.__bo, S = A.snaps; const shown = o=>{ for(let p = o; p; p = p.parent) if(!p.visible) return false; return true; };
  const labelOf = o=>{ for(let p = o; p; p = p.parent){ if(p.userData && p.userData.i != null && b.IB[p.userData.i]) return b.IB[p.userData.i].label; } return '(섬 바닥·기타)'; };
  const mv = {}; A.objs.forEach((o, i)=>{ if(!o.isMesh || !shown(o)) return; const a = S[0][i]; let d = 0; S.forEach(s=>{ d = Math.max(d, Math.hypot(s[i][0] - a[0], s[i][1] - a[1], s[i][2] - a[2]), Math.hypot(s[i][3] - a[3], s[i][4] - a[4], s[i][5] - a[5])); }); if(d < 0.02) return; const k = labelOf(o); (mv[k] = mv[k] || {n:0, max:0}); mv[k].n++; mv[k].max = Math.max(mv[k].max, d); });
  const glow = {}; b.islRoot.traverse(o=>{ if(!(o.isMesh || o.isInstancedMesh) || !shown(o)) return; const m = Array.isArray(o.material) ? o.material[0] : o.material; if(!m || !m.isMeshBasicMaterial || m.visible === false) return; if(m.transparent && m.opacity < 0.08) return;
    const powered = !!(m.userData && (m.userData.powered || m.userData.bulb)) || (m.onBeforeCompile && String(m.onBeforeCompile).length > 60); const k = labelOf(o) + (powered ? ' [전원 연동]' : ' [항상 켜짐]') + (m.map ? ' 그림' : ' #' + m.color.getHexString()); glow[k] = (glow[k] || 0) + (o.isInstancedMesh ? o.count : 1); });
  return {moving:Object.entries(mv).map(([k, v])=> [k, v.n, Math.round(v.max*10)/10]).sort((a, b)=> b[1] - a[1]), glow:Object.entries(glow).sort((a, b)=> b[1] - a[1])}; }"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist']); pg = await br.new_page(viewport={'width': 1180, 'height': 820}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:160])); await pg.route('**/api/void/**', lambda rt: rt.abort()); await pg.add_init_script("localStorage.setItem('void-sound','0');")
        await pg.goto(f'http://127.0.0.1:{PORT}/chapter05/index.html?team=9&world=island&nobatch=1', wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await pg.evaluate("()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display='none'; }); try{ __dbg.tutEnd(); }catch(e){} }"); await asyncio.sleep(3); await pg.evaluate("__dbg.setWorld('island', true)"); await asyncio.sleep(3)
        print(await pg.evaluate(JS0))
        for _ in range(8): await asyncio.sleep(2); await pg.evaluate("__bo.snap()")
        r = await pg.evaluate(JS1); print('== 정전인데 움직이는 것 (시설, 조각 수, 가장 크게 움직인 거리)'); [print('  ', x) for x in r['moving'][:40]]
        print('== 빛나는 재질'); [print('  ', x) for x in r['glow'][:70]]; print('errs', errs[:2])
        if OUT:
            os.makedirs(OUT, exist_ok=True)
            await pg.evaluate("()=>{ const cv = __dbg.renderer.domElement; document.querySelectorAll('body *').forEach(e=>{ if(e !== cv && !e.contains(cv) && e.tagName !== 'SCRIPT' && e.tagName !== 'STYLE') e.style.visibility = 'hidden'; }); }")
            for name, x, z, h, t in (('coaster', -200, 240, 70, 1.2), ('stage', -150, 100, 70, 1.2), ('street', 0, 260, 90, 1.2), ('plaza', 0, 67, 120, 1.0)):
                await pg.evaluate("([cx, cz, h, t])=>{ const T = __dbg.THREE; __dbg.controls.minDistance = 3; __dbg.flyTo(new T.Vector3(cx + h*t*0.5, __dbg.G + h, cz + h*t), new T.Vector3(cx, __dbg.G + 6, cz), 10); }", [x, z, h, t]); await asyncio.sleep(2.2); await pg.screenshot(path=os.path.join(OUT, name + '.png'), timeout=60000)
        await br.close()
asyncio.run(main())
