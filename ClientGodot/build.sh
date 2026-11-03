#!/usr/bin/env bash
# Build the Godot .NET client (compile check + NuGet restore with lockfile).
# Toolchain: .NET SDK 8.0.x (the apt/Ubuntu SDK must NOT be used — it pins a
# distro-only runtime pack; use the official Microsoft SDK tarball).
# Requires the vendored NuGet feed at ../nuget-local (see ../nuget-local/PACKAGES.md;
# run ../nuget-local/fetch_feed.sh once if the .nupkg files are absent).
set -euo pipefail
cd "$(dirname "$0")"
if [ -n "${DOTNET_ROOT:-}" ]; then export PATH="$DOTNET_ROOT:$PATH"; fi
dotnet restore NgumachPrototype.csproj
dotnet build NgumachPrototype.csproj -c Debug --no-restore
echo "BUILD OK"
