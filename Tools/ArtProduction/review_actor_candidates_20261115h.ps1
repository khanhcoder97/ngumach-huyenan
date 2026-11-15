param([switch]$Resume,[string[]]$Only)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo 'Implementation/Reports/Evidence/Actor_Batch_20261115h'
$cache='D:/Project/NGUMACHHUYENAN-tools/review-media'
$godot='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe'
$ffmpeg='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$env:APPDATA=Join-Path $cache 'godot-userdata-h';$env:LOCALAPPDATA=Join-Path $cache 'godot-local-h';$env:TEMP=Join-Path $cache 'native-temp-h';$env:TMP=$env:TEMP
foreach($directory in @($env:APPDATA,$env:LOCALAPPDATA,$env:TEMP)){New-Item -ItemType Directory -Path $directory -Force | Out-Null}
$env:DOTNET_ROOT='D:/Project/NGUMACHHUYENAN-tools/dotnet8';$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
$candidatePlan=Get-Content -LiteralPath (Join-Path $ev 'candidate_review_plan.json') -Raw | ConvertFrom-Json
if($candidatePlan.selected -ne 3 -or -not $candidatePlan.catalogueUnchanged){throw 'Need three isolated candidate projects'}
$jobs=@()
foreach($entry in $candidatePlan.entries){
 $launchArgs=@('--studio-project',(Join-Path $repo $entry.project),'--studio-play','--studio-trace-source')
 if($entry.loop){$launchArgs+='--studio-loop'}
 $jobs+=@{Name=('raw_'+$entry.id);Scene='ArtStudio.tscn';Args=$launchArgs;Timing=@($entry.timing);Raw=$true}
}
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown H capture job'}
$plan=@()
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ('actor_20261115h_'+$job.Name+'.avi');$mp4=Join-Path $ev ($job.Name+'.mp4')
 if(-not $Resume -or -not (Test-Path -LiteralPath $mp4)){
  & $godot --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after 180 $job.Scene -- @($job.Args) *> (Join-Path $ev ($job.Name+'.godot.log'))
  if($LASTEXITCODE){throw ('H native movie failed: '+$job.Name)}
  if(Select-String -LiteralPath (Join-Path $ev ($job.Name+'.godot.log')) -Pattern '^ERROR:' -Quiet){throw ('Godot logged a render/resource error: '+$job.Name)}
  & $ffmpeg -y -v error -i $avi -an -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $mp4 2> (Join-Path $ev ($job.Name+'.encode.log'))
  if($LASTEXITCODE){throw ('H encode failed: '+$job.Name)}
 }
 & $ffmpeg -v error -i $mp4 -map 0:v:0 -f null - 2> (Join-Path $ev ($job.Name+'.decode.log'))
 if($LASTEXITCODE){throw ('H decode failed: '+$job.Name)}
 $elapsed=0.0;$samples=@()
 if($job.Raw){
  $trace=Get-Content -LiteralPath (Join-Path $ev ($job.Name+'.godot.log')) -Raw
  $ticks=@([regex]::Matches($trace,'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)') | ForEach-Object {@{Native=[int]$_.Groups[1].Value;Source=[int]$_.Groups[2].Value}})
  $starts=@();foreach($sourceIndex in 0..15){$found=@($ticks | Where-Object {$_.Source -eq $sourceIndex});if(-not $found.Count){throw ('Missing rendered source pose '+$sourceIndex+' in '+$job.Name)};$starts+=$found[0].Native}
  foreach($sourceIndex in 0..15){$start=$starts[$sourceIndex];$last=if($sourceIndex -lt 15){$starts[$sourceIndex+1]-1}else{$start+1};if($last -lt $start){throw 'Non-monotonic rendered source trace'};$samples+=[Math]::Max(1,$start+[int][Math]::Floor(($last-$start)/2))}
  $elapsed=($job.Timing | Measure-Object -Sum).Sum
 }else{
  foreach($ms in $job.Timing){$mid=($elapsed+[double]$ms*.5)/1000;$samples+=[Math]::Max(1,[int][Math]::Ceiling($mid*60)-1);$elapsed+=[double]$ms}
 }
 if(@($samples | Select-Object -Unique).Count -ne 16){throw 'Native phase selection lost a source pose'}
 $select=($samples | ForEach-Object {'eq(n,'+$_+')'}) -join '+'
 & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',scale=480:270:flags=neighbor,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_samples.png'))
 if($LASTEXITCODE){throw 'H temporal samples failed'}
 if($job.Raw){
  & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',crop=640:480:400:100,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_source_samples.png'))
  if($LASTEXITCODE){throw 'H native source crop failed'}
  # Native-size stage-only evidence; removes editor chrome, never edits assets.
  & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',crop=256:256:550:120,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_poses.png'))
  if($LASTEXITCODE){throw 'H native pose evidence failed'}
 }
 $still=$samples[8]
 & $ffmpeg -y -v error -i $mp4 -vf ("select='eq(n,"+$still+")'") -frames:v 1 (Join-Path $ev ($job.Name+'.png'))
 if($LASTEXITCODE){throw 'H still capture failed'}
 $plan+=@{Name=$job.Name;SourceDurationMs=$elapsed;NativeSampleIndices=$samples;RenderedSourceFramesVerified=$(if($job.Raw){16}else{0});Scope='SOURCE_REVIEW_NOT_GAMEPLAY_FPS'}
 foreach($suffix in @('.avi','.wav')){
  $target=[System.IO.Path]::GetFullPath([System.IO.Path]::ChangeExtension($avi,$suffix))
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike 'actor_20261115h_*'){throw 'Unsafe F cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
$plan | ConvertTo-Json -Depth 6 -AsArray | Set-Content -LiteralPath (Join-Path $ev $(if($Only){'capture_sample_plan.partial.json'}else{'capture_sample_plan.json'})) -Encoding utf8
