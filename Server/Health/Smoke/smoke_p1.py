#!/usr/bin/env python3
"""Runtime smoke test for the P1 HTTP slice against a running server."""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5080").rstrip("/")
CHARACTER_ID = "CHR_SMOKE_01"
CHECKS = 0


def check(condition, message):
    global CHECKS
    if not condition:
        raise AssertionError(message)
    CHECKS += 1


def call(method, path, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(f"{BASE_URL}{path}", data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    for name, value in (headers or {}).items():
        request.add_header(name, value)

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.headers, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        return error.code, error.headers, json.loads(error.read() or b"{}")


def sent_at_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def move_envelope(sequence, move_x, move_y, character_id=CHARACTER_ID, request_id="1" * 32):
    return {
        "schemaVersion": 1,
        "requestId": request_id,
        "idempotencyKey": "2" * 32,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": {"inputSequence": sequence, "moveX": move_x, "moveY": move_y},
    }


def combat_envelope(sequence, skill_id, target_id=None, character_id=CHARACTER_ID,
                    request_id="3" * 32, idempotency_key="4" * 32):
    payload = {
        "inputSequence": sequence,
        "skillId": skill_id,
        "aimX": 1,
        "aimY": 0,
    }
    if target_id is not None:
        payload["targetId"] = target_id

    return {
        "schemaVersion": 1,
        "requestId": request_id,
        "idempotencyKey": idempotency_key,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": payload,
    }


def quest_accept_envelope(quest_id, npc_id, character_id=CHARACTER_ID,
                          request_id="5" * 32, idempotency_key="9" * 32):
    return {
        "schemaVersion": 1,
        "requestId": request_id,
        "idempotencyKey": idempotency_key,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": {"questId": quest_id, "npcId": npc_id},
    }


def interact_envelope(target_id, character_id=CHARACTER_ID, request_id="8" * 32,
                      idempotency_key="7" * 32):
    return {
        "schemaVersion": 1,
        "requestId": request_id,
        "idempotencyKey": idempotency_key,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": {"targetId": target_id},
    }


def turnin_envelope(quest_id, npc_id, character_id=CHARACTER_ID,
                    request_id="30" * 32, idempotency_key="31" * 32):
    return {
        "schemaVersion": 1,
        "requestId": request_id,
        "idempotencyKey": idempotency_key,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": {"questId": quest_id, "npcId": npc_id},
    }


def combat_v2_envelope(action_kind, sequence, skill_id=None, target_id=None,
                      character_id=CHARACTER_ID, request_id="4" * 32,
                      idempotency_key="5" * 32):
    payload = {
        "actionKind": action_kind,
        "inputSequence": sequence,
        "aimX": 1,
        "aimY": 0,
    }
    if skill_id is not None:
        payload["skillId"] = skill_id
    if target_id is not None:
        payload["targetId"] = target_id
    return {
        "schemaVersion": 2,
        "requestId": request_id,
        "idempotencyKey": idempotency_key,
        "sentAtUtc": sent_at_utc(),
        "characterId": character_id,
        "payload": payload,
    }


def expect_correlation(headers, expected):
    check(headers.get("X-Correlation-ID") == expected,
          f"expected correlation {expected}, got {headers.get('X-Correlation-ID')}")


def main():
    status, headers, body = call("GET", "/health", headers={"X-Correlation-ID": "smoke-health"})
    check(status == 200, f"health returned {status}")
    check(body.get("status") == "ok", f"health body {body}")
    expect_correlation(headers, "smoke-health")

    status, headers, body = call(
        "POST", "/p1/sessions",
        {"characterId": CHARACTER_ID},
        {"X-Correlation-ID": "smoke-session"})
    check(status == 201, f"session returned {status}: {body}")
    session_id = body.get("sessionId")
    check(isinstance(session_id, str) and len(session_id) == 32,
          f"unexpected sessionId {session_id}")
    check(headers.get("Location") == f"/p1/world/{session_id}",
          f"unexpected Location header {headers.get('Location')}")
    check(body.get("revision") == 1, f"session revision {body.get('revision')}")
    result = body.get("result") or {}
    check(result.get("mapId") == "MAP_BEN_MUA", f"unexpected map {result.get('mapId')}")
    self_state = result.get("self") or {}
    check(self_state.get("x") == 18 and self_state.get("y") == 0,
          f"unexpected spawn {self_state.get('x')},{self_state.get('y')}")
    expect_correlation(headers, "smoke-session")

    time.sleep(0.1)
    first_move = move_envelope(1, 1, 0)
    status, headers, body = call(
        "POST", "/p1/move", first_move,
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-move"})
    check(status == 200, f"move returned {status}: {body}")
    check(body.get("revision") == 2, f"move revision {body.get('revision')}")
    moved = (body.get("result") or {}).get("self") or {}
    check(moved.get("x", 18) > 18, f"move did not advance x: {moved.get('x')}")
    check(moved.get("y") == 0, f"move changed y: {moved.get('y')}")
    moved_x = moved.get("x")
    expect_correlation(headers, "smoke-move")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(1, 1, 0),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-stale"})
    check(status == 409, f"stale move returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "stale_sequence", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is False, "stale_sequence must not be retryable")
    check(error.get("correlationId") == "smoke-stale",
          f"unexpected error correlation {error.get('correlationId')}")
    expect_correlation(headers, "smoke-stale")

    status, headers, body = call(
        "GET", f"/p1/world/{session_id}",
        headers={"X-Correlation-ID": "smoke-world"})
    check(status == 200, f"world returned {status}: {body}")
    world_self = (body.get("result") or {}).get("self") or {}
    check(world_self.get("x") == moved_x, "stale move changed position")
    check(body.get("revision") == 2, f"world revision {body.get('revision')}")
    expect_correlation(headers, "smoke-world")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(2, 0, -1, character_id="CHR_OTHER_01"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-wrong-character"})
    check(status == 400, f"wrong character returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("characterId" in (error.get("fieldErrors") or []),
          f"characterId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-wrong-character")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(2, 0, -1),
        {"X-Correlation-ID": "smoke-no-session"})
    check(status == 400, f"missing session header returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("X-Session-ID" in (error.get("fieldErrors") or []),
          f"X-Session-ID missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-no-session")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(2, 0, -1),
        {"X-Session-ID": "f" * 32, "X-Correlation-ID": "smoke-unknown-session"})
    check(status == 404, f"unknown session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "session_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-unknown-session")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(2, 0, -1, request_id="a" * 31),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-bad-request-id"})
    check(status == 400, f"short requestId returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("requestId" in (error.get("fieldErrors") or []),
          f"requestId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-bad-request-id")

    time.sleep(0.1)
    status, headers, body = call(
        "POST", "/p1/move", move_envelope(2, 0, -1),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-second-move"})
    check(status == 200, f"second move returned {status}: {body}")
    check(body.get("revision") == 3, f"second move revision {body.get('revision')}")
    second = (body.get("result") or {}).get("self") or {}
    check(second.get("y", 0) < 0, f"second move did not advance y: {second.get('y')}")
    check(second.get("x") == moved_x, f"second move changed x: {second.get('x')}")
    expect_correlation(headers, "smoke-second-move")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(3, "SK-MK-01"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat"})
    check(status == 200, f"combat returned {status}: {body}")
    check(body.get("revision") == 4, f"combat revision {body.get('revision')}")
    event = body.get("result") or {}
    event_payload = event.get("payload") or {}
    check(event.get("eventType") == "combat.effect",
          f"unexpected event type {event.get('eventType')}")
    check(event_payload.get("sourceId") == CHARACTER_ID,
          f"unexpected source {event_payload.get('sourceId')}")
    check(event_payload.get("targetId") == CHARACTER_ID,
          f"self cast target {event_payload.get('targetId')}")
    check(event_payload.get("skillId") == "SK-MK-01",
          f"unexpected skill {event_payload.get('skillId')}")
    check("damage" not in event_payload and "hit" not in event_payload,
          "combat must not invent damage or hit")
    cooldown_ends = event_payload.get("cooldownEndsAtUtc") or ""
    check(cooldown_ends.endswith("Z"), f"unexpected cooldown {cooldown_ends}")
    expect_correlation(headers, "smoke-combat")

    status, headers, body = call(
        "POST", "/p1/move", move_envelope(3, 1, 0),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-move-after-combat"})
    check(status == 409, f"move reusing combat sequence returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "stale_sequence",
          f"unexpected move error {error.get('code')}")
    expect_correlation(headers, "smoke-move-after-combat")

    status, headers, body = call(
        "GET", f"/p1/world/{session_id}",
        headers={"X-Correlation-ID": "smoke-world-after-combat"})
    check(status == 200, f"world after combat returned {status}: {body}")
    after_combat = (body.get("result") or {}).get("self") or {}
    check(after_combat.get("mp") == 38, f"combat mp {after_combat.get('mp')}")
    check(after_combat.get("x") == moved_x, "combat changed x")
    check(after_combat.get("y") == second.get("y"), "combat changed y")
    check(body.get("revision") == 4, f"world revision after combat {body.get('revision')}")
    expect_correlation(headers, "smoke-world-after-combat")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(3, "SK-MK-01"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-replay"})
    check(status == 200, f"combat replay returned {status}: {body}")
    replayed_event = body.get("result") or {}
    check(replayed_event.get("eventId") == event.get("eventId"),
          f"replay event {replayed_event.get('eventId')} != {event.get('eventId')}")
    check(body.get("revision") == 4, f"replay revision {body.get('revision')}")
    expect_correlation(headers, "smoke-combat-replay")

    status, headers, body = call(
        "POST", "/p1/combat",
        combat_envelope(3, "SK-MK-01", idempotency_key="6" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-stale"})
    check(status == 409, f"stale combat returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "stale_sequence", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is False, "stale_sequence must not be retryable")
    expect_correlation(headers, "smoke-combat-stale")

    status, headers, body = call(
        "POST", "/p1/combat",
        combat_envelope(4, "SK-MK-01", idempotency_key="5" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-cooldown"})
    check(status == 409, f"cooldown combat returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "cooldown_active", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is True, "cooldown_active should be retryable")
    expect_correlation(headers, "smoke-combat-cooldown")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(4, "SK-MK-01"),
        {"X-Correlation-ID": "smoke-combat-no-session"})
    check(status == 400, f"combat without session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("X-Session-ID" in (error.get("fieldErrors") or []),
          f"X-Session-ID missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-combat-no-session")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(4, "SK-MK-01"),
        {"X-Session-ID": "e" * 32, "X-Correlation-ID": "smoke-combat-unknown-session"})
    check(status == 404, f"combat unknown session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "session_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-combat-unknown-session")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(4, "SK-MK-09"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-bad-skill"})
    check(status == 400, f"invalid skill returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("payload.skillId" in (error.get("fieldErrors") or []),
          f"payload.skillId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-combat-bad-skill")

    status, headers, body = call(
        "POST", "/p1/combat",
        combat_envelope(4, "SK-MK-02", idempotency_key="7" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-no-target"})
    check(status == 400, f"missing target returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("targetId" in (error.get("fieldErrors") or []),
          f"targetId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-combat-no-target")

    status, headers, body = call(
        "POST", "/p1/combat",
        combat_envelope(4, "SK-MK-03", target_id="TGT_SMOKE_UNKNOWN",
                        idempotency_key="8" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-unknown-target"})
    check(status == 404, f"unknown target returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "target_not_found", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is True, "target_not_found should be retryable")
    expect_correlation(headers, "smoke-combat-unknown-target")

    time.sleep(0.1)
    status, headers, body = call(
        "POST", "/p1/move", move_envelope(4, 1, 0),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-move-after-rejections"})
    check(status == 200, f"move after rejections returned {status}: {body}")
    check(body.get("revision") == 5, f"move revision after combat {body.get('revision')}")
    expect_correlation(headers, "smoke-move-after-rejections")

    status, headers, body = call(
        "GET", f"/p1/quests/{session_id}",
        headers={"X-Correlation-ID": "smoke-quests"})
    check(status == 200, f"quests returned {status}: {body}")
    quests = body.get("result") or []
    check(len(quests) == 1, f"unexpected quest list {quests}")
    quest = quests[0] if quests else {}
    check(quest.get("questId") == "P00-01", f"unexpected quest id {quest.get('questId')}")
    check(quest.get("state") == "AVAILABLE", f"unexpected quest state {quest.get('state')}")
    check(quest.get("stepId") == "STEP_P00_01_PACKAGES", f"unexpected step {quest.get('stepId')}")
    check(quest.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 0},
          f"unexpected counters {quest.get('objectiveCounters')}")
    check(quest.get("revision") == 1, f"quest revision {quest.get('revision')}")
    expect_correlation(headers, "smoke-quests")

    status, headers, body = call(
        "GET", "/p1/quests/" + "d" * 32,
        headers={"X-Correlation-ID": "smoke-quests-unknown-session"})
    check(status == 404, f"unknown quest session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "session_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-quests-unknown-session")

    status, headers, body = call(
        "GET", f"/p1/inventory/{session_id}",
        headers={"X-Correlation-ID": "smoke-inventory"})
    check(status == 200, f"inventory returned {status}: {body}")
    snapshot = body.get("result") or {}
    check(snapshot.get("inventoryRevision") == 0,
          f"inventory revision {snapshot.get('inventoryRevision')}")
    check(snapshot.get("items") == [], f"inventory items {snapshot.get('items')}")
    check(snapshot.get("currencies") == [], f"inventory currencies {snapshot.get('currencies')}")
    expect_correlation(headers, "smoke-inventory")

    status, headers, body = call(
        "GET", "/p1/inventory/" + "d" * 32,
        headers={"X-Correlation-ID": "smoke-inventory-unknown-session"})
    check(status == 404, f"unknown inventory session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "session_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-inventory-unknown-session")

    sequence = 4
    status, headers, body = call(
        "GET", f"/p1/world/{session_id}",
        headers={"X-Correlation-ID": "smoke-walk-start"})
    check(status == 200, f"world before accept returned {status}: {body}")
    walker_x = ((body.get("result") or {}).get("self") or {}).get("x", 0)
    while walker_x < 37.5:
        sequence += 1
        time.sleep(0.3)
        status, headers, body = call(
            "POST", "/p1/move", move_envelope(sequence, 1, 0),
            {"X-Session-ID": session_id, "X-Correlation-ID": f"smoke-walk-{sequence}"})
        check(status == 200, f"walk move {sequence} returned {status}: {body}")
        walker_x = ((body.get("result") or {}).get("self") or {}).get("x", walker_x)

    check(walker_x >= 37.5, f"walker stopped at {walker_x}")

    status, headers, body = call(
        "GET", f"/p1/world/{session_id}",
        headers={"X-Correlation-ID": "smoke-world-pre-accept"})
    check(status == 200, f"world pre-accept returned {status}: {body}")
    world_revision_before_accept = body.get("revision")

    status, headers, body = call(
        "POST", "/p1/quests/accept", quest_accept_envelope("P00-01", "NPC_LYAN"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept"})
    check(status == 200, f"quest accept returned {status}: {body}")
    accepted = body.get("result") or {}
    check(accepted.get("state") == "ACTIVE", f"quest state {accepted.get('state')}")
    check(accepted.get("revision") == 2, f"quest revision {accepted.get('revision')}")
    check(body.get("sessionId") == session_id, f"accept session {body.get('sessionId')}")
    expect_correlation(headers, "smoke-quest-accept")

    status, headers, body = call(
        "POST", "/p1/quests/accept", quest_accept_envelope("P00-01", "NPC_LYAN"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept-replay"})
    check(status == 200, f"accept replay returned {status}: {body}")
    replayed = body.get("result") or {}
    check(replayed.get("state") == "ACTIVE", f"replay state {replayed.get('state')}")
    check(replayed.get("revision") == 2, f"replay revision {replayed.get('revision')}")
    expect_correlation(headers, "smoke-quest-accept-replay")

    status, headers, body = call(
        "POST", "/p1/quests/accept",
        quest_accept_envelope("P00-01", "NPC_TA_VAN_KHANH"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept-key-conflict"})
    check(status == 409, f"key conflict returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "idempotency_conflict", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-quest-accept-key-conflict")

    status, headers, body = call(
        "POST", "/p1/quests/accept",
        quest_accept_envelope("P00-01", "NPC_LYAN", idempotency_key="8" * 32,
                              request_id="7" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept-second"})
    check(status == 409, f"second accept returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_transition", f"unexpected error {error.get('code')}")
    check(((body.get("result") or {}).get("state")) == "ACTIVE", "second accept changed state")
    check(((body.get("result") or {}).get("revision")) == 2,
          "second accept changed revision")
    expect_correlation(headers, "smoke-quest-accept-second")

    status, headers, body = call(
        "POST", "/p1/quests/accept",
        quest_accept_envelope("P00-01", "NPC_TA_VAN_KHANH", idempotency_key="6" * 32,
                              request_id="4" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept-npc"})
    check(status == 422, f"npc mismatch returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "npc_mismatch", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-quest-accept-npc")

    status, headers, body = call(
        "POST", "/p1/quests/accept",
        quest_accept_envelope("P99-99", "NPC_LYAN", idempotency_key="3" * 32,
                              request_id="2" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-quest-accept-unknown"})
    check(status == 404, f"unknown quest returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "quest_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-quest-accept-unknown")

    status, headers, body = call(
        "GET", f"/p1/quests/{session_id}",
        headers={"X-Correlation-ID": "smoke-quests-after-accept"})
    check(status == 200, f"quests after accept returned {status}: {body}")
    after_accept = (body.get("result") or [{}])[0]
    check(after_accept.get("state") == "ACTIVE", f"read back state {after_accept.get('state')}")
    expect_correlation(headers, "smoke-quests-after-accept")

    status, headers, body = call(
        "GET", f"/p1/world/{session_id}",
        headers={"X-Correlation-ID": "smoke-world-after-accept"})
    check(status == 200, f"world after accept returned {status}: {body}")
    check(body.get("revision") == world_revision_before_accept,
          f"accept changed world revision {body.get('revision')} != {world_revision_before_accept}")
    expect_correlation(headers, "smoke-world-after-accept")

    status, headers, body = call(
        "POST", "/p1/sessions",
        {"characterId": "CHR_SMOKE_FAR_01"},
        {"X-Correlation-ID": "smoke-far-session"})
    check(status == 201, f"far session returned {status}: {body}")
    far_session_id = body.get("sessionId")
    status, headers, body = call(
        "POST", "/p1/quests/accept",
        quest_accept_envelope("P00-01", "NPC_LYAN", character_id="CHR_SMOKE_FAR_01",
                              idempotency_key="1" * 31 + "0", request_id="0" * 31 + "1"),
        {"X-Session-ID": far_session_id, "X-Correlation-ID": "smoke-quest-accept-far"})
    check(status == 422, f"far accept returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "out_of_range", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is True, "out_of_range should be retryable")
    expect_correlation(headers, "smoke-quest-accept-far")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_01", idempotency_key="a" * 32,
                          request_id="b" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-package-1"})
    check(status == 200, f"interact returned {status}: {body}")
    interact_result = body.get("result") or {}
    check(interact_result.get("targetId") == "ENT_MAN_BM_OBJ_BM_PACKAGE_01",
          f"interact target {interact_result.get('targetId')}")
    check(interact_result.get("recordId") == "MAN-BM-OBJ_BM_PACKAGE_01",
          f"interact record {interact_result.get('recordId')}")
    check(interact_result.get("kind") == "INTERACTABLE",
          f"interact kind {interact_result.get('kind')}")
    check(interact_result.get("outcome") == "collected",
          f"interact outcome {interact_result.get('outcome')}")
    # P00-01 packages are per-character claims (Production Rules §5): the
    # world state stays AVAILABLE for other characters, only this character's
    # claim window is consumed.
    check(interact_result.get("targetState") == "AVAILABLE",
          f"interact targetState {interact_result.get('targetState')}")
    check(interact_result.get("yield") is None,
          f"package must not yield {interact_result.get('yield')}")
    check((interact_result.get("respawnAtUtc") or "").endswith("Z"),
          f"interact respawn {interact_result.get('respawnAtUtc')}")
    interaction_id = interact_result.get("interactionId")
    check(isinstance(interaction_id, str) and len(interaction_id) == 32,
          f"unexpected interactionId {interaction_id}")
    interact_updates = interact_result.get("questUpdates") or []
    check(len(interact_updates) == 1, f"unexpected questUpdates {interact_updates}")
    first_update = interact_updates[0] if interact_updates else {}
    check(first_update.get("questId") == "P00-01",
          f"unexpected updated quest {first_update.get('questId')}")
    check(first_update.get("state") == "ACTIVE",
          f"unexpected quest state {first_update.get('state')}")
    check(first_update.get("revision") == 3,
          f"quest revision {first_update.get('revision')}")
    check(first_update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 1},
          f"unexpected counters {first_update.get('objectiveCounters')}")
    expect_correlation(headers, "smoke-interact-package-1")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_01", idempotency_key="a" * 32,
                          request_id="b" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-replay"})
    check(status == 200, f"interact replay returned {status}: {body}")
    replayed_interact = body.get("result") or {}
    check(replayed_interact.get("interactionId") == interaction_id,
          f"replay interactionId {replayed_interact.get('interactionId')}")
    check(((replayed_interact.get("questUpdates") or [{}])[0]).get("revision") == 3,
          "replay must not advance quest progress")
    expect_correlation(headers, "smoke-interact-replay")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_02", idempotency_key="a" * 32,
                          request_id="c" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-conflict"})
    check(status == 409, f"interact conflict returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "idempotency_conflict",
          f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-interact-conflict")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_01", idempotency_key="d" * 32,
                          request_id="e" * 32),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-depleted"})
    check(status == 409, f"depleted interact returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "target_not_available",
          f"unexpected error {error.get('code')}")
    check(error.get("retryable") is False, "target_not_available must not be retryable")
    expect_correlation(headers, "smoke-interact-depleted")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_NPC_LYAN", idempotency_key="f" * 32,
                          request_id="10" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-npc"})
    check(status == 400, f"npc interact returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_target", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-interact-npc")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_SMOKE_MISSING", idempotency_key="11" * 16,
                          request_id="12" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-missing"})
    check(status == 404, f"missing target returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "target_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-interact-missing")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_03", character_id="CHR_SMOKE_FAR_01",
                          idempotency_key="13" * 16, request_id="14" * 16),
        {"X-Session-ID": far_session_id, "X-Correlation-ID": "smoke-interact-far"})
    check(status == 422, f"far interact returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "out_of_range", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is True, "out_of_range should be retryable")
    expect_correlation(headers, "smoke-interact-far")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_02", character_id="CHR_OTHER_01",
                          idempotency_key="15" * 16, request_id="16" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-wrong-character"})
    check(status == 400, f"wrong character interact returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("characterId" in (error.get("fieldErrors") or []),
          f"characterId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-interact-wrong-character")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_02", idempotency_key="17" * 16,
                          request_id="18" * 16),
        {"X-Correlation-ID": "smoke-interact-no-session"})
    check(status == 400, f"interact without session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("X-Session-ID" in (error.get("fieldErrors") or []),
          f"X-Session-ID missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-interact-no-session")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_02", idempotency_key="19" * 16,
                          request_id="20" * 16),
        {"X-Session-ID": "z" * 32, "X-Correlation-ID": "smoke-interact-unknown-session"})
    check(status == 404, f"interact unknown session returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "session_not_found", f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-interact-unknown-session")

    while walker_x < 39.5:
        sequence += 1
        time.sleep(0.3)
        status, headers, body = call(
            "POST", "/p1/move", move_envelope(sequence, 1, 0),
            {"X-Session-ID": session_id, "X-Correlation-ID": f"smoke-walk-pkg2-{sequence}"})
        check(status == 200, f"walk pkg2 move {sequence} returned {status}: {body}")
        walker_x = ((body.get("result") or {}).get("self") or {}).get("x", walker_x)

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_02", idempotency_key="21" * 16,
                          request_id="22" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-package-2"})
    check(status == 200, f"package 2 returned {status}: {body}")
    second_update = (((body.get("result") or {}).get("questUpdates")) or [{}])[0]
    check(second_update.get("state") == "ACTIVE",
          f"package 2 quest state {second_update.get('state')}")
    check(second_update.get("revision") == 4,
          f"package 2 quest revision {second_update.get('revision')}")
    check(second_update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 2},
          f"package 2 counters {second_update.get('objectiveCounters')}")
    expect_correlation(headers, "smoke-interact-package-2")

    while walker_x < 47.5:
        sequence += 1
        time.sleep(0.3)
        status, headers, body = call(
            "POST", "/p1/move", move_envelope(sequence, 1, 0),
            {"X-Session-ID": session_id, "X-Correlation-ID": f"smoke-walk-pkg3-{sequence}"})
        check(status == 200, f"walk pkg3 move {sequence} returned {status}: {body}")
        walker_x = ((body.get("result") or {}).get("self") or {}).get("x", walker_x)

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_OBJ_BM_PACKAGE_03", idempotency_key="23" * 16,
                          request_id="24" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-interact-package-3"})
    check(status == 200, f"package 3 returned {status}: {body}")
    third_update = (((body.get("result") or {}).get("questUpdates")) or [{}])[0]
    check(third_update.get("state") == "READY_TO_TURN_IN",
          f"package 3 quest state {third_update.get('state')}")
    check(third_update.get("revision") == 5,
          f"package 3 quest revision {third_update.get('revision')}")
    check(third_update.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 3},
          f"package 3 counters {third_update.get('objectiveCounters')}")
    expect_correlation(headers, "smoke-interact-package-3")

    status, headers, body = call(
        "GET", f"/p1/quests/{session_id}",
        headers={"X-Correlation-ID": "smoke-quests-ready"})
    check(status == 200, f"quests after packages returned {status}: {body}")
    ready_quest = (body.get("result") or [{}])[0]
    check(ready_quest.get("state") == "READY_TO_TURN_IN",
          f"read back state {ready_quest.get('state')}")
    check(ready_quest.get("objectiveCounters") == {"OBJ_P00_01_PACKAGES": 3},
          f"read back counters {ready_quest.get('objectiveCounters')}")
    check(ready_quest.get("revision") == 5, f"read back revision {ready_quest.get('revision')}")
    expect_correlation(headers, "smoke-quests-ready")

    status, headers, body = call(
        "POST", "/p1/sessions",
        {"characterId": "CHR_SMOKE_GATHER_01"},
        {"X-Correlation-ID": "smoke-gather-session"})
    check(status == 201, f"gather session returned {status}: {body}")
    gather_session_id = body.get("sessionId")
    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_NODE_BM_ORE_01", character_id="CHR_SMOKE_GATHER_01",
                          idempotency_key="25" * 16, request_id="26" * 16),
        {"X-Session-ID": gather_session_id, "X-Correlation-ID": "smoke-interact-gather"})
    check(status == 200, f"gather returned {status}: {body}")
    gather_result = body.get("result") or {}
    check(gather_result.get("kind") == "GATHER_NODE",
          f"gather kind {gather_result.get('kind')}")
    check(gather_result.get("outcome") == "gathered",
          f"gather outcome {gather_result.get('outcome')}")
    check(gather_result.get("targetState") == "AVAILABLE",
          f"gather targetState {gather_result.get('targetState')}")
    check((gather_result.get("respawnAtUtc") or "").endswith("Z"),
          f"gather respawn {gather_result.get('respawnAtUtc')}")
    gather_yield = gather_result.get("yield") or {}
    check(gather_yield.get("itemId") == "MAT-ORE-01",
          f"gather item {gather_yield.get('itemId')}")
    check(gather_yield.get("quantity") in (1, 2),
          f"gather quantity {gather_yield.get('quantity')}")
    expect_correlation(headers, "smoke-interact-gather")

    status, headers, body = call(
        "GET", f"/p1/inventory/{gather_session_id}",
        headers={"X-Correlation-ID": "smoke-gather-inventory"})
    check(status == 200, f"gather inventory returned {status}: {body}")
    gather_snapshot = body.get("result") or {}
    check(gather_snapshot.get("inventoryRevision") == 1,
          f"gather inventory revision {gather_snapshot.get('inventoryRevision')}")
    gather_items = gather_snapshot.get("items") or []
    check(len(gather_items) == 1, f"gather items {gather_items}")
    check(gather_items[0].get("templateId") == "MAT-ORE-01",
          f"gather item template {gather_items[0].get('templateId')}")
    check(gather_items[0].get("stack") == gather_yield.get("quantity"),
          f"gather item stack {gather_items[0].get('stack')}")
    check(gather_items[0].get("location") == "BAG",
          f"gather item location {gather_items[0].get('location')}")
    expect_correlation(headers, "smoke-gather-inventory")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_NODE_BM_ORE_01", character_id="CHR_SMOKE_GATHER_01",
                          idempotency_key="25" * 16, request_id="26" * 16),
        {"X-Session-ID": gather_session_id, "X-Correlation-ID": "smoke-interact-gather-replay"})
    check(status == 200, f"gather replay returned {status}: {body}")
    check(((body.get("result") or {}).get("interactionId"))
          == gather_result.get("interactionId"), "gather replay changed interactionId")
    expect_correlation(headers, "smoke-interact-gather-replay")

    status, headers, body = call(
        "POST", "/p1/world/interact",
        interact_envelope("ENT_MAN_BM_NODE_BM_ORE_01", character_id="CHR_SMOKE_GATHER_01",
                          idempotency_key="27" * 16, request_id="28" * 16),
        {"X-Session-ID": gather_session_id, "X-Correlation-ID": "smoke-interact-gather-cooldown"})
    check(status == 409, f"gather cooldown returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "target_not_available",
          f"unexpected error {error.get('code')}")
    expect_correlation(headers, "smoke-interact-gather-cooldown")

    status, headers, body = call(
        "GET", f"/p1/inventory/{gather_session_id}",
        headers={"X-Correlation-ID": "smoke-gather-no-double"})
    check(status == 200, f"gather inventory readback returned {status}: {body}")
    check((body.get("result") or {}).get("inventoryRevision") == 1,
          "rejected gather must not grant items twice")
    expect_correlation(headers, "smoke-gather-no-double")

    # ─── turn-in ────────────────────────────────────────────

    while walker_x < 64:
        sequence += 1
        time.sleep(0.3)
        status, headers, body = call(
            "POST", "/p1/move", move_envelope(sequence, 1, 0),
            {"X-Session-ID": session_id, "X-Correlation-ID": f"smoke-walk-turnin-{sequence}"})
        check(status == 200, f"walk turnin move {sequence} returned {status}: {body}")
        walker_x = ((body.get("result") or {}).get("self") or {}).get("x", walker_x)

    status, headers, body = call(
        "POST", "/p1/quests/turnin",
        turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                        idempotency_key="32" * 16, request_id="33" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-turnin"})
    check(status == 200, f"turnin returned {status}: {body}")
    turnin_result = body.get("result") or {}
    quest_state = turnin_result.get("questState") or {}
    check(quest_state.get("state") == "COMPLETED",
          f"turnin quest state {quest_state.get('state')}")
    check(quest_state.get("revision") == 6,
          f"turnin quest revision {quest_state.get('revision')}")
    rewards = turnin_result.get("rewards") or {}
    check(len(rewards.get("currency") or []) == 1, f"currency count {rewards.get('currency')}")
    check(rewards["currency"][0].get("currencyId") == "COIN",
          f"currency id {rewards['currency'][0].get('currencyId')}")
    check(rewards["currency"][0].get("amount") == 20,
          f"currency amount {rewards['currency'][0].get('amount')}")
    check(len(rewards.get("items") or []) == 1, f"item count {rewards.get('items')}")
    check(rewards["items"][0].get("templateId") == "EQ-MK-CHEST-T1-R-COMMON",
          f"item template {rewards['items'][0].get('templateId')}")
    check(rewards["items"][0].get("stack") == 1,
          f"item stack {rewards['items'][0].get('stack')}")
    check(rewards["items"][0].get("location") == "BAG",
          f"item location {rewards['items'][0].get('location')}")
    xp = rewards.get("xp") or {}
    check(xp.get("xpRule") == "LEVEL_BAND_BASE",
          f"xp rule {xp.get('xpRule')}")
    check(xp.get("applied") is False, f"xp applied {xp.get('applied')}")
    check(turnin_result.get("unlocks") == ["P00-02"],
          f"unlocks {turnin_result.get('unlocks')}")
    expect_correlation(headers, "smoke-turnin")

    # replay same key
    status, headers, body = call(
        "POST", "/p1/quests/turnin",
        turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                        idempotency_key="32" * 16, request_id="34" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-turnin-replay"})
    check(status == 200, f"turnin replay returned {status}: {body}")
    replay_result = body.get("result") or {}
    check((replay_result.get("questState") or {}).get("state") == "COMPLETED",
          f"replay state {(replay_result.get('questState') or {}).get('state')}")
    expect_correlation(headers, "smoke-turnin-replay")

    # second turn-in with new key → invalid_transition
    status, headers, body = call(
        "POST", "/p1/quests/turnin",
        turnin_envelope("P00-01", "NPC_TA_VAN_KHANH",
                        idempotency_key="35" * 16, request_id="36" * 16),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-turnin-second"})
    check(status == 409, f"second turnin returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_transition",
          f"second turnin error {error.get('code')}")
    expect_correlation(headers, "smoke-turnin-second")

    # inventory readback: no double reward
    status, headers, body = call(
        "GET", f"/p1/inventory/{session_id}",
        headers={"X-Correlation-ID": "smoke-turnin-inventory"})
    check(status == 200, f"turnin inventory returned {status}: {body}")
    inv = body.get("result") or {}
    check(len(inv.get("currencies") or []) == 1,
          f"inventory currencies after turnin {inv.get('currencies')}")
    check(inv["currencies"][0].get("amount") == 20,
          f"coin amount {inv['currencies'][0].get('amount')}")
    check(len(inv.get("items") or []) == 1,
          f"inventory items after turnin {inv.get('items')}")
    check(inv["items"][0].get("templateId") == "EQ-MK-CHEST-T1-R-COMMON",
          f"inv item template {inv['items'][0].get('templateId')}")
    expect_correlation(headers, "smoke-turnin-inventory")

    # -- v2 opt-in surface (P1__CombatV2__Enabled=true) -------------------
    v2_character = "CHR_SMOKE_V2_01"
    status, _, body = call("POST", "/p1/sessions", {"characterId": v2_character})
    check(status == 201, f"v2 session returned {status}: {body}")
    v2_session = body.get("sessionId")

    status, headers, body = call(
        "GET", f"/p1/v2/world/{v2_session}",
        headers={"X-Correlation-ID": "smoke-v2-world"})
    check(status == 200, f"v2 world returned {status}: {body}")
    world = body.get("result") or {}
    check(world.get("schemaVersion") == 2, f"v2 world schema {world.get('schemaVersion')}")
    check(world.get("mapId") == "MAP_BEN_MUA", f"v2 world map {world.get('mapId')}")
    check(world.get("mapInstanceId") == "MAP_BEN_MUA#1",
          f"v2 map instance {world.get('mapInstanceId')}")
    check(world.get("floorId") == "OVERWORLD", f"v2 floor {world.get('floorId')}")
    check(world.get("phase") == "OPEN_WORLD", f"v2 phase {world.get('phase')}")
    check((world.get("audience") or {}).get("aoiEnterWu") == 40, "v2 AOI enter")
    check((world.get("audience") or {}).get("aoiLeaveWu") == 48, "v2 AOI leave")
    check((world.get("self") or {}).get("characterId") == v2_character, "v2 self character")
    world_entities = world.get("entities") or []
    check(len(world_entities) > 0, "v2 world has no entities at spawn")
    by_id = {entity.get("entityId"): entity for entity in world_entities}
    npc = by_id.get("ENT_MAN_BM_NPC_LYAN")
    check(npc is not None, "v2 NPC missing at spawn")
    check(npc.get("healthState") == "INVULNERABLE", f"v2 NPC health {npc.get('healthState')}")
    check(npc.get("targetable") is False, "v2 NPC must not be targetable")
    check(npc.get("hp") == 0 and npc.get("maxHp") == 0, "v2 NPC hp must be 0")
    node = by_id.get("ENT_MAN_BM_NODE_BM_ORE_01")
    check(node is not None and node.get("availability") == "AVAILABLE",
          f"v2 node availability {node and node.get('availability')}")
    for entity in world_entities:
        for key in ("entityId", "kind", "mapInstanceId", "floorId", "phase", "state",
                    "healthState", "targetable", "revision", "lifeId"):
            check(key in entity, f"v2 entity missing {key}: {entity}")
    expect_correlation(headers, "smoke-v2-world")

    v2_sequence = 1
    walker_x = ((world.get("self") or {}).get("x"))
    while walker_x < 45:
        v2_sequence += 1
        time.sleep(0.3)
        status, _, body = call(
            "POST", "/p1/move",
            move_envelope(v2_sequence, 1, 0, character_id=v2_character),
            {"X-Session-ID": v2_session})
        check(status == 200, f"v2 walk {v2_sequence} returned {status}: {body}")
        walker_x = ((body.get("result") or {}).get("self") or {}).get("x", walker_x)

    status, headers, body = call(
        "GET", f"/p1/v2/world/{v2_session}",
        headers={"X-Correlation-ID": "smoke-v2-world-mob"})
    check(status == 200, f"v2 world 2 returned {status}: {body}")
    mob = next(
        (entity for entity in (body.get("result") or {}).get("entities") or []
         if entity.get("entityId") == "ENT_MAN_BM_SPAWN_BM_01"), None)
    check(mob is not None, "v2 mob missing inside AOI")
    check(mob.get("kind") == "MOB", f"v2 mob kind {mob.get('kind')}")
    check(mob.get("hp") == 192 and mob.get("maxHp") == 192, f"v2 mob hp {mob.get('hp')}")
    check(mob.get("healthState") == "ALIVE", f"v2 mob health {mob.get('healthState')}")
    check(mob.get("targetable") is True, "v2 alive mob must be targetable")
    # P1:MobBehavior stays off in smoke, so the AI lifecycle field is present
    # and parked at IDLE; TELEGRAPH/RECOVER are exercised by the self-check.
    check(mob.get("state") == "IDLE", f"v2 mob state {mob.get('state')}")
    expect_correlation(headers, "smoke-v2-world-mob")

    v2_sequence += 1
    basic_key = "42" * 16
    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("BASIC_ATTACK", v2_sequence,
                           character_id=v2_character, idempotency_key=basic_key),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-basic"})
    check(status == 200, f"v2 basic returned {status}: {body}")
    basic = body.get("result") or {}
    check(isinstance(basic.get("castId"), str) and len(basic["castId"]) == 32,
          f"v2 basic castId {basic.get('castId')}")
    check(basic.get("actionKind") == "BASIC_ATTACK", "v2 basic action")
    check(basic.get("mp") == 50 and basic.get("mpCost") == 0, "v2 basic cost")
    basic_events = basic.get("events") or []
    check(len(basic_events) == 1 and basic_events[0].get("type") == "CAST_START",
          f"v2 basic events {basic_events}")
    check(basic_events[0].get("cursor") == 1, "v2 basic cursor")
    expect_correlation(headers, "smoke-v2-basic")

    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("BASIC_ATTACK", v2_sequence,
                           character_id=v2_character, idempotency_key=basic_key),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-basic-replay"})
    check(status == 200, f"v2 replay returned {status}: {body}")
    replay_result = body.get("result") or {}
    check(replay_result.get("castId") == basic["castId"], "v2 replay castId")
    check((replay_result.get("events") or [{}])[0].get("cursor") == 1, "v2 replay cursor")
    expect_correlation(headers, "smoke-v2-basic-replay")

    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("BASIC_ATTACK", v2_sequence, target_id="ENT_MAN_BM_SPAWN_BM_01",
                           character_id=v2_character, idempotency_key=basic_key),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-conflict"})
    check(status == 409, f"v2 conflict returned {status}: {body}")
    check((body.get("error") or {}).get("code") == "idempotency_conflict",
          f"v2 conflict error {(body.get('error') or {}).get('code')}")
    expect_correlation(headers, "smoke-v2-conflict")

    v2_sequence += 1
    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("SKILL", v2_sequence, skill_id="SK-MK-01",
                           character_id=v2_character, idempotency_key="43" * 16),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-skill"})
    check(status == 200, f"v2 skill returned {status}: {body}")
    skill_result = body.get("result") or {}
    check(skill_result.get("mp") == 38, f"v2 skill mp {skill_result.get('mp')}")
    skill_start_cursor = (skill_result.get("events") or [{}])[0].get("cursor")
    check(isinstance(skill_start_cursor, int) and skill_start_cursor > basic_events[0]["cursor"], "v2 skill cursor after basic")
    expect_correlation(headers, "smoke-v2-skill")

    v2_sequence += 1
    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("SKILL", v2_sequence, skill_id="SK-MK-01",
                           character_id=v2_character, idempotency_key="44" * 16),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-cooldown"})
    check(status == 409, f"v2 cooldown returned {status}: {body}")
    check((body.get("error") or {}).get("code") == "cooldown_active",
          f"v2 cooldown error {(body.get('error') or {}).get('code')}")
    expect_correlation(headers, "smoke-v2-cooldown")

    status, headers, body = call(
        "POST", "/p1/v2/combat",
        combat_v2_envelope("BASIC_ATTACK", v2_sequence - 1,
                           character_id=v2_character, idempotency_key="45" * 16),
        {"X-Session-ID": v2_session, "X-Correlation-ID": "smoke-v2-stale"})
    check(status == 409, f"v2 stale returned {status}: {body}")
    check((body.get("error") or {}).get("code") == "stale_sequence",
          f"v2 stale error {(body.get('error') or {}).get('code')}")
    expect_correlation(headers, "smoke-v2-stale")

    status, headers, body = call(
        "GET", f"/p1/v2/events/{v2_session}?cursor=0",
        headers={"X-Correlation-ID": "smoke-v2-events"})
    check(status == 200, f"v2 events returned {status}: {body}")
    page = body.get("result") or {}
    check(page.get("schemaVersion") == 2 and page.get("sessionId") == v2_session,
          "v2 events envelope")
    check(page.get("nextCursor", 0) >= skill_start_cursor, f"v2 events next {page.get('nextCursor')}")
    check(page.get("resyncRequired") is False, "v2 events resync flag")
    page_events = page.get("events") or []
    cursors = [event.get("cursor") for event in page_events]
    check(cursors == sorted(set(cursors)) and cursors[-1] == page.get("nextCursor"),
          f"v2 events cursors {cursors}")
    starts = [event for event in page_events if event.get("type") == "CAST_START"]
    check(len(starts) == 2 and {event.get("castId") for event in starts} == {basic["castId"], skill_result["castId"]},
          "v2 command starts present once; real tick END may interleave")
    expect_correlation(headers, "smoke-v2-events")

    status, headers, body = call(
        "GET", f"/p1/v2/events/{v2_session}?cursor=1",
        headers={"X-Correlation-ID": "smoke-v2-events-since"})
    check(status == 200, f"v2 events since returned {status}: {body}")
    since_events = (body.get("result") or {}).get("events") or []
    check(all(event.get("cursor", 0) > 1 for event in since_events) and
          any(event.get("castId") == skill_result["castId"] and event.get("type") == "CAST_START" for event in since_events),
          f"v2 events since {since_events}")
    expect_correlation(headers, "smoke-v2-events-since")

    status, headers, body = call(
        "GET", f"/p1/v2/events/{v2_session}?cursor=99",
        headers={"X-Correlation-ID": "smoke-v2-events-resync"})
    check(status == 200, f"v2 events resync returned {status}: {body}")
    resync = body.get("result") or {}
    check(resync.get("resyncRequired") is True, "v2 resync flag missing")
    check(resync.get("resyncReason") == "CURSOR_TOO_OLD",
          f"v2 resync reason {resync.get('resyncReason')}")
    check((resync.get("events") or []) == [], "v2 resync must not return events")
    expect_correlation(headers, "smoke-v2-events-resync")

    status, headers, body = call(
        "GET", f"/p1/v2/events/{v2_session}?cursor=-1",
        headers={"X-Correlation-ID": "smoke-v2-events-bad-cursor"})
    check(status == 400, f"v2 bad cursor returned {status}: {body}")
    check((body.get("error") or {}).get("code") == "invalid_payload",
          f"v2 bad cursor error {(body.get('error') or {}).get('code')}")
    expect_correlation(headers, "smoke-v2-events-bad-cursor")

    # Regression: a receipt replay after END must not reschedule a completed cast.
    # Use a fresh isolated actor at spawn, outside damage range of any mob.
    status, _, spawned = call("POST", "/p1/sessions", {"classId": "CLASS_MINH_KIEM"})
    check(status == 201, "late replay create actor")
    late_session = spawned["sessionId"]
    late_character = spawned["result"]["self"]["characterId"]
    late_headers = {"X-Session-ID": late_session}
    late_command = combat_v2_envelope("BASIC_ATTACK", 1, character_id=late_character,
                                      request_id="6" * 32, idempotency_key="7" * 32)
    status, _, accepted = call("POST", "/p1/v2/combat", late_command, late_headers)
    check(status == 200, "late replay initial accept")
    late_cast = accepted["result"]["castId"]
    deadline = time.monotonic() + 3
    finished_page = {}
    late_read_status = 0
    while time.monotonic() < deadline:
        late_read_status, _, ended = call("GET", f"/p1/v2/events/{late_session}?cursor=0", headers=late_headers)
        finished_page = ended.get("result") or {}
        if any(e.get("type") == "END" for e in finished_page.get("events", [])):
            break
        time.sleep(0.05)
    # The status assertion lives outside the poll: a check inside a bounded wait
    # runs a different number of times per run, so the reported total would stop
    # meaning "these checks all ran".
    check(late_read_status == 200, "late replay read before END")
    check(sum(e.get("type") == "END" for e in finished_page.get("events", [])) == 1,
          "original cast completed exactly once")
    status, _, repeated = call("POST", "/p1/v2/combat", late_command, late_headers)
    check(status == 200 and repeated["result"]["castId"] == late_cast,
          "late replay returns original cast receipt")
    time.sleep(0.4)
    status, _, after_replay = call("GET", f"/p1/v2/events/{late_session}?cursor={finished_page['nextCursor']}", headers=late_headers)
    check(status == 200 and not after_replay["result"]["events"],
          "late replay emitted no new END, impact or other lifecycle event")

    # SK-MK-02 dash resolves on the real tick: the actor must actually move the
    # canonical 11 WU on this unreviewed map, and the committed MP is not
    # refunded by the movement. Fresh session so earlier cursor assertions hold.
    status, _, dash_created = call("POST", "/p1/sessions", {"classId": "CLASS_MINH_KIEM"})
    check(status == 201, "dash session created")
    dash_session = dash_created["sessionId"]
    dash_character = dash_created["result"]["self"]["characterId"]
    dash_headers = {"X-Session-ID": dash_session}
    dash_start_x = dash_created["result"]["self"]["x"]
    dash_revision = dash_created["revision"]
    dash_command = combat_v2_envelope("SKILL", 1, skill_id="SK-MK-02",
                                      character_id=dash_character,
                                      request_id="8" * 32, idempotency_key="9" * 32)
    status, _, dash_accept = call("POST", "/p1/v2/combat", dash_command, dash_headers)
    check(status == 200, f"dash accepted returned {status}: {dash_accept}")
    check((dash_accept.get("result") or {}).get("mp") == 34,
          f"dash mp {(dash_accept.get('result') or {}).get('mp')}")
    dash_deadline = time.monotonic() + 3
    dash_moved = False
    dash_self = {}
    dash_page = {}
    dash_read_status = 0
    while time.monotonic() < dash_deadline:
        dash_read_status, _, dash_world = call("GET", f"/p1/v2/world/{dash_session}", headers=dash_headers)
        dash_page = dash_world.get("result") or {}
        dash_self = dash_page.get("self") or {}
        if dash_self.get("x") != dash_start_x:
            dash_moved = True
            break
        time.sleep(0.05)
    check(dash_read_status == 200, f"dash world read returned {dash_read_status}")
    check(dash_moved and dash_self.get("x") == dash_start_x + 11,
          f"dash moved {dash_start_x} -> {dash_self.get('x')} (expected {dash_start_x + 11})")
    check(dash_self.get("mp") == 34 and dash_self.get("hp") == 100,
          f"dash kept cost/hp mp={dash_self.get('mp')} hp={dash_self.get('hp')}")
    check(dash_world.get("revision", dash_revision) > dash_revision,
          f"dash revision {dash_revision} -> {dash_world.get('revision')}")

    print(f"PASS: {CHECKS} smoke checks against {BASE_URL}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as failure:
        print(f"FAIL: {failure}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as failure:
        print(f"FAIL: server unreachable at {BASE_URL}: {failure}", file=sys.stderr)
        sys.exit(1)
