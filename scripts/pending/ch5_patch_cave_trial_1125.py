"""미션 5 동굴 개편안 2 적용 (사용자 2026-11-25 「걍 적용해봐」): 역전재판식 증언 → 이의 있어요 → 벽화 증거, 횃불 셋.
벽화 순서: 폭풍(증거: 갈라진 땅·마른 샘) / 함께 걷던 날 / 갈라진 길(새 그림) / 떠나는 날(+반전: 원류민이 보이드를 부숨) / 마지막 벽. 옛 「약속」 벽화는 뺌."""
import json, sys
p = 'C:/Users/dlgus/break_out/chapter05/index.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit(f'match {c} (want {n}): {a[:90]}')
    s = s.replace(a, b)
def cut_between(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i)
    if s.count(start) != 1:
        sys.exit('start not unique: ' + start[:60])
    s = s[:i] + new + s[j:]

# ---------- 1. mural pictures ----------
# scene 1: the 원류민 carrying them move into the base; the worn spot now hides cracked ground and a dried spring
rep("""      [668, 728].forEach((x, i)=> tree(g, x, 250 - i*10, 170, OC)); },
    gap(g){ fig(g, 480, 430, 170, OC, {kind:'won', legs:'walk', armL:1.2, armR:1.4}); fig(g, 610, 424, 176, OC, {kind:'won', legs:'walk', armL:1.3, armR:1.1, staff:true}); fig(g, 545, 356, 100, WT, {lie:-0.35, hair:'#2f5f9a'}); }},""",
"""      [668, 728].forEach((x, i)=> tree(g, x, 250 - i*10, 170, OC));
      fig(g, 470, 430, 170, OC, {kind:'won', legs:'walk', armL:1.2, armR:1.4}); fig(g, 590, 424, 176, OC, {kind:'won', legs:'walk', armL:1.3, armR:1.1, staff:true}); fig(g, 530, 356, 100, WT, {lie:-0.35, hair:'#2f5f9a'}); },
    gap(g){ /* 2026-11-25: the island was already sick before they came — cracked ground and a dried spring */
      g.fillStyle = DK; g.beginPath(); g.ellipse(700, 400, 54, 17, 0, 0, 6.3); g.fill(); g.strokeStyle = WT; g.lineWidth = 4; g.beginPath(); g.ellipse(700, 400, 54, 17, 0, 0, 6.3); g.stroke();
      g.strokeStyle = RD; g.lineCap = 'round'; [[[650, 470], [668, 444], [660, 428], [684, 404]], [[700, 476], [708, 450], [724, 436], [716, 414]], [[748, 466], [736, 444], [744, 424]], [[700, 384], [690, 366], [702, 350]]].forEach(L=>{ g.lineWidth = 6; g.beginPath(); L.forEach(([x, y], k)=> k ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); });
      g.strokeStyle = WT; g.lineWidth = 3; [[676, 400, 690, 406], [712, 396, 726, 404]].forEach(([a, b, c, d])=>{ g.beginPath(); g.moveTo(a, b); g.lineTo(c, d); g.stroke(); }); }},""")
rep("{worn:[420, 150, 290, 290], base(g){ hands(g, 11);", "{worn:[624, 330, 140, 150], base(g){ hands(g, 11);")

