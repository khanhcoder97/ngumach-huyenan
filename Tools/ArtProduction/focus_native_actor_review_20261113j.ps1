param([string[]]$Only,[switch]$SkipMissing)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261113j'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$count=0
foreach($action in @(@{Name='run';Duration=.64},@{Name='walk';Duration=.8},@{Name='basic_attack_02';Duration=.6},@{Name='basic_attack_03';Duration=.6},@{Name='interact';Duration=1.6})){
 foreach($direction in @('n','ne','e','se','s')){
  if($action.Name -eq 'walk' -and $direction -ne 'e'){continue}
  $name=$action.Name+'_raw_'+$direction
  if($Only -and $name -notin $Only){continue}
  if($SkipMissing -and -not (Test-Path -LiteralPath (Join-Path $ev ($name+'.mp4')))){continue}
  $samples=0..15 | ForEach-Object {3+[int][Math]::Floor($_*$action.Duration*60/16)}
  $selection=($samples | ForEach-Object {'eq(n,'+$_+')'}) -join '+'
  # Native viewport inspection only. Preserve pixel scale; never export this
  # crop as a sprite asset or modify any source PNG.
  & $ffmpeg -y -v error -i (Join-Path $ev ($name+'.mp4')) -vf ("select='"+$selection+"',crop=256:256:558:120,tile=4x4") -frames:v 1 (Join-Path $ev ($name+'_actor_samples.png'))
  if($LASTEXITCODE){throw ('Focus capture failed: '+$name)}
  $count++
 }
}
Write-Output ('NATIVE_ACTOR_FOCUS_COMPLETE '+$count)
