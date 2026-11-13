# ch5_audit_paths.py 결과(JSON)를 읽어 길 끝·교차·겹침·끊김·길 위 물체·벽 통과를 정리하고 전체 지도를 그린다.
# python scripts/pending/ch5_audit_paths_report.py <audit.json> <지도 png>
import json, sys, math
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
D = json.load(open(sys.argv[1], encoding='utf-8')); OUT = sys.argv[2]
R = D['routes']; IB = [b for b in D['ib'] if b]
def rid(ri): r = R[ri]; return f"{r['name']}#{r['k']}"
def seg_d(p, a, b):
    dx, dz = b[0]-a[0], b[1]-a[1]; L = dx*dx + dz*dz or 1e-9; u = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dz)/L)); return math.hypot(p[0]-a[0]-dx*u, p[1]-a[1]-dz*u)
def route_d(p, r):
    P = r['pts']; best = 1e9; bi = 0
    for i in range(len(P)-1):
        d = seg_d(p, P[i], P[i+1])
        if d < best: best, bi = d, i
    return best, bi
def arc(r):
    P = r['pts']; s = [0]
    for i in range(1, len(P)): s.append(s[-1] + math.hypot(P[i][0]-P[i-1][0], P[i][1]-P[i-1][1]))
    return s
ARC = [arc(r) for r in R]
def near_ib(p):
    best = None
    for b in IB:
        d = math.hypot(p[0]-b['cx'], p[1]-b['cz']) - b['r']
        if best is None or d < best[0]: best = (d, b['label'])
    return best
print('== 길 목록', len(R));
for ri, r in enumerate(R):
    P = r['pts']; print(f"{ri:>2} {rid(ri):<22} 폭 {r['hw']*2:4.1f} 길이 {ARC[ri][-1]:6.1f}  ({P[0][0]:.0f},{P[0][1]:.0f}) → ({P[-1][0]:.0f},{P[-1][1]:.0f}) {'' if r['shown'] else '[숨김]'} {r['owner']}")
# --- A. 끝점: 다른 길에 닿는가 / 시설에 닿는가
print('\n== A. 길 끝점 (다른 길과의 틈, 가장 가까운 시설)')
ends = []
for ri, r in enumerate(R):
    if not r['shown']: continue
    for which, p in (('시작', r['pts'][0]), ('끝', r['pts'][-1])):
        best = (1e9, -1)
        for rj, q in enumerate(R):
            if rj == ri or not q['shown']: continue
            d, _ = route_d(p, q); gap = d - q['hw']
            if gap < best[0]: best = (gap, rj)
        ib = near_ib(p); ends.append((ri, which, p, best, ib))
for ri, which, p, best, ib in ends:
    gap, rj = best; flag = ''
    if gap > 0.3 and ib[0] > 6: flag = '  ◀ 길에도 시설에도 안 닿음' if gap > 8 else '  ◀ 다른 길과 틈'
    elif 0.3 < gap <= 8: flag = '  ◁ 가까운 길과 틈(시설에는 닿음)'
    if flag or ARC[ri][-1] < 12: print(f"{rid(ri):<22} {which} ({p[0]:6.1f},{p[1]:6.1f}) 가장 가까운 길 {rid(rj)} 틈 {gap:5.1f} / 시설 {ib[1]} {ib[0]:5.1f}{flag}{'  (짧은 길 ' + format(ARC[ri][-1], '.1f') + ')' if ARC[ri][-1] < 12 else ''}")
