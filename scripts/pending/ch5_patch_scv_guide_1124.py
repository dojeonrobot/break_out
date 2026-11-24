# 2026-11-24 사용자: 「보이드」 도움(캠퍼스)에 Scaniverse 찍는 법을 넣자. 그림은 사용자가 준 폰 캡처 8장(chapter05/img/scv/1~8.jpg).
#  한 장씩 넘기는 안내 창 #scvGuide: 왼쪽 실제 화면 + 누를 곳 노란 고리, 오른쪽 단계 번호·할 일 한 줄. Space/탭 = 다음, Esc·× = 닫기.
#  캠퍼스에서 「보이드」를 누르면 지금 할 일 → 제출 방법 → 이 안내 창 순서.
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_text(encoding='utf-8').replace('\r\n', '\n')
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'anchor x{c}: {a[:90]}')
    s = s.replace(a, b)

CSS = ("#scvGuide{position:fixed;inset:0;z-index:45;display:none;place-items:center;padding:72px 16px 20px;box-sizing:border-box;background:rgba(5,9,16,.72);font-family:var(--sans)}"
"#scvGuide[data-on]{display:grid}"
"#scvGuide .in{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);gap:28px;align-items:center;width:min(880px,100%);max-height:100%;padding:24px 28px;box-sizing:border-box;border-radius:24px;background:linear-gradient(180deg,rgba(18,30,50,.97),rgba(8,14,26,.98));border:1px solid rgba(159,246,255,.32);color:#f4f7ff;box-shadow:0 30px 70px -30px #000}"
"#scvGuide .shot{position:relative;height:min(58vh,520px);border-radius:16px;overflow:hidden;background:#0b0f16;border:1px solid rgba(255,255,255,.12)}"
"#scvGuide .shot img{display:block;height:100%;width:auto}"
"#scvGuide .shot.wide{height:auto;width:min(42vw,380px)}#scvGuide .shot.wide img{width:100%;height:auto}"
"#scvGuide .ring{position:absolute;border:4px solid #ffd84a;border-radius:50%;box-shadow:0 0 0 4px rgba(0,0,0,.35),0 0 22px rgba(255,216,74,.7);transform:translate(-50%,-50%);pointer-events:none;animation:scvP 1.2s ease-in-out infinite}"
"@keyframes scvP{50%{transform:translate(-50%,-50%) scale(1.12)}}@media (prefers-reduced-motion:reduce){#scvGuide .ring{animation:none}}"
"#scvGuide small{display:block;font:800 13px var(--mono);letter-spacing:.18em;color:#9ff6ff}"
"#scvGuide .n{display:inline-grid;place-items:center;min-width:44px;height:44px;margin:14px 0 10px;padding:0 12px;border-radius:12px;background:#9ff6ff;color:#06111a;font:800 20px var(--mono);box-sizing:border-box}"
"#scvGuide h2{margin:0 0 8px;font:800 clamp(24px,3vw,32px)/1.3 var(--sans);word-break:keep-all}"
"#scvGuide p{margin:0;font:500 clamp(16px,2vw,19px)/1.6 var(--sans);color:#cfe0ee;word-break:keep-all}"
"#scvGuide .dots{display:flex;gap:6px;margin:22px 0 18px}#scvGuide .dots i{width:10px;height:10px;border-radius:50%;background:rgba(159,246,255,.25)}#scvGuide .dots i.on{background:#9ff6ff}"
"#scvGuide .row{display:flex;gap:10px}"
"#scvGuide .row button{min-height:52px;padding:0 22px;border-radius:999px;font:700 17px var(--sans);cursor:pointer;border:1px solid rgba(159,246,255,.45);background:transparent;color:#f4f7ff}"
"#scvGuide .row button.go{border:0;background:#9ff6ff;color:#06111a;min-width:140px}"
"#scvGuide .row button:disabled{opacity:.35;cursor:default}"
"#scvGuide .x{position:absolute;top:12px;right:12px;width:44px;height:44px;border-radius:50%;border:0;background:rgba(255,255,255,.08);color:#f4f7ff;font:700 22px var(--sans);cursor:pointer}"
"#scvGuide button:focus-visible{outline:3px solid #ffd84a;outline-offset:3px}"
"@media (orientation:portrait),(max-width:700px){#scvGuide .in{grid-template-columns:minmax(0,1fr);justify-items:center;text-align:center;gap:14px;padding:20px 18px}#scvGuide .shot{height:min(44vh,440px)}#scvGuide .shot.wide{width:min(80vw,380px)}#scvGuide .dots,#scvGuide .row{justify-content:center}}"
"@media (max-height:520px){#scvGuide{padding:10px}#scvGuide .in{padding:14px 18px;gap:18px}#scvGuide .shot{height:calc(100vh - 60px)}#scvGuide .n{margin:6px 0;height:34px;min-width:34px;font-size:16px}#scvGuide .dots{margin:10px 0}#scvGuide .row button{min-height:44px}}"
"\n")
MARK = '</style></head><body>'
if s.count(MARK) != 1: sys.exit('marker')
s = s.replace(MARK, CSS + MARK)

