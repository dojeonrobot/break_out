"""2026-11-04 사용자 지시: 예비 배전선 → 섬 전원 연출 → 네이티가 사라짐 → 미로에서 네이티 발견 → 두 번째 좌표(캠퍼스 2)
→ 관람차 아래 연구실 중간 점검(시뮬레이터 + 노이즈) → 숨겨진 선대의 잔재 3개 탐지·파내기·고리 해체 → 연구실 재실행 → 마지막 좌표(캠퍼스 3).
스카이루프 탑승·서쪽 숲 기록·미로 정원 기록·빛 길잡이·잔재 문양·「네이티가 원래 빛으로」 삭제. 네이티는 환원 전까지 붉게 흔들림.
섬 기록 두 곳은 사용자가 정하는 중(빈칸): 지금은 미션 1·2를 마치면 기존 방식대로 기록 수에 들어간다.
python scripts/pending/ch5_patch_naty_remnant.py  (한 번만)"""
import io, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'chapter05', 'index.html')
h = io.open(P, encoding='utf-8', newline='').read().replace('\r\n', '\n')
assert 'REM_R' not in h, 'already patched'


def rep(a, b, cnt=1):
    global h
    assert h.count(a) == cnt, (a[:80], h.count(a)); h = h.replace(a, b)


def L(who, text, img=None, nar=False):
    o = {'who': who, 'text': text}
    if img: o['img'] = img
    if nar: o['nar'] = True
    return o


NAR = lambda t: L('', t, nar=True)
STORY = {
    'yardDone': [L('제로', '돌아간다! 저쪽 놀이기구도 움직여!'), L('리코', '섬 전체에 전기가 들어왔어!'), L('자일로', '됐어요. 두 분이 섬의 전원을 되살렸습니다.')],
    'natyGone': [NAR('자일로가 주위를 둘러본다. 늘 곁을 맴돌던 네이티가 어디에도 보이지 않는다.'), L('자일로', '……네이티가 없어요.'), L('리코', '아까까지 있었잖아요?'),
                 L('자일로', '네이티는 일루아가 모습을 띤 존재예요. 일루아가 흔들리면 네이티도 흐트러집니다. 전원이 한꺼번에 들어오면서 일루아가 크게 흔들린 것 같아요.'),
                 L('자일로', '빛이 흩어져서 어딘가로 끌려갔을 거예요. 이렇게 흔들리는 건 처음 봅니다. 응축된 일루아가 오래 버티지 못한다는 뜻이에요.'),
                 L('제로', '그럼 환원을 서둘러야 하는 거네요.'),
                 L('자일로', '네. 그러려면 네이티부터 찾아야 해요. 네이티가 끌려간 쪽에 일루아가 흐르던 자리가 있을 겁니다. 관람차 뒤쪽 길부터 찾아봐 주세요.'),
                 L('리코', '알겠어요. 바로 갈게요.')],
    'q2intro': [L('리코', '네이티가 흐트러지는 게 일루아가 흔들린다는 뜻이면, 지금 섬 전체가 위험한 거야.'), L('제로', '빨리 찾자. 관람차 뒤쪽 길이랬어.')],
    'mazeEntrance': [L('제로', '저 울타리 안쪽에서 뭔가 깜빡여.'), L('리코', '미로야. 네이티가 이 안으로 끌려 들어간 것 같아.'), L('제로', '들어가 보자!')],
    'q2found': [L('네이티', '미로 한가운데. 네이티의 불꽃이 붉게 일그러져 있다. 몸이 몇 갈래로 갈라졌다가 다시 붙기를 되풀이한다.', 'naty_red'),
                L('제로', '네이티! 찾았다!'), L('리코', '몸이 계속 갈라져……. 일루아가 이만큼 흔들리고 있다는 거야.'),
                L('네이티', '불꽃 한 줄기가 길게 늘어나 한쪽을 가리킨다. 몇 번을 다시 모여도 같은 쪽으로 끌려간다.', 'naty_red'),
                L('보이드', '잠깐. 네이티가 끌려가는 방향을 재 볼게.'),
                L('보이드', '이 방향은 내 기록이 비어 있는 자리 중 하나야. 트윈으로 이어진 캠퍼스 좌표를 찾았어.'),
                L('제로', '네이티가 기록이 빈 곳을 알려 준 거야?'),
                L('보이드', '일루아가 원래 흐르던 길이 끊긴 곳으로 끌려가는 거야. 그 자리를 채우면 흐름을 하나 더 알 수 있어.'),
                L('리코', '그럼 바로 가서 찍어 오자.')],
    'record2': [L('보이드', '이번에는 관람차 언덕 주변의 흐름을 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.'),
                L('리코', '캠퍼스 두 번째 기록까지 채웠어. 이제 연구실로 가서 지금까지 모은 걸 확인해 보자.')],
    'act2': [L('자일로', '기록이 또 들어왔군요. 관람차 아래 연구실에서 지금까지 모은 걸로 시뮬레이션을 한번 돌려 보죠.'),
             L('제로', '지금까지 모은 걸로 뭘 알 수 있는지 보러 가자!')],
    'deviceIntro': [L('리코', '연구실 문은 관람차 언덕 아래야. 가 보자.')],
    'deviceFound': [L('자일로', '왔군요. 기록이 두 개 모였으니 지금까지의 흐름을 시뮬레이션으로 확인해 봅시다.')],
    'midA': [L('자일로', '이게 지금까지 모은 기록으로 돌린 시뮬레이션이에요.')],
    'midA2': [L('보이드', '기록이 있는 곳은 흐름이 이어졌어. 그런데…….')],
    'midB': [L('리코', '왜 저기로 꺾여요? 기록에는 저런 길이 없는데.'),
             L('자일로', '계산이 틀어지고 있어요. 섬 어딘가에서 무언가가 측정값을 어지럽히고 있습니다. 이대로면 다섯 기록을 다 모아도 시뮬레이션을 믿을 수 없어요.'),
             L('제로', '뭐가 어지럽히는 건데요?'),
             L('자일로', '선대가 일루아를 모을 때 섬 곳곳에 심어 둔 장치가 있었어요. 대부분 치웠는데, 몇 개는 땅이나 건물 밑에 숨어 있어 저도 다 찾지 못했습니다. 아직 켜져 있는 게 있다면 그게 신호를 흐트러뜨리는 거예요.'),
             L('보이드', '노이즈가 번지는 세 곳이 있어. 정확한 자리는 몰라도, 가까이 가면 내가 찾아낼 수 있어.'),
             L('네이티', '연구실 구석의 네이티가 다시 한번 크게 흩어졌다가 모인다.', 'naty_red'),
             L('자일로', '시간이 많지 않아요. 잔재를 찾아서 꺼 주세요. 그래야 남은 기록으로 제대로 된 시뮬레이션을 할 수 있습니다.')],
    'remFirst': [L('제로', '찾았다! 이게 선대의 장치야?'),
                 L('보이드', '응. 오래돼서 거의 다 망가졌는데, 신호를 내는 심장 부분만 아직 돌고 있어. 이게 자일로의 측정을 흐트러뜨려.'),
                 L('보이드', '심장에 걸린 고리를 바깥쪽부터 하나씩 빼면 멈출 거야. 고리의 틈이 위쪽 표시에 닿을 때 눌러.')],
    'remDone': [L('자일로', '노이즈가 사라졌어요. 이제 기록대로 흐름이 이어집니다.'), L('리코', '이제 제대로 나와요. 한 곳만 비었어요.'),
                L('보이드', '마지막 빈자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어. 카드에 띄워 둘게.'),
                L('네이티', '네이티의 빛은 여전히 붉게 흔들린다.', 'naty_red'), L('제로', '잔재를 없앴는데도 네이티는 그대로네…….'),
                L('자일로', '잔재는 계산을 어지럽혔을 뿐이에요. 일루아가 흔들리는 건 아직 환원을 못 했기 때문입니다. 마지막 기록을 서둘러 주세요.'),
                L('제로', '마지막 기록을 스캔하러 가자!')],
}
line_i = h.index('const STORY = {'); line_e = h.index('\n', line_i)
h = h[:line_e + 1] + 'Object.assign(STORY, ' + json.dumps(STORY, ensure_ascii=False) + ');   /* 2026-11-04 네이티 수색·중간 점검·잔재 수색 */\n' + \
    "STORY.act3 = STORY.act3.map(L=> L.text.indexOf('흐름을 방해하던 잔재도') >= 0 ? {...L, text:'네. 시뮬레이션을 어지럽히던 잔재도 없앴고요. 이제 환원 방법을 시험해 봅시다.'} : L);\n" + h[line_e + 1:]

