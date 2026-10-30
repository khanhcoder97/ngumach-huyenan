#!/usr/bin/env python3
"""OPC-09: deterministic, read-only asset bundle audit (standard library only).

Reads an asset delivery manifest and produces a deterministic audit report:
file presence, size, SHA-256, declared license/version, dependency references
and a coverage verdict (present / absent / unknown / unverified).

The tool never writes to the source art directory. Reports are byte-identical
for identical inputs: there is no wall-clock timestamp and JSON keys are sorted.
The ``bundleDigest`` uses the same canonical algorithm as the packed
``bundle-manifest.json``, so audit and verify results are comparable.

Usage (from the repository root):
    python Tools/AssetPack/audit_bundle.py \
        --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
        --output Tools/AssetPack/audit_out

    python Tools/AssetPack/audit_bundle.py \
        --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
        --output Tools/AssetPack/audit_out --copy-bundle

Exit codes:
    0  audit completed (findings may still be present)
    1  environment / usage error
    2  manifest validation failure (wrong shape or missing assets)

Refs #40, OPC-09. Not self-merging.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import bundle_format as bf


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"

# Compatibility aliases: earlier callers imported these from audit_bundle.
LFS_POINTER_PREFIX = bf.LFS_POINTER_PREFIX
PATH_CHARS_RE = bf.PATH_CHARS_RE
ART_ROOTS = bf.ART_ROOTS
inspect_repo_path = bf.inspect_repo_path
resolve_inside_root = bf.resolve_inside_root
under_art_root = bf.under_art_root
sha256_of_file = bf.sha256_of_file

COVERAGE_PRESENT = "present"
COVERAGE_ABSENT = "absent"
COVERAGE_UNKNOWN = "unknown"
COVERAGE_UNVERIFIED = "unverified"

EXIT_OK = 0
EXIT_ENVIRONMENT = 1
EXIT_VALIDATION = 2


class BundleAuditError(bf.BundleFormatError):
    """Raised for environment or usage problems."""


def load_json(path: Path):
    try:
        return bf.load_json(path)
    except bf.BundleFormatError as exc:
        raise BundleAuditError(str(exc)) from exc


def canonical_dependency_key(asset: dict) -> str:
    """Build a stable dependency reference key for an asset entry."""
    asset_id = asset.get("assetId") or ""
    kind = asset.get("kind") or ""
    path = asset.get("path") or ""
    return f"{kind}:{asset_id}:{path}"


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


def audit_asset(asset: dict, root: Path, manifest_rel: str,
                manifest_defaults: dict | None = None):
    """Audit a single asset entry and return a deterministic record dict."""
    label = asset.get("assetId") or "<unnamed>"
    defaults = manifest_defaults or {}
    raw_path = asset.get("path")
    rel, path_problem = bf.inspect_repo_path(raw_path)

    record = {
        "assetId": label,
        "kind": asset.get("kind"),
        "status": asset.get("status"),
        "declaredPath": raw_path,
        "resolvedPath": None,
        "coverage": COVERAGE_UNKNOWN,
        "sizeBytes": None,
        "sha256": None,
        "license": asset.get("sourceLicense") or defaults.get("sourceLicense") or "original",
        "version": asset.get("assetPackVersion") or defaults.get("assetPackVersion"),
        "dependencies": _declared_dependencies(asset),
        "evidence": [],
        "findings": [],
    }

    if path_problem:
        record["findings"].append(f"path: {path_problem}")
        return record

    record["resolvedPath"] = rel

    if not rel.startswith("Client/Assets/"):
        record["findings"].append("path: must live under Client/Assets/")
    target = bf.resolve_inside_root(root, rel)
    if target is None:
        record["findings"].append("path: escapes the repository root")
        return record
    if not bf.under_art_root(rel):
        record["findings"].append(
            "path: outside agreed art roots (" + ", ".join(bf.ART_ROOTS) + ")"
        )

    if not target.is_file():
        record["coverage"] = COVERAGE_ABSENT
        record["findings"].append("declared file does not exist in the repository")
        return record

    try:
        head = target.read_bytes()[: len(bf.LFS_POINTER_PREFIX)]
    except OSError:
        head = b""
    if head == bf.LFS_POINTER_PREFIX:
        record["coverage"] = COVERAGE_UNVERIFIED
        record["findings"].append(
            "file is a Git LFS pointer; LFS objects were not fetched"
        )
        return record

    size = target.stat().st_size
    try:
        digest = bf.sha256_of_file(target)
    except OSError as exc:
        record["coverage"] = COVERAGE_UNVERIFIED
        record["findings"].append(f"file cannot be read: {exc}")
        return record

    record["sizeBytes"] = size
    record["sha256"] = digest
    record["coverage"] = COVERAGE_PRESENT
    record["evidence"].append(f"sha256:{digest}")
    record["evidence"].append(f"size:{size}")
    return record


def audit_bundle(manifest: dict, root: Path, manifest_rel: str) -> dict:
    """Audit every asset in the manifest and return a deterministic report."""
    assets = bf.manifest_assets(manifest)
    defaults = {
        "assetPackVersion": manifest.get("assetPackVersion"),
        "sourceLicense": manifest.get("sourceLicense"),
    }
    records = [audit_asset(a, root, manifest_rel, defaults) for a in assets]
    records.sort(
        key=lambda rec: (
            rec["resolvedPath"] or rec["declaredPath"] or "",
            rec["assetId"] or "",
        )
    )

    id_counts = {}
    path_counts = {}
    for record in records:
        if record["assetId"] and record["assetId"] != "<unnamed>":
            id_counts[record["assetId"]] = id_counts.get(record["assetId"], 0) + 1
        if record["resolvedPath"]:
            path_counts[record["resolvedPath"]] = path_counts.get(
                record["resolvedPath"], 0
            ) + 1
    duplicate_ids = sorted(k for k, count in id_counts.items() if count > 1)
    duplicate_paths = sorted(k for k, count in path_counts.items() if count > 1)
    for record in records:
        if record["assetId"] in duplicate_ids:
            record["findings"].append(
                f"duplicate assetId {record['assetId']!r} appears "
                f"{id_counts[record['assetId']]} times"
            )
        if record["resolvedPath"] in duplicate_paths:
            record["findings"].append(
                f"duplicate path {record['resolvedPath']!r} appears "
                f"{path_counts[record['resolvedPath']]} times"
            )

    summary = {
        "totalAssets": len(records),
        "present": sum(1 for r in records if r["coverage"] == COVERAGE_PRESENT),
        "absent": sum(1 for r in records if r["coverage"] == COVERAGE_ABSENT),
        "unknown": sum(1 for r in records if r["coverage"] == COVERAGE_UNKNOWN),
        "unverified": sum(1 for r in records if r["coverage"] == COVERAGE_UNVERIFIED),
        "duplicateAssetIds": len(duplicate_ids),
        "duplicatePaths": len(duplicate_paths),
    }

    return {
        "reportFormat": 1,
        "manifest": manifest_rel,
        "assetPackId": manifest.get("assetPackId"),
        "assetPackVersion": manifest.get("assetPackVersion"),
        "owner": manifest.get("owner"),
        "sourceLicense": manifest.get("sourceLicense"),
        "bundleDigest": bf.compute_bundle_digest(records),
        "summary": summary,
        "coverage": {
            "present": COVERAGE_PRESENT,
            "absent": COVERAGE_ABSENT,
            "unknown": COVERAGE_UNKNOWN,
            "unverified": COVERAGE_UNVERIFIED,
        },
        "duplicateAssetIds": duplicate_ids,
        "duplicatePaths": duplicate_paths,
        "assets": records,
    }


def write_report(report: dict, output_dir: Path, copy_bundle: bool, root: Path):
    """Write deterministic audit JSON/summary and optional bundle copy."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "bundle-audit-report.json"
    bf.write_json(report_path, report)

    lines = [
        f"Bundle audit: {report['assetPackId']} @ {report['assetPackVersion']}",
        f"Manifest: {report['manifest']}",
        f"Bundle digest (SHA-256 of sorted asset records): {report['bundleDigest']}",
        "",
        "Coverage summary:",
        f"  present : {report['summary']['present']}",
        f"  absent  : {report['summary']['absent']}",
        f"  unknown : {report['summary']['unknown']}",
        f"  unverif.: {report['summary']['unverified']}",
        f"  duplicate ids  : {report['summary']['duplicateAssetIds']}",
        f"  duplicate paths: {report['summary']['duplicatePaths']}",
        f"  total   : {report['summary']['totalAssets']}",
        "",
        "Per-asset detail:",
    ]
    for rec in report["assets"]:
        lines.append(
            f"  [{rec['coverage']:10s}] {rec['assetId']:30s} "
            f"kind={rec['kind'] or '-':14s} path={rec['declaredPath'] or '-'}"
        )
        if rec["sha256"]:
            lines.append(
                f"            sha256={rec['sha256']} size={rec['sizeBytes']}"
            )
        for finding in rec["findings"]:
            lines.append(f"            FINDING: {finding}")
        for dep in rec["dependencies"]:
            lines.append(f"            dependsOn={dep}")
    summary_path = output_dir / "bundle-audit-summary.txt"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if copy_bundle:
        bundle_dir = output_dir / "bundle"
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        for rec in report["assets"]:
            if rec["coverage"] == COVERAGE_PRESENT and rec["resolvedPath"]:
                src = root / rec["resolvedPath"]
                dst = bundle_dir / rec["resolvedPath"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        manifest_src = root / report["manifest"]
        manifest_dst = bundle_dir / report["manifest"]
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(manifest_src, manifest_dst)

    return report_path, summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a Muse asset delivery bundle (read-only, stdlib only)."
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
        "--output",
        default="Tools/AssetPack/audit_out",
        help="output directory (relative paths are resolved under --root)",
    )
    parser.add_argument(
        "--copy-bundle",
        action="store_true",
        help="also copy verified assets into <output>/bundle (read-only source)",
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

    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()

    try:
        manifest = load_json(manifest_path)
        bf.manifest_assets(manifest)
    except (BundleAuditError, bf.BundleFormatError) as exc:
        print(f"MANIFEST ERROR: {exc}", file=sys.stderr)
        return EXIT_VALIDATION

    report = audit_bundle(manifest, root, manifest_rel)
    report_path, summary_path = write_report(report, output_dir, args.copy_bundle, root)

    print(f"Wrote audit report: {report_path}")
    print(f"Wrote audit summary: {summary_path}")
    print(
        f"SUMMARY assetPackId={report['assetPackId']} "
        f"version={report['assetPackVersion']} "
        f"assets={report['summary']['totalAssets']} "
        f"present={report['summary']['present']} "
        f"absent={report['summary']['absent']} "
        f"unknown={report['summary']['unknown']} "
        f"unverified={report['summary']['unverified']} "
        f"duplicate_ids={report['summary']['duplicateAssetIds']} "
        f"duplicate_paths={report['summary']['duplicatePaths']} "
        f"bundleDigest={report['bundleDigest']}"
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
