# 2026-11-17 사용자 요청 묶음 2. 한 번만 적용.
#  ① 미로 한가운데 버튼 「말 걸기」 → 「네이티를 찾았다!」
#  ② 전원 연출 뒤 네이티가 사라진 장면을 급박하게: 경보음·붉은 화면 테두리·「네이티가 사라졌다!」, 자일로 첫 마디
#  ③ 미션 시작 카드(큰 제목 + 「미션 시작」 버튼), 걷는 중 미션 안내 상자 글씨 키움
#  ④ 좌표 확보(미션 완료) 카드 다듬기
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)

# ① 네이티를 찾았다!
rep("miniGo.textContent = '말 걸기';", "miniGo.textContent = '네이티를 찾았다!';")
rep("'「말 걸기」를 눌러요' : 'Space를 눌러 말을 걸어요'", "'「네이티를 찾았다!」를 눌러요' : 'Space를 눌러요'")
rep("return {t:'말 걸기', run:()=> natyTalk()};", "return {t:'네이티를 찾았다!', run:()=> natyTalk()};")

# ② 급박한 장면
rep('"text": "……네이티가 없어요."', '"text": "……잠깐만요. 네이티가 없어요!"')
rep("setTimeout(()=> parkWake(()=> say([...STORY.yardDone, ...STORY.natyGone], ()=> questComplete(mini ? mini.q : QUESTS[0]))), 700); }",
    "setTimeout(()=> parkWake(()=> say(STORY.yardDone, ()=> natyGoneSay(()=> questComplete(mini ? mini.q : QUESTS[0])))), 700); }\n"
    "/* 네이티 is gone: an alarm, a red edge on the screen for as long as the lines run (user, 2026-11-17: it has to feel urgent) */\n"
    "function natyGoneSay(done){ let el = $('alarmEdge'); if(!el){ el = document.createElement('div'); el.id = 'alarmEdge'; el.setAttribute('aria-hidden', 'true'); document.body.appendChild(el); void el.offsetWidth; }\n"
    "  el.dataset.on = '1'; sfx('error'); setTimeout(()=> sfx('error'), 260); qPop('네이티가 사라졌다!'); setTimeout(()=> say(STORY.natyGone, ()=>{ delete el.dataset.on; done(); }), ffOn() ? 0 : 1500); }")
rep("TRAIN.lit = true; say(STORY.natyGone, ()=> questComplete(q)); return true; }", "TRAIN.lit = true; natyGoneSay(()=> questComplete(q)); return true; }")

# ③ 미션 시작 카드
rep("  if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name)); }, 700); }\n}",
    "  missionCard(q).then(()=>{ if(!seen){ try{ sessionStorage.setItem(key, '1'); }catch(e){} setTimeout(()=>{ if(walk && questLive === q && !vn) say(QUEST_INTRO[q.id](name)); }, 500); } });\n}\n"
    "/* the mission start card (user, 2026-11-17: the small box did not feel like a mission starting): big title, one button; nothing moves until it is pressed */\n"
    "let MCARD = null;\n"
    "function missionCard(q){ let auto = false; try{ auto = !!navigator.webdriver && !localStorage.getItem('void-card-test'); }catch(e){} if(ffOn() || auto) return Promise.resolve();\n"
    "  let el = $('missionCard'); if(!el){ el = document.createElement('div'); el.id = 'missionCard'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'mcT');\n"
    "    el.innerHTML = '<div class=\"in\"><small id=\"mcN\"></small><h1 id=\"mcT\"></h1><p id=\"mcH\"></p><button type=\"button\" id=\"mcGo\"></button></div>'; document.body.appendChild(el); el.addEventListener('click', e=>{ e.stopPropagation(); if(e.target.closest('#mcGo') && MCARD) MCARD(); }); }\n"
    "  $('mcN').textContent = `MISSION ${QUESTS.indexOf(q) + 1}`; $('mcT').textContent = q.title0 || q.title; $('mcH').textContent = q.hint || ''; $('mcGo').textContent = matchMedia('(pointer:coarse)').matches ? '미션 시작' : '미션 시작 · Space';\n"
    "  for(const k in WALK_KEYS) delete WALK_KEYS[k]; delete el.dataset.on; void el.offsetWidth; el.dataset.on = '1'; sfx('open'); const at = performance.now();\n"
    "  return new Promise(r=>{ MCARD = ()=>{ if(performance.now() - at < 700) return; MCARD = null; delete el.dataset.on; sfx('tap'); r(); }; setTimeout(()=>{ try{ $('mcGo').focus(); }catch(e){} }, 60); }); }\n"
    "addEventListener('keydown', e=>{ if(!MCARD) return; e.preventDefault(); e.stopImmediatePropagation(); if((e.code === 'Space' || e.code === 'Enter') && !e.repeat) MCARD(); }, true);")
