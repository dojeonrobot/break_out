# 챕터 5 「코덱스의 선택」 운영·배포 메모

허브의 챕터 5 카드는 진입로가 둘이다.

| 버튼 | 파일 | 내용 | 서버 필요 |
|---|---|---|---|
| 보이드의 기록 | `chapter05/index.html` + `chapter05/scans/` | ERICA 캠퍼스 / 도로랜드 섬 3D 디지털 트윈. 학생 Scaniverse 스캔이 빈 구역을 채움 | **있음** (`server/ch5_void_server.py`, 링크 제출·운영자용) |
| 도로그램 | `chapter05/feed.html`, `chapter05/feed-admin.html`, `chapter05/feed-config.js` | 미션 1 「도로랜드가 사라졌다?」 가짜뉴스 피드 | **있음** (`server/ch5_feed_server.py`) |

## 보이드의 기록

- 원본 빌드 도구는 `C:\Users\dlgus\erica-twin` (template.html + build.py). `python build.py` 결과(`dist/index.html`, `dist/scans/*`)를 이 폴더에 덮어쓴다.
- 게시본(claude.ai 아티팩트)에서 받은 `index.html`은 앞에 아티팩트 껍데기가 붙어 있지만 그대로 열어도 동작한다.
- 스캔 링크 제출은 `server/ch5_void_server.py`(포트 8096, `/api/void/*`)에 저장된다. 조별로 어느 구역에 어떤 링크를 냈는지(찍은 것 메모 포함) 운영자가 한눈에 본다. 서버에 못 붙으면(파일로 열었을 때 등) 예전처럼 그 기기 브라우저에만 저장된다.
- 화면: 패널의 **우리 조** 선택(기기에 기억) → "복구 필요" 구역 카드에서 링크 + 찍은 것 메모 제출 → 구역이 "복구 중". 취소는 우리 조 제출만 가능.
- **운영자**(패널의 운영자 버튼, 비밀번호 `CH5_ADMIN_KEY` 기본 0101): 조별 제출 목록(구역 실제 이름·메모·링크·시각·3D 반영 여부), 개별 삭제, 목록 복사(탭 구분 텍스트), **전체 초기화**, 숨긴 스캔 되살리기.
- **전체 초기화**는 제출 기록을 모두 지우고, 페이지에 이미 3D로 들어간 스캔을 "숨김"으로 표시해 모든 구역을 "복구 필요"로 되돌린다. 3D 데이터는 파일에 그대로 있으므로(지우려면 erica-twin에서 scans.json을 비우고 다시 빌드) "숨긴 스캔 되살리기"로 복구된다. 숨김 목록은 서버에 있고 각 기기는 상태를 받을 때 한 번 새로고침해 반영한다.
- 제출된 링크를 실제 3D로 넣는 건 여전히 수동: 운영자 목록에서 링크를 받아 erica-twin에서 `add_scan.py <url>=<구역id>` → `build.py` → 이 폴더에 덮어쓰기. 반영된 뒤에는 목록에 "3D 반영됨"으로 표시된다.
- 서버 설치(처음 한 번): `/home/ubuntu/voidrecord/`에 `ch5_void_server.py` 복사, `.env`에 `CH5_ADMIN_KEY=0101`, `sudo cp config/voidrecord.service /etc/systemd/system/ && sudo systemctl enable --now voidrecord`, nginx에 `location ^~ /api/void/` 블록(`config/nginx-breakout.conf`) 추가 후 reload. 데이터는 `/home/ubuntu/voidrecord/data/ch5_void.json`.
- 로컬 확인: `python server/ch5_void_server.py` 후 `http://localhost:8096/chapter05/index.html`.

## 도로그램

