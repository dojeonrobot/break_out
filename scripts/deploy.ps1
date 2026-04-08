<#
.SYNOPSIS
    BREAK-OUT deploy script

.EXAMPLE
    .\scripts\deploy.ps1
#>

param(
    [string]$KeyFile = "hy_key.pem"
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

# -- SSH test --
Write-Host "[1/5] SSH connecting to ${HOST_IP}..." -ForegroundColor Cyan
$sshResult = ssh -i $KEY -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_TARGET "echo ok" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SSH connection failed" -ForegroundColor Red
    Write-Host "  $sshResult" -ForegroundColor DarkGray
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

# -- tar --
Write-Host "[2/5] Compressing..." -ForegroundColor Cyan
$tarFile = Join-Path $ProjectRoot "breakout-deploy.tar.gz"

$excludes = @(
    "--exclude=.git",
    "--exclude=.gitignore",
    "--exclude=config",
    "--exclude=scripts",
    "--exclude=bak",
    "--exclude=docs",
    "--exclude=*.tar.gz"
)

Push-Location $ProjectRoot
tar -czf $tarFile $excludes -C $ProjectRoot .
Pop-Location

$sizeMB = [math]::Round((Get-Item $tarFile).Length / 1MB, 1)
Write-Host "  ${sizeMB}MB" -ForegroundColor Green

# -- mkdir --
Write-Host "[3/5] Preparing server..." -ForegroundColor Cyan
ssh -i $KEY $SSH_TARGET "mkdir -p $RemoteDir" 2>&1 | Out-Null

# -- upload --
Write-Host "[4/5] Uploading..." -ForegroundColor Cyan
scp -i $KEY -C $tarFile "${SSH_TARGET}:/tmp/breakout-deploy.tar.gz" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tarFile -ErrorAction SilentlyContinue
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    exit 1
}

# -- extract + permission + cache bust --
Write-Host "[5/5] Deploying..." -ForegroundColor Cyan
$ts = [int](Get-Date -UFormat %s)
ssh -i $KEY $SSH_TARGET "rm -rf ${RemoteDir}/* && cd ${RemoteDir} && tar -xzf /tmp/breakout-deploy.tar.gz && rm /tmp/breakout-deploy.tar.gz && chmod 755 /home/ubuntu && chmod -R 755 ${RemoteDir}" 2>&1 | Out-Null

# cache bust: upload and run script
$bustScript = Join-Path $ProjectRoot "scripts\cache-bust.sh"
scp -i $KEY $bustScript "${SSH_TARGET}:/tmp/cache-bust.sh" 2>&1 | Out-Null
ssh -i $KEY $SSH_TARGET "bash /tmp/cache-bust.sh $ts $RemoteDir && rm /tmp/cache-bust.sh" 2>&1 | Out-Null

# -- cleanup --
Remove-Item $tarFile -ErrorAction SilentlyContinue

# -- done --
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETE" -ForegroundColor Green
Write-Host "  https://breakout.doroedu.co.kr" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
