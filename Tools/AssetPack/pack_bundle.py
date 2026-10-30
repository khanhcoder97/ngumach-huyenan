#!/usr/bin/env python3
"""OPC-09: pack a Muse asset bundle with allowlist/dependency gating.

The pack is deterministic: no wall-clock timestamp, sorted JSON keys, sorted
asset entries and a content-addressed ``bundleDigest`` shared with
``verify_bundle``/``unpack_bundle``.

Gating rules:
  * missing, deprecated, duplicate or under-specified assets fail validation;
  * draft assets require ``--allow-draft`` and mark the bundle ``draft``;
  * every asset path must be relative, inside ``--root``, inside an agreed art
    root and on the allowlist (unless the allowlist file is absent);
  * Git LFS pointer files fail with an explicit message;
  * dependencies/replacements must reference another included asset;
  * validation happens before any bundle file is written, so a failed pack
    cannot leave a partial bundle.

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
    2  validation failure (missing/deprecated/duplicate/insufficient metadata)

Refs #40, OPC-09. Not self-merging.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import bundle_format as bf


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
DEFAULT_ALLOWLIST = "Tools/AssetPack/allowlist.txt"

LFS_POINTER_PREFIX = bf.LFS_POINTER_PREFIX
PATH_CHARS_RE = bf.PATH_CHARS_RE
ART_ROOTS = bf.ART_ROOTS
inspect_repo_path = bf.inspect_repo_path
resolve_inside_root = bf.resolve_inside_root
under_art_root = bf.under_art_root
sha256_of_file = bf.sha256_of_file

REQUIRED_META_FIELDS = (
    "assetId",
    "path",
    "kind",
    "status",
    "pixelWidth",
    "pixelHeight",
    "pixelsPerUnit",
    "previewPath",
)
ALLOWED_KINDS = (
    "sprite",
    "sprite_sheet",
    "tileset",
    "tilemap",
    "ui_texture",
    "vfx_sheet",
    "animation",
    "icon",
)
ALLOWED_STATUSES = ("draft", "approved", "deprecated")

EXIT_OK = 0
EXIT_ENVIRONMENT = 1
EXIT_VALIDATION = 2


class BundlePackError(bf.BundleFormatError):
    """Raised for environment or usage problems."""


def load_json(path: Path):
    try:
        return bf.load_json(path)
    except bf.BundleFormatError as exc:
        raise BundlePackError(str(exc)) from exc


def load_allowlist(path: Path):
    """Return a normalised set of repo-relative paths, or None if absent."""
    if not path.is_file():
        return None
    entries = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        rel, problem = bf.inspect_repo_path(value.replace("\\", "/"))
        if problem:
            raise BundlePackError(f"allowlist line {line_number}: {problem}")
        entries.append(rel)
    return bf.normalise_allowlist(entries)


def _is_positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def check_metadata(asset: dict, findings: list) -> bool:
    """Return True if the asset carries sufficient, well-typed metadata."""
    ok = True
    for field in REQUIRED_META_FIELDS:
        if field not in asset or asset[field] is None or asset[field] == "":
            findings.append(f"missing required metadata field: {field}")
            ok = False

    asset_id = asset.get("assetId")
    if not isinstance(asset_id, str) or not re.match(r"^[A-Z0-9_]+$", asset_id or ""):
        findings.append("assetId must match ^[A-Z0-9_]+$")
        ok = False

    if asset.get("kind") not in ALLOWED_KINDS:
        findings.append(f"kind must be one of {ALLOWED_KINDS}")
        ok = False
    if asset.get("status") not in ALLOWED_STATUSES:
        findings.append("status must be one of draft/approved/deprecated")
        ok = False

    ppu = asset.get("pixelsPerUnit")
    if (
        not isinstance(ppu, (int, float))
        or isinstance(ppu, bool)
        or float(ppu) != 20.0
    ):
        findings.append("pixelsPerUnit must equal 20")
        ok = False

    for field in ("pixelWidth", "pixelHeight"):
        if not _is_positive_int(asset.get(field)):
            findings.append(f"{field} must be a positive integer")
            ok = False

    preview = asset.get("previewPath")
    if not isinstance(preview, str) or not preview:
        findings.append("previewPath must be a non-empty string")
        ok = False
    else:
        _rel, preview_problem = bf.inspect_repo_path(preview)
        if preview_problem:
            findings.append(f"previewPath: {preview_problem}")
            ok = False
    return ok


def _declared_dependencies(asset: dict):
    dependencies = []
    raw = asset.get("dependencies")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and item and item not in dependencies:
                dependencies.append(item)
    replaces = asset.get("replacesAssetId")
    if isinstance(replaces, str) and replaces and replaces not in dependencies:
        dependencies.append(replaces)
    return dependencies


def pack_bundle(
    manifest: dict,
    root: Path,
    manifest_rel: str,
    allowlist,
    allow_draft: bool,
    dry_run: bool,
    output_dir: Path,
):
    """Validate and (on success) materialise a deterministic bundle.

    Validation errors never create bundle files. A caller-supplied non-empty
    ``output_dir`` is rejected rather than silently overwritten.
    """
    assets = bf.manifest_assets(manifest)
    errors = []
    warnings = []
    included = []
    skipped = []

    # Duplicate identities make assetId/path-based dependency and digest
    # semantics ambiguous, so fail before evaluating any single asset.
    seen_ids = {}
    seen_paths = {}
    duplicate_indexes = set()
    known_ids = set()
    status_by_id = {}
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"assets[{index}]: asset entry is not an object")
            continue
        asset_id = asset.get("assetId")
        if isinstance(asset_id, str) and asset_id:
            known_ids.add(asset_id)
            status_by_id.setdefault(asset_id, asset.get("status"))
            if asset_id in seen_ids:
                errors.append(
                    f"duplicate assetId {asset_id!r} at assets[{index}] "
                    f"and assets[{seen_ids[asset_id]}]"
                )
                duplicate_indexes.add(index)
                duplicate_indexes.add(seen_ids[asset_id])
            else:
                seen_ids[asset_id] = index
        rel, _problem = bf.inspect_repo_path(asset.get("path"))
        if rel:
            if rel in seen_paths:
                errors.append(
                    f"duplicate path {rel!r} at assets[{index}] "
                    f"and assets[{seen_paths[rel]}]"
                )
                duplicate_indexes.add(index)
                duplicate_indexes.add(seen_paths[rel])
            else:
                seen_paths[rel] = index

    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            continue
        label = asset.get("assetId") or f"assets[{index}]"
        if index in duplicate_indexes:
            skipped.append(
                {"assetId": label, "reason": "duplicate assetId/path"}
            )
            continue

        raw_path = asset.get("path")
        rel, path_problem = bf.inspect_repo_path(raw_path)

        findings = []
        if not check_metadata(asset, findings):
            errors.append(f"{label}: " + "; ".join(findings))
            skipped.append(
                {
                    "assetId": label,
                    "reason": "insufficient metadata",
                    "findings": findings,
                }
            )
            continue

        status = asset.get("status")
        if status == "deprecated":
            errors.append(f"{label}: status is 'deprecated', cannot be packed")
            skipped.append({"assetId": label, "reason": "deprecated"})
            continue
        if status == "draft" and not allow_draft:
            errors.append(
                f"{label}: status is 'draft'; pass --allow-draft to include"
            )
            skipped.append({"assetId": label, "reason": "draft (blocked)"})
            continue

        if rel is None:
            errors.append(f"{label}: path problem: {path_problem}")
            skipped.append(
                {
                    "assetId": label,
                    "reason": "invalid path",
                    "problem": path_problem,
                }
            )
            continue
        if allowlist is not None and rel not in allowlist:
            errors.append(f"{label}: path '{rel}' is not on the allowlist")
            skipped.append({"assetId": label, "reason": "not on allowlist"})
            continue
        if not bf.under_art_root(rel):
            errors.append(f"{label}: path '{rel}' is outside agreed art roots")
            skipped.append({"assetId": label, "reason": "outside art root"})
            continue

        target = bf.resolve_inside_root(root, rel)
        if target is None:
            errors.append(f"{label}: path '{rel}' escapes the repository root")
            skipped.append(
                {"assetId": label, "reason": "escapes repository root"}
            )
            continue
        if not target.is_file():
            errors.append(f"{label}: declared file does not exist: {rel}")
            skipped.append(
                {"assetId": label, "reason": "file missing", "path": rel}
            )
            continue

        try:
            head = target.read_bytes()[: len(bf.LFS_POINTER_PREFIX)]
        except OSError as exc:
            errors.append(f"{label}: cannot read '{rel}': {exc}")
            skipped.append(
                {"assetId": label, "reason": "unreadable", "path": rel}
            )
            continue
        if head == bf.LFS_POINTER_PREFIX:
            errors.append(
                f"{label}: '{rel}' is a Git LFS pointer; fetch LFS objects first"
            )
            skipped.append(
                {"assetId": label, "reason": "lfs pointer", "path": rel}
            )
            continue

        try:
            size = target.stat().st_size
            digest = bf.sha256_of_file(target)
        except OSError as exc:
            errors.append(f"{label}: cannot hash '{rel}': {exc}")
            skipped.append(
                {"assetId": label, "reason": "unreadable", "path": rel}
            )
            continue

        included.append(
            {
                "assetId": label,
                "kind": asset.get("kind"),
                "status": status,
                "path": rel,
                "sizeBytes": size,
                "sha256": digest,
                "dependencies": _declared_dependencies(asset),
            }
        )

    included.sort(key=lambda entry: (entry["path"], entry["assetId"]))
    included_ids = {entry["assetId"] for entry in included}

    for entry in included:
        for dependency in entry["dependencies"]:
            if dependency == entry["assetId"]:
                errors.append(
                    f"{entry['assetId']}: dependency cannot reference itself"
                )
            elif dependency not in known_ids:
                errors.append(
                    f"{entry['assetId']}: dependency {dependency!r} "
                    "does not exist in the manifest"
                )
            elif dependency not in included_ids:
                errors.append(
                    f"{entry['assetId']}: dependency {dependency!r} "
                    "is not included in this pack"
                )
            elif status_by_id.get(dependency) == "deprecated":
                errors.append(
                    f"{entry['assetId']}: dependency {dependency!r} is deprecated"
                )

    bundle_digest = bf.compute_bundle_digest(included)
    draft = any(entry["status"] == "draft" for entry in included)
    ok = not errors

    if not dry_run and ok:
        output_dir = Path(output_dir)
        if output_dir.exists():
            if not output_dir.is_dir():
                raise BundlePackError(
                    f"output path exists and is not a directory: {output_dir}"
                )
            if any(output_dir.iterdir()):
                raise BundlePackError(
                    f"output directory must be absent or empty: {output_dir}"
                )
        output_dir.mkdir(parents=True, exist_ok=True)

        for entry in included:
            src = root / entry["path"]
            dst = output_dir / entry["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

        manifest_src = root / manifest_rel
        manifest_dst = output_dir / manifest_rel
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(manifest_src, manifest_dst)

        bundle_manifest = {
            "bundleFormat": bf.BUNDLE_FORMAT_VERSION,
            "sourceManifest": manifest_rel,
            "assetPackId": manifest.get("assetPackId"),
            "assetPackVersion": manifest.get("assetPackVersion"),
            "owner": manifest.get("owner"),
            "sourceLicense": manifest.get("sourceLicense"),
            "draft": draft,
            "bundleDigest": bundle_digest,
            "assets": included,
        }
        bf.write_json(output_dir / "bundle-manifest.json", bundle_manifest)

    report = {
        "reportFormat": 1,
        "manifest": manifest_rel,
        "assetPackId": manifest.get("assetPackId"),
        "assetPackVersion": manifest.get("assetPackVersion"),
        "dryRun": dry_run,
        "allowDraft": allow_draft,
        "draft": draft,
        "bundleDigest": bundle_digest,
        "includedCount": len(included),
        "skippedCount": len(skipped),
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "included": included,
        "skipped": skipped,
        "errors": errors,
        "warnings": warnings,
        "ok": ok,
    }
    return report


def write_pack_report(report: dict, output_dir: Path, dry_run: bool):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "bundle-pack-report.json"
    bf.write_json(report_path, report)

    lines = [
        f"Bundle pack report (dry_run={dry_run})",
        f"Manifest: {report['manifest']}",
        f"Pack id: {report['assetPackId']} @ {report['assetPackVersion']}",
        f"Bundle digest: {report['bundleDigest']}",
        f"Draft: {report['draft']}",
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
    (output_dir / "bundle-pack-summary.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pack a Muse asset bundle with allowlist/dependency gating."
    )
    parser.add_argument(
        "--root", default=str(REPO_ROOT), help="repository root (default: auto-detect)"
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="manifest path relative to --root (absolute paths inside --root are accepted)",
    )
    parser.add_argument(
        "--allowlist",
        default=DEFAULT_ALLOWLIST,
        help="allowlist file relative to --root (absent = allow all)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="output directory (relative paths are resolved under --root; omitted = dry-run)",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="allow draft-status assets (bundle is marked draft)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate only; never materialise a bundle",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ENVIRONMENT ERROR: --root is not a directory: {root}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    try:
        manifest_path, manifest_rel = bf.resolve_input_path(
            root, args.manifest, "manifest"
        )
    except bf.BundleFormatError as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    allowlist = None
    if args.allowlist:
        try:
            allowlist_path, _allow_rel = bf.resolve_input_path(
                root, args.allowlist, "allowlist"
            )
            allowlist = load_allowlist(allowlist_path)
        except bf.BundleFormatError as exc:
            print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
            return EXIT_ENVIRONMENT
        if allowlist is None:
            print(
                f"Note: no allowlist file at {allowlist_path}; all paths permitted"
            )

    dry_run = args.output is None or args.dry_run
    if args.output:
        output_dir = Path(args.output)
        if not output_dir.is_absolute():
            output_dir = (root / output_dir).resolve()
    else:
        output_dir = (root / "Tools/AssetPack/pack_dryrun_out").resolve()

    try:
        manifest = load_json(manifest_path)
        bf.manifest_assets(manifest)
    except (BundlePackError, bf.BundleFormatError) as exc:
        print(f"MANIFEST ERROR: {exc}", file=sys.stderr)
        return EXIT_VALIDATION

    try:
        report = pack_bundle(
            manifest,
            root,
            manifest_rel,
            allowlist=allowlist,
            allow_draft=args.allow_draft,
            dry_run=dry_run,
            output_dir=output_dir,
        )
    except BundlePackError as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    report_path = write_pack_report(report, output_dir, dry_run)
    print(f"Wrote pack report: {report_path}")
    print(
        f"SUMMARY assetPackId={report['assetPackId']} "
        f"version={report['assetPackVersion']} "
        f"included={report['includedCount']} "
        f"skipped={report['skippedCount']} "
        f"errors={report['errorCount']} "
        f"draft={report['draft']} "
        f"bundleDigest={report['bundleDigest']} "
        f"dry_run={dry_run}"
    )
    if not report["ok"]:
        print(f"FAIL: {report['errorCount']} problem(s) prevent packing")
        return EXIT_VALIDATION
    print("OK: bundle pack validation passed")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
