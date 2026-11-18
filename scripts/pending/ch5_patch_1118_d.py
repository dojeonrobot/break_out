# 2026-11-18 묶음 3-2: 동굴 = 코덱스 설득. 동굴에 들어가면 미션 카드, 벽화마다 선택지(미연시식), 믿음이 모자라면 다시.
import io, json
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)
MARK = "</style></head><body>"
CSS = ("#choiceDlg{position:fixed;inset:0;z-index:37;display:none;align-items:flex-end;justify-content:center;padding:0 12px calc(16px + env(safe-area-inset-bottom,0px));background:linear-gradient(to top,rgba(4,8,16,.82),rgba(4,8,16,.3) 55%,transparent 80%);-webkit-user-select:none;user-select:none}"
       "#choiceDlg[data-on]{display:flex}#choiceDlg .in{display:grid;gap:12px;width:min(820px,100%)}"
       "#choiceDlg .q{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:14px;padding:16px 20px;border-radius:18px;background:linear-gradient(180deg,rgba(18,28,46,.96),rgba(8,13,24,.97));border:1px solid rgba(159,246,255,.3);color:#f4f7ff}"
       "#choiceDlg .q img{width:64px;height:64px;object-fit:cover;object-position:50% 8%;border-radius:50%;background:#1b2a44}"
       "#choiceDlg .q p{margin:0;font:500 17px/1.6 var(--sans);word-break:keep-all}#choiceDlg .q small{display:block;font:700 13px var(--sans);color:#9ff6ff;margin-bottom:2px}"
       "#choiceDlg .trust{display:grid;justify-items:end;gap:6px;font:600 12px var(--sans);color:#bfd6ea;white-space:nowrap}#choiceDlg .trust span{display:flex;gap:5px}#choiceDlg .trust i{width:14px;height:14px;border-radius:50%;box-sizing:border-box;border:2px solid rgba(159,246,255,.5)}#choiceDlg .trust i.ok{background:#9ff6ff;border-color:#9ff6ff}"
       "#choiceDlg .opts{display:grid;gap:10px}#choiceDlg .opts button{display:grid;grid-template-columns:auto minmax(0,1fr);gap:14px;align-items:center;min-height:60px;padding:12px 18px;text-align:left;border-radius:14px;border:1px solid rgba(159,246,255,.45);background:rgba(15,29,48,.96);color:#f4f7ff;font:500 17px/1.5 var(--sans);word-break:keep-all;cursor:pointer}"
       "#choiceDlg .opts button b{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:#9ff6ff;color:#06111a;font:700 15px var(--mono)}#choiceDlg .opts button em{display:block;font:700 12px var(--sans);font-style:normal;color:#9ff6ff}"
       "#choiceDlg .opts button:hover,#choiceDlg .opts button:focus-visible{background:#17304e;border-color:#9ff6ff;outline:none}#choiceDlg .opts button:active{transform:scale(.99)}"
       "@media (max-width:600px){#choiceDlg .q{grid-template-columns:minmax(0,1fr);gap:8px}#choiceDlg .q img{display:none}#choiceDlg .trust{justify-items:start}#choiceDlg .q p,#choiceDlg .opts button{font-size:15px}}"
       "@media (max-height:480px){#choiceDlg .in{gap:6px}#choiceDlg .q{padding:8px 14px}#choiceDlg .q img{width:40px;height:40px}#choiceDlg .opts{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}#choiceDlg .opts button{min-height:48px;padding:8px 10px;font-size:13px;grid-template-columns:minmax(0,1fr)}#choiceDlg .opts button b{display:none}}\n")
rep(MARK, CSS + MARK)

# the quest: found first, then persuaded
rep("short:'선대의 기록', title:'코덱스를 찾아라', hint:'북쪽 해안, 눈이 빛나는 곳'", "short:'코덱스 설득', title0:'코덱스를 찾아라', title:'코덱스를 설득하라', hint:'북쪽 해안, 눈이 빛나는 곳'")
rep("let MCARD = null, MCARD_R = null, MCARD_NEXT = null; const MCARD_WHO = {", "let MCARD = null, MCARD_R = null, MCARD_NEXT = null; const MCARD_WHO = {")