# scene 2 「약속」 out; 「함께 걷던 날」 moves up; new 「갈라진 길」; 「떠나는 날」 gains a second worn spot
i0 = s.index("  /* 2. 약속: 눈 지팡이를")
i1 = s.index("  /* 3. 함께 걷던 날:")
promise = s[i0:i1]
s = s[:i0] + s[i1:]
i2 = s.index("  /* 4. 떠나는 날:")
i3 = s.index("  /* 5. 마지막 벽:")
split = """  /* 3. 갈라진 길 (2026-11-25): 붉게 빛나는 렌의 장치와 렌, 말라 버린 나무와 떠나는 새 떼, (닳은 자리) 렌 앞을 팔 벌려 막아선 노아와 루나 */
  {worn:[400, 190, 200, 270], base(g){ hands(g, 29); g.fillStyle = RD; [[70, 450, 170, 100], [92, 350, 126, 100], [116, 250, 78, 90]].forEach(([x, y, w, h])=> g.fillRect(x, y - h, w, h));
      for(let i = 0; i < 9; i++){ const a = -2.8 + i*0.35; limb(g, 155 + Math.cos(a)*58, 150 + Math.sin(a)*58, 155 + Math.cos(a)*100, 150 + Math.sin(a)*100, 6, RD); }
      fig(g, 320, 440, 180, WT, {armL:2.2, armR:0.4, hair:DK, flip:true});
      [[640, 330], [722, 312]].forEach(([x, y])=>{ g.strokeStyle = DK; g.lineCap = 'round'; g.lineWidth = 8; g.beginPath(); g.moveTo(x, 470); g.lineTo(x, y); g.moveTo(x, y + 40); g.lineTo(x - 34, y + 6); g.moveTo(x, y + 20); g.lineTo(x + 30, y - 8); g.stroke(); });
      g.strokeStyle = WT; g.lineWidth = 4; [[600, 120], [646, 92], [690, 128], [734, 70], [560, 80]].forEach(([x, y])=>{ g.beginPath(); g.moveTo(x - 16, y - 8); g.quadraticCurveTo(x - 6, y - 12, x, y); g.quadraticCurveTo(x + 6, y - 12, x + 16, y - 8); g.stroke(); }); },
    gap(g){ fig(g, 450, 440, 176, WT, {armL:1.7, armR:1.7, hair:'#2f5f9a', flip:true}); fig(g, 545, 440, 168, WT, {armL:1.7, armR:1.7, hair:OC, flip:true}); }},
  /* 4. 떠나는 날: 렌의 장치, 섬을 떠나는 배 위의 두 사람, (닳은 자리) 바닷가에 홀로 선 보이드, (두 번째 닳은 자리, 반전) 그 로봇을 부수는 원류민들 */
  {worn:[420, 250, 150, 230], worn2:[584, 150, 184, 330], base(g){ hands(g, 41); g.fillStyle = RD; [[24, 450, 110, 80], [38, 370, 82, 70], [54, 300, 50, 60]].forEach(([x, y, w, h])=> g.fillRect(x, y - h, w, h));
      for(let i = 0; i < 9; i++){ const a = -2.8 + i*0.35; limb(g, 79 + Math.cos(a)*40, 230 + Math.sin(a)*40, 79 + Math.cos(a)*68, 230 + Math.sin(a)*68, 5, RD); }
      waves(g, 150, 560, 420, WT); boat(g, 290, 392, 1.2, WT, false); fig(g, 254, 384, 96, WT, {armR:1.9, hair:'#2f5f9a'}); fig(g, 326, 384, 94, WT, {armL:1.9, hair:OC}); },
    gap(g){ robot(g, 495, 450, 150, CY); },
    gap2(g){ g.save(); g.translate(676, 452); g.rotate(1.25); robot(g, 0, 0, 120, CY); g.restore(); g.fillStyle = CY; [[630, 466, 14], [728, 470, 10], [700, 440, 8]].forEach(([x, y, r])=>{ g.beginPath(); g.arc(x, y, r, 0, 6.3); g.fill(); });
      fig(g, 618, 440, 168, OC, {kind:'won', armL:2.5, armR:0.9, staff:true}); fig(g, 738, 440, 164, OC, {kind:'won', armL:0.9, armR:2.4, flip:true}); }},
"""
s = s[:i2] + split + s[i3:]
assert promise and 'gap(g){ eye(g, 384, 150' in promise