# ---- quests ----
rep("{id:'q1', act:1, who:[PAIR], short:'스카이 루프', title:'섬의 전원을 되살려라', hint:'롤러코스터가 제일 잘 보이는 자리', needs:['z1'], zones:['z2'], restores:'dl-coaster', mini:'loop', r:7, pop:'자일로 발견!'},",
    "{id:'q1', act:1, who:[PAIR], short:'예비 배전선', title:'섬의 전원을 되살려라', hint:'롤러코스터가 제일 잘 보이는 자리', needs:['z1'], zones:[], mini:'loop', r:7, pop:'자일로 발견!'},")
rep("{id:'q2', act:2, who:[PAIR], short:'미로와 연구실', title:'네이티를 찾아라', hint:'관람차 뒤쪽 산책로부터 살펴보기', needs:['z2'], zones:[], restores:'dl-carousel', mini:'maze', r:6, pop:'네이티 발견!'},",
    "{id:'q2', act:1, who:[PAIR], short:'네이티 수색', title:'네이티를 찾아라', hint:'관람차 뒤쪽 길', needs:['z1'], zones:['z2'], mini:'maze', r:6, pop:'네이티 발견!'},")
rep("{id:'q4', act:2, who:[PAIR], short:'흐름의 이상 지점', title:'흐름을 방해하는 원인을 찾아라', hint:'연구실 분석에 표시된 지점', needs:['z2'], zones:['z3'], mini:'device', r:8, pop:'선대의 잔재 발견!'},",
    "{id:'q4', act:2, who:[PAIR], short:'중간 점검·잔재', title:'숨겨진 잔재를 찾아라', hint:'관람차 언덕 아래 연구실', needs:['z2'], zones:['z3'], mini:'device', r:8, pop:'연구실 도착'},")
rep("q.id==='q4' ? deviceSpot() : CAVE_MOUTH; }", "q.id==='q4' ? (buildLabDoor(), LAB_DOOR) : CAVE_MOUTH; }")
rep("return q.id === 'q1' ? '첫 기록을 찾은 뒤' : q.id === 'q2' ? '두 번째 캠퍼스 기록을 찾은 뒤' : q.id==='q4' ? '연구실에서 이상 지점을 확인한 뒤' : '다섯 기록을 찾은 뒤';",
    "return q.id === 'q1' ? '첫 기록을 찾은 뒤' : q.id === 'q2' ? '섬의 전원을 되살린 뒤' : q.id==='q4' ? '두 번째 캠퍼스 기록을 찾은 뒤' : '다섯 기록을 찾은 뒤';")
