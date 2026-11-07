#!/usr/bin/env python3
"""Reconcile `docs/production/Map_Production_Atlas_vi.md` against shipped map data.

Work order 29 Q3 states the art reboot must not move placements without a synchronised,
hashed bundle, and `Visual_Reboot_And_Muse_Scope_20261104_vi.md:34` assigns the
coordinate / nav-version reconciliation to this server. The atlas is the layout source:
section 3 (Ban Me) gives NPC positions, spawn centres, quest trigger positions,
escort checkpoints, the boss ring and the portal/respawn anchors as numbers.

This tool compares every one of those numbers to what the server actually loads
(`world_records.json`, `npc_anchors.json`) plus the approved alpha overlay
(`ben_mua_alpha_20261103.json`), and exits non-zero on any of:

  * a position that used to match and no longer does (a placement moved without the
    atlas moving, or the other way round),
  * a delta that is not in KNOWN_DELTAS below (an unreviewed disagreement),
  * a KNOWN_DELTAS entry that has stopped being true (someone fixed one side and the
    ledger of open conflicts is now a lie),
  * an atlas row with no runtime row at all (the layout names something nothing ships).

Nothing here changes a coordinate and nothing enforces a geometry: it only keeps two
documents telling the same story, so a decision about which one wins is visible.
"""

import json
import os
import re
import sys

ATLAS = "docs/production/Map_Production_Atlas_vi.md"
RECORDS = "Implementation/Content/Runtime/world_records.json"
ANCHORS = "Implementation/Content/Runtime/npc_anchors.json"
ALPHA = "Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json"
# Atlas heading -> the map whose shipped placements it describes. Section 3 is Ben Mua
# and section 4 Thanh Lac; both state positions as numbers, so both get reconciled.
SECTIONS = {"### 3.": "MAP_BEN_MUA", "### 4.": "MAP_THANH_LAC"}

# The alpha design owns these rows; the atlas is the older layout statement for them.
# Both numbers are kept here so closing one out has to edit this file deliberately.
# The atlas names these and nothing ships them yet: four portal/respawn points and the
# boss-ring seal. The portal route is a separate pending packet, so they are recorded as
# absent rather than ignored - the day a record appears, this list has to shrink on
# purpose and the position gets compared for real.
KNOWN_ABSENT = {
    "TP_BM_HUB": "no teleport/portal route exists (portal packet awaits approval)",
    "TP_BM_THANH_LAC": "no teleport/portal route exists (portal packet awaits approval)",
    "TP_BM_THANG_LONG": "no teleport/portal route exists (portal packet awaits approval)",
    "TP_BM_DAM_CHUONG": "no teleport/portal route exists (portal packet awaits approval)",
    "OBJ_BM_SEAL": "the ring seal is carried by the encounter, not by a world record",
}

# Thanh Lac disagrees with nothing today - 21 of its 30 atlas rows match the shipped
# records exactly - so it only needs the absence list: five portals, a respawn anchor and
# two trial rows the atlas places and nothing ships, each with the reason.
ABSENT_THANH_LAC = {
    "TP_TL_BEN_MUA": "no portal/teleport route exists (portal packet awaits approval)",
    "TP_TL_WEST": "no portal/teleport route exists (portal packet awaits approval)",
    "TP_TL_EAST": "no portal/teleport route exists (portal packet awaits approval)",
    "TP_TL_THANG_LONG": "no portal/teleport route exists (portal packet awaits approval)",
    "TP_TL_LAM_TRIEU": "no portal/teleport route exists (portal packet awaits approval)",
    "SP_TL": "the approved death-return anchor exists only for the private-alpha map",
    "SPAWN_TL_STATUES": "the statue trial ships as individual SPAWN_TL_* rows, not a group",
    "OBJ_TL_CONTROL_STAKE_A": "the C1-01 control stake is not in the shipped record set",
}

ABSENT_BY_MAP = {"MAP_BEN_MUA": KNOWN_ABSENT, "MAP_THANH_LAC": ABSENT_THANH_LAC}

