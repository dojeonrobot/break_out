# 2026-11-18 묶음 3-1: 걷는 중에도 관리자 버튼, 관람차 언덕 통과 막기, 복구 현황은 기록 3곳·미션 클리어는 따로, 3막 시점은 인물·대사는 코덱스 설득.
import io
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
MARK = "</style></head><body>"

# 1. admin button stays reachable while a mission is walked (a login that timed out mid-mission could not be renewed)
CSS = ("body.walk #adminBtn{display:flex!important;top:calc(64px + env(safe-area-inset-top,0px))!important;bottom:auto!important;right:12px;opacity:.55}body.walk #adminBtn:hover,body.walk.admkey #adminBtn{opacity:1}"
       "#board.solo .bmis{display:flex;align-items:center;gap:8px;margin:12px 0 0;padding-top:10px;border-top:1px solid color-mix(in srgb,currentColor 14%,transparent);font-size:13px}#board.solo .bmis span{opacity:.75}#board.solo .bmis b{font-size:15px}"
       "#board.solo .bmis .pips{display:flex;gap:5px;margin-left:auto}#board.solo .bmis .pips i{width:12px;height:12px;border-radius:50%;box-sizing:border-box;border:2px solid color-mix(in srgb,currentColor 30%,transparent)}#board.solo .bmis .pips i.ok{background:#6c3df0;border-color:#6c3df0}\n")
rep(MARK, CSS + MARK)

# 2. the wheel's hill is solid: its 45-degree sides were no wall for the grid and groundY does not know it, so the walker went through the hill
rep("const HILL_BLOCKS = [[40*K, -295*K, 95*0.95, 82*0.95], [-120*K, -315*K, 60*0.95, 52*0.95]];",
    "const HILL_BLOCKS = [[40*K, -295*K, 95*0.95, 82*0.95], [-120*K, -315*K, 60*0.95, 52*0.95], [FERRIS_X*K, FERRIS_Z*K, 79, 79]];   /* + the wheel's terraced hill (user, 2026-11-18) */")

# 3. records = the three campus scans; island missions are counted apart (user, 2026-11-18)
rep("const recordCount=()=>GLYPH_ZONES.filter(z=>zoneMine(MI.find(m=>m.id===z.id))).length;",
    "const recordCount=()=>{ try{ return ['z1','z2','z3'].filter(id=>{ const z = MISSION_E.find(m=> m.id === id); return z && zoneMine(z); }).length; }catch(e){ return 0; } };   /* the three campus scans (user, 2026-11-18); island missions are counted apart */\nconst missionCount=()=>{ try{ return QUESTS.filter(q=> QDONE.has(q.id)).length; }catch(e){ return 0; } };")
rep("const RATE = ()=> (typeof MI !== 'undefined' ? MI.filter(m=> m.b && zoneDone(m)).length : M.filter(zoneDone).length)*20;", "const RATE = ()=> Math.round(recordCount()/3*100);")
rep("const bk = recordCount(), bT = GLYPH_ZONES.length;", "const bk = recordCount(), bT = 3, mk = missionCount();")
rep("""<p class="bcount">확보한 기록 <b>${bk}</b> / ${bT}</p>`; return;""", """<p class="bcount">확보한 기록 <b>${bk}</b> / ${bT}</p><p class="bmis"><span>미션 클리어</span><b>${mk}</b> / 5<span class="pips" aria-hidden="true">${Array.from({length:5}, (_, k)=> `<i class="${k < mk ? 'ok' : ''}"></i>`).join('')}</span></p>`; return;""")
rep("$('simN').textContent = `${SIM_LIT} / 5`; $('simCells').innerHTML = Array.from({length:5}, (_,i)=> `<i class=\"${i < SIM_LIT ? 'ok' : ''}\"></i>`).join('');",
    "{ const rk = SIM_LIT >= 5 ? 3 : SIM_LIT >= 3 ? 2 : SIM_LIT >= 1 ? 1 : 0; $('simN').textContent = `${rk} / 3`; $('simCells').innerHTML = Array.from({length:3}, (_,i)=> `<i class=\"${i < rk ? 'ok' : ''}\"></i>`).join(''); }")