rep("const STEP_LINE = {found:'찾았던 자리에서 이어서 하자.',", "const STEP_LINE = {hunt:'빨간 원 안으로 가 봐. 내 신호 소리가 빨라지는 쪽에 잔재가 있어.', mid:'연구실에서 시뮬레이션을 다시 보자.', 'device-return':'연구실로 돌아가서 시뮬레이션을 다시 돌려 보자.', found:'찾았던 자리에서 이어서 하자.',")

# ---- q1: power → wake → Naty gone → mission clear (no Sky Loop ride, no forest record) ----
rep("    if(islandRecord('q1')){say(STORY.forestDone,()=>questComplete(q));return true;}if(st==='coordinates'){mini.routes=[0,1,2,3];showRouteCard();return true;}if(['forest','forest-shot','forest-done'].includes(st)){mini.routes=[0,1,2,3];forestWalk(false);return true;}\n    mini.routes=cp.routes||[];if(st === 'station'){ TRAIN.lit = true; miniWalkTo(3, '스카이 루프 역으로', '선로 아래 계단', STATION.spot, 9, rideBoard); }",
    "    if(st !== 'yard' && st !== 'found'){ TRAIN.lit = true; say(STORY.natyGone, ()=> questComplete(q)); return true; }\n    if(false){}")
rep("  setTimeout(()=> parkWake(()=> say(STORY.yardDone,\n    ()=> miniWalkTo(3, '스카이 루프 역으로', '선로 아래 계단', STATION.spot, 9, rideBoard))), 700); }",
    "  setTimeout(()=> parkWake(()=> say([...STORY.yardDone, ...STORY.natyGone], ()=> questComplete(mini ? mini.q : QUESTS[0]))), 700); }")
rep("{ const saved=miniLoad(),cp=saved?.q===q.id?saved:islandRecord(q.id)?{q:q.id,step:q.id==='q1'?'forest-done':'lab'}:null;",
    "{ const saved=miniLoad(),cp=saved?.q===q.id?saved:null;")

# ---- q2: the maze, no light guide; found → coordinate → done ----
rep("    if(st==='maze'){q.mazeEntered=true;questLive=q;mini=null;miniHud(2,'네이티를 찾아라','미로 안쪽의 붉은 빛을 따라가기');return true;}\n    mini={q,kind:'maze',phase:'walk'};buildLabDoor();mazeToLab(false);",
    "    if(st==='maze'){q.mazeEntered=true;questLive=q;mini=null;miniHud(2,'네이티를 찾아라','미로 한가운데까지 가기');return true;}\n    say(STORY.q2found.slice(-1), ()=> questComplete(q)); return true;")
rep("say(STORY.mazeEntrance,()=>{$('qhT').textContent='네이티를 찾아라';$('qhHint').textContent='미로 안쪽의 붉은 빛을 따라가기';",
    "say(STORY.mazeEntrance,()=>{$('qhT').textContent='네이티를 찾아라';$('qhHint').textContent='미로 한가운데까지 가기';")
rep("  if(q.mini === 'maze'){ mini={q,kind:'maze',phase:'walk'};buildLabDoor();miniSave('naty-shot');mazeToLab(true);return;}",
    "  if(q.mini === 'maze'){ questComplete(q); return; }")
rep("  const guide=mini||questLive;if(!guide)return; if(guide.cellD == null){ guide.cellD = d; return; } if(d === guide.cellD) return;\n  NATY.userData.hold = {color:0xe05a4e,t:now,keep:true}; NATY.userData.guideBright=d<guide.cellD; if(d > guide.cellD && now - (guide.farAt || 0) > 4000){ guide.farAt = now; qPop('막다른 길'); } guide.cellD = d; }",
    "  NATY.userData.guideBright = false; }   /* 2026-11-04: no light guide in the maze (user) */")

# ---- q4: mid-check and the remnant hunt ----
rep("  if(q.mini==='device'){mini={q,kind:'device',phase:'break',hits:0};miniSave('device',{hits:0});deviceOpen();return;}",
    "  if(q.mini==='device'){mini={q,kind:'device',phase:'mid',got:[]};midCheck(q);return;}")
rep("  else if(q.mini==='device'){mini={q,kind:'device',phase:st==='device-return'?'walk':'break',hits:cp.hits||0};if(st==='device-return')deviceReturn();else deviceOpen(true);}",
    "  else if(q.mini==='device'){mini={q,kind:'device',phase:st,got:cp.got||[]};if(st==='device-return'){remBuild();remBack();}else if(st==='hunt')huntStart();else{midCheck(q);return true;}}")
