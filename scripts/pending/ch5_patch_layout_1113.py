# 2026-11-13 섬 길·대기줄·벤치 정리 (사용자 캡처 12장 + 지시: 등대 길 삭제, 집을 뚫는 길, 운전면허장 침범, 대기줄 전부 이상, 벤치가 풀밭에 있음)
#  길: 등대 구간 삭제 / 스플래시 리버 부지를 비켜 감 / 직원 숙소는 마을 가장자리에서 끝 / 스위트 스쿱은 관람차 언덕과 갤럭시 스윙 사이로 따로 /
#      운전면허장은 차도로 들어가던 보행로 둘을 지우고 시험장 건물 앞마당으로 / 사파리 안쪽 숨은 곁길(풍차) 삭제, 사파리 정문 아치로 / 막다른 꼬리 둘 정리 / 서쪽 길 시작 틈 / 호수 연결로
#  대기줄·이름 아치: 실제로 길이 울타리를 지나는 자리와 방향을 찾아(gateOf) 아치를 길 위에 직각으로 세우고, 대기줄은 그 바깥 길 바로 옆에 나란히
#  벤치: 길 중심에서 11 고정 → 길 폭 + 1.5, 끼워 넣는 긴 벤치는 길 폭 + 6 → + 1.9(겹치는 울타리 조각은 지움)
#  python scripts/pending/ch5_patch_layout_1113.py   (한 번만)
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:90]); s = s.replace(old, new)
def rex(pat, new, n=1):
    global s
    s, k = re.subn(pat, lambda m: new, s, flags=re.S); assert k == n, (k, pat[:90])
# ---- paths ----
rep("[[150,40],[232,78],[300,120],[400,118],[432,48],[395,-15],[450,-23]],", "[[150,40],[232,78],[255.6,88],[277.8,95.6],[300.7,111],[334.8,120],[400,118],[432,48]],")
rep("[[-120,-80],[-111,-119]],", "[[-120,-80],[-115.6,-102.2],[-118.5,-118.5],[-128.1,-124.4],[-134.1,-125.6]],")
rep("[[45,-60],[20,-110],[40,-150],[62,-190]],", "[[45,-60],[20,-110],[40,-150],[48,-165]],")
rep("[[432,48],[360,-40],[296,-100]],", "[[432,48],[380,-20],[352,-48]],")
rep("PATHS.push([[405,162],[440,155],[477.39,128.73]], [[230,321],[239,306],[244.25,294.75]]);",
    "PATHS.push([[513,-27],[480,-8],[452,4]], [[214,336],[230,321],[239,306],[244.25,294.75]], [[205,-93],[232,-150],[256,-164],[300,-192],[326,-218]]);   /* 2026-11-13 (user): to the exam hall forecourt instead of onto the driving track; the lake link starts on the lake path; Sweet Scoop between the wheel hill and the swing, not through the staff village */")
rep("PATHS[27]=[[-110,190],[-125,250],[-120,330],[-65,360],[0,360]];", "PATHS[27]=[[-116,177],[-125,250],[-120,330],[-65,360],[0,360]];")
rep("walkway([[0,53],[0,45],[2,34]],6,'course-entry',course,0.34);", "")
rep("walkway([[-32,-53],[-20,-50],[2,-48],[2,-42]],4,'exam-hall-walk',course,0.35);", "")
rep("'항구', '코덱스의 동굴', '그랜드 스테이지']);", "'항구', '코덱스의 동굴', '그랜드 스테이지', '숲 속 풍차']);")
# ---- the gate point of every ride, then the queue beside the path just outside it ----
rep("const people = [], postM = mat(0xc9ced6), ropeM = mat(0xd63a2f);",
    "const laneHalf=(x,z)=>{let h=3.5,bd=4;PATHS.forEach((pts,i)=>{for(const q of pts){const d=Math.hypot(q[0]-x,q[1]-z);if(d<bd){bd=d;h=pathHalfWidth(i);}}});return h;};\n"
    "  const gateOf=e=>{const b=e.b,lot=b.c==='ride'&&!NO_LOT.has(b.label),reach=Math.hypot(e.x-b.cx,e.z-b.cz),Rg=lot?b.r+13:reach+3;let sp=null,sc=1e9;\n"
    "    for(const q of pathSamples){const dx=q[0]-b.cx,dz=q[1]-b.cz,d=Math.hypot(dx,dz);if(Math.abs(d-Rg)>2.5)continue;const along=(dx*e.dx+dz*e.dz)/d;if(along<0.5)continue;const c=(1-along)*40+Math.abs(d-Rg);if(c<sc){sc=c;sp=q;}}\n"
    "    if(!sp)return {x:b.cx+e.dx*Rg,z:b.cz+e.dz*Rg,dx:e.dx,dz:e.dz,half:3.5};\n"
    "    let o=null,od=Math.hypot(sp[0]-b.cx,sp[1]-b.cz)+0.8;for(const q of pathSamples){const d=Math.hypot(q[0]-sp[0],q[1]-sp[1]);if(d<2.5||d>7)continue;const r=Math.hypot(q[0]-b.cx,q[1]-b.cz);if(r>od){od=r;o=q;}}\n"
    "    let dx=e.dx,dz=e.dz;if(o){const L=Math.hypot(o[0]-sp[0],o[1]-sp[1]);dx=(o[0]-sp[0])/L;dz=(o[1]-sp[1])/L;}\n"
    "    return {x:sp[0],z:sp[1],dx,dz,half:laneHalf(sp[0],sp[1])};};   /* where the approach path really crosses the ride's fence line, and which way it runs there (2026-11-13) */\n"
    "  entries.forEach(e=>{ if(e.b.c==='ride') e.b.gate=gateOf(e); });\n"
    "  const widePath=(x,z)=>PATHS.some((pts,i)=>{const h=pathHalfWidth(i);return h>4.5&&pts.some(q=>Math.hypot(q[0]-x,q[1]-z)<h+0.4);});\n"
    "  const people = [], postM = mat(0xc9ced6), ropeM = mat(0xd63a2f);")