# An id has to look like an id: without this, prose such as "A tai (154,0)/B (176,0)"
# contributes a row named "B" that nothing could ever ship.
ID = re.compile(r"[A-Z][A-Z0-9_]{3,}")

ALPHA_OVERLAY_ALIASES = {
    "OBJ_BM_WATER_RIPPLE_01": "ALPHA-BM-RIPPLE-01",
    "OBJ_BM_WATER_RIPPLE_02": "ALPHA-BM-RIPPLE-02",
    "OBJ_BM_WATER_RIPPLE_03": "ALPHA-BM-RIPPLE-03",
    "NPC_BM_RESCUE_01": "ALPHA-BM-VILLAGER-01",
    "NPC_BM_RESCUE_02": "ALPHA-BM-VILLAGER-02",
}

KNOWN_DELTAS = {
    # atlas (Map_Production_Atlas sec 3) vs DESIGN-BM-ALPHA-20261103/newOverlayRecords
    "OBJ_BM_WATER_RIPPLE_01": ((122, -1), (70, 3)),
    "OBJ_BM_WATER_RIPPLE_02": ((132, -1), (86, -3)),
    "OBJ_BM_WATER_RIPPLE_03": ((142, -1), (104, 3)),
    "NPC_BM_RESCUE_01": ((135, 0), (138, 3)),
    "NPC_BM_RESCUE_02": ((148, 0), (146, 3)),
    # atlas respawn anchor vs DEC-DEATH-RETURN-20261105 safeAnchorWu (appsettings SpawnX18)
    "SP_BM": ((24, 0), (18, 0)),
}

PAIR = r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)"


def atlas_section(root, heading):
    text = open(os.path.join(root, ATLAS), encoding="utf-8").read()
    start = text.index(heading)
    rest = text[start + len(heading):]
    cut = rest.find("\n### ")
    return rest if cut < 0 else rest[:cut]


def parse_positions(section):
    """Every `ID ... (x,y)` the section states, keyed by the id the runtime uses."""
    found = {}

    # Table rows: | NPC_LYAN | (42,0) | ... |  and  | SPAWN_BM_01 | (84,0) | ...
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and ID.fullmatch(cells[0] or ""):
            match = re.fullmatch(PAIR, cells[1])
            if match:
                found[cells[0]] = (int(match.group(1)), int(match.group(2)))

    # Prose rows: "OBJ_BM_PACKAGE_01/02/03 tai (36,0)/(44,0)/(52,0)" and
    # "NPC_BM_RESCUE_01=(135,0), TP_BM_HUB=(24,0), hoi sinh SP_BM=(24,0)".
    for stem, first, tail, coordinates in re.findall(
            r"([A-Z][A-Z0-9_]*?)_(\d{2})((?:/\d{2})*)\s+t\u1ea1i\s+((?:\(-?\d+,-?\d+\)\s*/?\s*)+)",
            section):
        pairs = re.findall(PAIR, coordinates)
        for index, pair in enumerate(pairs):
            found[f"{stem}_{int(first) + index:02d}"] = (int(pair[0]), int(pair[1]))

    for npc_id, anchor_x, anchor_y in re.findall(rf"({ID.pattern})=\s*{PAIR}", section):
        found.setdefault(npc_id, (int(anchor_x), int(anchor_y)))

    return found


def runtime_positions(root, map_id):
    positions = {}
    records = json.load(open(os.path.join(root, RECORDS), encoding="utf-8"))["records"]
    for record in records:
        if record.get("mapId") != map_id:
            continue
        # `MAN-BM-OBJ_BM_PACKAGE_01` - the manifest prefix is two segments.
        positions[record["recordId"].split("-", 2)[2]] = (
            int(record["xWu"]), int(record["yWu"]))
    alpha = json.load(open(os.path.join(root, ALPHA), encoding="utf-8"))
    if map_id == "MAP_BEN_MUA":
        # The alpha overlay only ever adds Ben Mua records, and the approved
        # death-return anchor is a Ben Mua rule; both are compared on that map alone.
        for record in alpha["newOverlayRecords"]:
            positions[record["recordId"]] = (int(record["xWu"]), int(record["yWu"]))
        positions["SP_BM"] = tuple(int(value) for value in
                                  alpha["deathReturn"]["safeAnchorWu"])
    for anchor in json.load(open(os.path.join(root, ANCHORS), encoding="utf-8"))["anchors"]:
        if anchor.get("mapId") == map_id and anchor.get("npcId"):
            positions.setdefault(anchor["npcId"],
                                 (int(anchor["xWu"]), int(anchor["yWu"])))
    return positions


