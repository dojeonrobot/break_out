# 2026-11-18 (사용자): 효과음을 알맞게 더 넣는다(맨 처음 시작할 때 짧은 곡, 누를 때 나는 소리, 스캔본을 올리면 나는 소리 등 여러 경우).
# 소리는 지금처럼 WebAudio 합성이다(파일 없음). 새 소리: intro(시작 곡 약 2.6초) · click(버튼) · pop(알림) · send(제출 보냄) · scan(스캔 접수) · void(보이드가 말할 때) · arrive(좌표 도착).
# 점검용: SND.log = [] 를 넣어 두면 sfx 이름이 쌓인다(소리가 꺼져 있어도).  python ch5_patch_sfx_1118.py (한 번만)
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
def rep(a, b, n=1):
    global s; assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

# 첫 터치 때: 세 음 등장음 대신 짧은 시작 곡
rep("setTimeout(()=>{ sfx('open'); }, 60); setInterval(bgmTick, 100);", "setTimeout(()=>{ sfx('intro'); }, 60); setInterval(bgmTick, 100);")
# 새 소리
rep("  const c = SND.ctx; if(!c || !SND.unlocked || !SND.on) return;\n  const t = c.currentTime;\n  try{ switch(name){\n",
    "  if(SND.log){ SND.log.push(name); if(SND.log.length > 200) SND.log.shift(); }   /* checks only */\n"
    "  const c = SND.ctx; if(!c || !SND.unlocked || !SND.on) return;\n  const t = c.currentTime;\n  try{ switch(name){\n"
    "    case 'intro':     [[72, 0], [76, .16], [79, .32], [84, .48], [79, .72], [84, .88], [88, 1.04]].forEach(([m, d], i)=> tone({f:midiHz(m), type:'triangle', t0:t + d, dur:i === 6 ? 1.5 : .34, g:.13})); [48, 55, 64].forEach(m=> tone({f:midiHz(m), t0:t, a:.25, dur:2.6, g:.06})); [60, 67, 72, 76].forEach(m=> tone({f:midiHz(m), t0:t + 1.04, a:.12, dur:1.6, g:.05})); for(let i = 0; i < 6; i++) tone({f:2200 + Math.random()*2600, t0:t + 1.1 + i*.07, dur:.3, g:.04}); break;\n"
    "    case 'click':     if(t - SND.lastTap < .06) return; SND.lastTap = t; tone({f:920, f2:640, type:'triangle', dur:.06, g:.07}); break;\n"
    "    case 'pop':       tone({f:660, f2:990, dur:.1, g:.08}); break;\n"
    "    case 'send':      tone({f:520, f2:1040, type:'triangle', dur:.14, g:.1}); tone({f:780, f2:1560, type:'triangle', t0:t + .1, dur:.16, g:.08}); break;\n"
    "    case 'scan':      noise({f0:700, f1:5200, dur:.55, g:.07, q:3}); [79, 84, 88, 91].forEach((m, i)=> tone({f:midiHz(m), type:'triangle', t0:t + .28 + i*.1, dur:i === 3 ? .9 : .3, g:.12})); [60, 67].forEach(m=> tone({f:midiHz(m), t0:t + .58, a:.08, dur:1.1, g:.05})); break;\n"
    "    case 'void':      if(t - (SND.lastVoid || 0) < .3) return; SND.lastVoid = t; tone({f:1320, dur:.06, g:.045}); tone({f:1760, t0:t + .07, dur:.08, g:.04}); break;\n"
    "    case 'arrive':    SND.lastVoid = t; [84, 88, 91].forEach((m, i)=> tone({f:midiHz(m), type:'triangle', t0:t + i*.13, dur:.6, g:.12})); tone({f:midiHz(96), t0:t + .39, dur:.9, g:.06}); break;\n")
# 누를 수 있는 것을 누르면 나는 소리(제 소리를 내는 버튼은 바로 앞의 tap 과 겹치지 않게 lastTap 으로 거른다)
rep("// --- 합성 재료\n",
    "addEventListener('click', e=>{ const el = e.target && e.target.closest ? e.target.closest('button, select, summary, a[href], [data-copy], [data-enter], [role=\"button\"], input[type=\"checkbox\"], input[type=\"radio\"]') : null; if(!el || el.id === 'sndBtn' || el.disabled) return; sfx('click'); });   /* a click on anything pressable (user, 2026-11-18) */\n"
    "// --- 합성 재료\n")
# 스캔 링크 제출: 보낼 때, 접수됐을 때, 잘못됐을 때
rep("  const say = (text, kind)=>{ MSG[m.id] = {text, kind}; refreshSubUI(); };\n  const hit = scanIdFrom(input.value);", "  const say = (text, kind)=>{ try{ sfx(kind === 'err' ? 'error' : 'scan'); }catch(e){} MSG[m.id] = {text, kind}; refreshSubUI(); };\n  const hit = scanIdFrom(input.value);")
rep("const btn = form.querySelector('button[type=submit]'); btn.disabled = true;\n", "const btn = form.querySelector('button[type=submit]'); btn.disabled = true; sfx('send');\n")
rep("    .then(st=>{ sfx('open'); clear(); STATE_VER = -1; applyState(st); say(", "    .then(st=>{ clear(); STATE_VER = -1; applyState(st); say(")
rep("    .catch(err=>{ sfx('error'); say(err.message, 'err');", "    .catch(err=>{ say(err.message, 'err');")
# 알림, 보이드가 말할 때, 좌표에 도착했을 때 (sfx 는 뒤쪽에서 선언한 SND 를 쓰므로 일찍 불릴 수 있는 자리는 try 로 감싼다)
rep("function toast(t){ const el=$('toast'); el.textContent=t;", "function toast(t){ try{ sfx('pop'); }catch(e){} const el=$('toast'); el.textContent=t;")
rep("function voidShow(text, pose='say', ms=0){ ", "function voidShow(text, pose='say', ms=0){ try{ sfx('void'); }catch(e){} ")
rep("g.here = true; g.hereAt = Date.now(); voidSay(ZONE_OBJ[m.id] ?", "g.here = true; g.hereAt = Date.now(); try{ sfx('arrive'); }catch(e){} voidSay(ZONE_OBJ[m.id] ?")
io.open(P, "w", encoding="utf-8", newline="").write(s); print("patched")
