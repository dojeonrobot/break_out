# 2026-11-11 튜토리얼에서 보이드가 설명하는 화면 부분을 확실히 짚기(사용자: 파란 박스 말고, 확대한다든지 아이들이 바로 알아채게).
# 대상만 밝게 남기고 화면 나머지를 어둡게 한 뒤, 대상은 조금 키우고 노란 고리(바깥에서 조여 들어옴)와 「여기!」 꼬리표를 붙인다. 대상이 움직이면(패널이 열리는 중) 따라간다.
# 사용: python ch5_patch_tut_spotlight.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
assert 'tutSpot' not in s and 'tut-zoom' not in s

def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)

swap('</style></head><body>', '''#tutSpot{position:fixed;left:0;top:0;width:0;height:0;z-index:39;pointer-events:none;border-radius:16px;box-shadow:0 0 0 200vmax rgba(8,14,26,.62);opacity:0;transition:opacity .25s ease-out}
#tutSpot::before{content:'';position:absolute;inset:-5px;border-radius:inherit;border:4px solid #ffd84a;animation:tutSpotIn .55s cubic-bezier(.16,1,.3,1) both,tutSpotPulse 1.5s ease-in-out .55s infinite}
#tutSpot b{position:absolute;left:50%;bottom:calc(100% + 18px);transform:translateX(-50%);white-space:nowrap;padding:7px 14px;border-radius:999px;background:#ffd84a;color:#1b2333;font-size:15px;font-weight:800;line-height:1;animation:tutSpotBob 1.3s ease-in-out infinite}
#tutSpot b::after{content:'';position:absolute;left:50%;top:100%;transform:translateX(-50%);border:8px solid transparent;border-top-color:#ffd84a;border-bottom:0}
#tutSpot[data-below="1"] b{bottom:auto;top:calc(100% + 18px)}
#tutSpot[data-below="1"] b::after{top:auto;bottom:100%;border:8px solid transparent;border-bottom-color:#ffd84a;border-top:0}
.tut-zoom{scale:1.08;transition:scale .35s cubic-bezier(.16,1,.3,1)}
#voidVn[data-top="1"]{align-items:flex-start;padding-top:8px;background:linear-gradient(to bottom,rgba(10,20,34,.55),rgba(10,20,34,.12) 45%,transparent 70%)}
#voidVn[data-top="1"] img{height:min(150px,22vh)}
@keyframes tutSpotIn{from{transform:scale(1.9);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes tutSpotPulse{50%{transform:scale(1.045);opacity:.75}}
@keyframes tutSpotBob{50%{translate:0 -5px}}
@media (prefers-reduced-motion:reduce){#tutSpot::before,#tutSpot b{animation:none}.tut-zoom{transition:none}}
</style></head><body>''')

swap('function tutShow(){ const st = TUT[tutStep];', r'''// ---- tutorial spotlight: the part of the page the void is talking about stays bright and grows a little, the rest dims (user, 2026-11-11) ----
let tutSpotEl = null, tutSpotRaf = 0, tutSpotTarget = null;
function tutSpot(target, label){ tutSpotOff(); const el = typeof target === 'string' ? document.querySelector(target) : target; if(!el) return;
  if(!tutSpotEl){ tutSpotEl = document.createElement('div'); tutSpotEl.id = 'tutSpot'; tutSpotEl.setAttribute('aria-hidden', 'true'); tutSpotEl.innerHTML = '<b></b>'; document.body.appendChild(tutSpotEl); }
  tutSpotTarget = el; el.classList.add('tut-zoom'); tutSpotEl.querySelector('b').textContent = label || '여기!'; tutSpotEl.hidden = false;
  const tick = ()=>{ if(tutSpotTarget !== el) return; const r = el.getBoundingClientRect(), pad = 8;
    if(r.width > 1 && r.height > 1){ const st = tutSpotEl.style; st.left = (r.left - pad) + 'px'; st.top = (r.top - pad) + 'px'; st.width = (r.width + pad*2) + 'px'; st.height = (r.height + pad*2) + 'px'; st.opacity = 1; tutSpotEl.dataset.below = r.top < 96 ? '1' : ''; const low = r.top + r.height/2 > innerHeight*0.5; if(low) $('voidVn').dataset.top = '1'; else delete $('voidVn').dataset.top; }   /* a target in the lower half would sit under the dialogue box: the box moves to the top */
    else tutSpotEl.style.opacity = 0;
    tutSpotRaf = requestAnimationFrame(tick); }; tick(); }
function tutSpotOff(){ cancelAnimationFrame(tutSpotRaf); if(tutSpotTarget) tutSpotTarget.classList.remove('tut-zoom'); tutSpotTarget = null; delete $('voidVn').dataset.top; if(tutSpotEl){ tutSpotEl.style.opacity = 0; tutSpotEl.hidden = true; } }
function tutShow(){ tutSpotOff(); const st = TUT[tutStep];''')
swap('function tutEnd(){ voidHide();', 'function tutEnd(){ tutSpotOff(); voidHide();')
# the four steps that point at a part of the page
swap("if(c) c.classList.add('hl'); }, 60);", "if(c) tutSpot(c); }, 60);")
swap("$('panel').classList.add('hl'); const f = document.querySelector('.cardsub input'); if(f) f.classList.add('pulse');", "setTimeout(()=>{ const f = document.querySelector('#list .cardsub'); if(f && tutStep === 17) tutSpot(f); }, 60);")
swap("do:()=>{ $('lMe').classList.add('pulse'); }}", "do:()=>{ tutSpot($('lMe')); }}")
swap("$('lMe').classList.remove('pulse'); $('restoreBtn').classList.add('hl');", "$('lMe').classList.remove('pulse'); tutSpot($('restoreBtn'));")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