rep("function miniTarget(){ if(!mini) return null;", "function miniTarget(){ if(!mini) return null; if(mini.kind === 'device' && mini.phase === 'hunt') return remNext();")
rep("  if(mini.phase === 'walk' && mini.target && !mini.arrived){", "  if(mini.kind === 'device' && mini.phase === 'hunt'){ huntTick(now); return; }\n  if(mini.phase === 'walk' && mini.target && !mini.arrived){")
rep("miniGo.addEventListener('pointerdown', e=>{ if(ride){ ride.press = true; miniGo.setPointerCapture(e.pointerId); e.preventDefault(); } });\n['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev=> miniGo.addEventListener(ev, ()=>{ if(ride) ride.press = false; }));",
    "miniGo.addEventListener('pointerdown', e=>{ const hunt = mini && mini.kind === 'device' && mini.phase === 'hunt'; if(ride || hunt){ if(ride) ride.press = true; else mini.press = true; miniGo.setPointerCapture(e.pointerId); e.preventDefault(); } });\n['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev=> miniGo.addEventListener(ev, ()=>{ if(ride) ride.press = false; if(mini) mini.press = false; }));")
rep("  if(on('deviceDlg')){if(mini?.hits>=3)go('dvContinue');return;}", "  if(on('remDlg')){ go('rmGo'); return; }\n  if(on('deviceDlg')){if(mini?.hits>=3)go('dvContinue');return;}")