def reconcile(atlas_positions, runtime, absent_allowed):
    """One map's verdict: the five buckets the report is printed from."""
    missing, agreements, deltas, surprises, absent = [], [], [], [], []
    for atlas_id, atlas_position in sorted(atlas_positions.items()):
        overlay_id = ALPHA_OVERLAY_ALIASES.get(atlas_id, atlas_id)
        if overlay_id not in runtime:
            prefixed = [key for key in runtime if key.startswith(f"{overlay_id}_")]
            if len(prefixed) == 1:
                # `SPAWN_BM_05` ships as `SPAWN_BM_05_QUEST`; a suffixed twin is the
                # manifest's way of naming the quest-scoped instance of the same point.
                overlay_id = prefixed[0]
        if overlay_id not in runtime:
            if atlas_id in absent_allowed:
                absent.append(atlas_id)
            else:
                missing.append((atlas_id, atlas_position))
            continue
        runtime_position = runtime[overlay_id]
        if atlas_position == runtime_position:
            agreements.append(atlas_id)
            continue
        known = KNOWN_DELTAS.get(atlas_id)
        if known == (atlas_position, runtime_position):
            deltas.append(atlas_id)
        else:
            surprises.append((atlas_id, atlas_position, runtime_position, known))
    return missing, agreements, deltas, surprises, absent


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    totals = {"rows": 0, "agree": 0, "delta": 0, "absent": 0}
    problems = []
    for heading, map_id in sorted(SECTIONS.items()):
        atlas_positions = parse_positions(atlas_section(root, heading))
        runtime = runtime_positions(root, map_id)
        missing, agreements, deltas, surprises, absent = reconcile(
            atlas_positions, runtime, ABSENT_BY_MAP[map_id])

        # A listed entry that stopped being true is as much a signal as a new delta:
        # either the sources were brought together (delete the entry) or one side moved.
        stale = [key for key in KNOWN_DELTAS
                 if key in atlas_positions and key not in deltas]
        new_absent = [key for key in ABSENT_BY_MAP[map_id]
                      if key in atlas_positions and key not in absent]

        for atlas_id, position in missing:
            problems.append(f"{map_id} MISSING {atlas_id} at {position} - the atlas "
                            "names it, no shipped record carries it")
        for atlas_id, atlas_position, runtime_position, known in surprises:
            problems.append(f"{map_id} UNREVIEWED {atlas_id}: atlas={atlas_position} "
                            f"runtime={runtime_position} allowed={known}")
        for atlas_id in stale:
            problems.append(f"{map_id} RESOLVED {atlas_id}: the allowed delta no longer "
                            "matches - the entry must be deleted deliberately")
        for atlas_id in new_absent:
            problems.append(f"{map_id} ARRIVED {atlas_id}: listed as not shipping, but a "
                            "record exists now - compare it and delete the entry")
        for atlas_id in deltas:
            print(f"  DELTA     {map_id} {atlas_id}: atlas={atlas_positions[atlas_id]} "
                  f"runtime={runtime[ALPHA_OVERLAY_ALIASES.get(atlas_id, atlas_id)]}")

        totals["rows"] += len(atlas_positions)
        totals["agree"] += len(agreements)
        totals["delta"] += len(deltas)
        totals["absent"] += len(absent)

    print(f"atlas rows={totals['rows']} agree={totals['agree']} "
          f"known_deltas={totals['delta']} listed_absent={totals['absent']} "
          f"problems={len(problems)}")
    for line in problems:
        print(f"  {line}")
    if problems:
        print("FAIL: atlas/runtime reconciliation is not the reviewed state")
        return 1
    print("OK: every atlas position either matches the shipped data, is a listed "
          "reviewed delta, or is a listed feature that does not exist yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
