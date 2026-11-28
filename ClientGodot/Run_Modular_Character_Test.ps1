param([string]$GodotPath,[string]$DotnetPath)
$ErrorActionPreference='Stop'
$toolRoot=Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'NGUMACHHUYENAN-tools'
if(-not $GodotPath){$GodotPath=Join-Path $toolRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'}
if(-not $DotnetPath){$DotnetPath=Join-Path $toolRoot 'dotnet8/dotnet.exe'}
$previousPath=$env:PATH;$previousDotnet=$env:DOTNET_ROOT
try {
    $env:DOTNET_ROOT=Split-Path $DotnetPath -Parent;$env:PATH=$env:DOTNET_ROOT+';'+$previousPath
    & $DotnetPath build (Join-Path $PSScriptRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
    if($LASTEXITCODE){throw 'Modular character build failed.'}
    & $GodotPath --headless --path $PSScriptRoot 'ModularCharacterTest.tscn'
    if($LASTEXITCODE){throw 'Modular character contract tests failed.'}
}
finally {$env:PATH=$previousPath;$env:DOTNET_ROOT=$previousDotnet}
