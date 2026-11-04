"""2026-11-04 바이킹 복구: 업로드 전에는 공사장, 조가 올린 STL/OBJ/GLB 배가 팔에 걸려 흔들린다(조 단위 서버 저장).
python scripts/pending/ch5_patch_viking.py  (저장소 루트에서, 한 번만)"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'chapter05', 'index.html')
S = os.path.join(ROOT, 'server', 'ch5_void_server.py')
N = os.path.join(ROOT, 'config', 'nginx-breakout.conf')


def load(p):
    return io.open(p, encoding='utf-8', newline='').read().replace('\r\n', '\n')


def dump(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (a[:70], s.count(a))
    return s.replace(a, b)


h = load(P)
assert 'VIK_EXT' not in h, 'already patched'

# ---- 1. viking block: construction site + swing that carries the uploaded ship ----
i0 = h.index('  /* collapsed ride (story 2026-11-04')
i1 = h.index('\n', h.index('add(vik, BOX(0.3, 2.8, 0.3)', i0)) + 1
new_block = r'''  /* 2026-11-04 rebuild (user): until the team uploads its own ship (STL/OBJ/GLB) the viking is a construction site. The A-frames stand;
     the swing (arms + the uploaded ship in VK.hold) and the site swap. Both are dynamic, so batchIsland never bakes them. */
  swing.remove(ship); swing.userData.dynamic = true; swing.visible = false;
  const hold = new THREE.Group(); hold.position.y = -26.4; swing.add(hold);
  const site = new THREE.Group(); site.userData.dynamic = true; vik.add(site);
  const POLE = mat(0xb9bec6), PLANK = mat(0x9a7b4f);
  [-1, 1].forEach(s=>{ const xs = [s*6, s*24];
    xs.forEach(x=> [-12, -6, 6, 12].forEach(z=> add(site, CYL(0.22, 0.22, 30, 6), POLE, x, 1.2, z, false)));
    for(let y = 7; y <= 31; y += 8){ [-12, 12].forEach(z=> add(site, BOX(18.4, 0.22, 0.22), POLE, s*15, y, z, false)); xs.forEach(x=> add(site, BOX(0.22, 0.22, 24.4), POLE, x, y, 0, false));
      [-11.2, 11.2].forEach(z=> add(site, BOX(18, 0.3, 1.6), PLANK, s*15, y + 0.22, z, false)); } });
  [[-18,0.9,8,0.3],[-14,0.8,-9,1.2],[16,0.8,-8,2.1]].forEach(([x,y,z,r],i)=>{ const d = add(site, new THREE.CylinderGeometry(1.6, 1.6, 0.4, 14), mat(SH[i%4]), x, y, z, false); d.rotation.set(0.15, r, 0.1); });
  add(site, BOX(9, 0.8, 1.2), mat(0x2f62b8), -8, 1, 10, false).rotation.y = 0.5;
  for(let k = 0; k < 4; k++) add(site, BOX(12, 0.6, 1.4), PLANK, 14, 1.2 + k*0.6, 4 + (k%2)*0.4, false).rotation.y = 0.08*k;
  [-20, -10, 0, 10, 20].forEach(x=>{ add(site, CONE(0.8, 2.2, 10), mat(0xff7a1a), x, 1.2, 14, false); add(site, CYL(0.62, 0.7, 0.35, 10), mat(0xffffff), x, 2.0, 14, false); });
  { const sg = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.4), new THREE.MeshBasicMaterial({map:signTex('REBUILDING', {bg:'#ffd400', fg:'#22252b', size:72, w:512, h:124}), side:THREE.DoubleSide}));
    sg.position.set(0, 6.2, 16.6); site.add(sg); [-6.4, 6.4].forEach(x=> add(site, BOX(0.4, 7.9, 0.4), mat(0x3a3f4a), x, 0, 16.6, false)); }
  const TAPE_Y = 0xffd400, TAPE_K = 0x22252b;
  [[-31,-16,31,-16],[31,-16,31,16],[31,16,-31,16],[-31,16,-31,-16]].forEach(([x0,z0,x1,z1])=>{ const L = Math.hypot(x1-x0, z1-z0), n = Math.round(L/2);
    for(let k=0;k<n;k++){ const u = (k+0.5)/n; add(site, BOX(L/n, 0.35, 0.12), mat(k%2 ? TAPE_K : TAPE_Y), x0+(x1-x0)*u, 2.4, z0+(z1-z0)*u, false).rotation.y = -Math.atan2(z1-z0, x1-x0); }
    for(let k=0;k<=Math.round(L/8);k++){ const u = k/Math.round(L/8); add(site, BOX(0.3, 2.8, 0.3), mat(0xe8e8e8), x0+(x1-x0)*u, 1.4, z0+(z1-z0)*u, false); } });
  Object.assign(VK, {vik, swing, hold, site});
  poweredAnim(t=>{ swing.rotation.z = VK.on ? Math.sin(t*0.75)*0.95 : 0; });
'''
h = h[:i0] + new_block + h[i1:]
h = rep(h, 'const viking = new THREE.Group();\n{', 'const viking = new THREE.Group(), VK = {on:false};\n{')

old_pick = "pickable(viking, {n:'바이킹', c:'ride', sub:'놀이기구', cx:70, cz:167,"
h = rep(h, old_pick, 'const VIK_B = ' + old_pick)
h = rep(h, "desc:'용머리를 단 거대한 배가 하늘 높이 흔들리던 바이킹. 배가 팔에서 떨어져 내려앉아, 지금은 운행을 멈추고 출입을 막아 두었습니다.',\n  facts:[['위치','정문 거리 동쪽'],['상태','운행 중지 · 출입 금지'],['특징','용머리 · 방패 장식']]});",
        "desc:'용머리를 단 거대한 배가 하늘 높이 흔들리던 바이킹. 배가 팔에서 떨어져 무너진 뒤, 지금은 다시 짓고 있습니다.',\n  facts:[['위치','정문 거리 동쪽'],['상태','공사 중'],['특징','용머리 · 방패 장식']]});\n" + r'''// ---------- viking rebuild from the team's own ship file (2026-11-04) ----------
// The team uploads a ship model; it is fitted to the swing (longest side along the swing, at most 42 long, 12 wide, 24 high) and the ride swings
// once the park has power. The server keeps one file per team (data/vikings/<team>.<ext>); team tablets show their own, the admin's 「모든 조」
// view and the big screen show the latest upload. Without a server (file:, LOCAL) the ship lives in this tab only.
const VIK_EXT = ['stl', 'obj', 'glb'], VIK_MAX = 20*1024*1024, VIK_TRIS = 800000;
let VIKINGS = {}, VIK_SHOWN = null, VIK_BUSY = false, VIK_SEQ = 0;
const VIK_TXT = {site:{d:VIK_B.desc, s:'공사 중'}, on:{d:'용머리를 단 거대한 배가 하늘 높이 흔들리는 바이킹. 신입사원이 설계한 배로 다시 세웠습니다.', s:'운행 중'}};
const vikMat = ()=> new THREE.MeshLambertMaterial({color:0xc0392b});
function vikTeam(){ const vt = viewTeam(); if(vt > 0 && VIKINGS[vt]) return String(vt); if(vt > 0 && !LOCAL) return ''; let best = '', bt = -1; for(const [t, v] of Object.entries(VIKINGS)) if(v && v.t > bt){ bt = v.t; best = t; } return best; }
async function vikLoad(buf, ext){
  let obj;
  if(ext === 'glb') obj = (await new GLTFLoader().parseAsync(buf, '')).scene;
  else if(ext === 'obj'){ const {OBJLoader} = await import('three/addons/loaders/OBJLoader.js'); obj = new OBJLoader().parse(new TextDecoder().decode(buf)); obj.traverse(o=>{ if(o.isMesh) o.material = vikMat(); }); }
  else { const {STLLoader} = await import('three/addons/loaders/STLLoader.js'); const g = new STLLoader().parse(buf); if(!g.attributes.normal) g.computeVertexNormals();
    obj = new THREE.Mesh(g, g.hasColors ? new THREE.MeshLambertMaterial({vertexColors:true}) : vikMat()); obj.rotation.x = -Math.PI/2; }   /* STL from CAD tools is Z-up */
  let tris = 0; obj.traverse(o=>{ if(o.isMesh){ const g = o.geometry; tris += (g.index ? g.index.count : g.attributes.position.count)/3; o.castShadow = o.receiveShadow = true; } });
  if(!tris) throw new Error('모델에 면이 없습니다');
  if(tris > VIK_TRIS) throw new Error('면이 너무 많습니다');
  const turn = new THREE.Group(), fit = new THREE.Group(); turn.add(obj); fit.add(turn); fit.updateMatrixWorld(true);
  let bb = new THREE.Box3().setFromObject(turn); if(bb.isEmpty()) throw new Error('모델이 비어 있습니다');
  let sz = bb.getSize(new THREE.Vector3()); if(sz.z > sz.x*1.05){ turn.rotation.y = Math.PI/2; fit.updateMatrixWorld(true); bb = new THREE.Box3().setFromObject(turn); sz = bb.getSize(new THREE.Vector3()); }
  const k = Math.min(42/Math.max(sz.x, 1e-6), 12/Math.max(sz.z, 1e-6), 24/Math.max(sz.y, 1e-6)), c = bb.getCenter(new THREE.Vector3());
  fit.scale.setScalar(k); fit.position.set(-c.x*k, -bb.min.y*k, -c.z*k); fit.userData.tris = tris; return fit;
}
function vikDrop(){ while(VK.hold.children.length){ const o = VK.hold.children.pop(); o.traverse(x=>{ if(x.isMesh){ x.geometry.dispose(); (Array.isArray(x.material) ? x.material : [x.material]).forEach(m=>{ if(m.map) m.map.dispose(); m.dispose(); }); } }); } }
function vikSet(on, model, live){
  vikDrop(); if(model) VK.hold.add(model);
  VK.on = !!on; VK.site.visible = !on; VK.swing.visible = !!on;
  if(on){ if(VK.site.parent) VK.site.parent.remove(VK.site); } else if(!VK.site.parent) VK.vik.add(VK.site);   /* detached while restored: rideSweep draws every mesh whose own flag is visible */
  const tx = on ? VIK_TXT.on : VIK_TXT.site; VIK_B.desc = tx.d; VIK_B.facts = [['위치','정문 거리 동쪽'],['상태', tx.s],['특징','용머리 · 방패 장식']];
  if(live && on && W.id === 'island'){ SWEEP_MODE.viking = 'rise'; let sw = null; fxChain('viking', [{n:'draw', start(){ sw = rideSweep({id:'viking', b:VIK_B}, 0.2); }, tick:k=>{ if(sw) sw.tick(k); return k >= (sw ? sw.until : 0.6); }, end(){ if(sw) sw.end(); }}]); sfx('power'); }
  vikCard();
}
async function vikingSync(){
  const t = vikTeam(), v = t ? VIKINGS[t] : null, key = v ? `${t}:${v.t}` : '';
  if(key === VIK_SHOWN) return; const live = VIK_SHOWN !== null; VIK_SHOWN = key; const seq = ++VIK_SEQ;
  if(!v){ vikSet(false); return; }
  try{ const buf = v.buf || await fetch(`${API}/viking/${t}.${v.ext}?v=${v.t}`).then(r=>{ if(!r.ok) throw new Error(r.status); return r.arrayBuffer(); });
    const model = await vikLoad(buf, v.ext); if(seq !== VIK_SEQ) return; vikSet(true, model, live); }
  catch(e){ console.error(e); if(seq === VIK_SEQ){ vikSet(false); toast('바이킹 배 모델을 불러오지 못했습니다'); } }
}
function vikCardHTML(){
  if(SCREEN) return '';
  const t = vikTeam(), v = t ? VIKINGS[t] : null, mine = LOCAL || (TEAM > 0 && (!v || +t === TEAM));
  let hh = '<div class="vik">';
  if(v) hh += `<p class="vikf">${LOCAL ? '' : `${esc(t)}조 · `}${esc(v.name || '배 모델')}</p>`;
  if(mine) hh += `<button class="enter" type="button" data-vik="up"${VIK_BUSY ? ' disabled' : ''}>${VIK_BUSY ? '올리는 중' : v ? '다른 배로 바꾸기' : '배 모델 올려 복구하기'}</button><small>STL, OBJ, GLB · 20MB까지</small>`;
  else if(!v && !TEAM && !ADMIN_KEY) hh += '<small>우리 조를 고르면 배 모델을 올릴 수 있습니다</small>';
  if(ADMIN_KEY && v && !LOCAL) hh += `<button class="enter ghost" type="button" data-vik="clear">공사 중으로 되돌리기</button>`;
  return hh + '</div>';
}
function vikCard(){ const box = document.querySelector('#iIsl .vik'); if(box) box.outerHTML = vikCardHTML(); }
const vikFile = Object.assign(document.createElement('input'), {type:'file', accept:'.stl,.obj,.glb', hidden:true}); document.body.appendChild(vikFile);
vikFile.addEventListener('change', ()=>{ const f = vikFile.files[0]; vikFile.value = ''; if(f) vikUpload(f); });
async function vikUpload(file){
  const ext = (file.name.split('.').pop() || '').toLowerCase();
  if(!VIK_EXT.includes(ext)){ toast('STL, OBJ, GLB 파일만 올릴 수 있습니다'); return; }
  if(file.size > VIK_MAX){ toast('20MB보다 작은 파일을 올려 주세요'); return; }
  VIK_BUSY = true; vikCard();
  try{
    const buf = await file.arrayBuffer();
    try{ await vikLoad(buf.slice(0), ext); }catch(e){ throw new Error(e.message === '면이 너무 많습니다' ? '면이 너무 많은 모델입니다. 줄여서 다시 내보내 주세요' : '이 파일은 3D 모델로 열 수 없습니다'); }
    if(LOCAL){ VIKINGS = {...VIKINGS, local:{ext, name:file.name, t:Date.now(), buf}}; }
    else {
      const r = await fetch(`${API}/viking?team=${TEAM}&ext=${ext}&name=${encodeURIComponent(file.name.slice(0, 60))}`, {method:'POST', headers:{'Content-Type':'application/octet-stream'}, body:buf});
      let j = {}; try{ j = await r.json(); }catch(e){} if(!r.ok) throw new Error(j.error || `서버 오류 (${r.status})`);
      VIK_BUSY = false; applyState(j);
    }
    VIK_BUSY = false; vikingSync(); toast('바이킹을 다시 세웠습니다');
  }catch(e){ toast(e.message); }
  finally{ VIK_BUSY = false; vikCard(); }
}
document.addEventListener('click', e=>{
  const b = e.target.closest('[data-vik]'); if(!b) return;
  if(b.dataset.vik === 'up'){ if(!VIK_BUSY) vikFile.click(); return; }
  if(b.dataset.vik === 'clear'){ const t = vikTeam(); if(!t || !confirm(`${t}조의 배 모델을 지우고 공사 중으로 되돌릴까요?`)) return;
    api('/admin/viking_clear', {team:+t}, true).then(st=>{ applyState(st); vikingSync(); toast('공사 중으로 되돌렸습니다'); }).catch(er=> toast(er.message)); }
});
window.__vikReady = true; vikingSync();
''')

# ---- 2. state wiring: vikings come with every state, view changes re-sync ----
h = rep(h, "  SUBS = st.subs || []; if(st.now) SNOW = st.now;\n",
        "  SUBS = st.subs || []; if(st.now) SNOW = st.now;\n  if(!LOCAL){ VIK_STATE = st.vikings || {}; if(window.__vikReady){ VIKINGS = VIK_STATE; vikingSync(); } }\n")
h = rep(h, "const API = '/api/void';", "const API = '/api/void';\nlet VIK_STATE = {};   /* vikings from the server state, read before the island is built (2026-11-04) */")
h = rep(h, "let VIKINGS = {}, VIK_SHOWN", "let VIKINGS = VIK_STATE, VIK_SHOWN")
h = rep(h, "function rescan(revealIds, arrive){\n  rebuildIndex();", "function rescan(revealIds, arrive){\n  rebuildIndex(); if(window.__vikReady) vikingSync();")

# ---- 3. info card: the viking's card carries the upload block ----
m = re.search(r"\n  \$\('iIsl'\)\.innerHTML = \(INTERIORS\[b\.label\][^\n]*\n", h)
assert m
h = h[:m.end()] + "  if(b.mesh === viking) $('iIsl').insertAdjacentHTML('beforeend', vikCardHTML());\n" + h[m.end():]

# ---- 4. CSS (one line before </style></head><body>) ----
lines = h.split('\n'); k = lines.index('</style></head><body>')
lines[k-1] += '.vik{display:grid;gap:8px;border-top:1px solid var(--line);padding-top:12px}.vik small{font-size:12px;opacity:.72}.vik .vikf{margin:0;font-size:13px;font-weight:600;word-break:keep-all;overflow-wrap:anywhere}.enter.ghost{background:transparent;color:var(--ink,inherit);box-shadow:inset 0 0 0 1px var(--line)}.enter:disabled{opacity:.6}'
h = '\n'.join(lines)
dump(P, h)

# ---- 5. server ----
s = load(S)
assert 'viking' not in s
s = rep(s, "SPLAT_DIR = os.path.join(DATA_DIR, 'splats')\n",
        "SPLAT_DIR = os.path.join(DATA_DIR, 'splats')\nVIK_DIR = os.path.join(DATA_DIR, 'vikings')   # 2026-11-04: 조별 바이킹 배 모델 <team>.<stl|obj|glb>\nVIK_MAX = 20 * 1024 * 1024\nVIK_TYPES = {'stl': 'model/stl', 'obj': 'text/plain; charset=utf-8', 'glb': 'model/gltf-binary'}\n")
s = rep(s, "'quests': DB.get('quests', {}), 'pairs'", "'quests': DB.get('quests', {}), 'vikings': DB.get('vikings', {}), 'pairs'")
s = rep(s, "def fetch_thumb(scan_id):", '''def vik_ok(data, ext):
    """올린 파일이 그 확장자의 3D 모델처럼 생겼는지 (내용까지 검사하지는 않음)."""
    if ext == 'glb':
        return data[:4] == b'glTF'
    if ext == 'stl':
        if len(data) >= 84 and 84 + 50 * int.from_bytes(data[80:84], 'little') == len(data):
            return True
        return data.lstrip()[:5].lower() == b'solid' and b'facet' in data[:4096]
    if ext == 'obj':
        head = data[:200000]
        return bool(re.search(rb'(^|\\n)v\\s', head)) and bool(re.search(rb'(^|\\n)f\\s', data))
    return False


def vik_remove(team):
    for e in VIK_TYPES:
        try:
            os.remove(os.path.join(VIK_DIR, f'{team}.{e}'))
        except OSError:
            pass


def fetch_thumb(scan_id):''')
s = rep(s, "        m = re.fullmatch(r'/api/void/splat/([a-z0-9]{6,40})\\.txt', path)\n",
        "        m = re.fullmatch(r'/api/void/viking/(\\d{1,2})\\.(stl|obj|glb)', path)\n        if m:\n            fp = os.path.join(VIK_DIR, f'{int(m.group(1))}.{m.group(2)}')\n            if not os.path.isfile(fp):\n                return self.fail('올린 배 모델이 없습니다.', 404)\n            return self.send_bytes(open(fp, 'rb').read(), VIK_TYPES[m.group(2)], cache=True)\n        m = re.fullmatch(r'/api/void/splat/([a-z0-9]{6,40})\\.txt', path)\n")
s = rep(s, "    def do_POST(self):\n        path = urlparse(self.path).path\n        try:\n",
        "    def do_POST(self):\n        path = urlparse(self.path).path\n        if path == '/api/void/viking':   # 본문이 JSON이 아니라 파일 그대로\n            try:\n                return self.viking_upload()\n            except ValueError as e:\n                return self.fail(str(e))\n        try:\n")
s = rep(s, "            '/api/void/admin/skip': self.admin_skip,\n", "            '/api/void/admin/skip': self.admin_skip, '/api/void/admin/viking_clear': self.admin_viking_clear,\n")
s = rep(s, "    # 학생: 우리 조 처음부터", '''    # 학생: 바이킹 복구 — 조가 설계한 배 모델(STL/OBJ/GLB)을 올린다. 조마다 하나, 다시 올리면 바뀐다 (2026-11-04)
    def viking_upload(self):
        qs = parse_qs(urlparse(self.path).query)
        team = clean_team((qs.get('team') or [''])[0])
        ext = (qs.get('ext') or [''])[0].lower()
        if not team:
            raise ValueError('우리 조를 먼저 고르세요.')
        if ext not in VIK_TYPES:
            raise ValueError('STL, OBJ, GLB 파일만 올릴 수 있습니다.')
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > VIK_MAX:
            self.close_connection = True
            raise ValueError('20MB보다 작은 파일을 올려 주세요.')
        data = self.rfile.read(n)
        if len(data) != n or not vik_ok(data, ext):
            raise ValueError('3D 모델 파일 형식이 맞지 않습니다.')
        os.makedirs(VIK_DIR, exist_ok=True)
        fp = os.path.join(VIK_DIR, f'{team}.{ext}')
        with open(fp + '.tmp', 'wb') as f:
            f.write(data)
        with lock:
            for e in VIK_TYPES:
                if e != ext:
                    try:
                        os.remove(os.path.join(VIK_DIR, f'{team}.{e}'))
                    except OSError:
                        pass
            os.replace(fp + '.tmp', fp)
            DB.setdefault('vikings', {})[str(team)] = {'ext': ext, 'name': clean_text((qs.get('name') or [''])[0], 60), 'size': n, 't': now_ms()}
            save()
            self.send_json(state())

    # 운영자: 한 조의 바이킹 배 모델을 지우고 공사 중으로 되돌린다
    def admin_viking_clear(self, b):
        team = clean_team(b.get('team'))
        if not team:
            raise ValueError('조 번호가 없습니다.')
        with lock:
            DB.setdefault('vikings', {}).pop(str(team), None)
            vik_remove(team)
            save()
            self.send_json(state())

    # 학생: 우리 조 처음부터''')
s = rep(s, "            DB.setdefault('quests', {}).pop(str(team), None)\n            save()\n",
        "            DB.setdefault('quests', {}).pop(str(team), None)\n            DB.setdefault('vikings', {}).pop(str(team), None)\n            vik_remove(team)\n            save()\n")
s = rep(s, "            DB['quests'] = {}\n            DB['notice'] = None\n",
        "            DB['quests'] = {}\n            for t in list(DB.get('vikings', {})):\n                vik_remove(t)\n            DB['vikings'] = {}\n            DB['notice'] = None\n")
dump(S, s)

# ---- 6. nginx: files up to 20 MB through /api/void/ ----
n = load(N)
n = rep(n, "        proxy_pass http://127.0.0.1:8096;\n        proxy_http_version 1.1;\n        proxy_set_header Host $host;\n        client_max_body_size 6m;",
        "        proxy_pass http://127.0.0.1:8096;\n        proxy_http_version 1.1;\n        proxy_set_header Host $host;\n        client_max_body_size 22m;   # 2026-11-04 바이킹 배 모델 업로드(20MB)")
dump(N, n)
print('patched')
