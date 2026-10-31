#!/usr/bin/env bash
# Headless E2E runner (QOD-15): builds the server, starts it with the chosen
# profile and drives the P1 scenario against it — one command, no manual steps.
#
#   ./Server/Health/Smoke/run_e2e_p1.sh default   # production gates OFF, expects blocked output
#   ./Server/Health/Smoke/run_e2e_p1.sh dev       # dev synthetic scenario, full golden loop
#   ./Server/Health/Smoke/run_e2e_p1.sh mob-combat # live mob combat: the combat
#                                                  # gates only, quest gates stay
#                                                  # OFF, plus endurance pools so
#                                                  # one actor survives every phase
#
# Requires: dotnet SDK (10.x), python3, curl.

set -u

PROFILE="${1:-dev}"
PORT="${E2E_PORT:-5081}"
BASE_URL="http://127.0.0.1:${PORT}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
HEALTH_BIN="${ROOT}/Server/Health/bin/Release/net10.0/Health.dll"
LOG_FILE="$(mktemp)"
PID_FILE="$(mktemp)"

cleanup() {
  if [ -f "${PID_FILE}" ]; then
    kill "$(cat "${PID_FILE}")" 2>/dev/null || true
    wait "$(cat "${PID_FILE}")" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "==> Building server"
dotnet build "${ROOT}/Server/Health/Health.csproj" --configuration Release || exit 1

echo "==> Starting server (profile=${PROFILE}, port=${PORT})"
if [ "${PROFILE}" = "dev" ]; then
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
elif [ "${PROFILE}" = "mob-combat" ]; then
  # Combat gates only. The starting pools are enlarged purely so one actor can
  # walk, escape, take hits, guard and then die inside a single run; every
  # per-hit number still comes from the shipped formula and fixture values.
  P1__CombatV2__Enabled=true \
  P1__CombatDamage__Enabled=true \
  P1__MobBehavior__Enabled=true \
  P1World__StartingHp=400 \
  P1World__StartingMaxHp=400 \
  P1World__StartingMp=200 \
  P1World__StartingMaxMp=200 \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
else
  dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
fi
echo $! > "${PID_FILE}"

for attempt in $(seq 1 60); do
  if curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1; then
    echo "==> Server healthy after ${attempt}s"
    break
  fi
  if ! kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo "==> Server exited during startup"
    cat "${LOG_FILE}"
    exit 1
  fi
  sleep 1
done

if ! curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1; then
  echo "==> Server did not become healthy within 60s"
  cat "${LOG_FILE}"
  exit 1
fi

echo "==> Running E2E scenario (mode=${PROFILE})"
if python3 "${SCRIPT_DIR}/e2e_p1.py" "${BASE_URL}" "${PROFILE}"; then
  echo "==> E2E PASS (profile=${PROFILE})"
  exit 0
else
  echo "==> E2E FAIL (profile=${PROFILE}); server log tail:"
  tail -n 40 "${LOG_FILE}"
  exit 1
fi
