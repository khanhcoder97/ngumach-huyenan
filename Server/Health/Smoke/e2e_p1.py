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

  mob-combat — server started with the combat gates only
            (P1__CombatV2__Enabled, P1__CombatDamage__Enabled,
            P1__MobBehavior__Enabled, plus larger starting HP/MP so one actor
            can live through every phase). Quest gates stay OFF: this is a
            separate fixture, not the dev scenario with more flags. Drives a
            live 20 Hz fight over HTTP with conditional waits: walk the road
            past one mob group -> read TELEGRAPH -> step out of attack range
            and prove the committed impact whiffs -> stand still and take the
            whole CARPLING hit ->
            guard the next front hit and read COUNTER_CONFIRMED plus the
            counter's own resolution against the mob's snapshot hp -> stay
            until HP reaches 0, then prove the server does not paper over
            death (no auto-heal, fresh cast refused, aggro dropped).

The Bến Mưa topology fixture is SYNTHETIC_TEST_ONLY, so wall
enforcement is NotEnforced on the server: the wall-crossing move
succeeds and the dev profile records "wall_enforcement=not_enforced". If a
REVIEWED bundle is ever loaded, the same move must return 422
movement_blocked; the script accepts exactly those two outcomes and
fails on anything else.

Usage: e2e_p1.py <base_url> <default|dev|mob-combat>
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
        sequence, _ = walk_east(session_id, character_id, 0, 37.5)
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
                request_id=("7" if slot == 0 else "8") * 32,
                idempotency_key=("9" if slot == 0 else "a") * 32),
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


# Q-B4: live mob combat driven over HTTP in its own profile. The constants below
# are the shipped DEV fixture values, written out so the scenario says what it
# waits for instead of guessing: aggro 6 WU, mob attack range 1,2 WU, telegraph
# 0,45 s, attack cooldown 2 s, mob speed 2 WU/s at 20 Hz, and CARPLING
# REFERENCE_L5 (attack 15, "Đòn thường" BITE coefficient 0,8) against the
# completion_v1 armor 10 baseline, which Production_Rules §2 floors to 10.

MOB_GROUP = (
    "ENT_MAN_BM_SPAWN_BM_01",
    "ENT_MAN_BM_SPAWN_BM_01_M2",
    "ENT_MAN_BM_SPAWN_BM_01_M3",
)
APPROACH_X = 87.0
ESCAPE_X = 91.5
CARPLING_DAMAGE = 10
CARPLING_MAX_HP = 192
AGGRO_STATES = ("AGGRO", "CHASE", "TELEGRAPH", "ATTACK", "RECOVER")


def v2_snapshot(session_id):
    """One authoritative v2 read: (status, self, entities by id, server tick)."""
    status, _, body = smoke_p1.call(
        "GET", f"/p1/v2/world/{session_id}", None, {"X-Session-ID": session_id})
    result = body.get("result") or {}
    entities = {entry.get("entityId"): entry for entry in result.get("entities") or []}
    return status, (result.get("self") or {}), entities, result.get("serverTick", 0)


def v2_events(session_id, cursor):
    """Read the session stream from cursor. Returns (status, events, nextCursor)."""
    status, _, body = smoke_p1.call(
        "GET", f"/p1/v2/events/{session_id}?cursor={cursor}", None,
        {"X-Session-ID": session_id})
    page = body.get("result") or {}
    return status, (page.get("events") or []), page.get("nextCursor", cursor)


def wait_for(deadline_seconds, probe):
    """Conditional wait: the first truthy probe result, or None after the
    deadline. It records no check per iteration on purpose — the caller asserts
    once on the outcome, so the reported check total cannot drift with timing."""
    deadline = time.monotonic() + deadline_seconds
    while True:
        outcome = probe()
        if outcome:
            return outcome
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.05)


