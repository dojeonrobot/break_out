# 2026-11-17 사용자: 스플래시 리버 통나무 배가 물길을 따라 움직이지 않는다 / 호수 데크의 뜬금없는 막대들.
#  원인: 배가 「움직이는 물체」 표시가 없어, 정전 상태로 시작한 조 태블릿에서는 섬을 합칠 때 굳어 버렸다. 방향도 놀이기구 안 좌표를 세계 좌표로 보고 잡아 틀어져 있었다.
#  (호수 데크의 낚싯대·홀로 선 등은 같은 날 앞서 지움.) 한 번만 적용.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60]); s = s.replace(old, new)
rep("    F.add(b); return b; });\n  const N = 140, SP", "    b.userData.dynamic = true; b.rotation.order = 'YXZ'; F.add(b); return b; });   /* moves once the power is back: never baked (2026-11-17) */\n  const N = 140, SP")
rep("b.position.copy(p).add(new THREE.Vector3(0, 1.0, 0)); b.lookAt(q.x, q.y + 1.0, q.z); b.rotateY(Math.PI);", "b.position.set(p.x, p.y + 1.0, p.z); { const dx = q.x - p.x, dy = q.y - p.y, dz = q.z - p.z; b.rotation.set(Math.atan2(dy, Math.hypot(dx, dz) || 1e-6), Math.atan2(dx, dz) + Math.PI, 0); }   /* along the channel, in the ride's own space */")
P.write_bytes(s.encode('utf-8')); print('patched')