rex(r"const px = -e\.dz, pz = e\.dx;.*?const cx=point\.x, cz=point\.z;",
    "const gt=e.b.gate||{x:e.x,z:e.z,dx:e.dx,dz:e.dz,half:3.5}, px=-gt.dz, pz=gt.dx, lotR=NO_LOT.has(e.b.label)?0:e.b.r+9;\n"
    "    const choices=[1,-1].flatMap(side=>[6.6,12,18,25].map(f=>({x:gt.x+gt.dx*f+px*side*(gt.half+3.7),z:gt.z+gt.dz*f+pz*side*(gt.half+3.7)})));   /* beside the path, just outside the gate (user, 2026-11-13: the queues stood off in the grass) */\n"
    "    const point=choices.find(p=>Math.hypot(p.x,p.z)<edgeR(p.x,p.z)-12 && !IB.some(b=>b!==e.b && b.c!=='char' && !b.noPop && Math.hypot(p.x-b.cx,p.z-b.cz)<Math.min(b.r,90)+6) && (!lotR||Math.hypot(p.x-e.b.cx,p.z-e.b.cz)>lotR+5.4) && [-3.2,0,3.2].every(x=>[-4.5,0,4.5].every(z=>{const X=p.x+px*x+gt.dx*z,Z=p.z+pz*x+gt.dz*z;return !nearPath(X,Z,3.3)&&!widePath(X,Z);})));\n"
    "    if(!point) return;\n"
    "    const cx=point.x, cz=point.z;")
rep("const th = Math.atan2(e.dx, e.dz), g = new THREE.Group(); g.position.set(cx, G, cz);", "const th = Math.atan2(gt.dx, gt.dz), g = new THREE.Group(); g.position.set(cx, G, cz);")
rep("push({name:e.b.label,x:cx,z:cz,entry:[e.x,e.z],direction:[e.dx,e.dz],group:g});", "push({name:e.b.label,x:cx,z:cz,entry:[gt.x,gt.z],direction:[gt.dx,gt.dz],group:g});")
rex(r"R = b\.r \+ 9;\s*woodFence\(b\.cx, b\.cz, R, ea, 13/R\);\s*gateSign\(b\.cx \+ Math\.cos\(ea\)\*\(R \+ 4\), b\.cz \+ Math\.sin\(ea\)\*\(R \+ 4\), Math\.PI/2 - ea, b\.label\);",
    "R = b.r + 9, gt = b.gate, ga = gt ? Math.atan2(gt.z - b.cz, gt.x - b.cx) : ea;\n    woodFence(b.cx, b.cz, R, ga, 13/R);\n    if(gt) gateSign(gt.x, gt.z, Math.PI/2 - Math.atan2(gt.dz, gt.dx), b.label); else gateSign(b.cx + Math.cos(ea)*(R + 4), b.cz + Math.sin(ea)*(R + 4), Math.PI/2 - ea, b.label);   /* the name arch stands across the path itself (2026-11-13) */")
# ---- benches ----
i = s.index("n = Math.floor(L/36);"); j = s.rindex("PATHS.forEach(pts=>{", 0, i); s = s[:j] + "PATHS.forEach((pts, bpi)=>{" + s[j + len("PATHS.forEach(pts=>{"):]
rep("const bx = p.x-nx*11, bz = p.z-nz*11;", "const bw = pathHalfWidth(bpi) + 1.5, bx = p.x-nx*bw, bz = p.z-nz*bw;   /* at the edge of the pavement, whatever the width (user, 2026-11-13: the benches sat out in the grass) */")
rep("x=p.x-v.z*side*(route.width/2+6),z=p.z+v.x*side*(route.width/2+6);", "x=p.x-v.z*side*(route.width/2+1.9),z=p.z+v.x*side*(route.width/2+1.9);")
rep("if(!free(x,z,2.8)||parkPolish.amenities.some(a=>Math.hypot(a.x-x,a.z-z)<12))continue;", "if(!free(x,z,.7)||parkPolish.amenities.some(a=>Math.hypot(a.x-x,a.z-z)<12))continue;")
rep("if(existingSeats.every(([a,b])=>Math.hypot(x-a,z-b)>20)&&parkPolish.borders.every(a=>Math.hypot(a.x-x,a.z-z)>3.6)){", "if(existingSeats.every(([a,b])=>Math.hypot(x-a,z-b)>20)){")
rep("parkPolish.amenities.push({kind:'bench',x,z});existingSeats.push([x,z]);", "parkPolish.amenities.push({kind:'bench',x,z});existingSeats.push([x,z]);parkPolish.borders.forEach((a,bi)=>{if(Math.hypot(a.x-x,a.z-z)<4.4){hedges.setMatrixAt(bi,new THREE.Matrix4().makeScale(0,0,0));hedges.instanceMatrix.needsUpdate=true;}});")
P.write_bytes(s.encode('utf-8')); print('ok crlf', s.count('\r\n'), 'course-entry refs', s.count('course-entry'), 'exam-hall-walk refs', s.count('exam-hall-walk'))