# muralPaint: a second worn spot that fills with its own k2
rep("root.muralPaint = function(g, i, k){ const S = SCENES[i];", "root.muralPaint = function(g, i, k, k2 = 0){ const S = SCENES[i];")
rep("S.base(g); g.globalAlpha = 0.88*k; S.gap(g); g.restore();", "S.base(g); g.globalAlpha = 0.88*k; S.gap(g); if(S.gap2){ g.globalAlpha = 0.88*k2; S.gap2(g); } g.restore();")
rep("""const [wx, wy, ww, wh] = S.worn; if(ww && k < 1){ g.globalAlpha = 1 - k; for(let n = 0; n < 420; n++){ const x = wx + rn()*ww, y = wy + rn()*wh, dx = (x - wx - ww/2)/(ww/2), dy = (y - wy - wh/2)/(wh/2); if(dx*dx + dy*dy > 1) continue; g.fillStyle = n % 4 ? 'rgba(118,102,86,0.9)' : 'rgba(138,121,102,0.75)'; g.beginPath(); g.ellipse(x, y, 6 + rn()*12, 4 + rn()*8, rn()*3, 0, 6.3); g.fill(); } g.globalAlpha = 1; }""",
"""[[S.worn, k], [S.worn2, k2]].forEach(([W, kk])=>{ if(!W) return; const [wx, wy, ww, wh] = W; if(ww && kk < 1){ g.globalAlpha = 1 - kk; for(let n = 0; n < 420; n++){ const x = wx + rn()*ww, y = wy + rn()*wh, dx = (x - wx - ww/2)/(ww/2), dy = (y - wy - wh/2)/(wh/2); if(dx*dx + dy*dy > 1) continue; g.fillStyle = n % 4 ? 'rgba(118,102,86,0.9)' : 'rgba(138,121,102,0.75)'; g.beginPath(); g.ellipse(x, y, 6 + rn()*12, 4 + rn()*8, rn()*3, 0, 6.3); g.fill(); } g.globalAlpha = 1; } });""")

# muralRoom: k2 state, reveal2, torches on/off
rep("SCENES.forEach((S, i)=>{ const st = {k:0}; const tex = canvasTex(768, 480, g=> muralPaint(g, i, st.k));", "SCENES.forEach((S, i)=>{ const st = {k:0, k2:0}; const tex = canvasTex(768, 480, g=> muralPaint(g, i, st.k, st.k2));")
rep("murals.push({m, tex, st, dir, lit:0.3, want:0.3, fill:0}); });", "murals.push({m, tex, st, dir, lit:0.3, want:0.3, fill:0, fill2:0}); });")
rep("    reveal(i){ murals[i].fill = 1; },", "    reveal(i){ murals[i].fill = 1; }, reveal2(i){ murals[i].fill2 = 1; },\n    torches(n){ torches.forEach((T, k)=>{ T.off = k >= n*2; }); },   /* 2026-11-25: a wrong answer puts out a pair of torches (three lives) */")
rep("    whole(i){ const m = murals[i]; m.fill = 1; m.st.k = 1; m.tex.userData.redraw(); },", "    whole(i){ const m = murals[i]; m.fill = m.fill2 = 1; m.st.k = m.st.k2 = 1; m.tex.userData.redraw(); },")
rep("    reset(){ murals.forEach(m=>{ m.fill = 0; m.st.k = 0;", "    reset(){ torches.forEach(T=>{ T.off = false; }); murals.forEach(m=>{ m.fill = m.fill2 = 0; m.st.k = m.st.k2 = 0;")
rep("torches.forEach((T, n)=>{ const p = t + T.ph, k = 1.0 +", "torches.forEach((T, n)=>{ T.fl.visible = !T.off; if(T.off){ T.Lt.intensity = 0; return; } const p = t + T.ph, k = 1.0 +")
rep("if(m.fill > m.st.k){ m.st.k = Math.min(m.fill, m.st.k + dt/1.5); m.tex.userData.redraw(); } });", "if(m.fill > m.st.k){ m.st.k = Math.min(m.fill, m.st.k + dt/1.5); m.tex.userData.redraw(); } if(m.fill2 > m.st.k2){ m.st.k2 = Math.min(m.fill2, m.st.k2 + dt/1.5); m.tex.userData.redraw(); } });")
rep("    state:()=> ({focus, k:murals.map(m=> +m.st.k.toFixed(2)), lit:", "    state:()=> ({focus, k:murals.map(m=> +m.st.k.toFixed(2)), k2:murals.map(m=> +m.st.k2.toFixed(2)), torches:torches.filter(T=> !T.off).length, lit:")