CHOICES = [
 {"q": "선대는 그들을 구했다. 그 뒤에 섬이 어떻게 됐는지는 너희도 봤을 거다. 할 말이 있나?",
  "opts": [{"who": "리코", "text": "구해 준 은혜를 저희가 대신 갚고 싶어요. 그래서 여기까지 왔어요.", "ok": True, "re": "……은혜를 갚겠다는 말은 처음 듣는군."},
           {"who": "제로", "text": "그건 옛날 일이잖아요. 저희랑은 상관없어요.", "re": "상관없다면 이 벽 앞에 설 이유도 없다."},
           {"who": "제로", "text": "그래도 덕분에 도로랜드가 생겼잖아요!", "re": "그 놀이공원 때문에 섬이 이렇게 됐다."}]},
 {"q": "섬을 해치지 않겠다는 약속은 깨졌다. 환원하겠다는 말도 약속일 뿐이지 않나.",
  "opts": [{"who": "제로", "text": "이번엔 진짜예요. 그냥 믿어 주세요!", "re": "그냥 믿으라는 말은 그때도 들었다."},
           {"who": "리코", "text": "말로만 약속하지 않을게요. 시뮬레이션으로 먼저 확인한 방법만 쓸 거예요.", "ok": True, "re": "……먼저 확인하고 움직이겠다는 거군."},
           {"who": "리코", "text": "약속을 깬 건 렌이지 저희가 아니에요.", "re": "누가 깼는지 따지자는 게 아니다."}]},
 {"q": "그때 나는 그들을 믿었다. 나더러 다시 믿으라는 건가.",
  "opts": [{"who": "리코", "text": "코덱스가 허락하지 않아도 환원은 해야 해요.", "re": "내 뜻과 상관없이 하겠다면 선대와 다를 게 없다."},
           {"who": "제로", "text": "어릴 때 일이니까 이제 잊어요.", "re": "잊으라는 말로는 아무것도 달라지지 않는다."},
           {"who": "제로", "text": "루나가 코덱스에게 먼저 물어봤던 것처럼, 저희도 코덱스에게 먼저 물어볼게요.", "ok": True, "re": "……루나는 늘 그렇게 했지."}]},
 {"q": "환원이 잘못되면 섬은 가라앉는다. 그 두려움을 너희가 아나.",
  "opts": [{"who": "리코", "text": "저희도 무서워요. 그래서 기록을 다 채우고, 잔재를 부수고, 조금씩 환원하는 방법을 찾았어요.", "ok": True, "re": "……두렵다고 말하는 쪽이 더 믿을 만하군."},
           {"who": "제로", "text": "걱정 마세요. 절대 실패 안 해요!", "re": "두려움을 모르는 자에게 섬을 맡길 수는 없다."},
           {"who": "제로", "text": "부수는 것보다는 낫잖아요.", "re": "낫다는 말만으로는 부족하다."}]}]
