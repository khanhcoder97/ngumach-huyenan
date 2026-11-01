#!/usr/bin/env python3
"""Build, check and diff Bến Mưa candidate bundles (OPC-11).

Examples:
    python Implementation/Tools/ContentPipeline/content_pipeline.py build
    python Implementation/Tools/ContentPipeline/content_pipeline.py build --check
    python Implementation/Tools/ContentPipeline/content_pipeline.py check --require-resolved
    python Implementation/Tools/ContentPipeline/content_pipeline.py diff old.json new.json
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:  # Direct execution from the tool directory.
    from compiler import (
        DEFAULT_ROOT,
        OUTPUT_REL,
        canonical_bytes,
        compile_bundle,
        output_path,
    )
    from validation import field_diff, format_diff, load_json_file, validate_bundle
except ImportError:  # Import as part of the ContentPipeline package.
    from .compiler import (
        DEFAULT_ROOT,
        OUTPUT_REL,
        canonical_bytes,
        compile_bundle,
        output_path,
    )
    from .validation import field_diff, format_diff, load_json_file, validate_bundle


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path(DEFAULT_ROOT).resolve()


def _print_errors(errors: list[str]) -> None:
    print(f"FAIL: {len(errors)} validation error(s)", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)


def _print_blocking(bundle: dict) -> None:
    print("BLOCKED: unresolved fields prevent activation", file=sys.stderr)
    for candidate in bundle.get("candidates", []):
        for entry in candidate.get("unresolved", []):
            if entry.get("blocking"):
                print(
                    f" - {candidate.get('candidateId')} {entry.get('path')}: "
                    f"{entry.get('reason')}",
                    file=sys.stderr,
                )


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        with open(temporary, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _summarize(bundle: dict, path: Path) -> None:
    summary = bundle["summary"]
    print(f"output: {path}")
    print(f"status: {bundle['status']}")
    print(f"bundleDigest: {bundle['bundleDigest']}")
    print(
        "candidates: "
        f"{summary['candidateCount']} total, "
        f"{summary['readyCount']} ready, "
        f"{summary['blockedCount']} blocked, "
        f"{summary['unresolvedCount']} unresolved"
    )
    if not bundle["activation"]["eligible"]:
        print(f"activation: blocked — {bundle['activation']['reason']}")


def command_build(args) -> int:
    root = _root(args.root)
    ctx, bundle = compile_bundle(root)
    errors = validate_bundle(bundle, ctx, root)
    if errors:
        _print_errors(errors)
        return 1
    data = canonical_bytes(bundle)
    path = Path(args.output).resolve() if args.output else output_path(root)
    if args.check:
        try:
            existing = path.read_bytes()
        except OSError:
            print(f"STALE: {path} does not exist; run build", file=sys.stderr)
            return 1
        if existing != data:
            print(f"STALE: {path} differs from a fresh build", file=sys.stderr)
            return 1
        print(f"OK: {path} is up to date")
        _summarize(bundle, path)
    else:
        _write_atomic(path, data)
        _summarize(bundle, path)
    if args.require_resolved and not bundle["activation"]["eligible"]:
        _print_blocking(bundle)
        return 1
    return 0


def command_check(args) -> int:
    root = _root(args.root)
    ctx, _ = compile_bundle(root)
    bundle_path = Path(args.bundle)
    if not bundle_path.is_absolute():
        bundle_path = root / bundle_path  # Relative paths resolve against --root, not the CWD.
    bundle = load_json_file(bundle_path, "bundle")
    errors = validate_bundle(bundle, ctx, root)
    if errors:
        _print_errors(errors)
        return 1
    print(
        f"OK: {args.bundle} — {bundle['summary']['candidateCount']} candidates, "
        f"{bundle['summary']['unresolvedCount']} unresolved"
    )
    if args.require_resolved and not bundle["activation"]["eligible"]:
        _print_blocking(bundle)
        return 1
    return 0


def command_diff(args) -> int:
    old = load_json_file(Path(args.old).resolve(), "old")
    new = load_json_file(Path(args.new).resolve(), "new")
    changes = field_diff(old, new)
    sys.stdout.write(format_diff(changes, as_json=args.json))
    if args.json:
        if changes:
            print(f"{len(changes)} field difference(s)", file=sys.stderr)
    elif changes:
        print(f"{len(changes)} field difference(s)")
    else:
        print("no field differences")
    return 1 if changes else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="compile a fresh candidate bundle")
    build_parser.add_argument("--root", help="repository root (defaults to this checkout)")
    build_parser.add_argument("--output", help=f"output path (defaults to {OUTPUT_REL})")
    build_parser.add_argument(
        "--check",
        action="store_true",
        help="verify the checked-in bundle is byte-identical instead of writing",
    )
    build_parser.add_argument(
        "--require-resolved",
        action="store_true",
        help="exit non-zero when activation is blocked by unresolved fields",
    )
    build_parser.set_defaults(func=command_build)

    check_parser = subparsers.add_parser("check", help="validate an existing candidate bundle")
    check_parser.add_argument("--root", help="repository root (defaults to this checkout)")
    check_parser.add_argument(
        "--bundle",
        default=OUTPUT_REL,
        help=f"bundle path (defaults to {OUTPUT_REL})",
    )
    check_parser.add_argument(
        "--require-resolved",
        action="store_true",
        help="exit non-zero when activation is blocked by unresolved fields",
    )
    check_parser.set_defaults(func=command_check)

    diff_parser = subparsers.add_parser("diff", help="show field-level differences between two JSON files")
    diff_parser.add_argument("old")
    diff_parser.add_argument("new")
    diff_parser.add_argument("--json", action="store_true", help="emit a JSON change list")
    diff_parser.set_defaults(func=command_diff)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # Fail closed with a readable message.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