### 활동 흐름 (운영자 탭에서 단계 넘김, 비밀번호 0101)
1. **자료 살펴보기**: 자료실(도로랜드 정리본)을 먼저 읽는다. 예제 27개(`server/ch5_seed.json`)만 보인다. 아이들이 진짜/가짜를 골라 보면 **바로 해설**이 뜬다(연습, 점수 없음).
2. **게시물 만들기**: 조마다 **스토리·쇼츠·기사 1개씩**(총 3개). 게시물마다 진짜/가짜를 비밀 칸에서 정한다(진짜는 사실 카드 근거, 가짜는 수법+숨긴 단서). 승인 없이 바로 저장, 다른 조에게는 아직 안 보인다.
3. **판별 시간**: 다른 조 게시물이 섞여 보인다(스토리 줄/쇼츠/뉴스). 공개 전에는 작성 조가 어디에도 안 나온다. "예제 자료" 칩으로 예제도 다시 볼 수 있다.
4. **정답 공개**: 우리 조가 몇 개 맞췄는지(N / 판별 대상), 속인 조 수, 순위. 상세 창에 각 조의 수법·단서.

점수: 다른 조 게시물 맞힌 판별 1점(근거 기준 고른 것만) + 우리 가짜를 진짜로 믿은 조마다 1점. 예제는 점수 제외.
조 수는 운영자 탭에서 2~12로 바꿀 수 있다(서버 DB `teamCount`). 도움말 탭(예시 사진은 `chapter05/images/help/`)에 판별법·작성법 상세 설명.

### 2026-10-08 개편: 실제 서비스처럼
- **스토리**: 슬라이드 여러 장(예제는 `slides`, 조 게시물은 본문 빈 줄로 나뉨 + "사진 더 넣기"), 위 진행 막대, 자동 넘김, 오른쪽/왼쪽 탭, 길게 누르면 멈춤, 위치·음악·투표·질문·링크·카운트다운 스티커, 끝나면 다음 계정 스토리로.
- **쇼츠**: 장면(`scenes`) 자동 재생(사진 켄번즈 + 자막, 아래 빨간 진행 바, 끝나면 반복), 탭으로 멈춤/재생, 오른쪽 레일(좋아요·댓글 창·공유·리믹스·회전 디스크), 채널+구독자+구독 버튼, 음악 줄, 썸네일에 길이 표시, 휠·↑↓로 다음 쇼츠.
- **기사**: 마스트헤드·섹션 탭·제목·부제(`subhead`)·기자 바이라인(입력/수정/조회)·사진 설명·본문 여러 문단·숫자 박스(`stats`)·인용(`quote`)·기자 이메일·댓글·관련 기사·ⓒ.
- **올린 사람**: `author.kind`(official/press/creator/person), `verified`(인증 배지, 운영실 자료에만. 조 게시물은 서버가 false로 고정), `posts`, `bio`. 이름·프로필을 누르면 계정 창이 열리고 자료실 등록 계정과 자동 대조(`regCheck`).
- **자료실 탭**(도로랜드 정리본): `feed-config.js`의 `ARCHIVE`(개요·배·구역·숫자·연표·이상 현상·운영실 입장·등록 계정). `FACTS`는 여기서 자동 생성되어 "자료 대조"와 진짜 게시물 근거 선택에 쓰인다. **예제 게시물의 숫자와 맞춰 둔 것이므로 한쪽만 고치지 말 것.**
- 수법에 「숫자 부풀리기」「들은 이야기」 추가. 예제 27개(기사 9·쇼츠 8·스토리 10, 가짜 11)로 교체. 예제 사진은 `images`({키: 영어 설명}) → `seed_images/<id>-<키>.jpg`, `ch5_make_seed_images_free.py`가 없는 것만 만든다(Pollinations 무료, 402가 나면 재시도).
- 서버 공개 필드에 `subhead, editedAt, extraImages, slides, scenes, quote, stats, poll, music, comments, commentCount` 추가. 예제를 바꾸면 서버 `data/ch5_feed.json`을 지우고(또는 운영자 "전부 초기화") 재시작해야 반영된다.

### 고칠 곳
- 미션 카드(조별 형식·수법), 자료실(ARCHIVE)·확인 기준·계정 종류·단계 설명: `chapter05/feed-config.js`
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
