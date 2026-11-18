# 2026-11-18 (사용자): ① 조작 안내 카드(시안 A: 노트북은 실제 키보드 그림에 W A S D·방향키·Shift 표시, 태블릿은 화면 그림에 조이스틱 자리 표시).
#   자일로를 처음 찾아가는 구간(q1)에서 한 번 뜨고, 걷는 화면의 「?」(조작법)로 다시 연다.
# ② 다른 점검에서 찾은 여섯 가지: 낮은 화면의 미션 완료 카드 버튼이 화면 밖 / 미로 안에서 이어할 때 카드가 「정문 동쪽 길」 /
#   대사 「이전」에 포커스를 두고 Enter를 누르면 다음으로 넘어감 / 폰에서 알림이 보이드 버튼에 가림 / 폰 기록 패널에서 스캔 입력칸이 안 보임 /
#   바이킹 완성 대사 때 목적지 기둥·거리 표식이 남음.
# python ch5_patch_ctrl_card_1118.py (한 번만).  태블릿 그림은 ch5_shot_ctrl_walk.py 로 찍어 chapter05/img/ctrl_walk.jpg 에 둔다.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
def rep(a, b, n=1):
    global s; assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

CSS = (
 "#ctrlCard{position:fixed;inset:0;z-index:38;display:none;place-items:center;padding:16px;background:rgba(4,10,20,.62);color:#f4f7ff;-webkit-user-select:none;user-select:none;word-break:keep-all}#ctrlCard[data-on]{display:grid}"
 "#ctrlCard .in{--ku:clamp(18px,min(2.9vw,5.6vh),44px);display:grid;gap:clamp(10px,2.6vh,22px);justify-items:center;width:min(900px,100%);max-height:100%;padding:clamp(16px,4vh,34px) clamp(16px,3vw,40px);border-radius:20px;box-sizing:border-box;background:#0f1d30;box-shadow:0 30px 60px -24px rgba(0,0,0,.7)}"
 "#ctrlCard h1{margin:0;font:800 clamp(20px,4vh,30px)/1.25 var(--sans);letter-spacing:-.01em}"
 "#ctrlCard .kb{display:grid;gap:5px;padding:calc(var(--ku)*.32);border-radius:14px;background:#0a1626;border:1px solid rgba(159,246,255,.28)}#ctrlCard .row{display:flex;gap:5px}"
 "#ctrlCard .k{--u:1;flex:0 0 calc(var(--u)*var(--ku) + (var(--u) - 1)*5px);height:var(--ku);border-radius:6px;box-sizing:border-box;background:#1b2c44;color:#6f86a2;font:700 calc(var(--ku)*.34)/1 var(--sans);display:grid;place-items:center}"
 "#ctrlCard .k.walk{background:#9ff6ff;color:#0f1d30;box-shadow:0 0 0 3px rgba(159,246,255,.25)}#ctrlCard .k.run{background:#ffd400;color:#0f1d30;box-shadow:0 0 0 3px rgba(255,212,0,.25)}"
 "#ctrlCard .stack{display:grid;gap:5px;flex:0 0 var(--ku)}#ctrlCard .k.half{height:calc(var(--ku)/2 - 2.5px);font-size:calc(var(--ku)*.24)}"
 "#ctrlCard .legend{display:flex;gap:6px 26px;flex-wrap:wrap;justify-content:center;font:700 clamp(14px,2.6vh,18px)/1.3 var(--sans)}#ctrlCard .legend span{display:flex;align-items:center;gap:8px}#ctrlCard .legend i{width:16px;height:16px;border-radius:5px;display:block;flex:none}#ctrlCard .legend .c{background:#9ff6ff}#ctrlCard .legend .y{background:#ffd400}#ctrlCard .legend em{font-style:normal;font-weight:600;color:#a9bbd0}"
 "#ctrlCard .tab{position:relative;width:min(560px,100%,72vh);aspect-ratio:16/10;border-radius:22px;box-sizing:border-box;background:#0a1626 url(img/ctrl_walk.jpg) center/cover;border:8px solid #0a1626;outline:3px solid #2a3f5c;overflow:hidden}"
 "#ctrlCard .pad{position:absolute;left:5%;bottom:8%;width:22%;aspect-ratio:1;border-radius:50%;background:rgba(15,29,48,.62);border:2px solid #9ff6ff;box-shadow:0 0 0 6px rgba(159,246,255,.25);display:grid;place-items:center}#ctrlCard .pad i{display:block;width:40%;height:40%;border-radius:50%;background:#9ff6ff;transform:translateY(-55%)}"
 "#ctrlCard .tag{position:absolute;padding:6px 12px;border-radius:999px;background:#9ff6ff;color:#0f1d30;font:800 clamp(12px,2.4vh,16px)/1.2 var(--sans);white-space:nowrap}#ctrlCard .tag.a{left:30%;bottom:15%}#ctrlCard .tag.b{right:8%;top:26%;background:#fff}#ctrlCard .swipe{position:absolute;right:14%;top:44%;width:28%;border-top:3px dashed #fff}"
 "#ctrlCard #ccGo{border:0;border-radius:999px;min-height:48px;padding:0 34px;background:#9ff6ff;color:#0f1d30;font:800 clamp(16px,2.8vh,18px) var(--sans);box-shadow:0 0 0 4px rgba(159,246,255,.22);cursor:pointer}#ctrlCard #ccGo:active{transform:translateY(1px)}#ctrlCard #ccGo:focus-visible{outline:3px solid #fff;outline-offset:3px}"
 "@media (prefers-reduced-motion:no-preference){#ctrlCard[data-on] .in{animation:mcIn .5s cubic-bezier(.16,1,.3,1) both}}"
 # 낮은 화면(가로로 누운 작은 창)에서 미션 완료 카드의 버튼이 화면 밖으로 나가던 것
 "@media (max-height:520px){#qReward{overflow-y:auto}#qReward .in{gap:8px;padding:14px 22px 16px;margin:6px 0;animation:none}#qReward small{font-size:11px;padding:4px 10px 4px 13px}#qReward h1{font-size:22px}#qReward p{font-size:14px;line-height:1.35}#qReward #qrCount{padding:3px 12px;font-size:13px}#qReward .zs{gap:6px;margin-top:0}#qReward .z{padding:8px 12px 10px;gap:2px}#qReward .z span{font-size:12px}#qReward .z code{font-size:24px}#qReward .row{margin-top:2px}#qReward .go{min-height:46px;font-size:16px}#qReward .por{width:30px;height:30px}}"
 # 폰: 알림이 보이드 도움 버튼에 가리던 것, 기록 패널에서 스캔 입력칸이 안 보이던 것 (본문 쪽 스타일보다 앞에 있으므로 body 를 붙여 이기게 한다)
 "@media (max-width:600px) and (min-height:481px){body #toast{bottom:calc(160px + env(safe-area-inset-bottom,0px))}body #panel:not(.closed){max-height:calc(100% - 262px - env(safe-area-inset-top,0px))}}"
 "\n")
