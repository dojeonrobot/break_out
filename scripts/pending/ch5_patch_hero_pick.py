# 2026-11-12 (사용자 결정): 탐험은 제로·리코 중 한 명을 골라 그 캐릭터로만 움직이고, 3인칭·1인칭도 고른다.
#   이유: 두 캐릭터가 뒤따라오는 방식이 떨려서 렉처럼 보였다.
#   - 처음 걷기를 시작할 때 고르는 창(#heroPick)이 뜬다. 고른 값은 태블릿에 저장(localStorage void-hero-<조>).
#   - 걷는 중에는 위쪽 알약의 「캐릭터·시점」으로 다시 고른다.
#   - 고른 캐릭터는 걷는 자리에 바로 선다(뒤따라오는 지연 없음). 고르지 않은 쪽은 걷는 동안 보이지 않는다.
#   - 1인칭: 눈높이 카메라, 캐릭터는 그리지 않는다. 미로도 눈높이로 본다.
#   미션 판정에 쓰는 걷기 이름은 그대로 「리코·제로」다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'heroPick' not in s
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)

CSS = ('#heroPick{position:fixed;inset:0;z-index:34;display:none;place-items:center;overflow:auto;background:color-mix(in srgb,var(--void) 88%,transparent);color:var(--void-fg);-webkit-user-select:none;user-select:none}'
       '#heroPick[data-on]{display:grid}'
       '#heroPick .in{display:grid;gap:18px;justify-items:center;width:min(560px,92vw);margin:16px 0;padding:26px 24px 24px;border-radius:22px;box-sizing:border-box;background:radial-gradient(ellipse at 50% -10%,color-mix(in srgb,var(--void-edge) 30%,transparent),transparent 55%),var(--void);border:1px solid color-mix(in srgb,var(--void-edge) 55%,transparent)}'
       '#heroPick h2{margin:0;font-size:22px;word-break:keep-all}'
       '#heroPick .who,#heroPick .view{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%}'
       '#heroPick .who button,#heroPick .view button{border:1px solid color-mix(in srgb,var(--void-fg) 18%,transparent);background:color-mix(in srgb,var(--void-fg) 6%,transparent);color:var(--void-fg);border-radius:16px;font:700 16px var(--sans);cursor:pointer;transition:border-color .15s,background .15s,transform .12s}'
       '#heroPick .who button{display:grid;justify-items:center;gap:8px;padding:14px 10px 14px}'
       '#heroPick .who img{height:clamp(96px,22vh,150px);max-width:100%;object-fit:contain;object-position:bottom}'
       '#heroPick .view button{display:grid;gap:4px;min-height:64px;padding:12px 10px;text-align:center}'
       '#heroPick .view span{font:500 13px/1.4 var(--sans);color:color-mix(in srgb,var(--void-fg) 72%,transparent);word-break:keep-all}'
       '#heroPick button[aria-pressed="true"]{border-color:#9ff6ff;background:color-mix(in srgb,#9ff6ff 12%,transparent);box-shadow:0 0 0 3px rgba(159,246,255,.18)}'
       '#heroPick button:active{transform:scale(.98)}'
       '#heroPick button:focus-visible{outline:2px solid #9ff6ff;outline-offset:2px}'
       '#heroPick .go{border:0;border-radius:999px;min-height:48px;padding:13px 40px;background:#9ff6ff;color:#06111a;font:700 16px var(--sans);cursor:pointer}'
       '@media (max-height:520px){#heroPick .in{gap:12px;padding:16px 18px}#heroPick .who img{height:80px}}'
       '@media (prefers-reduced-motion:reduce){#heroPick .who button,#heroPick .view button{transition:none}}'
       'html.aux #heroPick{display:none!important}\n')
rep('</style></head><body>\n', CSS + '</style></head><body>\n')
# 알약에 버튼이 하나 늘어 태블릿 세로(820)에서 미션 상자와 겹쳤다: 960 이하에서는 미션 상자를 한 줄 아래로.
# 걷기 화면 규칙은 본문 안의 둘째 스타일 블록에 있어, 그 뒤에 넣어야 이긴다(첫 블록 끝에 넣으면 진다).
_o = '@media(max-width:760px){body.walk #questHud{top:calc(80px + env(safe-area-inset-top,0px));width:min(520px,calc(100vw - 24px))}}\n'
rep(_o, _o + _o.replace('760px', '960px'))
rep('<section id="walkHud" class="glass" hidden aria-live="polite">',
    '<div id="heroPick" role="dialog" aria-modal="true" aria-labelledby="hpT"><div class="in"><h2 id="hpT">누구로 탐험할까요?</h2><div class="who" id="hpWho"></div><div class="view" id="hpView" role="group" aria-label="시점"></div><button type="button" class="go" id="hpGo">시작</button></div></div>\n'
    '<section id="walkHud" class="glass" hidden aria-live="polite">')
