# QOD-21: run the private-alpha tutorial chain (P00-01..P00-05 + C1-01) on Windows.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File Server\Health\Smoke\run_alpha_p00.ps1
#
# Same gates as the Linux CI job e2e-alpha-p00, and the same endurance pools.
# The alpha profile is private-alpha content only: this starts a local server
# with the gates on for this process, it never edits appsettings.json.

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$Project = Join-Path $Root 'Server\Health\Health.csproj'
$Binary = Join-Path $Root 'Server\Health\bin\Release\net10.0\Health.dll'
$Scenario = Join-Path $Root 'Server\Health\Smoke\e2e_p1.py'
$Port = if ($env:E2E_PORT) { $env:E2E_PORT } else { '5090' }
$BaseUrl = "http://127.0.0.1:$Port"
$LogPath = Join-Path $env:TEMP "alpha-p00-server-$Port.log"
$ErrPath = Join-Path $env:TEMP "alpha-p00-server-$Port.err.log"

Write-Host "==> Building server (Release)"
dotnet build $Project --configuration Release
if ($LASTEXITCODE -ne 0) { throw "build failed" }

$env:P1__AlphaProfile__Enabled = 'true'
$env:P1__QuestAccept__Enabled = 'true'
$env:P1__Interact__Enabled = 'true'
$env:P1__QuestTurnIn__Enabled = 'true'
$env:P1__Equipment__Enabled = 'true'
$env:P1__CombatV2__Enabled = 'true'
$env:P1__CombatDamage__Enabled = 'true'
$env:P1__MobBehavior__Enabled = 'true'
$env:P1__AlphaLoot__GrantEnabled = 'true'
$env:P1World__StartingHp = '2000'
$env:P1World__StartingMaxHp = '2000'
$env:P1World__StartingMp = '500'
$env:P1World__StartingMaxMp = '500'

Write-Host "==> Starting server (profile=alpha-p00, port=$Port)"
$Server = Start-Process -FilePath 'dotnet' `
    -ArgumentList @($Binary, '--urls', $BaseUrl) `
    -RedirectStandardOutput $LogPath -RedirectStandardError $ErrPath `
    -PassThru -NoNewWindow

try {
    $healthy = $false
    for ($attempt = 1; $attempt -le 60; $attempt++) {
        try {
            Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $healthy = $true
            Write-Host "==> Server healthy after ${attempt}s"
            break
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $healthy) { throw "server did not become healthy within 60s (see $LogPath)" }

    Write-Host "==> Running E2E scenario (mode=alpha-p00)"
    python $Scenario $BaseUrl 'alpha-p00'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "==> E2E FAIL (profile=alpha-p00); server log tail:"
        Get-Content $ErrPath -Tail 40
        exit 1
    }
    Write-Host "==> E2E PASS (profile=alpha-p00)"
} finally {
    if ($Server -and -not $Server.HasExited) {
        Stop-Process -Id $Server.Id -Force
        Write-Host "==> Server stopped (PID $($Server.Id))"
    }
}
