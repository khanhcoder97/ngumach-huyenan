# QOD-24 Q8: private-alpha server launcher for Windows.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File Server\Health\Smoke\launch_alpha.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File Server\Health\Smoke\launch_alpha.ps1 -Status
#   powershell -NoProfile -ExecutionPolicy Bypass -File Server\Health\Smoke\launch_alpha.ps1 -Stop
#
# Starts the P1 server with the alpha gate set on this process only - it never edits
# appsettings.json, so the release configuration keeps every P1:* gate OFF. The launcher
# owns exactly one PID: it records the process id and its start time in a per-port file,
# and -Stop kills only that process after re-checking the recorded start time, so a
# recycled PID is never a stranger's. A port that already answers is refused at start:
# the launcher does not stop what it did not start.
#
# Identity note: /health returns status/service/correlationId and carries no instance
# field, so "which server is this" is answered here by the PID, the binary path and its
# timestamp. A published build/instance identity is a wire change and belongs to the
# GET /p1/capability packet, not to this script.

param(
    [int]$Port = 5081,
    [ValidateSet('alpha', 'dev')] [string]$GateSet = 'alpha',
    [switch]$Build,
    [switch]$Stop,
    [switch]$Status
)

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$Project = Join-Path $Root 'Server\Health\Health.csproj'
$Binary = Join-Path $Root 'Server\Health\bin\Release\net10.0\Health.dll'
$BaseUrl = "http://127.0.0.1:$Port"
$PidFile = Join-Path $env:TEMP "p1-alpha-$Port.pid"
$LogPath = Join-Path $env:TEMP "p1-alpha-$Port.log"
$ErrPath = Join-Path $env:TEMP "p1-alpha-$Port.err.log"

function Get-Health {
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 3
        return ($response.Content | ConvertFrom-Json)
    } catch {
        return $null
    }
}

if ($Stop) {
    if (-not (Test-Path $PidFile)) {
        throw "no owned PID file at $PidFile - nothing to stop (the launcher never kills a process it did not start)"
    }
    $recorded = Get-Content $PidFile -Raw | ConvertFrom-Json
    $proc = Get-Process -Id $recorded.Id -ErrorAction SilentlyContinue
    if ($null -eq $proc) {
        Write-Host "==> PID $($recorded.Id) is already gone; removing $PidFile"
    } elseif ($proc.StartTime.ToString('o') -ne $recorded.StartTime) {
        # The PID was recycled by someone else between the two runs. Never touch it.
        throw "PID $($recorded.Id) now belongs to a different process (start time mismatch) - refusing to stop it"
    } else {
        Stop-Process -Id $proc.Id -Force
        $proc.WaitForExit(15000) | Out-Null
        Write-Host "==> stopped owned PID $($proc.Id)"
    }
    Remove-Item $PidFile -Force
    if (Get-Health) {
        Write-Host "==> WARNING: $BaseUrl still answers after the owned PID exited"
        exit 1
    }
    Write-Host "==> port_released=OK $BaseUrl"
    exit 0
}

if ($Status) {
    if (-not (Test-Path $PidFile)) {
        Write-Host "==> no owned PID file at $PidFile"
    } else {
        $recorded = Get-Content $PidFile -Raw | ConvertFrom-Json
        $proc = Get-Process -Id $recorded.Id -ErrorAction SilentlyContinue
        Write-Host "==> owned PID $($recorded.Id) alive=$($null -ne $proc) started=$($recorded.StartTime) binary=$($recorded.Binary)"
    }
    $health = Get-Health
    if ($health) {
        Write-Host "==> health status=$($health.status) service=$($health.service) correlationId=$($health.correlationId)"
    } else {
        Write-Host "==> $BaseUrl does not answer"
    }
    exit 0
}

if (Get-Health) {
    throw "$BaseUrl already answers. The launcher only stops servers it starts, so stop it by its own means or pick another port (-Port 5082)."
}

if ($Build -or -not (Test-Path $Binary)) {
    Write-Host "==> Building server (Release)"
    dotnet build $Project --configuration Release
    if ($LASTEXITCODE -ne 0) { throw "build failed" }
}

$Gates = [ordered]@{
    'P1__AlphaProfile__Enabled' = 'false'
    'P1__QuestAccept__Enabled' = 'false'
    'P1__Interact__Enabled' = 'false'
    'P1__QuestTurnIn__Enabled' = 'false'
    'P1__Equipment__Enabled' = 'false'
    'P1__CombatV2__Enabled' = 'false'
    'P1__CombatDamage__Enabled' = 'false'
    'P1__MobBehavior__Enabled' = 'false'
    'P1__AlphaLoot__GrantEnabled' = 'false'
    'P1__DeathReturn__Enabled' = 'false'
}
if ($GateSet -eq 'dev') {
    'P1__QuestAccept__Enabled', 'P1__Interact__Enabled', 'P1__QuestTurnIn__Enabled',
    'P1__Equipment__Enabled' | ForEach-Object { $Gates[$_] = 'true' }
} else {
    # DeathReturn is on here even though the e2e alpha profile leaves it off: a client
    # testing the death loop needs the route, and the route is mapped only when
    # AlphaProfile AND DeathReturn are both on. appsettings.json still keeps both false.
    $Gates.Keys | ForEach-Object { $Gates[$_] = 'true' }
    $env:P1World__StartingHp = '2000'
    $env:P1World__StartingMaxHp = '2000'
    $env:P1World__StartingMp = '500'
    $env:P1World__StartingMaxMp = '500'
}
foreach ($name in $Gates.Keys) { Set-Item -Path "Env:$name" -Value $Gates[$name] }

Write-Host "==> Starting server (gateSet=$GateSet, port=$Port)"
# No -NoNewWindow: sharing the launcher's console would keep this script attached to a
# server that is meant to outlive it, and a launcher that never returns cannot tell the
# operator the port is live. The child gets its own window and its own log files.
$Server = Start-Process -FilePath 'dotnet' `
    -ArgumentList @($Binary, '--urls', $BaseUrl) `
    -RedirectStandardOutput $LogPath -RedirectStandardError $ErrPath `
    -PassThru

$healthy = $false
for ($attempt = 1; $attempt -le 60; $attempt++) {
    $health = Get-Health
    if ($health) {
        $healthy = $true
        Write-Host "==> healthy after ${attempt}s: status=$($health.status) service=$($health.service)"
        break
    }
    if ($Server.HasExited) {
        throw "server exited during startup (exit code $($Server.ExitCode)); see $ErrPath"
    }
    Start-Sleep -Seconds 1
}
if (-not $healthy) {
    Stop-Process -Id $Server.Id -Force
    throw "server did not become healthy within 60s; see $ErrPath"
}

[PSCustomObject]@{
    Id = $Server.Id
    StartTime = $Server.StartTime.ToString('o')
    Binary = (Get-Item $Binary).FullName
    BinaryWritten = (Get-Item $Binary).LastWriteTimeUtc.ToString('o')
    Port = $Port
    GateSet = $GateSet
    Gates = ($Gates.GetEnumerator() | Where-Object Value -eq 'true' | ForEach-Object Key)
} | ConvertTo-Json | Set-Content -Path $PidFile -Encoding ascii

Write-Host "==> owned PID $($Server.Id) (recorded in $PidFile)"
Write-Host "==> log $LogPath"
Write-Host "==> stop with: powershell -NoProfile -ExecutionPolicy Bypass -File Server\Health\Smoke\launch_alpha.ps1 -Stop -Port $Port"
