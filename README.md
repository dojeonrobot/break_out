# 🏰 DOROLAND Break Out Adventure

교육용 방탈출(Break-Out) 웹 애플리케이션

## 실행 방법

별도 빌드 없이 **`index.html`을 브라우저에서 열면** 바로 실행됩니다.

```
index.html 더블 클릭 → 메인 대시보드 → 챕터 카드 클릭 → 각 미션 시작
```

> ⚠️ Chapter 03은 **웹캠**과 **Web Serial API**를 사용하므로 Chrome/Edge 브라우저를 권장합니다.

## 프로젝트 구조

```
BREAK-OUT/
├── index.html              ← 메인 대시보드 허브
├── assets/images/          ← 공용 로고/배경 이미지
│
├── chapter01/              ← 사파리 구역: 도트매트릭스 암호 해독
│   ├── index.html
│   ├── images/             ← 미션/힌트 이미지 (001~014)
│   └── docs/               ← PDF 교사자료
│
├── chapter02/              ← 하모니아 구역: 머지큐브 속 비밀
│   ├── index.html
│   ├── styles.css
│   ├── images/             ← diary, cubes, patterns, missions, icons, qr
│   └── audio/              ← BGM + 음계 사운드
│
└── chapter03/              ← 회전목마 구역: AI 이상감지 시스템
    ├── index.html
    ├── images/
    └── audio/
```

## 챕터 소개

| 챕터 | 구역 | 미션 |
|------|------|------|
| Chapter 01 | 사파리 | 도트매트릭스 패턴을 분석하여 마스터 키 해독 |
| Chapter 02 | 하모니아 | Teachable Machine AI + Arduino 연동 이상감지 |
| Chapter 03 | 회전목마 | 머지큐브, 일기장, 슬라이드 퍼즐로 문양 수집 |

## 기술 스택

- HTML5 / CSS3 / Vanilla JavaScript
- Tailwind CSS (CDN)
- TensorFlow.js + Teachable Machine
- Web Serial API (Arduino 연동)
- Google Fonts (Hahmlet, Inter, Noto Sans KR)

---

© DOROLAND Break Out Adventure. All rights reserved.
