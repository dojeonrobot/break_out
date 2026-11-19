# 2026-11-19 (사용자: 전원 들어왔을 때 연출이 아쉽다, 전기가 들어왔다는 느낌이 없다)
#  한낮이라 전구만 켜져서는 티가 안 났다. 연출 첫머리에 화면이 어둑해지고 → 형광등처럼 세 번 깜빡(지직 소리) → 「전기가 들어왔다!」와 함께 번쩍 밝아지며
#  따뜻한 빛이 퍼지고, 그 뒤에 빛 고리·전구·기구 출발이 이어진다. 한 번만 적용: python scripts/pending/ch5_patch_power_fx.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
rep("  PARK_WAKE = {k:0, dur:6.2 + tour.length*2.8, sp:0,", "  PARK_WAKE = {k:0, dur:7.6 + tour.length*2.8, sp:0, fz:0,")
rep("PARK_U.uLv.value = G - 6; sfx('power');\n}", "PARK_U.uLv.value = G - 6; sfx('powerdown');\n}")
rep("  w.sp = sm((k - 1.4)/3.2);\n  const lv = G - 6 + sm((k - 0.7)/2.6)*160; PARK_U.uLv.value = lv;",
    "  /* the surge first (user, 2026-11-19: 전기가 들어왔다는 느낌이 없다): the view dims, flickers three times like a tube catching, then snaps bright with a warm bloom; only then the ring, the bulbs and the rides */\n"
    "  { let el = $('pwFx'); if(!el){ el = document.createElement('div'); el.id = 'pwFx'; el.setAttribute('aria-hidden', 'true'); document.body.appendChild(el); }\n"
    "    const F = [0.62, 0.82, 1.08], ON = 1.4, dark = k < ON ? 0.58*sm(k/0.45) : 0; let flash = 0; F.forEach((t0, i)=>{ if(k >= t0 && k < t0 + 0.08) flash = 0.45 + i*0.12; if(k >= t0 && w.fz === i){ w.fz = i + 1; sfx('zap'); } });\n"
    "    if(k >= ON && w.fz === 3){ w.fz = 4; sfx('power'); sfx('bulbs'); try{ qPop('전기가 들어왔다!'); }catch(e){} }\n"
    "    const glow = k >= ON ? Math.max(0, 1 - (k - ON)/1.6) : 0;\n"
    "    el.style.background = flash ? `rgba(255,248,214,${flash})` : glow ? `radial-gradient(ellipse at 50% 55%, rgba(255,236,150,${(0.5*glow).toFixed(3)}) 0%, rgba(255,214,110,${(0.22*glow).toFixed(3)}) 55%, rgba(255,214,110,0) 100%)` : `rgba(5,9,22,${dark.toFixed(3)})`; el.style.display = (flash || glow || dark) ? 'block' : 'none'; }\n"
    "  w.sp = sm((k - 2.6)/3.2);\n  const lv = G - 6 + sm((k - 1.4)/2.6)*160; PARK_U.uLv.value = lv;")
rep("  const rk = Math.min(1, k/3.4); w.ring.scale.setScalar(1 + rk*720);", "  const rk = Math.min(1, Math.max(0, k - 1.4)/3.4); w.ring.visible = k >= 1.4; w.ring.scale.setScalar(1 + rk*720);")
rep("  if(k >= w.dur){ sceneI.remove(w.ring);", "  if(k >= w.dur){ { const el = $('pwFx'); if(el) el.style.display = 'none'; } sceneI.remove(w.ring);")
rep("    case 'powerdown': ", "    case 'zap':       noise({f0:2600, f1:5200, dur:.09, g:.13, q:2}); tone({f:118, type:'square', dur:.1, g:.07, lp:1400}); tone({f:2100, f2:900, type:'sawtooth', dur:.07, g:.04}); break;\n    case 'powerdown': ")
rep("#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}", "#pwFx{position:fixed;inset:0;z-index:20;pointer-events:none;display:none}\n#tutPin{position:fixed;width:120px;height:120px;pointer-events:none}")
p.write_bytes(s.encode('utf-8')); print('ok')
