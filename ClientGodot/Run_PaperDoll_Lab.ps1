param(
    [string]$GodotPath,
    [string]$DotnetPath,
    [switch]$SkipBuild,
    [switch]$SelfTest,
    [switch]$Female,
    [switch]$Indigo,
    [string]$Capture,
    [string]$Benchmark
)
$ErrorActionPreference='Stop'
$toolRoot=Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'NGUMACHHUYENAN-tools'
if(-not $GodotPath){$GodotPath=Join-Path $toolRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'}
if(-not $DotnetPath){$DotnetPath=Join-Path $toolRoot 'dotnet8/dotnet.exe'}
if(-not (Test-Path -LiteralPath $GodotPath -PathType Leaf)){throw "Missing Godot .NET: $GodotPath"}
if(-not (Test-Path -LiteralPath $DotnetPath -PathType Leaf)){throw "Missing .NET 8: $DotnetPath"}
$previousPath=$env:PATH
$previousDotnet=$env:DOTNET_ROOT
try {
    # A portable, space-free root also avoids Godot misreading the global SDK path.
    $env:DOTNET_ROOT=Split-Path $DotnetPath -Parent
    $env:PATH=$env:DOTNET_ROOT+';'+$previousPath
    if(-not $SkipBuild){
        & $DotnetPath build (Join-Path $PSScriptRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
        if($LASTEXITCODE){throw 'Paper-doll lab build failed.'}
        & $GodotPath --headless --editor --path $PSScriptRoot --import --quit
        if($LASTEXITCODE){throw 'Paper-doll lab import failed.'}
    }
    $launchArgs=@('--path',$PSScriptRoot,'PaperDollLab.tscn')
    if($SelfTest){$launchArgs=@('--headless')+$launchArgs}
    $launchArgs+='--'
    if($SelfTest){$launchArgs+='--paperdoll-self-test'}
    if($Female){$launchArgs+='--paperdoll-female'}
    if($Indigo){$launchArgs+='--paperdoll-indigo'}
    if($Capture){$launchArgs+=@('--paperdoll-capture',$Capture)}
    if($Benchmark){$launchArgs+=@('--paperdoll-benchmark',$Benchmark)}
    & $GodotPath @launchArgs
    if($LASTEXITCODE){throw 'Paper-doll lab failed.'}
}
finally {
    $env:PATH=$previousPath
    $env:DOTNET_ROOT=$previousDotnet
}
