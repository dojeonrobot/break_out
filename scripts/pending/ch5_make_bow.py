# 사과 자세 그림 만들기: 선 자세 사과 그림(zero_sorry.png·rico_sorry.png)에서 벌린 팔을 지우고, 두 손을 앞에 모은 팔을 그려 넣고, 고개를 살짝 숙인다.
#  python -X utf8 scripts/pending/ch5_make_bow.py <내보낼 폴더>   → zero_bow.png, rico_bow.png (페이지 폴더에는 쓰지 않는다)
import pathlib, sys, math
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]; CH = ROOT / 'chapter05/img/chars'; OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True); K = 4
P = {
 'zero': dict(L=((146, 288), (131, 458)), R=((231, 288), (250, 458)), y0=270, y1=562, keep=None, head=250, pivot=(189, 250), tilt=-6, drop=9,
              main=(190, 380), shade=(128, 365), cuff=(180, 458), skin=(45, 478), sL=(152, 304), eL=(127, 384), wL=(170, 424), sR=(226, 304), eR=(254, 386), wR=(210, 424), hand=(190, 431), w=34),
 'rico': dict(L=((156, 262), (139, 440)), R=((250, 262), (271, 425)), y0=244, y1=532, keep='hair', head=226, pivot=(203, 226), tilt=-5, drop=8,
              main=(180, 340), shade=(140, 350), cuff=(200, 412), skin=(40, 462), sL=(164, 282), eL=(134, 356), wL=(184, 392), sR=(246, 282), eR=(280, 358), wR=(226, 392), hand=(205, 399), w=36)}
def lerp_x(seg, y): (x0, y0), (x1, y1) = seg; return x0 + (x1 - x0)*(y - y0)/(y1 - y0)
def near(c, d, tol=60): return sum(abs(a - b) for a, b in zip(c[:3], d[:3])) < tol
def make(name):
    p = P[name]; src = Image.open(CH / f'{name}_sorry.png').convert('RGBA'); w, h = src.size; px = src.load()
    col = {k: px[p[k][0], p[k][1]][:3] for k in ('main', 'shade', 'cuff', 'skin')}
    body = src.copy(); bp = body.load()
    for y in range(p['y0'], p['y1']):   # 벌린 팔 지우기: 몸통 선 바깥
        xl, xr = lerp_x(p['L'], min(y, p['L'][1][1])), lerp_x(p['R'], min(y, p['R'][1][1]))
        for x in range(w):
            if xl <= x <= xr: continue
            c = bp[x, y]
            if c[3] and p['keep'] == 'hair' and not (near(c, col['main'], 90) or near(c, col['shade'], 90) or near(c, col['cuff'], 80) or near(c, col['skin'], 90) or near(c, (240, 240, 240), 60)) and not (x > 280 and y < 415): continue
            bp[x, y] = (0, 0, 0, 0)
    head = src.crop((0, 0, w, p['head'] + 14)); hm = Image.new('RGBA', src.size, (0, 0, 0, 0)); hm.paste(head, (0, 0))
    hm = hm.rotate(p['tilt'], resample=Image.BICUBIC, center=p['pivot']);
    for y in range(0, p['head']):
        for x in range(w): bp[x, y] = (0, 0, 0, 0)
    out = Image.new('RGBA', src.size, (0, 0, 0, 0)); out.alpha_composite(hm, (0, p['drop'])); out.alpha_composite(body)
    big = out.resize((w*K, h*K), Image.LANCZOS); d = ImageDraw.Draw(big); S = lambda pt, dx=0, dy=0: ((pt[0] + dx)*K, (pt[1] + dy)*K)
    def limb(pts, width, fill, dx=0, dy=0):
        q = [S(a, dx, dy) for a in pts]; d.line(q, fill=fill, width=int(width*K), joint='curve')
        for a in q: r = width*K/2; d.ellipse((a[0] - r, a[1] - r, a[0] + r, a[1] + r), fill=fill)
    dark = tuple(int(c*0.82) for c in col['skin'])
    for s, e, wr, sg in ((p['sL'], p['eL'], p['wL'], 1), (p['sR'], p['eR'], p['wR'], -1)):
        limb([s, e, wr], p['w'], col['shade'] + (255,), 2*sg, 5); limb([s, e, wr], p['w'] - 3, col['main'] + (255,))
        ux, uy = wr[0] - e[0], wr[1] - e[1]; L = math.hypot(ux, uy); ux /= L; uy /= L
        c0 = (wr[0] - ux*3, wr[1] - uy*3); c1 = (wr[0] + ux*8, wr[1] + uy*8); d.line([S(c0), S(c1)], fill=col['cuff'] + (255,), width=int((p['w'] - 5)*K))
    hx, hy = p['hand']
    for dx, rot in ((-9, 1), (9, -1)):
        d.ellipse(((hx + dx - 15)*K, (hy - 11)*K, (hx + dx + 15)*K, (hy + 12)*K), fill=dark + (255,)); d.ellipse(((hx + dx - 14)*K, (hy - 11)*K, (hx + dx + 14)*K, (hy + 10)*K), fill=col['skin'] + (255,))
    for i in (-1, 0, 1): d.line([((hx + i*7 - 3)*K, (hy + 1)*K), ((hx + i*7 + 3)*K, (hy + 7)*K)], fill=dark + (255,), width=int(1.6*K))
    res = big.resize((w, h), Image.LANCZOS); res = res.crop((res.getbbox()[0], 0, res.getbbox()[2], h)); res.save(OUT / f'{name}_bow.png', optimize=True); print(name, res.size, col)
for n in P: make(n)
