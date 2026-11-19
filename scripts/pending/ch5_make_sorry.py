# 사과(슬픔) 표정 초상화 만들기: 전신 그림(zero.png·rico.png)의 머리 자리에 디자인파일의 「슬픔」 표정 머리를 같은 크기로 얹는다.
#  대사 창이 그림 아래 42%를 가리므로 머리만 있는 그림을 쓰면 얼굴이 잘린다(사용자 2026-11-19). 몸을 위에 덮어 목·옷깃이 자연스럽게 이어진다.
#  python ch5_make_sorry.py <슬픔 표정 원본 폴더(zero_sad.png, rico_sad.png)>   → chapter05/img/chars/zero_sorry.png, rico_sorry.png
import pathlib, sys
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]; CH = ROOT / 'chapter05/img/chars'; SRC = pathlib.Path(sys.argv[1])
def rows_of(im):
    a = im.split()[3]; w, h = im.size; out = []
    for y in range(h):
        xs = [x for x in range(0, w, 2) if a.getpixel((x, y)) > 40]; out.append((min(xs), max(xs)) if xs else None)
    return out
for name, face, cut in (('zero', 'zero_sad.png', 0.262), ('rico', 'rico_sad.png', 0.285)):
    body = Image.open(CH / f'{name}.png').convert('RGBA'); f = Image.open(SRC / face).convert('RGBA'); f = f.crop(f.getbbox())
    br = rows_of(body); neck = round(body.height*cut); bx0 = min(r[0] for r in br[:neck] if r); bx1 = max(r[1] for r in br[:neck] if r)
    fr = rows_of(f); fneck = round(f.height*0.72); fx0 = min(r[0] for r in fr[:fneck] if r); fx1 = max(r[1] for r in fr[:fneck] if r)
    k = (bx1 - bx0)/(fx1 - fx0); fs = f.resize((round(f.width*k), round(f.height*k)), Image.LANCZOS); ox = round(bx0 - fx0*k)
    W = max(body.width, ox + fs.width) - min(0, ox); sh = -min(0, ox); out = Image.new('RGBA', (W, body.height), (0, 0, 0, 0)); out.alpha_composite(fs, (ox + sh, 0))
    b2 = body.copy(); b2.paste(Image.new('RGBA', (body.width, neck), (0, 0, 0, 0)), (0, 0)); out.alpha_composite(b2, (sh, 0))
    out.save(CH / f'{name}_sorry.png', optimize=True); print(name, 'head', (bx0, bx1), 'face', (fx0, fx1), 'k', round(k, 3), 'bust', fs.size, 'out', out.size)
