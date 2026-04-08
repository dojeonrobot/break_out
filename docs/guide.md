# 📖 프로젝트 수정 가이드

BREAK-OUT 프로젝트를 수정하고 싶을 때 참고하는 문서입니다.

---

## 전체 구조 한눈에 보기

```
BREAK-OUT/
├── index.html              ← ⭐ 메인 화면 (챕터 선택 페이지)
├── assets/images/          ← 메인 화면에서 쓰는 로고, 배경 이미지
│
├── chapter01/              ← 🟢 챕터 1: 도트매트릭스 암호 해독
│   ├── index.html          ← 챕터 1 화면
│   ├── images/             ← 미션 이미지 (001~014번)
│   └── docs/               ← 교사용 PDF 자료
│
├── chapter02/              ← 🟣 챕터 2: 머지큐브 속 비밀
│   ├── index.html          ← 챕터 2 화면 (가장 큰 파일)
│   ├── styles.css          ← 챕터 2 디자인
│   ├── images/             ← 이미지들 (아래에서 자세히 설명)
│   └── audio/              ← 배경음악, 효과음
│
├── chapter03/              ← 🔴 챕터 3: AI 이상감지
│   ├── index.html          ← 챕터 3 화면
│   ├── images/             ← 버튼 이미지
│   └── audio/              ← 배경음악
│
├── config/                 ← 서버 설정 (건드리지 않아도 됨)
├── scripts/                ← 배포 스크립트 (건드리지 않아도 됨)
└── bak/                    ← 원본 백업 (건드리지 않아도 됨)
```

---

## 자주 하는 수정

### 🖼️ "메인 화면의 로고/배경을 바꾸고 싶어요"

`assets/images/` 폴더에 있는 파일을 교체하면 됩니다.

| 파일명 | 역할 |
|--------|------|
| `logo.png` | 상단 도로랜드 로고 |
| `bg.png` | 전체 배경 이미지 |
| `chapter1-logo.png` | 챕터 1 카드 이미지 |
| `chapter2-logo.png` | 챕터 2 카드 이미지 |
| `chapter3-logo.png` | 챕터 3 카드 이미지 |

> 💡 같은 파일명으로 덮어쓰면 코드 수정 없이 바로 적용됩니다.

---

### 📝 "메인 화면의 글자를 바꾸고 싶어요"

`index.html`을 열어서 수정합니다.

- **메인 슬로건** (97~99번째 줄 근처):
  ```html
  기술은 자연을 해치지 않아, 우리가 올바르게 사용한다면..
  도로랜드가 멈춘 지금, 다시 움직이게 할 수 있는 건 너 뿐이야
  ```

- **챕터 제목/설명** — 각 카드 안의 `<h3>`, `<p>` 태그를 찾아 수정

---

### 🔑 "챕터 1의 정답/비밀번호를 바꾸고 싶어요"

`chapter01/index.html`에서 아래 부분을 찾으세요:

- **힌트 비밀번호**: `pwd: "5656"`, `pwd: "4545"` 부분
- **만능키**: `pwdValue === 'doro'` 부분 (교사용 비밀번호)
- **최종 정답**: `'4'`, `'+'`, `'10'`, `'14'` 부분

---

### 🧩 "챕터 2의 퍼즐 정답을 바꾸고 싶어요"

`chapter02/index.html`에서 수정합니다:

- **문양 퍼즐 정답** — `correctOrder = [1, 8, 5, 3]` (나비, 새싹, 달, 아이스 순서)
- **일기장 비밀번호** — `DIARY_PAGE_PASSWORDS` 부분
- **최종 비밀번호** — `DIARY_FINAL_PASSWORD` 부분 (`evolution`)
- **키 퍼즐 정답** — `key === '03'` 부분
- **힌트 비밀번호** — `HINT_PASSWORDS` 부분

---

### 🎨 "챕터 2의 디자인을 바꾸고 싶어요"

`chapter02/styles.css`를 수정합니다.

- **색상 바꾸기** — 파일 맨 위쪽의 색상 변수들:
  ```css
  --cyan: ...      /* 메인 파란색 */
  --magenta: ...   /* 메인 보라색 */
  --card: ...      /* 카드 배경색 */
  ```

- **글꼴 바꾸기** — `font-family` 부분

---

### 📷 "챕터 2의 이미지를 바꾸고 싶어요"

`chapter02/images/` 안에 종류별로 정리되어 있습니다:

| 폴더 | 내용 | 파일 |
|------|------|------|
| `diary/` | 일기장 페이지 | Diary1.png ~ Diary7.png |
| `cubes/` | 큐브 아이콘 | cube1~4.png |
| `patterns/` | 코덱스 문양 | codex_pattern*.png |
| `missions/` | 스토리 웹툰 | mission_start.png, mission_complete.png |
| `icons/` | 문양 선택 퍼즐용 아이콘 | butterfly.png, moon.png 등 12개 |
| `qr/` | QR 코드 | qr-1~3.png |

> 💡 같은 이름으로 이미지를 교체하면 코드 수정 없이 적용됩니다.

---

### 🤖 "챕터 3의 AI 모델을 바꾸고 싶어요"

`chapter03/index.html`에서 이 줄을 찾으세요:

```javascript
const URL = "https://teachablemachine.withgoogle.com/models/sRbjPP-Cq/";
```

[Teachable Machine](https://teachablemachine.withgoogle.com/)에서 새 모델을 학습시킨 후, 여기에 새 모델 URL을 넣으면 됩니다.

---

### 🎵 "배경음악을 바꾸고 싶어요"

| 챕터 | 파일 위치 |
|------|-----------|
| 챕터 2 | `chapter02/audio/bgm.mp3` |
| 챕터 3 | `chapter03/audio/mystery.mp3` |

같은 이름의 mp3 파일로 교체하면 됩니다.

---

## 수정 후 반영 순서

1. 파일 수정
2. 브라우저에서 해당 HTML 파일을 열어서 동작 확인
3. 문제 없으면 서버에 배포 (→ [배포 가이드](deploy.md) 참고)

---

## 파일을 잘못 수정했을 때

`bak/` 폴더에 원본이 보관되어 있으니, 거기서 해당 파일을 복사하면 복구할 수 있습니다.
