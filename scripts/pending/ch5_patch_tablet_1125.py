"""2026-11-25 노션 「scan break」 체크 필요 1~6 (태블릿·좁은 화면 겹침) 패치. 한 번만 적용.
1 보이드 대화창: 단계 카드가 있으면 아래 여백을 늘려 ‹ 이전·다음과 겹치지 않게
3 지도: 내 조 이름표를 맨 위·먼저 놓고, 다른 조 이름표가 겹치면 아래로 비켜 쌓기
5 달리기 버튼: 점프 옆(오른쪽)으로, ON/OFF 표시
2·4·6 떠 있는 UI 겹침 막기(layout guard): 좌표 카드·건물 카드는 아래 막대·버튼 위로, 패널·현황판은 그 위에서 끝나게,
      관리자 건너뛰기 알약은 시뮬레이터·미션 머리띠 아래로
"""
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_text(encoding='utf-8')
assert 'layout guard (2026-11-25' not in s, 'already applied'

# --- 3) placeLabels: 내 조 먼저, 조 이름표 겹치면 아래로 쌓기
old = """  markers.forEach(mk=>{
    v3.set(mk.x, mk.y, mk.z).project(camera);
    if(v3.z>1 || !mk.show){ mk.el.style.display='none'; return; }
    const x=(v3.x+1)/2*W, y=(1-v3.y)/2*H;
    const box=mapLabelBox(mk.el,x,y,W,H);if(box&&underHud(box)){mk.el.style.display='none';return;}if(box)placed.push(box);
  });"""
assert s.count(old) == 1, 'placeLabels anchor'
new = """  // my team first and on top; other team labels that would cover it stack below (user's tablet, 2026-11-25: 4조 hidden under 8조)
  const rank=mk=> mk.isTeam ? (mk.el.classList.contains('me') ? 0 : 1) : 2, teamBoxes=[], hit=(b,p)=> b[0]<p[2]&&b[2]>p[0]&&b[1]<p[3]&&b[3]>p[1];
  markers.slice().sort((a,b)=> rank(a)-rank(b)).forEach(mk=>{
    v3.set(mk.x, mk.y, mk.z).project(camera);
    if(v3.z>1 || !mk.show){ mk.el.style.display='none'; return; }
    const x=(v3.x+1)/2*W; let y=(1-v3.y)/2*H;
    let box=mapLabelBox(mk.el,x,y,W,H);
    if(box&&mk.isTeam){ for(let k=0;k<8;k++){ const hs=teamBoxes.filter(p=>hit(box,p)); if(!hs.length) break; y=Math.max(...hs.map(p=>p[3]))+4+(box[3]-box[1]-8); box=mapLabelBox(mk.el,x,y,W,H); if(!box) break; } }
    if(box&&underHud(box)){mk.el.style.display='none';return;}if(box){placed.push(box); if(mk.isTeam) teamBoxes.push(box);}
  });"""
s = s.replace(old, new)

# --- CSS (끝에 덧붙임, 마커 줄 바로 앞)
CSS = ("/* tablet overlaps (노션 scan break 체크 필요, 2026-11-25) */"
       "#voidVn .box:has(#voidCard:not(:empty)){padding-bottom:50px}"
       ".mk.team{z-index:1}.mk.team.me{z-index:3}"
       "body #walkRun{left:auto;right:calc(24px + var(--jumpW,132px) + 12px)}"
       "body #walkRun::after{content:'OFF';font:800 11px/1 var(--mono);letter-spacing:.06em;padding:4px 6px;border-radius:6px;background:rgba(255,255,255,.16);color:rgba(255,255,255,.75)}"
       "body #walkRun[aria-pressed=true]::after{content:'ON';background:#fff;color:#127a48}"
       "\n")
marker = '</style></head><body>'
assert s.count(marker) == 1
s = s.replace(marker, CSS + marker)

