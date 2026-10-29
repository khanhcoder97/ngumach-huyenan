#!/usr/bin/env python3
"""Headless end-to-end scenario for the P1 gameplay loop (QOD-15).

Two profiles, matching the production gates:

  default — server started WITHOUT the P1 feature flags (production
            profile). Expected blocked output: the quest accept, interact
            and turn-in POST handlers are not mapped, so the requests
            match the GET read routes instead and return HTTP 405,
            while sessions, movement and read endpoints keep working.

  dev     — server started WITH P1__QuestAccept__Enabled=true,
            P1__Interact__Enabled=true, P1__QuestTurnIn__Enabled=true
            (dev synthetic scenario). Runs the full loop: create session
            -> valid move -> wall-crossing attempt -> accept quest ->
            collect packages -> READY_TO_TURN_IN -> turn-in -> replay
            same key -> new key rejected -> inventory/quest readback ->
            parallel turn-ins grant exactly once.

The Bến Mưa topology fixture is SYNTHETIC_TEST_ONLY, so wall
enforcement is NotEnforced on the server: the wall-crossing move
succeeds and this script records "wall_enforcement=not_enforced". If a
REVIEWED bundle is ever loaded, the same move must return 422
movement_blocked; the script accepts exactly those two outcomes and
fails on anything else.

Usage: e2e_p1.py <base_url> <default|dev>
"""

import sys
import threading
import time

import smoke_p1

STEP_SECONDS = 0.3
WALL_X_MIN = 45.0
WALL_X_MAX = 46.0
TURN_IN_NPC_X = 64.0
PACKAGES = {
    "ENT_MAN_BM_OBJ_BM_PACKAGE_01": 36.0,
    "ENT_MAN_BM_OBJ_BM_PACKAGE_02": 44.0,
    "ENT_MAN_BM_OBJ_BM_PACKAGE_03": 52.0,
}


def fail(message):
    raise AssertionError(message)


def world_x(session_id):
    status, _, body = smoke_p1.call(
        "GET", f"/p1/world/{session_id}")
    smoke_p1.check(status == 200, f"world read returned {status}: {body}")
    return ((body.get("result") or {}).get("self") or {}).get("x", 0)


def walk_east(session_id, character_id, start_sequence, stop_before_x):
    """Move +x in 1.5-WU steps until x >= stop_before_x. Returns (sequence, x)."""
    sequence = start_sequence
    x = world_x(session_id)
    while x < stop_before_x:
        sequence += 1
        time.sleep(STEP_SECONDS)
        status, _, body = smoke_p1.call(
            "POST", "/p1/move",
            smoke_p1.move_envelope(sequence, 1, 0, character_id=character_id),
            {"X-Session-ID": session_id})
        smoke_p1.check(status == 200, f"move {sequence} returned {status}: {body}")
        x = ((body.get("result") or {}).get("self") or {}).get("x", x)
    return sequence, x


def collect_package(session_id, character_id, sequence, target_id, request_id,
                    idempotency_key, expected_counter, expected_state,
                    expected_revision):
    # P00-01 packages are per-character claims (Production Rules §5): the first
    # character's claim never removes the world item for anyone else, so no
    # respawn wait or retry loop is needed.
    status, _, body = smoke_p1.call(
        "POST", "/p1/world/interact",
        smoke_p1.interact_envelope(
            target_id, character_id=character_id,
            request_id=request_id,
            idempotency_key=idempotency_key),
        {"X-Session-ID": session_id})
    smoke_p1.check(status == 200, f"interact {target_id} returned {status}: {body}")
    check = body.get("result") or {}
    smoke_p1.check(check.get("targetState") == "AVAILABLE",
                   f"{target_id} targetState {check.get('targetState')}")
    updates = (check.get("questUpdates")) or [{}]
    update = updates[0]
    smoke_p1.check(update.get("state") == expected_state,
                   f"{target_id} state {update.get('state')} != {expected_state}")
    smoke_p1.check(update.get("revision") == expected_revision,
                   f"{target_id} revision {update.get('revision')} != {expected_revision}")
    smoke_p1.check(update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": expected_counter},
                   f"{target_id} counters {update.get('objectiveCounters')}")
    return sequence


