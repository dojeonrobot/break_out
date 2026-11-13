<#
.SYNOPSIS
    BREAK-OUT deploy script (git commit + push + server deploy)

.EXAMPLE
    .\scripts\deploy.ps1
    .\scripts\deploy.ps1 -Message "chapter01 이미지 교체"
    .\scripts\deploy.ps1 -Message "chapter03 허브" -Only chapter03/index.html,chapter03/hub.js

.PARAMETER Only
    이번 배포에서 고친 파일·폴더(저장소 기준 경로). 주면, 그 밖의 변경이 작업 폴더에
    있을 때 커밋·업로드 전에 멈춘다. 압축은 작업 폴더 전체를 올리므로 일부만 올리는
    기능이 아니라, 다른 사람·다른 세션의 작업이 섞여 올라가는 것을 막는 확인이다.
#>

param(
    [string]$KeyFile = "hy_key.pem",
    [string]$Message = "",
    [string[]]$Only = @()
)

# -Only a,b 를 -File 로 넘기면 한 문자열로 들어오므로 쉼표로 다시 나눈다
$Only = @($Only | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

# 작업 폴더의 변경 중 $Scope 밖에 있는 경로를 돌려준다 ($Scope 가 비면 변경 전부)
function Get-OutOfScope([string[]]$Scope) {
    $prevEnc = [Console]::OutputEncoding
    [Console]::OutputEncoding = [Text.Encoding]::UTF8
    $lines = git -c core.quotepath=false status --porcelain --untracked-files=all
    [Console]::OutputEncoding = $prevEnc
    $norm = @($Scope | ForEach-Object { (($_ -replace '\\', '/') -replace '^\./', '').TrimEnd('/') } | Where-Object { $_ })
    $found = @()
    foreach ($line in $lines) {
        if (-not $line -or $line.Length -lt 4) { continue }
        $p = $line.Substring(3)
        $parts = if ($p -match ' -> ') { $p -split ' -> ' } else { @($p) }
        foreach ($one in $parts) {
            $one = $one.Trim('"')
            $inScope = $false
            foreach ($s in $norm) {
                if ($one -eq $s -or $one.StartsWith("$s/", [StringComparison]::OrdinalIgnoreCase)) { $inScope = $true; break }
            }
            if (-not $inScope) { $found += $one }
        }
    }
    return ,$found
}

$HOST_IP    = if ($env:BREAKOUT_HOST) { $env:BREAKOUT_HOST } else { "210.109.15.216" }
$RemoteUser = "ubuntu"
$RemoteDir  = "/home/ubuntu/breakout"
$SSH_TARGET = "${RemoteUser}@${HOST_IP}"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# -- Key file --
$KEY = Join-Path $ProjectRoot $KeyFile
if (-not (Test-Path $KEY)) {
    $KEY = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "PW\$KeyFile"
}
if (-not (Test-Path $KEY)) {
    Write-Host "[ERROR] Key file '$KeyFile' not found." -ForegroundColor Red
    exit 1
}

# -- git sync: commit -> pull --rebase -> push --
Write-Host "[1/7] Git sync (commit + pull + push)..." -ForegroundColor Cyan
Push-Location $ProjectRoot
$changes = git status --porcelain
if ($Only.Count -gt 0) {
    $foreign = Get-OutOfScope $Only
    if ($foreign.Count -gt 0) {
        Pop-Location
        Write-Host "[ERROR] -Only 범위 밖의 변경이 있어 멈춤 (커밋·업로드 안 함). 누구 작업인지 확인하고 빼 둔 뒤 다시 실행:" -ForegroundColor Red
        $foreign | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        exit 1
    }
}
if ($changes) {
    if (-not $Message) { $Message = "deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
    git add -A
    git commit -m $Message | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Host "[ERROR] git commit failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  committed: $Message" -ForegroundColor Green
} else {
    Write-Host "  no changes to commit" -ForegroundColor Green
}

# pull first so a deploy from this PC never overwrites another PC's pushed work
$pullOut = git pull --rebase 2>&1
if ($LASTEXITCODE -ne 0) {
    git rebase --abort 2>&1 | Out-Null
    Pop-Location
    Write-Host "[ERROR] git pull failed - GitHub의 변경과 충돌. 직접 해결 후 다시 배포하세요." -ForegroundColor Red
    Write-Host "  $pullOut" -ForegroundColor DarkGray
    exit 1
}
Write-Host "  pulled (GitHub 최신과 동기화됨)" -ForegroundColor Green

$pushOut = git push 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [WARN] git push failed (deploy continues)" -ForegroundColor Yellow
    Write-Host "  $pushOut" -ForegroundColor DarkGray
} else {
    Write-Host "  pushed" -ForegroundColor Green
}
Pop-Location

# -- SSH test --
Write-Host "[2/7] SSH connecting to ${HOST_IP}..." -ForegroundColor Cyan
$sshResult = ssh -i $KEY -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_TARGET "echo ok" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SSH connection failed" -ForegroundColor Red
    Write-Host "  $sshResult" -ForegroundColor DarkGray
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

# -- tar --
Write-Host "[3/7] Compressing..." -ForegroundColor Cyan
# -Only: 커밋 뒤에는 작업 폴더가 깨끗해야 한다. 그 사이 새로 생긴 변경은 다른 작업이다.
if ($Only.Count -gt 0) {
    Push-Location $ProjectRoot
    $late = Get-OutOfScope @()
    Pop-Location
    if ($late.Count -gt 0) {
        Write-Host "[ERROR] 커밋 뒤에 작업 폴더가 바뀌어 멈춤 (업로드 안 함, 커밋·푸시는 이미 됨):" -ForegroundColor Red
        $late | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        exit 1
    }
}
$tarFile = Join-Path $ProjectRoot "breakout-deploy.tar.gz"

$excludes = @(
    "--exclude=.git",
    "--exclude=.gitignore",
    "--exclude=config",
    "--exclude=scripts",
    "--exclude=bak",
    "--exclude=docs",
    "--exclude=server",
    "--exclude=*.tar.gz",
    "--exclude=*.pem",
    "--exclude=CLAUDE.md",
    "--exclude=desktop.ini",
    "--exclude=Thumbs.db"
)

# Windows read-only folders (e.g. from a desktop.ini icon customization) get
# archived as dr-xr-xr-x, which makes extraction on the server fail.
Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.git\\?' -and ($_.Attributes -band [IO.FileAttributes]::ReadOnly) } |
    ForEach-Object {
        Write-Host "  clearing read-only attribute: $($_.FullName)" -ForegroundColor Yellow
        attrib -R $_.FullName
    }

Push-Location $ProjectRoot
tar -czf $tarFile $excludes -C $ProjectRoot .
Pop-Location

$sizeMB = [math]::Round((Get-Item $tarFile).Length / 1MB, 1)
Write-Host "  ${sizeMB}MB" -ForegroundColor Green

# -- mkdir --
Write-Host "[4/7] Preparing server..." -ForegroundColor Cyan
ssh -i $KEY $SSH_TARGET "mkdir -p $RemoteDir" 2>&1 | Out-Null

# -- upload --
Write-Host "[5/7] Uploading..." -ForegroundColor Cyan
scp -i $KEY -C $tarFile "${SSH_TARGET}:/tmp/breakout-deploy.tar.gz" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tarFile -ErrorAction SilentlyContinue
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    exit 1
}

