param([switch]$SkipMovies,[switch]$Resume,[string[]]$Only)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261113e'
$cache='D:/Project/NGUMACHHUYENAN-tools/review-media'
$godot='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$env:DOTNET_ROOT='D:/Project/NGUMACHHUYENAN-tools/dotnet8'
$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
New-Item -ItemType Directory -Force $ev | Out-Null
$jobs=@(
 @{Name='minh_kiem_hurt_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','hurt');Duration=0.3},
 @{Name='minh_kiem_death_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','death');Duration=1.2},
 @{Name='minh_kiem_dodge_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','dodge');Duration=0.48},
 @{Name='minh_kiem_reaction_chain';Scene='ActorReactionReview.tscn';Args=@();Duration=3.18;MovieFrames=240},
 @{Name='death_raw_e';Scene='ArtStudio.tscn';Args=@('--studio-entry','class_minh_kiem_death_e','--studio-play');Duration=1.2},
 @{Name='boatkeeper_walk_e';Scene='ArtStudio.tscn';Args=@('--studio-entry','npc_boat_keeper_walk_e','--studio-play','--studio-loop');Duration=0.8},
 @{Name='boatkeeper_walk_ne';Scene='ArtStudio.tscn';Args=@('--studio-entry','npc_boat_keeper_walk_ne','--studio-play','--studio-loop');Duration=0.8}
)
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown review job'}
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ('actor_20261113e_'+$job.Name+'.avi')
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
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike 'actor_20261113e_*'){throw 'Unsafe cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
