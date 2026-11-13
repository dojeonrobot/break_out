# 2026-11-13 (사용자)
#  관리자: 「도구 그냥 상단에 다 넣어놔줘, 숨긴 스캔 살리는 기능이 왜 필요하지? 제출목록 복사하는 것도 기능 없애」
#     → 「전체 초기화」를 머리줄(관리자 종료 옆)로, 접이식 「도구」 칸 삭제, 「숨긴 스캔 되살리기」·「제출 목록 복사」 버튼 삭제(새 CSS 없음, 있던 클래스 그대로)
#  미로: 「도착지점이 애매해 … 네이티가 보인다던지 해야 그걸 보고 따라가는데」
#     → 네이티를 울타리 위로 더 높이(5.4 → 8), 한가운데에 붉은 빛기둥(미션 2에서 네이티가 미로에 있는 동안만), 안내 문구에 빛기둥을 적음
#  python scripts/pending/ch5_patch_admin_maze_1113.py   (한 번만)
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
def rex(pat, new, n=1):
    global s
    s, k = re.subn(pat, lambda m: new, s, flags=re.S); assert k == n, (k, pat[:90])
# ---- admin ----
rep('<button type="button" class="mini" data-aact="logout">관리자 종료</button>', '<button type="button" class="mini danger" data-aact="reset">전체 초기화</button><button type="button" class="mini" data-aact="logout">관리자 종료</button>')
rex(r"\s*\$\{det\('tools', '도구',.*?data-aact=\"reset\">전체 초기화</button></div>`\)\}", "")
rex(r"<button type=\"button\" class=\"mini\" data-aact=\"copy\">표로 복사</button>", "")
rep(' 숨긴 스캔은 "숨긴 스캔 되살리기"로 되돌릴 수 있습니다. 계속할까요?', ' 되돌릴 수 없습니다. 계속할까요?')
# ---- maze heart ----
rep("[NATY_HIDE[0], NATY_HIDE[1], G + 5.4] : null;", "[NATY_HIDE[0], NATY_HIDE[1], G + 8] : null;")
rep("if(NATY.userData.park){ const pk = NATY.userData.park; NATY.position.set(pk[0], pk[2] + Math.sin(t*1.4)*0.5, pk[1]); NATY.rotation.y = MAZE.rot; }",
    "if(NATY.userData.park){ const pk = NATY.userData.park; NATY.position.set(pk[0], pk[2] + Math.sin(t*1.4)*0.5, pk[1]); NATY.rotation.y = MAZE.rot;"
    " if(!NATY.userData.beam){ const bm = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.5, 110, 16, 1, true), new THREE.MeshBasicMaterial({color:0xff6a5a, transparent:true, opacity:0.3, depthWrite:false, side:THREE.DoubleSide, blending:THREE.AdditiveBlending})); bm.userData.dynamic = true; bm.userData.noShadow = true; islRoot.add(bm); NATY.userData.beam = bm; }"
    " const bm = NATY.userData.beam; bm.visible = NATY.visible !== false; bm.position.set(pk[0], G + 55, pk[1]); bm.material.opacity = 0.26 + 0.1*Math.sin(t*3); }   /* a red column over the heart of the maze: the children see where Naty is from any corridor (user, 2026-11-13) */")
rep("else if(!STAGED){ NATY.position.set(60*K + Math.cos(an)*30, G + 12 + Math.sin(t*1.4)*1.5, -100*K + Math.sin(an)*30); NATY.rotation.y = -an; }",
    "else if(!STAGED){ if(NATY.userData.beam) NATY.userData.beam.visible = false; NATY.position.set(60*K + Math.cos(an)*30, G + 12 + Math.sin(t*1.4)*1.5, -100*K + Math.sin(an)*30); NATY.rotation.y = -an; }")
n = s.count("'미로 한가운데까지 가기'"); assert n >= 1, n
s = s.replace("'미로 한가운데까지 가기'", "'붉은 빛기둥이 선 한가운데까지 가기'")
P.write_bytes(s.encode('utf-8')); print('ok crlf', s.count('\r\n'), 'hint', n, 'copy refs', s.count('data-aact="copy"'), 'unhide refs', s.count('data-aact="unhide"'))
