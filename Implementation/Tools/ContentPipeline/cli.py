#!/usr/bin/env python3
"""Build/check/diff review-only content candidates. Never activates game data."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

try:
    from compiler import canonical_bytes, compile_bundle, output_path
    from compiler_core import DEFAULT_ROOT, PipelineError, PipelineEnvironmentError
    from validation import field_diff, load_json_file, validate_bundle
except ImportError:
    from .compiler import canonical_bytes, compile_bundle, output_path
    from .compiler_core import DEFAULT_ROOT, PipelineError, PipelineEnvironmentError
    from .validation import field_diff, load_json_file, validate_bundle


def summary(bundle):
    return {"bundleDigest": bundle["bundleDigest"], "status": bundle["status"],
            "summary": bundle["summary"], "activation": bundle["activation"],
            "unresolved": [{"candidateId": c["candidateId"], **entry}
                           for c in bundle["candidates"] for entry in c["unresolved"]]}


def atomic_write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".candidate-", delete=False) as file:
        temporary = Path(file.name)
        file.write(data)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["build", "check", "validate", "inspect"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", type=Path, default=DEFAULT_ROOT)
        cmd.add_argument("--bundle", type=Path, help="existing candidate file (check/validate/inspect)")
        cmd.add_argument("--require-ready", action="store_true", help="exit 3 if unresolved fields block review readiness")
        if name == "build":
            cmd.add_argument("--output", type=Path)
    diff = sub.add_parser("diff")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "diff":
            changes = field_diff(load_json_file(args.before, "before"), load_json_file(args.after, "after"))
            print(json.dumps(changes, ensure_ascii=False, sort_keys=True, indent=2))
            return 0
        root = args.root.resolve()
        ctx, expected = compile_bundle(root)
        if args.command == "build":
            bundle = expected
        else:
            path = (args.bundle or output_path(root)).resolve()
            bundle = load_json_file(path, "candidate")
        errors = validate_bundle(bundle, ctx, root)
        if errors:
            raise PipelineError("\n".join(errors))
        if args.command == "check" and canonical_bytes(bundle) != canonical_bytes(expected):
            raise PipelineError("candidate bytes differ from current compiler output; rebuild and review field diff")
        print(json.dumps(summary(bundle), ensure_ascii=False, sort_keys=True, indent=2))
        if args.require_ready and not bundle["activation"]["eligible"]:
            return 3
        if args.command == "build":
            path = (args.output or output_path(root)).resolve()
            # Inside the repository only candidate outputs may be written.
            # An explicit external scratch file remains useful to CI/reviewers.
            if path.is_relative_to(root) and not path.is_relative_to((root / "Implementation/Content/BuildCandidates").resolve()):
                raise PipelineError("output inside repository must stay under Implementation/Content/BuildCandidates")
            atomic_write(path, canonical_bytes(bundle))
        return 0
    except PipelineEnvironmentError as error:
        print("ENVIRONMENT ERROR: " + str(error))
        return 2
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as error:
        print("CONTENT ERROR: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
