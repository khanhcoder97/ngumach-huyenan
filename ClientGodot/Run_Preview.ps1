param(
    [string]$GodotPath,
    [string]$DotnetPath,
    [switch]$Test
)
$ErrorActionPreference = 'Stop'
$clientRoot = $PSScriptRoot
$workspaceParent = Split-Path (Split-Path $clientRoot -Parent) -Parent
if (-not $DotnetPath) {
    $localDotnet = Join-Path $workspaceParent 'NGUMACHHUYENAN-tools/dotnet8/dotnet.exe'
    if (Test-Path -LiteralPath $localDotnet) { $DotnetPath = $localDotnet }
    else { $DotnetPath = (Get-Command dotnet -ErrorAction Stop).Source }
}
if (-not $GodotPath) {
    $localGodot = Join-Path $workspaceParent 'NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
    if (Test-Path -LiteralPath $localGodot) { $GodotPath = $localGodot }
    else { $GodotPath = (Get-Command godot -ErrorAction Stop).Source }
}
$env:DOTNET_ROOT = Split-Path $DotnetPath -Parent
$env:PATH = $env:DOTNET_ROOT + ';' + $env:PATH
& $DotnetPath build (Join-Path $clientRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo
if ($LASTEXITCODE -ne 0) { throw 'Build failed; preview was not started.' }
& $GodotPath --headless --editor --path $clientRoot --quit
if ($LASTEXITCODE -ne 0) { throw 'Import failed; preview was not started.' }
if ($Test) {
    & $GodotPath --headless --path $clientRoot -- --camera-self-test
    if ($LASTEXITCODE -eq 0) { & $GodotPath --headless --path $clientRoot -- --scene-self-test }
}
else { & $GodotPath --path $clientRoot }
exit $LASTEXITCODE