rep("function questTick(){\n  const q = questLive; if(!q || !walk || vn || q.found || mini) return;", "function questTick(){\n  const q = questLive; if(!q || !walk || vn || q.found || mini || MCARD) return;")
rep("function admSkipWhat(){\n  if(!ADMIN_KEY || SCREEN || LOCAL) return null;", "function admSkipWhat(){\n  if(!ADMIN_KEY || SCREEN || LOCAL) return null;\n  if(MCARD) return {t:'미션 시작', run:()=>{ const f = MCARD; MCARD = null; delete $('missionCard').dataset.on; f && setTimeout(()=>{}, 0); MCARD_R && MCARD_R(); }};")
# the admin skip closes the card without the 0.7 s guard: keep the resolver reachable
rep("  return new Promise(r=>{ MCARD = ()=>{ if(performance.now() - at < 700) return; MCARD = null; delete el.dataset.on; sfx('tap'); r(); };", "  return new Promise(r=>{ MCARD_R = ()=>{ MCARD_R = null; r(); }; MCARD = ()=>{ if(performance.now() - at < 700) return; MCARD = null; delete el.dataset.on; sfx('tap'); MCARD_R && MCARD_R(); };")
rep("let MCARD = null;\n", "let MCARD = null, MCARD_R = null;\n")
rep("run:()=>{ const f = MCARD; MCARD = null; delete $('missionCard').dataset.on; f && setTimeout(()=>{}, 0); MCARD_R && MCARD_R(); }};", "run:()=>{ MCARD = null; delete $('missionCard').dataset.on; MCARD_R && MCARD_R(); }};")