def walk_to(session_id, character_id, sequence, target_x, target_y):
    """Walk 1,5-WU steps to a grid-aligned target, one axis at a time (the
    server clamps every step to MaxStepDistanceWu). Returns (sequence, x, y)."""
    _, self_state, _, _ = v2_snapshot(session_id)
    x = self_state.get("x", 0.0)
    y = self_state.get("y", 0.0)
    for axis, target in (("x", target_x), ("y", target_y)):
        for _ in range(200):
            current = x if axis == "x" else y
            delta = target - current
            if abs(delta) < 1e-6:
                break
            direction = 1 if delta > 0 else -1
            sequence += 1
            time.sleep(STEP_SECONDS)
            status, _, body = smoke_p1.call(
                "POST", "/p1/move",
                smoke_p1.move_envelope(
                    sequence, direction if axis == "x" else 0,
                    0 if axis == "x" else direction,
                    character_id=character_id),
                {"X-Session-ID": session_id})
            smoke_p1.check(status == 200, f"walk {axis} step {sequence} {status}: {body}")
            moved = ((body.get("result") or {}).get("self") or {})
            x = moved.get("x", x)
            y = moved.get("y", y)
        else:
            fail(f"walk along {axis} never reached {target} (stopped at {current})")
    return sequence, x, y


