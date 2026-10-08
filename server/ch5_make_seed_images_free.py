#!/usr/bin/env python3
"""Gemini 키 없이 운영실 자료 사진을 만든다 (Pollinations 무료 이미지 생성, 키 불필요).

ch5_seed.json 의 각 게시물 `images` ({키: 영어 설명})마다 server/seed_images/<id>-<키>.jpg 를 만든다.
스토리·쇼츠는 세로(720x1280), 기사는 가로(1024x640). 무료판은 오른쪽 아래에 워터마크가 찍혀서 아래쪽을 잘라낸다.
이미 있는 파일은 건너뛴다(다시 만들려면 지우고 실행). 예전 파일명(seed-*.jpg, daily-*.jpg)은 REUSE 표대로 복사해 쓴다.
Gemini 키가 생기면 ch5_make_seed_images.py 로 더 좋은 사진을 만들 수 있다.

사용: python server/ch5_make_seed_images_free.py
"""
import io
import json
import os
import shutil
import time
import urllib.parse
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, 'ch5_seed.json')
OUT = os.path.join(HERE, 'seed_images')
SIZES = {'story': (720, 1280), 'shorts': (720, 1280), 'news': (1024, 640)}
STYLE = ', realistic smartphone photo, natural colors, no text, no letters, no watermark, no visible faces'
# 예전에 만든 사진을 새 이름으로 재사용 (새 이름: 옛 파일)
REUSE = {
    'n-6y-main': 'seed-6y.jpg', 'n-3y-main': 'seed-3y.jpg', 'n-now-main': 'seed-now.jpg', 'n-closing-main': 'seed-closing.jpg',
    'n-sink-main': 'seed-expert.jpg', 's-expert-main': 'seed-expert.jpg', 's-coaster-b': 'daily-coaster.jpg',
    's-lights-b': 'seed-lights.jpg', 's-vlog-main': 'seed-story-ferry.jpg', 's-vlog-b': 'daily-safari.jpg',
    's-vlog-c': 'daily-churros.jpg', 's-vlog-d': 'daily-sunset.jpg', 's-safari-main': 'daily-safari.jpg',
    's-oldvideo-main': 'seed-photo.jpg', 't-ferry-main': 'seed-story-ferry.jpg', 't-oldphoto-main': 'seed-photo.jpg',
    't-churros-main': 'daily-churros.jpg', 't-sunset-main': 'daily-sunset.jpg', 't-rumor-main': 'daily-closing-rumor.jpg',
    't-official-main': 'daily-handsome.jpg', 't-viking-b': 'daily-viking.jpg', 't-lost-main': 'daily-lost.jpg',
}

os.makedirs(OUT, exist_ok=True)
seeds = json.load(open(SEED, encoding='utf-8'))
todo = []
for s in seeds:
    for key, prompt in (s.get('images') or {}).items():
        name = f"{s['id']}-{key}.jpg"
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            continue
        old = REUSE.get(f"{s['id']}-{key}")
        if old and os.path.exists(os.path.join(OUT, old)):
            shutil.copyfile(os.path.join(OUT, old), path)
            print('복사:', old, '->', name)
            continue
        todo.append((s, key, prompt, path))

print(f'만들 사진 {len(todo)}장', flush=True)
for i, (s, key, prompt, path) in enumerate(todo):
    w, h = SIZES.get(s['format'], (960, 720))
    gh = int(h * 1.08)  # 워터마크를 잘라낼 여유
    url = ('https://image.pollinations.ai/prompt/' + urllib.parse.quote(prompt + STYLE)
           + f'?width={w}&height={gh}&nologo=true&seed={2000 + i}')
    for attempt in range(6):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=180).read()
            im = Image.open(io.BytesIO(raw)).convert('RGB')
            im = im.crop((0, 0, im.width, int(im.height * (h / gh)))).resize((w, h), Image.LANCZOS)
            im.save(path, quality=86)
            print('만듦:', os.path.basename(path), im.size, flush=True)
            time.sleep(20)  # 무료판 요청 제한(같은 주소에서 연달아 요청하면 402)
            break
        except Exception as e:  # 무료 서비스라 가끔 실패함
            print('재시도', attempt + 1, os.path.basename(path), e, flush=True)
            time.sleep(30 + attempt * 15)
print('완료')
