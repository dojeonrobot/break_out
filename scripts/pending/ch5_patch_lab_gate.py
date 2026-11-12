# 2026-11-12 (사용자: 「관람차 뒤쪽에 자일로 지하시설로 가는 입구 하나 만들어줘 애들이 도착하면 입구 보이게」)
#   언덕 앞쪽(길 쪽)의 작은 출입금지 문을 없애고, 관람차 뒤쪽(길 반대편, 290도) 언덕 발치에 지하 연구실 입구를 둔다.
#   평소에는 언덕 안에 들어가 있어 보이지 않고, 미션 4가 열린 조가 38 안으로 오면 언덕에서 밀려 나오며 문이 열린다(약 2.4초).
#   미션 4를 하는 동안과 끝낸 뒤에는 계속 열려 있다. 조절: LABG = {ang, near, out, back}.
import pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
a = s.index('function buildLabDoor(){ if(LAB_DOOR) return;'); END = 'LAB_DOOR = freeSpot(FX + ux*86, FZ + uz*86); }'; b = s.index(END, a) + len(END)
assert s.count('function buildLabDoor(){') == 1 and b - a < 2500, (b - a)
NEW = r'''/* the way down to 자일로's lab (user, 2026-11-12): behind the wheel, inside the hill until the children get there */
const LABG = {ang:290, near:38, out:2.4, back:1.6};   /* ang: where round the hill (the park path climbs it at 118), near: how close before it shows, out/back: seconds to come out / go back in */
function labHallTex(){ const c = document.createElement('canvas'); c.width = 256; c.height = 288; const x = c.getContext('2d'), vx = 128, vy = 132;
  const bg = x.createLinearGradient(0, 0, 0, 288); bg.addColorStop(0, '#10242f'); bg.addColorStop(1, '#060d13'); x.fillStyle = bg; x.fillRect(0, 0, 256, 288);
  const pt = i=>{ const k = 1 - 1/(1 + i*0.42); return [288 - (288 - vy)*k, 128*(1 - k) + 24*k]; };
  for(let i = 0; i < 9; i++){ const [y0, w0] = pt(i), [y1, w1] = pt(i + 1), l = Math.max(10, 40 - i*4);
    x.fillStyle = `rgb(${l},${l + 14},${l + 22})`; x.beginPath(); x.moveTo(vx - w0, y0); x.lineTo(vx + w0, y0); x.lineTo(vx + w1, y1); x.lineTo(vx - w1, y1); x.closePath(); x.fill();
    x.fillStyle = 'rgba(127,227,255,' + (0.85 - i*0.07) + ')'; x.fillRect(vx - w1, y1 - 1.5, w1*2, 3); }
  const [yf, wf] = pt(9); x.fillStyle = '#bff1ff'; x.fillRect(vx - wf, yf - 58, wf*2, 58);
  const gl = x.createRadialGradient(vx, yf - 30, 4, vx, yf - 30, 96); gl.addColorStop(0, 'rgba(160,236,255,.85)'); gl.addColorStop(1, 'rgba(160,236,255,0)'); x.fillStyle = gl; x.fillRect(0, 0, 256, 288);
  x.strokeStyle = 'rgba(127,227,255,.55)'; x.lineWidth = 3; [[-1], [1]].forEach(([d])=>{ x.beginPath(); x.moveTo(vx + d*128, 0); x.lineTo(vx + d*wf, yf - 58); x.stroke(); x.beginPath(); x.moveTo(vx + d*122, 170); x.lineTo(vx + d*(wf + 2), yf - 22); x.stroke(); });
  const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; return tx; }
function labGateBuild(){ if(labGateBuild.o) return labGateBuild.o; const FX = FERRIS_X*K, FZ = FERRIS_Z*K, A = LABG.ang*Math.PI/180, ux = Math.cos(A), uz = Math.sin(A);
  const g = new THREE.Group(); g.name = 'lab-gate'; g.position.set(FX + ux*76, G, FZ + uz*76); g.rotation.y = Math.atan2(ux, uz); g.visible = false; islRoot.add(g);
  const conc = new THREE.MeshLambertMaterial({color:0x8d939b}), steel = new THREE.MeshLambertMaterial({color:0x4a5058}), dark = new THREE.MeshLambertMaterial({color:0x10151c}), warn = new THREE.MeshLambertMaterial({color:0xffd400});
  const P = new THREE.Group(), Q = new THREE.Group(); g.add(P); g.add(Q);
  add(P, BOX(14, 9, 7), conc, 0, 0, -1.5, false); add(P, BOX(15, 0.8, 7.6), steel, 0, 9, -1.5, false); add(P, BOX(14, 0.25, 6), conc, 0, 0, 5, false);
  add(P, BOX(6.8, 7.3, 0.2), dark, 0, 0, 2.0, false);
  const hall = add(P, new THREE.PlaneGeometry(6.4, 7), new THREE.MeshBasicMaterial({map:labHallTex(), transparent:true, opacity:0}), 0, 3.6, 2.13, false);
  const leaves = [-1, 1].map(sd=>{ const L = new THREE.Group(); P.add(L); add(L, BOX(3.4, 7.3, 0.4), steel, 0, 0, 0, false); add(L, BOX(3.4, 0.8, 0.46), warn, 0, 3.1, 0, false); L.position.set(sd*1.7, 0, 2.36); L.userData.sd = sd; return L; });
  add(P, new THREE.PlaneGeometry(4.6, 1.15), new THREE.MeshBasicMaterial({map:signTex('출입금지', {bg:'#ffd400', fg:'#1a1d22', size:60, w:384, h:96})}), 0, 8.15, 2.03, false);
  add(P, CYL(0.5, 0.6, 0.5, 8), steel, 0, 9.8, 1.2, false); const lamp = add(P, SPH(0.55, 10, 8), glowMat(0xffb23e, 0.5), 0, 10.6, 1.2, false);
  [-1, 1].forEach(sd=>{ add(Q, CYL(0.35, 0.35, 4.6, 8), conc, sd*7.6, 0, 7.2, false); add(Q, SPH(0.45, 8, 6), glowMat(0xffb23e, 0.9), sd*7.6, 4.8, 7.2, false); });
  const st = {k:0, last:null}, ez = v=>{ v = Math.min(Math.max(v, 0), 1); return v*v*(3 - 2*v); };
  const pose = t=>{ const a = ez(st.k/0.55), b = ez((st.k - 0.5)/0.5); g.visible = st.k > 0; P.position.z = -11*(1 - a); Q.position.y = -5.6*(1 - a);
    leaves.forEach(L=>{ L.position.x = L.userData.sd*(1.7 + 3.4*b); }); hall.material.opacity = b; lamp.material.opacity = st.k > 0 && st.k < 1 ? (Math.sin(t*14) > 0 ? 0.95 : 0.3) : 0.5; };
  islAnim.push(t=>{ if(typeof RIDE_PROBE !== 'undefined' && RIDE_PROBE) return; const dt = st.last == null ? 0 : Math.min(Math.max(t - st.last, 0), 0.05); st.last = t;
    const done = QDONE.has('q5'), open = !!ADMIN_KEY || QDONE.has('q4') || done, near = !!walk && Math.hypot(walk.x - g.position.x, walk.z - g.position.z) < LABG.near;
    const want = open && (near || done || (mini && mini.kind === 'device'));
    if(want && st.k === 0 && walk && dt > 0) sfx('open');
    if((want && st.k >= 1) || (!want && st.k <= 0)) return;
    st.k = Math.min(Math.max(st.k + (want ? dt/LABG.out : -dt/LABG.back), 0), 1); pose(t); });
  pose(0);
  return labGateBuild.o = {g, st, spot:[FX + ux*90, FZ + uz*90]}; }
window.__labGate = ()=>{ const o = labGateBuild(); return {k:+o.st.k.toFixed(3), visible:o.g.visible, x:o.g.position.x, z:o.g.position.z, spot:o.spot, door:LAB_DOOR}; };
function buildLabDoor(){ if(LAB_DOOR) return; const o = labGateBuild(); LAB_DOOR = freeSpot(o.spot[0], o.spot[1]); }'''
s = s[:a] + NEW + s[b:]
old = "function questApply(){ try{ flowLockUI(); if(collectorModel)collectorSync(); }catch(e){}"
assert s.count(old) == 1
s = s.replace(old, old + " try{ if(QDONE.has('q4') || QDONE.has('q5')) labGateBuild(); }catch(e){}   /* the lab's way down stays open for a team that has been there */")
P.write_bytes(s.encode('utf-8')); print('ok')

# 2차: 입구 앞에 서 있던 나무를 치운다(섬을 굽기 전, 정문 블록의 clearTreesAt 옆에서)
s = P.read_bytes().decode('utf-8')
old = "clearTreesAt(-70, 405, 42); clearTreesAt(70, 405, 42);"
if 'the lab gate behind the wheel' not in s:
    assert s.count(old) == 1
    s = s.replace(old, old + " clearTreesAt(FERRIS_X*K + Math.cos(290*Math.PI/180)*92, FERRIS_Z*K + Math.sin(290*Math.PI/180)*92, 15);   /* the lab gate behind the wheel (LABG.ang) */")
    P.write_bytes(s.encode('utf-8')); print('trees ok')
