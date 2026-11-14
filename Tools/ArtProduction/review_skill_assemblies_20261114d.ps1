param([switch]$Resume,[string[]]$Only)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261114d'
$cache='D:/Project/NGUMACHHUYENAN-tools/review-media'
$godot='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$env:DOTNET_ROOT='D:/Project/NGUMACHHUYENAN-tools/dotnet8';$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
$jobs=@()
$records=Get-Content -LiteralPath (Join-Path $repo 'Art_Source/Actor_Library_20261107/generation_records.json') -Raw | ConvertFrom-Json
foreach($r in @($records | Where-Object {$_.batch -eq '20261114d'})){
 $args=@('--studio-entry',$r.id,'--studio-play');if($r.previewLoop){$args+='--studio-loop'}
 $jobs+=@{Name=('raw_'+$r.id);Scene='ArtStudio.tscn';Args=$args;Duration=[double]$r.previewDurationSeconds;MovieFrames=180;Raw=$true;Tracks=@()}
}
$data=Get-Content -LiteralPath (Join-Path $repo 'ClientGodot/assets/actor_library_v1/skill_assemblies.json') -Raw | ConvertFrom-Json
foreach($p in $data.Profiles){foreach($v in $p.Variants){
 $jobs+=@{Name=('assembly_'+$p.Id.ToLowerInvariant()+'_'+$v.Id);Scene='SkillAssemblyReview.tscn';Args=@('--assembly-profile',$p.Id,'--assembly-variant',$v.Id);Duration=[double]$v.Duration;MovieFrames=600;Raw=$false;Tracks=@($v.Tracks)}
}}
foreach($id in @('SK_MK_03','SK_AD_06')){
 $p=$data.Profiles | Where-Object {$_.Id -eq $id};$v=$p.Variants[0]
 $jobs+=@{Name=('assembly_'+$id.ToLowerInvariant()+'_'+$v.Id+'_lowfx');Scene='SkillAssemblyReview.tscn';Args=@('--assembly-profile',$p.Id,'--assembly-variant',$v.Id,'--assembly-low-fx');Duration=[double]$v.Duration;MovieFrames=600;Raw=$false;Tracks=@($v.Tracks)}
}
if($jobs.Count -ne 27){throw 'Expected5raw+20scenario+2LowFX captures'}
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown review job'}
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ('actor_20261114d_'+$job.Name+'.avi');$mp4=Join-Path $ev ($job.Name+'.mp4')
 if(-not $Resume -or -not (Test-Path -LiteralPath $mp4)){
  & $godot --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after $job.MovieFrames $job.Scene -- @($job.Args) *> (Join-Path $ev ($job.Name+'.godot.log'))
  if($LASTEXITCODE){throw ('Godot movie failed: '+$job.Name)}
  & $ffmpeg -y -v error -i $avi -an -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $mp4 2> (Join-Path $ev ($job.Name+'.encode.log'))
  if($LASTEXITCODE){throw ('Encode failed: '+$job.Name)}
 }
 & $ffmpeg -v error -i $mp4 -map 0:v:0 -f null - 2> (Join-Path $ev ($job.Name+'.decode.log'))
 if($LASTEXITCODE){throw ('Decode failed: '+$job.Name)}
 $samples=0..15 | ForEach-Object {3+[int][Math]::Floor($_*$job.Duration*60/16)}
 $select=($samples | ForEach-Object {'eq(n,'+$_+')'}) -join '+'
 & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',scale=480:270:flags=neighbor,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_samples.png'))
 if($LASTEXITCODE){throw 'Temporal samples failed'}
 if($job.Raw){
  & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',crop=640:480:400:100,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_source_samples.png'))
  if($LASTEXITCODE){throw 'Native source crop failed'}
 }
 $still=3+[int][Math]::Floor($job.Duration*60*.5)
 & $ffmpeg -y -v error -i $mp4 -vf ("select='eq(n,"+$still+")'") -frames:v 1 (Join-Path $ev ($job.Name+'.png'))
 if($LASTEXITCODE){throw 'Still failed'}
 foreach($track in $job.Tracks){
  $phase=3+[int][Math]::Floor(([double]$track.Start+[Math]::Min([double]$track.Duration,[double]$track.SourceSeconds)*.5)*60)
  & $ffmpeg -y -v error -i $mp4 -vf ("select='eq(n,"+$phase+")'") -frames:v 1 (Join-Path $ev ($job.Name+'_phase_'+$track.Id+'.png'))
  if($LASTEXITCODE){throw 'Phase capture failed'}
 }
 foreach($suffix in @('.avi','.wav')){
  $target=[System.IO.Path]::GetFullPath([System.IO.Path]::ChangeExtension($avi,$suffix))
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike 'actor_20261114d_*'){throw 'Unsafe cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
