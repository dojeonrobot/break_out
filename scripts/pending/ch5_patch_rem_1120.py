# 2026-11-20 잔재 부수기: Space 연타로 깨지던 것(빗나가면 0.9초 잠금), 끝난 뒤 연타가 대사·탐지로 새던 것, 둘째(때 맞춰 치기) 쉽게·셋째(순서대로 누르기) 어렵게, 화면 요소 키움.
# python -X utf8 scripts/pending/ch5_patch_rem_1120.py   (chapter05/index.html을 고친다, LF 유지)
import os
P = os.path.join(os.path.dirname(__file__), '..', '..', 'chapter05', 'index.html'); src = open(P, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global src; assert src.count(a) == n, (src.count(a), a[:70]); src = src.replace(a, b)
rep("need:kind === 0 ? 6 : kind === 1 ? 5 : 3,", "need:kind === 0 ? 6 : kind === 1 ? 4 : 3,   /* 2026-11-20 (user): the bar was the hardest and the arrows the easiest */")
rep("G2.sp*(1 + G2.hits*0.16)*(G2.boost > now ? 1.7 : 1)*dt", "G2.sp*(1 + G2.hits*0.16)*dt")
rep("Math.max(0.06, 0.13 - G2.hits*0.015)", "Math.max(0.14, 0.2 - G2.hits*0.02)")
rep("(reduce ? 0.55 : 1.7 + G2.hits*0.22)*(G2.boost > now ? 1.5 : 1)", "(reduce ? 0.55 : 1.15 + G2.hits*0.12)")
rep("const n = reduce ? 4 + G2.hits : 6 + G2.hits*2,", "const n = reduce ? 4 + G2.hits : 8 + G2.hits*2,")
rep("G2.limit = reduce ? 9 + n*0.4 : 3 + n*0.33;", "G2.limit = reduce ? 9 + n*0.4 : 2 + n*0.28;")
rep("if(now - G2.tapAt < 170) return; G2.tapAt = now;\n  if(!G2.front){ G2.boost = now + 800; sfx('error'); remSay(G2.kind === 0 ? '빗나갔어. 약점이 앞으로 돌아올 때 쳐' : '빗나갔어. 노란 칸에 들어올 때 쳐'); return; }",
    "if(now - G2.tapAt < 170 || now < (G2.lock || 0)) return; G2.tapAt = now;\n  /* 2026-11-20 (user: Space 연타하면 버그): mashing won both games in two seconds, as a miss cost nothing. A miss now locks the hit for 0.9 s */\n  if(!G2.front){ G2.lock = now + 900; remLock(900); sfx('error'); remSay(G2.kind === 0 ? '빗나갔어! 잠깐 멈췄다가 약점이 앞에 올 때 쳐' : '빗나갔어! 잠깐 멈췄다가 노란 칸에 들어올 때 쳐'); return; }")
rep("function remTap(){", "function remLock(ms){ const el = remPlayEl(), aim = remAimEl(); el.classList.add('lock'); aim.classList.add('lock'); clearTimeout(remLock.t); remLock.t = setTimeout(()=>{ el.classList.remove('lock'); aim.classList.remove('lock'); }, ms); }\nfunction remTap(){")
rep("addEventListener('keydown', e=>{ const G2 = REM.game; if(!G2 || G2.done || vn) return;\n  if(e.code === 'Space'){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat && G2.kind !== 2) remTap(); }",
    "addEventListener('keydown', e=>{ const G2 = REM.game; if(e.code === 'Space' && performance.now() < (REM.quiet || 0)){ e.preventDefault(); e.stopImmediatePropagation(); return; }   /* the Space still being mashed when a remnant breaks skipped the next line and spent the detection chances */\n  if(!G2 || G2.done || vn) return;\n  if(e.code === 'Space'){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat && G2.kind !== 2) remTap(); }")
rep("if(G2.hits >= G2.need){ G2.done = true; cancelAnimationFrame(G2.raf);", "if(G2.hits >= G2.need){ G2.done = true; REM.quiet = now + (reduce ? 1000 : 2000); cancelAnimationFrame(G2.raf);")
rep("()=>{ if(!mini || ride !== R) return; mini.phase = 'ride'; R.down = null; R.pause = false;", "()=>{ if(!mini || ride !== R) return; REM.quiet = performance.now() + 800; mini.phase = 'ride'; R.down = null; R.pause = false;")
CSS = ("/* 2026-11-20 (user: 이거 UI 좀 키우자): the remnant game panel, its bar, arrows and pips are larger; a miss shows as a short lock */\n"
       "body #remPlay{width:min(860px,94vw);gap:14px;padding:18px 24px 22px;border-radius:22px}body #remPlay .hd b{font-size:26px}body #rpPips{gap:10px}body #rpPips i{width:24px;height:24px;border-width:3px}\n"
       "body #remPlay .bar{height:58px;border-radius:12px}body #remPlay .bar .mk{top:-4px;bottom:-4px;width:14px;margin-left:-7px;border-radius:7px}\n"
       "body #remPlay .seq{gap:8px}body #remPlay .seq i{flex:0 1 58px;min-width:0;width:58px;height:58px;border-radius:12px;border-width:3px;font-size:32px}body #remPlay .seq i.now{box-shadow:0 0 0 4px rgba(159,246,255,.3)}body #remPlay .tm{height:14px;border-radius:7px}\n"
       "body #remPlay.lock{box-shadow:0 0 0 4px #ff7a6e,0 10px 30px rgba(0,0,0,.35)}body #remPlay.lock .bar{opacity:.45}body #remAim{width:112px;height:112px;border-width:5px}body #remAim.lock{border-color:#ff7a6e;opacity:.5}\n"
       "@media (max-height:520px){body #remPlay{width:min(640px,94vw);gap:8px;padding:10px 16px 12px}body #remPlay .hd b{font-size:20px}body #rpPips i{width:18px;height:18px}body #remPlay .bar{height:40px}body #remPlay .seq i{flex-basis:42px;width:42px;height:42px;font-size:24px}body #remPlay .tm{height:8px}body #remAim{width:88px;height:88px}}\n")
rep("</style></head><body>", CSS + "</style></head><body>")
open(P, 'w', encoding='utf-8', newline='').write(src); print('patched', len(src))
