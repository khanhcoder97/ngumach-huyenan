#!/usr/bin/env python3
"""Build the runtime NPC anchor registry from the canonical spawn manifest.

Source of truth: docs/production/World_Spawn_Gathering_Manifest_vi.csv (record_type NPC).
Output: Implementation/Content/Runtime/npc_anchors.json

Every (npcId, mapId) pair must be unique and inside that map's bounds.
Floor is OVERWORLD for P1 (DEC-016); no other floor exists yet.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

MANIFEST = Path("docs/production/World_Spawn_Gathering_Manifest_vi.csv")
MAP_BOUNDS = Path("Implementation/Content/map_bounds.json")
OUTPUT = Path("Implementation/Content/Runtime/npc_anchors.json")
FLOOR_ID = "OVERWORLD"


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def bounds_for(map_id, config):
    override = (config.get("overrides") or {}).get(map_id)
    return override or config.get("defaultBounds") or {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--map-bounds", type=Path, default=MAP_BOUNDS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not args.manifest.is_file():
        fail(f"{args.manifest} not found")
    if not args.map_bounds.is_file():
        fail(f"{args.map_bounds} not found")

    map_config = json.loads(args.map_bounds.read_text(encoding="utf-8"))

    with args.manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    anchors = {}
    for row in rows:
        if (row.get("record_type") or "").strip() != "NPC":
            continue

        record_id = (row.get("record_id") or "").strip()
        npc_id = (row.get("entity_id") or "").strip()
        map_id = (row.get("map_id") or "").strip()
        if not npc_id.startswith("NPC_"):
            fail(f"{record_id}: entity_id '{npc_id}' is not an NPC ID")
        if not map_id.startswith("MAP_"):
            fail(f"{record_id}: map_id '{map_id}' is invalid")

        try:
            x_wu = float((row.get("x_wu") or "").strip())
            y_wu = float((row.get("y_wu") or "").strip())
        except ValueError:
            fail(f"{record_id}: x_wu/y_wu are not numeric")

        if not (math.isfinite(x_wu) and math.isfinite(y_wu)):
            fail(f"{record_id}: x_wu/y_wu are not finite")

        bounds = bounds_for(map_id, map_config)
        if not bounds:
            fail(f"{map_id}: no bounds entry")

        if not (
            bounds["xMin"] <= x_wu <= bounds["xMax"]
            and bounds["yMin"] <= y_wu <= bounds["yMax"]
        ):
            fail(f"{record_id}: ({x_wu}, {y_wu}) outside {map_id} bounds")

        key = (npc_id, map_id)
        if key in anchors:
            fail(f"{record_id}: duplicate anchor for {npc_id} on {map_id}")

        anchors[key] = {
            "npcId": npc_id,
            "mapId": map_id,
            "xWu": x_wu,
            "yWu": y_wu,
            "floorId": FLOOR_ID,
            "sourceRecordId": record_id,
        }

    if not anchors:
        fail("no NPC rows found in manifest")

    payload = {
        "schemaVersion": 1,
        "sourceRef": "docs/production/World_Spawn_Gathering_Manifest_vi.csv",
        "floorRule": "DEC-016: P1 ground floor is OVERWORLD only",
        "anchors": [anchors[key] for key in sorted(anchors)],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"OK: wrote {len(anchors)} anchors to {args.output}")


if __name__ == "__main__":
    main()