def prepare_ready_actor(character_id):
    """Create a session, walk to the quest NPC, accept P00-01 and collect
    the first two packages. Returns (session_id, next_sequence)."""
    sequence = 1
    status, _, body = smoke_p1.call(
        "POST", "/p1/sessions", {"characterId": character_id})
    smoke_p1.check(status == 201, f"session returned {status}: {body}")
    session = body.get("sessionId")
    smoke_p1.check(isinstance(session, str) and len(session) == 32,
                   f"unexpected sessionId {session}")
    smoke_p1.check((body.get("result") or {}).get("mapId") == "MAP_BEN_MUA",
                   f"unexpected map {(body.get('result') or {}).get('mapId')}")

    sequence, _ = walk_east(session, character_id, sequence, 37.5)

    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/accept",
        smoke_p1.quest_accept_envelope("P00-01", "NPC_LYAN", character_id=character_id,
                                       request_id="a" * 32, idempotency_key="b" * 32),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"accept returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("state") == "ACTIVE",
                   f"accept state {(body.get('result') or {}).get('state')}")

    collect_package(session, character_id, sequence, "ENT_MAN_BM_OBJ_BM_PACKAGE_01",
                    "c" * 32, "d" * 32, 1, "ACTIVE", 3)

    sequence, _ = walk_east(session, character_id, sequence, 39.5)
    collect_package(session, character_id, sequence, "ENT_MAN_BM_OBJ_BM_PACKAGE_02",
                    "e" * 32, "f" * 32, 2, "ACTIVE", 4)

    sequence, _ = walk_east(session, character_id, sequence, 43.5)
    return session, sequence


def default_profile():
    smoke_p1.check(
        smoke_p1.call("GET", "/health")[0] == 200, "health check failed")

    status, _, body = smoke_p1.call("POST", "/p1/sessions", {"characterId": "CHR_E2E_DEFAULT"})
    smoke_p1.check(status == 201, f"session returned {status}: {body}")
    session_id = body.get("sessionId")

    time.sleep(STEP_SECONDS)
    status, _, body = smoke_p1.call(
        "POST", "/p1/move",
        smoke_p1.move_envelope(1, 1, 0, character_id="CHR_E2E_DEFAULT"),
        {"X-Session-ID": session_id})
    smoke_p1.check(status == 200, f"move returned {status}: {body}")
    smoke_p1.check(
        ((body.get("result") or {}).get("self") or {}).get("x", 0) > 18,
        "move did not advance x")

    for path, label in [
        ("/p1/quests/accept", "quest_accept"),
        ("/p1/world/interact", "interact"),
        ("/p1/quests/turnin", "quest_turnin"),
    ]:
        status, _, body = smoke_p1.call(
            "POST", path,
            smoke_p1.turnin_envelope("P00-01", "NPC_LYAN",
                                     character_id="CHR_E2E_DEFAULT"),
            {"X-Session-ID": session_id})
        # Gates OFF: the gated POST handler is not mapped, but the path still
        # matches the GET read route (/p1/quests/{sessionId} or
        # /p1/world/{sessionId}) so minimal APIs answer 405, not 404.
        smoke_p1.check(
            status == 405,
            f"{label} expected 405 (gate OFF), got {status}: {body}")

    smoke_p1.check(
        smoke_p1.call("GET", f"/p1/quests/{session_id}")[0] == 200,
        "quests read must stay available with gates OFF")
    smoke_p1.check(
        smoke_p1.call("GET", f"/p1/inventory/{session_id}")[0] == 200,
        "inventory read must stay available with gates OFF")

    print("profile=default expected_blocked_output=OK "
          "(gated POST handlers unmapped, HTTP 405 via read-route match)")


