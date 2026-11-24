# 2026-11-24 사용자: 「시뮬레이션을 돌리는 장면이 없다. 자일로 비밀 연구실에서 버튼을 누르던 뭐 그런 게 있어야지」
#  3막: 연구실 앞 대사 → 연구실 모니터 벽(#labRoom) → 자일로 대사 → 아이가 큰 「가동」 버튼을 누름(탭·Space) → 모니터가 가동 중으로 → 시뮬레이터.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

CSS = ("#lrLaunch{position:absolute;left:50%;bottom:calc(13vh + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:6;display:none;justify-items:center;gap:12px;border:0;padding:0;background:none;cursor:pointer;-webkit-tap-highlight-color:transparent}"
"#lrLaunch[data-on]{display:grid}"
"#lrLaunch i{display:block;width:clamp(96px,12vw,136px);aspect-ratio:1;border-radius:50%;background:radial-gradient(circle at 38% 32%,#d9fdff 0,#7fe9ff 22%,#1fa3d4 62%,#0d5b80 100%);box-shadow:0 10px 0 #06344b,0 14px 30px rgba(0,0,0,.55),0 0 0 8px rgba(127,233,255,.16);transition:transform .12s,box-shadow .12s}"
"#lrLaunch b{font:800 clamp(18px,2vw,22px) var(--sans);color:#06111a;background:#9ff6ff;padding:10px 22px;border-radius:999px;white-space:nowrap}"
"#lrLaunch:active i,#lrLaunch.down i{transform:translateY(7px);box-shadow:0 3px 0 #06344b,0 6px 14px rgba(0,0,0,.55),0 0 0 8px rgba(127,233,255,.3)}"
"#lrLaunch:focus-visible{outline:none}#lrLaunch:focus-visible b{outline:3px solid #ffd84a;outline-offset:3px}"
"@media (prefers-reduced-motion:no-preference){#lrLaunch[data-on] i{animation:lrPulse 1.3s ease-in-out infinite}@keyframes lrPulse{50%{box-shadow:0 10px 0 #06344b,0 14px 30px rgba(0,0,0,.55),0 0 0 18px rgba(127,233,255,.08),0 0 46px rgba(127,233,255,.55)}}}"
"#labRoom[data-launch] .lst{color:#06111a;background:#7fe9ff}\n")
MARK = '</style></head><body>'
if s.count(MARK) != 1: sys.exit('marker')
s = s.replace(MARK, CSS + MARK)

JS = r'''
/* the simulator is started in 자일로's lab, by the child (user, 2026-11-24) */
STORY.simLaunch = [{who:'자일로', text:'세 기록을 모두 시뮬레이터에 넣었어요.'}, {who:'자일로', img:'xylo_point', text:'가운데 가동 버튼을 눌러 주세요!'}];
function simLaunch(){ if(ffOn() || reduce) return Promise.resolve();
  return new Promise(done=>{ fadeThrough('#05070c', ()=>{ labRoomOpen(false); const R = labRoom(); let b = $('lrLaunch'); if(!b){ b = document.createElement('button'); b.type = 'button'; b.id = 'lrLaunch'; b.innerHTML = '<i></i><b>시뮬레이션 가동</b>'; R.d.appendChild(b); }
    setTimeout(()=> say(STORY.simLaunch, ()=>{ b.dataset.on = '1'; setTimeout(()=> b.focus({preventScroll:true}), 60);
      const go = e=>{ if(e && e.type === 'keydown' && e.code !== 'Space' && e.code !== 'Enter') return; if(e){ e.preventDefault(); e.stopImmediatePropagation(); } removeEventListener('keydown', go, true); b.onclick = null;
        b.classList.add('down'); sfx('power'); R.d.dataset.launch = '1'; $('lrSt0').textContent = '시뮬레이션 가동'; R.d.dataset.run = '1';
        setTimeout(()=>{ delete b.dataset.on; b.classList.remove('down'); }, 500);
        setTimeout(()=>{ delete R.d.dataset.run; delete R.d.dataset.launch; labRoomClose().then(done); }, 2400); };
      b.onclick = e=>{ e.stopPropagation(); go(); }; addEventListener('keydown', go, true); }), 700); }); }); }
window.__simLaunch = ()=>{ const b = $('lrLaunch'); return b && b.dataset.on ? 'button' : (LABROOM && LABROOM.d.dataset.on ? 'room' : ''); };
'''
rep("async function playAct(n){", JS + "async function playAct(n){")
rep("  if(n === 3){ stageAt(ACT_STAGE[3], ACT_CAST[3]()); await wait(900); await new Promise(r=> say(STORY.act3pre, r)); STAGED = false; controls.minDistance = 40; await wait(250); }",
    "  if(n === 3){ stageAt(ACT_STAGE[3], ACT_CAST[3]()); await wait(900); await new Promise(r=> say(STORY.act3pre, r)); await simLaunch(); STAGED = false; controls.minDistance = 40; await wait(250); }")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
