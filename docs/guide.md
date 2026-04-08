# 프로젝트 수정 가이드

BREAK-OUT 프로젝트를 수정할 때 참고하는 문서입니다.

---

## 전체 구조

```
BREAK-OUT/
├── index.html              ← 메인 화면 (챕터 선택)
├── assets/images/          ← 메인 화면용 로고, 배경
│
├── chapter01/              ← 챕터 1: 도트매트릭스 암호 해독
│   ├── index.html
│   ├── images/             ← 미션 이미지 (001~014)
│   └── docs/               ← 교사용 PDF
│
├── chapter02/              ← 챕터 2: 머지큐브 속 비밀
│   ├── index.html          ← 화면 + 로직
│   ├── styles.css          ← 디자인
│   ├── images/             ← 이미지 (하위 폴더별 분류)
│   └── audio/              ← 배경음악, 효과음
│
├── chapter03/              ← 챕터 3: AI 이상감지
│   ├── index.html
│   ├── images/
│   └── audio/
│
├── docs/                   ← 이 문서들
├── config/                 ← 서버 설정 (수정 불필요)
├── scripts/                ← 배포 스크립트 (수정 불필요)
└── bak/                    ← 원본 백업 (수정 불필요)
```

---

## 메인 화면

**파일**: `index.html`

- 로고/배경 교체 → `assets/images/` 안의 파일을 같은 이름으로 덮어쓰기
- 챕터 카드 이미지 → `chapter1-logo.png`, `chapter2-logo.png`, `chapter3-logo.png`
- 슬로건, 챕터 설명 → `index.html` 내 해당 텍스트 직접 수정

---

## 챕터 1 — 도트매트릭스

**파일**: `chapter01/index.html`

- 미션 이미지 교체 → `chapter01/images/` 안의 png 파일을 같은 이름으로 교체
- 힌트 비밀번호, 최종 정답, 교사용 만능키 → `index.html` 내 해당 값 수정

---

## 챕터 2 — 머지큐브

**파일**: `chapter02/index.html`, `chapter02/styles.css`

### 이미지 위치

| 폴더 | 내용 |
|------|------|
| `images/diary/` | 일기장 페이지 (Diary1~7.png) |
| `images/cubes/` | 큐브 아이콘 |
| `images/patterns/` | 코덱스 문양 |
| `images/missions/` | 스토리 웹툰 이미지 |
| `images/icons/` | 문양 선택 퍼즐 아이콘 (12개) |
| `images/qr/` | QR 코드 (qr-1~3.png) |

### 수정 포인트

- 퍼즐 정답, 일기장 비밀번호, 힌트 비밀번호 → `index.html` 상단 데이터 영역
- 색상, 레이아웃 → `styles.css` 상단 변수 영역
- 배경음악 → `audio/bgm.mp3` 교체

---

## 챕터 3 — AI 이상감지

**파일**: `chapter03/index.html`

- AI 모델 변경 → Teachable Machine에서 새 모델 학습 후 `index.html`의 모델 URL 교체
- 버튼 이미지 → `images/` 안의 png 교체
- 배경음악 → `audio/mystery.mp3` 교체

---

## 공통 사항

- 이미지/음악은 같은 파일명으로 덮어쓰면 코드 수정 없이 적용됨
- 수정 후 해당 HTML을 브라우저에서 열어 확인 → 문제 없으면 배포 ([deploy.md](deploy.md) 참고)
- 잘못 수정한 경우 `bak/` 폴더에서 원본 복구 가능
