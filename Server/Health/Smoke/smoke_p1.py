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
                    request_id="3" * 32):
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
        "idempotencyKey": "4" * 32,
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
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-stale"})
    check(status == 409, f"replayed combat returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "stale_sequence", f"unexpected error {error.get('code')}")
    check(error.get("retryable") is False, "stale_sequence must not be retryable")
    expect_correlation(headers, "smoke-combat-stale")

    status, headers, body = call(
        "POST", "/p1/combat", combat_envelope(4, "SK-MK-01"),
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
        "POST", "/p1/combat", combat_envelope(4, "SK-MK-02"),
        {"X-Session-ID": session_id, "X-Correlation-ID": "smoke-combat-no-target"})
    check(status == 400, f"missing target returned {status}: {body}")
    error = body.get("error") or {}
    check(error.get("code") == "invalid_payload", f"unexpected error {error.get('code')}")
    check("targetId" in (error.get("fieldErrors") or []),
          f"targetId missing from {error.get('fieldErrors')}")
    expect_correlation(headers, "smoke-combat-no-target")

    status, headers, body = call(
        "POST", "/p1/combat",
        combat_envelope(4, "SK-MK-03", target_id="TGT_SMOKE_UNKNOWN"),
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
