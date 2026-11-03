#!/usr/bin/env bash
# Export the Windows Desktop build (preset "Windows Desktop").
# Per Work Order 24 M-D: the cold import runs with an explicit timeout and
# its own log — a cold-cache import stall must surface as a failure with a
# log, never hang silently. The warm import follows, then the export.
#
# Required env: GODOT_BIN (Godot 4.7.2 stable mono editor binary with the
# 4.7.2.stable.mono export templates installed), DOTNET_ROOT (.NET SDK 8).
set -euo pipefail
PROJ="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${DOTNET_ROOT:-}" ]; then export PATH="$DOTNET_ROOT:$PATH"; fi
: "${GODOT_BIN:?set GODOT_BIN to the Godot 4.7.2 stable mono editor binary}"
mkdir -p "$PROJ/build/windows"
echo "=== cold import (timeout 600s, log: build/import_cold.log) ==="
timeout 600 "$GODOT_BIN" --headless --path "$PROJ" --import > "$PROJ/build/import_cold.log" 2>&1 || {
  echo "COLD IMPORT FAILED OR TIMED OUT — see build/import_cold.log"; exit 1; }
echo "=== export Windows Desktop ==="
"$GODOT_BIN" --headless --path "$PROJ" --export-release "Windows Desktop" "$PROJ/build/windows/NgumachPrototype.exe"
ls -la "$PROJ/build/windows/"
echo "EXPORT WINDOWS OK"
