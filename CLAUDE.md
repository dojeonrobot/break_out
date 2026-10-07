# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

DOROLAND Break Out Adventure — 교육용 방탈출 웹 애플리케이션. 빌드 도구, 패키지 매니저, 테스트 프레임워크가 없는 순수 정적 사이트다 (HTML/CSS/Vanilla JS, Tailwind CDN). https://breakout.doroedu.co.kr 에서 서빙 중이며 카카오 클라우드 서버(nginx)에 배포되어 있다.

## 실행 및 배포

- **로컬 실행**: 빌드 없이 `index.html`을 브라우저에서 직접 열면 됨. Chapter 02는 웹캠·Web Serial API를 사용하므로 Chrome/Edge 필요.
- **배포**: `.\scripts\deploy.ps1 -Message "커밋 메시지"` 실행 (PowerShell). 스크립트가 git 커밋+push → tar 압축 → scp 업로드 → 서버의 `/home/ubuntu/breakout/` 에 압축 해제 → 캐시버스팅 → 주요 URL 200 검증까지 수행한다. `-Message` 생략 시 날짜 기반 기본 메시지로 커밋된다. SSH 키는 `C:\Users\pc\Documents\PW\hy_key.pem`. 상세 절차는 `docs/deploy.md` 참고.
- `bak/`, `config/`, `scripts/`, `docs/` 는 배포에서 제외됨 (로컬 관리용).

## 캐시 버스팅 (중요)

배포 시 `scripts/cache-bust.sh`가 **서버에서** 모든 HTML/CSS 내 정적 자산 참조(`.css`, `.js`, `.png`, `.mp3` 등)에 `?v=타임스탬프`를 자동으로 붙인다. 로컬 소스에는 쿼리스트링을 직접 쓰지 말 것 — 배포 파이프라인이 처리한다. nginx는 HTML을 no-cache, CSS/JS/이미지/오디오를 1년 immutable로 캐싱한다 (`config/nginx-breakout.conf`).

## 구조

