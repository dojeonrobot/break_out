# 2026-11-09 관리자 대시보드 「기록 좌표」: 캠퍼스 기록(z1~z3)마다 위도·경도를 바꾸는 칸. 기본값 = 페이지 MISSIONS에 적힌 값.
# 서버 DB['coords'] = {mission: {lat, lng}} (바꾼 것만), state()로 모든 태블릿에 내려감. 한 번만 적용.
import io, re, sys
ROOT = r'C:\Users\dlgus\break_out'
P = ROOT + r'\chapter05\index.html'
S = ROOT + r'\server\ch5_void_server.py'


def sub1(src, old, new, label):
    n = src.count(old)
    if n != 1:
        sys.exit(f'앵커 {label}: {n}곳')
    return src.replace(old, new)


# ---------- server ----------
s = io.open(S, encoding='utf-8', newline='').read().replace('\r\n', '\n')
if 'admin_coords' in s:
    sys.exit('서버: 이미 적용됨')
s = sub1(s, "'quests': {}, 'notice': None}", "'quests': {}, 'notice': None, 'coords': {}}", 'fresh_db')
s = sub1(s, "'notice': DB.get('notice'), 'now': now_ms()}", "'notice': DB.get('notice'), 'coords': DB.get('coords', {}), 'now': now_ms()}", 'state')
s = sub1(s, "    # 운영자: 링크가 변환되면 바로 복구됨으로 할지(auto)\n",
"""    # 운영자: 캠퍼스 기록 좌표 바꾸기 (2026-11-09). clear면 페이지 기본값으로. 바꾼 것만 저장한다.
    def admin_coords(self, b):
        mid = str(b.get('mission') or '')
        if not MISSION_ID.match(mid):
            raise ValueError('기록 이름이 올바르지 않습니다.')
        with lock:
            cs = DB.setdefault('coords', {})
            if b.get('clear'):
                cs.pop(mid, None)
            else:
                try:
                    lat, lng = float(b.get('lat')), float(b.get('lng'))
                except (TypeError, ValueError):
                    raise ValueError('위도·경도는 숫자로 적어 주세요.')
                if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                    raise ValueError('위도는 -90~90, 경도는 -180~180 사이여야 합니다.')
                cs[mid] = {'lat': round(lat, 7), 'lng': round(lng, 7), 't': now_ms()}
            save()
            self.send_json(state())

    # 운영자: 링크가 변환되면 바로 복구됨으로 할지(auto)
""", 'admin_auto')
s = sub1(s, "'/api/void/admin/auto': self.admin_auto,", "'/api/void/admin/auto': self.admin_auto, '/api/void/admin/coords': self.admin_coords,", 'routes')

# ---------- page ----------
h = io.open(P, encoding='utf-8', newline='').read().replace('\r\n', '\n')
if 'COORD_DEF' in h:
    sys.exit('페이지: 이미 적용됨')
lines = h.split('\n')
i = next(k for k, l in enumerate(lines) if l.startswith('const MISSIONS = ['))
lines.insert(i + 1, "/* record coordinates the admin can change on the dashboard (user, 2026-11-09): the values written above are the defaults; the server keeps only the changed ones */\n"
                    "const COORD_DEF = Object.fromEntries(MISSIONS.filter(m=> m.lat != null).map(m=> [m.id, {lat:m.lat, lng:m.lng}])); let COORDS = {};")
h = '\n'.join(lines)

h = sub1(h, "const MISSION_E = M;\n",
"const MISSION_E = M;\n"
"function coordsApply(c){ c = (c && typeof c === 'object') ? c : {}; const j = JSON.stringify(c); if(j === coordsApply.j) return false; coordsApply.j = j; COORDS = c;\n"
"  [MISSIONS, M].forEach(list=> list.forEach(m=>{ const d = COORD_DEF[m.id]; if(!d) return; const v = c[m.id], ok = v && isFinite(+v.lat) && isFinite(+v.lng); m.lat = ok ? +v.lat : d.lat; m.lng = ok ? +v.lng : d.lng; }));\n"
"  return true; }\n"
"try{ coordsApply(JSON.parse(localStorage.getItem('void-coords') || '{}')); }catch(e){}   /* last coordinates this device saw, until the server answers */\n", 'MISSION_E')

h = sub1(h, "  noticeApply(st.notice);\n",
"  noticeApply(st.notice);\n"
"  if(coordsApply(st.coords)){ try{ localStorage.setItem('void-coords', JSON.stringify(COORDS)); }catch(e){} if(typeof myPos !== 'undefined' && myPos) try{ showMeCoord(); }catch(e){} }\n", 'applyState')

CARD = """        <section class="card"><h3>기록 좌표</h3>
          ${MISSIONS.filter(m=> COORD_DEF[m.id]).map(m=>{ const d = COORD_DEF[m.id], ch = !!COORDS[m.id]; return `<div class="crow">
            <div class="cn"><b>${esc(m.name)}</b>${ch ? `<button type="button" class="mini" data-cdef="${esc(m.id)}">기본값으로</button>` : ''}</div>
            <div class="cin"><label><small>위도</small><input type="text" inputmode="decimal" autocomplete="off" data-keep="clat-${esc(m.id)}" value="${m.lat.toFixed(6)}" aria-label="${esc(m.name)} 위도"></label>
              <label><small>경도</small><input type="text" inputmode="decimal" autocomplete="off" data-keep="clng-${esc(m.id)}" value="${m.lng.toFixed(6)}" aria-label="${esc(m.name)} 경도"></label>
              <button type="button" class="mini on" data-csave="${esc(m.id)}">저장</button></div>
            ${ch ? `<small class="cdef">기본값 ${d.lat.toFixed(6)}, ${d.lng.toFixed(6)}</small>` : ''}</div>`; }).join('')}</section>
"""
h = sub1(h, "        <section class=\"card\"><h3>보기</h3>\n", CARD + "        <section class=\"card\"><h3>보기</h3>\n", 'card')

