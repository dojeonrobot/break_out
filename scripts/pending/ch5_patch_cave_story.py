# 2026-11-12 (사용자): 코덱스 동굴은 퀘스트가 아니라 선대의 기록을 확인하는 스토리 장면이다.
#   동굴 안 벽화와 그것을 보는 제로·리코·자일로·코덱스의 모습이 보이는 연출(페이지 안 3D 장면으로 결정), 동굴 디자인 개선.
#   - 미션 5: 코덱스를 만나면 대사 → 동굴 안(둥근 방, 벽화 다섯 점)으로 들어감 → 벽화마다 보이드의 불빛이 비추고 닳은 자리가 채워지며 대사 → 마지막 벽 → 밖으로 → 환원(기존 엔딩).
#     그림 글자 해독·가상 시험(caveDlg)은 쓰지 않는다(코드만 남음). 대사는 대본 미션 5를 그대로 옮겼다(게임 지시문만 뺌).
#   - 동굴 바깥: 깊이 있는 입구, 양쪽 돌기둥과 횃불, 덩굴, 길가의 선돌.
import json, pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'caveStory' not in s
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
def L(who, text, **k): return dict(who=who, text=text, **k)
def N(text): return dict(who='', text=text, nar=True)

STORY = {
 'q3found': [L('코덱스', '왔군. 기록을 모두 채웠다고 들었다.'), N('따라온 네이티가 코덱스 곁에서 흩어졌다가 모이기를 되풀이한다. 코덱스가 그 모습을 한참 본다.'),
             L('코덱스', '일루아가 더는 버티지 못하는군.'), L('리코', '네. 이제 일루아를 환원할 수 있어요. 시간이 없어요. 코덱스도 함께해 주셨으면 해요.'),
             L('코덱스', '……그 전에 이걸 봐라. 우리 선대가 이 벽에 남긴 그림이다.')],
 'caveIn': [N('보이드의 불빛만 비치는 동굴. 벽을 따라 그림이 길게 이어져 있다. 군데군데 닳아서 무엇을 그렸는지 알 수 없다.'),
            L('코덱스', '원류민이 섬을 떠나기 전에 새겼다고 들었다. 닳은 곳이 많아서 나도 끝까지 읽은 적이 없다.'), L('제로', '보이드, 벽을 비춰 줄 수 있어?'),
            L('보이드', '응. 그런데 이 그림, 내 기록이랑 닮은 장면이 있어. 노아와 루나가 나한테 남긴 기록이야.'), L('코덱스', '그 로봇에 그때 일이 남아 있다는 건가. ……비춰 봐라.')],
 'mural1': [L('보이드', '노아, 루나, 렌이야. 폭풍에 배가 부서져서 이 섬에 닿았어.'), L('제로', '쓰러진 사람들을 데려가는 건…… 원류민이야?'),
            L('코덱스', '그렇다. 바다에서 그들을 건진 건 우리 선대였지.'), L('리코', '노아랑 루나가 처음부터 섬을 연구하러 온 게 아니었구나.')],
 'mural2': [L('보이드', '원류민은 섬에 대해 아는 걸 알려 줬고, 세 사람은 섬의 이상 현상을 막아 주겠다고 약속했어.'), L('코덱스', '섬을 해치지 않는다는 약속이었다.'),
            L('제로', '처음에는 다 같이 섬을 지키려고 했던 거네요.')],
 'mural3a': [N('측정기를 든 루나가 숲을 걷고, 노아가 물길 끝에 앉아 무언가를 그린다. 루나 옆자리가 닳아 있다.')],
 'mural3': [N('루나 옆에 작은 원류민 아이가 나타난다. 머리에 들꽃이 꽂혀 있다.'), L('보이드', '루나는 값이 이상한 자리마다 이 아이에게 먼저 물어봤어. 아이가 고개를 끄덕이면 그 값을 믿고 적었지.'),
            L('제로', '이 아이, 머리에 꽃이 있어. 누구지?'), L('코덱스', '……나다.'), L('리코', '코덱스요?'), L('코덱스', '선대가 이날을 새겨 두었을 줄은 몰랐다.'),
            L('보이드', '노아는 원류민이 바다로 드나드는 옛 물길 위에 다리를 그리고 있었어. 길을 막지 않도록 몇 번이고 다시 그렸어.')],
 'mural4a': [L('코덱스', '렌의 장치는 점점 커졌다. 두 사람은 그걸 막지 못하고 섬을 떠났지. 나는 그날 그들이 섬을 버렸다고 생각했다.')],
 'mural4': [N('해안에 작은 로봇이 나타난다. 보이드다.'), L('제로', '보이드다! 보이드가 그려져 있어!'),
            L('보이드', '노아와 루나는 떠나기 전에 나를 만들었어. 섬에 무슨 일이 생기는지 기록해 두고, 언젠가 누군가에게 전하라고.'),
            L('리코', '버리고 간 게 아니었어요. 기록을 남기고 간 거예요.'), L('코덱스', '……선대는 그걸 보고 이 벽에 새겼군. 나는 끝까지 읽지 않았다.')],
 'caveEnd': [N('마지막 벽에는 사람 넷이 손을 맞대고 있는 그림이 있다. 원류민 하나, 그리고 노아와 루나를 닮은 둘, 그 뒤로 작은 로봇.'), L('제로', '이건…… 우리 같아.'),
             L('코덱스', '너희에게 초대장을 보낸 건 나다. 약속을 지키려던 자들의 핏줄이라면 내 이야기를 들어 줄 거라 생각했지.'), L('코덱스', '그런데 다시 믿는 게 두려웠다. 그래서 다 부수려 했다.'),
             L('리코', '저희는 노아랑 루나가 남긴 기록으로 여기까지 왔어요. 이번에는 끝까지 같이 해 주세요.'), L('코덱스', '……좋다. 환원해라. 이번에는 내가 너희를 믿어 보겠다.'),
             N('흔들리던 네이티가 코덱스의 지팡이 끝에 잠깐 기대듯 머문다. 빛은 아직 붉다.'), L('코덱스', '서둘러라. 이 아이가 흩어지기 전에.'), L('보이드', '바로 시뮬레이터로 확인하고, 진짜 섬에 환원하자.')],
}
rep('const QUESTS = [\n', 'Object.assign(STORY, ' + json.dumps(STORY, ensure_ascii=False) + ');   /* 2026-11-12 미션 5 = 동굴 벽화 스토리(대본 미션 5 그대로) */\nconst QUESTS = [\n')

