#!/usr/bin/env python3
"""OPC-09: Pack a Muse asset bundle with allowlist gating (standard library only).

Reads an asset delivery manifest and assembles a deterministic bundle into a
fresh output directory. By default runs in dry-run mode (no files written);
use --output to materialise the bundle.

Gating rules:
  * fail on missing/deprecated references
  * fail on assets with insufficient metadata
  * draft-status assets are only allowed when --allow-draft is passed; they
    produce a bundle marked 'draft' with a prominent warning
  * allowlist of paths controls which assets may be included

Usage (from the repository root):
    python Tools/AssetPack/pack_bundle.py \
        --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
        --allowlist Tools/AssetPack/allowlist.txt \
        --dry-run

    python Tools/AssetPack/pack_bundle.py \
        --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
        --allowlist Tools/AssetPack/allowlist.txt \
        --output Tools/AssetPack/bundle_out --allow-draft

Exit codes:
    0  pack/dry-run succeeded
    1  environment / usage error
    2  validation failure (missing/deprecated/insufficient metadata)

Refs #40, OPC-09. Not self-merging.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
DEFAULT_ALLOWLIST = "Tools/AssetPack/allowlist.txt"

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
PATH_CHARS_RE = re.compile(r"^[A-Za-z0-9._~/-]+$")

ART_ROOTS = (
    "Client/Assets/Art",
    "Client/Assets/UI/Art",
    "Client/Assets/Tilemaps",
    "Client/Assets/VFX",
    "Client/Assets/Animation",
)

REQUIRED_META_FIELDS = ("assetId", "path", "kind", "status", "pixelWidth",
                        "pixelHeight", "pixelsPerUnit", "previewPath")

EXIT_OK = 0
EXIT_ENVIRONMENT = 1
EXIT_VALIDATION = 2


class BundlePackError(Exception):
    """Raised for environment or usage problems."""


def load_json(path: Path):
    if not path.is_file():
        raise BundlePackError(f"file not found: {path}")
    raw = path.read_bytes()
    if raw.startswith(LFS_POINTER_PREFIX):
        raise BundlePackError(
            f"{path}: Git LFS pointer instead of file content "
            "(fetch the LFS objects, in CI use actions/checkout with lfs: true)"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundlePackError(f"{path}: not valid UTF-8 ({exc})") from exc
    try:
        return json.loads(text)
    except ValueError as exc:
        raise BundlePackError(f"{path}: invalid JSON ({exc})") from exc


def inspect_repo_path(value):
    if not isinstance(value, str) or not value:
        return None, "must be a non-empty string"
    if "\\" in value:
        return None, "must use forward slashes"
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return None, "must be relative to the repository root, not absolute"
    if not PATH_CHARS_RE.match(value):
        return None, "must only use ASCII letters, digits, dot, dash, underscore and slash"
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return None, "must not contain '.', '..' or empty segments"
    return "/".join(parts), None


def resolve_inside_root(root: Path, rel: str):
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def under_art_root(rel: str) -> bool:
    return any(rel == root or rel.startswith(root + "/") for root in ART_ROOTS)


def sha256_of_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_allowlist(path: Path):
    """Return a set of normalised repo-relative paths from the allowlist file."""
    if not path.is_file():
        return None  # no allowlist = all paths allowed
    allowed = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        rel = line.strip().replace("\\", "/")
        if not rel or rel.startswith("#"):
            continue
        allowed.add(rel)
    return allowed


def check_metadata(asset: dict, findings: list) -> bool:
    """Return True if the asset carries sufficient metadata for packing."""
    ok = True
    for field in REQUIRED_META_FIELDS:
        if field not in asset or asset[field] is None or asset[field] == "":
            findings.append(f"missing required metadata field: {field}")
            ok = False
    asset_id = asset.get("assetId")
    if not isinstance(asset_id, str) or not re.match(r"^[A-Z0-9_]+$", asset_id or ""):
        findings.append("assetId must match ^[A-Z0-9_]+$")
        ok = False
    kind = asset.get("kind")
    allowed_kinds = ("sprite", "sprite_sheet", "tileset", "tilemap", "ui_texture",
                     "vfx_sheet", "animation", "icon")
    if kind not in allowed_kinds:
        findings.append(f"kind must be one of {allowed_kinds}")
        ok = False
    status = asset.get("status")
    if status not in ("draft", "approved", "deprecated"):
        findings.append("status must be one of draft/approved/deprecated")
        ok = False
    ppu = asset.get("pixelsPerUnit")
    if ppu != 20:
        findings.append("pixelsPerUnit must equal 20")
        ok = False
    return ok


def pack_bundle(manifest: dict, root: Path, manifest_rel: str,
                allowlist, allow_draft: bool, dry_run: bool, output_dir: Path):
    """Validate and (optionally) materialise the bundle. Returns a report dict."""
    assets = manifest.get("assets") or []
    errors = []
    warnings = []
    included = []
    skipped = []

    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"assets[{index}]: asset entry is not an object")
            continue
        label = asset.get("assetId") or f"assets[{index}]"
        raw_path = asset.get("path")
        rel, path_problem = inspect_repo_path(raw_path)

        # Metadata sufficiency check.
        findings = []
        metadata_ok = check_metadata(asset, findings)
        if not metadata_ok:
            errors.append(f"{label}: " + "; ".join(findings))
            skipped.append({"assetId": label, "reason": "insufficient metadata",
                            "findings": findings})
            continue

        # Status gating.
        status = asset.get("status")
        if status == "deprecated":
            errors.append(f"{label}: status is 'deprecated', cannot be packed")
            skipped.append({"assetId": label, "reason": "deprecated"})
            continue
        if status == "draft" and not allow_draft:
            errors.append(f"{label}: status is 'draft'; pass --allow-draft to include")
            skipped.append({"assetId": label, "reason": "draft (blocked)"})
            continue

        # Allowlist gating.
        if rel is None:
            errors.append(f"{label}: path problem: {path_problem}")
            skipped.append({"assetId": label, "reason": "invalid path",
                            "problem": path_problem})
            continue
        if allowlist is not None and rel not in allowlist:
            errors.append(f"{label}: path '{rel}' is not on the allowlist")
            skipped.append({"assetId": label, "reason": "not on allowlist"})
            continue

        # Art root check.
        if not under_art_root(rel):
            errors.append(f"{label}: path '{rel}' is outside agreed art roots")
            skipped.append({"assetId": label, "reason": "outside art root"})
            continue

        target = resolve_inside_root(root, rel)
        if target is None:
            errors.append(f"{label}: path '{rel}' escapes the repository root")
            skipped.append({"assetId": label, "reason": "escapes repository root"})
            continue
        if not target.is_file():
            errors.append(f"{label}: declared file does not exist: {rel}")
            skipped.append({"assetId": label, "reason": "file missing", "path": rel})
            continue

        # LFS pointer check.
        head = target.read_bytes()[: len(LFS_POINTER_PREFIX)]
        if head == LFS_POINTER_PREFIX:
            errors.append(f"{label}: '{rel}' is a Git LFS pointer; fetch LFS objects first")
            skipped.append({"assetId": label, "reason": "lfs pointer", "path": rel})
            continue

        size = target.stat().st_size
        digest = sha256_of_file(target)

        entry = {
            "assetId": label,
            "kind": asset.get("kind"),
            "status": status,
            "path": rel,
            "sizeBytes": size,
            "sha256": digest,
            "previewPath": asset.get("previewPath"),
            "pixelsPerUnit": asset.get("pixelsPerUnit"),
            "pixelWidth": asset.get("pixelWidth"),
            "pixelHeight": asset.get("pixelHeight"),
        }
        included.append(entry)

        if not dry_run:
            dst = output_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dst)

    # Materialise manifest copy into bundle output.
    if not dry_run and included:
        manifest_dst = output_dir / manifest_rel
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / manifest_rel, manifest_dst)
        # Write a bundle manifest with pack metadata.
        bundle_manifest = {
            "packedAt": datetime.now(timezone.utc).isoformat(),
            "sourceManifest": manifest_rel,
            "assetPackId": manifest.get("assetPackId"),
            "assetPackVersion": manifest.get("assetPackVersion"),
            "draft": bool(allow_draft and any(a.get("status") == "draft" for a in assets)),
            "assets": included,
        }
        (output_dir / "bundle-manifest.json").write_text(
            json.dumps(bundle_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "manifest": manifest_rel,
        "assetPackId": manifest.get("assetPackId"),
        "assetPackVersion": manifest.get("assetPackVersion"),
        "dryRun": dry_run,
        "allowDraft": allow_draft,
        "includedCount": len(included),
        "skippedCount": len(skipped),
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "included": included,
        "skipped": skipped,
        "errors": errors,
        "warnings": warnings,
        "ok": len(errors) == 0,
    }
    return report


def write_pack_report(report: dict, output_dir: Path, dry_run: bool):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "bundle-pack-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"Bundle pack report (dry_run={dry_run})",
        f"Manifest: {report['manifest']}",
        f"Pack id: {report['assetPackId']} @ {report['assetPackVersion']}",
        f"Included: {report['includedCount']}, Skipped: {report['skippedCount']}",
        f"Errors: {report['errorCount']}, Warnings: {report['warningCount']}",
        f"OK: {report['ok']}",
        "",
        "Included assets:",
    ]
    for entry in report["included"]:
        lines.append(
            f"  + {entry['assetId']:30s} {entry['path']} "
            f"({entry['sizeBytes']} bytes, sha256={entry['sha256'][:12]}...)"
        )
    lines.append("")
    lines.append("Skipped assets:")
    for entry in report["skipped"]:
        lines.append(f"  - {entry['assetId']:30s} reason={entry['reason']}")
    lines.append("")
    lines.append("Errors:")
    for err in report["errors"]:
        lines.append(f"  ! {err}")
    (output_dir / "bundle-pack-summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pack a Muse asset bundle with allowlist gating (stdlib only)."
    )
    parser.add_argument(
        "--root", default=str(REPO_ROOT), help="repository root (default: auto-detect)"
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="manifest path, relative to --root",
    )
    parser.add_argument(
        "--allowlist",
        default=DEFAULT_ALLOWLIST,
        help="allowlist file (one repo-relative path per line; absent = allow all)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="output directory to materialise the bundle (omitted = dry-run only)",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="allow draft-status assets (bundle will be marked draft with warning)",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    manifest_rel = args.manifest.replace("\\", "/")
    dry_run = args.output is None
    output_dir = Path(args.output) if args.output else Path("Tools/AssetPack/pack_dryrun_out")

    try:
        manifest = load_json(root / manifest_rel)
    except BundlePackError as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    allowlist_path = Path(args.allowlist)
    allowlist = load_allowlist(allowlist_path)
    if allowlist is None:
        print(f"Note: no allowlist file at {allowlist_path}; all paths permitted")

    report = pack_bundle(
        manifest, root, manifest_rel,
        allowlist=allowlist,
        allow_draft=args.allow_draft,
        dry_run=dry_run,
        output_dir=output_dir,
    )

    report_path = write_pack_report(report, output_dir, dry_run)
    print(f"Wrote pack report: {report_path}")
    print(
        f"SUMMARY assetPackId={report['assetPackId']} "
        f"version={report['assetPackVersion']} "
        f"included={report['includedCount']} "
        f"skipped={report['skippedCount']} "
        f"errors={report['errorCount']} "
        f"dry_run={dry_run}"
    )
    if not report["ok"]:
        print(f"FAIL: {report['errorCount']} problem(s) prevent packing")
        return EXIT_VALIDATION
    print("OK: bundle pack validation passed")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
