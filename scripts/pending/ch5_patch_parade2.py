# 2026-11-19: 퍼레이드 수레를 사람 크기에 맞게 키우고(0.42 → 0.6, 차선 반지름 3.3 → 5, 수레 간격 13 → 17), 조형을 가리던 깃발 줄을 뺀다. 보이드는 밝은 흰색 재질.
# 한 번만 적용: python scripts/pending/ch5_patch_parade2.py
import pathlib
p = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
R = [("    [-4.4, 4.4].forEach(x=>{ for(let i = 0; i < 9; i++){ const u = (i + 0.5)/9, f = add(g, CONE(0.55, 1.1, 4), mat(PAL[i % 6]), x, 9.6 - Math.sin(u*Math.PI)*1.5, -8.6 + u*17.2, false); f.rotation.x = Math.PI; } });\n", ""),
     ("    [[-4.4, -8.6], [4.4, -8.6], [-4.4, 8.6], [4.4, 8.6]].forEach(([x, z])=>{ add(g, CYL(0.14, 0.14, 7.2, 6), mat(0xffffff), x, 3.1, z, false); add(g, SPH(0.4, 8, 6), mat(C.gold), x, 10.5, z, false); });\n", ""),
     ("f1.add(vb); const WH = 0xf6f8fb, BL = 0x2f9fe6;", "f1.add(vb); const WHM = new THREE.MeshLambertMaterial({color:0xffffff, emissive:0x6f747c}), BL = 0x2f9fe6;"),
     ("[f1, f2, f3, f4].forEach(f=>{ f.scale.setScalar(0.42); parade.add(f); floats.push(f); });", "[f1, f2, f3, f4].forEach(f=>{ f.scale.setScalar(0.6); parade.add(f); floats.push(f); });"),
     ("    const radius=3.3,north=205,south=340,", "    const radius=5,north=205,south=340,"),
     ("    floats.forEach((f,k)=>pose(f,lead-18-k*13));", "    floats.forEach((f,k)=>pose(f,lead-22-k*17));")]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
n = s.count("mat(WH)"); assert n >= 4, n; s = s.replace("mat(WH)", "WHM")
p.write_bytes(s.encode('utf-8')); print('ok', n)