# ---------- 2. the trial data ----------
W = lambda w, t: {"who": w, "text": t}
N = lambda t: {"who": "", "nar": True, "text": t}
TRIAL = [
 {"intro": "mural1", "objector": "리코",
  "claim": ["그들이 오기 전까지 이 섬은 아무 탈이 없었다.", "우리 선대는 쓰러진 그들을 거두어 주었다.", "그런데 그들은 도와준다는 명목하에 섬을 망가뜨렸다."], "lie": 0,
  "claimRe": ["", "벽에 그려진 그대로다. 우리가 그들을 데려갔다.", "그건 너희도 큐브에서 봤을 거다."],
  "light": [W("보이드", "오른쪽 아래가 닳아 있어. 내 기록이랑 겹쳐 볼게.")],
  "ev": [{"who": "제로", "text": "부서진 배 조각이요!", "re": "배가 부서진 건 그들 사정이다."},
         {"who": "제로", "text": "원류민에게 들려 가는 세 사람이요!", "re": "그래. 우리가 그들을 데려갔다. 그래서?"},
         {"who": "리코", "text": "갈라진 땅이랑 말라 버린 샘이요!", "ok": True}],
  "win": [W("리코", "땅이 벌써 갈라져 있어요. 샘도 말라 있고요."), W("리코", "세 사람이 오기 전부터 섬이 아팠던 거예요."),
          W("코덱스", "……일루아가 약해지는 해였다. 백 년에 한 번 오는."),
          W("보이드", "그래서 토네이도가 섬 안까지 들어올 수 있었던 거야. 원래는 바깥 사람이 들어올 수 없는 섬이니까."),
          W("코덱스", "섬이 먼저 그들을 들인 셈이군.")]},
 {"intro": [N("측정기를 든 루나가 숲을 걷고, 노아가 물길 끝에 앉아 무언가를 그린다. 루나 옆자리가 닳아 있다."), W("코덱스", "그들이 섬을 재고 다니던 때다.")], "objector": "제로",
  "claim": ["인간들은 숲을 제멋대로 헤집고 다녔다.", "우리에게는 한 번도 묻지 않았다.", "재고, 적고, 가져갔을 뿐이다."], "lie": 1,
  "claimRe": ["숲을 걸은 건 맞다. 벽에도 그려져 있지.", "", "측정기를 든 게 보이지 않나."],
  "light": [W("보이드", "루나 옆자리, 내 기록에 뭔가 남아 있어. 비춰 볼게.")],
  "ev": [{"who": "리코", "text": "측정기를 든 루나요!", "re": "그게 바로 섬을 쟀다는 증거다."},
         {"who": "리코", "text": "물길에 다리를 그리는 노아요!", "re": "다리를 그렸다고 우리에게 물은 건 아니다."},
         {"who": "제로", "text": "루나 옆에 꽃 꽂은 아이요!", "ok": True}],
  "win": [W("제로", "루나가 이 아이한테 뭔가 물어보고 있어요. 머리에 꽃 꽂은 아이요."),
          W("보이드", "루나는 값이 이상하면 이 아이한테 먼저 물었어. 아이가 고개를 끄덕여야 적었지."),
          W("제로", "이 아이, 누구예요?"), W("코덱스", "……나다."), W("코덱스", "고개를 끄덕인 건 나였군. 잊고 있었다.")]},
 {"intro": [N("붉게 빛나는 커다란 장치 옆에 렌이 서 있다. 나무는 말라 있고, 새 떼가 섬을 떠난다."), W("코덱스", "렌의 장치다. 섬이 무너지기 시작한 때지.")], "objector": "리코",
  "claim": ["렌의 장치는 날마다 커졌다.", "샘이 마르고 새들이 떠났다.", "나머지 둘은 그걸 보고만 있었다."], "lie": 2,
  "claimRe": ["벽에 그대로 있지 않나.", "새들이 떠난 건 나도 봤다.", ""],
  "light": [W("보이드", "장치 앞이 닳아 있어. 비춰 볼게.")],
  "ev": [{"who": "제로", "text": "붉게 빛나는 장치요!", "re": "그래, 그게 섬을 망가뜨렸다. 그래서?"},
         {"who": "제로", "text": "섬을 떠나는 새 떼요!", "re": "새들이 떠난 건 둘이 막지 않았다는 뜻이기도 하다."},
         {"who": "리코", "text": "렌 앞을 막아선 노아랑 루나요!", "ok": True}],
  "win": [W("리코", "노아랑 루나가 렌 앞을 막고 있어요. 보고만 있던 게 아니에요."),
          W("보이드", "내 기록에 그날 목소리가 남아 있어. 「렌. 여기서 멈춰야 해.」"),
          W("보이드", "렌은 이렇게 대답했어. 「조금만 더 하면 돼. 시스템이 완성되면 다 지킬 수 있어.」"),
          W("코덱스", "렌도 섬을 지키려 했다는 건가."),
          W("리코", "지키려는 마음은 같았는데, 혼자서 다 정하려고 한 거예요."),
          W("코덱스", "……그날 숲이 유난히 시끄러웠지.")]},
 {"intro": [N("렌의 장치를 뒤로하고, 두 사람이 배를 타고 섬을 떠난다. 바닷가 쪽이 크게 닳아 있다."), W("코덱스", "그들이 떠난 날이다.")], "objector": "제로",
  "claim": ["렌을 막지 못하자 둘은 배를 탔다.", "섬에는 아무것도 남기지 않았다.", "그날 나는 그들이 섬을 버렸다고 생각했다."], "lie": 1,
  "claimRe": ["배를 탄 건 벽에도 그려져 있다.", "", "그건 내 마음이다. 벽이 대신 말해 줄 수는 없다."],
  "light": [W("보이드", "바닷가 쪽…… 내 기록이랑 같은 자리야. 비춰 볼게.")],
  "ev": [{"who": "리코", "text": "섬을 떠나는 배요!", "re": "떠났다는 증거일 뿐이다."},
         {"who": "리코", "text": "붉게 빛나는 장치요!", "re": "그건 렌이 남긴 것이다. 둘이 남긴 게 아니다."},
         {"who": "제로", "text": "바닷가의 작은 로봇이요!", "ok": True}],
  "win": [W("제로", "바닷가에 보이드가 있어요!"),
          W("보이드", "노아와 루나는 떠나기 전에 나를 만들었어. 섬에 무슨 일이 생기는지 기록해 두고, 언젠가 누군가에게 전하라고."),
          W("리코", "버리고 간 게 아니었어요. 기록을 남기고 간 거예요.")],
  "twistPre": [N("보이드의 불빛이 옆 벽에 닿다가 멈춘다."), W("보이드", "……이 옆은 비추고 싶지 않아."), W("제로", "보이드?"), N("코덱스가 지팡이로 직접 벽을 밝힌다.")],
  "twist": [N("원류민들이 작은 로봇을 둘러싸고 부수고 있다."), W("코덱스", "……그 로봇을 부순 건 우리였다."),
            W("코덱스", "기술이 다시 시작될까 두려웠다. 그래서 진실을 남긴 눈을 우리 손으로 묻었다."),
            W("제로", "그래서 보이드가 코덱스를 그렇게 무서워했구나……"),
            W("보이드", "괜찮아. 제로가 날 다시 고쳐 줬잖아. 그래서 지금 이걸 보여 줄 수 있는 거야."),
            W("코덱스", "끝까지 읽지 않은 건 나였군.")]},
]
FAIL = [W("코덱스", "……됐다. 벽도 제대로 읽지 못하는군."), N("코덱스가 등을 돌린다. 꺼졌던 횃불이 다시 타오른다."), W("보이드", "다시 보자. 닳은 자리에 답이 있어.")]
data = 'const CAVE_TRIAL = ' + json.dumps(TRIAL, ensure_ascii=False) + ', CAVE_FAIL = ' + json.dumps(FAIL, ensure_ascii=False) + ';   /* 2026-11-25 개편안 2 (docs/보이드의기록_동굴대사.md) */\n'
rep("const CAVE_NEED = 4;", data + "const CAVE_NEED = 4;")