- `index.html` — 메인 대시보드 (챕터 선택 허브). 각 챕터는 독립된 폴더로, 챕터 간 공유 코드 없음.
- `chapter01/` — 도트매트릭스 암호 해독. 로직은 `js/app.js`에 분리되어 있고, 미션/힌트 데이터(비밀번호, 이미지 경로)가 파일 상단 `missions` 배열에 정의됨.
- `chapter01/linetracer.html` — 사파리 라인트레이서 매뉴얼 페이지(챕터 1의 두 번째 진입로, 허브의 `chapterData['1-linetracer']`). 구성은 ① 연결 및 코드 업로드(`#setup`: USB 첫 업로드 → 자동차 Wi-Fi 접속 → 무선 업로드) ② 대시보드 확인 방법(`#dashboard`: 번호 달린 캡처 `images/linetracer/dashboard.png` + 로그 읽는 법 + 점검 순서) ③ 센서 및 속도 튜닝(`#tuning`: 시뮬레이터 → 속도 조정 → 코드 수정 방법) → 문제 해결 → 완주 기록 순이며, 외부 매뉴얼 링크 없는 단일 공식 매뉴얼이다. 화면 문구에서 기기는 "로봇"이 아니라 "사파리 자동차"로 부른다. 대시보드 캡처는 zip의 `dashboard.h`를 가짜 SSE 서버로 띄워 찍은 것이라 대시보드 디자인을 바꾸면 다시 찍어야 한다. 로봇 Wi-Fi 정보는 파일 상단 `ROBOT`(`Safari-Linetracer-00` / `linetracer00` / `192.168.4.1`), 링크는 `LINKS`, 센서 패턴별 모터 값은 `PATTERNS`에 있다. 스케치는 `chapter01/files/safari_linetracer.zip`(펌웨어 v0.1.0)으로 직접 서빙하며 모든 값은 이 코드 기준. 스케치를 바꾸면 zip과 페이지 값을 함께 맞출 것. zip 안의 `dashboard.h`(192.168.4.1에서 뜨는 로봇 대시보드 HTML)는 원본에서 스타일·표시 문구·색상 값만 바꾼 도로랜드 디자인이고 제작자 표기는 `© 2026 DORO Inc.`로 정리했다. 요소 id와 `/events` 처리 로직은 원본 그대로이므로 수정 시에도 유지할 것(로봇엔 인터넷이 없어 외부 CDN·폰트 사용 불가, 이미지는 base64). 맨 아래 **완주 기록**(`#record`)은 스톱워치 + 팀별 최고 기록 순위표로, 기록은 그 기기 브라우저의 localStorage(`doroland-linetracer-records-v1`)에만 저장된다(로봇 Wi-Fi엔 인터넷이 없어 서버 저장 없음). 기기 간 공유는 안 되므로 기록은 한 대(강사 PC)에서 받고 CSV로 내보낸다.
- `chapter02/` — AI 이상감지 (진범찾기). TensorFlow.js + Teachable Machine 웹캠 분류, Web Serial API로 Arduino 연동 — Chrome/Edge 필요. AI 모델 교체 시 `index.html` 내 Teachable Machine 모델 URL 변경.
- `chapter03/` — 머지큐브 속 비밀 (단일 대형 `index.html`, ~2100줄). 퍼즐 정답·일기장 비밀번호 등이 `index.html` 상단 데이터 영역에, 색상·레이아웃 변수는 `styles.css` 상단에 있음.
- `chapter03/mission.html` — 시그널 브레이크 미션 뽑기(현장 운영용, 챕터 3의 두 번째 진입로). 상/중/하 난이도 탭을 누르고 카드를 고르면 미션이 공개된다. 미션 목록은 스크립트 상단 `DEFAULT_MISSIONS`에 `{name, desc}` 형태로 있고(`name`=크게, `desc`=그 아래 작게), 이 값을 고치면 **`MISSION_VERSION`도 1 올려야** 이미 localStorage에 저장된 기기에 반영된다. 같은 블록의 `DECK_SIZE`(기본 12)는 화면에 까는 카드 수로, 미션이 그보다 적으면 같은 미션을 복제해 항상 그 장수를 채운다(미션 3개 → 4장씩 12장). 12로 딱 안 나뉘면 남는 장수를 매번 다른 미션에 얹어 편중을 막는다. 미션은 각자 `id`로 구분되므로 **제목이 같은 미션을 여러 개 둬도 된다**(중 난이도가 그 예). 미션에 사진(`img`)을 붙이면 뽑혔을 때 설명 옆에 크게 뜬다 — 설정 화면에서 올리면 긴 변 900px·JPEG 0.75로 줄여 localStorage에 담고(아이폰 HEIC는 `heic2any`를 CDN에서 **그때만** 지연 로드해 JPEG로 변환),  코드에 박으려면 `chapter03/images/missions/`에 파일을 넣고 `img: 'images/missions/파일명.jpg'` 경로를 적는다(용량 걱정 없이 모든 기기에 적용됨). 상 난이도는 매번 바뀌는 유행 챌린지를 넣기로 해서 기본값이 비어 있고, 비면 카드 대신 "미션을 추가해주세요" 안내가 뜬다. 카드 크기·열 수는 `layoutDeck()`이 화면 크기와 미션 개수로 계산하므로 그리드 클래스를 직접 손대지 말 것. 메인 허브의 챕터 3 카드는 버튼이 둘(`chapter03/index.html` / `chapter03/mission.html`)이며 `index.html`의 `chapterData['3-mission']`로 연결된다.
- `chapter04/` — 트레이스 브레이크 / 도로랜드 데이터 분석기 (단일 대형 `index.html`, CSS·데이터 모두 인라인). 진입 비밀번호 `0101`, 출입증 코드(예: `J-088`)와 출입기록 표 데이터가 `index.html` 스크립트 상단에 정의됨. 기밀 기록실 인증코드는 `VAULT_UNLOCK_CODES`에 자료별로 따로 있고(출입증 대조 파일 `PQUDJ`, 직원 휴가 캘린더 `CAFLY`), 입력창이 대문자 영숫자로 강제 변환한 뒤 비교하므로 **코드는 대문자로 적을 것**. 전체 해금용 `all` 코드는 `null`로 꺼져 있다. 캐릭터 사원증은 `images/chars/<영문명>.png`(썸네일)과 `images/chars/large/`(확대 라이트박스용) 두 벌을 파일명으로 매칭하므로 교체 시 두 곳 모두 같은 이름으로 넣을 것. **엔딩 영상**은 `chapter04/ending.mp4`(1920×1080, 약 62초, 좌우 검은 여백이 원본에 박혀 있음). 다섯 단서를 모두 맞혀 기밀 파일이 열렸을 때만 나타나는 **엔딩 영상 보기** 버튼으로 재생되며, 극장 오버레이(`#endingStage`)가 기밀 파일 위에 뜨고 재생이 끝나면 THE END 카드(`#esEndCard`)가 나온다. 영상 교체 시 `ending.mp4` 이름을 유지할 것 — 한글·공백 파일명은 배포 경로에서 깨질 수 있어 ASCII로 통일했다. `data/`의 CSV는 출제 원본 참고용이며 앱이 런타임에 읽지는 않음 — 수치를 고치려면 `index.html` 내장 데이터를 함께 수정해야 한다. `chapter04/bak/`에는 인쇄 소품(`print/`), 고해상도 캐릭터 원본(`src/`), 구버전 HTML·분리 CSS(`html/`)가 있고 git·배포 모두에서 제외된다 (원본 출처: 공유 드라이브 `DOROLAND\Chpt4. 구름 너머의 진실\Trace Break`).
- `chapter05/` — 챕터 5 「코덱스의 선택」, 허브 카드 진입로 둘(`chapterData[5]`, `chapterData['5-feed']`). 상세는 `docs/chapter05.md`.
  - `index.html` + `scans/` — 「보이드의 기록」 3D 디지털 트윈(ERICA 캠퍼스 / 도로랜드 섬). 정적 파일이며 원본 빌드 도구는 `C:\Users\dlgus\erica-twin`(build.py 결과를 덮어씀). 스캔 데이터는 gzip+base64 `.splat.txt`.
  - `feed.html`(학생) / `feed-admin.html`(운영자, 비밀번호 `CH5_ADMIN_KEY`, 기본 0101) / `feed-config.js`(미션 카드·사실 카드·확인 기준·단계 문구) — 「도로그램」 가짜뉴스 피드. **이 챕터만 서버가 필요하다**: `server/ch5_feed_server.py`(Python 표준 라이브러리, SSE 실시간, `/api/ch5/*`). 운영실 자료(정답 포함)는 `server/ch5_seed.json`, 사진은 `server/seed_images/`(`ch5_make_seed_images.py`로 생성). 아이들 게시물은 올릴 때 진짜/가짜를 직접 정하고 승인 없이 바로 올라가며, 정답 공개 전에는 API가 작성 조·운영실 자료 여부·작성 시각을 내려주지 않는다(조 게시물이 티 나지 않게). AI 이미지·문장 다듬기는 서버에서 Gemini 호출(`GEMINI_API_KEY`).
  - `server/`는 배포 tar에서 제외되며(웹 루트에 .py가 올라가지 않게), 서버에는 `/home/ubuntu/dorogram/`에 따로 두고 systemd(`config/dorogram.service`) + nginx `location /api/ch5/`(`config/nginx-breakout.conf`)로 붙인다. 로컬 확인은 `python server/ch5_feed_server.py` 후 `http://localhost:8095/chapter05/feed.html`.
- 주의: `docs/guide.md`는 chapter02와 chapter03의 내용이 서로 뒤바뀌어 기술되어 있음 (실제: ch02=AI 이상감지, ch03=머지큐브). 챕터 내용은 코드를 기준으로 판단할 것.
- `bak/` — 원본 백업 (gitignore됨, 수정 금지, 잘못 고쳤을 때 복구용).

## 수정 시 관례

- 이미지/오디오는 같은 파일명으로 덮어쓰면 코드 수정 없이 반영되는 구조다. 교체 시 파일명을 유지할 것.
- 게임 정답·비밀번호·힌트 값은 각 챕터 HTML/JS 상단의 데이터 영역에 모여 있음 — 로직이 아니라 데이터를 수정.
- 수정 후 해당 HTML을 브라우저에서 열어 확인하고 배포. 편집 가이드 상세는 `docs/guide.md` 참고.
