# 챕터 5 「코덱스의 선택」 운영·배포 메모

허브의 챕터 5 카드는 진입로가 둘이다.

| 버튼 | 파일 | 내용 | 서버 필요 |
|---|---|---|---|
| 보이드의 기록 | `chapter05/index.html` + `chapter05/scans/` | ERICA 캠퍼스 / 도로랜드 섬 3D 디지털 트윈. 학생 Scaniverse 스캔이 빈 구역을 채움 | 없음 (정적) |
| 도로그램 | `chapter05/feed.html`, `chapter05/feed-admin.html`, `chapter05/feed-config.js` | 미션 1 「도로랜드가 사라졌다?」 가짜뉴스 피드 | **있음** (`server/ch5_feed_server.py`) |

## 보이드의 기록

- 원본 빌드 도구는 `C:\Users\dlgus\erica-twin` (template.html + build.py). `python build.py` 결과(`dist/index.html`, `dist/scans/*`)를 이 폴더에 덮어쓴다.
- 게시본(claude.ai 아티팩트)에서 받은 `index.html`은 앞에 아티팩트 껍데기가 붙어 있지만 그대로 열어도 동작한다.
- 스캔 링크 제출은 아직 그 기기 브라우저(localStorage)에만 저장된다. 서버 저장은 도로버스 서버로 옮길 때 붙인다.

## 도로그램

### 활동 흐름 (운영자 탭에서 단계 넘김, 비밀번호 0101)
1. **자료 살펴보기**: 예제 22개(`server/ch5_seed.json`)만 보인다. 아이들이 진짜/가짜를 골라 보면 **바로 해설**이 뜬다(연습, 점수 없음).
2. **게시물 만들기**: 조마다 **스토리·쇼츠·기사 1개씩**(총 3개). 게시물마다 진짜/가짜를 비밀 칸에서 정한다(진짜는 사실 카드 근거, 가짜는 수법+숨긴 단서). 승인 없이 바로 저장, 다른 조에게는 아직 안 보인다.
3. **판별 시간**: 다른 조 게시물이 섞여 보인다(스토리 줄/쇼츠/뉴스). 공개 전에는 작성 조가 어디에도 안 나온다. "예제 자료" 칩으로 예제도 다시 볼 수 있다.
4. **정답 공개**: 우리 조가 몇 개 맞췄는지(N / 판별 대상), 속인 조 수, 순위. 상세 창에 각 조의 수법·단서.

점수: 다른 조 게시물 맞힌 판별 1점(근거 기준 고른 것만) + 우리 가짜를 진짜로 믿은 조마다 1점. 예제는 점수 제외.
조 수는 운영자 탭에서 2~12로 바꿀 수 있다(서버 DB `teamCount`). 도움말 탭(예시 사진은 `chapter05/images/help/`)에 판별법·작성법 상세 설명.

### 고칠 곳
- 미션 카드(조별 형식·수법), 사실 카드, 확인 기준 문구, 단계 설명: `chapter05/feed-config.js`
- 운영실 자료(정답 포함): `server/ch5_seed.json` → 서버 화면에서 "전부 초기화"를 해야 반영된다.
- 운영실 자료 사진: `GEMINI_API_KEY=... python server/ch5_make_seed_images.py` → `server/seed_images/`에 저장(커밋). 사진이 없으면 "사진 있는 글 = 조 게시물"로 티가 나므로 꼭 만들어 둘 것.

### AI 기능 (Gemini, 서버에서만 호출)
- AI로 그리기 / AI로 사진 고치기: `GEMINI_IMAGE_MODEL` (기본 `gemini-3.1-flash-image`, 나노바나나 2). 조마다 `CH5_AI_QUOTA`회(기본 8).
- AI로 말투 다듬기: `GEMINI_TEXT_MODEL` (기본 `gemini-2.5-flash`).
- 키가 없으면 AI 버튼이 꺼지고 사진 올리기만 된다.
- 아이들은 외부 AI 사이트에 가입하지 않는다(13세 미만 가입 문제 없음).

### 로컬에서 확인
```
python server/ch5_feed_server.py
# 학생: http://localhost:8095/chapter05/feed.html   (?team=3 으로 조 고정, ?view=screen 진행 화면)
# 운영자: http://localhost:8095/chapter05/feed-admin.html  (비밀번호 기본 0101, CH5_ADMIN_KEY로 변경)
```
로컬 확인용으로 이 서버가 저장소 파일도 같이 서빙한다(`CH5_STATIC=1`, 기본). 서버에서는 nginx가 정적 파일을 서빙하므로 `CH5_STATIC=0`.

### 서버 설치 (처음 한 번)
`deploy.ps1`은 정적 파일만 올리고 `server/`는 제외한다. 도로그램 서버는 웹 루트 밖 별도 폴더에 둔다.
```
# 1) 코드 올리기
scp -i hy_key.pem server/ch5_feed_server.py server/ch5_seed.json ubuntu@210.109.15.216:/home/ubuntu/dorogram/
scp -i hy_key.pem -r server/seed_images ubuntu@210.109.15.216:/home/ubuntu/dorogram/
# 2) 서버에서 .env 작성 (CH5_ADMIN_KEY=..., GEMINI_API_KEY=...)
# 3) systemd 등록
sudo cp dorogram.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now dorogram
# 4) nginx: config/nginx-breakout.conf 의 location /api/ch5/ 블록 반영 후 sudo nginx -t && sudo systemctl reload nginx
```
데이터는 `/home/ubuntu/dorogram/data/`(게시물 JSON + 업로드 사진)에 쌓인다. 새 기수 시작 전에 운영자 화면에서 "전부 초기화".
