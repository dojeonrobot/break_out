<#
.SYNOPSIS
    BREAK-OUT 배포 스크립트 (PowerShell)

.DESCRIPTION
    DoroBus deploy.ps1 패턴 기반.
    정적 파일만 배포: SSH 확인 → tar 압축 → SCP 업로드 → 압축 해제

.EXAMPLE
    .\scripts\deploy.ps1                    # 기본 배포
    .\scripts\deploy.ps1 -KeyFile hy_key.pem  # 키 파일 지정
#>

param(
    [string]$KeyFile = "hy_key.pem"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ══════════════════════════════════════════
# 배포 설정 — 카카오 클라우드 서버 정보
# ══════════════════════════════════════════
$HOST_IP    = if ($env:BREAKOUT_HOST) { $env:BREAKOUT_HOST } else { "210.109.15.216" }
$RemoteUser = "ubuntu"
$RemoteDir  = "/home/ubuntu/breakout"
$SSH_TARGET = "${RemoteUser}@${HOST_IP}"
# ══════════════════════════════════════════

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# ── 키 파일 확인 ──
$KEY = Join-Path $ProjectRoot $KeyFile
if (-not (Test-Path $KEY)) {
    $KEY = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "PW\$KeyFile"
}
if (-not (Test-Path $KEY)) {
    Write-Host "❌ 키 파일 '$KeyFile'을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# ── SSH 연결 테스트 ──
Write-Host "🔗 ${HOST_IP} 연결 확인..." -ForegroundColor Cyan
$sshResult = ssh -i $KEY -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_TARGET "echo ok" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ SSH 연결 실패" -ForegroundColor Red
    Write-Host "   $sshResult" -ForegroundColor DarkGray
    exit 1
}
Write-Host "   ✓ SSH 연결 성공" -ForegroundColor Green

# ── 배포 시작 ──
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🚀 BREAK-OUT 배포 시작" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# ── tar 압축 (빠른 전송) ──
$tarFile = Join-Path $ProjectRoot "breakout-deploy.tar.gz"
Write-Host "   📦 압축 중..." -ForegroundColor DarkGray

# 배포에 포함할 파일들만 압축 (.git, node_modules 제외)
$excludes = @(
    "--exclude=.git",
    "--exclude=.gitignore",
    "--exclude=config",
    "--exclude=scripts",
    "--exclude=bak",
    "--exclude=*.tar.gz"
)

Push-Location $ProjectRoot
tar -czf $tarFile $excludes -C $ProjectRoot .
Pop-Location

$sizeMB = [math]::Round((Get-Item $tarFile).Length / 1MB, 1)
Write-Host "   ✓ 압축 완료 (${sizeMB}MB)" -ForegroundColor Green

# ── 서버 준비 ──
Write-Host "   🗂️  서버 디렉토리 준비..." -ForegroundColor DarkGray
ssh -i $KEY $SSH_TARGET "mkdir -p $RemoteDir" 2>&1 | Out-Null

# ── 업로드 ──
Write-Host "   📤 업로드 중..." -ForegroundColor DarkGray
scp -i $KEY -C $tarFile "${SSH_TARGET}:/tmp/breakout-deploy.tar.gz" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tarFile -ErrorAction SilentlyContinue
    Write-Host "❌ 업로드 실패" -ForegroundColor Red
    exit 1
}

# ── 서버에서 압축 해제 ──
Write-Host "   📂 배포 중..." -ForegroundColor DarkGray
ssh -i $KEY $SSH_TARGET @"
    rm -rf ${RemoteDir}/*
    cd ${RemoteDir}
    tar -xzf /tmp/breakout-deploy.tar.gz
    rm /tmp/breakout-deploy.tar.gz
    chmod -R 755 ${RemoteDir}
"@ 2>&1 | Out-Null

# ── 정리 ──
Remove-Item $tarFile -ErrorAction SilentlyContinue

# ── nginx 설정 확인 ──
Write-Host "   🔄 Nginx 설정 확인..." -ForegroundColor DarkGray
$nginxCheck = ssh -i $KEY $SSH_TARGET "sudo nginx -t 2>&1 && sudo systemctl reload nginx 2>&1"
Write-Host "   ✓ Nginx 리로드 완료" -ForegroundColor Green

# ── 결과 ──
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ BREAK-OUT 배포 완료!" -ForegroundColor Green
Write-Host "   🌐 http://${HOST_IP}" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
