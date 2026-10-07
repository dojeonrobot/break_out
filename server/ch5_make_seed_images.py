#!/usr/bin/env python3
"""운영실 자료(ch5_seed.json)의 imagePrompt로 사진을 만들어 server/seed_images/ 에 저장한다.

운영실 자료에 사진이 없으면 "사진 있는 글 = 조가 만든 글"로 티가 나서, 운영실 자료에도 사진을 넣어 둔다.
한 번 만들어 커밋해 두면 서버를 초기화할 때마다 그대로 쓴다. 이미 있는 파일은 건너뛴다(다시 만들려면 지우고 실행).

사용: GEMINI_API_KEY=... python server/ch5_make_seed_images.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ch5_feed_server as srv  # noqa: E402  (같은 Gemini 호출 코드를 씀)

os.makedirs(srv.SEED_IMG_DIR, exist_ok=True)
seeds = json.load(open(srv.SEED_PATH, encoding='utf-8'))
for s in seeds:
    name, prompt = s.get('image'), s.get('imagePrompt')
    if not name or not prompt:
        continue
    out = os.path.join(srv.SEED_IMG_DIR, name)
    if os.path.exists(out):
        print('있음:', name)
        continue
    ratio = '세로 9:16 비율. ' if s.get('format') == 'story' else '가로 4:3 비율. '
    raw = srv.gemini_image(ratio + prompt)
    with open(out, 'wb') as f:
        f.write(raw)
    print('만듦:', name, len(raw), 'bytes')
