$ErrorActionPreference = 'Stop'
$reviewRoot = 'D:/Project/NGUMACHHUYENAN-review-qod-20261108'
$reviewEvidence = Join-Path $PSScriptRoot 'Evidence'
$reviewPort = 5202
if ([System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object Port -eq $reviewPort) { throw 'Review port already bound' }
foreach ($reviewFlag in @('AlphaProfile','QuestAccept','Interact','QuestTurnIn','Equipment','CombatV2','CombatDamage','MobBehavior','DeathReturn','QuestTalk','Portal')) { [Environment]::SetEnvironmentVariable("P1__${reviewFlag}__Enabled",'true','Process') }
$env:P1__AlphaLoot__GrantEnabled = 'true'
$env:P1__DeathReturn__RestoreHpFixture = '0'
$env:P1World__StartingHp = '2000'
$env:P1World__StartingMaxHp = '2000'
$env:P1World__StartingMp = '500'
$env:P1World__StartingMaxMp = '500'
$reviewProcess = Start-Process -FilePath 'D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe' -ArgumentList @("$reviewRoot/Server/Health/bin/Release/net10.0/Health.dll",'--urls',"http://127.0.0.1:$reviewPort") -WorkingDirectory $reviewRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput "$reviewEvidence/qod-alpha-server.log" -RedirectStandardError "$reviewEvidence/qod-alpha-server.err.log"
try {
    $reviewReady = $false
    for ($reviewAttempt=0; $reviewAttempt -lt 40; $reviewAttempt++) {
        if ($reviewProcess.HasExited) { throw 'Owned server exited before healthy' }
        try { $reviewHealth = Invoke-RestMethod "http://127.0.0.1:$reviewPort/health" -TimeoutSec 2; if ($reviewHealth.status -eq 'ok') { $reviewReady = $true; break } } catch { }
        Start-Sleep -Milliseconds 500
    }
    if (-not $reviewReady) { throw 'Owned server not healthy' }
    "head=6814126e2def8a1c4270a1016f0ab85404cba46e pid=$($reviewProcess.Id) port=$reviewPort"
    python "$reviewRoot/Server/Health/Smoke/e2e_p1.py" "http://127.0.0.1:$reviewPort" alpha-p00 *> "$reviewEvidence/qod-alpha-http.txt"
    $reviewExit = $LASTEXITCODE
    Get-Content "$reviewEvidence/qod-alpha-http.txt" -Tail 12
    if ($reviewExit -ne 0) { throw "Alpha E2E exited $reviewExit" }
} finally { if (-not $reviewProcess.HasExited) { Stop-Process -Id $reviewProcess.Id -Force }; 'owned_server_stopped' }