def mob_combat_profile():
    status, _, body = smoke_p1.call(
        "POST", "/p1/sessions", {"classId": "CLASS_MINH_KIEM"})
    smoke_p1.check(status == 201, f"mob session create returned {status}: {body}")
    created = body.get("result") or {}
    session = body.get("sessionId")
    character_id = (created.get("self") or {}).get("characterId")
    smoke_p1.check(isinstance(character_id, str) and character_id.startswith("CHR_"),
                   f"mob profile characterId {character_id}")
    start_self = created.get("self") or {}
    full_hp = start_self.get("hp", 0)
    # The profile is allowed to give this actor endurance HP/MP so one run can
    # walk, escape, take hits, guard several times and then actually die. Those
    # are pool sizes, not balance: every per-hit number below still comes from
    # the shipped formula.
    smoke_p1.check(full_hp > 200, f"mob profile did not start with endurance HP: {full_hp}")

    sequence = 1
    # Walk the road east past the group's spawn at x=84 and stop four WU beyond
    # it. The actor moves 6 WU/s while a CARPLING walks 2 WU/s, so passing
    # x=78..90 engages the group without ever being caught mid-walk.
    sequence, x, y = walk_to(session, character_id, sequence, APPROACH_X, 0.0)
    smoke_p1.check(abs(x - APPROACH_X) < 1e-6 and abs(y) < 1e-6,
                   f"approach stopped at {x},{y}")
    _, self_state, entities, _ = v2_snapshot(session)
    engaged_now = sorted(entry.get("entityId") for entry in entities.values()
                         if entry.get("kind") == "MOB" and entry.get("state") in AGGRO_STATES)
    smoke_p1.check(bool(engaged_now) and set(engaged_now) <= set(MOB_GROUP),
                   f"the road engaged something outside the SPAWN_BM_01 group: {engaged_now}")
    smoke_p1.check(self_state.get("hp") == full_hp,
                   f"the engaged group caught the actor mid-walk: {self_state.get('hp')}")

    def telegraphed_mob():
        _, _, entities, _ = v2_snapshot(session)
        return next((entry for entry in entities.values()
                     if entry.get("kind") == "MOB" and entry.get("state") == "TELEGRAPH"),
                    None)

    telegraph = wait_for(15, telegraphed_mob)
    smoke_p1.check(telegraph is not None, "the engaged mob never opened a TELEGRAPH")

    # Step out of the 1,2 WU attack range before the committed impact frame.
    # Three steps: the mob walks 2 WU/s, so 4,5 WU of separation buys the whole
    # read window plus the next telegraph's approach.
    for _ in range(3):
        sequence += 1
        time.sleep(STEP_SECONDS)
        status, _, body = smoke_p1.call(
            "POST", "/p1/move",
            smoke_p1.move_envelope(sequence, 1, 0, character_id=character_id),
            {"X-Session-ID": session})
        smoke_p1.check(status == 200, f"escape step {sequence} {status}: {body}")
    _, self_state, _, _ = v2_snapshot(session)
    smoke_p1.check(abs(self_state.get("x", 0) - ESCAPE_X) < 1e-6,
                   f"escape stopped at {self_state.get('x')}")
    time.sleep(0.7)
    _, self_state, _, _ = v2_snapshot(session)
    smoke_p1.check(self_state.get("hp") == full_hp,
                   f"the committed telegraph still landed after stepping out of range: "
                   f"{full_hp} -> {self_state.get('hp')}")

    # Stand still: the range recheck at the impact tick gates the damage, it does
    # not cancel the fight, so the next committed impact must actually hit.
    def hp_dropped():
        _, self_state, _, _ = v2_snapshot(session)
        hp = self_state.get("hp", full_hp)
        return self_state if hp < full_hp else None

    hurt = wait_for(25, hp_dropped)
    smoke_p1.check(hurt is not None, "standing in range produced no mob damage")
    drop = full_hp - hurt.get("hp")
    smoke_p1.check(drop % CARPLING_DAMAGE == 0,
                   f"mob damage {drop} is not a whole number of CARPLING hits "
                   f"({CARPLING_DAMAGE})")

    # DEC-022 over HTTP: a guard cast facing the attacker must confirm on the
    # front hit and reserve a counter. The window is 8 ticks, so the cast has to
    # be issued inside the read window; retry until one confirms.
    events = []
    event_cursor = 0

    def drain_events():
        nonlocal event_cursor
        status, page, next_cursor = v2_events(session, event_cursor)
        if status == 200:
            events.extend(page)
            event_cursor = max(next_cursor, event_cursor)

    def find_event(event_type, cast_id=None, target_id=None):
        return next((event for event in events
                     if event.get("type") == event_type
                     and (cast_id is None or event.get("castId") == cast_id)
                     and (target_id is None or event.get("targetId") == target_id)), None)

    guard_cast = None
    guard_casts = 0
    confirmation = None
    for attempt in range(8):
        _, alive_check, _, _ = v2_snapshot(session)
        if alive_check.get("hp", 0) <= 0:
            break
        telegraph = wait_for(15, telegraphed_mob)
        if telegraph is None:
            continue
        sequence += 1
        cast_key = f"{0xc0 + attempt:032x}"
        cast_request = f"{0xd0 + attempt:032x}"
        status, _, body = smoke_p1.call(
            "POST", "/p1/v2/combat",
            smoke_p1.combat_v2_envelope(
                "SKILL", sequence, skill_id="SK-MK-01", character_id=character_id,
                request_id=cast_request, idempotency_key=cast_key, aim_x=-1),
            {"X-Session-ID": session})
        smoke_p1.check(
            status in (200, 409),
            f"guard cast {attempt} returned an unexpected {status}: {body}")
        result = body.get("result") or {}
        if status != 200 or not result.get("castId"):
            # A refused cast (cooldown, resource) is a normal retry signal here;
            # the leg asserts that at least one guard actually opened.
            continue
        guard_casts += 1
        guard_cast = result.get("castId")

        def confirmed(cid=guard_cast):
            drain_events()
            return find_event("COUNTER_CONFIRMED", cast_id=cid)

        confirmation = wait_for(1.0, confirmed)
        if confirmation:
            break

    _, hp_at_guard, _, _ = v2_snapshot(session)
    smoke_p1.check(guard_casts > 0, "every guard cast was refused")
    smoke_p1.check(confirmation is not None,
                   f"no COUNTER_CONFIRMED appeared for any of the {guard_casts} guard "
                   f"casts (hp now {hp_at_guard.get('hp')})")
    counter_source = confirmation.get("targetId")
    smoke_p1.check(counter_source in MOB_GROUP,
                   f"confirmation targeted something outside the engaged group: "
                   f"{counter_source}")

    def resolved_counter(cid=guard_cast):
        drain_events()
        return find_event("IMPACT", cast_id=cid) or find_event("MISS", cast_id=cid)

    counter = wait_for(2.0, resolved_counter)
    smoke_p1.check(counter is not None, "the reserved counter never resolved")
    smoke_p1.check(counter.get("targetId") == counter_source,
                   f"counter retargeted: {counter.get('targetId')} != {counter_source}")

    def mob_in_snapshot(entity_id):
        _, _, entities, _ = v2_snapshot(session)
        return entities.get(entity_id)

    if counter.get("type") == "IMPACT":
        hp_damage = (counter.get("result") or {}).get("hpDamage", 0)
        mob = wait_for(3, lambda: mob_in_snapshot(counter_source))
        smoke_p1.check(hp_damage > 0 and mob is not None and
                       mob.get("maxHp") == CARPLING_MAX_HP and
                       mob.get("hp") == CARPLING_MAX_HP - hp_damage,
                       f"counter damage {hp_damage} does not match the snapshot hp "
                       f"{None if mob is None else mob.get('hp')}")
        print(f"profile=mob-combat counter_hit={hp_damage} on {counter_source}")
    else:
        print(f"profile=mob-combat counter_missed_on={counter_source}")

    # Death: standing next to the group must finish the actor, and the server
    # must not paper over it — no auto-heal, no new casts, aggro drops.
    def hp_zero():
        _, self_state, _, _ = v2_snapshot(session)
        return self_state if self_state.get("hp", 1) == 0 else None

    downed = wait_for(90, hp_zero)
    smoke_p1.check(downed is not None, "standing in range never led to death")
    _, self_state, _, _ = v2_snapshot(session)
    smoke_p1.check(self_state.get("hp") == 0, f"downed actor hp {self_state.get('hp')}")

    sequence += 1
    status, _, body = smoke_p1.call(
        "POST", "/p1/v2/combat",
        smoke_p1.combat_v2_envelope(
            "BASIC_ATTACK", sequence, character_id=character_id,
            request_id="e" * 32, idempotency_key="f" * 32),
        {"X-Session-ID": session})
    smoke_p1.check(status == 409 and
                   (body.get("error") or {}).get("code") == "actor_not_alive",
                   f"downed actor cast returned {status}: {body}")

    time.sleep(3)
    _, self_state, _, _ = v2_snapshot(session)
    smoke_p1.check(self_state.get("hp") == 0,
                   f"HP came back on its own: {self_state.get('hp')}")

    def group_disengaged():
        _, _, entities, _ = v2_snapshot(session)
        live = [entities.get(entity_id) for entity_id in MOB_GROUP
                if entities.get(entity_id) is not None]
        return live if live and all(entry.get("state") in ("RETURN", "IDLE")
                                    for entry in live) else None

    disengaged = wait_for(30, group_disengaged)
    smoke_p1.check(disengaged is not None,
                   "mobs still chasing a downed actor never dropped the target")

    _, _, final_entities, final_tick = v2_snapshot(session)
    smoke_p1.check(final_tick > 0 and
                   any(entry.get("kind") == "MOB" for entry in final_entities.values()),
                   f"v2 snapshot stopped serving after death: tick {final_tick}")

    states = sorted({entry.get("state") for entry in (final_entities.values())
                     if entry.get("entityId") in MOB_GROUP})
    print(f"profile=mob-combat telegraph=OK escape_whiff=OK mob_damage={drop} "
          f"guard_confirm=OK counter={counter.get('type')} death_stays_down=OK "
          f"mob_states={','.join(states)}")


def main():
    if len(sys.argv) < 3:
        fail("usage: e2e_p1.py <base_url> <default|dev|mob-combat>")
    smoke_p1.BASE_URL = sys.argv[1].rstrip("/")
    mode = sys.argv[2]
    if mode == "default":
        default_profile()
    elif mode == "dev":
        dev_profile()
    elif mode == "mob-combat":
        mob_combat_profile()
    else:
        fail(f"unknown mode '{mode}' (expected default|dev|mob-combat)")

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
