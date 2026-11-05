param(
    [switch]$Test,
    [switch]$UiTest,
    [switch]$UiGallery,
    [switch]$MotionTest,
    [switch]$CombatTest,
    [int]$Port = 0,
    [string]$GodotPath,
    [string]$Dotnet8Path,
    [string]$Dotnet10Path,
    [string]$EvidenceDirectory
)
$ErrorActionPreference = 'Stop'
if($CombatTest -and ($UiTest -or $UiGallery -or $MotionTest)){throw 'CombatTest uses its own acceptance session; run separately from quest UI tests.'}
if($CombatTest){$Test=$true}
if ($UiGallery -or $MotionTest) { $UiTest = $true }
if ($UiTest) { $Test = $true }
$clientRoot = $PSScriptRoot
$repoRoot = Split-Path $clientRoot -Parent
$projectParent = Split-Path $repoRoot -Parent
$toolsRoot = Join-Path $projectParent 'NGUMACHHUYENAN-tools'
if (-not $GodotPath) { $GodotPath = Join-Path $toolsRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe' }
if (-not $Dotnet8Path) { $Dotnet8Path = Join-Path $toolsRoot 'dotnet8/dotnet.exe' }
if (-not $Dotnet10Path) { $Dotnet10Path = Join-Path $toolsRoot 'dotnet10/dotnet.exe' }
foreach ($requiredTool in @($GodotPath,$Dotnet8Path,$Dotnet10Path)) {
    if (-not (Test-Path -LiteralPath $requiredTool -PathType Leaf)) { throw "Missing tool: $requiredTool. Supply its path as a script parameter." }
}
if (-not $EvidenceDirectory) {
    if ($Test) { $EvidenceDirectory = Join-Path $repoRoot 'Implementation/Reports/Evidence/Playable_Alpha_20261105' }
    else {
        $playSession = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')+'-'+[Guid]::NewGuid().ToString('N').Substring(0,8)
        $EvidenceDirectory = Join-Path $toolsRoot ('play-sessions/'+$playSession)
    }
}
$EvidenceDirectory = [IO.Path]::GetFullPath($EvidenceDirectory)
New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
$prefix = if ($CombatTest) { 'combat.' } elseif ($UiTest) { 'ui.' } else { '' }
$serverOut = Join-Path $EvidenceDirectory ($prefix+'server.stdout.log')
$serverErr = Join-Path $EvidenceDirectory ($prefix+'server.stderr.log')
$gameLog = Join-Path $EvidenceDirectory ($prefix+'godot.stdout.log')
$captureName = if ($CombatTest) { 'native_combat_target.png' } elseif ($UiTest) { 'native_ui_p00_01_inventory.png' } else { 'native_p00_01_inventory.png' }
$capturePath = Join-Path $EvidenceDirectory $captureName
$priorPath = $env:PATH
$priorDotnet = $env:DOTNET_ROOT
$priorBaseUrl = $env:P1_BASE_URL
$serverProcess = $null
$gameExit = 1
try {
    $env:DOTNET_ROOT = Split-Path $Dotnet10Path -Parent
    $env:PATH = $env:DOTNET_ROOT + ';' + $priorPath
    & $Dotnet10Path build (Join-Path $repoRoot 'Server/Health/Health.csproj') -c Release --nologo -m:1
    if ($LASTEXITCODE -ne 0) { throw 'Health build failed.' }
    $env:DOTNET_ROOT = Split-Path $Dotnet8Path -Parent
    $env:PATH = $env:DOTNET_ROOT + ';' + $priorPath
    & $Dotnet8Path build (Join-Path $clientRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
    if ($LASTEXITCODE -ne 0) { throw 'Godot client build failed.' }
    & $GodotPath --headless --editor --path $clientRoot --quit
    if ($LASTEXITCODE -ne 0) { throw 'Godot import failed.' }
    if ($Port -eq 0) {
        $portProbe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
        $portProbe.Start()
        $Port = ([Net.IPEndPoint]$portProbe.LocalEndpoint).Port
        $portProbe.Stop()
    }
    if ($Port -lt 1024 -or $Port -gt 65535) { throw 'Use a private unprivileged TCP port.' }
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { throw "Port $Port is already in use. No process was stopped." }
    $baseUrl = "http://127.0.0.1:$Port"
    $serverDll = Join-Path $repoRoot 'Server/Health/bin/Release/net10.0/Health.dll'
    $serverSettings = @{
        'DOTNET_ROOT' = (Split-Path $Dotnet10Path -Parent)
        'Content__BenMuaTerrainPath' = (Join-Path $repoRoot 'Implementation/Content/Maps/BenMua/terrain.json')
        'P1World__MoveSpeedWuPerSecond' = '3.2'
        'P1World__MaxStepSeconds' = '0.10'
        'P1__QuestAccept__Enabled' = 'true'
        'P1__Interact__Enabled' = 'true'
        'P1__QuestTurnIn__Enabled' = 'true'
        'P1__CombatV2__Enabled' = 'true'
        'P1__CombatDamage__Enabled' = 'true'
        'P1__MobBehavior__Enabled' = 'false'
        'P1__DeathReturn__Enabled' = 'false'
        'Logging__LogLevel__Microsoft.AspNetCore' = $(if ($Test) { 'Information' } else { 'Warning' })
    }
    $priorServerSettings = @{}
    try {
        foreach ($entry in $serverSettings.GetEnumerator()) {
            $priorServerSettings[$entry.Key] = [Environment]::GetEnvironmentVariable($entry.Key,'Process')
            [Environment]::SetEnvironmentVariable($entry.Key,$entry.Value,'Process')
        }
        $serverArgs = '"' + $serverDll + '" --urls ' + $baseUrl
        $serverProcess = Start-Process -FilePath $Dotnet10Path -ArgumentList $serverArgs -WorkingDirectory $repoRoot -WindowStyle Hidden -RedirectStandardOutput $serverOut -RedirectStandardError $serverErr -PassThru
    }
    finally {
        foreach ($entry in $priorServerSettings.GetEnumerator()) { [Environment]::SetEnvironmentVariable($entry.Key,$entry.Value,'Process') }
    }
    $ready = $false
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        $serverProcess.Refresh()
        if ($serverProcess.HasExited) { throw "Owned server exited. Read $serverErr and $serverOut" }
        try {
            $health = Invoke-RestMethod -Uri ($baseUrl+'/health') -TimeoutSec 2
            $ownedListener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -eq $serverProcess.Id }
            if ($health.service -eq 'ngu-mach-huyen-an-server' -and $health.status -eq 'ok' -and $ownedListener) { $ready = $true; break }
        } catch { }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'Private server did not become healthy under the owned PID.' }
    $env:DOTNET_ROOT = Split-Path $Dotnet8Path -Parent
    $env:PATH = $env:DOTNET_ROOT + ';' + $priorPath
    $env:P1_BASE_URL = $baseUrl
    if ($Test) {
        $testFlag = if ($CombatTest) { '--combat-online-test' } elseif ($UiTest) { '--online-ui-self-test' } else { '--online-self-test' }
        $gameArgs = @('--path',$clientRoot,'--',$testFlag)
        if ($UiGallery) { $gameArgs += '--ui-gallery' }
        if ($MotionTest) { $gameArgs += '--motion-online-test' }
        $gameArgs += @('--capture',$capturePath)
        & $GodotPath @gameArgs 2>&1 | Tee-Object -FilePath $gameLog
    } else {
        Write-Output 'Online local: WASD move, E talk/collect, I inventory, Space attack, 1-3 skills, Esc close.'
        Write-Output ("Session logs: "+$EvidenceDirectory)
        & $GodotPath --path $clientRoot 2>&1 | Tee-Object -FilePath $gameLog
    }
    $gameExit = $LASTEXITCODE
    if ($gameExit -ne 0) { throw "Godot exited with $gameExit; see $gameLog" }
    if ($Test) {
        $pattern = if ($CombatTest) { 'NATIVE_COMBAT_PASS assertions=(\d+)' } elseif ($UiTest) { 'NATIVE_UI_P00_01_PASS assertions=(\d+)' } else { 'NATIVE_P00_01_PASS assertions=(\d+)' }
        $marker = Select-String -LiteralPath $gameLog -Pattern $pattern | Select-Object -Last 1
        if (-not $marker -or [int]$marker.Matches[0].Groups[1].Value -le 0) { throw 'No nonzero real native quest assertion marker.' }
        if (-not (Test-Path -LiteralPath $capturePath)) { throw 'Native renderer did not create its capture.' }
        [ordered]@{
            status=$(if ($CombatTest) { 'PASS_NATIVE_COMBAT' } elseif ($UiTest) { 'PASS_NATIVE_UI_P00_01' } else { 'PASS_NATIVE_P00_01' })
            assertions=[int]$marker.Matches[0].Groups[1].Value
            serverService=$health.service
            serverPid=$serverProcess.Id
            baseUrl=$baseUrl
            capture=$captureName
            authoritativeRewards=$true
            productionEnabled=$false
            fullCampaignVerified=$false
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $EvidenceDirectory ($prefix+'run.json')) -Encoding utf8
    }
}
finally {
    if ($serverProcess) {
        $serverProcess.Refresh()
        if (-not $serverProcess.HasExited) { Stop-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue }
    }
    $env:PATH = $priorPath
    $env:DOTNET_ROOT = $priorDotnet
    $env:P1_BASE_URL = $priorBaseUrl
}
exit $gameExit