# --- B. 연결 성분
par = list(range(len(R)))
def find(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for ri, r in enumerate(R):
    for rj in range(ri+1, len(R)):
        q = R[rj]; touch = False
        for p in (r['pts'][0], r['pts'][-1]):
            if route_d(p, q)[0] < q['hw'] + r['hw']*0.5 + 0.5: touch = True
        for p in (q['pts'][0], q['pts'][-1]):
            if route_d(p, r)[0] < r['hw'] + q['hw']*0.5 + 0.5: touch = True
        if not touch:
            for p in r['pts'][::2]:
                if route_d(p, q)[0] < 0.6*(r['hw'] + q['hw']): touch = True; break
        if touch: par[find(ri)] = find(rj)
comp = defaultdict(list)
for ri in range(len(R)): comp[find(ri)].append(ri)
main = find(0); print('\n== B. 정문 큰길과 이어지지 않은 길 묶음')
for c, m in comp.items():
    if c != main: print('  ', [rid(x) for x in m], '첫 점', [round(v) for v in R[m[0]]['pts'][0][:2]], '시설', near_ib(R[m[0]]['pts'][0]))
# --- C. 교차·겹침 (끝점 근처 합류는 제외)
print('\n== C. 길끼리 교차·겹침 (합류점 밖)')
for ri, r in enumerate(R):
    for rj in range(ri+1, len(R)):
        q = R[rj]; run = []
        for i, p in enumerate(r['pts']):
            d, j = route_d(p, q)
            if d < (r['hw'] + q['hw'])*0.85: run.append((i, j, d))
        if not run: continue
        sa, sb = ARC[ri], ARC[rj]
        # 합류점: 한쪽 길의 끝에서 20 안이면 정상 합류로 본다
        inner = [(i, j, d) for i, j, d in run if min(sa[i], sa[-1]-sa[i]) > 18 and min(sb[j], sb[-1]-sb[j]) > 18]
        ln = sa[run[-1][0]] - sa[run[0][0]]
        if inner:
            i0, i1 = inner[0][0], inner[-1][0]; p = r['pts'][inner[len(inner)//2][0]]
            print(f"  교차/겹침 {rid(ri)} × {rid(rj)} 근처 ({p[0]:.0f},{p[1]:.0f}) 겹친 길이 {sa[i1]-sa[i0]:.0f} (두 길 모두 끝에서 18 넘게 떨어진 곳)")
        elif ln > 2.2*(r['hw'] + q['hw']) + 14:
            p = r['pts'][run[len(run)//2][0]]; print(f"  나란히 겹침 {rid(ri)} × {rid(rj)} 근처 ({p[0]:.0f},{p[1]:.0f}) 길이 {ln:.0f}")
# --- D. 길 위·길을 가로지르는 물체
print('\n== D. 길 위에 있거나 길을 가로지르는 물체 (광선)')
grp = defaultdict(list)
for h in D['hits']:
    d = h['d']; grp[(h['ri'], d['label'], d['col'], d['geo'], d['name'], d['inst'])].append(h)
rows = []
for k, hs in grp.items():
    hs.sort(key=lambda h: h['i']); xs = [h['x'] for h in hs]; zs = [h['z'] for h in hs]
    kinds = ''.join(sorted(set(h['k'] for h in hs))); lanes = sorted(set(h['lane'] for h in hs)); d = hs[0]['d']
    rows.append((k[0], len(hs), kinds, lanes, (min(xs), max(xs), min(zs), max(zs)), max(h['y'] for h in hs), d, hs[0]['i'], hs[-1]['i']))
rows.sort(key=lambda r: (r[0], r[7]))
for ri, n, kinds, lanes, box, ymax, d, i0, i1 in rows:
    print(f"  {rid(ri):<22} 표본 {i0}~{i1} 히트 {n:>3} [{kinds}] 차선 {lanes} x {box[0]:.0f}~{box[1]:.0f} z {box[2]:.0f}~{box[3]:.0f} 높이 {ymax:.1f} | 시설 '{d['label']}' 색 #{d['col']} {d['geo']} 크기 {d['sz']} 바닥 {d['base']} {d['name']} {d['chain']}{' (인스턴스)' if d['inst'] else ''}")
# --- E. 길 밑의 걷기 격자
print('\n== E. 그려진 길인데 걷지 못하는 곳 / 길이 막힘 칸 위를 지나는 곳')
runs = defaultdict(list)
for ri, i, lane, x, z, a, path, blk in D['under']:
    kind = '못 걸음' if blk else ('막힘 칸 위(통과해서 걸음)' if a and path else ('길 판정 아님' if not path else None))
    if kind: runs[(ri, kind)].append((i, lane, x, z))
for (ri, kind), v in sorted(runs.items()):
    idx = sorted(set(i for i, *_ in v)); spans = []; s = idx[0]; p = idx[0]
    for i in idx[1:]:
        if i > p + 2: spans.append((s, p)); s = i
        p = i
    spans.append((s, p)); P = R[ri]['pts']
    print(f"  {rid(ri):<22} {kind}: " + ', '.join(f"표본 {a}~{b} ({P[a][0]:.0f},{P[a][1]:.0f})→({P[b][0]:.0f},{P[b][1]:.0f}) {ARC[ri][b]-ARC[ri][a]:.0f}m" for a, b in spans[:8]) + (' …' if len(spans) > 8 else '') + f"  차선 {sorted(set(l for _, l, *_ in v))}")
# --- 지도
S = 2.0; X0, Z0, Wd, Hd = -640, -660, 1280, 1320; im = Image.new('RGB', (int(Wd*S), int(Hd*S)), (246, 247, 242)); dr = ImageDraw.Draw(im)
try: ft = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15); fs = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 12)
except Exception: ft = fs = ImageFont.load_default()
T = lambda x, z: ((x - X0)*S, (z - Z0)*S)
for gx in range(-600, 601, 100):
    dr.line([T(gx, Z0), T(gx, Z0 + Hd)], fill=(225, 226, 220)); dr.text(T(gx + 2, Z0 + 2), str(gx), fill=(150, 150, 150), font=fs)
for gz in range(-600, 601, 100):
    dr.line([T(X0, gz), T(X0 + Wd, gz)], fill=(225, 226, 220)); dr.text(T(X0 + 2, gz + 2), str(gz), fill=(150, 150, 150), font=fs)
for b in IB:
    x, y = T(b['cx'], b['cz']); r = b['r']*S; dr.ellipse([x-r, y-r, x+r, y+r], outline=(120, 170, 120) if b['c'] != 'place' else (150, 150, 200), width=2); dr.text((x - 30, y - 8), b['label'], fill=(60, 90, 60), font=fs)
COL = {'public-path': (200, 150, 90), 'facility-spur': (230, 120, 60), 'queue-arrival': (120, 120, 220), 'queue-to-gate': (90, 160, 220)}
for ri, r in enumerate(R):
    c = COL.get(r['name'], (170, 90, 170)); pts = [T(p[0], p[1]) for p in r['pts']]; dr.line(pts, fill=c, width=max(2, int(r['hw']*2*S)), joint='curve')
for ri, r in enumerate(R):
    pts = [T(p[0], p[1]) for p in r['pts']]; dr.line(pts, fill=(70, 50, 30), width=1); m = pts[len(pts)//2]; dr.text((m[0] + 4, m[1] - 6), str(ri), fill=(0, 0, 0), font=fs)
for h in D['hits']:
    x, y = T(h['x'], h['z']); dr.ellipse([x-3, y-3, x+3, y+3], fill=(220, 30, 30) if h['k'] == 'h' else (240, 150, 0))
for ri, i, lane, x, z, a, path, blk in D['under']:
    if blk: px, py = T(x, z); dr.rectangle([px-2, py-2, px+2, py+2], fill=(0, 0, 0))
im.save(OUT); print('\nmap', OUT)
