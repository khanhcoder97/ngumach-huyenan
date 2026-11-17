param(
    [ValidateSet('S','SE','E','NE','N')][string[]]$Direction = @('S','SE','E','NE','N'),
    [string]$GodotPath = 'D:/Project/NGUMACHHUYENAN-tools/godot-4.7.2/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe',
    [string]$FfmpegPath = 'D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe',
    [string]$CacheRoot = 'D:/Project/NGUMACHHUYENAN-tools/review-media',
    [string]$DotNetRoot = 'D:/Project/NGUMACHHUYENAN-tools/dotnet8'
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$bundle = Join-Path $repo 'Implementation/Reports/Evidence/Actor_Assembly_20261117a/Sanctuary_TC06_v2'
$project = Join-Path $bundle 'project.json'
$projectSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $project).Hash.ToLowerInvariant()
$descriptor = Get-Content -Raw -LiteralPath (Join-Path $bundle 'assembly_descriptor.json') | ConvertFrom-Json
if ($descriptor.projectSha256 -ne $projectSha) { throw 'Studio project has changed since assembly registration.' }
$cache = [IO.Path]::GetFullPath($CacheRoot)
$env:APPDATA = Join-Path $cache 'godot-userdata-c'
$env:LOCALAPPDATA = Join-Path $cache 'godot-local-c'
$env:TEMP = Join-Path $cache 'native-temp-c'
$env:TMP = $env:TEMP
$env:DOTNET_ROOT = $DotNetRoot
$env:PATH = $DotNetRoot + ';' + $env:PATH
$scratch = Join-Path $cache 'sanctuary_capture'
New-Item -ItemType Directory -Path $scratch -Force | Out-Null

foreach ($facing in $Direction) {
    $movie = Join-Path $bundle ("preview_" + $facing + ".mp4")
    $log = Join-Path $bundle ("preview_" + $facing + ".godot.log")
    $receipt = Join-Path $bundle ("preview_" + $facing + ".receipt.json")
    if (Test-Path -LiteralPath $receipt) {
        $prior = Get-Content -Raw -LiteralPath $receipt | ConvertFrom-Json
        $movieSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $movie).Hash.ToLowerInvariant()
        $logSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $log).Hash.ToLowerInvariant()
        if ($prior.projectSha256 -ne $projectSha -or $prior.movieSha256 -ne $movieSha -or $prior.logSha256 -ne $logSha) {
            throw "Existing capture no longer matches its receipt: $facing"
        }
        Write-Output "SANCTUARY_CAPTURE_ALREADY_VERIFIED $facing"
        continue
    }
    $avi = Join-Path $scratch ("sanctuary_" + $facing + ".avi")
    $temporaryMovie = Join-Path $scratch ("sanctuary_" + $facing + ".mp4")
    & $GodotPath --path (Join-Path $repo 'ClientGodot') --write-movie $avi --fixed-fps 60 --quit-after 324 ArtStudio.tscn -- --studio-project $project --studio-direction $facing --studio-play --studio-fixed-view --studio-clean-view --studio-trace-layers *> $log
    if ($LASTEXITCODE -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR' -Quiet)) { throw "Studio capture failed for $facing" }
    $logText = [IO.File]::ReadAllText($log).Replace("`r`n", "`n")
    [IO.File]::WriteAllText($log, $logText, [Text.UTF8Encoding]::new($false))
    & $FfmpegPath -v error -y -i $avi -an -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $temporaryMovie
    if ($LASTEXITCODE) { throw "Movie encoding failed for $facing" }
    & $FfmpegPath -v error -i $temporaryMovie -map 0:v:0 -f null -
    if ($LASTEXITCODE) { throw "Movie decode failed for $facing" }
    Move-Item -LiteralPath $temporaryMovie -Destination $movie -Force
    [ordered]@{
        direction = $facing
        frameClock = 60
        projectSha256 = $projectSha
        movieSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $movie).Hash.ToLowerInvariant()
        logSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $log).Hash.ToLowerInvariant()
    } | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
    foreach ($temporary in @($avi, [IO.Path]::ChangeExtension($avi, '.wav'))) {
        if (Test-Path -LiteralPath $temporary -PathType Leaf) { Remove-Item -LiteralPath $temporary -Force }
    }
    Write-Output "SANCTUARY_CAPTURE_COMPLETE $facing"
}
