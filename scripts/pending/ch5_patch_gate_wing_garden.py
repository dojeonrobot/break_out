# 2026-11-12 (사용자 「미로 가는 길이 벽으로 나 있다 · 벽에 놀이기구가 있다 · 벽이랑 꽃밭이 겹친다 · 꽃밭이 길을 막는다」)
#   원인: 정문의 동쪽 날개 벽(아치 5칸 + 모서리 탑)이 z=390을 따라 x≈165까지 뻗어, 울타리가 남동쪽으로 꺾이는 x=60 너머의 공원 안쪽을 가로질렀다.
#         미로 길이 그 벽을 지나갔고, 플라잉 카펫과 꽃밭 남쪽 끝이 벽에 걸렸다. 꽃밭(x 14~70, z 346~392)은 z=360을 지나는 두 길(미로 쪽·롤러코스터 쪽)도 덮고 있었다.
#   고침: 동쪽 날개는 아치 1칸 + 탑(울타리가 꺾이는 자리)까지만. 꽃밭은 x 14~62·z 346~385로 줄이고 z=360에 길 통로를 낸다. 미로 길은 탑 동쪽으로 돌아간다.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70]); s = s.replace(old, new)
rep("      for(let i=0;i<5;i++){ const x = s*(44 + i*16);\n        add(Gt, BOX(14, 16, 6), mat(beige), x, 0, 0);", "      for(let i=0;i<(s > 0 ? 1 : 5);i++){ const x = s*(44 + i*16);   /* 2026-11-12: the east wing ran across the park inside the fence; it now ends where the fence turns */\n        add(Gt, BOX(14, 16, 6), mat(beige), x, 0, 0);")
rep("      const tx = s*128;\n", "      const tx = s > 0 ? 66 : -128;\n")
rep("      for(let i=0;i<4;i++){ const x = s*(52 + i*16); add(Gt, BOX(8, 3, 4), mat(0x9a6b45), x, 0, 8);", "      for(let i=0;i<(s > 0 ? 0 : 4);i++){ const x = s*(52 + i*16); add(Gt, BOX(8, 3, 4), mat(0x9a6b45), x, 0, 8);")
rep("add(Gt, BOX(44, 5.6, 1.2), mat(0x3b4c78), 76, 17.6, 3.2);", "add(Gt, BOX(44, 5.6, 1.2), mat(0x3b4c78), -76, 17.6, 3.2);")
rep("{bg:'#1d2f55', fg:'#ffd400', size:60, w:1024, h:128})}), 76, 20.4, 3.9, false);", "{bg:'#1d2f55', fg:'#ffd400', size:60, w:1024, h:128})}), -76, 20.4, 3.9, false);")
# the garden: smaller, clear of the wall, with a lane for the two paths along z = 360
rep("    for(let x=16; x<=68; x+=2.1) for(let z=348; z<=390; z+=2.1){", "    for(let x=16; x<=60; x+=2.1) for(let z=348; z<=383; z+=2.1){ if(Math.abs(z - 360) < 5.6) continue;   /* the lane: the maze path and the coaster path run along z = 360 */")
rep("      if(Math.hypot(Math.abs(x)-42, z-369) < 6) continue;", "      if(Math.hypot(Math.abs(x)-38, z-375) < 6) continue;")
rep("    add(garden, BOX(56, 1.6, 1.4), mat(0x4f8a3c), side*42, 0, 346);\n    add(garden, BOX(56, 1.6, 1.4), mat(0x4f8a3c), side*42, 0, 392);\n    add(garden, BOX(1.4, 1.6, 46), mat(0x4f8a3c), side*70, 0, 369);\n    add(garden, BOX(1.4, 1.6, 46), mat(0x4f8a3c), side*14, 0, 369);\n    const tp = new THREE.Group(); tp.position.set(side*42, 0, 369); garden.add(tp);",
    "    [346, 354.4, 365.6, 385].forEach(z=> add(garden, BOX(48, 1.6, 1.4), mat(0x4f8a3c), side*38, 0, z));\n    [14, 62].forEach(x=>{ add(garden, BOX(1.4, 1.6, 8.4), mat(0x4f8a3c), side*x, 0, 350.2); add(garden, BOX(1.4, 1.6, 19.4), mat(0x4f8a3c), side*x, 0, 375.3); });\n    const tp = new THREE.Group(); tp.position.set(side*38, 0, 375); garden.add(tp);")
rep("PATHS[17]=[[0,360],[48,360],[85,380],[115,407],[140,421]];", "PATHS[17]=[[0,360],[68,360],[96,376],[116,407],[140,421]];   /* through the garden lane, then east of the gate's corner tower */")
rep("PATHS[24]=[[85,380],[97,385],[106,386]];", "PATHS[24]=[[96,376],[101,374]];")
P.write_bytes(s.encode('utf-8')); print('ok')
