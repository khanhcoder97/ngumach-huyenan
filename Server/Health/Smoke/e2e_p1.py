#!/usr/bin/env python3
"""Headless end-to-end scenario for the P1 gameplay loop (QOD-15).

Profiles, matching the production gates:

  default — server started WITHOUT the P1 feature flags (production
            profile). Expected blocked output: the quest accept, interact,
            turn-in and equipment POST handlers are not mapped, so the
            requests match the GET read routes instead and return HTTP 405,
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
            live 20 Hz fight over HTTP with conditional waits: walk the
            y=7,5 corridor (outside every group's aggro radius) -> drop onto
            the road beside one group -> read TELEGRAPH -> step out of attack
            range and prove the committed impact whiffs -> stand still and take the
            whole CARPLING hit ->
            guard the next front hit and read COUNTER_CONFIRMED plus the
            counter's own resolution against the mob's snapshot hp -> stay
            until HP reaches 0, then prove the server does not paper over
            death (no auto-heal, fresh cast refused, aggro dropped).

  two-client — two real sessions with distinct characters and the quest,
            interact, turn-in and equipment gates ON. Proves isolation rather
            than inventing contention: both clients claim the same
            PER_CHARACTER package (and the same gather node) with the same
            idempotency keys and both succeed independently; A's turn-in and
            equipment never move B's inventory; B can reuse A's turn-in key
            because idempotency is character-scoped; P00-02 is then asserted
            as BLOCKED with its activation.blocked field so the campaign stop
            has a reason instead of a false PASS.

The Bến Mưa topology fixture is SYNTHETIC_TEST_ONLY, so wall
enforcement is NotEnforced on the server: the wall-crossing move
succeeds and the dev profile records "wall_enforcement=not_enforced". If a
REVIEWED bundle is ever loaded, the same move must return 422
movement_blocked; the script accepts exactly those two outcomes and
fails on anything else.

  alpha-p00 — the private-alpha tutorial chain over real HTTP (QOD-21 Q4):
            every gate the opening loop touches plus P1:AlphaProfile, with
            endurance pools so one actor can stand in the Mãng Cốt ring.
            Walks P00-01 → P00-05 and reads C1-01 through the API only:
            packages, ripples, CARPLING kills, a villager rescue, WATERROOT
            kills, the training-wave dodge, the P00-04 escort to both
            checkpoints with both waves cleared, the quest boss killed through
            the ordinary cast path, the fragment claim, a PAID loot kill (coin inside
            the sourced band, exactly one mutation per death) and the v2 twelve-slot
            equip/unequip surface over HTTP — and then the finale's
            TALK objective, for which P1 has no route, so the profile asserts
            the campaign stops there (P00-05 stays ACTIVE, C1-01 stays LOCKED)
            instead of faking a completion. A second client proves the same
            build keeps progress per character.

  audience-gateoff — the shape issue #96 reported: P1:CombatV2 and
            P1:MobBehavior ON with P1:CombatDamage OFF, so no mob stat bundle
            exists. No other profile boots it, which is how a MOB audience row
            reached a client as ALIVE/targetable at hp 0. Asserts the row is
            BLOCKED/not targetable/0-0 while the behaviour state still travels,
            the NPC and claimable policies are untouched, the actor's own hp is
            still real, and the cast the route still accepts resolves into no
            event naming that mob.

Usage: e2e_p1.py <base_url> <default|dev|mob-combat|two-client|alpha-p00|audience-gateoff>
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
    """Move +x in 1.5-WU steps until x >= stop_before_x. Returns (sequence, x).

    How many steps the 20 Hz tick budget allows depends on wall-clock, so a check
    inside this loop would run a different number of times per run and the reported
    total would stop meaning "these checks all ran". Failures are collected and
    asserted once, after the walk.
    """
    sequence = start_sequence
    failures = []
    x = world_x(session_id)
    while x < stop_before_x:
        sequence += 1
        time.sleep(STEP_SECONDS)
        status, _, body = smoke_p1.call(
            "POST", "/p1/move",
            smoke_p1.move_envelope(sequence, 1, 0, character_id=character_id),
            {"X-Session-ID": session_id})
        if status != 200:
            failures.append((sequence, status, str(body)[:120]))
        x = ((body.get("result") or {}).get("self") or {}).get("x", x)
    smoke_p1.check(not failures, f"walk_east to {stop_before_x} had failing moves: {failures}")
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
        # The body is irrelevant while the gate is off: the POST falls through
        # to the GET /p1/inventory/{sessionId} template and answers 405.
        ("/p1/inventory/equip", "inventory_equip"),
        ("/p1/inventory/unequip", "inventory_unequip"),
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

    # Equipment (dev profile enables P1:Equipment): the P00-01 chest is a real
    # catalogue reward, so equip/unequip runs over the wire on it.
    chest = (inventory.get("items") or [{}])[0]
    revision = inventory.get("inventoryRevision")
    smoke_p1.check(chest.get("location") == "BAG",
                   f"reward location {chest.get('location')}")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/equip",
        smoke_p1.equip_envelope(chest.get("instanceId"), revision,
                                character_id=character_id,
                                request_id="32" * 16, idempotency_key="33" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"equip returned {status}: {body}")
    equipped = body.get("result") or {}
    equipped_item = next(
        (item for item in equipped.get("items") or []
         if item.get("instanceId") == chest.get("instanceId")), {})
    smoke_p1.check(
        equipped_item.get("location") == "EQUIPPED" and
        equipped_item.get("slot") == "CHEST" and
        equipped_item.get("durability") == 100,
        f"equipped item {equipped_item} — durability must be the catalog's 100, not "
        f"the 0 an unspecified grant used to store (Q5 audit)")
    smoke_p1.check(equipped.get("inventoryRevision") == revision + 1,
                   f"equip revision {equipped.get('inventoryRevision')}")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/equip",
        smoke_p1.equip_envelope(chest.get("instanceId"), revision,
                                character_id=character_id,
                                request_id="36" * 16, idempotency_key="33" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"equip replay returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("inventoryRevision") == revision + 1,
                   "equip replay must not move the item again")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/unequip",
        smoke_p1.unequip_envelope("CHEST", revision + 1,
                                  character_id=character_id,
                                  request_id="37" * 16, idempotency_key="38" * 16),
        {"X-Session-ID": session})
    smoke_p1.check(status == 200, f"unequip returned {status}: {body}")
    unequipped = body.get("result") or {}
    unequipped_item = next(
        (item for item in unequipped.get("items") or []
         if item.get("instanceId") == chest.get("instanceId")), {})
    smoke_p1.check(
        unequipped_item.get("location") == "BAG" and "slot" not in unequipped_item,
        f"unequipped item {unequipped_item}")
    smoke_p1.check(unequipped.get("inventoryRevision") == revision + 2,
                   f"unequip revision {unequipped.get('inventoryRevision')}")

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
APPROACH_Y = 7.5
ESCAPE_X = 91.5
CARPLING_DAMAGE = 10
CARPLING_MAX_HP = 192
AGGRO_STATES = ("AGGRO", "CHASE", "TELEGRAPH", "ATTACK", "RECOVER")
# The mob cycle as the frozen WorldSnapshotV2 schema enumerates it.
MOB_LIFECYCLE_STATES = frozenset({
    "IDLE", "AGGRO", "CHASE", "TELEGRAPH", "ATTACK", "RECOVER", "RETURN", "DEAD",
})


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


def walk_to(session_id, character_id, sequence, target_x, target_y,
            axes=("y", "x")):
    """Walk 1,5-WU steps to a grid-aligned target, one axis at a time (the
    server clamps every step to MaxStepDistanceWu). The axis order matters: the
    scenario needs to clear the mob line in y before closing in x, because
    every group stands on y=0 and aggro is a radius, not a lane.
    Returns (sequence, x, y)."""
    _, self_state, _, _ = v2_snapshot(session_id)
    x = self_state.get("x", 0.0)
    y = self_state.get("y", 0.0)
    for axis in axes:
        target = target_x if axis == "x" else target_y
        step_failures = []
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
            if status != 200:
                # One check per axis, after the walk: the number of steps depends on
                # the tick budget, so a check per step would drift the total.
                step_failures.append((axis, sequence, status, str(body)[:120]))
            moved = ((body.get("result") or {}).get("self") or {})
            x = moved.get("x", x)
            y = moved.get("y", y)
        else:
            fail(f"walk along {axis} never reached {target} (stopped at {current})")
        smoke_p1.check(
            not step_failures, f"walk along {axis} had failing moves: {step_failures}")
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
    # Lane first, then the road: every group on this map stands on y=0, so a
    # corridor at y=7,5 (above the 6 WU aggro radius) is outside all of them
    # regardless of x. Approaching along the road itself does not work — the
    # first CI run of this profile proved that by engaging two groups at once
    # while passing x=80 and x=84.
    sequence, x, y = walk_to(session, character_id, sequence, APPROACH_X, APPROACH_Y)
    smoke_p1.check(abs(x - APPROACH_X) < 1e-6 and abs(y - APPROACH_Y) < 1e-6,
                   f"approach stopped at {x},{y}")
    _, self_state, entities, _ = v2_snapshot(session)
    lane_engaged = sorted(entry.get("entityId") for entry in entities.values()
                          if entry.get("kind") == "MOB" and entry.get("state") in AGGRO_STATES)
    smoke_p1.check(not lane_engaged,
                   f"something engaged from the {APPROACH_Y} WU lane: {lane_engaged}")
    smoke_p1.check(self_state.get("hp") == full_hp,
                   f"the lane was not safe: hp {self_state.get('hp')} of {full_hp}")

    def telegraphed_mob():
        _, _, entities, _ = v2_snapshot(session)
        return next((entry for entry in entities.values()
                     if entry.get("kind") == "MOB" and entry.get("state") == "TELEGRAPH"),
                    None)

    def engaged_mobs():
        _, _, entities, _ = v2_snapshot(session)
        return sorted(entry.get("entityId") for entry in entities.values()
                      if entry.get("kind") == "MOB" and entry.get("state") in AGGRO_STATES)

    def group_engaged():
        engaged = engaged_mobs()
        return engaged if engaged and set(engaged) <= set(MOB_GROUP) else None

    # Drop onto the road beside the target group. The escort group four WU back
    # stays out: at x=87 it is 7 WU away, past its own radius.
    sequence, x, y = walk_to(session, character_id, sequence, APPROACH_X, 0.0)
    engaged = wait_for(10, group_engaged)
    smoke_p1.check(engaged is not None,
                   f"descending onto the road did not engage exactly the target group: "
                   f"{engaged_mobs()}")
    _, landed, _, _ = v2_snapshot(session)
    smoke_p1.check(landed.get("hp") == full_hp,
                   f"mob damage landed during the descent: {landed.get('hp')}")

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
    cast_outcomes = []
    for attempt in range(8):
        _, alive_check, _, _ = v2_snapshot(session)
        if alive_check.get("hp", 0) <= 0:
            break
        telegraph = wait_for(15, telegraphed_mob)
        if telegraph is None:
            continue
        # The read window is 0,45 s = nine ticks and the guard covers the eight
        # ticks after the cast, so the cast has to land a couple of ticks *into*
        # the telegraph: casting the instant it is seen puts the impact on the
        # window's exclusive end and the hit walks straight through unreduced.
        time.sleep(0.15)
        sequence += 1
        cast_key = f"{0xc0 + attempt:032x}"
        cast_request = f"{0xd0 + attempt:032x}"
        status, _, body = smoke_p1.call(
            "POST", "/p1/v2/combat",
            smoke_p1.combat_v2_envelope(
                "SKILL", sequence, skill_id="SK-MK-01", character_id=character_id,
                request_id=cast_request, idempotency_key=cast_key, aim_x=-1),
            {"X-Session-ID": session})
        # Recorded, not asserted here: the number of attempts depends on when a
        # mob happens to swing, so a check inside this loop would make the
        # profile's total move from run to run.
        cast_outcomes.append((attempt, status, body))
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
    smoke_p1.check(
        all(outcome[1] in (200, 409) for outcome in cast_outcomes),
        f"guard casts returned unexpected statuses: "
        f"{[outcome[1] for outcome in cast_outcomes]}")
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

    counter_impact = counter.get("type") == "IMPACT"
    counter_damage = (counter.get("result") or {}).get("hpDamage", 0) if counter_impact else 0
    # One claim whichever way the roll fell, so the profile's total cannot move
    # with it (a counter misses legitimately — it shares the DEC-022 hit channel
    # the self-check pins). A hit must match the mob's snapshot HP; a miss must
    # leave it untouched.
    mob = (wait_for(3, lambda: mob_in_snapshot(counter_source)) if counter_impact
           else mob_in_snapshot(counter_source))
    smoke_p1.check(
        mob is not None and mob.get("maxHp") == CARPLING_MAX_HP and
        (mob.get("hp") == CARPLING_MAX_HP - counter_damage if counter_impact
         else mob.get("hp") == CARPLING_MAX_HP),
        f"counter {counter.get('type')} damage {counter_damage} vs snapshot hp "
        f"{None if mob is None else mob.get('hp')}")
    print(f"profile=mob-combat counter={counter.get('type')} "
          f"counter_damage={counter_damage} on {counter_source}")

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


def two_client_profile():
    """Q-G: two real sessions, two real characters, one shared server."""
    character_a = "CHR_E2E_TWO_A"
    character_b = "CHR_E2E_TWO_B"

    # prepare_ready_actor uses fixed request/idempotency keys. Running it for a
    # second character is itself a proof that idempotency is character-scoped:
    # a global ledger would replay or conflict here.
    session_a, sequence_a = prepare_ready_actor(character_a)
    session_b, sequence_b = prepare_ready_actor(character_b)
    smoke_p1.check(session_a != session_b, "the two clients share a session")

    sequence_a, _ = walk_east(session_a, character_a, sequence_a, 47.5)
    sequence_b, _ = walk_east(session_b, character_b, sequence_b, 47.5)

    # The same package, the same keys, two clients, one barrier. The package is
    # PER_CHARACTER, so both must succeed independently; this is isolation, not
    # a claim that the shared world lets one client steal the other's claim.
    package_barrier = threading.Barrier(2)
    package_responses = [None, None]

    def claim_package(index, session, character):
        package_barrier.wait(timeout=10)
        package_responses[index] = smoke_p1.call(
            "POST", "/p1/world/interact",
            smoke_p1.interact_envelope(
                "ENT_MAN_BM_OBJ_BM_PACKAGE_03", character_id=character,
                request_id="10" * 16, idempotency_key="11" * 16),
            {"X-Session-ID": session})

    package_threads = [
        threading.Thread(target=claim_package, args=(0, session_a, character_a)),
        threading.Thread(target=claim_package, args=(1, session_b, character_b)),
    ]
    for thread in package_threads:
        thread.start()
    for thread in package_threads:
        thread.join()

    for label, response in zip(("A", "B"), package_responses):
        smoke_p1.check(response is not None, f"client {label} produced no claim response")
        status, _, body = response
        smoke_p1.check(status == 200, f"client {label} claim returned {status}: {body}")
        result = body.get("result") or {}
        smoke_p1.check(result.get("targetState") == "AVAILABLE",
                       f"client {label} claim state {result.get('targetState')}")
        update = (result.get("questUpdates") or [{}])[0]
        smoke_p1.check(update.get("state") == "READY_TO_TURN_IN",
                       f"client {label} quest state {update.get('state')}")
        smoke_p1.check(
            update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 3},
            f"client {label} counters {update.get('objectiveCounters')}")

    # A turns in first. Nothing of A's reward may appear on B, whose quest is
    # still READY_TO_TURN_IN and whose inventory is still empty.
    sequence_a, _ = walk_east(session_a, character_a, sequence_a, TURN_IN_NPC_X)
    sequence_b, _ = walk_east(session_b, character_b, sequence_b, TURN_IN_NPC_X)

    turn_key = "13" * 16
    turn_request = "12" * 16
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_a,
                                 request_id=turn_request, idempotency_key=turn_key),
        {"X-Session-ID": session_a})
    smoke_p1.check(status == 200, f"client A turn-in returned {status}: {body}")
    smoke_p1.check(
        ((body.get("result") or {}).get("questState") or {}).get("state") == "COMPLETED",
        "client A turn-in did not complete")

    status, _, body = smoke_p1.call("GET", f"/p1/quests/{session_b}")
    smoke_p1.check(status == 200, f"client B quest read returned {status}: {body}")
    b_quest = next((state for state in body.get("result") or []
                    if state.get("questId") == "P00-01"), {})
    smoke_p1.check(b_quest.get("state") == "READY_TO_TURN_IN",
                   f"client B quest state changed to {b_quest.get('state')}")

    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session_b}")
    smoke_p1.check(status == 200, f"client B inventory read returned {status}: {body}")
    b_before = body.get("result") or {}
    smoke_p1.check(
        b_before.get("inventoryRevision") == 0 and not b_before.get("items"),
        f"client A's turn-in leaked into B: {b_before}")

    # B reuses A's key. Turn-in idempotency is scoped to the character, so this
    # is a fresh turn-in for B, not a replay of A's receipt.
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                                 character_id=character_b,
                                 request_id=turn_request, idempotency_key=turn_key),
        {"X-Session-ID": session_b})
    smoke_p1.check(status == 200,
                   f"client B turn-in with A's key returned {status}: {body}")
    b_rewards = (body.get("result") or {}).get("rewards") or {}
    smoke_p1.check(
        (b_rewards.get("items") or [{}])[0].get("templateId") == "EQ-MK-CHEST-T1-R-COMMON",
        f"client B reward {b_rewards.get('items')}")

    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session_a}")
    smoke_p1.check(status == 200, f"client A inventory read returned {status}: {body}")
    a_inventory = body.get("result") or {}
    smoke_p1.check(
        a_inventory.get("inventoryRevision") == 1 and
        len(a_inventory.get("items") or []) == 1,
        f"client A inventory changed when B turned in: {a_inventory}")

    a_chest = (a_inventory.get("items") or [{}])[0]
    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/equip",
        smoke_p1.equip_envelope(a_chest.get("instanceId"), 1,
                                character_id=character_a,
                                request_id="2d" * 16, idempotency_key="2e" * 16),
        {"X-Session-ID": session_a})
    smoke_p1.check(status == 200, f"client A equip returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("inventoryRevision") == 2,
                   "client A equip did not advance exactly one revision")

    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session_b}")
    smoke_p1.check(status == 200, f"client B inventory read returned {status}: {body}")
    b_after_equip = body.get("result") or {}
    smoke_p1.check(
        b_after_equip.get("inventoryRevision") == 1 and
        (b_after_equip.get("items") or [{}])[0].get("location") == "BAG",
        f"client A's equip leaked into B: {b_after_equip}")

    b_chest = (b_after_equip.get("items") or [{}])[0]
    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/equip",
        smoke_p1.equip_envelope(b_chest.get("instanceId"), 1,
                                character_id=character_b,
                                request_id="2f" * 16, idempotency_key="30" * 16),
        {"X-Session-ID": session_b})
    smoke_p1.check(status == 200, f"client B equip returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("inventoryRevision") == 2,
                   "client B equip did not advance exactly one revision")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/unequip",
        smoke_p1.unequip_envelope("CHEST", 2, character_id=character_a,
                                  request_id="31" * 16, idempotency_key="32" * 16),
        {"X-Session-ID": session_a})
    smoke_p1.check(status == 200, f"client A unequip returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("inventoryRevision") == 3,
                   "client A unequip did not advance exactly one revision")

    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session_b}")
    smoke_p1.check(status == 200, f"client B inventory read returned {status}: {body}")
    smoke_p1.check((body.get("result") or {}).get("inventoryRevision") == 2,
                   "client A's unequip leaked into B")

    # The campaign has to stop with a reason, not pass. A completed P00-01, so
    # the next quest's prerequisite is met; the loader still keeps P00-02
    # BLOCKED on its source gap.
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/accept",
        smoke_p1.quest_accept_envelope(
            "P00-02", "NPC_TA_VAN_KHANH", character_id=character_a,
            request_id="33" * 16, idempotency_key="34" * 16),
        {"X-Session-ID": session_a})
    smoke_p1.check(status == 422, f"blocked P00-02 accept returned {status}: {body}")
    accept_error = body.get("error") or {}
    smoke_p1.check(accept_error.get("code") == "prerequisite_not_met",
                   f"blocked P00-02 error {accept_error.get('code')}")
    blocked_fields = [field for field in accept_error.get("fieldErrors") or []
                      if field.startswith("activation.blocked.")]
    smoke_p1.check(bool(blocked_fields),
                   f"blocked P00-02 fields {accept_error.get('fieldErrors')}")

    # Gather nodes are PER_CHARACTER too: two fresh clients at spawn (x=18)
    # harvest the same node at x=21 with one barrier and the same keys. Both
    # succeed and each sees only its own instance.
    node_clients = []
    for character in ("CHR_E2E_NODE_A", "CHR_E2E_NODE_B"):
        status, _, body = smoke_p1.call(
            "POST", "/p1/sessions", {"characterId": character})
        smoke_p1.check(status == 201, f"node session returned {status}: {body}")
        node_clients.append((body.get("sessionId"), character))

    node_barrier = threading.Barrier(2)
    node_responses = [None, None]

    def gather_node(index):
        node_barrier.wait(timeout=10)
        node_responses[index] = smoke_p1.call(
            "POST", "/p1/world/interact",
            smoke_p1.interact_envelope(
                "ENT_MAN_BM_NODE_BM_ORE_01",
                character_id=node_clients[index][1],
                request_id="29" * 16, idempotency_key="2a" * 16),
            {"X-Session-ID": node_clients[index][0]})

    node_threads = [threading.Thread(target=gather_node, args=(index,))
                    for index in range(2)]
    for thread in node_threads:
        thread.start()
    for thread in node_threads:
        thread.join()

    node_instances = []
    for label, response in zip(("A", "B"), node_responses):
        smoke_p1.check(response is not None, f"node client {label} produced no response")
        status, _, body = response
        smoke_p1.check(status == 200, f"node client {label} gather returned {status}: {body}")
        gather_result = body.get("result") or {}
        smoke_p1.check(gather_result.get("outcome") == "gathered",
                       f"node client {label} outcome {gather_result.get('outcome')}")
        smoke_p1.check((gather_result.get("yield") or {}).get("itemId") == "MAT-ORE-01",
                       f"node client {label} yield {gather_result.get('yield')}")

    for session, character in node_clients:
        status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session}")
        smoke_p1.check(status == 200, f"node inventory read returned {status}: {body}")
        snapshot = body.get("result") or {}
        items = snapshot.get("items") or []
        smoke_p1.check(
            snapshot.get("inventoryRevision") == 1 and len(items) == 1 and
            items[0].get("templateId") == "MAT-ORE-01",
            f"node inventory for {character}: {snapshot}")
        node_instances.append(items[0].get("instanceId"))

    smoke_p1.check(node_instances[0] != node_instances[1],
                   f"the two node clients share an instance: {node_instances}")

    print(f"profile=two-client isolation=OK reward=per_character "
          f"equip=per_character node=per_character "
          f"campaign=BLOCKED({blocked_fields[0].split('.')[-1]})")


ALPHA_RIPPLES = (
    ("ALPHA_OBJ_BM_RIPPLE_01", 70.0, 3.0),
    ("ALPHA_OBJ_BM_RIPPLE_02", 86.0, -3.0),
    ("ALPHA_OBJ_BM_RIPPLE_03", 104.0, 3.0),
)
ALPHA_VILLAGERS = (
    ("ALPHA_OBJ_BM_VILLAGER_01", 138.0, 3.0),
    ("ALPHA_OBJ_BM_VILLAGER_02", 146.0, 3.0),
)
ALPHA_WAVE_RECT = (140.0, -2.0, 148.0, 2.0)  # minX, minY, maxX, maxY (design)
ALPHA_FRAGMENT = ("ALPHA_OBJ_BM_FRAGMENT", 178.0, 0.0)
ALPHA_BOSS_ENTITY = "ENT_MAN_BM_SPAWN_BM_05_QUEST"
ALPHA_CARPLING_COIN_MIN = 5   # design.lootAlphaOnly mobLevel..2*mobLevel, CARPLING is level 5
ALPHA_CARPLING_COIN_MAX = 10

# Each candidate carries the spawn record's own atlas position, because a mob the
# audience cannot see yet (more than 40 WU away) has no row to read x/y from — the
# runner has to walk to the group first, then fight what it finds there.
ALPHA_CARPLING_GROUP = (
    ("ENT_MAN_BM_SPAWN_BM_01", 84.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_01_M2", 84.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_01_M3", 84.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_02", 116.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_02_M2", 116.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_02_M3", 116.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_02_M4", 116.0, 0.0),
)
ALPHA_WATERROOT_GROUP = (
    ("ENT_MAN_BM_SPAWN_BM_03", 143.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_03_M2", 143.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_03_M3", 143.0, 0.0),
    ("ENT_MAN_BM_SPAWN_BM_04_M2", 160.0, 0.0),
)
ALPHA_WAVE_A = (
    ("ENT_MAN_BM_WAVE_BM_ESCORT_A", 80.0, 0.0),
    ("ENT_MAN_BM_WAVE_BM_ESCORT_A_M2", 80.0, 0.0),
    ("ENT_MAN_BM_WAVE_BM_ESCORT_A_M3", 80.0, 0.0),
)
ALPHA_WAVE_B = (
    ("ENT_MAN_BM_WAVE_BM_ESCORT_B", 120.0, 0.0),
    ("ENT_MAN_BM_WAVE_BM_ESCORT_B_M2", 120.0, 0.0),
    ("ENT_MAN_BM_WAVE_BM_ESCORT_B_M3", 120.0, 0.0),
)
ALPHA_PACKAGES = (
    ("ENT_MAN_BM_OBJ_BM_PACKAGE_01", 36.0),
    ("ENT_MAN_BM_OBJ_BM_PACKAGE_02", 44.0),
    ("ENT_MAN_BM_OBJ_BM_PACKAGE_03", 52.0),
)

_key_counter = [0]


def alpha_key(tag):
    """32-hex idempotency/request key, unique per run and per tag."""
    _key_counter[0] += 1
    return f"{tag:02x}{_key_counter[0]:030x}"


def alpha_session(character_id):
    status, _, body = smoke_p1.call(
        "POST", "/p1/sessions",
        {"characterId": character_id, "classId": "CLASS_MINH_KIEM"})
    smoke_p1.check(status == 201, f"{character_id} session returned {status}: {body}")
    smoke_p1.check(
        (body.get("result") or {}).get("mapId") == "MAP_BEN_MUA",
        f"{character_id} started on {(body.get('result') or {}).get('mapId')}")
    return body.get("sessionId"), 1


def alpha_quests_read(session_id):
    """Unasserted quest read, for the conditional waits: a probe that polls this
    would otherwise add one check per poll and the reported total would drift
    with timing."""
    status, _, body = smoke_p1.call("GET", f"/p1/quests/{session_id}")
    if status != 200:
        return None
    return {entry.get("questId"): entry for entry in (body.get("result") or [])}


def alpha_quests(session_id):
    quests = alpha_quests_read(session_id)
    smoke_p1.check(quests is not None, f"quest read for {session_id} did not return 200")
    return quests


def alpha_counter(quests, quest_id, objective_id):
    entry = quests.get(quest_id) or {}
    return (entry.get("objectiveCounters") or {}).get(objective_id, -1)


def alpha_step(session_id, character_id, sequence, move_x, move_y, pace):
    sequence += 1
    time.sleep(pace)
    status, _, body = smoke_p1.call(
        "POST", "/p1/move",
        smoke_p1.move_envelope(sequence, move_x, move_y, character_id=character_id),
        {"X-Session-ID": session_id})
    moved = ((body.get("result") or {}).get("self") or {})
    return sequence, status, moved.get("x", 0.0), moved.get("y", 0.0)


def alpha_approach(session_id, character_id, sequence, target_x, target_y,
                   within=3.0, pace=STEP_SECONDS, failures=None):
    """Walk the 1,5-WU grid until the target is inside `within` WU *in a straight
    line* (the P1 interaction range is a euclidean 5 WU, so stopping on a
    per-axis tolerance would let a diagonal stop fail the very next interact).
    Steps are never asserted per step. Without `failures` the caller gets one
    check for this walk; with it, the caller owns a single check for a whole
    phase, because a loop that retries candidates must not grow the profile's
    reported total with the number of attempts the fight happened to need.
    """
    _, self_state, _, _ = v2_snapshot(session_id)
    x = self_state.get("x", 0.0)
    y = self_state.get("y", 0.0)

    def gap():
        return ((x - target_x) ** 2 + (y - target_y) ** 2) ** 0.5

    step_failures = []
    for _ in range(240):
        if gap() <= within:
            break
        if abs(target_x - x) >= abs(target_y - y):
            sequence, status, x, y = alpha_step(
                session_id, character_id, sequence,
                1 if target_x > x else -1, 0, pace)
        else:
            sequence, status, x, y = alpha_step(
                session_id, character_id, sequence,
                0, 1 if target_y > y else -1, pace)
        if status != 200:
            step_failures.append((sequence, status))
    distance = gap()
    if failures is None:
        smoke_p1.check(
            not step_failures,
            f"walk to {target_x},{target_y} had failing moves: {step_failures}")
        smoke_p1.check(
            distance <= within,
            f"walk to {target_x},{target_y} stopped {distance} WU away at {x},{y}")
    else:
        failures.extend(step_failures)
        if distance > within:
            failures.append(f"stop {round(distance, 2)}>{within} at {x},{y}")
    return sequence, x, y


def alpha_accept(session_id, character_id, quest_id, npc_id):
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/accept",
        smoke_p1.quest_accept_envelope(
            quest_id, npc_id, character_id=character_id,
            request_id=alpha_key(0xa1), idempotency_key=alpha_key(0xa2)),
        {"X-Session-ID": session_id})
    return status, body


def alpha_interact(session_id, character_id, target_id):
    status, _, body = smoke_p1.call(
        "POST", "/p1/world/interact",
        smoke_p1.interact_envelope(
            target_id, character_id=character_id,
            request_id=alpha_key(0xb1), idempotency_key=alpha_key(0xb2)),
        {"X-Session-ID": session_id})
    return status, body


def alpha_turnin(session_id, character_id, quest_id, npc_id):
    status, _, body = smoke_p1.call(
        "POST", "/p1/quests/turnin",
        smoke_p1.turnin_envelope(
            quest_id, npc_id, character_id=character_id,
            request_id=alpha_key(0xc1), idempotency_key=alpha_key(0xc2)),
        {"X-Session-ID": session_id})
    return status, body


def alpha_kill(session_id, character_id, sequence, entity_id, pace=0.12):
    """Cast the basic attack at one entity, staying in reach, until the snapshot
    reports that life DEAD. Returns (nextSequence, acceptedCasts, refusedCodes,
    witnessedDeath) — a cast that merely stopped seeing the entity is NOT counted
    as a kill, because the group respawn makes an absent row ambiguous and the
    quest counter must be compared against deaths the run actually observed.
    """
    accepted = 0
    refused = {}
    for _ in range(1200):
        _, self_state, entities, _ = v2_snapshot(session_id)
        target = entities.get(entity_id)
        if target is None or self_state.get("hp", 0) <= 0:
            return sequence, accepted, refused, False
        if target.get("state") == "DEAD":
            return sequence, accepted, refused, True
        me_x = self_state.get("x", 0.0)
        me_y = self_state.get("y", 0.0)
        gap_x = target.get("x", me_x) - me_x
        gap_y = target.get("y", me_y) - me_y
        distance = (gap_x * gap_x + gap_y * gap_y) ** 0.5
        if distance > 2.5:
            # Close in on the longer axis first; the basic attack is a facing
            # cone, so walking past the target is as useless as missing it.
            sequence, _, _, _ = alpha_step(
                session_id, character_id, sequence,
                1 if gap_x >= 0 else -1, 0, STEP_SECONDS)
            continue
        aim_x = round(gap_x / distance, 4) if distance else 1.0
        aim_y = round(gap_y / distance, 4) if distance else 0.0
        sequence += 1
        status, _, body = smoke_p1.call(
            "POST", "/p1/v2/combat",
            smoke_p1.combat_v2_envelope(
                "BASIC_ATTACK", sequence, character_id=character_id,
                target_id=entity_id, aim_x=aim_x, aim_y=aim_y,
                request_id=alpha_key(0xd1), idempotency_key=alpha_key(0xd2)),
            {"X-Session-ID": session_id})
        if status == 200:
            accepted += 1
        else:
            code = (body.get("error") or {}).get("code") or str(status)
            refused[code] = refused.get(code, 0) + 1
        time.sleep(pace)
    return sequence, accepted, refused, False


def alpha_kill_watched(session, character, sequence, pool, wanted, label):
    """Kill until `wanted` deaths are witnessed. Every candidate is approached at
    its spawn record's atlas position first (a mob outside the 40-WU audience has
    no row to read yet), then fought until the snapshot reports that life DEAD.
    Returns (nextSequence, deaths, refusalsByName)."""
    deaths = 0
    attempts = 0
    refused = {}
    walk_failures = []
    while deaths < wanted and attempts < wanted * 4:
        for entity_id, anchor_x, anchor_y in pool:
            if deaths >= wanted:
                break
            attempts += 1
            _, _, entities, _ = v2_snapshot(session)
            if (entities.get(entity_id) or {}).get("state") == "DEAD":
                continue
            sequence, _, _ = alpha_approach(
                session, character, sequence, anchor_x, anchor_y, within=3.0,
                failures=walk_failures)
            sequence, accepted, codes, died = alpha_kill(
                session, character, sequence, entity_id)
            for code, count in codes.items():
                refused[code] = refused.get(code, 0) + count
            if died:
                deaths += 1
    smoke_p1.check(
        deaths >= wanted and not walk_failures,
        f"{label}: witnessed {deaths} of {wanted} deaths (attempts {attempts}, "
        f"refusals {refused}, walks {walk_failures[:4]})")
    return sequence, deaths, refused


def alpha_v2_equip_envelope(instance_id, expected_revision, character_id):
    return {
        "schemaVersion": 2,
        "requestId": alpha_key(0xe1),
        "idempotencyKey": alpha_key(0xe2),
        "sentAtUtc": smoke_p1.sent_at_utc(),
        "characterId": character_id,
        "payload": {"itemInstanceId": instance_id, "expectedRevision": expected_revision},
    }


def alpha_v2_unequip_envelope(slot_id, expected_revision, character_id, key=None):
    return {
        "schemaVersion": 2,
        "requestId": alpha_key(0xe3),
        "idempotencyKey": key or alpha_key(0xe4),
        "sentAtUtc": smoke_p1.sent_at_utc(),
        "characterId": character_id,
        "payload": {"slotId": slot_id, "expectedRevision": expected_revision},
    }


def alpha_inventory(session_id):
    status, _, body = smoke_p1.call("GET", f"/p1/inventory/{session_id}")
    smoke_p1.check(status == 200, f"v1 inventory read returned {status}: {body}")
    return body.get("result") or {}


def alpha_inventory_v2(session_id):
    status, _, body = smoke_p1.call("GET", f"/p1/inventory/v2/{session_id}")
    smoke_p1.check(status == 200, f"v2 inventory read returned {status}: {body}")
    return body.get("result") or {}


def alpha_coin(snapshot):
    return sum(entry.get("amount", 0) for entry in (snapshot.get("currencies") or [])
               if entry.get("currencyId") == "COIN")


def alpha_v2_surface(session, character):
    """The twelve-slot surface exercised over HTTP on a real reward, next to the v1
    read of the same inventory. The dev profile only proves v1 equip and the
    self-check only proves the handler, so this is the route-level proof."""
    v1 = alpha_inventory(session)
    revision = v1.get("inventoryRevision", 0)
    chest = next((item for item in (v1.get("items") or [])
                  if item.get("location") == "BAG"), None)
    smoke_p1.check(chest is not None, f"no BAG item to equip for the v2 leg: {v1}")

    before = alpha_inventory_v2(session)
    smoke_p1.check(
        len(before.get("slots") or []) == 12 and
        before.get("bagSlots") == 100 and
        before.get("slotSpec") == "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT" and
        all(entry.get("item") is None for entry in (before.get("slots") or [])) and
        before.get("inventoryRevision") == revision and
        before.get("unsupported") == [],
        f"v2 read before the equip is not twelve empty slots: "
        f"slots={len(before.get('slots') or [])} bagSlots={before.get('bagSlots')} "
        f"spec={before.get('slotSpec')} rev={before.get('inventoryRevision')}")

    equip_request = alpha_v2_equip_envelope(chest.get("instanceId"), revision, character)
    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/v2/equip", equip_request, {"X-Session-ID": session})
    equipped = body.get("result") or {}
    chest_slot = next((entry for entry in (equipped.get("slots") or [])
                       if entry.get("slotId") == "CHEST"), {})
    smoke_p1.check(
        status == 200 and
        (chest_slot.get("item") or {}).get("instanceId") == chest.get("instanceId") and
        equipped.get("inventoryRevision") == revision + 1,
        f"v2 equip {status}: {(body.get('error') or equipped)}")

    v1_after = alpha_inventory(session)
    smoke_p1.check(
        any(item.get("location") == "EQUIPPED" and item.get("slot") == "CHEST"
            and item.get("instanceId") == chest.get("instanceId")
            for item in (v1_after.get("items") or [])) and
        v1_after.get("inventoryRevision") == revision + 1,
        f"v1 does not see the v2 equip in its own vocabulary: {v1_after}")

    # Same key, same payload: the recorded answer, and no second move.
    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/v2/equip", equip_request, {"X-Session-ID": session})
    smoke_p1.check(
        status == 200 and
        (body.get("result") or {}).get("inventoryRevision") == revision + 1 and
        alpha_inventory(session).get("inventoryRevision") == revision + 1,
        f"v2 equip replay moved the item again: {status} "
        f"{(body.get('result') or {}).get('inventoryRevision')}")

    # Same key, different payload is a conflict, not a second opinion.
    conflicting = alpha_v2_equip_envelope(chest.get("instanceId"), revision + 5, character)
    conflicting["idempotencyKey"] = equip_request["idempotencyKey"]
    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/v2/equip", conflicting, {"X-Session-ID": session})
    smoke_p1.check(
        status == 409 and
        (body.get("error") or {}).get("code") == "idempotency_conflict",
        f"v2 accepted a same-key different-payload equip: {status} "
        f"{(body.get('error') or {})}")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/v2/unequip",
        alpha_v2_unequip_envelope("CHEST", revision + 1, character),
        {"X-Session-ID": session})
    back = body.get("result") or {}
    smoke_p1.check(
        status == 200 and
        all(entry.get("item") is None for entry in (back.get("slots") or [])) and
        any(item.get("instanceId") == chest.get("instanceId")
            for item in (back.get("bag") or [])) and
        back.get("inventoryRevision") == revision + 2,
        f"v2 unequip {status}: {(body.get('error') or back)}")

    status, _, body = smoke_p1.call(
        "POST", "/p1/inventory/v2/unequip",
        alpha_v2_unequip_envelope("ACCESSORY", revision + 2, character),
        {"X-Session-ID": session})
    smoke_p1.check(
        status == 400 and
        (body.get("error") or {}).get("code") == "invalid_payload" and
        "payload.slotId" in ((body.get("error") or {}).get("fieldErrors") or []),
        f"v2 accepted the v1 ACCESSORY token: {status} {(body.get('error') or {})}")


def alpha_p00_profile():
    """QOD-21 Q4: the whole private-alpha opening, over real HTTP, on one actor.

    This is the leg every earlier report marked UNVERIFIED: P00-01 -> P00-05
    needs the whole prerequisite chain to actually run through the API, because
    prerequisite_not_met is enforced and no in-process fixture can stand in for
    it. Progress is read from the authoritative quest read only — never from a
    client-side assumption about what should have counted.
    """
    smoke_p1.check(
        smoke_p1.call("GET", "/health")[0] == 200, "health check failed")

    character = "CHR_E2E_ALPHA_A"
    session, sequence = alpha_session(character)

    quests = alpha_quests(session)
    smoke_p1.check(
        set(quests) == {"P00-01", "P00-02", "P00-03", "P00-04", "P00-05", "C1-01"},
        f"alpha quest surface is {sorted(quests)}")
    smoke_p1.check(
        all(quests[qid].get("state") != "BLOCKED" for qid in
            ("P00-02", "P00-03", "P00-04", "P00-05")),
        f"alpha pack still blocked: {[(qid, quests[qid].get('state')) for qid in ('P00-02', 'P00-03', 'P00-04', 'P00-05')]}")

    # ── P00-01: three packages, then the first real XP receipt ──
    sequence, _, _ = alpha_approach(session, character, sequence, 42.0, 0.0)
    status, body = alpha_accept(session, character, "P00-01", "NPC_LYAN")
    smoke_p1.check(status == 200 and (body.get("result") or {}).get("state") == "ACTIVE",
                   f"accept P00-01 {status}: {(body.get('error') or {})}")

    for index, (entity_id, target_x) in enumerate(ALPHA_PACKAGES, start=1):
        sequence, _, _ = alpha_approach(session, character, sequence, target_x, 0.0)
        status, body = alpha_interact(session, character, entity_id)
        updates = ((body.get("result") or {}).get("questUpdates")) or []
        smoke_p1.check(
            status == 200 and updates and
            updates[0].get("objectiveCounters", {}).get("OBJ_P00_01_PACKAGES") == index,
            f"package {entity_id} {status}: {updates or (body.get('error') or {})}")

    sequence, _, _ = alpha_approach(session, character, sequence, TURN_IN_NPC_X, 0.0)
    status, body = alpha_turnin(session, character, "P00-01", "NPC_TA_VAN_KHANH")
    first_rewards = (body.get("result") or {}).get("rewards") or {}
    smoke_p1.check(
        status == 200 and (body.get("result") or {}).get("questState", {}).get("state")
        == "COMPLETED",
        f"turnin P00-01 {status}: {(body.get('error') or {})}")
    # The alpha XP rule finally resolves over HTTP: with the profile off the
    # shipped resolver answers applied:false, and the self-check's L1 oracle value
    # (43) is server-side only — the frozen turn-in contract carries {xpRule,
    # applied} and no amount, so this asserts the receipt, not a number the wire
    # does not expose.
    smoke_p1.check(
        (first_rewards.get("xp") or {}).get("applied") is True and
        (first_rewards.get("xp") or {}).get("xpRule") == "LEVEL_BAND_BASE",
        f"P00-01 XP receipt {first_rewards.get('xp')}")
    quests = alpha_quests(session)
    smoke_p1.check(quests["P00-02"].get("state") == "AVAILABLE",
                   f"P00-02 after P00-01 is {quests['P00-02'].get('state')}")
    alpha_v2_surface(session, character)

    # ── P00-02: water ripples (overlay records) + four CARPLING kills ──
    status, body = alpha_accept(session, character, "P00-02", "NPC_TA_VAN_KHANH")
    smoke_p1.check(status == 200, f"accept P00-02 {status}: {(body.get('error') or {})}")

    for index, (entity_id, target_x, target_y) in enumerate(ALPHA_RIPPLES, start=1):
        sequence, _, _ = alpha_approach(session, character, sequence, target_x, target_y)
        status, body = alpha_interact(session, character, entity_id)
        updates = ((body.get("result") or {}).get("questUpdates")) or []
        smoke_p1.check(
            status == 200 and updates and
            updates[0].get("objectiveCounters", {}).get("OBJ_P00_02_RIPPLES") == index,
            f"ripple {entity_id} {status}: {updates or (body.get('error') or {})}")

    # Loot ON under the alpha profile means every paid death is one inventory
    # mutation: coin in the sourced mobLevel..2*mobLevel band (CARPLING is level 5,
    # so 5..10 each) plus the recipe item, in the SAME Apply. Four paid deaths must
    # therefore move the inventory revision exactly four times - a double payment
    # shows up as a bigger revision, a missing one as a smaller one.
    loot_before = alpha_inventory(session)
    coin_before = alpha_coin(loot_before)
    revision_before = loot_before.get("inventoryRevision", 0)
    sequence, carpling_kills, _ = alpha_kill_watched(
        session, character, sequence, ALPHA_CARPLING_GROUP, 4, "P00-02 CARPLING")
    loot_after = alpha_inventory(session)
    coin_delta = alpha_coin(loot_after) - coin_before
    revision_delta = loot_after.get("inventoryRevision", 0) - revision_before
    smoke_p1.check(
        4 * ALPHA_CARPLING_COIN_MIN <= coin_delta <= 4 * ALPHA_CARPLING_COIN_MAX and
        revision_delta == 4,
        f"paid loot over HTTP: coin delta {coin_delta} outside "
        f"[{4 * ALPHA_CARPLING_COIN_MIN}, {4 * ALPHA_CARPLING_COIN_MAX}] and revision "
        f"moved {revision_delta} times for 4 kills")
    quests = alpha_quests(session)
    smoke_p1.check(
        alpha_counter(quests, "P00-02", "OBJ_P00_02_CARPLING") >= 4,
        f"CARPLING counter after {carpling_kills} kills is "
        f"{alpha_counter(quests, 'P00-02', 'OBJ_P00_02_CARPLING')}")

    sequence, _, _ = alpha_approach(session, character, sequence, TURN_IN_NPC_X, 0.0)
    status, body = alpha_turnin(session, character, "P00-02", "NPC_TA_VAN_KHANH")
    smoke_p1.check(
        status == 200 and (body.get("result") or {}).get("unlocks") == ["P00-03"],
        f"turnin P00-02 {status}: {(body.get('error') or (body.get('result') or {}))}")

    # ── P00-03: two villagers, three WATERROOT kills, the training-wave dodge ──
    sequence, _, _ = alpha_approach(session, character, sequence, 42.0, 0.0)
    status, body = alpha_accept(session, character, "P00-03", "NPC_LYAN")
    smoke_p1.check(status == 200, f"accept P00-03 {status}: {(body.get('error') or {})}")

    for index, (entity_id, target_x, target_y) in enumerate(ALPHA_VILLAGERS, start=1):
        sequence, _, _ = alpha_approach(session, character, sequence, target_x, target_y)
        status, body = alpha_interact(session, character, entity_id)
        updates = ((body.get("result") or {}).get("questUpdates")) or []
        smoke_p1.check(
            status == 200 and updates and
            updates[0].get("objectiveCounters", {}).get("OBJ_P00_03_VILLAGERS") == index,
            f"villager {entity_id} {status}: {updates or (body.get('error') or {})}")

    sequence, waterroot_kills, _ = alpha_kill_watched(
        session, character, sequence, ALPHA_WATERROOT_GROUP, 3, "P00-03 WATERROOT")

    # The trial cycle only opens while the actor stands inside the sourced rect
    # (140,-2)-(148,2) and credits at the impact tick if they left first: 24 ticks
    # of windup at 20 Hz = 1,2 s, so dip in, get out, and let the tick decide. A
    # hit is not a dodge — only standing outside at the impact frame can credit
    # this, so an accidental hit while clearing the waterroots above cannot fake it.
    min_x, _, max_x, _ = ALPHA_WAVE_RECT
    dip_x = min_x + 2.0
    escape_x = min_x - 6.0
    def wave_trial_credited():
        polled = alpha_quests_read(session) or {}
        return alpha_counter(polled, "P00-03", "OBJ_P00_03_WAVE_TRIAL") >= 1

    attempts = 0
    dodge_walk_failures = []
    while attempts < 6 and not wait_for(0.2, wave_trial_credited):
        attempts += 1
        sequence, _, _ = alpha_approach(session, character, sequence, dip_x, 0.0,
                                       within=1.0, pace=0.15,
                                       failures=dodge_walk_failures)
        sequence, _, _ = alpha_approach(session, character, sequence, escape_x, 0.0,
                                       within=1.0, pace=0.15,
                                       failures=dodge_walk_failures)
        time.sleep(0.7)

    smoke_p1.check(
        wait_for(20.0, wave_trial_credited) is not None and not dodge_walk_failures,
        f"the training-wave dodge never credited OBJ_P00_03_WAVE_TRIAL over HTTP "
        f"after {attempts} in/out attempts (walks {dodge_walk_failures[:4]})")

    # P00-03 hands in to Ly An, not to Ta Van Khanh: the walk back is part of
    # the quest, and the server gates it by distance.
    sequence, _, _ = alpha_approach(session, character, sequence, 42.0, 0.0)
    status, body = alpha_turnin(session, character, "P00-03", "NPC_LYAN")
    smoke_p1.check(
        status == 200 and (body.get("result") or {}).get("questState", {}).get("state")
        == "COMPLETED",
        f"turnin P00-03 {status}: {(body.get('error') or {})}")

    # ── P00-04: walk the escort to both checkpoints and clear each wave ──
    # Ta Van Khanh gives the quest, Ly An is the actor being escorted, so the
    # leg starts by accepting at x=64 and then walks back to the NPC's own
    # station at x=42 before accompanying it east.
    sequence, _, _ = alpha_approach(session, character, sequence, TURN_IN_NPC_X, 0.0)
    status, body = alpha_accept(session, character, "P00-04", "NPC_TA_VAN_KHANH")
    smoke_p1.check(status == 200, f"accept P00-04 {status}: {(body.get('error') or {})}")
    sequence, _, _ = alpha_approach(session, character, sequence, 42.0, 0.0)

    def wave_alive(expected):
        _, _, entities, _ = v2_snapshot(session)
        alive = [entry[0] for entry in expected
                 if (entities.get(entry[0]) or {}).get("state") not in (None, "DEAD")]
        return alive if len(alive) == len(expected) else None

    def accompany_until(limit_x, start_x):
        """Pace east at the NPC's 3 wu/s and report the first tick on which the
        checkpoint wave is up. Steps are not asserted per step (the count depends
        on wall-clock), so one check after the walk carries the whole leg.
        """
        nonlocal sequence
        walked = 0
        x = start_x
        while walked < 45 and x < limit_x:
            sequence, _, x, _ = alpha_step(session, character, sequence, 1, 0, 0.5)
            walked += 1
        return walked, x

    # Wave A activates when the escort reaches its x=80 checkpoint.
    walked_a, x_after_a = accompany_until(82.0, 42.0)
    alive_a = wait_for(60.0, lambda: wave_alive(ALPHA_WAVE_A))
    smoke_p1.check(
        alive_a is not None,
        f"the P00-04 escort never activated wave A (walked {walked_a} paced steps "
        f"to x={x_after_a})")
    sequence, wave_a_deaths, _ = alpha_kill_watched(
        session, character, sequence, ALPHA_WAVE_A, 3, "P00-04 wave A")

    _, self_state, _, _ = v2_snapshot(session)
    walked_b, x_after_b = accompany_until(122.0, self_state.get("x", 82.0))
    alive_b = wait_for(75.0, lambda: wave_alive(ALPHA_WAVE_B))
    smoke_p1.check(
        alive_b is not None,
        f"the P00-04 escort never activated wave B (walked {walked_b} paced steps "
        f"to x={x_after_b})")
    sequence, wave_b_deaths, _ = alpha_kill_watched(
        session, character, sequence, ALPHA_WAVE_B, 3, "P00-04 wave B")

    quests = alpha_quests(session)
    smoke_p1.check(
        alpha_counter(quests, "P00-04", "OBJ_P00_04_WAVE_A") == 3 and
        alpha_counter(quests, "P00-04", "OBJ_P00_04_WAVE_B") == 3,
        f"P00-04 counters {quests.get('P00-04', {}).get('objectiveCounters')}")
    sequence, _, _ = alpha_approach(session, character, sequence, TURN_IN_NPC_X, 0.0)
    status, body = alpha_turnin(session, character, "P00-04", "NPC_TA_VAN_KHANH")
    smoke_p1.check(
        status == 200 and (body.get("result") or {}).get("unlocks") == ["P00-05"],
        f"turnin P00-04 {status}: {(body.get('error') or {})}")

    # ── P00-05: the Mãng Cốt encounter, fought over HTTP ──
    sequence, _, _ = alpha_approach(session, character, sequence, TURN_IN_NPC_X, 0.0)
    status, body = alpha_accept(session, character, "P00-05", "NPC_TA_VAN_KHANH")
    smoke_p1.check(status == 200, f"accept P00-05 {status}: {(body.get('error') or {})}")

    # Registration is physical: the owner has to stand inside the sourced ring
    # (circle (178,0) r 11) before any cast reaches the quest boss.
    sequence, _, _ = alpha_approach(session, character, sequence, 178.0, 0.0, within=3.0)
    # Standing in the ring is what registers the encounter for this owner, and the
    # owner-facing audience row is the promise that makes the fight reachable: the
    # quest boss reads ALIVE and targetable here (and only for this session) before
    # any cast lands.
    _, _, boss_rows, _ = v2_snapshot(session)
    boss_row = boss_rows.get(ALPHA_BOSS_ENTITY) or {}
    smoke_p1.check(
        boss_row.get("targetable") is True and boss_row.get("healthState") == "ALIVE",
        f"the quest boss row was not owner-targetable before the fight: "
        f"targetable={boss_row.get('targetable')} healthState={boss_row.get('healthState')}")
    sequence, accepted, refused, boss_died = alpha_kill(
        session, character, sequence, ALPHA_BOSS_ENTITY)
    smoke_p1.check(
        accepted > 20 and boss_died,
        f"the quest boss never died for this owner: {accepted} casts accepted, "
        f"witnessed death {boss_died}, refusals {refused}")
    _, _, dead_rows, _ = v2_snapshot(session)
    dead_row = dead_rows.get(ALPHA_BOSS_ENTITY) or {}
    smoke_p1.check(
        dead_row.get("targetable") is False and
        dead_row.get("healthState") == "DEAD",
        f"the quest boss stayed targetable after its death: "
        f"targetable={dead_row.get('targetable')} healthState={dead_row.get('healthState')}")
    quests = alpha_quests(session)
    smoke_p1.check(
        alpha_counter(quests, "P00-05", "OBJ_P00_05_BOSS") == 1,
        f"BOSS counter after the kill is "
        f"{alpha_counter(quests, 'P00-05', 'OBJ_P00_05_BOSS')}")

    entity_id, target_x, target_y = ALPHA_FRAGMENT
    sequence, _, _ = alpha_approach(session, character, sequence, target_x, target_y,
                                    within=3.0)
    status, body = alpha_interact(session, character, entity_id)
    smoke_p1.check(
        status == 200 and ((body.get("result") or {}).get("questUpdates") or [{}])[0]
        .get("objectiveCounters", {}).get("OBJ_P00_05_FRAGMENT") == 1,
        f"fragment interact {status}: {(body.get('result') or {}).get('questUpdates') or (body.get('error') or {})}")

    # The finale's last objective is a TALK, and P1 has no dialogue route: this
    # is where the HTTP tutorial genuinely stops. Recorded as the named reason
    # it is, rather than being skipped or passed by fixture.
    status, body = alpha_turnin(session, character, "P00-05", "NPC_TA_VAN_KHANH")
    quests = alpha_quests(session)
    smoke_p1.check(
        status != 200 and
        alpha_counter(quests, "P00-05", "OBJ_P00_05_CLASS_CONFIRM") == 0 and
        quests["P00-05"].get("state") == "ACTIVE",
        f"P00-05 stopped where expected? turnin {status}: {(body.get('error') or {})} "
        f"state {quests['P00-05'].get('state')}")
    smoke_p1.check(
        quests["C1-01"].get("state") == "LOCKED",
        f"C1-01 before P00-05 completes is {quests['C1-01'].get('state')}")

    # ── a second client, so "per character" is proven on the same build ──
    second = "CHR_E2E_ALPHA_B"
    session_b, sequence_b = alpha_session(second)
    sequence_b, _, _ = alpha_approach(session_b, second, sequence_b, 42.0, 0.0)
    status, body = alpha_accept(session_b, second, "P00-01", "NPC_LYAN")
    smoke_p1.check(status == 200, f"B accept P00-01 {status}: {(body.get('error') or {})}")
    sequence_b, _, _ = alpha_approach(session_b, second, sequence_b, 36.0, 0.0)
    status, body = alpha_interact(session_b, second, "ENT_MAN_BM_OBJ_BM_PACKAGE_01")
    smoke_p1.check(
        status == 200 and ((body.get("result") or {}).get("questUpdates") or [{}])[0]
        .get("objectiveCounters", {}).get("OBJ_P00_01_PACKAGES") == 1,
        f"B package claim {status}: {(body.get('error') or {})}")
    quests_b = alpha_quests(session_b)
    smoke_p1.check(
        alpha_counter(quests_b, "P00-02", "OBJ_P00_02_RIPPLES") == 0 and
        alpha_counter(quests_b, "P00-02", "OBJ_P00_02_CARPLING") == 0,
        f"B inherited A's P00-02 progress: {quests_b.get('P00-02')}")
    # B is one quest deep, so the graph stops it exactly the way it stops
    # everyone else: P00-02 stays LOCKED until P00-01 is handed in.
    smoke_p1.check(
        quests_b["P00-02"].get("state") == "LOCKED" and
        quests["P00-05"].get("state") == "ACTIVE",
        f"B P00-02 state {quests_b.get('P00-02', {}).get('state')}, "
        f"A P00-05 state {quests.get('P00-05', {}).get('state')}")

    print(
        "profile=alpha-p00 chain=P00-01..P00-05 "
        f"boss=KILLED fragment=OK wave_trial=OK escort=A+B loot=PAID v2_inventory=OK "
        f"talk=NO_HTTP_ROUTE c1_01=LOCKED second_client=ISOLATED")


def audience_gateoff_profile():
    """The #96 report shape over real HTTP: P1:CombatV2 and P1:MobBehavior ON
    with P1:CombatDamage OFF.

    No other profile boots that combination — `default`, `dev` and `two-client`
    never enable the v2 route, while `mob-combat` and `alpha-p00` both enable the
    damage gate — so the audience policy for a MOB whose stats cannot be resolved
    was only ever covered in-process, and a row that told a client
    `ALIVE`/`targetable:true` at `hp: 0` reached a real consumer undetected.
    Asserted here: the health claim is `BLOCKED` and not targetable, the
    behaviour state still travels because it is real, the other kinds keep their
    own policy, the actor's own numbers stay real, and the cast the route still
    accepts at such a mob never resolves into an event naming it.
    """
    character = "CHR_QOD21_AUDIENCE_GATEOFF"
    session, sequence = alpha_session(character)

    status, self_state, entities, _ = v2_snapshot(session)
    smoke_p1.check(
        status == 200,
        f"v2 world read with the damage gate off returned {status}")
    smoke_p1.check(
        self_state.get("maxHp", 0) >= 1 and
        self_state.get("hp") == self_state.get("maxHp"),
        f"the actor's own numbers stopped being real: {self_state}")

    npc = entities.get("ENT_MAN_BM_NPC_LYAN") or {}
    smoke_p1.check(
        npc.get("kind") == "NPC" and
        npc.get("healthState") == "INVULNERABLE" and
        npc.get("targetable") is False and
        npc.get("hp") == 0,
        f"the NPC audience policy changed: {npc}")

    node = entities.get("ENT_MAN_BM_NODE_BM_ORE_01") or {}
    smoke_p1.check(
        node.get("kind") == "GATHER_NODE" and
        node.get("availability") == "AVAILABLE",
        f"the claimable availability policy changed: {node}")

    # The spawn audience has no mob inside 40 WU, so walk east to the first
    # CARPLING group (x=84 in the shipped world-entity records).
    failures = []
    sequence, _, _ = alpha_approach(
        session, character, sequence, 80.0, 0.0, within=6.0, failures=failures)
    smoke_p1.check(not failures, f"walk to the CARPLING group failed: {failures}")

    status, _, entities, _ = v2_snapshot(session)
    mobs = {entity_id: row
            for entity_id, row in entities.items()
            if row.get("kind") == "MOB"}
    smoke_p1.check(
        status == 200 and len(mobs) >= 1 and
        any(entity_id in MOB_GROUP for entity_id in mobs),
        f"the CARPLING group never reached the audience near x=80 "
        f"(status={status} mobs={sorted(mobs)[:3]})")

    unhealthy = [(entity_id, row.get("healthState"), row.get("targetable"),
                  row.get("hp"), row.get("maxHp"))
                 for entity_id, row in mobs.items()
                 if row.get("healthState") != "BLOCKED" or
                 row.get("targetable") is not False or
                 row.get("hp") != 0 or row.get("maxHp") != 0]
    smoke_p1.check(
        not unhealthy,
        f"damage-gate-off mob rows still advertise a fightable target: "
        f"{unhealthy[:3]}")

    misbehaving = [(entity_id, row.get("state"))
                   for entity_id, row in mobs.items()
                   if row.get("state") not in MOB_LIFECYCLE_STATES]
    smoke_p1.check(
        not misbehaving,
        f"mob behaviour state stopped travelling: {misbehaving[:3]}")

    # A cast is still *accepted* by the route — acceptance never looks at the
    # target's stats — so the proof the client needs is that it resolves nothing:
    # no event on the session stream ever names this mob. Standing inside the
    # basic attack's 4,4-WU cone makes that a real statement rather than a
    # range artefact, and the mob-combat profile is its mirror image: with
    # P1:CombatDamage ON, the same swing produces IMPACT/MISS events naming the
    # very same entity ids.
    entity_id = sorted(mobs)[0]
    failures = []
    close = mobs[entity_id]
    sequence, _, _ = alpha_approach(
        session, character, sequence, close.get("x", 0.0), close.get("y", 0.0),
        within=2.5, failures=failures)
    smoke_p1.check(not failures, f"close approach to {entity_id} failed: {failures}")

    _, self_state, entities, _ = v2_snapshot(session)
    target = entities.get(entity_id) or {}
    gap_x = target.get("x", 0.0) - self_state.get("x", 0.0)
    gap_y = target.get("y", 0.0) - self_state.get("y", 0.0)
    distance = max((gap_x * gap_x + gap_y * gap_y) ** 0.5, 1e-9)
    sequence += 1
    status, _, body = smoke_p1.call(
        "POST", "/p1/v2/combat",
        smoke_p1.combat_v2_envelope(
            "BASIC_ATTACK", sequence, character_id=character,
            target_id=entity_id, aim_x=round(gap_x / distance, 4),
            aim_y=round(gap_y / distance, 4),
            request_id=alpha_key(0xd1), idempotency_key=alpha_key(0xd2)),
        {"X-Session-ID": session})
    smoke_p1.check(
        status == 200 and distance <= 4.4,
        f"cast at a blocked mob: status={status} distance={round(distance, 2)} "
        f"error={(body.get('error') or {})}")

    # Past the windup and the impact tick, then one read of the whole stream.
    time.sleep(1.5)
    status, events, _ = v2_events(session, 0)
    naming = [(event.get("type"), event.get("targetId"))
              for event in events if event.get("targetId") == entity_id]
    smoke_p1.check(
        status == 200 and not naming,
        f"the engine resolved something for a mob it cannot score: {naming[:3]}")

    _, _, entities, _ = v2_snapshot(session)
    row = entities.get(entity_id) or {}
    smoke_p1.check(
        row.get("healthState") == "BLOCKED" and row.get("hp") == 0,
        f"the accepted cast changed the blocked mob row: {row}")

    print(
        f"profile=audience-gateoff mobs={len(mobs)} health=BLOCKED "
        f"targetable=false hp=0/0 behaviour_states="
        f"{sorted({value.get('state') for value in mobs.values()})} "
        f"cast=accepted_but_unresolved npc=INVULNERABLE node=AVAILABLE")


def main():
    if len(sys.argv) < 3:
        fail("usage: e2e_p1.py <base_url> "
             "<default|dev|mob-combat|two-client|alpha-p00|audience-gateoff>")
    smoke_p1.BASE_URL = sys.argv[1].rstrip("/")
    mode = sys.argv[2]
    if mode == "default":
        default_profile()
    elif mode == "dev":
        dev_profile()
    elif mode == "mob-combat":
        mob_combat_profile()
    elif mode == "two-client":
        two_client_profile()
    elif mode == "alpha-p00":
        alpha_p00_profile()
    elif mode == "audience-gateoff":
        audience_gateoff_profile()
    else:
        fail(f"unknown mode '{mode}' "
             "(expected default|dev|mob-combat|two-client|alpha-p00|"
             "audience-gateoff)")

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
