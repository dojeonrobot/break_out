# 2026-11-12 (사용자): 방문객이 줄지어 다니고 서로 비켜 가는 것이 어색하다 → 길 폭 전체를 자유롭게 오가게, 서로 비켜 가기 없음,
#   제로·리코(탐험 캐릭터)는 그냥 통과. 가끔 멈춰 서는 사람도 둔다.
#   - 차선(오른쪽 한 줄) 대신 사람마다 길 폭 안에서 좌우로 천천히 흘러 다니는 자리
#   - 구간마다 가운데로 모였다 벌어지던 것을 없애고, 실제 자리를 부드럽게 따라가게(모퉁이에서 튀지 않음), 바라보는 방향 = 실제 가는 방향
# 사용: python scripts/pending/ch5_patch_visitors_free.py   (한 번만)
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
assert 'w.sway' not in s
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70]); s = s.replace(old, new)
rep("wait=n.stop?4+rand()*7:n.edges.length===1?1.3:0;", "wait=n.stop?4+rand()*7:n.edges.length===1?1.3:rand()<.03?2+rand()*5:0;")
rep("walkers.push({legs,total,phase:rand()*total,lane:.18+rand()*.57});", "walkers.push({legs,total,phase:rand()*total,lane:(rand()*2-1)*.55,sway:.07+rand()*.1,sph:rand()*6.28});")
rep("    near.clear();for(let j=0;j<positions.length;j++){const p=positions[j];if(!p)continue;const k=nearKey(Math.floor(p[0]),Math.floor(p[1]));nearNext[j]=near.has(k)?near.get(k):-1;near.set(k,j);}\n", "")
a = s.index("      const dx=l.b.x-l.a.x,dz=l.b.z-l.a.z,len=Math.hypot(dx,dz)||1,off=w.lane*"); b = s.index("      // Keep every lane clear of fountain basins, including the small plaza pair.")
s = s[:a] + ("      const dx=l.b.x-l.a.x,dz=l.b.z-l.a.z,len=Math.hypot(dx,dz)||1,hw=Math.max(0,l.width/2-.7),off=hw*Math.max(-1,Math.min(1,w.lane+.45*Math.sin(t*w.sway+w.sph)));   /* anywhere across the path, drifting slowly (user, 2026-11-12) */\n"
               "      let x=l.a.x+dx*u-dz/len*off,z=l.a.z+dz*u+dx/len*off;\n"
               "      { const p=positions[i]; if(p&&Math.hypot(x-p[0],z-p[1])<5){ x=p[0]+(x-p[0])*.14; z=p[1]+(z-p[1])*.14; } }   /* follow the target smoothly: no jump at corners or where a leg turns back */\n") + s[b:]
rep("      let yaw=Math.atan2(dx,dz);\n", "      let yaw=Math.atan2(dx,dz); { const p=positions[i]; if(p){ const mx=x-p[0],mz=z-p[1]; if(mx*mx+mz*mz>4e-4&&mx*mx+mz*mz<4) yaw=Math.atan2(mx,mz); else if(p[2]!=null) yaw=p[2]; } }\n")
rep("positions[i]=[x,z];guests.set(", "positions[i]=[x,z,yaw];guests.set(")
P.write_bytes(s.encode('utf-8')); print('ok')