m = "</style></head><body>\n"; assert s.count(m) == 1
for name in ("#ctrlCard", "ccGo"): assert name not in s, name
s = s.replace(m, CSS + m)

# 걷기 잠금: 조작 안내 카드가 떠 있는 동안
rep("const k = WALK_KEYS, hold = vn || qRewardEl.dataset.on || $('heroPick').dataset.on ? 0 : 1;", "const k = WALK_KEYS, hold = vn || CTRL || qRewardEl.dataset.on || $('heroPick').dataset.on ? 0 : 1;")
# 대사 「이전」「건너뛰기」에 포커스를 두고 Enter 를 누르면 그 버튼이 눌리게(전에는 다음 대사로 넘어갔다). 마우스로 누른 뒤에는 포커스를 풀어 Space·Enter 가 다시 「다음」이 되게.
rep("document.addEventListener('keydown', e=>{ if(vn && (e.code === 'Space' || e.code === 'Enter')){ e.preventDefault(); vnNext(); } }, true);",
    "document.addEventListener('keydown', e=>{ if(vn && (e.code === 'Space' || e.code === 'Enter')){ if(e.code === 'Enter' && e.target && e.target.closest && e.target.closest('#vnPrev,#vnSkip')) return; e.preventDefault(); vnNext(); } }, true);")
rep("if(e.target.closest('#vnPrev')){ if(vn && vn.i > 0){", "if(e.target.closest('#vnPrev')){ if(e.detail) $('vnPrev').blur(); if(vn && vn.i > 0){")
# 끝난 미니 미션(바이킹 완성 대사 등)에는 목적지 기둥·거리 표식을 두지 않는다
rep("const q = questLive, w = walk; if(!q || !w || q.found){ qNavHide(); return; }", "const q = questLive, w = walk; if(!q || !w || q.found || (mini && mini.phase === 'done')){ qNavHide(); return; }")
# 미로 안에서 저장한 뒤 이어할 때의 카드
rep("  q2chase:{sit:'네이티가 미로 밖으로 날아가 버렸다!', act:'놓치지 말고 끝까지 따라가자!', who:'naty'},\n",
    "  q2chase:{sit:'네이티가 미로 밖으로 날아가 버렸다!', act:'놓치지 말고 끝까지 따라가자!', who:'naty'},\n  q2maze:{sit:'미로 안에서 네이티를 찾고 있었다!', act:'붉은 화살표를 따라 미로 한가운데까지 가자!', who:'naty'},\n")