# -- extract + permission + cache bust --
Write-Host "[6/7] Deploying..." -ForegroundColor Cyan
$ts = [int](Get-Date -UFormat %s)
# Unpack into a staging dir and swap it in only on success, so a failed extract
# never leaves the live site emptied out.
$remoteCmd = @(
    "rm -rf ${RemoteDir}.new",
    "mkdir -p ${RemoteDir}.new",
    "tar -xzf /tmp/breakout-deploy.tar.gz -C ${RemoteDir}.new --no-same-permissions --delay-directory-restore",
    "rm -f /tmp/breakout-deploy.tar.gz",
    "chmod -R u+rwX ${RemoteDir}",
    "rm -rf ${RemoteDir}",
    "mv ${RemoteDir}.new ${RemoteDir}",
    "chmod 755 /home/ubuntu",
    "chmod -R 755 ${RemoteDir}"
) -join " && "
$deployOut = ssh -i $KEY $SSH_TARGET $remoteCmd 2>&1
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tarFile -ErrorAction SilentlyContinue
    Write-Host "[ERROR] Server deploy step failed (live site left untouched)" -ForegroundColor Red
    Write-Host "  $deployOut" -ForegroundColor DarkGray
    exit 1
}

# cache bust: upload and run script
$bustScript = Join-Path $ProjectRoot "scripts\cache-bust.sh"
scp -i $KEY $bustScript "${SSH_TARGET}:/tmp/cache-bust.sh" 2>&1 | Out-Null
$bustOut = ssh -i $KEY $SSH_TARGET "sed -i 's/\r`$//' /tmp/cache-bust.sh && bash /tmp/cache-bust.sh $ts $RemoteDir && rm /tmp/cache-bust.sh" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cache bust failed" -ForegroundColor Red
    Write-Host "  $bustOut" -ForegroundColor DarkGray
    exit 1
}

# -- cleanup --
Remove-Item $tarFile -ErrorAction SilentlyContinue

# -- verify --
Write-Host "[7/7] Verifying..." -ForegroundColor Cyan
$failed = $false
foreach ($path in @("index.html", "chapter01/images/001.png", "images/logo.png")) {
    $code = curl.exe -s -o NUL -w "%{http_code}" "https://breakout.doroedu.co.kr/$path"
    if ($code -ne "200") {
        Write-Host "  [FAIL] $path => HTTP $code" -ForegroundColor Red
        $failed = $true
    }
}
if ($failed) {
    Write-Host "[ERROR] Verification failed - site may be broken" -ForegroundColor Red
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

# -- done --
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETE" -ForegroundColor Green
Write-Host "  https://breakout.doroedu.co.kr" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
