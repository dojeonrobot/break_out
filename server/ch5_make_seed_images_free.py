#!/usr/bin/env python3
"""Gemini 키 없이 운영실 자료 사진을 만든다 (Pollinations 무료 이미지 생성, 키 불필요).

ch5_seed.json 의 imagePromptEn(영어 설명)으로 사진을 받아 server/seed_images/<id>.jpg 로 저장하고,
seed 의 image 필드를 채운다. 무료판은 오른쪽 아래에 워터마크가 찍혀서 아래쪽을 잘라낸다.
이미 있는 파일은 건너뛴다(다시 만들려면 지우고 실행). Gemini 키가 생기면 ch5_make_seed_images.py 로 더 좋은 사진을 만들 수 있다.

사용: python server/ch5_make_seed_images_free.py
"""
import io
import json
import os
import time
import urllib.parse
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, 'ch5_seed.json')
OUT = os.path.join(HERE, 'seed_images')
SIZES = {'story': (720, 1280), 'sns': (864, 1080), 'news': (1024, 640), 'witness': (960, 720), 'notice': (1024, 576)}
STYLE = ', realistic smartphone photo, natural colors, no text, no letters, no watermark, no visible faces'

os.makedirs(OUT, exist_ok=True)
seeds = json.load(open(SEED, encoding='utf-8'))
for i, s in enumerate(seeds):
    prompt = s.get('imagePromptEn')
    if not prompt:
        continue
    name = s['id'] + '.jpg'
    path = os.path.join(OUT, name)
    s['image'] = name
    if os.path.exists(path):
        print('있음:', name)
        continue
    w, h = SIZES.get(s['format'], (960, 720))
    gh = int(h * 1.08)  # 워터마크를 잘라낼 여유
    url = ('https://image.pollinations.ai/prompt/' + urllib.parse.quote(prompt + STYLE)
           + f'?width={w}&height={gh}&nologo=true&seed={1000 + i}')
    for attempt in range(6):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=180).read()
            im = Image.open(io.BytesIO(raw)).convert('RGB')
            im = im.crop((0, 0, im.width, int(im.height * (h / gh)))).resize((w, h), Image.LANCZOS)
            im.save(path, quality=86)
            print('만듦:', name, im.size, flush=True)
            time.sleep(20)  # 무료판 요청 제한(같은 주소에서 연달아 요청하면 402)
            break
        except Exception as e:  # 무료 서비스라 가끔 실패함
            print('재시도', attempt + 1, name, e, flush=True)
            time.sleep(30 + attempt * 15)
json.dump(seeds, open(SEED, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('완료')
