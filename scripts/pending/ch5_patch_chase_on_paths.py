# 2026-11-12 (사용자 "네이티가 움직이는 경로가 벽을 뚫고 다닌다"): 추격 경로가 길 그래프의 긴 직선(100m짜리 두 개)이라 잔디·시설을 가로질렀다.
#   걸을 수 있는 칸(2 m)만 밟는 최단 경로를 찾되 길 밖은 5배 비싸게 쳐서 되도록 길로 가게 하고, 막히지 않는 곳에서만 곧게 편다.
#   이미 옛 판(BFS)을 넣은 파일에도, 안 넣은 파일에도 돌릴 수 있다.
import pathlib, re
P = pathlib.Path(__file__).resolve().parents[2] / 'chapter05/index.html'
s = P.read_bytes().decode('utf-8').replace('\r\n', '\n')
FN = r'''/* a route a child can walk: Dijkstra over walkable cells (2 m), off-pavement cells cost 5x, then pulled straight only where nothing is in the way */
function pavedRoute(sx, sz, tx, tz){ if(!WGRID) WGRID = buildWalkGrid(); const S = 2, free = (x, z)=> !walkBlocked(x, z), K2 = (i, j)=> (i + 2048)*4096 + (j + 2048);
  const snap = (x, z)=>{ const i0 = Math.round(x/S), j0 = Math.round(z/S); for(let r = 0; r < 40; r++) for(let di = -r; di <= r; di++) for(let dj = -r; dj <= r; dj++){ if(Math.max(Math.abs(di), Math.abs(dj)) !== r) continue; if(free((i0 + di)*S, (j0 + dj)*S)) return [i0 + di, j0 + dj]; } return null; };
  const a = snap(sx, sz), b = snap(tx, tz); if(!a || !b) return null; const dist = new Map([[K2(a[0], a[1]), 0]]), prev = new Map([[K2(a[0], a[1]), null]]), heap = [[0, a[0], a[1]]];
  const push = e=>{ heap.push(e); let k = heap.length - 1; while(k){ const p = (k - 1) >> 1; if(heap[p][0] <= heap[k][0]) break; [heap[p], heap[k]] = [heap[k], heap[p]]; k = p; } };
  const pop = ()=>{ const top = heap[0], last = heap.pop(); if(heap.length){ heap[0] = last; let k = 0; for(;;){ let m = k; const l = 2*k + 1, r = l + 1; if(l < heap.length && heap[l][0] < heap[m][0]) m = l; if(r < heap.length && heap[r][0] < heap[m][0]) m = r; if(m === k) break; [heap[m], heap[k]] = [heap[k], heap[m]]; k = m; } } return top; };
  let hit = false, guard = 0;
  while(heap.length && guard++ < 600000){ const [d, i, j] = pop(); if(d > dist.get(K2(i, j))) continue; if(i === b[0] && j === b[1]){ hit = true; break; }
    for(const [di, dj] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){ const x = (i + di)*S, z = (j + dj)*S; if(!free(x, z)) continue; const nd = d + Math.hypot(di, dj)*(onPath(x, z) ? 1 : 5), k = K2(i + di, j + dj); if(nd < (dist.has(k) ? dist.get(k) : Infinity)){ dist.set(k, nd); prev.set(k, [i, j]); push([nd, i + di, j + dj]); } } }
  if(!hit) return null; let cells = [], c = b; while(c){ cells.push([c[0]*S, c[1]*S]); c = prev.get(K2(c[0], c[1])); } cells.reverse();
  const clear = (p, r)=>{ const both = onPath(p[0], p[1]) && onPath(r[0], r[1]), L = Math.hypot(r[0] - p[0], r[1] - p[1]), n = Math.ceil(L); for(let k = 1; k < n; k++){ const x = p[0] + (r[0] - p[0])*k/n, z = p[1] + (r[1] - p[1])*k/n; if(!free(x, z) || (both && !onPath(x, z))) return false; } return true; };
  const out = [cells[0]]; let i = 0; while(i < cells.length - 1){ let j = Math.min(cells.length - 1, i + 30); while(j > i + 1 && !clear(cells[i], cells[j])) j--; out.push(cells[j]); i = j; } return out; }
'''
if 'function pavedRoute' in s:
    a = s.index('/* a route that stays on the pavement'); b = s.index('function chasePath(){'); s = s[:a] + FN + s[b:]
else:
    assert s.count('function chasePath(){ if(chasePath.R) return chasePath.R;') == 1
    s = s.replace('function chasePath(){ if(chasePath.R) return chasePath.R;', FN + 'function chasePath(){ if(chasePath.R) return chasePath.R;')
    o = "let pts = qRoute(a[0], a[1], e[0], e[1], true).map(p=> [p[0], p[1]]);"; assert s.count(o) == 1
    s = s.replace(o, "let pts = pavedRoute(a[0], a[1], e[0], e[1]) || qRoute(a[0], a[1], e[0], e[1], true).map(p=> [p[0], p[1]]);")
if '__chaseRoute' not in s:
    o = "window.__chase = ()=> chase ?"; assert s.count(o) == 1; s = s.replace(o, "window.__chaseRoute = ()=> chasePath();\n" + o)
o = 'const CHASE = {lead:12, lose:36,'
if o in s: s = s.replace(o, 'const CHASE = {lead:12, lose:42,')   # 경로가 498 → 551로 길어져 실패 거리도 늘림(자동 조종 기준 가장 멀어진 거리 27 / 42)
P.write_bytes(s.encode('utf-8')); print('ok')
