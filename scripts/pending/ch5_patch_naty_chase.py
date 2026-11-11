# 2026-11-11 미션 2 「네이티 추격」(사용자 설계): 미로 한가운데서 네이티를 찾으면 네이티가 미로 밖으로 날아가고, 미로 입구에서부터 회전목마 뒤 정원까지 쫓아간다.
#  - 네이티는 기다려 주지 않는다. 일정 거리 넘게 멀어지면 실패 → 「다시 하기」 → 미로 입구에서 다시.
#  - 경로를 세 구간으로 나눠 구간마다 네이티가 빨라진다. 마지막 구간은 달리기보다 빠르다(간신히 도착하도록). 속도·거리는 CHASE 한 줄에서 조절.
#  - 태블릿: 추격 중에는 조이스틱을 끝까지 밀면 달린다(평소에는 원 밖까지 끌어야 달림).
# 사용: python ch5_patch_naty_chase.py [사본경로]
import pathlib, sys, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
assert 'chaseBegin' not in s and 'chaseFail' not in s

def swap(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)

# ---- dialogue (also written into docs/chapter05_script.md; the user edits it there afterwards) ----
Q2FOUND = [
    ('네이티', '미로 한가운데. 네이티의 불꽃이 붉게 일그러져 있다. 몸이 몇 갈래로 갈라졌다가 다시 붙기를 되풀이한다.', True),
    ('제로', '네이티! 찾았다!', False),
    ('리코', '몸이 계속 갈라져……. 일루아가 이만큼 흔들리고 있다는 거야.', False),
    ('네이티', '네이티의 불꽃이 길게 늘어나더니, 울타리 위로 솟구쳐 미로 밖으로 날아간다.', True),
    ('제로', '어, 어디 가!', False),
    ('보이드', '따라가자. 네이티의 자취를 따라가면 비어 있는 흐름을 찾을 수 있을지도 몰라.', False),
    ('리코', '놓치면 안 돼. 뛰자!', False),
]
CHASEDONE = [
    ('네이티', '네이티가 회전목마 뒤 정원에서 멈춘다. 붉은 불꽃이 한자리를 맴돈다.', True),
    ('제로', '멈췄다……. 여기 회전목마잖아. 네이티가 처음 나타났던 곳이야.', False),
    ('보이드', '찾았어. 네이티의 자취가 끝나는 이 자리가, 내 기록이 비어 있던 곳이야.', False),
    ('리코', '네이티는 일루아가 흔들리는 자리로 끌려온 거구나.', False),
    ('보이드', '이 자리의 흐름을 기록했어. 흐름이 이어지는 쪽에서 트윈으로 이어진 캠퍼스 좌표도 찾았어.', False),
    ('리코', '그럼 바로 가서 찍어 오자.', False),
]
def js(lines):
    return '[' + ', '.join('{"who": "%s", "text": "%s"%s}' % (w, t, ', "img": "naty_red", "nar": true' if nar else '') for w, t, nar in lines) + ']'
m = list(re.finditer(r'"q2found": \[.*?\], "record2": \[', s)); assert len(m) == 1, len(m)
s = s[:m[0].start()] + '"q2found": ' + js(Q2FOUND) + ', "chaseDone": ' + js(CHASEDONE) + ', "record2": [' + s[m[0].end():]

# ---- CSS (top level) ----
swap('</style></head><body>', '''#chaseFail{position:fixed;inset:0;z-index:37;display:grid;place-items:center;padding:16px;background:rgba(4,8,16,.62)}
#chaseFail[hidden]{display:none}
#chaseFail .in{width:min(420px,100%);padding:28px 26px 24px;border-radius:18px;background:linear-gradient(180deg,rgba(18,28,46,.97),rgba(8,13,24,.98));border:1px solid rgba(159,246,255,.3);color:#f4f7ff;text-align:center;box-shadow:0 24px 60px -24px #000;animation:rise .35s both}
#chaseFail h2{margin:0 0 10px;font-size:22px;line-height:1.3;word-break:keep-all}
#chaseFail p{margin:0 0 20px;font-size:15px;line-height:1.65;color:#c9d6e6;word-break:keep-all}
#chaseFail button{min-height:48px;padding:0 26px;border:0;border-radius:999px;background:#9ff6ff;color:#06202a;font:800 16px var(--sans);cursor:pointer}
#chaseFail button:active{transform:scale(.98)}
#questHud.far{border-color:#ff8a7a;box-shadow:0 0 0 3px rgba(255,107,94,.35)}
@media (prefers-reduced-motion:reduce){#chaseFail .in{animation:none}}
</style></head><body>''')

