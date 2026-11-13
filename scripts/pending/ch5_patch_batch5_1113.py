# 2026-11-13 사용자 지시
#  ① 미로 도착 지점을 딱 봐도 알게: 한가운데 위에 아래를 가리키는 큰 붉은 화살표(울타리 위로 보임) + 바닥의 붉은 고리 + 빛기둥(하얗게 타지 않게),
#     네이티는 눈높이로 내려 도착하면 바로 보이게. 미로 안에서는 「바로 앞」 대신 남은 거리를 5m 안까지 숫자로.
#  ② 복구된 구역 이름표(초록 알약): 이름·건수 없이 작은 「✓ 복구 완료」만, 걷는 화면에서는 숨김
#  ③ 「채운 기록」 → 「확보한 기록」
import pathlib, re
R = pathlib.Path(__file__).resolve().parents[2]; P = R / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
# ---- ① ----
rep("[NATY_HIDE[0], NATY_HIDE[1], G + 8] : null;", "[NATY_HIDE[0], NATY_HIDE[1], G + 2.6] : null;")
a = s.index("if(!NATY.userData.beam){"); b = s.index("/* a red column over the heart of the maze", a); b = s.index("*/", b) + 2
new = ("if(!NATY.userData.beam){ const gm = new THREE.Group(); gm.userData.dynamic = true; const mk = (c, o, add)=> new THREE.MeshBasicMaterial({color:c, transparent:true, opacity:o, depthWrite:false, side:THREE.DoubleSide, blending:add ? THREE.AdditiveBlending : THREE.NormalBlending});\n"
       "      const col = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 60, 16, 1, true), mk(0xff4a3a, 0.34)); col.position.y = 30; gm.add(col);\n"
       "      const arrow = new THREE.Mesh(new THREE.ConeGeometry(3.2, 5.5, 4).rotateX(Math.PI), mk(0xff4a3a, 0.95)); arrow.name = 'goal-arrow'; gm.add(arrow);\n"
       "      const ring = new THREE.Mesh(new THREE.RingGeometry(1.7, 2.5, 40).rotateX(-Math.PI/2), mk(0xff4a3a, 0.95)); ring.position.y = 0.5; ring.name = 'goal-ring'; gm.add(ring);\n"
       "      const disc = new THREE.Mesh(new THREE.CircleGeometry(1.7, 32).rotateX(-Math.PI/2), mk(0xff8a6a, 0.35)); disc.position.y = 0.48; gm.add(disc);\n"
       "      gm.traverse(o=>{ o.userData.dynamic = true; o.userData.noShadow = true; o.renderOrder = 6; }); islRoot.add(gm); NATY.userData.beam = gm; }\n"
       "    const bm = NATY.userData.beam; bm.visible = NATY.visible !== false; bm.position.set(pk[0], G, pk[1]); { const ar = bm.getObjectByName('goal-arrow'), rg = bm.getObjectByName('goal-ring'); ar.position.y = 11.5 + Math.sin(t*2.4)*0.9; ar.rotation.y = t*1.2; const k = 1 + 0.12*Math.sin(t*3); rg.scale.set(k, 1, k); } }   /* the goal of the maze, plain to see (user, 2026-11-13): a big red arrow above the hedges pointing down, a red ring on the floor of the heart, and Naty at eye level */")
s = s[:a] + new + s[b:]
rep("txt = d < 14 ? '바로 앞' : `${m} m`;", "txt = d < (questLive && questLive.mini === 'maze' && questLive.mazeEntered ? 5 : 14) ? '바로 앞' : `${m} m`;")
rep("$('qhDist').textContent = d < 14 ? '바로 앞' : `${m} m`;", "$('qhDist').textContent = d < (q.mini === 'maze' && q.mazeEntered ? 5 : 14) ? '바로 앞' : `${m} m`;")
k = s.count("'붉은 빛기둥이 선 한가운데까지 가기'"); assert k >= 1; s = s.replace("'붉은 빛기둥이 선 한가운데까지 가기'", "'붉은 화살표가 가리키는 곳까지 가기'")
# ---- ② ----
rep("`${m.scans[0] ? `<img src=\"${esc(m.scans[0].thumb)}\" alt=\"\">` : ''}${esc(m.name)} <em>${isl ? '✓ 복구 완료' : '✓ 복구 완료'} ${m.scans.length || ''}</em>`", "`<em>✓ 복구 완료</em>`")
# ---- ③ ----
n3 = s.count('채운 기록'); s = s.replace('채운 기록', '확보한 기록')
CSS = ".mk.ok{padding:3px;box-shadow:none}.mk.ok em{margin:0}body.walk .mk.ok{display:none!important}\n"
mk = '</style></head><body>'; assert s.count(mk) == 1 and s.count('body.walk .mk.ok') == 0; i = s.index(mk); s = s[:i] + CSS + s[i:]
P.write_bytes(s.encode('utf-8')); print('ok crlf', s.count('\r\n'), 'hint', k, '기록 문구', n3)
sc = R / 'docs/chapter05_script.md'; t = sc.read_bytes().decode('utf-8'); print('script', t.count('채운 기록')); sc.write_bytes(t.replace('채운 기록', '확보한 기록').encode('utf-8'))