anchor = "// Keep keyboard navigation within the active analysis/game without intercepting dialogue controls."
REMCODE = r'''// ---------- mission 3 (user, 2026-11-04): the lab's mid-check, then three hidden remnants found by the void's detector and dismantled ----------
// The remnants are not ruining the Illua: they scramble Xylo's simulation. They are hidden (under ground, under a building, at the water's edge) and never
// visible by just walking past: only the red circles from the mid-check, the void's beeps and a held 「파내기」 reveal one. Dismantling = take the three
// rings off the core, outermost first, each when its gap meets the mark on top.
const REM_R = 46, REM = {spots:null, models:[], rings:[], game:null};
function remSpots(){ if(REM.spots) return REM.spots;
  const car = MI.find(m=> m.id === 'dl-carousel'), cb = car && car.b, lake = IB.find(b=> /레이크|호수|LAKE/i.test(b.label || ''));
  const out = (b, d)=>{ const L = Math.hypot(b.cx, b.cz) || 1; return [b.cx + b.cx/L*((b.r || 30) + d), b.cz + b.cz/L*((b.r || 30) + d)]; };
  const seeds = [[-418, -88, '땅 밑'], cb ? [...out(cb, 16), '건물 아래'] : [120, -60, '건물 아래'], lake ? [...out(lake, 6), '물가'] : [-120, 120, '물가']];
  REM.spots = seeds.map(([x, z, kind], i)=>{ const s = freeSpot(x, z), a = i*2.1 + 0.7, off = 14 + i*4; return {x:s[0], z:s[1], kind, cx:s[0] + Math.cos(a)*off, cz:s[1] + Math.sin(a)*off}; });
  return REM.spots; }
function remBuild(){ if(REM.models.length) return; remSpots().forEach((s, i)=>{
  const g = new THREE.Group(); g.name = 'remnant-' + i; g.userData.dynamic = true; const y0 = groundY(s.x, s.z) - 0.2; g.position.set(s.x, y0 - 7, s.z); g.visible = false; islRoot.add(g);
  add(g, CYL(3.2, 3.8, 0.8, 10), mat(0x5d5f5a));
  const parts = [[-1.6, 0.8, -0.6, 0.25], [1.5, 0.9, 0.4, -0.3], [0, 1.1, 1.4, 0.1]].map(([x, y, z, r], k)=>{ const p = add(g, BOX(2.2, 2, 1.6), mat(k%2 ? 0x6e7570 : 0x7b7264), x, y, z); p.rotation.z = r; return p; });
  const core = add(g, new THREE.IcosahedronGeometry(0.9, 0), glowMat(0xff6a4e, 0.9), 0, 3.6, 0, false);
  const rings = [2.4, 1.9, 1.4].map((r, k)=>{ const m = add(g, new THREE.TorusGeometry(r, 0.13, 6, 28), mat(0x9aa0a6), 0, 3.6, 0, false); m.rotation.x = Math.PI/2 + k*0.5; return m; });
  REM.models.push({g, parts, core, rings, s, y0, state:0}); });
  islAnim.push(t=> REM.models.forEach((m, i)=>{ if(m.state !== 1) return; m.core.rotation.y = t*2; m.rings.forEach((r, k)=>{ if(r.visible) r.rotation.z = t*(0.8 + k*0.5)*(k%2 ? -1 : 1); }); m.core.material.opacity = 0.55 + 0.4*Math.abs(Math.sin(t*6 + i)); })); }
function remTween(ms, f){ if(reduce){ f(1); return; } const t0 = performance.now(); const step = ()=>{ const k = Math.min(1, (performance.now() - t0)/ms); f(k); if(k < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); }
function remCollapse(m, instant){ m.state = 2; m.g.visible = true; m.core.visible = false; m.rings.forEach(r=> r.visible = false);
  const from = m.parts.map(p=> [p.position.y, p.rotation.z]); const end = (p, k, i)=>{ p.position.y = from[i][0]*(1 - k) + 0.5*k; p.rotation.z = from[i][1] + k*(i%2 ? -1.2 : 1.1); };
  if(instant){ m.g.position.y = m.y0; m.parts.forEach((p, i)=> end(p, 1, i)); return; } remTween(900, k=> m.parts.forEach((p, i)=> end(p, k, i))); }
function remNext(){ const w = walk, got = mini ? mini.got || [] : []; let best = null, bd = 1e9; remSpots().forEach((s, i)=>{ if(got.includes(i)) return; const d = w ? Math.hypot(w.x - s.cx, w.z - s.cz) : i; if(d < bd){ bd = d; best = [s.cx, s.cz]; } }); return best; }
function remPulseEl(){ let el = $('remPulse'); if(!el){ el = document.createElement('div'); el.id = 'remPulse'; el.setAttribute('aria-hidden', 'true'); document.body.appendChild(el); } return el; }
function remPulse(k){ const el = remPulseEl(); el.style.setProperty('--k', k.toFixed(2)); if(k > 0.02) el.dataset.on = '1'; else delete el.dataset.on; }
function remHud(){ const left = 3 - (mini.got || []).length; miniHud(2, '숨겨진 잔재를 찾아라', `빨간 원 안에서 보이드의 신호 따라가기 · 남은 잔재 ${left}`); }
function huntStart(){ remBuild(); const got = mini.got = mini.got || [];
  REM.models.forEach((m, i)=>{ if(got.includes(i)) remCollapse(m, true); });
  REM.rings = remSpots().map((s, i)=>{ if(got.includes(i)) return null; const r = add(miniRoot, new THREE.RingGeometry(REM_R - 1.4, REM_R, 96).rotateX(-Math.PI/2), glowMat(0xff5a4e, 0.5), s.cx, groundY(s.cx, s.cz) + 0.7, s.cz, false); r.material.side = THREE.DoubleSide; r.material.depthWrite = false; return r; });
  mini.phase = 'hunt'; mini.dig = 0; mini.press = false; miniSave('hunt', {got}); remHud(); miniGo.textContent = '파내기'; miniGo.disabled = false; miniDots.innerHTML = ''; miniDoneBtn.hidden = true; miniBox.hidden = true; }
function huntTick(now){ const w = walk, got = mini.got; let best = -1, bd = 1e9;
  remSpots().forEach((s, i)=>{ if(got.includes(i)) return; const d = Math.hypot(w.x - s.x, w.z - s.z); if(d < bd){ bd = d; best = i; } });
  const s = REM.spots[best], inC = !!s && Math.hypot(w.x - s.cx, w.z - s.cz) < REM_R + 4, k = inC ? Math.max(0, 1 - bd/(REM_R + 20)) : 0;
  remPulse(vn ? 0 : k);
  if(inC && !vn){ const gap = Math.max(110, Math.min(1100, bd*26)); if(now - (mini.beepAt || 0) > gap){ mini.beepAt = now; sfx('tap'); } }
  const near = inC && bd < 4.2, dt = Math.min(0.1, (now - (mini.lastT || now))/1000); mini.lastT = now;
  miniBox.hidden = !near || !!vn; $('qhHint').textContent = near ? '여기야! 「파내기」를 꾹 눌러' : inC ? `신호가 ${k > 0.66 ? '아주 강해' : k > 0.33 ? '강해지고 있어' : '약하게 잡혀'} · 남은 잔재 ${3 - got.length}` : `빨간 원 안에서 보이드의 신호 따라가기 · 남은 잔재 ${3 - got.length}`;
  if(near && !vn){ const press = mini.press || WALK_KEYS.Space; mini.dig = press ? Math.min(1, mini.dig + dt/1.2) : Math.max(0, mini.dig - dt); miniGo.style.setProperty('--p', mini.dig.toFixed(2)); miniGo.classList.toggle('hot', true);
    if(mini.dig >= 1){ mini.dig = 0; mini.press = false; remReveal(best); } }
  else { mini.dig = 0; miniGo.classList.remove('hot'); } }
function remReveal(i){ const m = REM.models[i]; mini.phase = 'dig'; miniBox.hidden = true; remPulse(0); m.g.visible = true; m.state = 1; sfx('open'); flash();
  remTween(1300, k=>{ m.g.position.y = m.y0 - 7*(1 - k)*(1 - k); });
  const w = walk; if(w){ w.yaw = Math.atan2(m.s.x - w.x, m.s.z - w.z); }
  setTimeout(()=>{ if(!mini || mini.kind !== 'device') return; if(!(mini.got || []).length && !mini.firstSaid){ mini.firstSaid = true; say(STORY.remFirst, ()=> remGame(i)); } else remGame(i); }, reduce ? 200 : 1500); }
function remDlg(){ let d = $('remDlg'); if(d) return d; d = document.createElement('div'); d.id = 'remDlg'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-labelledby', 'rmT');
  d.innerHTML = '<div class="in"><small>ANCESTOR DEVICE</small><h1 id="rmT">잔재 해체</h1><p id="rmP"></p><svg id="rmSvg" viewBox="0 0 300 300" aria-hidden="true"></svg><button type="button" class="go" id="rmGo">지금!</button></div>';
  document.body.appendChild(d); $('rmGo').onclick = remTap; $('rmSvg').addEventListener('pointerdown', e=>{ e.preventDefault(); remTap(); }); return d; }
const REM_GAP = 0.98, REM_HIT = 0.3;   /* gap width and the hit window, radians */
function remArc(r, a, gap){ const a0 = a + gap/2, a1 = a + Math.PI*2 - gap/2, p = t=> `${(150 + Math.cos(t)*r).toFixed(1)} ${(150 + Math.sin(t)*r).toFixed(1)}`; return `M${p(a0)} A${r} ${r} 0 1 1 ${p(a1)}`; }
function remDraw(){ const G2 = REM.game; if(!G2) return; const R = [118, 88, 58];
  $('rmSvg').innerHTML = `<circle cx="150" cy="150" r="26" fill="#ff6a4e" opacity="${(0.55 + 0.4*Math.abs(Math.sin(performance.now()/160))).toFixed(2)}"/><circle cx="150" cy="150" r="36" fill="none" stroke="#ff6a4e" stroke-opacity=".35" stroke-width="2"/>`
    + R.map((r, k)=> k < G2.ring ? '' : `<path d="${remArc(r, G2.a[k], REM_GAP)}" fill="none" stroke="${k === G2.ring ? '#ffd84a' : '#5d6670'}" stroke-width="${k === G2.ring ? 14 : 10}" stroke-linecap="round"/>`).join('')
    + `<path d="M150 6 L140 -10 L160 -10 Z" transform="translate(0 16)" fill="#9ff6ff"/><line x1="150" y1="22" x2="150" y2="${150 - R[G2.ring < 3 ? G2.ring : 2] + 12}" stroke="#9ff6ff" stroke-opacity=".35" stroke-dasharray="4 5"/>`; }
function remGame(i){ const d = remDlg(); mini.phase = 'game';
  REM.game = {i, ring:0, a:[Math.random()*6.28, Math.random()*6.28, Math.random()*6.28], sp:reduce ? [0.9, -1.2, 1.5] : [1.4, -2.0, 2.6], boost:0, last:performance.now(), done:false};
  $('rmP').textContent = '노란 고리의 틈이 위쪽 표시에 닿을 때 「지금!」'; d.dataset.on = '1'; sfx('open');
  const loop = ()=>{ const G2 = REM.game; if(!G2 || G2.done) return; const now = performance.now(), dt = Math.min(0.05, (now - G2.last)/1000); G2.last = now;
    for(let k = G2.ring; k < 3; k++) G2.a[k] = (G2.a[k] + G2.sp[k]*dt*(G2.boost > now ? 1.8 : 1) + Math.PI*2) % (Math.PI*2); remDraw(); G2.raf = requestAnimationFrame(loop); };
  loop(); setTimeout(()=> $('rmGo').focus(), 50); }
function remTap(){ const G2 = REM.game; if(!G2 || G2.done || vn) return; const k = G2.ring, top = -Math.PI/2, diff = Math.atan2(Math.sin(G2.a[k] - top), Math.cos(G2.a[k] - top));
  if(Math.abs(diff) < REM_HIT){ G2.ring++; sfx('powerdown'); const m = REM.models[G2.i]; if(m.rings[k]) m.rings[k].visible = false;
    if(G2.ring >= 3){ G2.done = true; cancelAnimationFrame(G2.raf); remDraw(); $('rmP').textContent = '심장이 멈췄다.'; sfx('success'); setTimeout(()=> remFinish(G2.i), reduce ? 200 : 900); }
    else $('rmP').textContent = `고리 하나가 빠졌다. 남은 고리 ${3 - G2.ring}`; }
  else { G2.boost = performance.now() + 900; sfx('tap'); $('rmP').textContent = '빗나갔어. 틈이 표시에 닿을 때까지 기다려.'; const d = $('remDlg'); d.classList.remove('shake'); void d.offsetWidth; d.classList.add('shake'); } }
function remFinish(i){ delete $('remDlg').dataset.on; REM.game = null; const m = REM.models[i]; remCollapse(m, false); const got = mini.got = [...new Set([...(mini.got || []), i])]; miniSave('hunt', {got});
  if(REM.rings[i]){ miniRoot.remove(REM.rings[i]); REM.rings[i] = null; } const left = 3 - got.length;
  say([{who:'보이드', text: left ? `신호 하나가 꺼졌어. 남은 건 ${left}개야.` : '마지막 신호까지 꺼졌어. 연구실로 돌아가서 다시 돌려 보자.'}], ()=>{ if(!mini) return; if(left){ mini.phase = 'hunt'; remHud(); } else remBack(); }); }
function remBack(){ buildLabDoor(); remPulse(0); const got = mini.got || [0, 1, 2]; REM.models.forEach((m, i)=>{ if(got.includes(i) && m.state !== 2) remCollapse(m, true); }); miniSave('device-return', {got});
  miniWalkTo(3, '연구실로 돌아가기', '관람차 언덕 아래 연구실 문', LAB_DOOR, 8, remRerun); }
async function remRerun(){ const q = mini.q; actBusy = true; stopWalk(); await wait(300); setSim(true); await wait(reduce ? 400 : 3400);
  await new Promise(r=> say(STORY.remDone, r)); setSim(false); actBusy = false; questComplete(q); }
// the mid-check: the simulator over the island shows the records so far, then the stretches that bend off into red noise at the three remnant areas
let SIM_NOISE = null;
function simNoise(on){ if(SIM_NOISE){ simRoot.remove(SIM_NOISE.g); SIM_NOISE.g.traverse(o=>{ if(o.geometry) o.geometry.dispose(); if(o.material) o.material.dispose(); }); SIM_NOISE = null; } if(!on) return;
  const g = new THREE.Group(); simRoot.add(g); const Y = FLOW_Y, items = [];
  remSpots().forEach((s, i)=>{ const disk = add(g, new THREE.CircleGeometry(REM_R*0.6, 48).rotateX(-Math.PI/2), glowMat(0xff4a3a, 0.35, true), s.cx, Y + 0.5, s.cz, false); disk.material.depthTest = false; disk.renderOrder = 9; items.push({m:disk, ph:i, jit:false});
    for(let k = 0; k < 5; k++){ const a0 = k*1.26 + i, pts = []; for(let j = 0; j <= 9; j++){ const r = j*7, a = a0 + Math.sin(j*1.7 + k)*0.7; pts.push(new THREE.Vector3(s.cx + Math.cos(a)*r, Y + 1 + Math.sin(j + k)*2, s.cz + Math.sin(a)*r)); }
      const m = add(g, new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 30, 1.3, 5), glowMat(0xff5a4e, 0.8, true), 0, 0, 0, false); m.material.depthTest = false; m.renderOrder = 10; items.push({m, ph:i*3 + k, jit:true}); } });
  SIM_NOISE = {g, items}; simAnim.push(t=>{ if(!SIM_NOISE) return; SIM_NOISE.items.forEach(it=>{ const f = Math.sin(t*23 + it.ph*7) > 0.15 ? 1 : 0.12; it.m.material.opacity = (0.25 + 0.6*Math.abs(Math.sin(t*5 + it.ph)))*f; if(it.jit){ it.m.position.x = (Math.random() - 0.5)*2; it.m.position.z = (Math.random() - 0.5)*2; } }); }); }
async function midCheck(q){ miniSave('mid'); actBusy = true; stopWalk(); await wait(300); setSim(true); await wait(reduce ? 400 : 3000);
  await new Promise(r=> say(STORY.midA, r)); await new Promise(r=> say(STORY.midA2, r)); simNoise(true); sfx('powerdown'); await wait(reduce ? 400 : 3200);
  await new Promise(r=> say(STORY.midB, r)); simNoise(false); setSim(false); await wait(500);
  const cp = miniLoad() || {q:q.id}; cp.q = q.id; cp.step = 'hunt'; cp.got = cp.got || []; try{ localStorage.setItem(MINI_KEY(), JSON.stringify(cp)); }catch(e){}
  actBusy = false; startWalk(PAIR); }
window.__rem = ()=> ({spots:REM.spots, models:REM.models.map(m=> m.state), mini:mini && mini.kind === 'device' ? {phase:mini.phase, got:mini.got, dig:mini.dig} : null, game:REM.game ? {ring:REM.game.ring, a:REM.game.a, done:REM.game.done} : null, noise:!!SIM_NOISE});
window.__remAim = ()=>{ const G2 = REM.game; if(G2) G2.a[G2.ring] = -Math.PI/2; };
'''
rep(anchor, REMCODE + anchor)