CSS = ('body.cavestory #walkHud,body.cavestory #walkPad,body.cavestory #questHud,body.cavestory #miniBox,body.cavestory .lbl,body.cavestory #qMark,body.cavestory #questPill,body.cavestory #restoreBtn{display:none!important}\n')
rep('</style></head><body>\n', CSS + '</style></head><body>\n')

ROOM = r'''/* ---------- mission 5 · the mural chamber (user, 2026-11-12): a story scene, not a quest ---------- */
let CAVE_ROOM = null, caveTok = 0, caveKeep = null;
function muralRoom(){
  if(CAVE_ROOM) return CAVE_ROOM;
  const H = Math.max(1.6, new THREE.Box3().setFromObject(ZERO).getSize(new THREE.Vector3()).y), R = 6.6*H, WH = 4.4*H;
  const sc = new THREE.Scene(); sc.background = new THREE.Color(0x06070a); sc.fog = new THREE.Fog(0x0b0c10, 7*H, 26*H); lightUp(sc, 0xb9b2c4, 0x3a2e24, 1.05);
  let sd = 77; const rnd = ()=> (sd = (sd*16807) % 2147483647)/2147483647;
  { const g = new THREE.CylinderGeometry(R*1.02, R*1.08, WH, 44, 7, true), p = g.attributes.position;
    for(let i = 0; i < p.count; i++){ const x = p.getX(i), y = p.getY(i), z = p.getZ(i), n = 1 + 0.045*Math.sin(x*0.9/H + y*1.3/H)*Math.cos(z*0.8/H + y*0.6/H); p.setXYZ(i, x*n, y, z*n); } g.computeVertexNormals();
    const w = new THREE.Mesh(g, new THREE.MeshLambertMaterial({color:0x51473c, flatShading:true, side:THREE.BackSide})); w.position.y = WH/2 - 0.1*H; sc.add(w);
    add(sc, new THREE.CircleGeometry(R*1.1, 44).rotateX(-Math.PI/2), new THREE.MeshLambertMaterial({color:0x2c2722}), 0, 0, 0, false);
    const dome = new THREE.Mesh(new THREE.SphereGeometry(R*1.1, 24, 10, 0, Math.PI*2, 0, Math.PI/2), new THREE.MeshLambertMaterial({color:0x362f29, flatShading:true, side:THREE.BackSide})); dome.scale.y = 0.42; dome.position.y = WH - 0.2*H; sc.add(dome);
    for(let i = 0; i < 26; i++){ const a = rnd()*6.28, r = (0.25 + rnd()*0.7)*R, h = (0.5 + rnd()*1.4)*H; const st = add(sc, new THREE.ConeGeometry(0.16*H + rnd()*0.14*H, h, 5), flat(0x3d362f), Math.cos(a)*r, WH + R*0.42*(1 - (r/R)*(r/R)) - h/2 - 0.1*H, Math.sin(a)*r, false); st.rotation.x = Math.PI; }
    for(let i = 0; i < 16; i++){ const a = Math.PI*0.06 + rnd()*Math.PI*0.88, r = R*(0.9 + rnd()*0.08), k = (0.3 + rnd()*0.5)*H; add(sc, ICO(k, 0), flat(0x4a4138), Math.cos(a)*r, k*0.4, Math.sin(a)*r, false).rotation.set(rnd()*3, rnd()*3, 0); }
    add(sc, new THREE.CircleGeometry(1.5*H, 20), glowMat(0x9fd4ff, 0.2), 0, 1.6*H, R*0.98, false).rotation.y = Math.PI;   /* the way out, behind */ }
  /* cave paintings: pigment figures on rock, drawn on a canvas; `k` fills the worn spot (0 = worn away, 1 = whole) */
  const OC = '#c9763a', RD = '#a8432c', WT = '#efe2c4', CY = '#9ff6ff';
  const person = (g, x, y, h, col, o = {})=>{ g.save(); g.translate(x, y); if(o.lie) g.rotate(o.lie); g.strokeStyle = col; g.fillStyle = col; g.lineWidth = Math.max(3, h*0.075); g.lineCap = 'round';
    const hd = h*0.14; g.beginPath(); g.arc(0, -h + hd, hd, 0, 6.3); g.fill();
    g.beginPath(); g.moveTo(0, -h + hd*2); g.lineTo(0, o.sit ? -h*0.3 : -h*0.42); g.stroke();
    g.beginPath(); if(o.sit){ g.moveTo(0, -h*0.3); g.lineTo(h*0.26, -h*0.26); g.lineTo(h*0.3, 0); } else { g.moveTo(0, -h*0.42); g.lineTo(-h*0.15, 0); g.moveTo(0, -h*0.42); g.lineTo(h*0.15, 0); } g.stroke();
    const ay = -h*0.66, al = o.armL == null ? 0.5 : o.armL, ar = o.armR == null ? 0.5 : o.armR; g.beginPath(); g.moveTo(0, ay); g.lineTo(-h*0.3, ay + h*0.3*(al*2 - 1)); g.moveTo(0, ay); g.lineTo(h*0.3, ay + h*0.3*(ar*2 - 1)); g.stroke();
    if(o.flower){ g.fillStyle = WT; for(let i = 0; i < 5; i++){ g.beginPath(); g.arc(hd*0.9 + Math.cos(i*1.257)*hd*0.5, -h - hd*0.1 + Math.sin(i*1.257)*hd*0.5, hd*0.3, 0, 6.3); g.fill(); } g.fillStyle = OC; g.beginPath(); g.arc(hd*0.9, -h - hd*0.1, hd*0.24, 0, 6.3); g.fill(); }
    g.restore(); };
  const waves = (g, x0, x1, y, col)=>{ g.strokeStyle = col; g.lineWidth = 4; for(let r = 0; r < 3; r++){ g.beginPath(); for(let x = x0; x <= x1; x += 6){ const yy = y + r*16 + Math.sin(x*0.07 + r)*5; x === x0 ? g.moveTo(x, yy) : g.lineTo(x, yy); } g.stroke(); } };
  const tree = (g, x, y, h, col)=>{ g.fillStyle = col; g.beginPath(); g.moveTo(x, y - h); g.lineTo(x - h*0.3, y - h*0.25); g.lineTo(x + h*0.3, y - h*0.25); g.fill(); g.fillRect(x - 3, y - h*0.25, 6, h*0.25); };
  const robot = (g, x, y, h, col)=>{ g.fillStyle = col; g.strokeStyle = col; g.lineWidth = 5; g.lineCap = 'round'; const w = h*0.5; g.fillRect(x - w/2, y - h*0.55, w, h*0.5); g.beginPath(); g.arc(x, y - h*0.72, h*0.2, 0, 6.3); g.fill();
    g.beginPath(); g.moveTo(x, y - h*0.9); g.lineTo(x, y - h*1.05); g.stroke(); g.beginPath(); g.arc(x, y - h*1.08, 4, 0, 6.3); g.fill(); g.beginPath(); g.moveTo(x - w/2, y - h*0.4); g.lineTo(x - w*0.85, y - h*0.2); g.moveTo(x + w/2, y - h*0.4); g.lineTo(x + w*0.85, y - h*0.2); g.moveTo(x - w*0.2, y - h*0.05); g.lineTo(x - w*0.2, y); g.moveTo(x + w*0.2, y - h*0.05); g.lineTo(x + w*0.2, y); g.stroke();
    g.fillStyle = '#3a2e24'; g.fillRect(x - h*0.12, y - h*0.76, h*0.24, h*0.07); };
  const SCENES = [
    {worn:[430, 170, 270, 230], base(g){ waves(g, 30, 330, 330, WT); g.strokeStyle = RD; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath(); g.moveTo(70, 300); g.quadraticCurveTo(150, 360, 250, 290); g.stroke(); g.beginPath(); g.moveTo(150, 318); g.lineTo(135, 220); g.lineTo(190, 250); g.stroke();
        [[300, 372, -1.45], [356, 384, -1.5], [414, 392, 1.5]].forEach(([x, y, r])=> person(g, x, y, 70, WT, {lie:r})); [610, 660, 705].forEach((x, i)=> tree(g, x, 250 - i*8, 120, OC)); },
      gap(g){ person(g, 470, 372, 96, OC, {armL:0.1, armR:0.9}); person(g, 548, 366, 100, OC, {armL:0.15}); person(g, 506, 366, 70, WT, {lie:-0.5}); }},
    {worn:[300, 235, 170, 150], base(g){ [[150, 0.2], [240, -0.1], [528, 0.1], [618, -0.2]].forEach(([x], i)=> person(g, x, 370, 104, i < 2 ? OC : WT, {sit:true, armR:0.55})); person(g, 384, 196, 92, WT, {sit:true}); person(g, 330, 420, 0, OC);
        g.strokeStyle = OC; g.lineWidth = 3; g.setLineDash([6, 10]); g.beginPath(); g.ellipse(384, 330, 290, 96, 0, 0, 6.3); g.stroke(); g.setLineDash([]); },
      gap(g){ g.strokeStyle = OC; g.lineWidth = 6; g.beginPath(); g.moveTo(322, 318); g.bezierCurveTo(330, 268, 392, 262, 410, 300); g.bezierCurveTo(424, 334, 372, 352, 336, 344); g.closePath(); g.stroke(); g.fillStyle = OC; [[350, 310], [378, 296], [386, 326]].forEach(([x, y])=>{ g.beginPath(); g.arc(x, y, 5, 0, 6.3); g.fill(); });
        g.fillStyle = WT; g.fillRect(430, 300, 30, 40); g.strokeStyle = WT; g.lineWidth = 4; g.beginPath(); g.moveTo(445, 300); g.lineTo(445, 274); g.stroke(); g.beginPath(); g.arc(445, 270, 5, 0, 6.3); g.fill(); }},
    {worn:[250, 215, 120, 190], base(g){ [70, 130, 640, 700].forEach((x, i)=> tree(g, x, 300 - (i%2)*14, 150, OC)); person(g, 200, 384, 124, WT, {armR:0.3}); g.fillStyle = WT; g.fillRect(232, 286, 22, 30);
        g.strokeStyle = CY; g.globalAlpha *= 0.75; g.lineWidth = 7; g.beginPath(); g.moveTo(420, 430); g.bezierCurveTo(470, 380, 560, 400, 600, 330); g.stroke(); g.globalAlpha /= 0.75; person(g, 560, 300, 108, WT, {sit:true, armR:0.6});
        g.strokeStyle = WT; g.lineWidth = 4; g.beginPath(); g.moveTo(600, 278); g.quadraticCurveTo(640, 250, 680, 278); g.moveTo(612, 278); g.lineTo(612, 300); g.moveTo(668, 278); g.lineTo(668, 300); g.stroke(); },
      gap(g){ person(g, 306, 384, 82, OC, {flower:true, armL:0.35}); }},
    {worn:[520, 240, 150, 180], base(g){ g.fillStyle = RD; [[150, 400, 120, 70], [168, 330, 86, 70], [184, 268, 54, 62]].forEach(([x, y, w, h])=> g.fillRect(x, y - h, w, h)); g.strokeStyle = RD; g.lineWidth = 4; for(let i = 0; i < 7; i++){ const a = -2.6 + i*0.35; g.beginPath(); g.moveTo(211 + Math.cos(a)*40, 200 + Math.sin(a)*40); g.lineTo(211 + Math.cos(a)*74, 200 + Math.sin(a)*74); g.stroke(); }
        waves(g, 300, 740, 404, WT); g.strokeStyle = WT; g.lineWidth = 7; g.beginPath(); g.moveTo(330, 372); g.quadraticCurveTo(400, 420, 480, 372); g.stroke(); g.beginPath(); g.moveTo(404, 392); g.lineTo(404, 268); g.lineTo(456, 318); g.lineTo(404, 318); g.stroke(); person(g, 372, 378, 84, WT, {armR:0.2}); person(g, 438, 378, 84, WT, {armL:0.2}); },
      gap(g){ robot(g, 596, 396, 110, CY); }},
    {worn:[0, 0, 0, 0], base(g){ [[258, OC, 0.85, 0.5], [344, WT, 0.5, 0.5], [430, WT, 0.5, 0.5], [516, WT, 0.5, 0.85]].forEach(([x, c, l, r])=> person(g, x, 400, 150, c, {armL:l, armR:r})); g.strokeStyle = WT; g.lineWidth = 9; g.lineCap = 'round'; g.beginPath(); g.moveTo(213, 301); g.lineTo(561, 301); g.stroke(); robot(g, 388, 214, 74, CY); }, gap(){}}];
  const SP = [-72, -36, 0, 36, 72].map(d=> d*Math.PI/180), MW = 3.9*H, MH = MW*480/768, murals = [];
  SCENES.forEach((S, i)=>{ const st = {k:0}; const tex = canvasTex(768, 480, g=>{ g.clearRect(0, 0, 768, 480); const bg = g.createRadialGradient(384, 240, 60, 384, 240, 430); bg.addColorStop(0, 'rgba(112,96,80,1)'); bg.addColorStop(0.72, 'rgba(96,82,68,0.94)'); bg.addColorStop(1, 'rgba(81,71,60,0)'); g.fillStyle = bg; g.fillRect(0, 0, 768, 480);
      let q = 31 + i*7; const rn = ()=> (q = (q*16807) % 2147483647)/2147483647; g.fillStyle = 'rgba(40,32,26,0.22)'; for(let n = 0; n < 240; n++){ g.fillRect(40 + rn()*688, 30 + rn()*420, 2 + rn()*5, 1 + rn()*3); }
      g.globalAlpha = 0.9; S.base(g); g.globalAlpha = 0.9*st.k; S.gap(g); g.globalAlpha = 1;
      const [wx, wy, ww, wh] = S.worn; if(ww && st.k < 1){ g.globalAlpha = 1 - st.k; for(let n = 0; n < 420; n++){ const x = wx + rn()*ww, y = wy + rn()*wh, dx = (x - wx - ww/2)/(ww/2), dy = (y - wy - wh/2)/(wh/2); if(dx*dx + dy*dy > 1) continue; g.fillStyle = n%3 ? 'rgba(104,90,76,0.95)' : 'rgba(72,62,52,0.9)'; g.fillRect(x, y, 7 + rn()*14, 5 + rn()*9); } g.globalAlpha = 1; } });
    const a = SP[i], dir = new THREE.Vector3(Math.sin(a), 0, -Math.cos(a)), mat2 = new THREE.MeshBasicMaterial({map:tex, transparent:true, depthWrite:false}); mat2.color.setScalar(0.3);
    const m = add(sc, new THREE.PlaneGeometry(MW, MH), mat2, dir.x*R*0.955, 2.35*H, dir.z*R*0.955, false); m.lookAt(0, 2.35*H, 0); murals.push({m, tex, st, dir, lit:0.3, want:0.3, fill:0}); });
  const eye = add(sc, new THREE.PlaneGeometry(1.5*H, 1.5*H), new THREE.MeshBasicMaterial({map:eyeTex('#ffd84a'), transparent:true, depthWrite:false, opacity:0}), murals[4].dir.x*R*0.95, 3.95*H, murals[4].dir.z*R*0.95, false); eye.lookAt(0, 3.95*H, 0);
  const torches = [-90, -54, -18, 18, 54, 90].map(d=>{ const a = d*Math.PI/180, x = Math.sin(a)*R*0.93, z = -Math.cos(a)*R*0.93; add(sc, CYL(0.05*H, 0.07*H, 1.5*H, 6), mat(0x5a3e28), x, 0, z, false); const fl = add(sc, CONE(0.13*H, 0.4*H, 7), glowMat(0xffa53b), x, 1.5*H, z, false); const Lt = new THREE.PointLight(0xff9a3b, 1.7, 10*H); Lt.position.set(x*0.92, 1.9*H, z*0.92); sc.add(Lt); return [Lt, fl]; });
  const orb = add(sc, SPH(0.16*H, 12, 8), glowMat(0x9ff6ff), 0, 2.9*H, 0, false), halo = add(sc, SPH(0.26*H, 12, 8), glowMat(0x9ff6ff, 0.18, true), 0, 2.9*H, 0, false), orbL = new THREE.PointLight(0x9fe8ff, 1.5, 11*H); sc.add(orbL);
  const beam = add(sc, new THREE.CylinderGeometry(0.1*H, 1.5*H, 1, 20, 1, true).translate(0, -0.5, 0).rotateX(-Math.PI/2), glowMat(0x9ff6ff, 0.1, true), 0, 0, 0, false); beam.material.side = THREE.DoubleSide; beam.visible = false;
  const cam = {pos:new THREE.Vector3(0, 2*H, 5*H), tgt:new THREE.Vector3(0, 2*H, -R), p2:new THREE.Vector3(0, 2*H, 5*H), t2:new THREE.Vector3(0, 2*H, -R), snap:true};
  let focus = -1, last = 0; const _o = new THREE.Vector3();
  CAVE_ROOM = {scene:sc, story:true, clickables:[], H, R, murals,
    place(i, cast){ focus = i; const mu = murals[i], d = mu.dir, px = -d.z, pz = d.x, c0 = [d.x*R*0.34, d.z*R*0.34];
      cast.forEach((g, n)=>{ const k = n - (cast.length - 1)/2, x = c0[0] + px*k*0.82*H - d.x*Math.abs(k)*0.22*H, z = c0[1] + pz*k*0.82*H - d.z*Math.abs(k)*0.22*H; g.position.set(x, g.userData.caveLift || 0, z); g.rotation.y = Math.atan2(d.x*R - x, d.z*R - z); });
      _o.set(c0[0] + d.x*1.2*H, 3.3*H, c0[1] + d.z*1.2*H); orb.position.copy(_o); halo.position.copy(_o); orbL.position.copy(_o);
      beam.position.copy(_o); beam.scale.set(1, 1, _o.distanceTo(mu.m.position)); beam.lookAt(mu.m.position); beam.visible = true;
      cam.p2.set(c0[0] - d.x*4.6*H + px*0.5*H, 1.75*H, c0[1] - d.z*4.6*H + pz*0.5*H); cam.t2.set(d.x*R*0.9, 1.05*H, d.z*R*0.9);   /* low and behind: the backs of those who look at the wall are in the picture */ cam.snap = true;
      murals.forEach((m, n)=>{ m.want = n === i ? 1 : (n < i ? 0.55 : 0.3); if(n === i){ m.lit = Math.max(m.lit, 0.4); } }); },
    reveal(i){ murals[i].fill = 1; },
    whole(i){ const m = murals[i]; m.fill = 1; m.st.k = 1; m.tex.userData.redraw(); },
    reset(){ murals.forEach(m=>{ m.fill = 0; m.st.k = 0; m.lit = m.want = 0.3; m.m.material.color.setScalar(0.3); m.tex.userData.redraw(); }); eye.material.opacity = 0; beam.visible = false; focus = -1; },
    state:()=> ({focus, k:murals.map(m=> +m.st.k.toFixed(2)), lit:murals.map(m=> +m.lit.toFixed(2))}),
    update(t){ const dt = Math.min(0.05, last ? t - last : 0.016); last = t;
      torches.forEach(([Lt, f], n)=>{ const k = 1.0 + Math.sin(t*9 + n*3)*0.2 + Math.sin(t*23 + n)*0.1; Lt.intensity = k*1.7; f.scale.setScalar(0.9 + (k - 1)); });
      murals.forEach(m=>{ m.lit += (m.want - m.lit)*(1 - Math.exp(-dt*2.2)); m.m.material.color.setScalar(m.lit); if(m.fill > m.st.k){ m.st.k = Math.min(m.fill, m.st.k + dt/1.5); m.tex.userData.redraw(); } });
      eye.material.opacity += ((focus === 4 ? 0.6 + Math.sin(t*1.4)*0.25 : 0) - eye.material.opacity)*(1 - Math.exp(-dt*2));
      halo.scale.setScalar(1 + Math.sin(t*3)*0.12); beam.material.opacity = 0.08 + Math.sin(t*2.3)*0.02;
      if(cam.snap){ cam.pos.copy(cam.p2); cam.tgt.copy(cam.t2); cam.snap = false; } else { const e = 1 - Math.exp(-dt*2.4); cam.pos.lerp(cam.p2, e); cam.tgt.lerp(cam.t2, e); }
      cam.pos.x += Math.sin(t*0.5)*0.004*H; camera.position.copy(cam.pos); controls.target.copy(cam.tgt); camera.lookAt(cam.tgt); } };
  return CAVE_ROOM; }
function caveEnter(){ const room = muralRoom(); room.reset(); const cast = [ZERO, RICO, CODEX, XYLO, NATY];
  caveKeep = {near:camera.near, fov:camera.fov, min:controls.minDistance, max:controls.maxDistance, en:controls.enabled, pos:camera.position.clone(), tgt:controls.target.clone(),
    cast:cast.map(g=> ({g, parent:g.parent, p:g.position.clone(), r:g.rotation.y, v:g.visible}))};
  NATY.userData.caveLift = room.H*1.5; cast.forEach(g=>{ room.scene.add(g); g.visible = true; });
  camera.near = 0.1; camera.fov = 52; camera.updateProjectionMatrix(); controls.minDistance = 0.1; controls.maxDistance = 2000; controls.enabled = false;
  inside = room; document.body.classList.add('cavestory'); return room; }
function caveLeave(){ if(!caveKeep) return; const k = caveKeep; caveKeep = null; caveTok++;
  k.cast.forEach(c=>{ if(c.parent) c.parent.add(c.g); c.g.position.copy(c.p); c.g.rotation.y = c.r; c.g.visible = c.v; });
  if(inside && inside.story) inside = null; camera.near = k.near; camera.fov = k.fov; camera.updateProjectionMatrix(); controls.minDistance = k.min; controls.maxDistance = k.max; controls.enabled = k.en; camera.position.copy(k.pos); controls.target.copy(k.tgt);
  document.body.classList.remove('cavestory'); if(walk) walk.snap = true; }
async function caveStory(q){ const tok = ++caveTok, dead = ()=> tok !== caveTok || !mini || mini.kind !== 'cave';
  miniBox.hidden = true; $('questHud').hidden = true; qNavHide(); miniSave('cave');
  const cut = f=> new Promise(r=> fadeThrough('#05070c', ()=>{ if(tok === caveTok) f(); setTimeout(r, 420); })), talk = lines=> new Promise(r=> say(lines, r));   /* not the dark dialogue style: its scrim hid the murals */
  let room = null; const row = [RICO, ZERO, CODEX, XYLO, NATY];
  await cut(()=>{ room = caveEnter(); room.place(0, row); room.murals.forEach(m=>{ m.want = 0.3; }); sfx('dark'); }); if(dead()) return;
  caveTok = tok;   /* caveEnter does not change the token; kept explicit */
  await wait(reduce ? 200 : 900); if(dead()) return; await talk(STORY.caveIn); if(dead()) return;
  const steps = [[0, null, STORY.mural1], [1, null, STORY.mural2], [2, STORY.mural3a, STORY.mural3], [3, STORY.mural4a, STORY.mural4]];
  for(const [i, before, after] of steps){
    if(i > 0){ await cut(()=> room.place(i, row)); if(dead()) return; } else room.place(0, row);
    await wait(reduce ? 200 : 1300); if(dead()) return;
    if(before){ await talk(before); if(dead()) return; }
    room.reveal(i); sfx('sparkle'); await wait(reduce ? 200 : 1700); if(dead()) return;
    await talk(after); if(dead()) return; }
  await cut(()=> room.place(4, row)); if(dead()) return; await wait(reduce ? 200 : 1300); if(dead()) return;
  await talk(STORY.caveEnd); if(dead()) return;
  await cut(()=> caveLeave()); if(!mini || mini.kind !== 'cave') return;
  questComplete(q); }
window.__cave = ()=> ({on:!!caveKeep, room:CAVE_ROOM ? CAVE_ROOM.state() : null, inside:!!(inside && inside.story)});
function caveOpen(){'''
rep('function caveOpen(){', ROOM)
rep("  if(q.mini === 'cave'){ mini = {q, kind:'cave'}; miniSave('cave'); caveOpen(); }\n}", "  if(q.mini === 'cave'){ mini = {q, kind:'cave'}; caveStory(q); }\n}")
rep("else if(q.mini === 'cave'){ mini = {q, kind:'cave', decoded:!!cp.decoded,trialRows:cp.trialRows||[]}; caveOpen(); }", "else if(q.mini === 'cave'){ mini = {q, kind:'cave'}; caveStory(q); return true; }")
rep("function miniClear(){", "function miniClear(){ if(caveKeep) caveLeave();")
rep("function exitInterior(){\n  if(!inside) return;", "function exitInterior(){\n  if(!inside || inside.story) return;")
rep("return m?.decoded||cp?.decoded?'선대의 글에 나온 순서와 연구실에서 확인한 양으로 가상 시험을 해 보자. 실패한 결과는 시험 기록에서 다시 볼 수 있어.':'누락된 내용을 모두 채웠어. 환원하기 전에 코덱스를 만나러 동굴로 가자.';",
    "return '누락된 내용을 모두 채웠어. 환원하기 전에 코덱스를 만나러 동굴로 가자.';")

