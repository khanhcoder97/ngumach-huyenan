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
