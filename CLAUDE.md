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
- `chapter02/` — AI 이상감지 (진범찾기). TensorFlow.js + Teachable Machine 웹캠 분류, Web Serial API로 Arduino 연동 — Chrome/Edge 필요. AI 모델 교체 시 `index.html` 내 Teachable Machine 모델 URL 변경.
- `chapter03/` — 머지큐브 속 비밀 (단일 대형 `index.html`, ~2100줄). 퍼즐 정답·일기장 비밀번호 등이 `index.html` 상단 데이터 영역에, 색상·레이아웃 변수는 `styles.css` 상단에 있음.
- `chapter03/mission.html` — 시그널 브레이크 미션 뽑기(현장 운영용, 챕터 3의 두 번째 진입로). 상/중/하 난이도 탭을 누르고 카드를 고르면 미션이 공개된다. 미션 목록은 스크립트 상단 `DEFAULT_MISSIONS`에 `{name, desc}` 형태로 있고(`name`=크게, `desc`=그 아래 작게), 이 값을 고치면 **`MISSION_VERSION`도 1 올려야** 이미 localStorage에 저장된 기기에 반영된다. 같은 블록의 `MIN_CARDS`(기본 6)는 화면에 깔 최소 카드 수로, 미션이 그보다 적으면 같은 미션을 복제해 채운다(미션 3개 → 2장씩 6장). 카드 크기·열 수는 `layoutDeck()`이 화면 크기와 미션 개수로 계산하므로 그리드 클래스를 직접 손대지 말 것. 메인 허브의 챕터 3 카드는 버튼이 둘(`chapter03/index.html` / `chapter03/mission.html`)이며 `index.html`의 `chapterData['3-mission']`로 연결된다.
- `chapter04/` — 트레이스 브레이크 / 도로랜드 데이터 분석기 (단일 대형 `index.html`, CSS·데이터 모두 인라인). 진입 비밀번호 `0101`, 출입증 코드(예: `J-088`)와 출입기록 표 데이터가 `index.html` 스크립트 상단에 정의됨. 캐릭터 사원증은 `images/chars/<영문명>.png`(썸네일)과 `images/chars/large/`(확대 라이트박스용) 두 벌을 파일명으로 매칭하므로 교체 시 두 곳 모두 같은 이름으로 넣을 것. `data/`의 CSV는 출제 원본 참고용이며 앱이 런타임에 읽지는 않음 — 수치를 고치려면 `index.html` 내장 데이터를 함께 수정해야 한다. `chapter04/bak/`에는 인쇄 소품(`print/`), 고해상도 캐릭터 원본(`src/`), 구버전 HTML·분리 CSS(`html/`)가 있고 git·배포 모두에서 제외된다 (원본 출처: 공유 드라이브 `DOROLAND\Chpt4. 구름 너머의 진실\Trace Break`).
- 주의: `docs/guide.md`는 chapter02와 chapter03의 내용이 서로 뒤바뀌어 기술되어 있음 (실제: ch02=AI 이상감지, ch03=머지큐브). 챕터 내용은 코드를 기준으로 판단할 것.
- `bak/` — 원본 백업 (gitignore됨, 수정 금지, 잘못 고쳤을 때 복구용).

## 수정 시 관례

- 이미지/오디오는 같은 파일명으로 덮어쓰면 코드 수정 없이 반영되는 구조다. 교체 시 파일명을 유지할 것.
- 게임 정답·비밀번호·힌트 값은 각 챕터 HTML/JS 상단의 데이터 영역에 모여 있음 — 로직이 아니라 데이터를 수정.
- 수정 후 해당 HTML을 브라우저에서 열어 확인하고 배포. 편집 가이드 상세는 `docs/guide.md` 참고.
