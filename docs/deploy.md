# 배포 가이드

## 접속 정보

| 항목 | 값 |
|------|-----|
| 사이트 | https://breakout.doroedu.co.kr |
| 서버 IP | 210.109.15.216 |
| 계정 | ubuntu |
| 키 파일 | `C:\Users\pc\Documents\PW\hy_key.pem` |
| 서버 경로 | `/home/ubuntu/breakout/` |
| GitHub | https://github.com/dojeonrobot/break_out |

---

## 새 PC에서 처음 사용할 때

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

PowerShell 스크립트 실행 허용 설정. PC마다 한 번만 하면 됨.

---

## 배포 순서

배포 스크립트 하나로 **git 커밋 + push + 서버 반영 + 검증**까지 자동으로 처리됩니다.

```powershell
cd C:\Users\pc\Documents\BREAK-OUT
.\scripts\deploy.ps1 -Message "변경 내용 설명"
```

- `-Message`를 생략하면 `deploy 2026-07-02 11:30` 형식의 기본 메시지로 커밋됩니다.
- 변경사항이 없으면 커밋은 건너뛰고 배포만 진행합니다.
- 배포 전에 GitHub 최신 내용을 자동으로 pull 하므로, 다른 PC에서 올린 수정을 덮어쓰지 않습니다. (충돌 시 배포가 중단되고 에러가 표시됩니다)
- 마지막에 사이트 주요 URL이 정상(200)인지 자동 확인하고, 실패 시 빨간 에러가 표시됩니다.

> 💡 **여러 PC에서 작업하는 경우**: 각 PC에서 최초 한 번 `git pull`을 해서 이 스크립트를 받아두면, 이후에는 어느 PC에서 배포하든 커밋/pull/push가 자동으로 처리됩니다.

---

## SSH 접속

```powershell
ssh -i "C:\Users\pc\Documents\PW\hy_key.pem" ubuntu@210.109.15.216
```

서버에서 nginx 상태 확인:
```bash
sudo systemctl status nginx
sudo tail -20 /var/log/nginx/error.log
```

---

## SSL 인증서

- Let's Encrypt 인증서 사용, 자동 갱신됨
- 만료일: 2026-07-06
- 수동 갱신: `sudo certbot renew`

---

## 참고

- `bak/`, `config/`, `scripts/`는 서버에 올라가지 않음 (로컬 관리용)
- 전체 배포 용량 약 130MB
