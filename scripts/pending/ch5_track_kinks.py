# 아일랜드 익스프레스 궤도(trackR)의 꺾임 재기: 페이지의 식을 그대로 옮겨 1도 간격 점 사이의 방향 변화를 잰다.
#  python -X utf8 scripts/pending/ch5_track_kinks.py [smooth]   smooth를 주면 제안하는 다듬기(둘레 방향 이동 평균)를 적용한 값도 같이 낸다
import math, sys
K = 1.35
islR = lambda a: K*(400 + 40*math.sin(3*a + 1) + 25*math.sin(5*a + 2) + 15*math.sin(9*a))
def bump(a, c, w):
    d = abs(math.atan2(math.sin(a - c), math.cos(a - c))); return 0.5*(1 + math.cos(math.pi*d/w)) if d < w else 0
CC = (-270, 256); CLEAR = 160
def ss(x0, x1, x): t = min(1, max(0, (x - x0)/(x1 - x0))); return t*t*(3 - 2*t)
def trackR(a):
    sn = math.sin(a); b = islR(a) - 58 - 22*bump(a, -1.65, 0.32); r = min(b, 338/sn) if sn > 0.2 else b
    cu = CC[0]*math.cos(a) + CC[1]*sn; disc = CLEAR*CLEAR - (CC[0]**2 + CC[1]**2) + cu*cu
    if disc > 0:
        arc = cu + math.sqrt(disc); w = ss(1.9, 2.04, a)*(1 - ss(2.56, 2.7, a))
        if arc > r: r += (arc - r)*w
    fx, fz, FC = 160*1.35, -180*1.35, 90; fu = fx*math.cos(a) + fz*sn; fd = FC*FC - (fx*fx + fz*fz) + fu*fu
    if fd > 0:
        s0 = math.sqrt(fd); far = fu + s0
        if fu - s0 < r < far: r = min(far, islR(a) - 20)
    return r
N = 360
def turns(R):
    P = [(math.cos(i/N*2*math.pi)*R[i], math.sin(i/N*2*math.pi)*R[i]) for i in range(N)]; out = []
    for i in range(N):
        a, b, c = P[i - 1], P[i], P[(i + 1) % N]; h1 = math.atan2(b[1] - a[1], b[0] - a[0]); h2 = math.atan2(c[1] - b[1], c[0] - b[0]); d = math.degrees(math.atan2(math.sin(h2 - h1), math.cos(h2 - h1)))
        seg = math.hypot(c[0] - b[0], c[1] - b[1]); out.append((abs(d), i, round(b[0]), round(b[1]), round(seg, 1), round(R[i])))
    return out
def report(name, R):
    t = turns(R); big = sorted([x for x in t if x[0] > 8], reverse=True)
    print(name, '가장 큰 꺾임 %.1f도' % max(x[0] for x in t), '8도 넘는 점', len(big))
    for d, i, x, z, seg, r in big[:14]: print('   각도 %3d도 (라디안 %.2f)  꺾임 %5.1f도  자리 (%d, %d)  반지름 %d' % (i, i/N*2*math.pi, d, x, z, r))
def bounds(a, r):   # 지켜야 하는 한계: lo = 롤러코스터 부지·관람차 언덕 바깥, hi = 정문 뒤 직선·해안 안쪽
    sn = math.sin(a); hi = islR(a) - 20
    if sn > 0.2: hi = min(hi, 338/sn)
    lo = 0; cu = CC[0]*math.cos(a) + CC[1]*sn; disc = 150*150 - (CC[0]**2 + CC[1]**2) + cu*cu
    if disc > 0: lo = max(lo, (cu + math.sqrt(disc))*ss(1.9, 2.04, a)*(1 - ss(2.56, 2.7, a)))
    fx, fz, FC = 160*1.35, -180*1.35, 84; fu = fx*math.cos(a) + fz*sn; fd = FC*FC - (fx*fx + fz*fz) + fu*fu
    if fd > 0: lo = max(lo, fu + math.sqrt(fd))
    return min(lo, hi), hi
def smooth(R0, W=4, it=14, fin=2):
    n = len(R0); B = [bounds(i/n*2*math.pi if i/n*2*math.pi <= math.pi else i/n*2*math.pi - 2*math.pi, R0[i]) for i in range(n)]; R = R0[:]
    blur = lambda R, w: [sum(R[(i + k) % n] for k in range(-w, w + 1))/(2*w + 1) for i in range(n)]
    for _ in range(it): R = blur(R, W); R = [min(max(R[i], B[i][0]), B[i][1]) for i in range(n)]
    R = blur(R, fin); return R, max(max(B[i][0] - R[i], R[i] - B[i][1]) for i in range(n))
R0 = [trackR(i/N*2*math.pi if i/N*2*math.pi <= math.pi else i/N*2*math.pi - 2*math.pi) for i in range(N)]
if len(sys.argv) > 1 and sys.argv[1] == 'fit':
    for W, it, fin in ((4, 14, 2), (6, 20, 2), (8, 30, 3), (10, 40, 3)):
        R, viol = smooth(R0, W, it, fin); report('맞춤 W%d it%d fin%d  한계 넘음 %.1f  반지름 변화 최대 %.0f' % (W, it, fin, viol, max(abs(R[i] - R0[i]) for i in range(N))), R)
    sys.exit()
report('지금', R0)
if len(sys.argv) > 1:
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 7; R = R0[:]
    for _ in range(3): R = [sum(R[(i + k) % N] for k in range(-W, W + 1))/(2*W + 1) for i in range(N)]
    report('다듬은 뒤(창 %d도 × 3번)' % W, R)
    print('  반지름이 가장 많이 달라진 곳', max(((abs(R[i] - R0[i]), i, round(R0[i]), round(R[i])) for i in range(N)))[:4])