# ---------- 3. choice dialog: a label, torches as lives, the current question for the checks ----------
rep("d.innerHTML = '<div class=\"trust\">코덱스 설득<span id=\"chTrust\"></span></div>", "d.innerHTML = '<div class=\"trust\">횃불<span id=\"chTrust\"></span></div>")
rep("function choiceAsk(c, trust){ if(ffOn()) return Promise.resolve(c.opts.findIndex(o=> o.ok)); const d = choiceDlg(); $('chQ').textContent = c.q; $('chTrust').innerHTML = Array.from({length:CAVE_CHOICE.length}, (_, i)=> `<i class=\"${i < trust ? 'ok' : ''}\"></i>`).join('');",
    "let CHOICE_CUR = null;\nfunction choiceAsk(c, trust, of = CAVE_CHOICE.length){ CHOICE_CUR = c; if(ffOn()) return Promise.resolve(c.opts.findIndex(o=> o.ok)); const d = choiceDlg(); $('chQ').textContent = c.q; d.querySelector('.q small').textContent = c.label || '코덱스'; $('chTrust').innerHTML = Array.from({length:of}, (_, i)=> `<i class=\"${i < trust ? 'ok' : ''}\"></i>`).join('');")
rep("window.__choiceOk = q=>{ const c = CAVE_CHOICE.find(c=> c.q === q); return c ? c.opts.findIndex(o=> o.ok) : 0; };",
    "window.__choiceOk = q=>{ const c = CHOICE_CUR && CHOICE_CUR.q === q ? CHOICE_CUR : CAVE_CHOICE.find(c=> c.q === q); return c ? c.opts.findIndex(o=> o.ok) : 0; };")