rep(": q.id === 'q2' && cp.step === 'chase' ? MCARDS.q2chase : MCARDS[q.id];", ": q.id === 'q2' && cp.step === 'chase' ? MCARDS.q2chase : q.id === 'q2' && cp.step === 'maze' ? MCARDS.q2maze : MCARDS[q.id];")
# 조작 안내: 자일로를 처음 찾아가는 구간
rep("(go ? Promise.resolve() : missionCard(q)).then(()=>{ if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name)); }, go ? 900 : 500); } });",
    "(go ? Promise.resolve() : missionCard(q)).then(()=>{ const ctl = ()=>{ if(q.id === 'q1' && walk && questLive === q) ctrlCard(); }; if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name), ctl); else ctl(); }, go ? 900 : 500); } else ctl(); });")
rep("$('walkHelp').onclick = ()=>{ const open = $('walkHint').hidden; $('walkHint').hidden = !open; $('walkHelp').setAttribute('aria-expanded', String(open)); };", "$('walkHelp').onclick = ()=>{ ctrlCard(true); };   /* the same card as the first walk (user, 2026-11-18) */")

JS = r"""/* the controls card (user, 2026-11-18: show a real keyboard so children understand; on a tablet show where the joystick is). Once, on the first walk to 자일로; 「?」 opens it again */
var CTRL = null;
const CTRL_ROWS = [['`','1','2','3','4','5','6','7','8','9','0','-','=',['←',2]], [['Tab',1.5],'Q','W','E','R','T','Y','U','I','O','P','[',']',['\\',1.5]], [['Caps',1.8],'A','S','D','F','G','H','J','K','L',';',"'",['Enter',2.2]], [['Shift',2.4],'Z','X','C','V','B','N','M',',','.','/',['',2.6]], [['Ctrl',1.3],['Fn',1],['',1],['Alt',1.3],['Space',6.1],['Alt',1.2],['Ctrl',1.2],'◀','UD','▶']];
function ctrlKb(){ const WK = ['W','A','S','D','◀','▶']; return '<div class="kb" aria-hidden="true">' + CTRL_ROWS.map(r=> '<div class="row">' + r.map(c=>{ const t = Array.isArray(c) ? c[0] : c, u = Array.isArray(c) ? c[1] : 1; if(t === 'UD') return '<div class="stack"><div class="k half walk">▲</div><div class="k half walk">▼</div></div>'; return `<div class="k${WK.includes(t) ? ' walk' : t === 'Shift' ? ' run' : ''}" style="--u:${u}">${t === 'Space' ? '' : esc(t)}</div>`; }).join('') + '</div>').join('') + '</div>'; }
function ctrlCard(force){ let auto = false, seen = false; try{ auto = !!navigator.webdriver && !localStorage.getItem('void-card-test'); seen = !!localStorage.getItem('void-ctrl-seen'); }catch(e){} if(ffOn() || auto || CTRL || !walk || walk.ride || (!force && seen)) return;
  if(vn || MCARD){ setTimeout(()=>{ if(walk) ctrlCard(force); }, 400); return; }
  let el = $('ctrlCard'); if(!el){ const touch = matchMedia('(pointer:coarse)').matches; el = document.createElement('div'); el.id = 'ctrlCard'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'ccT');
    el.innerHTML = '<div class="in"><h1 id="ccT">이렇게 움직여요</h1>' + (touch ? '<div class="tab" aria-hidden="true"><div class="pad"><i></i></div><span class="tag a">밀어서 걷기</span><i class="swipe"></i><span class="tag b">화면을 끌어 둘러보기</span></div><div class="legend"><span><i class="c"></i>걷기 <em>왼쪽 아래 동그라미 밀기</em></span><span>달리기 <em>끝까지 밀기</em></span></div><button type="button" id="ccGo">알겠어요</button>' : ctrlKb() + '<div class="legend"><span><i class="c"></i>걷기 <em>W A S D 또는 방향키</em></span><span><i class="y"></i>달리기 <em>Shift와 함께</em></span><span>둘러보기 <em>마우스로 화면 끌기</em></span></div><button type="button" id="ccGo">알겠어요 · Space</button>') + '</div>';
    document.body.appendChild(el); el.addEventListener('click', e=>{ e.stopPropagation(); if(e.target.closest('#ccGo') && CTRL) CTRL(); }); }
  try{ localStorage.setItem('void-ctrl-seen', '1'); }catch(e){}
  for(const k in WALK_KEYS) delete WALK_KEYS[k]; walkPad.dx = walkPad.dz = 0; delete el.dataset.on; void el.offsetWidth; el.dataset.on = '1'; sfx('open'); const at = performance.now();
  CTRL = ()=>{ if(performance.now() - at < 700) return; CTRL = null; delete el.dataset.on; sfx('tap'); }; setTimeout(()=>{ try{ $('ccGo').focus(); }catch(e){} }, 60); }
addEventListener('keydown', e=>{ if(!CTRL) return; e.preventDefault(); e.stopImmediatePropagation(); if((e.code === 'Space' || e.code === 'Enter') && !e.repeat) CTRL(); }, true);
window.__ctrl = ()=> !!CTRL;
"""
a = "function natyAsk(q, on){"; assert s.count(a) == 1; s = s.replace(a, JS + a)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("patched")
