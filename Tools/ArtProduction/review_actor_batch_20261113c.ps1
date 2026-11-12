param([switch]$SkipMovies,[switch]$Resume,[string[]]$Only)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261113c'
$cache='D:/Project/NGUMACHHUYENAN-tools/review-media'
$godot='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$env:DOTNET_ROOT='D:/Project/NGUMACHHUYENAN-tools/dotnet8'
$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
New-Item -ItemType Directory -Force $ev | Out-Null
$jobs=@(
 @{Name='minh_kiem_tam_long_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','skill_02');Duration=0.59},
 @{Name='minh_kiem_kiem_tran_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','skill_03');Duration=0.6},
 @{Name='minh_kiem_thiet_y_eight_angles';Scene='ActorLibrary.tscn';Args=@('--actor','CLASS_MINH_KIEM','--clip','skill_04');Duration=0.8},
 @{Name='tam_long_raw_n';Scene='ArtStudio.tscn';Args=@('--studio-entry','class_minh_kiem_skill_02_n','--studio-play');Duration=0.59},
 @{Name='kiem_tran_raw_n';Scene='ArtStudio.tscn';Args=@('--studio-entry','class_minh_kiem_skill_03_n','--studio-play');Duration=0.6},
 @{Name='tam_long_trail';Scene='ArtStudio.tscn';Args=@('--studio-entry','sk_mk_02_trail_component','--studio-play');Duration=0.32},
 @{Name='tam_long_stop_dust';Scene='ArtStudio.tscn';Args=@('--studio-entry','sk_mk_02_stop_dust_component','--studio-play');Duration=0.32},
 @{Name='thiet_y_gain';Scene='ArtStudio.tscn';Args=@('--studio-entry','sk_mk_04_gain_component','--studio-play');Duration=0.4},
 @{Name='thiet_y_break';Scene='ArtStudio.tscn';Args=@('--studio-entry','sk_mk_04_break_component','--studio-play');Duration=0.32},
 @{Name='thiet_y_expire';Scene='ArtStudio.tscn';Args=@('--studio-entry','sk_mk_04_expire_component','--studio-play');Duration=0.4}
)
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown review job'}
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ('actor_20261113c_'+$job.Name+'.avi')
 $mp4=Join-Path $ev ($job.Name+'.mp4')
 if(-not $SkipMovies -and (-not $Resume -or -not (Test-Path -LiteralPath $mp4))){
  & $godot --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after 180 $job.Scene -- @($job.Args) *> (Join-Path $ev ($job.Name+'.godot.log'))
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
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike 'actor_20261113c_*'){throw 'Unsafe cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
