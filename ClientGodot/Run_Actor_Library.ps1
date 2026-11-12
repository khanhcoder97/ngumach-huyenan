param(
    [switch]$Test,[string]$GodotPath,[string]$DotnetPath,[switch]$SkipBuild,
    [switch]$CombatReview,[string]$Actor,[string]$Clip,
    [ValidateRange(1,2)][int]$CombatVariant=1,
    [ValidateSet('N','NE','E','SE','S','SW','W','NW')][string]$Direction,
    [ValidateRange(0,15)][int]$Frame=7,[string]$Capture
)
$ErrorActionPreference='Stop'
$toolRoot=Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'NGUMACHHUYENAN-tools'
if(-not $GodotPath){$GodotPath=Join-Path $toolRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'}
if(-not $DotnetPath){$DotnetPath=Join-Path $toolRoot 'dotnet8/dotnet.exe'}
$priorPath=$env:PATH;$priorRoot=$env:DOTNET_ROOT
try {
    $env:DOTNET_ROOT=Split-Path $DotnetPath -Parent;$env:PATH=$env:DOTNET_ROOT+';'+$priorPath
    if(-not $SkipBuild){
        & $DotnetPath build (Join-Path $PSScriptRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
        if($LASTEXITCODE){throw 'Actor library build failed.'}
        & $GodotPath --headless --editor --path $PSScriptRoot --import --quit
        if($LASTEXITCODE){throw 'Actor library import failed.'}
    }
    if($CombatReview -and -not $Actor){$Actor='MOB_WATERROOT'}
    if($CombatReview -and $Actor -notin @('MOB_WATERROOT','MOB_CARPLING')){throw 'Combat review supports Waterroot or Carpling.'}
    if($CombatReview -and $Test -and $Actor -ne 'MOB_WATERROOT'){throw 'The cue self-test requires MOB_WATERROOT.'}
    if($CombatVariant -eq 2 -and (-not $CombatReview -or $Actor -ne 'MOB_WATERROOT')){throw 'Variant 2 requires Waterroot combat review.'}
    $scene=if($CombatReview){'CarplingCombatReview.tscn'}else{'ActorLibrary.tscn'}
    $launchArgs=@('--path',$PSScriptRoot,$scene,'--')
    if($Test){$launchArgs=@('--headless')+$launchArgs;$launchArgs+=@($(if($CombatReview){'--combat-self-test'}else{'--library-self-test'}))}
    if($Actor){$launchArgs+=@($(if($CombatReview){'--combat-actor'}else{'--actor'}),$Actor)}
    if($Clip -and -not $CombatReview){$launchArgs+=@('--clip',$Clip)}
    if($Direction -and $CombatReview){$launchArgs+=@('--combat-direction',$Direction)}
    if($CombatReview){$launchArgs+=@('--combat-variant',[string]$CombatVariant)}
    if($Capture){
        $launchArgs+=@($(if($CombatReview){'--combat-capture'}else{'--library-capture'}),$Capture)
        if(-not $CombatReview){$launchArgs+=@('--library-frame',[string]$Frame)}
    }
    & $GodotPath @launchArgs
    if($LASTEXITCODE){throw 'Actor library exited with an error.'}
}
finally {$env:PATH=$priorPath;$env:DOTNET_ROOT=$priorRoot}
