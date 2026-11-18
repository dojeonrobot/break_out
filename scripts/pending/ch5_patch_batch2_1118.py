# 2026-11-18 (사용자 요청 묶음 2): 자일로가 시뮬레이터를 켤 때 화면은 연구실 모니터, 잔재를 부순 뒤 노이즈가 사라지는 모션 + 다시 돌리는 연출,
# 「한 곳만 비었어요」 삭제, 자일로가 마지막 위치를 알려 주는 대사.
import io, json
P = "C:/Users/dlgus/break_out/chapter05/index.html"
s = io.open(P, encoding="utf-8", newline="").read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)

# 1. the lab monitor is on screen while Xylo talks: the game dialog opens first (covered with the games), the how-to starts when the talk ends
rep("function sliceGame(){ return new Promise(done=>{ if(ffOn()){ done(); return; }", "function sliceGame(gate){ return new Promise(done=>{ if(ffOn()){ done(); return; }")
rep("  const tutNext = ()=>{ if(S.tut == null) return; sfx('tap');", "  const tutNext = ()=>{ if(S.tut == null || S.tut < 0) return; sfx('tap');")
rep("  const tutKey = e=>{ if(S.tut != null && (e.code === 'Space' || e.code === 'Enter')){", "  const tutKey = e=>{ if(S.tut != null && S.tut >= 0 && (e.code === 'Space' || e.code === 'Enter')){")
rep("  stageStart(0); S.tut = 0; S.tt = 0; S.banner = ''; tutShow(); draw(); }); }", "  stageStart(0); S.tt = 0; S.banner = ''; if(gate){ S.tut = -1; $('slP').textContent = ''; gate.then(()=>{ if(SLICE !== S) return; S.tut = 0; S.tt = 0; tutShow(); }); } else { S.tut = 0; tutShow(); } draw(); }); }")
rep("    if(S.tut != null){ const u = S.tt % 2.6, cx = W2/2,", "    if(S.tut != null && S.tut >= 0){ const u = S.tt % 2.6, cx = W2/2,")
rep("  await new Promise(r=> say(STORY.labGame, r)); await sliceGame(); await new Promise(r=> say(STORY.labGameDone, r));", "  await sliceGame(ffOn() ? null : new Promise(r=> say(STORY.labGame, r))); if(ffOn()) await new Promise(r=> say(STORY.labGame, r)); await new Promise(r=> say(STORY.labGameDone, r));")

# 2. the noise fades out on screen, then the simulation runs again
rep("it.m.material.opacity = (0.25 + 0.6*Math.abs(Math.sin(t*5 + it.ph)))*f;", "it.m.material.opacity = (0.25 + 0.6*Math.abs(Math.sin(t*5 + it.ph)))*f*SIM_NOISE.k;")
rep("  SIM_NOISE = {g, items}; simAnim.push(", "  SIM_NOISE = {g, items, k:1}; simAnim.push(")
a = s.index("async function remRerun(){")
b = s.index("questComplete(q); }", a) + len("questComplete(q); }")
NEW = """const simNoiseOut = ()=> new Promise(r=>{ if(!SIM_NOISE || reduce){ simNoise(false); r(); return; } const t0 = performance.now(); sfx('powerdown');
  const step = ()=>{ const k = Math.min(1, (performance.now() - t0)/2200); if(SIM_NOISE) SIM_NOISE.k = (1 - k)*(1 - k); if(k < 1) requestAnimationFrame(step); else { simNoise(false); r(); } }; requestAnimationFrame(step); });
/* 2026-11-18 (user): the red noise is still there when the lab screen opens, dies away on screen, and only then the simulation runs again */
async function remRerun(){ const q = mini.q, D = STORY.remDone; actBusy = true; stopWalk(); await wait(300); setSim(true); simNoise(true); await wait(reduce ? 400 : 3000);
  await new Promise(r=> say(D.slice(0, 1), r)); await simNoiseOut(); await wait(300);
  buildSim(GLYPH_ZONES.map(z=> z.id)); const endT = Math.max(0, ...REVEALS.map(r=> r.delay + r.dur), ...FADES.map(f=> f.delay + f.dur)); await wait(reduce ? 400 : (endT + 1.2)*1000);
  await new Promise(r=> say(D.slice(1), r)); setSim(false); actBusy = false; questComplete(q); }"""
old = s[a:b]
assert "say(STORY.remDone" in old and old.rstrip().endswith("questComplete(q); }"), old[-200:]
s = s[:a] + NEW + s[b:]

# 3. dialogue: no "one place is empty"; Xylo reads where the last one is
n0 = s.index('"remDone": [')
dec = json.JSONDecoder(); arr, end = dec.raw_decode(s[n0 + len('"remDone": '):])
old_txt = s[n0:n0 + len('"remDone": ') + end]
new_arr = [
 {"who": "자일로", "text": "노이즈가 사라졌어요. 다시 돌려 볼게요."},
 {"who": "리코", "text": "이제 흐름이 흔들리지 않고 제대로 나와요."},
 {"who": "자일로", "text": "이 결과로 마지막 위치를 찾아볼게요. ……관람차 근처에서 반응이 오고 있어요."},
 {"who": "보이드", "text": "그 자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어. 카드에 띄워 둘게."},
] + [l for l in arr if l["who"] == "네이티" or (l["who"] == "제로" and "네이티는 그대로" in l["text"])] + [
 {"who": "자일로", "text": "잔재는 계산을 어지럽혔을 뿐이에요. 일루아가 흔들리는 건 아직 환원을 못 했기 때문입니다. 마지막 스캔을 서둘러 주세요."},
 {"who": "제로", "text": "마지막 기록을 스캔하러 가자!"},
]
assert len(new_arr) == 8, len(new_arr)
s = s.replace(old_txt, '"remDone": ' + json.dumps(new_arr, ensure_ascii=False))
io.open(P, "w", encoding="utf-8", newline="").write(s)

M = "C:/Users/dlgus/break_out/docs/chapter05_script.md"
t = io.open(M, encoding="utf-8", newline="").read()
import re
m = re.search(r"- 리코: 이제 제대로 나와요\. 한 곳만 비었어요\.\r?\n- 보이드: 마지막 빈자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어\. 카드에 띄워 둘게\.", t)
print("script md match:", bool(m))
if m:
    nl = "\r\n" if "\r\n" in m.group(0) else "\n"
    t = t.replace(m.group(0), nl.join(["- 리코: 이제 흐름이 흔들리지 않고 제대로 나와요.", "- 자일로: 이 결과로 마지막 위치를 찾아볼게요. ……관람차 근처에서 반응이 오고 있어요.", "- 보이드: 그 자리와 트윈으로 이어진 캠퍼스 좌표를 찾았어. 카드에 띄워 둘게."]))
    t = t.replace("마지막 기록을 서둘러 주세요.", "마지막 스캔을 서둘러 주세요.")
    io.open(M, "w", encoding="utf-8", newline="").write(t)
print("ok")