# ---- reward card, routing, campus prompts ----
rep("$('qrT').textContent = q.id==='q2'?'네이티 발견 · 누락 기록 수집 완료':q.id==='q4'?'선대의 잔재 파괴':q.id==='q1'?'서쪽 숲 기록 수집 완료':isl?'누락 기록 수집 완료':'미션 완료';",
    "$('qrT').textContent = q.id==='q2'?'네이티 발견 · 두 번째 좌표 확보':q.id==='q4'?'선대의 잔재 해체':q.id==='q1'?'섬 전체 전원 복구':isl?'누락 기록 수집 완료':'미션 완료';")
rep("$('qrMap').textContent=ready?(q.id==='q2'?'미션 3 · 이상 지점 조사':'다음 캠퍼스 기록 보기'):",
    "$('qrMap').textContent=ready?(q.id==='q1'?'미션 2 · 네이티를 찾아라':'다음 캠퍼스 기록 보기'):")
rep("if(id==='q2'){if(simOn)setSim(false);buildLabDoor();STAGED=false;startWalk(PAIR);if(walk){walk.x=LAB_DOOR[0];walk.z=LAB_DOOR[1];walk.snap=true;}}else goBack();};",
    "if(id==='q1'){if(simOn)setSim(false);STAGED=false;startWalk(PAIR);}else goBack();};")