def dev_profile():
    character_id = "CHR_E2E_DEV"
    session, sequence = prepare_ready_actor(character_id)

    # Wall-crossing attempt: the walk to package 3 crosses the blocked rect
    # x in [45,46] on y=0. The fixture topology is SYNTHETIC_TEST_ONLY so the
    # server does not enforce walls; record which behavior is active.
    wall_state = "unknown"
    sequence += 1
    time.sleep(STEP_SECONDS)
    status, _, body = smoke_p1.call(
        "POST", "/p1/move",
        smoke_p1.move_envelope(sequence, 1, 0, character_id=character_id),
        {"X-Session-ID": session})
    error = body.get("error") or {}
    if status == 200:
        wall_state = "not_enforced"
    elif status == 422 and error.get("code") == "movement_blocked":
        wall_state = "enforced"
        fail("wall became enforced (REVIEWED topology); the dev fixture "
             "scenario needs a path around x=45..46")
    else:
        fail(f"wall-crossing move returned {status}: {body}")
    smoke_p1.check(
        wall_state in ("not_enforced", "enforced"),
        f"unexpected wall_state {wall_state}")

    if wall_state == "not_enforced":
        sequence, _ = walk_east(session, character_id, sequence, 47.5)
        smoke_p1.check(world_x(session) >= 47.5, "walk to package 3 failed")
    collect_package(session, character_id, sequence, "ENT_MAN_BM_OBJ_BM_PACKAGE_03",
                    "10" * 16, "11" * 16, 3, "READY_TO_TURN_IN", 5)

    status, _, body = smoke_p1.call(
        "GET", f"/p1/quests/{session}")
    smoke_p1.check(status == 200, f"quests returned {status}: {body}")
    ready = (body.get("result") or [{}])[0]
    smoke_p1.check(ready.get("state") == "READY_TO_TURN_IN",
                   f"read back state {ready.get('state')}")

    sequence, _ = walk_east(session, character_id, sequence, TURN_IN_NPC_X)

    # Turn-in: success, replay same key, new key rejected, single reward.
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_id,
                                 request_id="12" * 16, idempotency_key="13" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"turn-in returned {status}: {body}")
    result = body.get("result") or {}
    quest_state = result.get("questState") or {}
    smoke_p1.check(quest_state.get("state") == "COMPLETED",
                   f"turn-in state {quest_state.get('state')}")
    smoke_p1.check(quest_state.get("revision") == 6,
                   f"turn-in revision {quest_state.get('revision')}")
    rewards = result.get("rewards") or {}
    smoke_p1.check(
        (rewards.get("currency") or [{}])[0].get("amount") == 20,
        f"currency reward {rewards.get('currency')}")
    smoke_p1.check(
        (rewards.get("items") or [{}])[0].get("templateId") == "EQ-MK-CHEST-T1-R-COMMON",
        f"item reward {rewards.get('items')}")
    smoke_p1.check(
        (rewards.get("xp") or {}).get("applied") is False,
        f"xp reward {rewards.get('xp')}")
    smoke_p1.check(result.get("unlocks") == ["P00-02"],
                   f"unlocks {result.get('unlocks')}")

    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_id,
                                 request_id="14" * 16, idempotency_key="13" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"turn-in replay returned {status}: {body}")
    smoke_p1.check(
        ((body.get("result") or {}).get("questState") or {}).get("state") == "COMPLETED",
        "replay must return the stored COMPLETED result")

    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_id,
                                 request_id="15" * 16, idempotency_key="16" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 409, f"second turn-in returned {status}: {body}")
    smoke_p1.check((body.get("error") or {}).get("code") == "invalid_transition",
                   f"second turn-in error {(body.get('error') or {}).get('code')}")

    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session}")
    smoke_p1.check(status == 200, f"inventory returned {status}: {body}")
    inventory = body.get("result") or {}
    smoke_p1.check(len(inventory.get("currencies") or []) == 1 and
                   inventory["currencies"][0].get("amount") == 20,
                   f"currency after turn-in {inventory.get('currencies')}")
    smoke_p1.check(len(inventory.get("items") or []) == 1,
                   f"items after turn-in {inventory.get('items')}")

    # Invalid ownership/session guards on the turn-in endpoint.
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id="CHR_E2E_WRONG",
                                 request_id="17" * 16, idempotency_key="18" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 400, f"wrong character turn-in returned {status}: {body}")
    smoke_p1.check("characterId" in ((body.get("error") or {}).get("fieldErrors") or []),
                   "characterId field error missing")

    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_id,
                                 request_id="19" * 16, idempotency_key="20" * 16),
        {"X-Session-ID": "f" * 32})
    smoke_p1.check(status == 404, f"unknown session turn-in returned {status}: {body}")
    smoke_p1.check((body.get("error") or {}).get("code") == "session_not_found",
                   f"unknown session error {(body.get('error') or {}).get('code')}")

    # Parallel turn-ins with different keys must grant exactly once. Packages
    # are per-character claims, so the second character collects them with no
    # respawn wait.
    parallel_session, parallel_sequence = prepare_ready_actor("CHR_E2E_PARALLEL")
    sequence, _ = walk_east(
        parallel_session, "CHR_E2E_PARALLEL", parallel_sequence, 47.5)
    collect_package(parallel_session, "CHR_E2E_PARALLEL", sequence,
                    "ENT_MAN_BM_OBJ_BM_PACKAGE_03",
                    "25" * 16, "26" * 16, 3, "READY_TO_TURN_IN", 5)
    sequence, _ = walk_east(
        parallel_session, "CHR_E2E_PARALLEL", sequence, TURN_IN_NPC_X)

    outcomes = {}

    def turn_in_worker(key, request_id, slot):
        status, _, body = smoke_p1.call(
            "POST", "/p1/quests/turnin",
            smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                     character_id="CHR_E2E_PARALLEL",
                                     request_id=request_id, idempotency_key=key),
            {"X-Session-ID": parallel_session})
        outcomes[slot] = (status, body)

    threads = [
        threading.Thread(target=turn_in_worker, args=("21" * 16, "22" * 16, 0)),
        threading.Thread(target=turn_in_worker, args=("23" * 16, "24" * 16, 1)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    statuses = [outcomes[0][0], outcomes[1][0]]
    smoke_p1.check(
        statuses.count(200) == 1 and statuses.count(409) == 1,
        f"parallel turn-ins returned {statuses}")
    rejected = outcomes[0] if outcomes[0][0] == 409 else outcomes[1]
    smoke_p1.check(
        (rejected[1].get("error") or {}).get("code") == "invalid_transition",
        f"parallel loser error {(rejected[1].get('error') or {}).get('code')}")

    status, _, body = smoke_p1.call(
        "GET", f"/p1/inventory/{parallel_session}")
    smoke_p1.check(status == 200, f"parallel inventory returned {status}: {body}")
    parallel_inventory = body.get("result") or {}
    smoke_p1.check(
        len(parallel_inventory.get("currencies") or []) == 1 and
        parallel_inventory["currencies"][0].get("amount") == 20 and
        len(parallel_inventory.get("items") or []) == 1,
        f"parallel inventory {parallel_inventory}")

    # Two characters claim the same P00-01 package at the same time:
    # per-character claims (Production Rules §5) mean neither waits for the
    # other's window, and the world state stays AVAILABLE for both.
    concurrent_actors = []
    for index, suffix in enumerate(("A", "B")):
        character_id = f"CHR_E2E_CONCURRENT_{suffix}"
        status, _, body = smoke_p1.call(
            "POST", "/p1/sessions", {"characterId": character_id})
        smoke_p1.check(
            status == 201, f"concurrent session {suffix} returned {status}: {body}")
        session_id = body.get("sessionId")
        sequence, _ = walk_east(session_id, character_id, 0, 36.0)
        status, _, body = smoke_p1.call(
            "POST", "/p1/quests/accept",
            smoke_p1.quest_accept_envelope(
                "P00-01", "NPC_LYAN", character_id=character_id,
                request_id=f"{5 + index}" * 32, idempotency_key=f"{3 + index}" * 32),
            {"X-Session-ID": session_id})
        smoke_p1.check(
            status == 200, f"concurrent accept {suffix} returned {status}: {body}")
        concurrent_actors.append((index, session_id, character_id))

    concurrent_outcomes = {}

    def collect_worker(slot, session_id, character_id):
        status, _, body = smoke_p1.call(
            "POST", "/p1/world/interact",
            smoke_p1.interact_envelope(
                "ENT_MAN_BM_OBJ_BM_PACKAGE_01", character_id=character_id,
                request_id=f"{7 + slot}" * 32, idempotency_key=f"{9 + slot}" * 32),
            {"X-Session-ID": session_id})
        concurrent_outcomes[slot] = (status, body)

    workers = [
        threading.Thread(target=collect_worker, args=actor)
        for actor in concurrent_actors
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    for slot in (0, 1):
        status, body = concurrent_outcomes[slot]
        smoke_p1.check(
            status == 200, f"concurrent collect {slot} returned {status}: {body}")
        result = body.get("result") or {}
        smoke_p1.check(
            result.get("targetState") == "AVAILABLE",
            f"concurrent collect targetState {result.get('targetState')}")
        update = ((result.get("questUpdates")) or [{}])[0]
        smoke_p1.check(
            update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 1},
            f"concurrent collect counters {update.get('objectiveCounters')}")

    print(f"profile=dev wall_enforcement={wall_state} "
          "golden_loop=OK parallel_reward_once=OK concurrent_package_claim=OK")


def main():
    if len(sys.argv) < 3:
        fail("usage: e2e_p1.py <base_url> <default|dev>")
    smoke_p1.BASE_URL = sys.argv[1].rstrip("/")
    mode = sys.argv[2]
    if mode == "default":
        default_profile()
    elif mode == "dev":
        dev_profile()
    else:
        fail(f"unknown mode '{mode}' (expected default|dev)")

    print(f"PASS: e2e_p1 ({mode}) {smoke_p1.CHECKS} checks against {smoke_p1.BASE_URL}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as failure:
        print(f"FAIL: {failure}", file=sys.stderr)
        sys.exit(1)
    except Exception as failure:
        print(f"FAIL: {failure}", file=sys.stderr)
        sys.exit(1)
