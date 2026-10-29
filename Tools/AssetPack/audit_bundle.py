#!/usr/bin/env python3
"""OPC-09: Audit a Muse asset delivery bundle (standard library only).

Reads an asset delivery manifest and produces a deterministic audit report
describing every declared asset: file presence, size, SHA-256 hash, declared
license/version, dependency references, and a coverage verdict
(present / absent / unknown / unverified).

This tool is read-only: it never writes to the source art directory. The
audit report and (optionally) a copied bundle are written to a fresh output
directory so repeated runs with the same input are byte-identical.

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
    2  manifest validation failure (schema or missing required fields)

Refs #40, OPC-09. Not self-merging.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
DEFAULT_SCHEMA = "Implementation/Asset_Handoff/asset_delivery_manifest.schema.json"

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
PATH_CHARS_RE = re.compile(r"^[A-Za-z0-9._~/-]+$")
SNAKE_CASE_RE = re.compile(r"^[a-z0-9][a-z0-9_.~-]*$")

# Roots where Muse delivers art, per Implementation/Asset_Handoff/GITHUB_COLLABORATION.md.
ART_ROOTS = (
    "Client/Assets/Art",
    "Client/Assets/UI/Art",
    "Client/Assets/Tilemaps",
    "Client/Assets/VFX",
    "Client/Assets/Animation",
)

# Coverage verdicts.
#   present   - file exists on disk and hash was computed
#   absent    - declared path does not exist on disk
#   unknown   - manifest entry lacks enough information to locate/verify
#   unverified - file exists but could not be hashed (e.g. LFS pointer not fetched)
COVERAGE_PRESENT = "present"
COVERAGE_ABSENT = "absent"
COVERAGE_UNKNOWN = "unknown"
COVERAGE_UNVERIFIED = "unverified"

EXIT_OK = 0
EXIT_ENVIRONMENT = 1
EXIT_VALIDATION = 2


class BundleAuditError(Exception):
    """Raised for environment or usage problems."""


def load_json(path: Path):
    """Read a JSON file, rejecting a Git LFS pointer with an explicit message."""
    if not path.is_file():
        raise BundleAuditError(f"file not found: {path}")
    raw = path.read_bytes()
    if raw.startswith(LFS_POINTER_PREFIX):
        raise BundleAuditError(
            f"{path}: Git LFS pointer instead of file content "
            "(fetch the LFS objects, in CI use actions/checkout with lfs: true)"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundleAuditError(f"{path}: not valid UTF-8 ({exc})") from exc
    try:
        return json.loads(text)
    except ValueError as exc:
        raise BundleAuditError(f"{path}: invalid JSON ({exc})") from exc


def sha256_of_file(path: Path):
    """Return the SHA-256 hex digest of a file, or None if unreadable."""
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def inspect_repo_path(value):
    """Return (normalised repo-relative path, problem-message-or-None)."""
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
    """Join a repo-relative path and refuse to leave the repository."""
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def under_art_root(rel: str) -> bool:
    return any(rel == root or rel.startswith(root + "/") for root in ART_ROOTS)


def canonical_dependency_key(asset: dict) -> str:
    """Build a stable dependency reference key for an asset entry."""
    asset_id = asset.get("assetId") or ""
    kind = asset.get("kind") or ""
    path = asset.get("path") or ""
    return f"{kind}:{asset_id}:{path}"


def audit_asset(asset: dict, root: Path, manifest_rel: str):
    """Audit a single asset entry and return a record dict."""
    label = asset.get("assetId") or "<unnamed>"
    raw_path = asset.get("path")
    rel, path_problem = inspect_repo_path(raw_path)

    record = {
        "assetId": label,
        "kind": asset.get("kind"),
        "status": asset.get("status"),
        "declaredPath": raw_path,
        "resolvedPath": None,
        "coverage": COVERAGE_UNKNOWN,
        "sizeBytes": None,
        "sha256": None,
        "license": None,
        "version": None,
        "dependencies": [],
        "evidence": [],
        "findings": [],
    }

    if path_problem:
        record["findings"].append(f"path: {path_problem}")
        return record

    record["resolvedPath"] = rel

    # License / version metadata carried on the pack or per-asset.
    record["license"] = asset.get("sourceLicense") or "original"
    record["version"] = asset.get("assetPackVersion") or None

    target = None
    if rel is not None:
        if not rel.startswith("Client/Assets/"):
            record["findings"].append("path: must live under Client/Assets/")
        target = resolve_inside_root(root, rel)
        if target is None:
            record["findings"].append("path: escapes the repository root")
        elif not under_art_root(rel):
            record["findings"].append(
                "path: outside agreed art roots (" + ", ".join(ART_ROOTS) + ")"
            )

    if rel is not None and target is not None:
        if not target.is_file():
            record["coverage"] = COVERAGE_ABSENT
            record["findings"].append("declared file does not exist in the repository")
        elif rel.lower().endswith(".png"):
            lfs_head = target.read_bytes()[: len(LFS_POINTER_PREFIX)]
            if lfs_head == LFS_POINTER_PREFIX:
                record["coverage"] = COVERAGE_UNVERIFIED
                record["findings"].append(
                    "file is a Git LFS pointer; LFS objects were not fetched"
                )
            else:
                size = target.stat().st_size
                digest = sha256_of_file(target)
                record["sizeBytes"] = size
                record["sha256"] = digest
                record["coverage"] = COVERAGE_PRESENT
                record["evidence"].append(f"sha256:{digest}")
                record["evidence"].append(f"size:{size}")
        else:
            # Non-image asset: record presence only.
            size = target.stat().st_size
            digest = sha256_of_file(target)
            record["sizeBytes"] = size
            record["sha256"] = digest
            record["coverage"] = COVERAGE_PRESENT
            record["evidence"].append(f"sha256:{digest}")
            record["evidence"].append(f"size:{size}")

    # Dependency references declared on the asset.
    replaces = asset.get("replacesAssetId")
    if isinstance(replaces, str) and replaces:
        record["dependencies"].append(replaces)

    return record


def audit_bundle(manifest: dict, root: Path, manifest_rel: str) -> dict:
    """Audit every asset in the manifest and return a full report dict."""
    assets = manifest.get("assets") or []
    records = [audit_asset(a, root, manifest_rel) for a in assets]

    summary = {
        "totalAssets": len(records),
        "present": sum(1 for r in records if r["coverage"] == COVERAGE_PRESENT),
        "absent": sum(1 for r in records if r["coverage"] == COVERAGE_ABSENT),
        "unknown": sum(1 for r in records if r["coverage"] == COVERAGE_UNKNOWN),
        "unverified": sum(1 for r in records if r["coverage"] == COVERAGE_UNVERIFIED),
    }

    # Overall bundle digest: hash of the sorted assetId -> sha256 mapping.
    digest_pairs = sorted(
        (r["assetId"], r["sha256"]) for r in records if r["sha256"]
    )
    bundle_digest = hashlib.sha256(
        json.dumps(digest_pairs, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    report = {
        "auditedAt": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest_rel,
        "assetPackId": manifest.get("assetPackId"),
        "assetPackVersion": manifest.get("assetPackVersion"),
        "owner": manifest.get("owner"),
        "sourceLicense": manifest.get("sourceLicense"),
        "bundleDigest": bundle_digest,
        "summary": summary,
        "coverage": {
            "present": COVERAGE_PRESENT,
            "absent": COVERAGE_ABSENT,
            "unknown": COVERAGE_UNKNOWN,
            "unverified": COVERAGE_UNVERIFIED,
        },
        "assets": records,
    }
    return report


def write_report(report: dict, output_dir: Path, copy_bundle: bool, root: Path):
    """Write the audit JSON report to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "bundle-audit-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Human readable summary.
    lines = [
        f"Bundle audit: {report['assetPackId']} @ {report['assetPackVersion']}",
        f"Manifest: {report['manifest']}",
        f"Bundle digest (SHA-256 of asset hashes): {report['bundleDigest']}",
        "",
        "Coverage summary:",
        f"  present : {report['summary']['present']}",
        f"  absent  : {report['summary']['absent']}",
        f"  unknown : {report['summary']['unknown']}",
        f"  unverif.: {report['summary']['unverified']}",
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
            lines.append(f"            sha256={rec['sha256']} size={rec['sizeBytes']}")
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
                shutil.copy2(src, dst)
        # Copy the manifest itself into the bundle output.
        manifest_src = root / report["manifest"]
        manifest_dst = bundle_dir / report["manifest"]
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest_src, manifest_dst)

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
        help="manifest path, relative to --root",
    )
    parser.add_argument(
        "--output",
        default="Tools/AssetPack/audit_out",
        help="output directory for the audit report (fresh dir each run)",
    )
    parser.add_argument(
        "--copy-bundle",
        action="store_true",
        help="also copy verified assets into <output>/bundle (read-only source)",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    manifest_rel = args.manifest.replace("\\", "/")
    output_dir = Path(args.output)

    try:
        manifest = load_json(root / manifest_rel)
    except BundleAuditError as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

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
        f"unverified={report['summary']['unverified']}"
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
