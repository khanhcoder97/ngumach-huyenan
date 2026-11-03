#!/usr/bin/env bash
# Download the exact vendored NuGet packages listed in PACKAGES.md into this
# directory, from nuget.org's flat-container API. Idempotent: existing files
# with the right name are kept. After this runs once, `dotnet restore` in
# ClientGodot works fully offline.
set -euo pipefail
cd "$(dirname "$0")"
dl() { # id (lowercase), version, exact file name on disk
  local id="$1" ver="$2" file="$3"
  if [ -f "$file" ]; then echo "have $file"; return; fi
  echo "fetch $id $ver"
  curl -sSL -m 300 -o "$file" "https://api.nuget.org/v3-flatcontainer/$id/$ver/$id.$ver.nupkg"
}
dl godot.net.sdk 4.7.2 godot.net.sdk.4.7.2.nupkg
dl godotsharp 4.7.2 godotsharp.4.7.2.nupkg
dl godotsharpeditor 4.7.2 godotsharpeditor.4.7.2.nupkg
dl godot.sourcegenerators 4.7.2 godot.sourcegenerators.4.7.2.nupkg
dl godot.net.sdk 4.3.0 Godot.NET.Sdk.4.3.0.nupkg
dl godotsharp 4.3.0 GodotSharp.4.3.0.nupkg
dl godotsharpeditor 4.3.0 GodotSharpEditor.4.3.0.nupkg
dl godot.sourcegenerators 4.3.0 Godot.SourceGenerators.4.3.0.nupkg
dl microsoft.netcore.app.runtime.linux-x64 8.0.11 microsoft.netcore.app.runtime.linux-x64.8.0.11.nupkg
dl microsoft.netcore.app.runtime.win-x64 8.0.11 microsoft.netcore.app.runtime.win-x64.8.0.11.nupkg
dl microsoft.netcore.app.runtime.mono.android-arm64 8.0.11 microsoft.netcore.app.runtime.mono.android-arm64.8.0.11.nupkg
dl microsoft.aspnetcore.app.runtime.linux-x64 8.0.11 microsoft.aspnetcore.app.runtime.linux-x64.8.0.11.nupkg
dl microsoft.aspnetcore.app.runtime.win-x64 8.0.11 microsoft.aspnetcore.app.runtime.win-x64.8.0.11.nupkg
dl microsoft.netcore.app.runtime.linux-x64 8.0.0 microsoft.netcore.app.runtime.linux-x64.8.0.0.nupkg
dl microsoft.netcore.app.runtime.mono.android-arm64 8.0.0 microsoft.netcore.app.runtime.mono.android-arm64.8.0.0.nupkg
dl microsoft.aspnetcore.app.runtime.linux-x64 8.0.0 microsoft.aspnetcore.app.runtime.linux-x64.8.0.0.nupkg
echo "FEED READY: $(ls *.nupkg | wc -l) packages"