rep("await voidAsk(seen === 2 ? '방해는 없어졌어. 마지막 좌표에서 남은 기록 하나를 채우자.' : '스카이루프에서 확보한 다음 좌표야. 캠퍼스에서 그 자리의 내용을 기록해 줘.');",
    "await voidAsk(seen === 2 ? '시뮬레이션이 다시 맞기 시작했어. 마지막 좌표에서 남은 기록 하나를 채우자.' : '네이티의 빛이 가리킨 좌표야. 캠퍼스에서 그 자리의 내용을 기록해 줘.');")
rep("else voidSay('기록은 모두 채웠어. 이제 섬으로 돌아가 환원 순서와 양을 확인하자.', 8000, 'idle'); }, 1200); }",
    "else voidSay('기록은 모두 채웠어. 이제 섬으로 돌아가 코덱스를 만나자.', 8000, 'idle'); }, 1200); }")
rep("  2:[{who:'자일로',text:'제로, 리코! 관람차 앞입니다. 두 분에게 부탁할 일이 있어요.'},{who:'제로',text:'무슨 일이지?'},{who:'리코',text:'가서 들어 보자.'}],",
    "  2:[{who:'자일로',text:'제로, 리코! 관람차 앞입니다. 연구실에서 시뮬레이션을 돌려 봅시다.'},{who:'제로',text:'지금까지 모은 걸 확인하러 가자!'}],")
i = h.index('const ACT_EXIT={'); j = h.index('};', i) + 2
h = h[:i] + "const ACT_EXIT={\n q1:{card:{who:'자일로',img:'xylo_talk',text:'네이티부터 찾아 주세요. 관람차 뒤쪽 길입니다.'}},\n q2:{card:{who:'보이드',img:'void',text:'네이티의 빛이 가리킨 캠퍼스 좌표야. 그 자리의 기록을 찍어 줘.'}},\n q4:{card:{who:'자일로',img:'xylo_talk',text:'마지막 캠퍼스 좌표입니다. 서둘러 주세요.'}}};" + h[j:]
rep("function recDone(n){ const z = campusZone(n), k = 2*n - 1;", "function recDone(n){ const z = campusZone(n), k = Math.max(1, recordCount());")

