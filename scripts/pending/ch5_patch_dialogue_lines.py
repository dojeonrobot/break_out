# 2026-11-11 대사 줄바꿈(사용자: 한 문장은 무조건 한 줄에): 대사 창(#vnText, #voidTxt)은 문장마다 줄을 바꾸고 문장 안에서는 줄이 넘어가지 않는다.
# 한 줄에 안 들어가는 문장은 글자를 줄여 맞추고(바닥 13px), 그래도 넘치면 쉼표 뒤에서만 나눈다. 타자 효과 중에도 줄 위치가 움직이지 않게 남은 글자는 숨긴 채 자리를 잡아 둔다.
# 사용: python ch5_patch_dialogue_lines.py [사본경로]
import pathlib, sys
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05' / 'index.html'
s = P.read_bytes().decode('utf-8'); assert '\r\n' not in s
assert 'vsen' not in s and 'dlShow' not in s

def swap(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)

# CSS at the top level, just before the style block closes (not inside any @media)
swap('</style></head><body>', '''.vsen{display:block;width:max-content;max-width:none;white-space:nowrap}
.vsen.vwrap{width:auto;white-space:normal}
.vhid{visibility:hidden;font-style:inherit}
</style></head><body>''')

swap('function vnNext(){\n', r'''// ---- dialogue lines: one sentence per line and a sentence never wraps (user, 2026-11-11) ----
const dlEsc = t=> t.replace(/[&<>]/g, c=> ({'&':'&amp;', '<':'&lt;', '>':'&gt;'}[c]));
function dlSplit(text){ const out = []; let cur = ''; for(let i = 0; i < text.length; i++){ const ch = text[i]; cur += ch; if('.!?'.includes(ch) && /\s/.test(text[i + 1] || '')){ while(/\s/.test(text[i + 1] || '')) i++; out.push(cur); cur = ''; } } if(cur.trim()) out.push(cur); if(!out.length) return [text];
  // a very short sentence does not get a line of its own: it shares one with its neighbour (user, 2026-11-11: "안녕! 난 보이드." on one line)
  const SHORT = 8, MAX = 34, lines = [];
  for(const t of out){ const last = lines[lines.length - 1]; if(last !== undefined && last.length <= SHORT && (last + ' ' + t).length <= MAX) lines[lines.length - 1] = last + ' ' + t; else lines.push(t); }
  if(lines.length > 1 && lines[lines.length - 1].length <= SHORT && (lines[lines.length - 2] + ' ' + lines[lines.length - 1]).length <= MAX){ const t = lines.pop(); lines[lines.length - 1] += ' ' + t; }
  return lines; }
function dlPlan(p, text){
  const key = text + '|' + innerWidth + 'x' + innerHeight + '|' + p.className; if(p._dl && p._dl.key === key) return p._dl;
  let parts = dlSplit(text), wrap = false; const draw = ()=>{ p.innerHTML = parts.map(t=> `<span class="vsen">${dlEsc(t)}</span>`).join(''); }, widest = ()=> Math.max(0, ...[...p.children].map(c=> c.offsetWidth));
  p.style.fontSize = ''; draw(); const base = parseFloat(getComputedStyle(p).fontSize) || 16, avail = p.clientWidth, floor = Math.min(base, 13);
  if(!avail) return {key:'', parts, size:0, total:parts.reduce((n, t)=> n + t.length, 0), wrap};   // not laid out yet: no fitting, nothing cached
  let size = base, w = widest();
  if(w > avail && base*avail/w < floor){   // even the smallest size is too wide: break those sentences after a comma, nowhere else
    parts = parts.flatMap((t, i)=>{ const cw = p.children[i].offsetWidth; if(cw*floor/base <= avail) return [t]; const max = Math.max(8, Math.floor(avail/(cw*floor/base)*t.length) - 1), out = []; let cur = '';
      t.split(/(?<=,)\s+/).forEach(c=>{ if(cur && (cur + ' ' + c).length > max){ out.push(cur); cur = c; } else cur = cur ? cur + ' ' + c : c; }); if(cur) out.push(cur); return out; });
    draw(); w = widest(); }
  if(w > avail){ size = Math.max(floor, Math.floor(base*avail/w*10)/10); p.style.fontSize = size + 'px'; if(widest() > avail) wrap = true; }
  return p._dl = {key, parts, size:size === base ? 0 : size, total:parts.reduce((n, t)=> n + t.length, 0), wrap};
}
function dlShow(p, text, k){ const d = dlPlan(p, text); p.style.fontSize = d.size ? d.size + 'px' : ''; let left = k;
  p.innerHTML = d.parts.map(t=>{ const v = Math.max(0, Math.min(t.length, left)); left -= t.length; return `<span class="vsen${d.wrap ? ' vwrap' : ''}">${dlEsc(t.slice(0, v))}<i class="vhid">${dlEsc(t.slice(v))}</i></span>`; }).join(''); return d.total; }
function vnNext(){
''')
# character dialogue
swap("vn.typing = null; $('vnText').textContent = vn.full; delete $('vn').dataset.typing; return; }", "vn.typing = null; dlShow($('vnText'), vn.full, 1e9); delete $('vn').dataset.typing; return; }")
swap("vn.typing = setInterval(()=>{ k++; p.textContent = L.text.slice(0, k); if(k >= L.text.length){", "const vnTotal = dlShow(p, L.text, 0); vn.typing = setInterval(()=>{ k++; dlShow(p, L.text, k); if(k >= vnTotal){")
# the void's lines
swap("voidTyping = setInterval(()=>{ k++; p.textContent = text.slice(0, k); if(k >= text.length){", "const voidTotal = dlShow(p, text, 0); voidTyping = setInterval(()=>{ k++; dlShow(p, text, k); if(k >= voidTotal){")
swap("$('voidTxt').textContent = voidHist[i];", "dlShow($('voidTxt'), voidHist[i], 1e9);")
swap("$('voidTxt').textContent = voidFull; } else $('voidTxt').textContent = voidHist[voidView];", "dlShow($('voidTxt'), voidFull, 1e9); } else dlShow($('voidTxt'), voidHist[voidView], 1e9);")
swap("voidTyping = null; $('voidTxt').textContent = voidFull; delete $('voidVn').dataset.typing; return; }", "voidTyping = null; dlShow($('voidTxt'), voidFull, 1e9); delete $('voidVn').dataset.typing; return; }")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else P
OUT.write_bytes(s.encode('utf-8')); print('patched', OUT, len(s))
