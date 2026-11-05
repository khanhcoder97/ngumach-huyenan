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
#   ./Server/Health/Smoke/run_e2e_p1.sh alpha-p00  # the private-alpha tutorial
#                                                  # chain P00-01..P00-05 + C1-01
#                                                  # over real HTTP: every gameplay
#                                                  # gate plus P1:AlphaProfile, and
#                                                  # endurance pools for the boss
#   ./Server/Health/Smoke/run_e2e_p1.sh death-return # the approved return route:
#                                                  # die to mob damage, return
#                                                  # to the design anchor, replay
#                                                  # as a pure read, 5 negatives
#   ./Server/Health/Smoke/run_e2e_p1.sh gate-one    # E2E_GATE names ONE gate; the
#                                                  # profile then asserts which routes
#                                                  # that gate maps and that every other
#                                                  # gated route stays unmapped
#                                                  # E2E_GATE=AlphaLoot is the exception:
#                                                  # that combination must not boot, so the
#                                                  # leg asserts no listener plus the refusal
#                                                  # text in the startup log
#   ./Server/Health/Smoke/run_e2e_p1.sh restart     # work order 29 Q8 restart HTTP
#                                                  # proof: loop in process #1, stop the
#                                                  # owned PID, assert nothing survived
#                                                  # in process #2 on the same port
#   ./Server/Health/Smoke/run_e2e_p1.sh audience-gateoff
#                                                  # the issue #96 shape: v2 world
#                                                  # and mob AI ON, P1:CombatDamage
#                                                  # OFF, so no mob stats exist
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
  if [ -n "${E2E_EVIDENCE:-}" ] && [ -f "${E2E_EVIDENCE}" ]; then
    rm -f "${E2E_EVIDENCE}"
  fi
}
trap cleanup EXIT

# Stop the process this runner started and prove the port is really free before the
# next boot: a restart proof that races a still-listening socket proves nothing.
stop_owned_pid() {
  local pid="$1"
  kill "${pid}" 2>/dev/null || true
  for _ in $(seq 1 15); do
    curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1 || return 0
    sleep 1
  done
  # On Windows the bash job id is not the socket owner's pid, so resolve whatever is
  # still answering on the port this runner chose and stop that. The port was free
  # before the boot above, so the listener can only be the server this runner started.
  if command -v taskkill > /dev/null 2>&1 && command -v netstat > /dev/null 2>&1; then
    local listener
    listener="$(netstat -ano -p tcp 2>/dev/null |
      awk -v port=":${PORT}" '$2 ~ port"$" && $4 == "LISTENING" { print $5; exit }')"
    if [ -n "${listener}" ]; then
      echo "==> stopping socket owner ${listener} on port ${PORT}"
      taskkill //PID "${listener}" //F > /dev/null 2>&1 || true
    fi
  fi
  for _ in $(seq 1 15); do
    curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1 || return 0
    sleep 1
  done
  echo "==> port ${PORT} still answering after stopping owned PID ${pid}" >&2
  return 1
}

wait_healthy() {
  for attempt in $(seq 1 60); do
    if curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1; then
      echo "==> Server healthy after ${attempt}s"
      return 0
    fi
    if ! kill -0 "$1" 2>/dev/null; then
      echo "==> Server exited during startup"
      cat "${LOG_FILE}"
      return 1
    fi
    sleep 1
  done
  echo "==> Server did not become healthy within 60s"
  cat "${LOG_FILE}"
  return 1
}