# keep what the admin is typing when the dashboard re-renders on a state poll
h = sub1(h, "function renderAdmin(){ const b = $('adminBody'); if(b && !$('adminDlg').hidden) b.innerHTML = adminHTML(); }",
"function renderAdmin(){ const b = $('adminBody'); if(!b || $('adminDlg').hidden) return;\n"
"  const keep = {}, fk = document.activeElement && b.contains(document.activeElement) && document.activeElement.dataset ? document.activeElement.dataset.keep : null;\n"
"  b.querySelectorAll('input[data-keep]').forEach(i=>{ if(i.dataset.dirty) keep[i.dataset.keep] = i.value; });\n"
"  b.innerHTML = adminHTML();\n"
"  b.querySelectorAll('input[data-keep]').forEach(i=>{ if(i.dataset.keep in keep){ i.value = keep[i.dataset.keep]; i.dataset.dirty = '1'; } if(fk && i.dataset.keep === fk) i.focus(); }); }", 'renderAdmin')

h = sub1(h, "  const np = e.target.closest('[data-npre]');\n",
"  const cs = e.target.closest('[data-csave]'); if(cs){ e.stopPropagation(); saveCoord(cs.dataset.csave); return; }\n"
"  const cd = e.target.closest('[data-cdef]'); if(cd){ e.stopPropagation(); saveCoord(cd.dataset.cdef, true); return; }\n"
"  const np = e.target.closest('[data-npre]');\n", 'click')

h = sub1(h, "async function sendNotice(text){",
"""/* admin: change one record's coordinates (or put the default back); every tablet picks it up with its next state poll (user, 2026-11-09) */
document.addEventListener('input', e=>{ const i = e.target; if(!(i instanceof HTMLInputElement) || !i.dataset.keep || !/^cl(at|ng)-/.test(i.dataset.keep)) return; i.dataset.dirty = '1';
  const two = i.value.match(/(-?\\d+(?:\\.\\d+)?)\\s*[,\\s]\\s*(-?\\d+(?:\\.\\d+)?)/); if(!two) return;   /* "37.29, 126.84" pasted into one box fills both */
  const id = i.dataset.keep.slice(5), la = document.querySelector(`[data-keep="clat-${id}"]`), ln = document.querySelector(`[data-keep="clng-${id}"]`); if(!la || !ln) return;
  la.value = two[1]; ln.value = two[2]; la.dataset.dirty = ln.dataset.dirty = '1'; });
async function saveCoord(id, clear){
  const m = MISSIONS.find(x=> x.id === id), d = COORD_DEF[id]; if(!m || !d) return;
  let body = {mission:id, clear:true};
  if(!clear){ const la = document.querySelector(`[data-keep="clat-${id}"]`), ln = document.querySelector(`[data-keep="clng-${id}"]`);
    const lat = parseFloat((la && la.value || '').trim()), lng = parseFloat((ln && ln.value || '').trim());
    if(!isFinite(lat) || !isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180){ toast('위도·경도를 숫자로 적어 주세요'); return; }
    const km = Math.hypot((lat - DATA.origin[0])*110.54, (lng - DATA.origin[1])*111.32*Math.cos(lat*Math.PI/180));
    if(km > 3 && !confirm(`캠퍼스에서 ${km.toFixed(1)}km 떨어진 곳입니다. 위도와 경도가 바뀌지 않았는지 확인해 주세요. 그래도 저장할까요?`)) return;
    body = {mission:id, lat, lng}; }
  try{ STATE_VER = -1; const st = await api('/admin/coords', body, true);
    document.querySelectorAll(`[data-keep="clat-${id}"],[data-keep="clng-${id}"]`).forEach(i=> delete i.dataset.dirty);
    applyState(st); renderAdmin(); toast(clear ? `${m.name} 좌표를 기본값으로 돌렸습니다` : `${m.name} 좌표를 저장했습니다`); }
  catch(err){ toast(LOCAL ? '서버에 연결되지 않아 저장할 수 없습니다' : err.message); } }
async function sendNotice(text){""", 'sendNotice')

# CSS: appended to the notice-input rule line (one line, like the rest of this block)
css = (" .adm .crow{display:grid;gap:6px;padding:10px 0;border-top:1px solid var(--line)} .adm .crow:first-of-type{border-top:0;padding-top:2px}"
       " .adm .crow .cn{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:13px}"
       " .adm .crow .cin{display:grid;grid-template-columns:1fr 1fr auto;gap:6px;align-items:end}"
       " .adm .crow label{display:grid;gap:3px;min-width:0} .adm .crow label small{font-size:11px;color:var(--muted)}"
       " .adm .crow input{box-sizing:border-box;width:100%;min-width:0;padding:8px 9px;border-radius:8px;border:1px solid var(--line);background:var(--panel-solid);color:var(--fg);font:13px var(--mono);font-variant-numeric:tabular-nums}"
       " .adm .crow input:focus-visible{outline:2px solid var(--accent);outline-offset:1px} .adm .crow .cin .mini{min-height:36px;white-space:nowrap}"
       " .adm .crow .cdef{font:11px var(--mono);color:var(--muted)}"
       " @media (pointer:coarse){.adm .crow input,.adm .crow .cin .mini{min-height:44px}}")
lines = h.split('\n')
k = next(n for n, l in enumerate(lines) if l.startswith('#noticeIn{'))
lines[k] = lines[k] + css
h = '\n'.join(lines)

io.open(S, 'w', encoding='utf-8', newline='').write(s)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('ok')
