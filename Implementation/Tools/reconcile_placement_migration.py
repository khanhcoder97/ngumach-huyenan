"""Reconcile the TOP-DOWN placement migration artifact against the source manifest and
the world records the server actually loads (work order 31 Q6, navigation 349-anchor
delta).

`Implementation/Reports/TopDown_Placement_Migration_20261028.json` was produced by DEC-016
and no code in this repository reads it - which is how a 349-row artifact ends up
describing a migration nobody can see the state of. This tool makes that state a
measured line instead of a rumour:

  * the artifact and `docs/production/World_Spawn_Gathering_Manifest_vi.csv` must cover the
    same record ids, and each artifact `originalXY` must equal the manifest `x_wu`/`y_wu`
    (the artifact claims to be derived from that file, so a divergence means one of the two
    was edited alone);
  * how many rows have actually been reviewed - `reviewState` and a non-null `approvedXY` -
    because "the delta" only exists once an approval is recorded;
  * for the rows whose map the server ships, the shipped runtime position must equal the
    manifest, which is the part a client can be built against today.

Exit code is non-zero on a divergence in the first and third bullets. The second is a
count, not a failure: an un-reviewed migration is a status, and inventing approved
coordinates to make the number look better is exactly what this file must not do.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "Implementation/Reports/TopDown_Placement_Migration_20261028.json"
MANIFEST = ROOT / "docs/production/World_Spawn_Gathering_Manifest_vi.csv"
WORLD_RECORDS = ROOT / "Implementation/Content/Runtime/world_records.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    artifact = read_json(ARTIFACT)
    records = artifact["records"]
    with io.open(MANIFEST, encoding="utf-8-sig", newline="") as handle:
        manifest = {row["record_id"]: row for row in csv.DictReader(handle)}
    shipped = read_json(WORLD_RECORDS)

    positions: dict[str, tuple[str, str]] = {}
    for entry in shipped.get("records", shipped if isinstance(shipped, list) else []):
        record_id = entry.get("recordId") or entry.get("id")
        if record_id:
            positions[record_id] = (str(entry.get("xWu")), str(entry.get("yWu")))

    problems: list[str] = []

    missing = [r["recordId"] for r in records if r["recordId"] not in manifest]
    extra = sorted(set(manifest) - {r["recordId"] for r in records})
    if missing:
        problems.append(f"artifact ids not in manifest: {missing[:5]} ({len(missing)})")
    if extra:
        problems.append(f"manifest ids not in artifact: {extra[:5]} ({len(extra)})")

    derive_mismatch = []
    for row in records:
        source = manifest.get(row["recordId"])
        if source is None:
            continue
        # The manifest is the source the artifact cites, so originalXY must be its
        # x_wu/y_wu. Compared against the wrong columns earlier today, this check would
        # have reported all 349 rows as mismatched - a harness bug, not a data finding.
        if [source["x_wu"].strip(), source["y_wu"].strip()] != [
            str(v).strip() for v in row["originalXY"]
        ]:
            derive_mismatch.append(
                f'{row["recordId"]} artifact={row["originalXY"]} '
                f'manifest={[source["x_wu"], source["y_wu"]]}'
            )
    if derive_mismatch:
        problems.append(
            f"artifact does not match the manifest it cites: {derive_mismatch[:5]} "
            f"({len(derive_mismatch)})"
        )

    states: dict[str, int] = {}
    for row in records:
        states[row["reviewState"]] = states.get(row["reviewState"], 0) + 1
    approved = sum(1 for row in records if row.get("approvedXY"))

    shipped_on_map = [
        row for row in records
        if row["recordId"] in positions
    ]
    position_conflicts = []

    def same(first: str, second: str) -> bool:
        # Positions are numbers, and one file writes "42" while the other writes "42.0".
        # Compared as text every row looked migrated wrong; the first run of this tool
        # reported 349 conflicts that were really 0. Compare the numbers, and fall back
        # to text only for something that is not a number at all.
        try:
            return float(first) == float(second)
        except (TypeError, ValueError):
            return str(first).strip() == str(second).strip()

    for row in shipped_on_map:
        shipped_xy = positions[row["recordId"]]
        chosen = (
            [str(v).strip() for v in row["approvedXY"]]
            if row.get("approvedXY")
            else [str(v).strip() for v in row["originalXY"]]
        )
        if not (same(shipped_xy[0], chosen[0]) and same(shipped_xy[1], chosen[1])):
            position_conflicts.append(
                f'{row["recordId"]} runtime={shipped_xy} artifact={chosen}'
            )
    if position_conflicts:
        problems.append(
            f"server loads positions the migration does not state: "
            f"{position_conflicts[:5]} ({len(position_conflicts)})"
        )

    print(f"artifact: {ARTIFACT.relative_to(ROOT).as_posix()} "
          f"records={len(records)} decision={artifact.get('decision')}")
    print(f"manifest: {MANIFEST.relative_to(ROOT).as_posix()} rows={len(manifest)}")
    print(f"reviewState distribution: "
          f"{', '.join(f'{k}={v}' for k, v in sorted(states.items()))}")
    print(f"rows with a recorded approvedXY: {approved} of {len(records)}")
    print(f"maps covered: {len({row['mapId'] for row in records})}; rows whose recordId "
          f"is in the shipped world records: {len(shipped_on_map)}")
    print(f"runtime position conflicts: {len(position_conflicts)}")

    if problems:
        for problem in problems:
            print(f"PROBLEM: {problem}")
        return 1
    print("OK: the migration artifact is derived from the manifest it cites, the server "
          "loads positions the migration states, and the un-reviewed count is reported "
          "rather than filled in.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
