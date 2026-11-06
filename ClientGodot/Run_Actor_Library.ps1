param([switch]$Test,[string]$GodotPath,[string]$DotnetPath)
$ErrorActionPreference='Stop'
$toolRoot=Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'NGUMACHHUYENAN-tools'
if(-not $GodotPath){$GodotPath=Join-Path $toolRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'}
if(-not $DotnetPath){$DotnetPath=Join-Path $toolRoot 'dotnet8/dotnet.exe'}
$priorPath=$env:PATH;$priorRoot=$env:DOTNET_ROOT
try {
    $env:DOTNET_ROOT=Split-Path $DotnetPath -Parent;$env:PATH=$env:DOTNET_ROOT+';'+$priorPath
    & $DotnetPath build (Join-Path $PSScriptRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
    if($LASTEXITCODE){throw 'Actor library build failed.'}
    & $GodotPath --headless --editor --path $PSScriptRoot --quit
    if($LASTEXITCODE){throw 'Actor library import failed.'}
    if($Test){& $GodotPath --headless --path $PSScriptRoot 'ActorLibrary.tscn' -- --library-self-test}
    else {& $GodotPath --path $PSScriptRoot 'ActorLibrary.tscn'}
    if($LASTEXITCODE){throw 'Actor library exited with an error.'}
}
finally {$env:PATH=$priorPath;$env:DOTNET_ROOT=$priorRoot}