rep('<button type="button" id="walkX">나가기</button></section>', '<button type="button" id="walkWho" hidden>캐릭터·시점</button><button type="button" id="walkX">나가기</button></section>')

JS = r'''/* ---------- one explorer of the pair, third or first person (user, 2026-11-12) ---------- */
let HERO = null, FPV = false, heroSel = {n:'제로', fp:false}, heroCb = null;
const HERO_KEY = ()=> `void-hero-${TEAM || 0}`;
function heroLoad(){ HERO = null; FPV = false; try{ const o = JSON.parse(localStorage.getItem(HERO_KEY()) || 'null'); if(o && PAIR_NAMES.includes(o.n)){ HERO = o.n; FPV = !!o.fp; } }catch(e){} return HERO; }
function heroSave(n, fp){ HERO = n; FPV = !!fp; try{ localStorage.setItem(HERO_KEY(), JSON.stringify({n, fp:FPV})); }catch(e){} }
function heroDraw(){
  $('hpWho').innerHTML = ['제로', '리코'].map(n=> `<button type="button" data-n="${n}" aria-pressed="${heroSel.n === n}"><img src="img/chars/${n === '제로' ? 'zero' : 'rico'}.png?v=20261028c" alt=""><b>${n}</b></button>`).join('');
  $('hpView').innerHTML = [[0, '3인칭', '캐릭터가 화면에 보여요'], [1, '1인칭', '캐릭터의 눈으로 봐요']].map(([v, t, d])=> `<button type="button" data-fp="${v}" aria-pressed="${!!v === heroSel.fp}"><b>${t}</b><span>${d}</span></button>`).join(''); }
function heroPick(cb){ heroLoad(); heroSel = {n:HERO || '제로', fp:FPV}; heroCb = cb || null; heroDraw(); $('heroPick').dataset.on = '1'; setTimeout(()=>{ try{ $('hpGo').focus(); }catch(e){} }, 50); }
$('heroPick').addEventListener('click', e=>{ const b = e.target.closest('button'); if(!b) return; e.stopPropagation();
  if(b.dataset.n){ heroSel.n = b.dataset.n; sfx('tap'); heroDraw(); return; }
  if(b.dataset.fp != null){ heroSel.fp = b.dataset.fp === '1'; sfx('tap'); heroDraw(); return; }
  if(b.id === 'hpGo'){ heroSave(heroSel.n, heroSel.fp); delete $('heroPick').dataset.on; sfx('open'); const cb = heroCb; heroCb = null; if(walk) heroApply(); if(cb) cb(); } });
function heroHide(w){ w.hid = w.name === PAIR ? CHAR.filter(x=> PAIR_NAMES.includes(x.n) && x !== w.c).map(x=> ({g:x.g, v:x.g.visible})) : []; w.hid.forEach(h=>{ h.g.visible = false; }); }
function heroApply(){ const w = walk; if(!w || w.name !== PAIR) return; const c = CHAR.find(x=> x.n === HERO); if(!c) return;
  if(c !== w.c){ w.home.forEach(h=>{ h.g.position.copy(h.p); h.g.rotation.y = h.r; }); (w.hid || []).forEach(h=>{ h.g.visible = h.v; }); w.mates.forEach(m=>{ m.g.visible = true; });
    w.c = c; w.mates = [c]; w.home = [{g:c.g, p:c.g.position.clone(), r:c.g.rotation.y}]; heroHide(w); c.g.userData.fx = null; }
  w.fp = FPV; w.pitch = FPV ? -0.05 : -0.32; w.snap = true; $('walkName').textContent = HERO; }
$('walkWho').onclick = ()=>{ if(walk && walk.name === PAIR && !vn) heroPick(null); };
function startWalk(name){
'''
rep('function startWalk(name){\n', JS)
rep("const lead = name === PAIR ? '제로' : name, c = CHAR.find(c=> c.n === lead); if(!c || walk) return; sfx('whoosh');",
    "const lead = name === PAIR ? (heroLoad() || '제로') : name, c = CHAR.find(c=> c.n === lead); if(!c || walk) return;")
rep("  delete $('walkPick').dataset.on;\n  if(W.id !== 'island') setWorld('island', true);",
    "  delete $('walkPick').dataset.on;\n  if(name === PAIR && !HERO){ heroPick(()=> startWalk(name)); return; }   /* the first walk: choose who and how */\n  sfx('whoosh');\n  if(W.id !== 'island') setWorld('island', true);")
rep("walk = {c, name, mates:name === PAIR ? CHAR.filter(x=> PAIR_NAMES.includes(x.n)) : [c], eye, x:p.x, z:p.z, yaw:c.g.rotation.y, pitch:-0.32,",
    "walk = {c, name, mates:[c], fp:name === PAIR && FPV, eye, x:p.x, z:p.z, yaw:c.g.rotation.y, pitch:name === PAIR && FPV ? -0.05 : -0.32,")
