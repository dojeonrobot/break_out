# 2026-11-11 사람 그림자 끄기(사용자: 렉에 한몫): 걷는 방문객·대기 줄·놀이기구 탑승객·미니열차 승객은 그림자를 만들지 않는다
# 사용: python ch5_patch_people_shadows.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s

def swap(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)

# visitors and queue guests (instanced)
swap("m.castShadow=!PHONE&&shadow;m.frustumCulled=false;", "m.castShadow=false;m.frustumCulled=false;")
# seated riders on every ride
swap("  \n  return g;}\n// ---------- missions ----------", "  g.traverse(o=>{o.castShadow=false;});   /* people cast no shadows (2026-11-11) */\n  return g;}\n// ---------- missions ----------")
# mini train passengers
swap("g.scale.setScalar(s);guests.push({g,legs});parkPolish.passengers.push(g);", "g.scale.setScalar(s);g.traverse(o=>{o.castShadow=false;});guests.push({g,legs});parkPolish.passengers.push(g);")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
