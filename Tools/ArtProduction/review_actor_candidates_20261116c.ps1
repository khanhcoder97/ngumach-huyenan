param(
 [switch]$Resume,[string[]]$Only,
 [ValidatePattern('^[0-9]{8}[a-z]$')][string]$Batch = '20261116c',
 [string]$GodotPath='D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe',
 [string]$FfmpegPath='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe',
 [string]$CacheRoot='D:/Project/NGUMACHHUYENAN-tools/review-media',
 [string]$DotNetRoot='D:/Project/NGUMACHHUYENAN-tools/dotnet8'
)
$ErrorActionPreference='Stop'
$repo=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$ev=Join-Path $repo ('Implementation/Reports/Evidence/Actor_Batch_'+$Batch)
$capturePrefix='actor_'+$Batch+'_'
$cache=[IO.Path]::GetFullPath($CacheRoot)
$godot=$GodotPath
$ffmpeg=$FfmpegPath
function Get-ReviewProjectSha([string]$Path){
 $projectText=[IO.File]::ReadAllText($Path).Replace("`r`n","`n")
 $hasher=[Security.Cryptography.SHA256]::Create()
 try{return [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($projectText))).Replace('-','').ToLowerInvariant()}finally{$hasher.Dispose()}
}
$env:APPDATA=Join-Path $cache 'godot-userdata-c';$env:LOCALAPPDATA=Join-Path $cache 'godot-local-c';$env:TEMP=Join-Path $cache 'native-temp-c';$env:TMP=$env:TEMP
foreach($directory in @($env:APPDATA,$env:LOCALAPPDATA,$env:TEMP)){New-Item -ItemType Directory -Path $directory -Force | Out-Null}
$env:DOTNET_ROOT=$DotNetRoot;$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
$candidatePlan=Get-Content -LiteralPath (Join-Path $ev 'candidate_review_plan.json') -Raw | ConvertFrom-Json
if($candidatePlan.selected -lt 1 -or $candidatePlan.selected -gt 50 -or -not $candidatePlan.catalogueUnchanged){throw 'Need1to50isolated candidate projects'}
$jobs=@()
foreach($entry in $candidatePlan.entries){
 $launchArgs=@('--studio-project',(Join-Path $repo $entry.project),'--studio-play','--studio-trace-source')
 if($entry.loop){$launchArgs+='--studio-loop'}
 $jobs+=@{Name=('raw_'+$entry.id);Scene='ArtStudio.tscn';Args=$launchArgs;Timing=@($entry.timing);Raw=$true;SourceSha256=$entry.sourceSha256;ProjectSha256=(Get-ReviewProjectSha (Join-Path $repo $entry.project));OriginalProjectSha256=(Get-FileHash -LiteralPath (Join-Path $repo $entry.project) -Algorithm SHA256).Hash.ToLowerInvariant()}
}
if($Only -and @($Only | Where-Object {$_ -notin $jobs.Name}).Count){throw 'Unknown C capture job'}
$plan=@()
foreach($job in @($jobs | Where-Object {-not $Only -or $_.Name -in $Only})){
 $avi=Join-Path $cache ($capturePrefix+$job.Name+'.avi');$mp4=Join-Path $ev ($job.Name+'.mp4')
 $receiptPath=Join-Path $ev ($job.Name+'.capture_receipt.json')
 if($Resume -and (Test-Path -LiteralPath $mp4)){
  if(-not (Test-Path -LiteralPath $receiptPath)){throw ('No capture receipt for resume: '+$job.Name)}
  $receipt=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
  if($receipt.sourceSha256 -ne $job.SourceSha256 -or $receipt.projectSha256 -ne $job.ProjectSha256 -or $receipt.movieSha256 -ne (Get-FileHash -LiteralPath $mp4 -Algorithm SHA256).Hash.ToLowerInvariant()){throw ('Changed source/project/movie; archive and recapture: '+$job.Name)}
 }
 if(-not $Resume -or -not (Test-Path -LiteralPath $mp4)){
  & $godot --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after 180 $job.Scene -- @($job.Args) *> (Join-Path $ev ($job.Name+'.godot.log'))
  if($LASTEXITCODE){throw ('C native movie failed: '+$job.Name)}
  if(Select-String -LiteralPath (Join-Path $ev ($job.Name+'.godot.log')) -Pattern '^ERROR:' -Quiet){throw ('Godot logged a render/resource error: '+$job.Name)}
  & $ffmpeg -y -v error -i $avi -an -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $mp4 2> (Join-Path $ev ($job.Name+'.encode.log'))
  if($LASTEXITCODE){throw ('C encode failed: '+$job.Name)}
 }
 if(Select-String -LiteralPath (Join-Path $ev ($job.Name+'.godot.log')) -Pattern '^ERROR:' -Quiet){throw ('Reject recorded Godot error: '+$job.Name)}
 & $ffmpeg -v error -i $mp4 -map 0:v:0 -f null - 2> (Join-Path $ev ($job.Name+'.decode.log'))
 if($LASTEXITCODE){throw ('C decode failed: '+$job.Name)}
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
 if($LASTEXITCODE){throw 'C temporal samples failed'}
 if($job.Raw){
  & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',crop=640:480:400:100,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_source_samples.png'))
  if($LASTEXITCODE){throw 'C native source crop failed'}
  # Native-size stage-only evidence; removes editor chrome, never edits assets.
  & $ffmpeg -y -v error -i $mp4 -vf ("select='"+$select+"',crop=256:256:550:120,tile=4x4") -frames:v 1 (Join-Path $ev ($job.Name+'_poses.png'))
  if($LASTEXITCODE){throw 'C native pose evidence failed'}
 }
 $still=$samples[8]
 & $ffmpeg -y -v error -i $mp4 -vf ("select='eq(n,"+$still+")'") -frames:v 1 (Join-Path $ev ($job.Name+'.png'))
 if($LASTEXITCODE){throw 'C still capture failed'}
 $plan+=@{Name=$job.Name;SourceDurationMs=$elapsed;NativeSampleIndices=$samples;RenderedSourceFramesVerified=$(if($job.Raw){16}else{0});Scope='SOURCE_REVIEW_NOT_GAMEPLAY_FPS'}
 foreach($suffix in @('.avi','.wav')){
  $target=[System.IO.Path]::GetFullPath([System.IO.Path]::ChangeExtension($avi,$suffix))
  if((Split-Path $target -Parent) -ne [System.IO.Path]::GetFullPath($cache) -or (Split-Path $target -Leaf) -notlike ($capturePrefix+'*')){throw 'Unsafe candidate cache path'}
  if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target -Force}
 }
 @{sourceSha256=$job.SourceSha256;projectSha256=$job.ProjectSha256;projectHashEncoding='UTF8_LF';capturedOriginalProjectSha256=$job.OriginalProjectSha256;movieSha256=(Get-FileHash -LiteralPath $mp4 -Algorithm SHA256).Hash.ToLowerInvariant();scope='NATIVE_SOURCE_CAPTURE_NOT_APPROVAL'} | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding utf8
 $plan | ConvertTo-Json -Depth 6 -AsArray | Set-Content -LiteralPath (Join-Path $ev $(if($Only){'capture_sample_plan.partial.json'}else{'capture_sample_plan.json'})) -Encoding utf8
 Write-Output ('REVIEW_MEDIA_COMPLETE '+$job.Name)
}
$plan | ConvertTo-Json -Depth 6 -AsArray | Set-Content -LiteralPath (Join-Path $ev $(if($Only){'capture_sample_plan.partial.json'}else{'capture_sample_plan.json'})) -Encoding utf8