# Work order 29 Q8: "Phải có restart HTTP proof trước khi gọi Health durable". Two
# successive processes on one port, and the runner owns and stops both PIDs, so the
# pair is a real process restart rather than a second session. The gate set is dev's:
# the loop has to write quest state, currency, an item and an equipped slot before the
# process dies, because those are exactly the stores the persistence proposal names.
run_restart_proof() {
  E2E_EVIDENCE="$(mktemp)"
  export E2E_EVIDENCE

  echo "==> Starting server #1 (restart proof)"
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
  P1__Equipment__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
  PID1=$!
  echo "${PID1}" > "${PID_FILE}"
  wait_healthy "${PID1}" || exit 1

  python3 "${SCRIPT_DIR}/e2e_p1.py" "${BASE_URL}" restart-before || exit 1

  echo "==> Stopping owned PID ${PID1}"
  stop_owned_pid "${PID1}" || exit 1
  wait "${PID1}" 2>/dev/null || true

  echo "==> Starting server #2 (same port, fresh process)"
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
  P1__Equipment__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
  PID2=$!
  echo "${PID2}" > "${PID_FILE}"
  wait_healthy "${PID2}" || exit 1

  if [ "${PID1}" = "${PID2}" ]; then
    echo "==> restart proof needs two distinct processes (got PID ${PID1})" >&2
    exit 1
  fi

  python3 "${SCRIPT_DIR}/e2e_p1.py" "${BASE_URL}" restart-after || {
    echo "==> restart-after failed; server #2 log tail:"
    tail -n 40 "${LOG_FILE}"
    exit 1
  }
  echo "==> E2E PASS (profile=restart pid1=${PID1} pid2=${PID2})"
  exit 0
}

echo "==> Building server"
dotnet build "${ROOT}/Server/Health/Health.csproj" --configuration Release || exit 1

if [ "${PROFILE}" = "restart" ]; then
  run_restart_proof
fi

echo "==> Starting server (profile=${PROFILE}, port=${PORT})"
if [ "${PROFILE}" = "dev" ]; then
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
  P1__Equipment__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
elif [ "${PROFILE}" = "two-client" ]; then
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
  P1__Equipment__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
elif [ "${PROFILE}" = "alpha-p00" ]; then
  # The private-alpha tutorial chain over real HTTP: every gate the opening
  # P00-01..P00-05 + C1-01 loop touches, with the alpha profile on, and
  # P1__AlphaLoot__GrantEnabled so a mob death actually pays (the profile is
  # what makes the coin band exist, and appsettings keeps both flags OFF).
  # Endurance pools are enlarged so one actor can stand in the Mãng Cốt ring
  # and live through 1200 HP of boss; damage numbers still come from the
  # shipped formula, so the run proves the chain, not a tuning claim.
  P1__AlphaProfile__Enabled=true \
  P1__QuestAccept__Enabled=true \
  P1__Interact__Enabled=true \
  P1__QuestTurnIn__Enabled=true \
  P1__Equipment__Enabled=true \
  P1__CombatV2__Enabled=true \
  P1__CombatDamage__Enabled=true \
  P1__MobBehavior__Enabled=true \
  P1__AlphaLoot__GrantEnabled=true \
  P1World__StartingHp=2000 \
  P1World__StartingMaxHp=2000 \
  P1World__StartingMp=500 \
  P1World__StartingMaxMp=500 \
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
elif [ "${PROFILE}" = "death-return" ]; then
  # DEC-DEATH-RETURN-20261105: the two gates that map the route, plus the combat
  # gates that can actually end a life. The pools are small on purpose — 10 HP is
  # one CARPLING hit, so the death is the shipped damage path rather than a
  # fixture, and max(1, ceil(10 * 0.5)) = 5 is a number only the approved formula
  # can produce. RestoreHpFixture stays 0: under the alpha profile a positive
  # fixture is a startup failure.
  P1__AlphaProfile__Enabled=true \
  P1__DeathReturn__Enabled=true \
  P1__CombatV2__Enabled=true \
  P1__CombatDamage__Enabled=true \
  P1__MobBehavior__Enabled=true \
  P1World__StartingHp=10 \
  P1World__StartingMaxHp=10 \
  P1World__StartingMp=7 \
  P1World__StartingMaxMp=7 \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
