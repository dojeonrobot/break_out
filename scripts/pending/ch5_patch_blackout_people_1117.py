# 2026-11-17 사용자: 전력이 끊긴 동안에는 섬에 사람(방문객·대기줄)도 없어야 하고, 전력이 복구된 뒤부터 생긴다. 한 번만 적용.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
old = "try{parkDark(!PARK_ON);}catch(e){}}"
assert s.count(old) == 1
new = old + "{const pv=PARK_ON&&(!PARK_WAKE||PARK_WAKE.k>1.4);if(!parkDark.ppl){parkDark.ppl=[];islRoot.traverse(o=>{if(/^(park|queue)-visitors$/.test(o.name))parkDark.ppl.push(o);});}parkDark.ppl.forEach(o=>{if(!pv){if(o.visible){o.visible=false;o.userData.po=1;}}else if(o.userData.po){o.visible=true;o.userData.po=0;}});}   /* no power, no visitors: they come back as the rides start (user, 2026-11-17) */"
s = s.replace(old, new); P.write_bytes(s.encode('utf-8')); print('patched')