JS = ("/* ---------- persuading Codex (user, 2026-11-18): after each mural Codex asks, the child picks what to say; a good answer adds a point of trust; three of four are needed ---------- */\n"
      "const CAVE_CHOICE = " + json.dumps(CHOICES, ensure_ascii=False) + ";\n"
      "const CAVE_NEED = 3; let CHOICE_PICK = null;\n"
      "function choiceDlg(){ let d = $('choiceDlg'); if(d) return d; d = document.createElement('div'); d.id = 'choiceDlg'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-labelledby', 'chQ');\n"
      "  d.innerHTML = '<div class=\"in\"><div class=\"q\"><img src=\"img/chars/codex.png?v=20261028c\" alt=\"\"><div><small>코덱스</small><p id=\"chQ\"></p></div><div class=\"trust\">코덱스의 믿음<span id=\"chTrust\"></span></div></div><div class=\"opts\" id=\"chOpts\"></div></div>'; document.body.appendChild(d);\n"
      "  d.addEventListener('click', e=>{ e.stopPropagation(); const b = e.target.closest('#chOpts button'); if(b && CHOICE_PICK) CHOICE_PICK(+b.dataset.k); });\n"
      "  addEventListener('keydown', e=>{ if(!d.dataset.on || !CHOICE_PICK) return; const k = ['Digit1', 'Digit2', 'Digit3', 'Numpad1', 'Numpad2', 'Numpad3'].indexOf(e.code); if(k < 0){ if(e.code === 'Space') { e.preventDefault(); e.stopImmediatePropagation(); } return; } e.preventDefault(); e.stopImmediatePropagation(); CHOICE_PICK(k % 3); }, true); return d; }\n"
      "function choiceAsk(c, trust){ if(ffOn()) return Promise.resolve(c.opts.findIndex(o=> o.ok)); const d = choiceDlg(); $('chQ').textContent = c.q; $('chTrust').innerHTML = Array.from({length:CAVE_CHOICE.length}, (_, i)=> `<i class=\"${i < trust ? 'ok' : ''}\"></i>`).join('');\n"
      "  $('chOpts').innerHTML = c.opts.map((o, k)=> `<button type=\"button\" data-k=\"${k}\"><b>${k + 1}</b><span><em>${esc(o.who)}</em>${esc(o.text)}</span></button>`).join(''); d.dataset.on = '1'; sfx('open'); const at = performance.now();\n"
      "  return new Promise(r=>{ CHOICE_PICK = k=>{ if(performance.now() - at < 600 || !c.opts[k]) return; CHOICE_PICK = null; delete d.dataset.on; sfx('tap'); r(k); }; }); }\n"
      "window.__choice = ()=> $('choiceDlg') && $('choiceDlg').dataset.on ? {q:$('chQ').textContent, n:$('chOpts').children.length, trust:$('chTrust').querySelectorAll('.ok').length} : null; window.__choicePick = k=>{ if(CHOICE_PICK) CHOICE_PICK(k); };\n")
rep("async function caveStory(q){ const tok = ++caveTok,", JS + "async function caveStory(q){ const tok = ++caveTok,")
# was caveStory already async? keep a single keyword
s = s.replace("async async function caveStory", "async function caveStory")
assert s.count("async function caveStory(q){") == 1

# the mission card when the cave scene opens, and a choice after every mural
rep("  await wait(reduce ? 200 : 900); if(dead()) return; await talk(STORY.caveIn); if(dead()) return;\n",
    "  await wait(reduce ? 200 : 900); if(dead()) return; await talk(STORY.caveIn); if(dead()) return;\n"
    "  await missionCard(q, {hint:'알맞은 말을 골라 코덱스의 믿음을 얻으세요'}); if(dead()) return;\n"
    "  let trust = 0, round = 0; const ask = async i=>{ const c = CAVE_CHOICE[i]; await talk([{who:'코덱스', text:c.q}]); if(dead()) return; const k = await choiceAsk(c, trust); if(dead()) return; const o = c.opts[k]; if(o.ok){ trust++; sfx('sparkle'); } else sfx('error');\n"
    "    await talk([{who:o.who, text:o.text}, {who:'코덱스', img:o.ok ? 'codex' : 'codex_dark', text:o.re}, {who:'', nar:true, text:o.ok ? `코덱스의 믿음이 한 칸 찼다. (${trust} / ${CAVE_CHOICE.length})` : '코덱스의 표정이 굳는다.'}]); };\n")
rep("    await talk(after); if(dead()) return; }\n", "    await talk(after); if(dead()) return; await ask(i); if(dead()) return; }\n"
    "  while(trust < CAVE_NEED){ round++; await talk([{who:'코덱스', img:'codex_dark', text:'……아직은 너희를 믿기 어렵다.'}, {who:'보이드', text:'벽화를 다시 보면서 코덱스의 마음을 생각해 보자.'}]); if(dead()) return; trust = 0;\n"
    "    for(let i = 0; i < CAVE_CHOICE.length; i++){ await cut(()=> room.place(i, row)); if(dead()) return; await wait(reduce ? 200 : 700); if(dead()) return; await ask(i); if(dead()) return; } }\n")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("ok", "async" in s[s.index("function caveStory(q)")-8:s.index("function caveStory(q)")])
