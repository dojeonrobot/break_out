# 2026-11-19 밤: 앞 패치(1119c)가 미션 카드 윗줄 처리를 엉뚱한 자리에 끼워 문법이 깨진 것을 바로잡는다(페이지에 올리기 전).
#  + 사과 표정 그림을 머리만이 아니라 원래 전신 그림의 몸 위에 얹어 다시 만든다(대사 창이 그림 아래 42%를 가리므로 머리만 있는 그림은 얼굴이 잘린다).
# 한 번만 적용: python scripts/pending/ch5_patch_1119d.py <슬픔 표정 원본 폴더>
import pathlib, sys
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]; p = ROOT / 'chapter05/index.html'; s = p.read_bytes().decode('utf-8')
bad = " $('mcN').classList.toggle('ko', /[가-힣]/.test($('mcN').textContent));"
assert s.count(bad) == 1; s = s.replace(bad, '')
a = "if(q.label) $('mcN').textContent = q.label;"; assert s.count(a) == 1
s = s.replace(a, a + " $('mcN').classList.toggle('ko', /[가-힣]/.test($('mcN').textContent));")
p.write_bytes(s.encode('utf-8')); print('page ok')
# 표정 머리를 전신 그림의 머리 자리에 얹는다: 전신 그림에서 머리(위쪽 덩어리)의 폭을 재고, 표정 그림의 머리 폭을 거기에 맞춘다.
SRC = pathlib.Path(sys.argv[1]); CH = ROOT / 'chapter05/img/chars'
def head_box(im):   # 위에서부터 가장 넓어졌다가 목에서 좁아지는 지점까지
    a = im.split()[3]; w, h = im.size; rows = []
    for y in range(h):
        xs = [x for x in range(0, w, 2) if a.getpixel((x, y)) > 40]
        rows.append((min(xs), max(xs)) if xs else None)
    top = next(y for y, r in enumerate(rows) if r); wid = [(r[1] - r[0]) if r else 0 for r in rows]; peak = max(range(top, top + int(h*0.45)), key=lambda y: wid[y])
    neck = next((y for y in range(peak, int(h*0.6)) if wid[y] < wid[peak]*0.42), int(h*0.3)); xs0 = min(r[0] for r in rows[top:neck] if r); xs1 = max(r[1] for r in rows[top:neck] if r)
    return top, neck, xs0, xs1
for name, face in (('zero', 'zero_sad.png'), ('rico', 'rico_sad.png')):
    body = Image.open(CH / f'{name}.png').convert('RGBA'); f = Image.open(SRC / face).convert('RGBA'); f = f.crop(f.getbbox())
    bt, bn, bx0, bx1 = head_box(body); ft, fn, fx0, fx1 = head_box(f)
    k = (bx1 - bx0)/(fx1 - fx0); fh = f.crop((0, 0, f.width, fn + 2)).resize((round(f.width*k), round((fn + 2)*k)), Image.LANCZOS)
    out = body.copy(); ox = round(bx0 - fx0*k); oy = bt
    out.paste(Image.new('RGBA', (bx1 - bx0 + 8, bn - bt), (0, 0, 0, 0)), (bx0 - 4, bt))   # 원래 머리를 지우고
    pad = Image.new('RGBA', (max(out.width, ox + fh.width) - min(0, ox), out.height), (0, 0, 0, 0)); sh = -min(0, ox); pad.alpha_composite(out, (sh, 0)); pad.alpha_composite(fh, (ox + sh, oy))
    pad.save(CH / f'{name}_sorry.png', optimize=True); print(name, 'body head', (bt, bn, bx0, bx1), 'face head', (ft, fn, fx0, fx1), 'scale', round(k, 3), pad.size)
