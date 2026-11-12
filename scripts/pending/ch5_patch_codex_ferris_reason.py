# 2026-11-12 (사용자)
#  1) 동굴 앞 코덱스가 바위에 겹쳐 서 있음 → 입구 앞 빈 자리로 옮기고, 찾아가는 목표도 그 자리로.
#  2) 관람차 앞 장면(2막·3막): 기둥에 가리고 관람차가 안 보임 → 카메라를 뒤로 빼고 낮춰 올려다보게.
#  3) 잔재를 없애는 이유 = 정확한 시뮬레이션으로 일루아를 정확하게 환원하기 위해(대사, 대본도 같이).
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]
p = R / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70]); s = s.replace(old, new)
rep("else { CODEX.position.set(CAVE_MOUTH[0] + 4, G, CAVE_MOUTH[1] + 8); CODEX.rotation.y = Math.atan2(-CAVE_MOUTH[0], -CAVE_MOUTH[1]); }",
    "else { const cw = codexWait(); CODEX.position.set(cw[0], G, cw[1]); CODEX.rotation.y = Math.atan2(-cw[0], -cw[1]); }")
rep("function questTarget(q){", "function codexWait(){ return codexWait.p || (codexWait.p = freeSpot(CAVE_MOUTH[0] + 7, CAVE_MOUTH[1] + 19)); }   /* clear of the boulders at the mouth (user, 2026-11-12) */\nfunction questTarget(q){")
rep("q.id==='q5' ? (buildLabDoor(), LAB_DOOR) : CAVE_MOUTH; }", "q.id==='q5' ? (buildLabDoor(), LAB_DOOR) : codexWait(); }")
rep("  flyTo(new THREE.Vector3(cx2, G + 5.5, cz2), new THREE.Vector3(fx, G + 2.6, fz), ms);",
    "  if(zoneId === 'dl-ferris'){ let bx = fx + ux*85, bz = fz + uz*85; flyTo(new THREE.Vector3(bx, G + 8, bz), new THREE.Vector3(fx - ux*20, G + 30, fz - uz*20), ms); return {fx, fz, ux, uz}; }   /* the wheel stands on a hill: step back and look up so it is in the picture (user, 2026-11-12) */\n"
    "  flyTo(new THREE.Vector3(cx2, G + 5.5, cz2), new THREE.Vector3(fx, G + 2.6, fz), ms);")
A = '시간이 많지 않아요. 잔재를 찾아서 꺼 주세요. 그래야 남은 기록으로 제대로 된 시뮬레이션을 할 수 있습니다.'
B = '잔재를 찾아서 꺼 주세요. 시뮬레이션이 정확해야 일루아를 정확하게 환원할 수 있습니다.'
rep(A, B); p.write_bytes(s.encode('utf-8'))
p = R / 'docs/chapter05_script.md'; t = p.read_bytes().decode('utf-8'); assert t.count(A) == 1; t = t.replace(A, B)
a = '- 선대의 잔재는 일루아를 망가뜨리는 장치가 아니다. 일루아의 흐름을 복구하고 파악하는 것을 방해하기 때문에 없앤다.'; assert t.count(a) == 1
t = t.replace(a, '- 선대의 잔재는 일루아를 망가뜨리는 장치가 아니다. 정확한 시뮬레이션으로 일루아를 정확하게 환원하기 위해 없앤다(2026-11-12 사용자).')
p.write_bytes(t.encode('utf-8')); print('ok')
