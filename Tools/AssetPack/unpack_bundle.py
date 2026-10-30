#!/usr/bin/env python3
"""OPC-09: verify a packed bundle and optionally unpack it losslessly.

Verification is deliberately independent from the pack process:

* ``bundle-manifest.json`` must use ``bundleFormat: 1``;
* every asset path must be relative, duplicate-free and confined to the bundle;
* every file must exist, be a regular file (not a symlink) and match its
  declared size and SHA-256;
* the recomputed ``bundleDigest`` must equal the manifest's digest;
* unpacking copies only verified files, then re-verifies those copies.

Usage (from the repository root):
    python Tools/AssetPack/unpack_bundle.py \
        --bundle Tools/AssetPack/bundle_out

    python Tools/AssetPack/unpack_bundle.py \
        --bundle Tools/AssetPack/bundle_out \
        --output Tools/AssetPack/unpacked_out

Exit codes:
    0  verified (and unpacked, if requested)
    1  environment / usage error
    2  verification failure

Refs #40, OPC-09. Not self-merging.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import bundle_format as bf


REPO_ROOT = Path(__file__).resolve().parents[2]

EXIT_OK = 0
EXIT_ENVIRONMENT = 1
EXIT_VERIFICATION = 2

IGNORED_REPORT_FILES = {
    "bundle-pack-report.json",
    "bundle-pack-summary.txt",
    "bundle-audit-report.json",
    "bundle-audit-summary.txt",
    "bundle-verify-report.json",
    "bundle-verify-summary.txt",
}


class BundleUnpackError(bf.BundleFormatError):
    """Raised for environment or usage problems."""


def _path_has_symlink(bundle_dir: Path, rel: str) -> bool:
    current = bundle_dir
    for part in rel.split("/"):
        current = current / part
        if current.is_symlink():
            return True
    return False


def _list_extra_files(bundle_dir: Path, expected: set) -> list:
    extras = []
    for current_dir, dirnames, filenames in os.walk(bundle_dir, followlinks=False):
        current = Path(current_dir)
        # Do not descend into directory symlinks; they are reported by the
        # asset checks when they affect a declared path.
        dirnames[:] = [
            name for name in dirnames if not (current / name).is_symlink()
        ]
        for name in filenames:
            path = current / name
            rel = path.relative_to(bundle_dir).as_posix()
            if rel in expected or name in IGNORED_REPORT_FILES:
                continue
            extras.append(rel)
    return sorted(extras)


def verify_bundle(bundle_dir: Path) -> dict:
    """Return a deterministic verification report for one bundle directory."""
    bundle_dir = Path(bundle_dir).resolve()
    report = {
        "reportFormat": 1,
        "bundle": bundle_dir.as_posix(),
        "bundleFormat": None,
        "assetPackId": None,
        "assetPackVersion": None,
        "declaredDigest": None,
        "computedDigest": None,
        "assetCount": 0,
        "verifiedCount": 0,
        "errors": [],
        "warnings": [],
        "extraFiles": [],
        "assets": [],
        "ok": False,
    }

    manifest_path = bundle_dir / "bundle-manifest.json"
    if not bundle_dir.is_dir():
        report["errors"].append(f"bundle directory does not exist: {bundle_dir}")
        return report
    if not manifest_path.is_file():
        report["errors"].append("bundle-manifest.json is missing")
        return report
    try:
        manifest = bf.load_json(manifest_path)
    except bf.BundleFormatError as exc:
        report["errors"].append(str(exc))
        return report
    if not isinstance(manifest, dict):
        report["errors"].append("bundle-manifest.json root must be an object")
        return report

    report["bundleFormat"] = manifest.get("bundleFormat")
    report["assetPackId"] = manifest.get("assetPackId")
    report["assetPackVersion"] = manifest.get("assetPackVersion")
    report["declaredDigest"] = manifest.get("bundleDigest")
    if manifest.get("bundleFormat") != bf.BUNDLE_FORMAT_VERSION:
        report["errors"].append(
            f"bundleFormat must be {bf.BUNDLE_FORMAT_VERSION}, "
            f"got {manifest.get('bundleFormat')!r}"
        )

    source_manifest = manifest.get("sourceManifest")
    expected = {"bundle-manifest.json"}
    if isinstance(source_manifest, str):
        source_rel, source_problem = bf.inspect_repo_path(source_manifest)
        if source_problem:
            report["errors"].append(f"sourceManifest: {source_problem}")
        else:
            expected.add(source_rel)
            if not (bundle_dir / source_rel).is_file():
                report["warnings"].append(
                    f"source manifest copy is missing: {source_rel}"
                )

    entries = manifest.get("assets")
    if not isinstance(entries, list):
        report["errors"].append("bundle assets must be an array")
        entries = []
    report["assetCount"] = len(entries)

    seen_ids = {}
    seen_paths = {}
    verified_entries = []
    for index, entry in enumerate(entries):
        prefix = f"assets[{index}]"
        if not isinstance(entry, dict):
            report["errors"].append(f"{prefix}: entry is not an object")
            continue
        asset_id = entry.get("assetId")
        if not isinstance(asset_id, str) or not asset_id:
            report["errors"].append(f"{prefix}: assetId must be a non-empty string")
        elif asset_id in seen_ids:
            report["errors"].append(
                f"{prefix}: duplicate assetId {asset_id!r} "
                f"(also assets[{seen_ids[asset_id]}])"
            )
        else:
            seen_ids[asset_id] = index

        rel, problem = bf.inspect_repo_path(entry.get("path"))
        if problem:
            report["errors"].append(f"{prefix}: path: {problem}")
            continue
        if rel in seen_paths:
            report["errors"].append(
                f"{prefix}: duplicate path {rel!r} "
                f"(also assets[{seen_paths[rel]}])"
            )
            continue
        seen_paths[rel] = index
        expected.add(rel)

        if _path_has_symlink(bundle_dir, rel):
            report["errors"].append(f"{prefix}: path uses a symlink: {rel}")
            continue
        target = bf.resolve_inside_root(bundle_dir, rel)
        if target is None:
            report["errors"].append(f"{prefix}: path escapes the bundle: {rel}")
            continue
        if not target.is_file():
            report["errors"].append(f"{prefix}: file is missing: {rel}")
            continue

        declared_size = entry.get("sizeBytes")
        declared_sha = entry.get("sha256")
        if not isinstance(declared_size, int) or declared_size < 0:
            report["errors"].append(f"{prefix}: sizeBytes must be a non-negative integer")
        if not isinstance(declared_sha, str) or len(declared_sha) != 64:
            report["errors"].append(f"{prefix}: sha256 must be 64 hex characters")

        actual_size = target.stat().st_size
        actual_sha = bf.sha256_of_file(target)
        if isinstance(declared_size, int) and actual_size != declared_size:
            report["errors"].append(
                f"{prefix}: size mismatch for {rel} "
                f"(declared {declared_size}, actual {actual_size})"
            )
        if isinstance(declared_sha, str) and actual_sha != declared_sha:
            report["errors"].append(
                f"{prefix}: sha256 mismatch for {rel} "
                f"(declared {declared_sha[:12]}..., actual {actual_sha[:12]}...)"
            )
        verified_entries.append(entry)
        report["assets"].append(
            {
                "assetId": asset_id,
                "path": rel,
                "sizeBytes": actual_size,
                "sha256": actual_sha,
            }
        )

    report["verifiedCount"] = len(verified_entries)
    report["computedDigest"] = bf.compute_bundle_digest(verified_entries)
    if report["declaredDigest"] != report["computedDigest"]:
        report["errors"].append(
            "bundleDigest mismatch "
            f"(declared {report['declaredDigest']!r}, "
            f"computed {report['computedDigest']!r})"
        )
    if report["verifiedCount"] != report["assetCount"]:
        report["errors"].append(
            f"verified {report['verifiedCount']} of {report['assetCount']} assets"
        )

    report["extraFiles"] = _list_extra_files(bundle_dir, expected)
    if report["extraFiles"]:
        report["warnings"].append(
            "unexpected files are not covered by the bundle digest: "
            + ", ".join(report["extraFiles"])
        )

    report["ok"] = not report["errors"]
    return report


def unpack_bundle(bundle_dir: Path, output_dir: Path) -> dict:
    """Verify ``bundle_dir``, then copy it to a fresh ``output_dir`` and verify."""
    report = verify_bundle(bundle_dir)
    bundle_dir = Path(bundle_dir).resolve()
    output_dir = Path(output_dir).resolve()
    report["output"] = output_dir.as_posix()
    report["unpacked"] = False
    if not report["ok"]:
        return report

    if output_dir.exists():
        if not output_dir.is_dir():
            raise BundleUnpackError(
                f"output path exists and is not a directory: {output_dir}"
            )
        if any(output_dir.iterdir()):
            raise BundleUnpackError(
                f"output directory must be absent or empty: {output_dir}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = bf.load_json(bundle_dir / "bundle-manifest.json")
    for entry in manifest.get("assets", []):
        rel = entry["path"]
        src = bundle_dir / rel
        dst = output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    shutil.copyfile(bundle_dir / "bundle-manifest.json", output_dir / "bundle-manifest.json")
    source_manifest = manifest.get("sourceManifest")
    if isinstance(source_manifest, str):
        source = bundle_dir / source_manifest
        if source.is_file():
            destination = output_dir / source_manifest
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

    output_report = verify_bundle(output_dir)
    report["unpacked"] = True
    report["outputDigest"] = output_report["computedDigest"]
    report["outputOk"] = output_report["ok"]
    report["outputErrors"] = output_report["errors"]
    if not output_report["ok"]:
        report["errors"].extend(
            f"unpacked output: {error}" for error in output_report["errors"]
        )
    report["ok"] = report["ok"] and output_report["ok"]
    return report


def write_verify_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bf.write_json(path, report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify and optionally unpack a deterministic asset bundle."
    )
    parser.add_argument(
        "--bundle",
        default="Tools/AssetPack/bundle_out",
        help="packed bundle directory (contains bundle-manifest.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="optional fresh directory to unpack verified files into",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="optional path for a deterministic JSON verification report",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    bundle_dir = Path(args.bundle).expanduser().resolve()
    if not bundle_dir.is_dir():
        print(f"ENVIRONMENT ERROR: bundle directory not found: {bundle_dir}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    output_dir = Path(args.output).expanduser().resolve() if args.output else None
    try:
        if output_dir is not None:
            report = unpack_bundle(bundle_dir, output_dir)
        else:
            report = verify_bundle(bundle_dir)
    except (BundleUnpackError, bf.BundleFormatError) as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    if args.report:
        write_verify_report(report, Path(args.report).expanduser().resolve())

    print(
        f"BUNDLE bundleFormat={report['bundleFormat']} "
        f"assetPackId={report['assetPackId']} "
        f"assets={report['assetCount']} "
        f"verified={report['verifiedCount']} "
        f"digest={report['computedDigest']}"
    )
    for warning in report["warnings"]:
        print(f"WARN: {warning}")
    if output_dir is not None:
        print(
            f"UNPACKED output={report.get('output')} "
            f"outputDigest={report.get('outputDigest')} "
            f"outputOk={report.get('outputOk')}"
        )
        for error in report.get("outputErrors", []):
            print(f"OUTPUT ERROR: {error}")
    for error in report["errors"]:
        print(f"ERROR: {error}")
    if not report["ok"]:
        print(f"FAIL: bundle verification failed ({len(report['errors'])} error(s))")
        return EXIT_VERIFICATION
    print("OK: bundle verified")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
