# 🚀 배포 가이드

## 접속 정보

| 항목 | 값 |
|------|-----|
| **사이트 주소** | https://breakout.doroedu.co.kr |
| **서버 IP** | 210.109.15.216 |
| **서버 계정** | ubuntu |
| **키 파일** | `C:\Users\pc\Documents\PW\hy_key.pem` |
| **서버 경로** | `/home/ubuntu/breakout/` |
| **GitHub** | https://github.com/dojeonrobot/break_out |

---

## 배포 방법 (수정 후 반영하기)

### 1단계: 수정한 파일 GitHub에 올리기

```powershell
cd C:\Users\pc\Documents\BREAK-OUT
git add -A
git commit -m "변경 내용 설명"
git push
```

### 2단계: 서버에 반영하기

```powershell
$KEY = "C:\Users\pc\Documents\PW\hy_key.pem"
$SSH = "ubuntu@210.109.15.216"

# 압축
tar -czf breakout-deploy.tar.gz --exclude=.git --exclude=bak --exclude=config --exclude=scripts --exclude="*.tar.gz" -C . .

# 업로드 + 배포
scp -i $KEY breakout-deploy.tar.gz "${SSH}:/tmp/breakout-deploy.tar.gz"
ssh -i $KEY $SSH "rm -rf /home/ubuntu/breakout/* && cd /home/ubuntu/breakout && tar -xzf /tmp/breakout-deploy.tar.gz && rm /tmp/breakout-deploy.tar.gz && chmod -R 755 /home/ubuntu/breakout"

# 정리
Remove-Item breakout-deploy.tar.gz
```

> 💡 또는 배포 스크립트를 사용할 수도 있습니다:
> ```powershell
> .\scripts\deploy.ps1
> ```

### 3단계: 확인하기

브라우저에서 https://breakout.doroedu.co.kr 접속해서 변경사항이 반영됐는지 확인합니다.

---

## 서버 상태 확인

```powershell
# SSH 접속
ssh -i "C:\Users\pc\Documents\PW\hy_key.pem" ubuntu@210.109.15.216

# nginx 상태 확인
sudo systemctl status nginx

# 에러 로그 확인
sudo tail -20 /var/log/nginx/error.log
```

---

## SSL 인증서

- Let's Encrypt 인증서가 설치되어 있으며, **자동 갱신** 됩니다.
- 만료일: 2026-07-06 (3개월마다 자동 갱신)
- 수동 갱신이 필요한 경우:

```bash
sudo certbot renew
```

---

## 주의사항

- `bak/` 폴더는 원본 백업용이므로 서버에 올라가지 않습니다.
- `config/`, `scripts/` 폴더도 서버에 올라가지 않습니다 (로컬 관리용).
- 이미지 파일이 많아 첫 배포는 시간이 걸릴 수 있습니다 (~130MB).
