# 2026-11-13 오후 사용자 지시 묶음
#  ① 미로: 크기는 그대로(75), 난이도 낮춤 → 15×15칸 → 11×11칸(통로 넓어짐) + 막다른 길의 3/4을 뚫어 돌아가는 길을 만듦
#  ② 네이티 위치에 맞게 대사: 「관람차 뒤쪽 길」 → 「정문 동쪽 길」
#  ③ 태블릿 달리기 버튼(#walkRun, 누르면 켜짐·다시 누르면 꺼짐)
#  ④ 정전: 탑승객을 숨기고(전기가 끊겼는데 기구에 타고 있으면 안 됨), 캐노피 어드벤처도 멈추고, 전광판·무대 조명·전구처럼 전원과 무관하게 켜져 있던 빛을 어둡게
#  ⑤ 현황판(조 화면): 구역 목록 대신 복구율을 크게 + 다섯 칸
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
# ---- ① maze ----
rep("const S = 75, n = 15, mid = (n - 1)/2,", "const S = 75, n = 11, mid = (n - 1)/2,")
rep("  // the entrance faces the park path that ends at the maze\n",
    "  /* easier (user, 2026-11-13: same size, lower difficulty): three dead ends in four are opened into a loop, so a wrong turn usually leads on instead of back */\n"
    "  for(let i=0;i<n;i++) for(let j=0;j<n;j++){ if(i === mid && j === mid) continue; const w = [[i > 0, ()=> H[i][j], ()=>{ H[i][j] = 0; }], [i < n - 1, ()=> H[i+1][j], ()=>{ H[i+1][j] = 0; }], [j > 0, ()=> V[i][j], ()=>{ V[i][j] = 0; }], [j < n - 1, ()=> V[i][j+1], ()=>{ V[i][j+1] = 0; }]];\n"
    "    const open = (H[i][j] ? 0 : 1) + (H[i+1][j] ? 0 : 1) + (V[i][j] ? 0 : 1) + (V[i][j+1] ? 0 : 1); if(open !== 1 || r2() > 0.5) continue; const shut = w.filter(x=> x[0] && x[1]()); if(shut.length) shut[Math.floor(r2()*shut.length)][2](); }\n"
    "  // the entrance faces the park path that ends at the maze\n")
# ---- ② dialogue ----
n2 = s.count('관람차 뒤쪽 길'); assert n2 >= 4, n2; s = s.replace('관람차 뒤쪽 길', '정문 동쪽 길')
# ---- ③ run button ----
rep('<div id="walkPad" hidden aria-hidden="true"><i></i></div>', '<div id="walkPad" hidden aria-hidden="true"><i></i></div><button type="button" id="walkRun" hidden aria-pressed="false">달리기</button>')
rep("(k.ShiftLeft || k.ShiftRight || walkPad.run ? 11 : 5.5)", "(k.ShiftLeft || k.ShiftRight || walkPad.run || walkPad.lock ? 11 : 5.5)")
rep("{ const pad = $('walkPad'), nub = pad.querySelector('i'), R = 44;",
    "{ const rb = $('walkRun'), wp = $('walkPad'); rb.onclick = e=>{ e.stopPropagation(); walkPad.lock = !walkPad.lock; rb.setAttribute('aria-pressed', walkPad.lock ? 'true' : 'false'); sfx('tap'); };\n"
    "  new MutationObserver(()=>{ rb.hidden = wp.hidden; if(wp.hidden){ walkPad.lock = false; rb.setAttribute('aria-pressed', 'false'); } }).observe(wp, {attributes:true, attributeFilter:['hidden']}); }   /* a run button for the tablets (user, 2026-11-13) */\n"
    "{ const pad = $('walkPad'), nub = pad.querySelector('i'), R = 44;")
n3 = s.count('멀어지면 놓쳐요 · 조이스틱을 끝까지 밀면 달려요'); assert n3 >= 1; s = s.replace('멀어지면 놓쳐요 · 조이스틱을 끝까지 밀면 달려요', '멀어지면 놓쳐요 · 「달리기」를 누르면 달려요')
# ---- ④ blackout ----
rep("function rider(parent,x,y,z,i,s=1,rot=0){const g=new THREE.Group();g.position.set(x,y,z);g.rotation.y=rot;g.scale.setScalar(s);parent.add(g);",
    "function rider(parent,x,y,z,i,s=1,rot=0){const g=new THREE.Group();g.position.set(x,y,z);g.rotation.y=rot;g.scale.setScalar(s);parent.add(g);g.userData.dynamic=true;(window.__RIDERS||(window.__RIDERS=[])).push(g);   /* kept apart from the merged scenery: nobody sits on a ride during the blackout (user, 2026-11-13) */")
