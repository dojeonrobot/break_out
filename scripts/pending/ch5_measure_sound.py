# 소리가 실제로 얼마나 크게 나가는지 잰다(SND.master에 분석기를 달아 RMS·최댓값, 1.0 = 최대).
# 사용: 정적 서버(python -m http.server 8097, break_out 폴더) 뒤  python ch5_measure_sound.py
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.async_api import async_playwright
URL = 'http://127.0.0.1:8097/chapter05/index.html'
TAP = """(()=>{ const c = SND.ctx; const an = c.createAnalyser(); an.fftSize = 2048; SND.master.connect(an); window.__an = an; window.__buf = new Float32Array(2048); return c.state; })()"""
MEAS = """(async (sec)=>{ const an = window.__an, b = window.__buf; let sum = 0, n = 0, peak = 0; const t0 = performance.now();
  while(performance.now() - t0 < sec*1000){ an.getFloatTimeDomainData(b); for(let i = 0; i < b.length; i++){ const v = b[i]; sum += v*v; n++; if(Math.abs(v) > peak) peak = Math.abs(v); } await new Promise(r=>setTimeout(r, 40)); }
  return {rms:+Math.sqrt(sum/n).toFixed(4), peak:+peak.toFixed(4), mode:SND.mode, bgm:+SND.bgmGain.gain.value.toFixed(3)}; })"""
async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=d3d11', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        pg = await br.new_page(viewport={'width': 1280, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); await pg.route('**/api/void/**', lambda rt: rt.abort())
        await pg.goto(URL, wait_until='domcontentloaded', timeout=120000)
        for _ in range(480):
            try:
                if await pg.evaluate("typeof window.__dbg!=='undefined' && !!window.__dbg.rideState"): break
            except Exception: pass
            await asyncio.sleep(.25)
        await asyncio.sleep(7)
        await pg.mouse.click(640, 400); await asyncio.sleep(.3); print('ctx', await pg.evaluate(TAP))
        print('시작 곡(intro) 3초   ', await pg.evaluate(MEAS + '(3)'))
        await pg.evaluate("(()=>{ document.querySelectorAll('#teamPick,#intro').forEach(e=>{ delete e.dataset.on; e.style.display = 'none'; }); try{ __dbg.tutEnd(); }catch(e){} })()")
        await asyncio.sleep(4)
        print('캠퍼스 배경음 8초    ', await pg.evaluate(MEAS + '(8)'))
        await pg.evaluate("(()=>{ try{ __dbg.setWorld('island'); }catch(e){} })()"); await asyncio.sleep(6)
        print('섬 배경음 8초        ', await pg.evaluate(MEAS + '(8)'))
        for n in sys.argv[1:] or ['void', 'click', 'pop', 'arrive', 'scan']:
            await pg.evaluate("SND.bgmGain.disconnect()") if n == (sys.argv[1:] or ['void'])[0] else None
            await asyncio.sleep(.6); await pg.evaluate(f"sfx('{n}')"); print(f'효과음 {n:8s} (배경음 뺌)', await pg.evaluate(MEAS + '(1.2)'))
        print('errors:', errs[:3]); await br.close()
asyncio.run(main())