elif [ "${PROFILE}" = "audience-gateoff" ]; then
  # The configuration issue #96 was filed against: the v2 world read and the mob
  # AI are both ON, but P1:CombatDamage stays at its production default OFF, so
  # no mob stat bundle is loaded and ResolveHit cannot score a swing against
  # anything. Nothing else in this suite boots that shape, which is how an
  # ALIVE/targetable/hp-0 audience row reached a client.
  P1__CombatV2__Enabled=true \
  P1__MobBehavior__Enabled=true \
    dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
elif [ "${PROFILE}" = "gate-one" ]; then
  # One gate at a time, so that "enabling a feature cannot light up another
  # feature's route" is measured rather than assumed. The legs with no mapped
  # route (DeathReturn alone, CombatDamage, MobBehavior, AlphaLoot) are the pairing
  # proof: /p1/actor/death-return needs AlphaProfile AND DeathReturn, the two damage
  # gates never map a route of their own, and AlphaLoot must not add one even when it
  # sits next to the profile that gives it something to do.
  case "${E2E_GATE:-none}" in
    QuestAccept) GATE_ENV="P1__QuestAccept__Enabled=true" ;;
    Interact) GATE_ENV="P1__Interact__Enabled=true" ;;
    QuestTurnIn) GATE_ENV="P1__QuestTurnIn__Enabled=true" ;;
    Equipment) GATE_ENV="P1__Equipment__Enabled=true" ;;
    CombatV2) GATE_ENV="P1__CombatV2__Enabled=true" ;;
    AlphaProfile) GATE_ENV="P1__AlphaProfile__Enabled=true" ;;
    DeathReturn) GATE_ENV="P1__DeathReturn__Enabled=true" ;;
    CombatDamage) GATE_ENV="P1__CombatDamage__Enabled=true" ;;
    MobBehavior) GATE_ENV="P1__MobBehavior__Enabled=true" ;;
    AlphaLoot) GATE_ENV="P1__AlphaLoot__GrantEnabled=true" ;;
    AlphaLootAlpha) GATE_ENV="P1__AlphaLoot__GrantEnabled=true P1__AlphaProfile__Enabled=true" ;;
    DeathReturnAlpha) GATE_ENV="P1__DeathReturn__Enabled=true P1__AlphaProfile__Enabled=true" ;;
    *) echo "==> unknown E2E_GATE=${E2E_GATE:-unset}" >&2; exit 2 ;;
  esac
  # A refusal leg boots the same way but must never reach a healthy listener: the
  # composition root stops the process, and the gate-refusal profile reads why from
  # the log. AlphaLoot without AlphaProfile is that combination - the coin band only
  # exists in DESIGN-BM-ALPHA-20261103, so paying it out from any other profile is a
  # configuration the server refuses rather than a server that answers 404s.
  if [ "${E2E_GATE}" = "AlphaLoot" ]; then
    # shellcheck disable=SC2086
    env ${GATE_ENV} dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
    REFUSAL_PID=$!
    echo "${REFUSAL_PID}" > "${PID_FILE}"
    for attempt in $(seq 1 30); do
      if curl --silent --fail "${BASE_URL}/health" > /dev/null 2>&1; then
        echo "==> ${E2E_GATE} became healthy; the startup refusal is gone" >&2
        exit 1
      fi
      if ! kill -0 "${REFUSAL_PID}" 2>/dev/null; then
        break
      fi
      sleep 1
    done
    E2E_REFUSAL_LOG="${LOG_FILE}" python3 "${SCRIPT_DIR}/e2e_p1.py" \
        "${BASE_URL}" gate-refusal || {
      echo "==> gate-refusal failed; server log tail:"
      tail -n 20 "${LOG_FILE}"
      exit 1
    }
    echo "==> E2E PASS (profile=gate-one gate=${E2E_GATE} refused at startup)"
    exit 0
  fi

  # shellcheck disable=SC2086
  env ${GATE_ENV} dotnet "${HEALTH_BIN}" --urls "${BASE_URL}" > "${LOG_FILE}" 2>&1 &
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