# ---------- 4. the cave story: four trials, then the last wall ----------
start = "  let trust = 0, round = 0, failed = false; const ask = async i=>{"
end = "  await cut(()=> room.place(4, row));"
new = """  const MARK = ['①', '②', '③'];
  const trial = async i=>{ const T = CAVE_TRIAL[i]; let lives = 3; room.torches(3);
    await talk(typeof T.intro === 'string' ? STORY[T.intro] : T.intro); if(dead()) return;
    await talk([{who:'코덱스', text:'내 말을 잘 들어라.'}, ...T.claim.map((c, n)=> ({who:'코덱스', text:`${MARK[n]} ${c}`}))]); if(dead()) return;
    await talk(T.light); if(dead()) return; room.reveal(i); sfx('sparkle'); await wait(reduce ? 200 : 1700); if(dead()) return;
    const miss = async re=>{ lives--; room.torches(lives); sfx('error'); await talk([{who:'코덱스', img:'codex_dark', text:re}, {who:'', nar:true, text:lives > 0 ? `횃불이 꺼진다. 남은 횃불 ${lives}개.` : '마지막 횃불이 꺼진다.'}]); if(dead()) return;
      if(lives <= 0){ qPop('설득 실패!'); await talk(CAVE_FAIL); lives = 3; room.torches(3); } };
    for(;;){ if(dead()) return;
      const a = await choiceAsk({q:'내 말 중에 벽화와 다른 게 있다면 짚어 봐라.', label:'코덱스의 증언', opts:T.claim.map((c, n)=> ({who:'코덱스', text:`${MARK[n]} ${c}`, ok:n === T.lie}))}, lives, 3); if(dead()) return;
      if(a !== T.lie){ await miss(T.claimRe[a]); continue; }
      await talk([{who:T.objector, text:`이의 있어요! 「${T.claim[T.lie]}」 이 말, 벽화랑 달라요.`}]); if(dead()) return;
      const b = await choiceAsk({q:'어디가 다르다는 거지? 벽에서 찾아 봐라.', label:'증거', opts:T.ev}, lives, 3); if(dead()) return;
      if(!T.ev[b].ok){ await miss(T.ev[b].re); continue; }
      sfx('sparkle'); qPop('반박 성공!'); break; }
    await talk(T.win); if(dead()) return;
    if(T.twist){ await talk(T.twistPre); if(dead()) return; room.reveal2(i); sfx('dark'); await wait(reduce ? 200 : 1900); if(dead()) return; await talk(T.twist); } };
  for(let i = 0; i < CAVE_TRIAL.length; i++){
    if(i > 0){ await cut(()=> room.place(i, row)); if(dead()) return; } else room.place(0, row);
    await wait(reduce ? 200 : 1300); if(dead()) return;
    room.zoom(i); await wait(reduce ? 200 : 1500); if(dead()) return;
    await trial(i); if(dead()) return; }
  room.torches(3);
"""
cut_between(start, end, new)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
