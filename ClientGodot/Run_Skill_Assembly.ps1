param(
 [switch]$SkipBuild,[switch]$SelfTest,[string]$Profile,[string]$Variant,[switch]$LowFx,
 [ValidateRange(0,5)][int]$Resource=5,[string]$Project,[string]$GodotPath,[string]$DotnetPath
)
$ErrorActionPreference='Stop'
$toolRoot=Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'NGUMACHHUYENAN-tools'
if(-not $GodotPath){$GodotPath=Join-Path $toolRoot 'godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'}
if(-not $DotnetPath){$DotnetPath=Join-Path $toolRoot 'dotnet8/dotnet.exe'}
$priorPath=$env:PATH;$priorRoot=$env:DOTNET_ROOT
try{
 $env:DOTNET_ROOT=Split-Path $DotnetPath -Parent;$env:PATH=$env:DOTNET_ROOT+';'+$priorPath
 if(-not $SkipBuild){
  & $DotnetPath build (Join-Path $PSScriptRoot 'VisualReboot.csproj') -p:RestoreLockedMode=true --nologo -m:1
  if($LASTEXITCODE){throw 'Skill assembly build failed'}
  & $GodotPath --headless --editor --path $PSScriptRoot --import --quit
  if($LASTEXITCODE){throw 'Skill assembly import failed'}
 }
 $launch=@('--path',$PSScriptRoot,'SkillAssemblyReview.tscn','--','--assembly-resource',[string]$Resource)
 if($Profile){$launch+=@('--assembly-profile',$Profile)}
 if($Variant){$launch+=@('--assembly-variant',$Variant)}
 if($LowFx){$launch+='--assembly-low-fx'}
 if($Project){$launch+=@('--assembly-project',$Project)}
 if($SelfTest){$launch=@('--headless')+$launch;$launch+='--assembly-self-test'}
 & $GodotPath @launch
 if($LASTEXITCODE){throw 'Skill assembly review failed'}
}finally{$env:PATH=$priorPath;$env:DOTNET_ROOT=$priorRoot}
