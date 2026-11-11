# 2026-11-11 전체 점검에서 고친 것: ① 탐험 중 지도 이름표·표식이 미션 안내 상자(#questHud, #walkHud) 밑에 깔리지 않게 ② 방문객이 탐험 중인 캐릭터를 뚫고 지나가지 않게
# 사용: python ch5_patch_checkup_1111.py [사본경로]   (ch5_patch_visitors.py 적용 뒤에)
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s

def swap(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)

# ① labels keep clear of the walk-mode HUD cards (rects re-read at most every 400 ms, not per frame)
swap('''function placeLabels(){
  const W=innerWidth, H=innerHeight, placed=[];
''', '''let hudBoxAt=0,hudBoxList=[];
function labelHudBoxes(){
  const now=performance.now();
  if(now-hudBoxAt>400){hudBoxAt=now;hudBoxList=['questHud','walkHud'].map(id=>document.getElementById(id)).filter(Boolean).map(e=>e.getBoundingClientRect()).filter(r=>r.width>1&&r.height>1).map(r=>[r.left-6,r.top-6,r.right+6,r.bottom+6]);}
  return hudBoxList;
}
function placeLabels(){
  const W=innerWidth, H=innerHeight, placed=[], huds=labelHudBoxes(), underHud=box=>huds.some(p=>box[0]<p[2]&&box[2]>p[0]&&box[1]<p[3]&&box[3]>p[1]);
''')
swap('''    const box=mapLabelBox(mk.el,x,y,W,H);if(box)placed.push(box);
''', '''    const box=mapLabelBox(mk.el,x,y,W,H);if(box&&underHud(box)){mk.el.style.display='none';return;}if(box)placed.push(box);
''')
swap('''    if(!emphasized&&placed.some(p=>box[0]<p[2]&&box[2]>p[0]&&box[1]<p[3]&&box[3]>p[1])){el.style.display='none';return;}
    placed.push(box);el.classList.toggle('sel',isSel);''', '''    if(underHud(box)||(!emphasized&&placed.some(p=>box[0]<p[2]&&box[2]>p[0]&&box[1]<p[3]&&box[3]>p[1]))){el.style.display='none';return;}
    placed.push(box);el.classList.toggle('sel',isSel);''')
# ② visitors walk around the explorer (and the partner beside them) instead of through them
swap('''        if(push){push=Math.min(.4,push);x-=dz/len*push;z+=dx/len*push;}}
''', '''        if(push){push=Math.min(.4,push);x-=dz/len*push;z+=dx/len*push;}}
      if(walk&&!walk.fly){const ex=x-walk.x,ez=z-walk.z,ed=Math.hypot(ex,ez),er=2.3;if(ed<er){if(ed>.01){x=walk.x+ex/ed*er;z=walk.z+ez/ed*er;}else{x-=dz/len*er;z+=dx/len*er;}}}
''')
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
