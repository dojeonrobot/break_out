# 2026-11-13 사용자 캡처·지시
#  ① SKY LOOP 역 간판: 한 장을 양면으로 써서 뒤에서는 글씨가 뒤집혀 보였고 기둥이 글자를 가렸다 → 앞뒤에 한 장씩, 기둥은 두 장 사이에
#  ② 스카이 루프(모노레일)가 관람차 언덕 가장자리를 뚫고 지나감 → 언덕 바깥으로 돌아가게(롤러코스터를 비켜 가는 것과 같은 방식)
#  ③ PC에서 Space가 안 먹던 곳: 잔재 해체 「지금!」, 스카이 루프의 꾹 누르기(탐지·좌표 확인)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90]); s = s.replace(old, new)
rep("add(g, new THREE.PlaneGeometry(9, 1.8), new THREE.MeshBasicMaterial({map:signTex('SKY LOOP', {bg:'#1d2f55', fg:'#ffd400', size:84, w:512, h:110}), side:THREE.DoubleSide}), px + inx*17, G + 8, pz + inz*17, false).rotation.y = Math.atan2(inx, inz) + Math.PI;",
    "{ const sm = new THREE.MeshBasicMaterial({map:signTex('SKY LOOP', {bg:'#1d2f55', fg:'#ffd400', size:84, w:512, h:110})}); [0, Math.PI].forEach(tw=>{ const th = Math.atan2(inx, inz) + Math.PI + tw; add(g, new THREE.PlaneGeometry(9, 1.8), sm, px + inx*17 + Math.sin(th)*0.46, G + 8, pz + inz*17 + Math.cos(th)*0.46, false).rotation.y = th; }); add(g, BOX(9, 1.8, 0.86), mat(0x1d2f55), px + inx*17, G + 7.1, pz + inz*17).rotation.y = Math.atan2(inx, inz); }   /* one face each way, the post between them (user, 2026-11-13: the back read mirrored) */")
rep("  return r; };\nconst coveAt = ",
    "  /* north-east: round the outside of the Ferris wheel's hill, which it used to cut through (user, 2026-11-13) */\n"
    "  { const fx = 160*1.35, fz = -180*1.35, FC = 90, fu = fx*Math.cos(a) + fz*sn, fd = FC*FC - (fx*fx + fz*fz) + fu*fu; if(fd > 0){ const s0 = Math.sqrt(fd), far = fu + s0; if(r > fu - s0 && r < far) r = Math.min(far, islR(a) - 20); } }\n"
    "  return r; };\nconst coveAt = ")
rep("function remGame(i){",
    "/* Space on the PC (user, 2026-11-13: it did nothing here): the timing button of the remnant game, and the hold button on the Sky Loop */\n"
    "document.addEventListener('keydown', e=>{ if(e.code !== 'Space' || vn || $('voidVn').dataset.on) return; const rd = $('remDlg');\n"
    "  if(rd && rd.dataset.on){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) remTap(); return; }\n"
    "  const hunt = mini && mini.kind === 'device' && mini.phase === 'hunt'; if((ride || hunt) && !miniBox.hidden){ e.preventDefault(); e.stopImmediatePropagation(); if(ride) ride.press = true; else mini.press = true; } }, true);\n"
    "document.addEventListener('keyup', e=>{ if(e.code !== 'Space') return; if(ride) ride.press = false; if(mini) mini.press = false; }, true);\n"
    "function remGame(i){")
assert 'K = 1.35' in s or 'K=1.35' in s, 'K'
P.write_bytes(s.encode('utf-8')); print('ok', s.count('\r\n'))