# ---------- the cave outside: depth, pillars with torches, vines, standing stones ----------
rep("place(cave, -31, -391, 0.35);",
    "{ /* 2026-11-12 (user: the cave looked poor): a mouth with depth, carved pillars with torches, vines, standing stones along the approach */\n"
    "  add(cave, new THREE.TorusGeometry(11.4, 3.2, 7, 16, Math.PI), flat(0x6a6156), 0, 0, -3.2); add(cave, new THREE.TorusGeometry(9, 2.6, 6, 14, Math.PI), flat(0x4b443c), 0, 0, -6.4);\n"
    "  add(cave, new THREE.CircleGeometry(4.2, 18), glowMat(0xffb35a, 0.16), 0, 4.6, -5.6, false);\n"
    "  [[-23, 2.5, 7, 0.3], [-27, 6, 6, 1.4], [-21, 9, 5, 2.2], [23, 2.5, 7, 0.9], [27, 5.5, 6, 2.6], [20.5, 9.5, 5, 0.5], [-9, 20, 5, 1.1], [8, 21, 5.5, 2.0], [0, 23, 4, 0.2]].forEach(([x, y, r, a])=> add(cave, ICO(r, 0), flat(C.rock), x, y, -4 - r*0.3).rotation.set(a, a*1.7, 0));\n"
    "  [-1, 1].forEach(sx=>{ add(cave, BOX(3.4, 14, 3.4), flat(0x8d8577), sx*18.5, 0, 7); add(cave, BOX(4.6, 1.3, 4.6), flat(0x6f675b), sx*18.5, 14, 7); add(cave, BOX(4.2, 1.1, 4.2), flat(0x6f675b), sx*18.5, 0, 7);\n"
    "    add(cave, new THREE.PlaneGeometry(2.6, 2.6), new THREE.MeshBasicMaterial({map:eyeTex('#ffd84a'), transparent:true, depthWrite:false}), sx*18.5, 9.5, 8.76, false);\n"
    "    add(cave, CYL(0.5, 0.8, 1.4, 8), flat(0x4b443c), sx*18.5, 15.3, 7); add(cave, CONE(0.9, 2.6, 7), glowMat(0xffa53b), sx*18.5, 16.5, 7, false); add(cave, SPH(1.5, 10, 8), glowMat(0xffc46b, 0.22, true), sx*18.5, 17.4, 7, false); });\n"
    "  for(let i = 0; i < 9; i++){ const a = Math.PI*(0.14 + i*0.09), h = 3.5 + ((i*37) % 5)*1.1; add(cave, BOX(0.35, h, 0.35), mat(0x4f9a52), Math.cos(a)*15.5, Math.sin(a)*15.5 - h, 3.9, false); if(i % 2) add(cave, SPH(0.55, 6, 5), mat(0x6cbf63), Math.cos(a)*15.5, Math.sin(a)*15.5 - h, 3.9, false); }\n"
    "  [[-13, 16, 1], [13.5, 18, 0.8], [-14, 28, 0.9], [14.5, 30, 1.1]].forEach(([x, z, k], i)=>{ const st = add(cave, ICO(2.4*k, 0), flat(0x7d766a), x, 3.2*k, z); st.scale.set(0.8, 1.9, 0.7); st.rotation.y = i*1.3; add(cave, SPH(0.42, 8, 6), glowMat(0xffd84a), x + (x < 0 ? 1.6 : -1.6)*k, 3.6*k, z + 0.3, false); }); }\n"
    "place(cave, -31, -391, 0.35);")
rep("for(let i=0;i<4;i++) add(cave, ICO(4+i,0), flat(C.rock), -20+i*13, 1, 4+(i%2)*3);", "[[-25, 4, 5], [-15.5, 5, 9], [15, 5.5, 9], [25, 6, 5]].forEach(([x, r, z])=> add(cave, ICO(r, 0), flat(C.rock), x, 1, z));   /* 2026-11-12: the two middle boulders stood in the mouth */")
assert '\r\n' not in s
P.write_bytes(s.encode('utf-8')); print('ok')
