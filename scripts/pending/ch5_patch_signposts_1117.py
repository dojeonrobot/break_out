# 2026-11-17 사용자: 표지판이 가리키는 곳이 전부 틀리고, 먼 항구까지 적혀 있다. 한 번만 적용.
#  손으로 적은 글자 대신, 표지판마다 가까운 명소 셋을 골라 그 방향을 실제로 가리키는 화살 모양 판으로 만든다(앞뒤 양면 글씨, 항구는 넣지 않음).
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
i = s.index("const SIGN = [['← 사파리'"); j = s.index("cart(0xf6b6c9", i)
new = ("/* signposts point where they say (user, 2026-11-17): each post takes the three nearest of these places and turns an arrow board towards each; built once every place exists */\n"
"  window.__signPosts = ()=>{ const DEST = ['사파리', '롤러코스터', '관람차', '회전목마', '하모니아', '바이킹', '미러 레이크', '도로랜드 정문', '팬텀 하우스', '그랜드 스테이지'].map(l=> IB.find(b=> b && b.label === l)).filter(Boolean);\n"
"    [[-70, 120], [40, 200], [110, 0], [-120, 180]].forEach(([x, z])=>{\n"
"      const g = new THREE.Group(); g.position.set(x, G, z); g.scale.setScalar(0.35); islRoot.add(g);\n"
"      add(g, CYL(0.35, 0.4, 12, 6), mat(0x8a6243));\n"
"      DEST.map(b=> [b, Math.hypot(b.cx - x, b.cz - z)]).filter(e=> e[1] > 45).sort((a, b)=> a[1] - b[1]).slice(0, 3).forEach(([b], k)=>{\n"
"        const arm = new THREE.Group(); arm.position.y = 10 - k*2.4; arm.rotation.y = Math.atan2(-(b.cz - z), b.cx - x); g.add(arm);   /* +x of the arm looks at the place */\n"
"        add(arm, BOX(8, 1.9, 0.36), mat(0x9a6b45), 4.6, -0.95, 0); const tip = add(arm, new THREE.CylinderGeometry(0, 1.35, 1.9, 3).rotateZ(-Math.PI/2), mat(0x9a6b45), 9.5, 0, 0, false); tip.scale.z = 0.14;\n"
"        const name = b.label === '도로랜드 정문' ? '정문' : b.label, tm = ()=> new THREE.MeshBasicMaterial({map:signTex(name, {bg:'#9a6b45', fg:'#fff7d6', size:58, w:384, h:72})});\n"
"        add(arm, new THREE.PlaneGeometry(7.4, 1.5), tm(), 4.6, 0, 0.2, false); const back = add(arm, new THREE.PlaneGeometry(7.4, 1.5), tm(), 4.6, 0, -0.2, false); back.rotation.y = Math.PI; }); }); };\n  ")
s = s[:i] + new + s[j:]
old = "if(!/[?&]nobatch/.test(location.search)) batchIsland();"; assert s.count(old) == 1
s = s.replace(old, "try{ window.__signPosts(); }catch(e){ console.warn('signposts', e); }\n" + old)
assert '\r\n' not in s; P.write_bytes(s.encode('utf-8')); print('patched', len(s))