rep('<b id="simN">0 / 5</b>', '<b id="simN">0 / 3</b>')
rep("$('rdCells').innerHTML = Array.from({length:5}, (_, i)=>", "$('rdCells').innerHTML = Array.from({length:3}, (_, i)=>")
rep("`<b>확보한 기록 ${k} / 5</b>`;", "`<b>확보한 기록 ${k} / 3</b>`;")
rep("$('qrCount').textContent=`확보한 기록 ${recordCount()} / 5`;", "$('qrCount').textContent=`미션 클리어 ${missionCount()} / 5`;")
rep("$('qrCount').textContent='확보한 기록 1 / 5';", "$('qrCount').textContent='미션 클리어 1 / 5';")
rep("qPop(`기록 수집 완료 · ${recordCount()} / 5`);", "qPop('이 자리의 상태를 확인했어요');")
rep("누락된 다섯 기록 중 세 개는 캠퍼스에서, 두 개는 섬 안에서 채울 거야. 먼저 첫 번째 좌표부터 알려 줄게.", "누락된 기록 세 개를 캠퍼스에서 스캔해서 채울 거야. 먼저 첫 번째 좌표부터 알려 줄게.")
rep("<h1>다섯 기록이 모두 돌아왔습니다</h1>", "<h1>기록이 모두 돌아왔습니다</h1>")
rep("'다섯 기록을 찾은 뒤'", "'기록을 모두 찾은 뒤'")
# story lines that counted five records or said an island mission filled a record
for a, b in (
 ("서쪽 숲 가장자리의 기록을 채웠어. 일루아가 숲의 바깥 둘레를 따라 흐르고 있었구나.", "서쪽 숲 가장자리의 상태를 확인했어."),
 ("미로 정원 아래의 흐름을 확인했어. 이 자리 아래로도 일루아가 이어져 있었구나. 이걸로 네 번째 기록을 채웠어.", "미로 정원 자리의 상태를 확인했어."),
 ("이걸로 누락됐던 다섯 기록을 모두 채웠어. 원천에서 다섯 기록의 자리까지 전부 이어졌어.", "이걸로 누락됐던 기록을 모두 채웠어. 원천에서 섬 끝까지 흐름이 전부 이어졌어."),
 ("봐. 원천에서 다섯 기록의 자리까지 전부 이어졌어. 경고도 뜨지 않아.", "봐. 원천에서 섬 끝까지 전부 이어졌어. 경고도 뜨지 않아."),
 ("이대로면 다섯 기록을 다 모아도 시뮬레이션을 믿을 수 없어요.", "이대로면 기록을 다 모아도 시뮬레이션을 믿을 수 없어요."),
 ("이번에는 관람차 언덕 주변의 흐름을 확인했어. 언덕 아래를 지나 해안 쪽으로 이어지고 있었어.", "이번에는 회전목마에서 롤러코스터까지 이어지는 흐름을 확인했어."),
 ("사파리 아래의 흐름도 확인했어. 원천에서 나온 일루아가 사파리 아래로 이어지고 있었어.", "관람차에서 사파리까지 이어지는 흐름도 확인했어."),
):
    assert s.count(a) >= 1, a; s = s.replace(a, b)
rep("다섯 개를 전부 채웠어요!", "기록을 전부 채웠어요!", 2)

# 4. act 3: the people at the lab door, not a far view of the wheel; the talk leads to persuading Codex
rep("  const dx = fx - b.cx, dz = fz - b.cz, L = Math.hypot(dx, dz) || 1, ux = dx/L, uz = dz/L;   // facing away from the zone, towards the camera\n  STAGED = true;",
    "  if(zoneId === 'dl-ferris'){ try{ buildLabDoor(); if(LAB_DOOR){ fx = LAB_DOOR[0]; fz = LAB_DOOR[1]; } }catch(e){} }   /* act 3 is played at the lab door, on the people (user, 2026-11-18: the far view of the wheel said nothing) */\n  const dx = fx - b.cx, dz = fz - b.cz, L = Math.hypot(dx, dz) || 1, ux = dx/L, uz = dz/L;   // facing away from the zone, towards the camera\n  STAGED = true;")
a = s.index("  if(zoneId === 'dl-ferris'){ let bx = fx + ux*85, bz = fz + uz*85; flyTo(")
b = s.index("\n", a)
s = s[:a] + s[b + 1:]
import json
def story_set(key, lines):
    global s
    tag = '"%s":' % key
    i = s.index(tag); assert s.count(tag) == 1, (key, s.count(tag))
    j = s.index("[", i); arr, end = json.JSONDecoder().raw_decode(s[j:])
    s = s[:j] + json.dumps(lines, ensure_ascii=False) + s[j + end:]
    return arr
old = story_set("act3", [
 {"who": "자일로", "text": "환원 시뮬레이션이 성공했어요. 이 방법이라면 일루아를 제자리로 환원할 수 있습니다."},
 {"who": "제로", "text": "그럼 바로 환원하면 되겠네요!"},
 {"who": "자일로", "text": "환원은 우리끼리 정할 일이 아니에요. 이 섬의 수호자인 코덱스가 허락해야 합니다."},
 {"who": "리코", "text": "코덱스는 환원이 잘못될까 봐 불안해하고 있어요."},
 {"who": "자일로", "text": "그래서 설득해야 해요. 코덱스는 북쪽 해안 동굴에 있어요. 선대가 남긴 벽화 앞에 자주 혼자 있습니다."},
 {"who": "네이티", "text": "자일로 옆의 네이티가 잠깐 흩어졌다가 겨우 다시 모인다.", "nar": True},
 {"who": "제로", "text": "네이티가 점점 더 흐려져……. 서두르자. 코덱스를 설득하러 가자!"}])
print("old act3", len(old))
story_set("q3intro", [{"who": "리코", "text": "환원 시뮬레이션은 성공했어. 이제 코덱스를 설득해야 해."}, {"who": "제로", "text": "북쪽 해안 동굴에 있다고 했지? 가 보자!"}])
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok")
