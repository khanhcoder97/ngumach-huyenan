#!/usr/bin/env python3
"""Validate MapTopology bundles against the map registry and spawn manifest.

Checks per bundle: registry bounds match, floor references, polygon geometry
(>=3 finite points, inside bounds, non-self-intersecting), and placement
recordId/npcId/map/floor/position consistency with the canonical manifest.

Usage:
  python validate_topology.py [--dir Implementation/Content/Examples/MapTopology]

Exit codes: 0 valid, 1 validation failures, 2 environment/usage error.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

DEFAULT_DIR = Path("Implementation/Content/Examples/MapTopology")
MAP_BOUNDS = Path("Implementation/Content/map_bounds.json")
MANIFEST = Path("docs/production/World_Spawn_Gathering_Manifest_vi.csv")
SUPPORTED_BUNDLE_VERSION = 2


def fail_environment(message):
    print(f"ENVIRONMENT: {message}", file=sys.stderr)
    sys.exit(2)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail_environment(f"{path}: cannot read JSON ({exc})")


def bounds_for(map_id, config):
    override = (config.get("overrides") or {}).get(map_id)
    return override or config.get("defaultBounds")


def cross(ax, ay, bx, by):
    return (ax * by) - (ay * bx)


def orientation(a, b, c):
    return cross(b[0] - a[0], b[1] - a[1], c[0] - a[0], c[1] - a[1])


def on_segment(a, b, p):
    if orientation(a, b, p) != 0:
        return False
    return (
        min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
        and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])
    )


def segments_intersect(a1, a2, b1, b2):
    d1 = orientation(b1, b2, a1)
    d2 = orientation(b1, b2, a2)
    d3 = orientation(a1, a2, b1)
    d4 = orientation(a1, a2, b2)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True

    if d1 == 0 and on_segment(b1, b2, a1):
        return True
    if d2 == 0 and on_segment(b1, b2, a2):
        return True
    if d3 == 0 and on_segment(a1, a2, b1):
        return True
    if d4 == 0 and on_segment(a1, a2, b2):
        return True

    return False


def polygon_self_intersects(points):
    count = len(points)
    for i in range(count):
        a1 = points[i]
        a2 = points[(i + 1) % count]
        for j in range(i + 2, count):
            if i == 0 and j == count - 1:
                continue
            b1 = points[j]
            b2 = points[(j + 1) % count]
            if segments_intersect(a1, a2, b1, b2):
                return True
    return False


def check_polygon(label, polygon, floor_ids, bounds, errors):
    floor_id = polygon.get("floorId")
    points_raw = polygon.get("points")
    if floor_id not in floor_ids:
        errors.append(f"{label}: floorId '{floor_id}' is not declared in floorIds")
        return
    if not isinstance(points_raw, list) or len(points_raw) < 3:
        errors.append(f"{label}: needs at least 3 points")
        return

    points = []
    for index, point in enumerate(points_raw):
        x = point.get("xWu")
        y = point.get("yWu")
        if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x):
            errors.append(f"{label}.points[{index}].xWu is not finite")
            return
        if not isinstance(y, (int, float)) or isinstance(y, bool) or not math.isfinite(y):
            errors.append(f"{label}.points[{index}].yWu is not finite")
            return
        if not (
            bounds["xMin"] <= x <= bounds["xMax"]
            and bounds["yMin"] <= y <= bounds["yMax"]
        ):
            errors.append(f"{label}.points[{index}] ({x},{y}) is outside map bounds")
            return
        points.append((float(x), float(y)))

    if polygon_self_intersects(points):
        errors.append(f"{label}: polygon self-intersects")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()

    if not MAP_BOUNDS.is_file():
        fail_environment(f"{MAP_BOUNDS} not found")
    if not MANIFEST.is_file():
        fail_environment(f"{MANIFEST} not found")
    if not args.dir.is_dir():
        fail_environment(f"{args.dir} not found")

    map_config = load_json(MAP_BOUNDS)
    manifest_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig", newline="")))
    records = {
        (row.get("record_id") or "").strip(): row
        for row in manifest_rows
        if (row.get("record_id") or "").strip()
    }

    paths = sorted(args.dir.glob("*.json"))
    if not paths:
        fail_environment(f"{args.dir}: no topology bundles found")

    errors = []
    reviewed = 0
    synthetic = 0
    for path in paths:
        bundle = load_json(path)
        label = f"MapTopology/{path.name}"

        if bundle.get("schemaVersion") != 1:
            errors.append(f"{label}: unsupported schemaVersion")
            continue
        if bundle.get("coordinateSystem") != "TOP_DOWN_XY":
            errors.append(f"{label}: coordinateSystem must be TOP_DOWN_XY")
        if bundle.get("bundleVersion") != SUPPORTED_BUNDLE_VERSION:
            errors.append(
                f"{label}: bundleVersion {bundle.get('bundleVersion')} is not "
                f"{SUPPORTED_BUNDLE_VERSION}"
            )

        review_state = bundle.get("reviewState")
        if review_state == "REVIEWED":
            reviewed += 1
        elif review_state == "SYNTHETIC_TEST_ONLY":
            synthetic += 1
        else:
            errors.append(f"{label}: reviewState '{review_state}' is invalid")

        map_id = bundle.get("mapId")
        bundle_bounds = bundle.get("bounds") or {}
        registry_bounds = bounds_for(map_id, map_config)
        if registry_bounds is None:
            errors.append(f"{label}: mapId '{map_id}' has no registry bounds")
            continue

        for key in ("xMin", "xMax", "yMin", "yMax"):
            if bundle_bounds.get(key) != registry_bounds.get(key):
                errors.append(
                    f"{label}: bounds.{key}={bundle_bounds.get(key)} does not match "
                    f"registry {registry_bounds.get(key)}"
                )
                break

        floor_ids = bundle.get("floorIds") or []
        if not floor_ids:
            errors.append(f"{label}: floorIds must not be empty")
        if len(floor_ids) != len(set(floor_ids)):
            errors.append(f"{label}: floorIds contains duplicates")

        walkable = bundle.get("walkablePolygons") or []
        blocked = bundle.get("blockedPolygons") or []
        if not walkable:
            errors.append(f"{label}: walkablePolygons must not be empty")

        for index, polygon in enumerate(walkable):
            check_polygon(
                f"{label}.walkablePolygons[{index}]", polygon, floor_ids,
                registry_bounds, errors)
        for index, polygon in enumerate(blocked):
            check_polygon(
                f"{label}.blockedPolygons[{index}]", polygon, floor_ids,
                registry_bounds, errors)

        seen_placements = set()
        for index, placement in enumerate(bundle.get("placements") or []):
            plabel = f"{label}.placements[{index}]"
            record_id = placement.get("recordId")
            npc_id = placement.get("npcId")
            floor_id = placement.get("floorId")
            x = placement.get("xWu")
            y = placement.get("yWu")

            record = records.get(record_id)
            if record is None:
                errors.append(f"{plabel}: recordId '{record_id}' is not in the manifest")
                continue
            if (record.get("record_type") or "").strip() != "NPC":
                errors.append(f"{plabel}: recordId '{record_id}' is not an NPC row")
            if (record.get("entity_id") or "").strip() != npc_id:
                errors.append(
                    f"{plabel}: npcId '{npc_id}' does not match manifest "
                    f"entity '{record.get('entity_id')}'"
                )
            if (record.get("map_id") or "").strip() != map_id:
                errors.append(
                    f"{plabel}: record map '{record.get('map_id')}' does not match "
                    f"bundle map '{map_id}'"
                )
            if floor_id not in floor_ids:
                errors.append(f"{plabel}: floorId '{floor_id}' is not declared")
            if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) \
                    or not isinstance(y, (int, float)) or isinstance(y, bool) \
                    or not math.isfinite(y):
                errors.append(f"{plabel}: xWu/yWu are not finite")
                continue
            if not (
                registry_bounds["xMin"] <= x <= registry_bounds["xMax"]
                and registry_bounds["yMin"] <= y <= registry_bounds["yMax"]
            ):
                errors.append(f"{plabel}: ({x},{y}) is outside map bounds")

            key = (npc_id, floor_id)
            if key in seen_placements:
                errors.append(f"{plabel}: duplicate placement for {npc_id} on {floor_id}")
            seen_placements.add(key)

        if not bundle.get("sourceRefs"):
            errors.append(f"{label}: sourceRefs must not be empty")

    if errors:
        print(f"FAILED: {len(errors)} problem(s) found:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Bundles: {len(paths)} (reviewed={reviewed}, synthetic={synthetic})")
    print(f"OK: all {len(paths)} topology bundle(s) passed validation.")


if __name__ == "__main__":
    main()
