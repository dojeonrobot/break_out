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

## 배포 순서

### 1. GitHub에 올리기

```powershell
cd C:\Users\pc\Documents\BREAK-OUT
git add -A
git commit -m "변경 내용 설명"
git push
```

### 2. 서버에 반영하기

```powershell
.\scripts\deploy.ps1
```

### 3. 확인

https://breakout.doroedu.co.kr 접속해서 확인.

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