# --- layout guard (본문 끝, </body> 앞)
JS = r"""<script>/* layout guard (2026-11-25, 노션 scan break 체크 2·4·6): 화면 크기마다 겹치는 떠 있는 UI를 비켜 세운다. 겹침이 없으면 아무것도 바꾸지 않는다 */
(()=>{const $=id=>document.getElementById(id), G=8;
const R=e=>{if(!e||e.hidden)return null;const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||+s.opacity<.05)return null;const r=e.getBoundingClientRect();return r.width>1&&r.height>1?r:null};
const xo=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>4, yo=(a,b)=>Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;
const ids=a=>a.map($).filter(Boolean);
function lift(el,bl){if(!el)return;el.style.bottom='';for(let k=0;k<4;k++){const r=R(el);if(!r)return;let f=Infinity;bl.forEach(b=>{const q=R(b);if(q&&b!==el&&xo(r,q)&&yo(r,q))f=Math.min(f,q.top)});if(f===Infinity)return;el.style.bottom=(innerHeight-f+G)+'px'}}
function down(el,bl){if(!el)return;el.style.top='';const r=R(el);if(!r)return;let t=-1;bl.forEach(b=>{const q=R(b);if(q&&xo(r,q)&&yo(r,q))t=Math.max(t,q.bottom)});if(t>=0)el.style.top=(t+G)+'px'}
function fit(el,bl){if(!el)return;el.style.maxHeight='';const r=R(el);if(!r)return;let f=Infinity;bl.forEach(b=>{const q=R(b);if(q&&xo(r,q)&&q.top>r.top+80&&q.top<r.bottom)f=Math.min(f,q.top)});if(f<Infinity)el.style.maxHeight=Math.max(120,f-G-r.top)+'px'}
function side(el,bl){if(!el)return;el.style.left='';el.style.right='';const r=R(el);if(!r)return;const W=innerWidth;let L=0,Rt=W,n=0;bl.forEach(b=>{const q=R(b);if(!q||b===el||!yo(r,q))return;if(xo(r,q))n++;if(q.left+q.width/2<W/2)L=Math.max(L,q.right+G);else Rt=Math.min(Rt,q.left-G)});if(n&&Rt-L>=r.width){el.style.left=L+'px';el.style.right=(W-Rt)+'px'}}
function tick(){try{
  down($('panel'),ids(['worlds']));down($('board'),ids(['worlds']));
  const mb=ids(['bar','restoreBtn','callPill','sndBtn','adminBtn','simBtn','questPill']);side($('meCoord'),mb);lift($('meCoord'),mb);
  lift($('info'),ids(['bar','meCoord','sndBtn','adminBtn','restoreBtn','callPill','simBtn']));
  fit($('panel'),ids(['restoreBtn','callPill','simBtn','questPill','meCoord','bar','info']));
  fit($('board'),ids(['info','meCoord','bar','sndBtn','adminBtn']));
  const a=$('admSkip');if(a){a.style.top='';const r=R(a);if(r){let t=-1;ids(['simHud','questHud','walkHud','worlds']).forEach(b=>{const q=R(b);if(q&&xo(r,q)&&yo(r,q))t=Math.max(t,q.bottom)});if(t>=0)a.style.top=(t+G)+'px'}}
  const j=R($('walkJump')),rb=$('walkRun');if(j)document.documentElement.style.setProperty('--jumpW',Math.round(j.width)+'px');
  if(j&&rb){rb.style.right='';rb.style.bottom='';const r=R(rb),p=R($('walkPad'));if(r&&p&&xo(r,p)&&yo(r,p)){rb.style.right=(innerWidth-j.right)+'px';rb.style.bottom=(innerHeight-j.top+12)+'px'}}   /* narrow screen: RUN goes above JUMP instead of under the joystick */
}catch(e){}}
addEventListener('resize',()=>setTimeout(tick,60));setInterval(tick,500);tick();})();
</script>
"""
assert s.count('</body>') == 1
s = s.replace('</body>', JS + '</body>')
P.write_text(s, encoding='utf-8', newline='')
print('patched', len(s))