JS = r'''
/* ---------- how to scan with Scaniverse (user, 2026-11-24, from the user's own phone captures) ---------- */
const SCV_STEPS = [
  {img:1, t:'「+」 누르기', p:'Scaniverse를 열고 아래 가운데 빨간 「+」를 눌러요.', r:[.5, .868, .22]},
  {img:2, t:'「Splat」 고르기', p:'두 가지 중 위쪽 「Splat」을 골라요.', r:[.5, .629, .9, .14]},
  {img:3, t:'빨간 버튼 누르고 한 바퀴', p:'찍을 것을 화면 가운데에 두고 빨간 버튼을 눌러요. 천천히 한 바퀴 빙 돌며 찍고, 다 돌면 다시 눌러 멈춰요.', r:[.5, .855, .24]},
  {img:4, t:'「Process Now」 누르기', p:'처리가 끝날 때까지 앱을 닫지 말고 기다려요.', r:[.72, .884, .42, .1]},
  {img:5, t:'「Close」 누르기', p:'다 만들어지면 「Close」를 눌러요. 「Post to Map」은 누르지 않아도 돼요.', r:[.277, .886, .42, .1]},
  {img:6, t:'방금 찍은 스캔 누르기', p:'라이브러리 맨 위에 방금 찍은 스캔이 있어요.', r:[.5, .55, .9, .78], wide:true},
  {img:7, t:'「SHARE」 누르기', p:'스캔 화면 아래 오른쪽 「SHARE」를 눌러요.', r:[.81, .873, .2]},
  {img:8, t:'「Share Link」 누르고 복사', p:'「Share Link」를 누르고 링크를 복사해요. 이 앱으로 돌아와 「스캔 링크」 칸에 붙여 넣고 「제출」!', r:[.5, .41, .66, .17], wide:true}];
let SCV_I = 0, SCV_DONE = null;
function scvDlg(){ let d = $('scvGuide'); if(d) return d; d = document.createElement('div'); d.id = 'scvGuide'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-labelledby', 'scvT');
  d.innerHTML = '<div class="in"><button type="button" class="x" id="scvX" aria-label="닫기">×</button><div class="shot" id="scvShot"><img id="scvImg" alt=""><i class="ring" id="scvRing"></i></div><div><small>SCANIVERSE 찍는 법</small><span class="n" id="scvN"></span><h2 id="scvT"></h2><p id="scvP"></p><div class="dots" id="scvDots"></div><div class="row"><button type="button" id="scvPrev">‹ 이전</button><button type="button" class="go" id="scvNext">다음 ›</button></div></div></div>';
  document.body.appendChild(d);
  d.addEventListener('click', e=>{ e.stopPropagation(); if(e.target.closest('#scvX')) scvClose(); else if(e.target.closest('#scvPrev')) scvShow(SCV_I - 1); else if(e.target.closest('#scvNext')) scvShow(SCV_I + 1); else if(e.target === d) scvClose(); });
  addEventListener('keydown', e=>{ if(!d.dataset.on) return; if(e.code === 'Escape'){ e.preventDefault(); e.stopImmediatePropagation(); scvClose(); } else if(e.code === 'Space' || e.code === 'Enter' || e.code === 'ArrowRight'){ e.preventDefault(); e.stopImmediatePropagation(); scvShow(SCV_I + 1); } else if(e.code === 'ArrowLeft'){ e.preventDefault(); e.stopImmediatePropagation(); scvShow(SCV_I - 1); } }, true);
  SCV_STEPS.forEach(st=>{ const im = new Image(); im.src = `img/scv/${st.img}.jpg`; }); return d; }
function scvShow(i){ if(i >= SCV_STEPS.length){ scvClose(); return; } if(i < 0) return; SCV_I = i; const st = SCV_STEPS[i];
  $('scvShot').classList.toggle('wide', !!st.wide); $('scvImg').src = `img/scv/${st.img}.jpg`; $('scvImg').alt = st.t;
  const r = $('scvRing'), w = st.r[2], h = st.r[3]; r.style.left = st.r[0]*100 + '%'; r.style.top = st.r[1]*100 + '%'; r.style.width = w*100 + '%'; r.style.height = h ? h*100 + '%' : 'auto'; r.style.aspectRatio = h ? 'auto' : '1'; r.style.borderRadius = h ? '18px' : '50%';
  $('scvN').textContent = `${i + 1} / ${SCV_STEPS.length}`; $('scvT').textContent = st.t; $('scvP').textContent = st.p;
  $('scvDots').innerHTML = SCV_STEPS.map((_, k)=> `<i class="${k === i ? 'on' : ''}"></i>`).join(''); $('scvPrev').disabled = i === 0; $('scvNext').textContent = i === SCV_STEPS.length - 1 ? '알겠어요' : '다음 ›'; try{ sfx('tap'); }catch(e){} }
function scvGuide(){ const d = scvDlg(); return new Promise(res=>{ SCV_DONE = res; d.dataset.on = '1'; scvShow(0); setTimeout(()=> $('scvNext').focus({preventScroll:true}), 60); }); }
function scvClose(){ const d = $('scvGuide'); if(!d) return; delete d.dataset.on; const f = SCV_DONE; SCV_DONE = null; if(f) f(); }
window.__scv = ()=> $('scvGuide') && $('scvGuide').dataset.on ? {i:SCV_I, n:SCV_STEPS.length} : null;
'''
rep("// the 「보이드」 button (user, 2026-10-28): what to do right now, said one line at a time, then the 내 시점 reminder on the campus",
    JS + "// the 「보이드」 button (user, 2026-10-28): what to do right now, said one line at a time, then the 내 시점 reminder on the campus")
rep("    await voidAsk('다 찍었으면 「공유 → 링크 복사」 해서 카드의 「스캔 링크」 칸에 붙여 넣고 「제출」.', 'idle');",
    "    await voidAsk('다 찍었으면 「공유 → 링크 복사」 해서 카드의 「스캔 링크」 칸에 붙여 넣고 「제출」.', 'idle');\n    await voidAsk('Scaniverse로 찍는 법을 그림으로 한 단계씩 보여 줄게.'); await scvGuide();")
P.write_text(s, encoding='utf-8', newline='\n'); print('patched')
