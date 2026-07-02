<#
.SYNOPSIS
    BREAK-OUT deploy script (git commit + push + server deploy)

.EXAMPLE
    .\scripts\deploy.ps1
    .\scripts\deploy.ps1 -Message "chapter01 이미지 교체"
#>

param(
    [string]$KeyFile = "hy_key.pem",
    [string]$Message = ""
)

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

# -- git commit + push --
Write-Host "[1/7] Git commit & push..." -ForegroundColor Cyan
Push-Location $ProjectRoot
$changes = git status --porcelain
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
$tarFile = Join-Path $ProjectRoot "breakout-deploy.tar.gz"

$excludes = @(
    "--exclude=.git",
    "--exclude=.gitignore",
    "--exclude=config",
    "--exclude=scripts",
    "--exclude=bak",
    "--exclude=docs",
    "--exclude=*.tar.gz",
    "--exclude=*.pem",
    "--exclude=CLAUDE.md"
)

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
$deployOut = ssh -i $KEY $SSH_TARGET "chmod -R u+rwX ${RemoteDir} && rm -rf ${RemoteDir}/* && cd ${RemoteDir} && tar -xzf /tmp/breakout-deploy.tar.gz --no-same-permissions && rm /tmp/breakout-deploy.tar.gz && chmod 755 /home/ubuntu && chmod -R 755 ${RemoteDir}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tarFile -ErrorAction SilentlyContinue
    Write-Host "[ERROR] Server deploy step failed" -ForegroundColor Red
    Write-Host "  $deployOut" -ForegroundColor DarkGray
    exit 1
}

# cache bust: upload and run script
$bustScript = Join-Path $ProjectRoot "scripts\cache-bust.sh"
scp -i $KEY $bustScript "${SSH_TARGET}:/tmp/cache-bust.sh" 2>&1 | Out-Null
$bustOut = ssh -i $KEY $SSH_TARGET "sed -i 's/\r\$//' /tmp/cache-bust.sh && bash /tmp/cache-bust.sh $ts $RemoteDir && rm /tmp/cache-bust.sh" 2>&1
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
