param([switch]$SkipMovies,[switch]$Resume,[string[]]$Only)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261113i'
$cache='D:/Project/NGUMACHHUYENAN-tools/review-media'
$godot='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$env:DOTNET_ROOT='D:/Project/NGUMACHHUYENAN-tools/dotnet8'
$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
New-Item -ItemType Directory -Force $ev | Out-Null
$jobs=@(
 @{Name='idle_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_ANH_DAO','--clip','idle');Duration=1},
 @{Name='walk_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_ANH_DAO','--clip','walk');Duration=0.8},
 @{Name='basic_attack_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_ANH_DAO','--clip','basic_attack');Duration=0.6},
 @{Name='locomotion_chain';Scene='ActorLocomotionReview.tscn';Args=@();Duration=4.4;MovieFrames=300}
)
foreach($action in @(@{Clip='idle';Duration=1},@{Clip='walk';Duration=0.8},@{Clip='basic_attack';Duration=0.6})){
 foreach($direction in @('n','ne','e','se','s')){
  $args=@('--studio-entry',('class_anh_dao_'+$action.Clip+'_'+$direction),'--studio-play')
  if($action.Clip -ne 'basic_attack'){$args+='--studio-loop'}
  $jobs+=@{Name=($action.Clip+'_raw_'+$direction);Scene='ArtStudio.tscn';Args=$args;Duration=$action.Duration}
 }
}
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown review job'}
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ('actor_20261113i_'+$job.Name+'.avi')
 $mp4=Join-Path $ev ($job.Name+'.mp4')
 if(-not $SkipMovies -and (-not $Resume -or -not (Test-Path -LiteralPath $mp4))){
  $movieFrames=if($job.ContainsKey('MovieFrames')){$job.MovieFrames}else{180}
  & $godot --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after $movieFrames $job.Scene -- @($job.Args) *> (Join-Path $ev ($job.Name+'.godot.log'))
  if($LASTEXITCODE){throw ('Godot movie failed: '+$job.Name)}
  & $ffmpeg -y -v error -i $avi -an -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $mp4 2> (Join-Path $ev ($job.Name+'.encode.log'))
  if($LASTEXITCODE){throw ('Encode failed: '+$job.Name)}
 }
 & $ffmpeg -v error -i $mp4 -map 0:v:0 -f null - 2> (Join-Path $ev ($job.Name+'.decode.log'))
 if($LASTEXITCODE){throw ('Decode failed: '+$job.Name)}
 # Studio waits two layout ticks before starting. Samples begin after fitting;
 # these are native temporal samples, not sprite-source cells.
 $warmup=if($job.Scene -eq 'ArtStudio.tscn'){3}else{0}
 $samples=0..15 | ForEach-Object { $warmup+[int][Math]::Floor($_*$job.Duration*60/16) }
 $selection=($samples | ForEach-Object { 'eq(n,'+$_+')' }) -join '+'
 & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$selection+"',scale=480:270:flags=neighbor,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_samples.png'))
 if($LASTEXITCODE){throw ('Sample capture failed: '+$job.Name)}
 $stillFrame=$warmup+[int][Math]::Floor($job.Duration*60*.5)
 & $ffmpeg -y -v error -i $mp4 -vf ("select='eq(n,"+$stillFrame+")'") -frames:v 1 (Join-Path $ev ($job.Name+'.png'))
 if($LASTEXITCODE){throw ('Still capture failed: '+$job.Name)}
 # Remove only this script's two exact cache files, after successful decode.
 foreach($suffix in @('.avi','.wav')){
  $target=[System.IO.Path]::GetFullPath([System.IO.Path]::ChangeExtension($avi,$suffix))
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike 'actor_20261113i_*'){throw 'Unsafe cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