CSS = (
"#missionCard{position:fixed;inset:0;z-index:38;display:none;place-items:center;padding:16px;background:rgba(4,10,20,.62);color:#f4f7ff;text-align:center;-webkit-user-select:none;user-select:none}"
"#missionCard[data-on]{display:grid}"
"#missionCard .in{display:grid;justify-items:center;gap:14px;width:min(680px,100%);padding:40px 32px 34px;border-radius:24px;box-sizing:border-box;background:linear-gradient(180deg,rgba(20,38,62,.97),rgba(9,18,33,.98));border:1px solid rgba(159,246,255,.42);box-shadow:0 30px 70px -30px #000,0 0 0 6px rgba(159,246,255,.1)}"
"#missionCard small{font:700 15px var(--mono);letter-spacing:.3em;color:#06111a;background:#9ff6ff;padding:6px 14px 6px 18px;border-radius:999px}"
"#missionCard h1{margin:6px 0 0;font:800 clamp(34px,6vw,58px)/1.2 var(--sans);letter-spacing:-.01em;word-break:keep-all;text-wrap:balance}"
"#missionCard p{margin:0;font:500 clamp(17px,2.4vw,21px)/1.6 var(--sans);color:#bfe7ff;word-break:keep-all}"
"#missionCard button{margin-top:14px;min-height:60px;padding:0 44px;border:0;border-radius:999px;background:#9ff6ff;color:#06111a;font:800 clamp(18px,2.6vw,22px) var(--sans);box-shadow:0 0 0 6px rgba(159,246,255,.22);cursor:pointer}"
"#missionCard button:active{transform:scale(.97)}#missionCard button:focus-visible{outline:3px solid #fff;outline-offset:4px}"
"#alarmEdge{position:fixed;inset:0;z-index:36;pointer-events:none;opacity:0;box-shadow:inset 0 0 0 6px rgba(255,74,58,.85),inset 0 0 120px rgba(255,74,58,.55);transition:opacity .25s}#alarmEdge[data-on]{opacity:1}"
# walking: the mission box is read from a tablet at arm's length
"body.walk #questHud{width:min(640px,calc(100vw - 24px))}body.walk #questHud b#qhT{font-size:21px}body.walk #questHud #qhHint{font-size:15px}body.walk #questHud small{font-size:11px}body.walk #questHud small em{font-size:15px}body.walk #questHud .nav small{font-size:12px}body.walk #questHud .nav b{font-size:21px!important}"
# the mission clear / coordinates card
"#qReward .in{gap:14px;width:min(640px,92vw);padding:38px 30px 32px;border-radius:24px;box-sizing:border-box;background:linear-gradient(180deg,rgba(20,38,62,.94),rgba(9,18,33,.96));border:1px solid rgba(159,246,255,.38);box-shadow:0 30px 70px -30px #000,0 0 0 6px rgba(159,246,255,.08)}"
"#qReward small{font:700 14px var(--mono);letter-spacing:.24em;color:#06111a;background:#9ff6ff;padding:6px 12px 6px 16px;border-radius:999px}"
"#qReward h1{font:800 clamp(30px,5.2vw,46px)/1.25 var(--sans);word-break:keep-all;text-wrap:balance}"
"#qReward p{font-size:clamp(16px,2.2vw,19px);word-break:keep-all}"
"#qReward #qrCount{padding:6px 16px;border-radius:999px;border:1px solid rgba(159,246,255,.35);font:700 15px var(--sans);color:#dffcff}"
"#qReward .zs{gap:10px;margin-top:4px}"
"#qReward .z{display:grid;justify-items:center;gap:8px;padding:18px 16px 20px;border-radius:18px;background:rgba(159,246,255,.08);border:2px solid rgba(159,246,255,.55);box-shadow:0 0 34px rgba(159,246,255,.18);text-align:center}"
"#qReward .z span{font:700 14px var(--sans);letter-spacing:.04em;color:#9ff6ff}"
"#qReward .z code{font-size:clamp(26px,5vw,40px);letter-spacing:.01em;white-space:nowrap}"
"#qReward .go{min-height:58px;padding:0 36px;font:800 clamp(17px,2.4vw,20px) var(--sans)}#qReward .go:disabled{opacity:.55;box-shadow:none}"
"@media (prefers-reduced-motion:no-preference){"
"#missionCard[data-on] .in{animation:mcIn .5s cubic-bezier(.16,1,.3,1) both}#missionCard[data-on] h1{animation:mcUp .55s .12s cubic-bezier(.16,1,.3,1) both}#missionCard[data-on] p{animation:mcUp .55s .22s cubic-bezier(.16,1,.3,1) both}#missionCard[data-on] button{animation:mcUp .55s .34s cubic-bezier(.16,1,.3,1) both}"
"#qReward[data-on] h1{animation:mcUp .55s .1s cubic-bezier(.16,1,.3,1) both}#qReward[data-on] .z{animation:mcIn .6s .35s cubic-bezier(.16,1,.3,1) both}#qReward[data-on] .row{animation:mcUp .5s .6s cubic-bezier(.16,1,.3,1) both}"
"#alarmEdge[data-on]{animation:alarmP .9s ease-in-out infinite}}"
"@keyframes mcIn{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:none}}@keyframes mcUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}@keyframes alarmP{50%{opacity:.45}}")
k = s.find("</style></head><body>"); assert s[:k].count('{') == s[:k].count('}')   # brace depth zero at the insertion point
rep("</style></head><body>", CSS + "</style></head><body>")
assert '\r\n' not in s and '—' not in CSS
P.write_bytes(s.encode('utf-8'))
# the script file follows (the user asked for the urgent line; they edit the wording there)
D = ROOT / 'docs/chapter05_script.md'; d = D.read_bytes().decode('utf-8'); assert d.count('……네이티가 없어요.') == 1
D.write_bytes(d.replace('……네이티가 없어요.', '……잠깐만요. 네이티가 없어요!').encode('utf-8'))
print('patched', len(s))
