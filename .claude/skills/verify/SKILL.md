---
name: verify
description: DOROLAND Break Out 정적 사이트를 로컬에서 띄우고 브라우저로 구동해 변경을 눈으로 확인하는 방법
---

# 로컬 실행 및 검증

빌드 없음. 정적 파일이므로 로컬 HTTP 서버만 띄우면 된다 (file:// 로 열면 상대경로 자산은 되지만 서버 환경과 다르므로 서버 권장).

```bash
cd /c/Users/dlgus/break_out
python -m http.server 8899 --bind 127.0.0.1 &
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8899/chapter04/index.html
```

## 브라우저 구동 (Playwright + 설치된 Chrome)

Node는 없다. Python Playwright를 쓰되 브라우저는 시스템 Chrome을 재사용한다 (`channel="chrome"` — 별도 브라우저 다운로드 불필요).

```bash
python -m pip install playwright        # 브라우저 다운로드는 하지 말 것
PYTHONIOENCODING=utf-8 python drive.py  # 한글 출력 시 필수 (cp949 UnicodeEncodeError)
```

```python
b = p.chromium.launch(channel="chrome", headless=True)
```

## 챕터 진입 경로

- 허브(`index.html`) 카드 클릭 → 비밀번호 모달 → **전 챕터 공통 `0101`** (`checkPassword()`가 단일 값 비교) → `chapterData[id].url` 로 이동.
- 카드 셀렉터: `div[onclick*='handleEnterChapter(4']`

## chapter04 (트레이스 브레이크) 구동 시 함정

- 첫 진입에 **4단계 튜토리얼 오버레이**(`#tutOverlay`)가 뜬다. 클릭을 가로채므로 `#tutSkip` 을 먼저 누를 것.
- 게임 본 흐름: 좌측 3개 슬롯(`input[data-input="safari|harmonia|carousel"]`)에 CSV 3개 업로드 → 3/3 되면 차트·수사노트 활성.
  테스트용 CSV는 `docs/chapter04-kit/data/` 에 있다 (배포 제외 자료).
- 힌트 모달: `#hintFab` → `#pwInput` 에 `0101`.
- 기밀 기록실: `#vaultBtn` → 탭 `.vault-tab[data-tab="badges"|"calendar"]` → `#vlPw` 에 **탭별로 다른 코드** (badges=`PQUDJ`, calendar=`CAFLY`). 입력창이 자동으로 대문자로 바꾸고 영숫자 외 문자는 지운다. 코드는 `index.html` 의 `VAULT_UNLOCK_CODES` 에 있다.
- 슬롯은 파일이 채워지면 `disabled` 되므로, 한 슬롯에 두 번 올리려면 페이지를 새로 로드해야 한다.
