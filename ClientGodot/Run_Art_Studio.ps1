param(
    [switch]$SkipBuild,
    [switch]$SelfTest,
    [string]$Project,
    [string]$Capture,
    [string]$GodotPath,
    [string]$DotnetPath
)
$ErrorActionPreference='Stop'
$options=@{SkipBuild=$SkipBuild;StudioSelfTest=$SelfTest}
if($Project){$options.StudioProject=$Project}
if($Capture){$options.Capture=$Capture}
if($GodotPath){$options.GodotPath=$GodotPath}
if($DotnetPath){$options.DotnetPath=$DotnetPath}
& (Join-Path $PSScriptRoot 'Run_PaperDoll_Lab.ps1') @options
