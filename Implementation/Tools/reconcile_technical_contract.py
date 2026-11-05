#!/usr/bin/env python3
"""Reconcile docs/production/Production_Technical_Contracts_vi.md against what this
repository actually ships.

The contract doc is the frozen, transport-independent baseline the P1 surface was built
to, and until now nothing compared it to the shipped surface: no loader reads it and no
check cites it. This reads the three lists the doc states - the request envelope fields,
the server event fields, and the canonical error codes - against the wire contract
schemas and the error-code constants declared in the server, and prints every divergence
by name.

It changes nothing: not a route, not a schema, not a gate, not a docs/production file.
A divergence listed here is a decision somebody has to make; the point is that it becomes
a named field instead of a feeling, and that a future edit of either list has to be
deliberate.

    python Implementation/Tools/reconcile_technical_contract.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "production" / "Production_Technical_Contracts_vi.md"
WIRE_SCHEMA_DIR = ROOT / "Implementation" / "Contracts" / "P1"
SERVER_DIR = ROOT / "Server" / "Health"

# Section 1, 4 and 7 are written in Vietnamese around the tokens, so every anchor below is
# a sentence the doc uses, not a line number. EXPECTED holds the counts measured from the
# doc and from the shipped contract set at this head; changing any of them is a contract
# change and must be a deliberate edit of this file, not a drift.
EXPECTED = {
    "request_envelope": 6,
    "response_envelope": 4,
    "event_fields": 7,
    "canonical_errors": 13,
    "wire_schemas": 31,
}

ENVELOPE_BLOCK = re.compile(r"## 1\..*?\n```json\n(.*?)```", re.DOTALL)
RESPONSE_FIELDS = re.compile(r"Response th\u00eam ((?:[ `\w]+,)+[ `\w]+)")
EVENT_FIELDS = re.compile(r"Server events have `\{([^`]*)\}`")
CANONICAL_ERRORS = re.compile(r"Canonical errors: ((?:`[A-Z][A-Z_]+`,? ?)+)")
JSON_KEY = re.compile(r'^\s*"?([A-Za-z][A-Za-z0-9]*)"?\s*:', re.MULTILINE)
# The server declares its wire codes as lowercase constants, e.g.
# `public const string RevisionConflict = "revision_conflict";` in the outcome types.
ERROR_CONST = re.compile(r'const string \w+ = "([a-z][a-z0-9_]{3,})";')
# Retention and acceptance numbers the doc states in prose, kept as anchors so a change
# in the doc is reported rather than missed.
IDEMPOTENCY_RETENTION = re.compile(r"`idempotencyKey \+ actorId \+ operation` [^.]*?(\d+) ng\u00e0y")
REPLAY_BASELINE = re.compile(r"([0-9][0-9,.]{3,}) replayed idempotent commands")
RATE_LIMIT_SENTENCE = "rate limit"


def strip_backticks(text: str) -> list[str]:
    return [token.strip().strip("`") for token in text.split(",") if token.strip()]


def contract_lists() -> tuple[list[str], list[str], list[str], list[str]]:
    text = DOC.read_text(encoding="utf-8")

    block = ENVELOPE_BLOCK.search(text)
    if block is None:
        raise SystemExit("contract.envelope: the request envelope block is gone from the doc")
    request_fields = [
        key for key in JSON_KEY.findall(block.group(1))
        if key not in {"uuid", "uuid-per-logical-action", "CHR_..."}
    ]

    response_match = RESPONSE_FIELDS.search(text)
    if response_match is None:
        raise SystemExit("contract.envelope: the response field sentence is gone from the doc")
    response_fields = strip_backticks(response_match.group(1))

    event_match = EVENT_FIELDS.search(text)
    if event_match is None:
        raise SystemExit("contract.events: the event field list is gone from the doc")
    event_fields = [name.split(":")[0].strip() for name in event_match.group(1).split(",")]

    error_match = CANONICAL_ERRORS.search(text)
    if error_match is None:
        raise SystemExit("contract.errors: the canonical error list is gone from the doc")
    canonical_errors = strip_backticks(error_match.group(1))

    return request_fields, response_fields, event_fields, canonical_errors


def walk_properties(node: object) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"properties", "required"} and isinstance(value, (dict, list)):
                found.update(value.keys() if isinstance(value, dict) else value)
            found.update(walk_properties(value))
    elif isinstance(node, list):
        for item in node:
            found.update(walk_properties(item))
    return found


def shipped_schema_fields() -> tuple[set[str], int]:
    names: set[str] = set()
    count = 0
    for path in sorted(WIRE_SCHEMA_DIR.glob("*.schema.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        count += 1
        names.update(walk_properties(document))
    return names, count


def shipped_error_codes() -> tuple[set[str], int]:
    codes: set[str] = set()
    files = 0
    for path in sorted(SERVER_DIR.rglob("*.cs")):
        found = ERROR_CONST.findall(path.read_text(encoding="utf-8", errors="replace"))
        if found:
            files += 1
            codes.update(found)
    return codes, files


def main() -> int:
    request_fields, response_fields, event_fields, canonical_errors = contract_lists()
    schema_fields, schema_count = shipped_schema_fields()
    shipped_errors, code_files = shipped_error_codes()
    doc_text = DOC.read_text(encoding="utf-8")

    print(f"contract doc: {DOC.relative_to(ROOT).as_posix()}")
    print(f"shipped wire schemas: {schema_count} from "
          f"{WIRE_SCHEMA_DIR.relative_to(ROOT).as_posix()}")
    print(f"doc lists: request envelope {len(request_fields)}, response envelope "
          f"{len(response_fields)}, event {len(event_fields)}, canonical errors "
          f"{len(canonical_errors)}")
    print(f"lowercase wire-code constants: {len(shipped_errors)} declared across "
          f"{code_files} files under {SERVER_DIR.relative_to(ROOT).as_posix()}")

    problems: list[str] = []
    for name, actual in (
        ("request_envelope", len(request_fields)),
        ("response_envelope", len(response_fields)),
        ("event_fields", len(event_fields)),
        ("canonical_errors", len(canonical_errors)),
        ("wire_schemas", schema_count),
    ):
        if actual != EXPECTED[name]:
            problems.append(f"{name} changed: {actual} (was {EXPECTED[name]})")
    if code_files == 0:
        problems.append("no wire-code constants found; the error comparison is meaningless")

    # The envelope. This server carries the wrapper fields on its own DTOs, so a doc field
    # that appears in no shipped schema is a field the contract and the wire disagree on.
    envelope = request_fields + response_fields
    absent = [name for name in envelope if name not in schema_fields]
    print(f"doc envelope fields absent from every shipped schema: {len(absent)} -> "
          f"{', '.join(absent) or 'none'}")

    events_present = [name for name in event_fields if name in schema_fields]
    print(f"doc event fields present in a shipped schema: {len(events_present)} of "
          f"{len(event_fields)}")

    # The error surface. The doc's canonical list is SCREAMING_SNAKE and the wire codes are
    # lowercase, so the match is case-insensitive by design; anything else is reported,
    # never averaged away.
    lowered_shipped = {code.lower() for code in shipped_errors}
    never_emitted = [code for code in canonical_errors if code.lower() not in lowered_shipped]
    mapped = [code for code in canonical_errors if code.lower() in lowered_shipped]
    print(f"canonical codes answered by a shipped wire code: {len(mapped)} of "
          f"{len(canonical_errors)} -> {', '.join(mapped) or 'none'}")
    print(f"canonical codes this server never emits: {len(never_emitted)} -> "
          f"{', '.join(never_emitted) or 'none'}")

    # Numbers the doc states that the running server cannot currently satisfy. These are
    # printed, not asserted, because the fix is an owner decision about persistence and
    # throttling, not a constant to update.
    retention = IDEMPOTENCY_RETENTION.search(doc_text)
    replay = REPLAY_BASELINE.search(doc_text)
    print(f"doc idempotency retention: "
          f"{'at least ' + retention.group(1) + ' days' if retention else 'NOT STATED'}")
    print(f"doc replay acceptance baseline: "
          f"{replay.group(1) + ' replayed idempotent commands' if replay else 'NOT STATED'}")
    print("server side: the idempotency ledgers are in-memory and bounded to 256 entries "
          "per character and are lost on restart, and no rate limiting exists on any "
          "endpoint, so both numbers above are unreachable today (section 5 and section 6 "
          "of the contract)")
    if RATE_LIMIT_SENTENCE in doc_text.lower() and not any(
        "ratelimit" in path.name.lower() or "rate_limit" in path.name.lower()
        for path in SERVER_DIR.rglob("*.cs")
    ):
        print("named gap: the contract requires per-account and per-IP rate limits; no "
              "server type or middleware carries that name")

    for line in problems:
        print(f"PROBLEM {line}")
    if problems:
        return 1
    print("OK: each list was read from the doc, the shipped surface from schemas and wire "
          "constants, and every divergence above is named")
    return 0


if __name__ == "__main__":
    sys.exit(main())