# ---- void help lines ----
i = h.index(" if(q.id==='q1'){\n  if(islandRecord('q1'))"); j = h.index(" return m?.decoded||cp?.decoded", i)
h = h[:i] + """ if(q.id==='q1'){
  if(step==='station')return '섬의 전원이 돌아왔어. 그런데 네이티가 사라졌대. 자일로의 이야기를 들어 보자.';
  if(step==='yard')return '예비 배전선의 칸을 돌려 발전기에서 모든 칸까지 선을 이어 줘.';
  return '자일로가 롤러코스터 근처에서 기다리고 있어. 만나서 섬의 전원이 끊긴 이유를 들어 보자.';
 }
 if(q.id==='q2'){
  if(step==='maze')return '미로 한가운데까지 가 보자. 네이티는 미로 안으로 끌려 들어갔어.';
  return '네이티가 사라졌어. 네이티가 흩어지는 건 일루아가 흔들린다는 뜻이야. 관람차 뒤쪽 길부터 찾아보자.';
 }
 if(q.id==='q4')return step==='device-return'?'잔재 세 개를 모두 없앴어. 연구실로 돌아가서 시뮬레이션을 다시 돌려 보자.':step==='hunt'?`빨간 원 안으로 가면 내 신호 소리가 들려. 빨라지는 쪽으로 가서 「파내기」를 꾹 눌러. 남은 잔재 ${3-((m?.got||cp?.got||[]).length)}개.`:'관람차 아래 연구실로 가자. 지금까지 모은 기록으로 시뮬레이션을 돌려 볼 거야.';
""" + h[j:]

# ---- Naty: red and unsteady until the restoration ----
rep("  if(TEAM&&!flowFree()){_c2.set(QDONE.has('q4')||(mini?.kind==='device'&&mini.hits>=3)?0x7cc8f0:0xe05a4e);}", "  if(TEAM&&!flowFree()){_c2.set(0xe05a4e);}")
rep("  NATY.userData.bits.forEach((b,i)=>{ const q = t*2 + i*2.1; b.position.set(Math.cos(q)*4.5, 4 + Math.sin(q*1.3)*2, Math.sin(q)*4.5); });",
    "  NATY.userData.bits.forEach((b,i)=>{ const q = t*2 + i*2.1; b.position.set(Math.cos(q)*4.5, 4 + Math.sin(q*1.3)*2, Math.sin(q)*4.5); });\n"
    "  { const s0 = NATY.userData.s0 ??= NATY.scale.x; if(TEAM && !flowFree()){ const sp = Math.sin(t*1.9)*Math.sin(t*0.71), k = sp > 0.45 ? (sp - 0.45)/0.55 : 0;   /* 2026-11-04: the Illua is unsteady, so its spirit keeps splitting and pulling back together */\n"
    "      NATY.scale.set(s0*(1 + k*0.35*Math.sin(t*31)), s0*(1 - k*0.25), s0*(1 + k*0.3*Math.cos(t*27))); if(k > 0) NATY.userData.bits.forEach(b=> b.position.multiplyScalar(1 + k*1.6)); } else if(NATY.scale.x !== s0) NATY.scale.setScalar(s0); }")

# ---- CSS ----
lines = h.split('\n'); k = lines.index('</style></head><body>')
lines[k-1] += ('#remDlg{position:fixed;inset:0;z-index:35;display:none;place-items:center;background:radial-gradient(ellipse at 50% 0%,rgba(255,80,60,.18),transparent 55%),rgba(5,7,12,.9);color:var(--void-fg);text-align:center;-webkit-user-select:none;user-select:none}'
               '#remDlg[data-on]{display:grid}#remDlg .in{display:grid;gap:12px;justify-items:center;width:min(560px,94vw)}'
               '#remDlg small{font-family:var(--mono);letter-spacing:.3em;font-size:12px;color:#9ff6ff}#remDlg h1{margin:0;font-size:clamp(22px,4vw,32px)}'
               '#remDlg p{margin:0;font-size:15px;line-height:1.6;min-height:1.6em;max-width:40ch;word-break:keep-all}#remDlg svg{width:min(300px,64vw,52vh);height:auto;touch-action:manipulation}'
               '#remDlg .go{border:0;border-radius:999px;padding:14px 40px;min-height:48px;background:#9ff6ff;color:#06111a;font:700 17px var(--sans)}#remDlg .go:active{transform:scale(.97)}'
               '#remDlg.shake svg{animation:remShake .3s}@keyframes remShake{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}'
               '#remPulse{position:fixed;inset:0;pointer-events:none;z-index:20;opacity:0;transition:opacity .3s;box-shadow:inset 0 0 calc(30px + 140px*var(--k,0)) rgba(255,90,78,calc(.8*var(--k,0)))}'
               '#remPulse[data-on]{opacity:1;animation:remBeat 1.1s ease-in-out infinite}@keyframes remBeat{50%{opacity:.6}}'
               '@media (prefers-reduced-motion:reduce){#remPulse[data-on]{animation:none}#remDlg.shake svg{animation:none}}')
h = '\n'.join(lines)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('patched')