rep("  walk.home = walk.mates.map(m=> ({g:m.g, p:m.g.position.clone(), r:m.g.rotation.y}));   // put them back where they stood when the walk ends\n",
    "  walk.home = walk.mates.map(m=> ({g:m.g, p:m.g.position.clone(), r:m.g.rotation.y}));   // put them back where they stood when the walk ends\n  heroHide(walk);   /* the one who was not chosen is not drawn while walking */\n")
rep("$('walkName').textContent = name; $('walkHud').setAttribute", "$('walkName').textContent = name === PAIR ? HERO : name; $('walkWho').hidden = name !== PAIR; $('walkHud').setAttribute")
rep("  walk.home.forEach(h=>{ h.g.position.copy(h.p); h.g.rotation.y = h.r; }); walk = null;", "  (walk.hid || []).forEach(h=>{ h.g.visible = h.v; }); walk.mates.forEach(m=>{ m.g.visible = true; }); delete $('heroPick').dataset.on;\n  walk.home.forEach(h=>{ h.g.position.copy(h.p); h.g.rotation.y = h.r; }); walk = null;")
rep("const k = WALK_KEYS, hold = vn || qRewardEl.dataset.on ? 0 : 1;", "const k = WALK_KEYS, hold = vn || qRewardEl.dataset.on || $('heroPick').dataset.on ? 0 : 1;")
# one explorer stands exactly where the walk is: no follower lag (that lag against the camera was the shake)
rep("else { const fk = 1 - Math.exp(-dt*(inMaze ? 20 : 11)), ox = u.fx, oz = u.fz;", "else { const fk = w.mates.length === 1 ? 1 : 1 - Math.exp(-dt*(inMaze ? 20 : 11)), ox = u.fx, oz = u.fz;")
rep("    m.g.position.set(u.fx, characterGroundY(u.fx, u.fz) + lift, u.fz); m.g.rotation.y = u.fyaw;", "    m.g.position.set(u.fx, characterGroundY(u.fx, u.fz) + lift, u.fz); m.g.rotation.y = u.fyaw; m.g.visible = !w.fp;")
rep("const inMaze = mazeInside(w.x, w.z, w.mazeCamera ? 4 : 1); w.mazeCamera = inMaze;", "const inMazeNow = mazeInside(w.x, w.z, w.mazeCamera ? 4 : 1), inMaze = inMazeNow && !w.fp; w.mazeCamera = inMazeNow;")
rep("document.body.classList.toggle('inmaze', inMaze);", "document.body.classList.toggle('inmaze', inMazeNow);")
rep("  camera.lookAt(_wt); controls.target.copy(_wt); if(PARK_WAKE) parkWakeCam();",
    "  camera.lookAt(_wt);\n  if(w.fp){ const ey = gy + w.eye + lift, cpf = Math.cos(w.pitch), spf = Math.sin(w.pitch); camera.position.set(w.x, ey, w.z); _wt.set(w.x + sy*cpf*10, ey + spf*10, w.z + cy*cpf*10); camera.lookAt(_wt); }   /* first person: the eye line, the explorer is not drawn */\n"
    "  controls.target.copy(_wt); if(PARK_WAKE) parkWakeCam();")
# Space confirms the picker; the mission pill waits; the admin pill can pass it; the debug handle never opens the picker
i = s.index("return true; } return false; };\n  if(on('callDlg')){ go('callGo'); return; }"); j = i + len("return true; } return false; };\n")
s = s[:j] + "  if(on('heroPick')){ go('hpGo'); return; }\n" + s[j:]
rep("startWalk:(n)=> startWalk(n),", "startWalk:(n)=>{ if(n === PAIR && !heroLoad()) heroSave('제로', false); startWalk(n); }, hero:()=> ({n:HERO, fp:FPV, open:!!$('heroPick').dataset.on, walkFp:walk ? !!walk.fp : null, mates:walk ? walk.mates.map(m=> CHAR.find(c=> c.g === m.g).n) : null, shown:CHAR.filter(c=> PAIR_NAMES.includes(c.n)).map(c=> [c.n, c.g.visible])}),")
rep("  if(on('qReward')) return {t:'보상 카드 닫기', run:()=> $('qrMap').click()};", "  if(on('heroPick')) return {t:'캐릭터 고르기 넘기기', run:()=> $('hpGo').click()};\n  if(on('qReward')) return {t:'보상 카드 닫기', run:()=> $('qrMap').click()};")
rep("&& !$('teamPick').dataset.on && !qRewardEl.dataset.on && !$('callDlg').dataset.on", "&& !$('teamPick').dataset.on && !$('heroPick').dataset.on && !qRewardEl.dataset.on && !$('callDlg').dataset.on")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8')); print('ok')
