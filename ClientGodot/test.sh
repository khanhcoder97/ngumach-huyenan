#!/usr/bin/env bash
# Headless test battery for the Godot .NET client.
#
# Offline suites (8) always run. The two online suites (NETTEST, ONLINETEST)
# additionally need Qoder's P1 server slice: set NGUMACH_P1_SERVER_DIR to the
# Server/Health project directory and NGUMACH_SERVER_DOTNET to the dotnet
# binary that runs it (the slice currently targets a newer SDK than the
# client's; on the Muse VM that is /usr/local/dotnet10b/dotnet).
#
# Required env:
#   GODOT_BIN   path to the Godot 4.7.2 stable MONO editor binary
# Optional env:
#   DOTNET_ROOT             .NET SDK 8 root for the client build
#   NGUMACH_P1_SERVER_DIR   enables the online suites when set
#   NGUMACH_SERVER_DOTNET   dotnet for the server (default: dotnet)
#
# Exit code 0 only if every executed suite passes. Suites print
# "<NAME> RESULT: PASS/FAIL" lines; this script aggregates them.
set -uo pipefail
PROJ="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${DOTNET_ROOT:-}" ]; then export PATH="$DOTNET_ROOT:$PATH"; fi
: "${GODOT_BIN:?set GODOT_BIN to the Godot 4.7.2 stable mono editor binary}"
PASS=0; FAIL=0; FAILED_SUITES=""

run_suite() { # name, scene, args...
  local name="$1"; shift
  local out
  out=$(timeout 180 "$GODOT_BIN" --headless --path "$PROJ" "$@" 2>&1 | grep -E "RESULT" | tail -1)
  echo "[$name] $out"
  if echo "$out" | grep -q "RESULT: PASS"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); FAILED_SUITES="$FAILED_SUITES $name"; fi
}

echo "=== build ==="
(cd "$PROJ" && dotnet build 2>&1 | grep -E "Build succ|error" | head -3)

echo "=== offline suites ==="
run_suite SELFTEST   -- --selftest
run_suite TILEMTEST  TilemapTest.tscn -- --tilemtest
run_suite FULLTEST   FullMapTest.tscn -- --fulltest
run_suite HUDTEST    HudTest.tscn -- --hudtest
run_suite ANIMTEST   AnimTest.tscn -- --animtest
run_suite DETAILTEST DetailTest.tscn -- --detailtest
run_suite CLASSTEST  ClassTest.tscn -- --classtest
run_suite SELECTTEST OnlineTest.tscn -- --selecttest

if [ -n "${NGUMACH_P1_SERVER_DIR:-}" ]; then
  echo "=== starting P1 server (Qoder slice, unmodified) ==="
  (cd "$NGUMACH_P1_SERVER_DIR" && ASPNETCORE_URLS=http://127.0.0.1:5000 DOTNET_CLI_TELEMETRY_OPTOUT=1 "${NGUMACH_SERVER_DOTNET:-dotnet}" run --no-build > /tmp/p1server.log 2>&1 &)
  for i in $(seq 1 30); do
    if curl -s -m 2 http://127.0.0.1:5000/health >/dev/null 2>&1; then echo "server up"; break; fi
    sleep 1
  done
  echo "=== online suites ==="
  run_suite NETTEST    NetTest.tscn -- --nettest
  run_suite ONLINETEST OnlineTest.tscn -- --onlinetest
  echo "=== stopping server ==="
  fuser -k 5000/tcp 2>/dev/null || true
else
  echo "=== online suites SKIPPED (NGUMACH_P1_SERVER_DIR not set) ==="
fi

echo "=============================="
echo "SUITES PASS: $PASS  FAIL: $FAIL${FAILED_SUITES:+  (failed:$FAILED_SUITES)}"
[ "$FAIL" -eq 0 ]