rep("function poweredAnim(f){",
    "var PARK_SHOWN=null;\n"
    "/* blackout (user, 2026-11-13): the riders are gone and whatever shone on its own (stage screen and lights, string bulbs, ride lamps) goes dark. Fire, the characters and painted signs stay. */\n"
    "function parkDark(off){ (window.__RIDERS||[]).forEach(g=>{ if(off){ if(g.visible){ g.visible=false; g.userData.po=1; } } else if(g.userData.po){ g.visible=true; g.userData.po=0; } });\n"
    "  if(!parkDark.g){ parkDark.g=[]; const seen=new Set(), KEEP=new Set(['코덱스의 동굴','포레스트 캠프','팬텀 하우스','미러 레이크','항구']);\n"
    "    islRoot.traverse(o=>{ if(!(o.isMesh||o.isInstancedMesh)) return; const m=o.material; if(!m||Array.isArray(m)||!m.isMeshBasicMaterial||m.userData.bulb||seen.has(m)) return; let b=null; for(let p=o;p;p=p.parent){ if(p.userData&&p.userData.i!=null&&IB[p.userData.i]){ b=IB[p.userData.i]; break; } }\n"
    "      if(b&&(b.c==='char'||KEEP.has(b.label))) return; if(m.map ? !(b&&b.label==='그랜드 스테이지') : (!b&&m.transparent)) return; seen.add(m); parkDark.g.push([m,m.color.clone()]); }); }\n"
    "  parkDark.g.forEach(([m,c])=>{ m.color.copy(c); if(off) m.color.multiplyScalar(0.2); }); }\n"
    "function poweredAnim(f){")
rep("PARK_ON=parkPowerOn();if(PARK_ON)", "PARK_ON=parkPowerOn();if(PARK_ON!==PARK_SHOWN&&typeof RIDE_READY!=='undefined'&&RIDE_READY){PARK_SHOWN=PARK_ON;try{parkDark(!PARK_ON);}catch(e){}}if(PARK_ON)")
m = re.search(r"pickable\((\w+), \{[^{}]{0,80}n:'캐노피 어드벤처'", s); assert m, 'canopy'
var = m.group(1); a = s.rfind(f"const {var} = new THREE.Group()", 0, m.start()); assert a > 0, var
blk = s[a:m.start()]; k4 = blk.count('islAnim.push('); assert 1 <= k4 <= 8, k4
s = s[:a] + blk.replace('islAnim.push(', 'poweredAnim(') + s[m.start():]
# ---- ⑤ board ----
rep("  $('bN').textContent = `${ok} / ${rows.length}`; $('bFill').style.width = rows.length ? `${ok/rows.length*100}%` : '0';\n  const cut = rows.findIndex(",
    "  /* a team's board (user, 2026-11-13): how much is back, not which places */\n"
    "  $('board').classList.add('solo'); $('bN').textContent = `${rows.length ? Math.round(ok/rows.length*100) : 0}%`; $('bFill').style.width = rows.length ? `${ok/rows.length*100}%` : '0';\n"
    "  $('bRows').innerHTML = `<div class=\"bseg\" role=\"img\" aria-label=\"채운 기록 ${ok} / ${rows.length}\">${rows.map((_, i)=> `<i class=\"${i < ok ? 'ok' : ''}\"></i>`).join('')}</div><p class=\"bcount\">채운 기록 <b>${ok}</b> / ${rows.length}</p>`; return;\n"
    "  const cut = rows.findIndex(")
rep("    $('bN').textContent = `${okAny} / ${rows.length}`;", "    $('board').classList.remove('solo'); $('bN').textContent = `${okAny} / ${rows.length}`;")
CSS = ("#board.solo .bbar{display:none}#board.solo #bN{font-size:34px;line-height:1;font-variant-numeric:tabular-nums}"
       "#board.solo .bseg{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:6px;margin-top:12px}#board.solo .bseg i{height:12px;border-radius:6px;background:color-mix(in srgb,currentColor 14%,transparent)}#board.solo .bseg i.ok{background:var(--restored,#1a9a5a)}"
       "#board.solo .bcount{margin:10px 0 0;font-size:13px;opacity:.75}#board.solo .bcount b{font-size:15px;opacity:1}"
       "#walkRun{position:fixed;left:166px;bottom:calc(34px + env(safe-area-inset-bottom,0px));z-index:21;min-width:76px;height:52px;padding:0 16px;border-radius:26px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);background:var(--panel-solid);color:inherit;font:inherit;font-weight:700;font-size:15px;touch-action:manipulation;display:none}"
       "#walkRun:not([hidden]){display:block}#walkRun[aria-pressed=true]{background:var(--restored,#1a9a5a);color:#fff;border-color:transparent}#walkRun:active{transform:scale(.97)}body.cavestory #walkRun{display:none!important}@media (pointer:fine){#walkRun{display:none!important}}\n")
assert s.count('#walkRun{') == 0 and s.count('.bseg{') == 0
mk = '</style></head><body>'; assert s.count(mk) == 1; i = s.index(mk); print('before marker:', repr(s[i-160:i]))
s = s[:i] + CSS + s[i:]
P.write_bytes(s.encode('utf-8')); print('ok crlf', s.count('\r\n'), 'dialogue', n2, 'canopy anims', k4)
sc = P.parents[1] / 'docs/chapter05_script.md'; t = sc.read_bytes().decode('utf-8'); c = t.count('관람차 뒤쪽 길'); sc.write_bytes(t.replace('관람차 뒤쪽 길', '정문 동쪽 길').encode('utf-8')); print('script lines changed', c)

# 그 뒤 씨앗 7 → 18(정답 45칸, 막다른 길 10개)로 맞춤: index.html의 미로 블록 `let s2 = 18`