# ---- Naty's position while it flies out of the maze and while it is chased ----
swap("  if(following){NATY.position.set(walk.x+Math.cos(walk.yaw)*1.8", "  if(NATY.userData.run){ const r = NATY.userData.run; NATY.position.set(r[0], groundY(r[0], r[1]) + r[2] + Math.sin(t*3)*0.25, r[1]); NATY.rotation.y = r[3] || 0; }\n  if(following){NATY.position.set(walk.x+Math.cos(walk.yaw)*1.8")

# ---- the chase itself ----
swap("function miniStart(q){\n", r'''// ----- q2 · the chase (user design, 2026-11-11): Naty leaves the maze and does not wait; lose sight of it and the chase starts again at the maze entrance -----
// 조절: lead = 출발할 때 네이티가 앞서 있는 거리, lose = 이 거리보다 멀어지면 실패, catchR = 멈춘 네이티에게 이만큼 다가가면 성공,
//       speed = 구간 1·2·3의 네이티 속도(걷기 5.5, 달리기 11), near/spurt = 이 거리 안으로 따라붙으면 네이티가 내는 속도(따라잡히지 않게)
const CHASE = {lead:12, lose:36, catchR:9, speed:[9.4, 10.6, 12.3], near:8, spurt:12.6, back:50};
let chase = null;
function chasePath(){ if(chasePath.R) return chasePath.R;
  const a = mazeEntrance(), e = freeSpot(carousel.position.x, carousel.position.z - CHASE.back); let pts = qRoute(a[0], a[1], e[0], e[1], true).map(p=> [p[0], p[1]]);
  if(Math.hypot(pts[0][0] - a[0], pts[0][1] - a[1]) > 0.5) pts.unshift([a[0], a[1]]); const l = pts[pts.length - 1]; if(Math.hypot(l[0] - e[0], l[1] - e[1]) > 0.5) pts.push([e[0], e[1]]);
  const cum = [0]; for(let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  return chasePath.R = {pts, cum, len:cum[cum.length - 1]}; }
function chaseAt(R, d){ d = Math.max(0, Math.min(R.len, d)); let i = 1; while(i < R.cum.length - 1 && R.cum[i] < d) i++; const a = R.pts[i - 1], b = R.pts[i], seg = R.cum[i] - R.cum[i - 1] || 1, u = (d - R.cum[i - 1])/seg; return [a[0] + (b[0] - a[0])*u, a[1] + (b[1] - a[1])*u, Math.atan2(b[0] - a[0], b[1] - a[1])]; }
function chaseBig(on){ const u = NATY.userData, base = u.s0b ??= (u.s0 ?? NATY.scale.x); u.s0 = on ? base*2.4 : base; if(!on) NATY.scale.setScalar(base); }   /* a small spirit has to stay visible from 30 m behind */
let chaseTrail = null;
function chaseTrailStep(x, z, reset){ if(!chaseTrail){ const g = new THREE.Group(); g.userData.dynamic = true; islRoot.add(g); const m = glowMat(0xff8a6e, 0.75, true); chaseTrail = {g, dots:Array.from({length:22}, ()=>{ const d = new THREE.Mesh(SPH(0.5, 8, 6), m); d.visible = false; d.castShadow = false; g.add(d); return d; }), i:0, last:null}; }
  const T = chaseTrail; if(reset){ T.dots.forEach(d=> d.visible = false); T.last = null; if(x == null) return; }
  T.dots.forEach(d=>{ if(d.visible){ d.scale.multiplyScalar(0.985); if(d.scale.x < 0.25) d.visible = false; } });   /* the trail fades behind it */
  if(!T.last || Math.hypot(x - T.last[0], z - T.last[1]) > 3){ const d = T.dots[T.i = (T.i + 1) % T.dots.length]; d.position.set(x, groundY(x, z) + 2.2, z); d.scale.setScalar(1); d.visible = true; T.last = [x, z]; } }
function chaseIntro(q){ const w = walk; if(!w) return; mini = {q, kind:'chase', phase:'intro'}; miniSave('chase'); $('questHud').hidden = true; qNavHide(); sfx('sparkle'); chaseBig(true);
  const a = [NATY_HIDE[0], NATY_HIDE[1]], b = mazeEntrance(), t0 = performance.now(), dl = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, ux = (b[0] - a[0])/dl, uz = (b[1] - a[1])/dl, yaw = Math.atan2(ux, uz), gy = groundY(a[0], a[1]), far = Math.max(1, (dl + 26)/dl);
  mini.cam = ()=>{ const r = NATY.userData.run; if(!r) return; camera.position.set(a[0] - ux*24, gy + 22, a[1] - uz*24); camera.lookAt(r[0], gy + r[2], r[1]); };   /* from above the maze: Naty rises over the hedges and leaves */
  (function fly(){ if(!mini || mini.phase !== 'intro') return; const k = Math.min(1, (performance.now() - t0)/(reduce ? 400 : 2600)), e = k*k*(3 - 2*k), rise = Math.sin(Math.min(1, k*2.2)*Math.PI/2);
    const x = a[0] + (b[0] - a[0])*e*far, z = a[1] + (b[1] - a[1])*e*far; NATY.userData.run = [x, z, 5.4 + rise*10, yaw]; chaseTrailStep(x, z);
    if(k < 1) requestAnimationFrame(fly); else fadeThrough('#05070c', ()=> chaseBegin(q)); })(); }
function chaseBegin(q){ const w = walk; if(!w) return; const R = chasePath(); q.found = false; questLive = q; mini = {q, kind:'chase', phase:'chase'}; miniSave('chase');
  const p0 = R.pts[0], ahead = chaseAt(R, CHASE.lead), p = chaseAt(R, CHASE.lead);
  w.x = p0[0]; w.z = p0[1]; w.yaw = Math.atan2(ahead[0] - p0[0], ahead[1] - p0[1]); w.pitch = -0.2; w.snap = true; w.imx = w.imz = 0; w.mates.forEach(m=>{ m.g.userData.fx = null; });
  chase = {q, R, s:CHASE.lead, x:p[0], z:p[1], seg:0, last:performance.now(), over:false, max:0, tries:(chase && chase.q === q ? chase.tries : 0) + 1};
  NATY.userData.run = [p[0], p[1], 3, p[2]]; chaseBig(true); chaseTrailStep(p[0], p[1], true); const f = $('chaseFail'); if(f) f.hidden = true; $('questHud').classList.remove('far');
  miniHud(3, '네이티를 놓치지 마라', COARSE ? '멀어지면 놓쳐요 · 조이스틱을 끝까지 밀면 달려요' : '멀어지면 놓쳐요 · Shift를 누르면 달려요'); qPop('네이티를 쫓아라!'); }
function chaseTick(now){ const c = chase, w = walk; if(!c || !w) return; const dt = Math.min(0.05, Math.max(0, (now - c.last)/1000)); c.last = now; if(c.over || vn) return;
  const gap = Math.hypot(w.x - c.x, w.z - c.z), seg = c.s < c.R.len/3 ? 0 : c.s < c.R.len*2/3 ? 1 : 2; c.max = Math.max(c.max, gap);
  if(seg !== c.seg){ c.seg = seg; sfx('sparkle'); qPop(seg === 1 ? '네이티가 더 빨라졌다!' : '네이티가 또 빨라졌다!'); }
  if(c.s < c.R.len){ const v = gap < CHASE.near ? Math.max(CHASE.speed[seg], CHASE.spurt) : CHASE.speed[seg]; c.s = Math.min(c.R.len, c.s + v*dt); const p = chaseAt(c.R, c.s); c.x = p[0]; c.z = p[1]; NATY.userData.run = [p[0], p[1], 3, p[2]]; }
  else if(gap < CHASE.catchR){ chaseWin(); return; }
  chaseTrailStep(c.x, c.z);
  if(gap > CHASE.lose){ chaseFail(); return; }
  const far = gap > CHASE.lose*0.7; if(far !== c.far){ c.far = far; $('questHud').classList.toggle('far', far); $('qhHint').textContent = far ? '네이티가 멀어지고 있어요!' : COARSE ? '멀어지면 놓쳐요 · 조이스틱을 끝까지 밀면 달려요' : '멀어지면 놓쳐요 · Shift를 누르면 달려요'; } }
function chaseFail(){ const c = chase; if(!c || c.over) return; c.over = true; sfx('tap'); $('questHud').classList.remove('far'); for(const k in WALK_KEYS) delete WALK_KEYS[k];
  let el = $('chaseFail'); if(!el){ el = document.createElement('div'); el.id = 'chaseFail'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'chaseFailT');
    el.innerHTML = '<div class="in"><h2 id="chaseFailT">네이티를 놓쳤습니다</h2><p>너무 멀어져서 네이티가 보이지 않습니다.<br>미로 입구에서 다시 따라가세요.</p><button type="button" id="chaseRetry">다시 하기</button></div>'; document.body.appendChild(el);
    el.querySelector('button').onclick = ()=>{ el.hidden = true; const q = chase && chase.q; if(q) fadeThrough('#05070c', ()=> chaseBegin(q)); }; }
  el.hidden = false; try{ el.querySelector('button').focus(); }catch(e){} }
function chaseWin(){ const c = chase; if(!c || c.over) return; c.over = true; $('questHud').classList.remove('far'); $('questHud').hidden = true; qNavHide(); const w = walk; w.yaw = Math.atan2(c.x - w.x, c.z - w.z); w.pitch = -0.05;
  NATY.userData.run = [c.x, c.z, 3, Math.atan2(w.x - c.x, w.z - c.z)]; qPop('네이티가 멈췄다!'); say(STORY.chaseDone, ()=>{ const q = c.q; chase = null; NATY.userData.run = null; chaseBig(false); chaseTrailStep(null, null, true); questComplete(q); }); }
window.__chase = ()=> chase ? {on:!chase.over, s:+chase.s.toFixed(1), len:+chase.R.len.toFixed(1), x:chase.x, z:chase.z, seg:chase.seg, max:+chase.max.toFixed(1), tries:chase.tries, pts:chase.R.pts, cfg:CHASE, fail:!!($('chaseFail') && !$('chaseFail').hidden)} : null;
function miniStart(q){
''')
swap("  if(q.mini === 'maze'){ questComplete(q); return; }", "  if(q.mini === 'maze'){ chaseIntro(q); return; }")
swap("    say(STORY.q2found.slice(-1), ()=> questComplete(q)); return true;", "    chaseBegin(q); return true;   /* left after Naty was found: the chase starts again at the maze entrance */")
swap("function miniTarget(){ if(!mini) return null;", "function miniTarget(){ if(!mini) return null; if(mini.kind === 'chase') return chase ? [chase.x, chase.z] : null;")
swap("  if(mini.kind === 'device' && mini.phase === 'hunt'){ huntTick(now); return; }", "  if(mini.kind === 'chase'){ chaseTick(now); return; }\n  if(mini.kind === 'device' && mini.phase === 'hunt'){ huntTick(now); return; }")
swap("mini = null; miniBox.hidden = true; ['yardDlg'", "mini = null; if(chase || NATY.userData.run){ chase = null; NATY.userData.run = null; chaseBig(false); chaseTrailStep(null, null, true); } { const cf = $('chaseFail'); if(cf) cf.hidden = true; } $('questHud').classList.remove('far'); miniBox.hidden = true; ['yardDlg'")
# the exit scene borrows the camera for a moment (same hook the park wake scene uses)
swap("camera.lookAt(_wt); controls.target.copy(_wt); if(PARK_WAKE) parkWakeCam();", "camera.lookAt(_wt); controls.target.copy(_wt); if(PARK_WAKE) parkWakeCam(); if(mini && mini.cam) mini.cam();")
# the distance on the mission card is the distance to Naty during the chase
swap("function miniHud(step, title, hint){ $('qhStep').textContent", "function miniHud(step, title, hint){ { const lb = $('questHud').querySelector('.nav small'); if(lb) lb.textContent = mini?.kind === 'chase' ? '네이티까지' : '남은 거리'; } $('qhStep').textContent")
swap("$('qhStep').textContent = q.mini === 'loop' ? '1 / 4' : '1 / 3';", "$('qhStep').textContent = q.mini === 'loop' ? '1 / 4' : '1 / 3'; { const lb = $('questHud').querySelector('.nav small'); if(lb) lb.textContent = '남은 거리'; }")
# tablets: during the chase the stick pushed to its rim runs (normally the finger has to leave the pad)
swap("walkPad.run = d > R*1.15;", "walkPad.run = d > R*(chase && !chase.over ? 0.82 : 1.15);")
# the void button during the chase
swap("  if(step==='maze')return '미로 한가운데까지 가 보자.", "  if(step==='chase')return '네이티를 따라가자. 너무 멀어지면 놓쳐. 네이티의 자취 끝에 비어 있는 흐름이 있을 거야.';\n  if(step==='maze')return '미로 한가운데까지 가 보자.")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
