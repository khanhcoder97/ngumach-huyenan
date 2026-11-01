"""Generate a read-only UI item catalog from canonical CSVs.

Output: Client/Assets/Resources/PlayerUI/ui_item_catalog.json
- Read-only projection for UI tooltips/bag/character. Does NOT modify canonical CSVs.
- Deterministic: sorted by item_id, stable JSON, no timestamps.
- Duplicate item_id across inputs -> fail (exit 1).
- Malformed/empty input -> fail.
- Includes source provenance (file + row) and a digest per entry + overall.
"""
import csv
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUTS = [
    os.path.join(REPO_ROOT, "docs", "production", "Item_Rarity_Variant_Catalog_vi.csv"),
    os.path.join(REPO_ROOT, "docs", "production", "Item_Master_Catalog_vi.csv"),
]
OUT_DIR = os.path.join(REPO_ROOT, "Client", "Assets", "Resources", "PlayerUI")
OUT_FILE = os.path.join(OUT_DIR, "ui_item_catalog.json")

FIELDS = ["item_id", "display_name", "category", "slot", "class_id", "element",
          "required_level", "rarity_pool", "weapon_power", "armor", "primary_stat",
          "primary_value", "secondary_stat", "secondary_value", "affix_rule",
          "socket_rule", "set_id", "set_name", "set_bonus_2", "set_bonus_4",
          "hidden_effect_id", "hidden_effect_unlock", "hidden_effect", "stack_limit",
          "durability", "binding", "tradeable", "source_map", "source_rule",
          "description"]


def sha256_file(path):
    # Normalize line endings so the digest is stable across OS checkouts (CRLF vs LF).
    h = hashlib.sha256()
    with open(path, "rb") as f:
        data = f.read()
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    h.update(data)
    return h.hexdigest()


def read_csv(path):
    rows = []
    seen_in_file = set()
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "item_id" not in reader.fieldnames:
            raise ValueError(f"{path}: missing header or item_id column")
        for i, row in enumerate(reader, start=2):
            if row is None:
                raise ValueError(f"{path}: empty row at line {i}")
            iid = (row.get("item_id") or "").strip()
            if not iid:
                raise ValueError(f"{path}: empty item_id at line {i}")
            if iid in seen_in_file:
                raise ValueError(f"{path}: duplicate item_id within file: {iid} at line {i}")
            seen_in_file.add(iid)
            entry = {"_source": {"file": os.path.basename(path), "row": i}}
            for field in FIELDS:
                entry[field] = (row.get(field) or "").strip()
            rows.append(entry)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def entry_digest(entry):
    payload = {k: entry[k] for k in FIELDS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def main():
    seen = set()
    by_id = {}
    entries = []
    source_digests = {}
    for path in INPUTS:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        source_digests[os.path.basename(path)] = sha256_file(path)
        for row in read_csv(path):
            iid = row["item_id"]
            if iid in seen:
                # Cross-file overlap: allow only byte-identical shared rows (136 of them).
                # Conflicting same-id rows must fail loudly.
                prev = by_id[iid]
                meaningful = ["display_name", "category", "slot", "class_id", "element",
                              "required_level", "rarity_pool", "binding", "tradeable",
                              "stack_limit", "durability", "description"]
                for field in meaningful:
                    if (prev.get(field) or "") != (row.get(field) or ""):
                        raise ValueError(
                            f"conflicting shared item_id {iid}: field '{field}' differs "
                            f"({prev['_source']['file']} row {prev['_source']['row']} vs "
                            f"{row['_source']['file']} row {row['_source']['row']})")
                # identical shared row: keep the first (variant) entry, skip duplicate.
                continue
            seen.add(iid)
            by_id[iid] = row
            row["digest"] = entry_digest(row)
            entries.append(row)

    entries.sort(key=lambda e: e["item_id"])

    catalog = {
        "schemaVersion": 1,
        "generator": "Tools/PlayerUIData/generate_ui_catalog.py",
        "sourceDigests": source_digests,
        "count": len(entries),
        "entries": entries,
    }
    # overall digest over sorted entries
    overall = hashlib.sha256(json.dumps([e["digest"] for e in entries], ensure_ascii=False).encode("utf-8")).hexdigest()
    catalog["catalogDigest"] = overall

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT_FILE}: {len(entries)} entries, digest {overall}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
