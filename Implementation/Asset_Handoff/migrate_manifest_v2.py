#!/usr/bin/env python3
"""Dry-run migration from the legacy asset manifest to the OPC-06 v2 draft.

The tool only reads the source manifest. By default it prints a unified diff
between the legacy document and the proposed v2 document; it never edits the
Muse manifest in place. Use ``--output`` to write the proposal to a new file
after review, and ``--force`` only to replace that output file.

Migration is deliberately conservative:

* ``sprite_sheet`` is migrated only when it carries the eight canonical
  directions in order and exactly one animation with an unambiguous frame count.
  Width and height are derived as ``pixelWidth / framesPerDirection`` and
  ``pixelHeight / directionCount`` -- never by multiplying directions into both
  axes.
* ``vfx_sheet`` is not guessed from a frame count. It must already carry
  ``frameSize``, ``layout`` and ``isDirectional``; otherwise the tool reports a
  blocker and exits non-zero.
* Other kinds only receive the top-level ``manifestVersion: 2`` marker.

Usage (from the repository root):
  python Implementation/Asset_Handoff/migrate_manifest_v2.py
  python Implementation/Asset_Handoff/migrate_manifest_v2.py --quiet
  python Implementation/Asset_Handoff/migrate_manifest_v2.py --output out/manifest_v2.json
  python Implementation/Asset_Handoff/migrate_manifest_v2.py --show-json

Exit codes:
  0  migration is possible (dry-run) or the output was written
  1  migration is blocked, the output exists, or the request is unsafe
  2  environment or usage error
"""

import argparse
import copy
import difflib
import json
import sys
from pathlib import Path

import manifest_geometry

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"

ANIMATION_FIELDS = {
    "name",
    "fps",
    "loop",
    "framesPerDirection",
    "frames",
    "frameCount",
    "frameStart",
    "columnStart",
}


class MigrationBlocked(Exception):
    """The source cannot be migrated without a human decision."""


def load_manifest(path):
    raw = path.read_bytes()
    if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise MigrationBlocked(
            f"{path}: Git LFS pointer instead of file content "
            "(fetch the LFS objects first)"
        )
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise MigrationBlocked(f"{path}: invalid JSON ({exc})") from exc


def _frame_count(animation, label):
    for key in ("framesPerDirection", "frames", "frameCount"):
        if key in animation:
            value = animation[key]
            if not manifest_geometry.positive_int(value):
                raise MigrationBlocked(
                    f"{label}: animation field {key} must be an integer >= 1, found {value!r}"
                )
            return value
    raise MigrationBlocked(
        f"{label}: animation has no framesPerDirection/frames/frameCount"
    )


def _migrate_sprite_sheet(asset, label):
    directions = asset.get("directions")
    if not isinstance(directions, list) or tuple(directions) != manifest_geometry.DIRECTIONS:
        raise MigrationBlocked(
            f"{label}: sprite_sheet migration needs the eight canonical directions in "
            "order; set isDirectional/frameSize/layout manually instead of guessing"
        )
    animations = asset.get("animations")
    if not isinstance(animations, list) or len(animations) != 1:
        raise MigrationBlocked(
            f"{label}: sprite_sheet migration currently supports exactly one animation; "
            "multiple clips need explicit columnStart ranges"
        )
    animation = animations[0]
    if not isinstance(animation, dict):
        raise MigrationBlocked(f"{label}: animation entry is not an object")
    extra = sorted(set(animation) - ANIMATION_FIELDS)
    if extra:
        raise MigrationBlocked(
            f"{label}: animation has unsupported field(s) {extra}; refuse to drop data"
        )
    frames = _frame_count(animation, label)
    width, height = asset.get("pixelWidth"), asset.get("pixelHeight")
    if not manifest_geometry.positive_int(width) or not manifest_geometry.positive_int(height):
        raise MigrationBlocked(f"{label}: pixelWidth/pixelHeight must be positive integers")
    if width % frames:
        raise MigrationBlocked(
            f"{label}: pixelWidth {width} is not divisible by framesPerDirection {frames}"
        )
    if height % len(directions):
        raise MigrationBlocked(
            f"{label}: pixelHeight {height} is not divisible by directionCount "
            f"{len(directions)}"
        )

    migrated = copy.deepcopy(asset)
    migrated["isDirectional"] = True
    migrated["layout"] = "direction_rows"
    migrated["frameSize"] = {"width": width // frames, "height": height // len(directions)}

    new_animation = copy.deepcopy(animation)
    for key in ("frames", "frameCount"):
        new_animation.pop(key, None)
    new_animation["framesPerDirection"] = frames
    if "frameStart" in new_animation:
        raise MigrationBlocked(
            f"{label}: frameStart is only valid for strip layout; remove it before migration"
        )
    start = new_animation.get("columnStart", 0)
    if not manifest_geometry.non_negative_int(start):
        raise MigrationBlocked(
            f"{label}: columnStart must be an integer >= 0, found {start!r}"
        )
    columns = width // frames
    if start + frames > columns:
        raise MigrationBlocked(
            f"{label}: columnStart {start} + {frames} frames exceeds the {columns} "
            "frame columns in the sheet"
        )
    if start == 0:
        new_animation.pop("columnStart", None)
    migrated["animations"] = [new_animation]
    return migrated


def _migrate_vfx_sheet(asset, label):
    required = ("frameSize", "layout", "isDirectional")
    missing = [key for key in required if key not in asset]
    if missing:
        raise MigrationBlocked(
            f"{label}: vfx_sheet migration requires explicit {missing}; a frame count "
            "alone does not describe the sheet grid"
        )
    if asset.get("isDirectional") is not False or asset.get("layout") != "strip":
        raise MigrationBlocked(
            f"{label}: vfx_sheet migration currently accepts only isDirectional=false "
            "with layout='strip'"
        )
    if manifest_geometry.frame_size_of(asset) is None:
        raise MigrationBlocked(
            f"{label}: frameSize must contain positive integer width/height"
        )
    return copy.deepcopy(asset)


def _migrate_other_kind(asset, label):
    if "frameSize" in asset or "layout" in asset:
        raise MigrationBlocked(
            f"{label}: frameSize/layout are only valid on sprite_sheet and vfx_sheet"
        )
    if asset.get("isDirectional") is True:
        raise MigrationBlocked(
            f"{label}: only sprite_sheet supports isDirectional=true"
        )
    if asset.get("directions"):
        raise MigrationBlocked(
            f"{label}: static and non-sheet kinds must not declare directions in v2"
        )
    return copy.deepcopy(asset)


def migrate_manifest(manifest):
    """Return ``(migrated, problems, changed)`` without mutating ``manifest``."""
    version = manifest.get("manifestVersion", 1)
    if version == 2:
        return copy.deepcopy(manifest), [], False
    if isinstance(version, bool) or version not in (1, None):
        return None, [
            f"unsupported manifestVersion {version!r}; supported versions are "
            "1 (legacy, may be omitted) and 2"
        ], False
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        return None, ["manifest has no assets to migrate"], False

    migrated = {"manifestVersion": 2}
    for key, value in manifest.items():
        if key == "manifestVersion":
            continue
        migrated[key] = copy.deepcopy(value)

    problems = []
    new_assets = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            problems.append(f"assets[{index}]: entry is not an object")
            new_assets.append(copy.deepcopy(asset))
            continue
        label = asset.get("assetId") or f"assets[{index}]"
        kind = asset.get("kind")
        try:
            if kind == "sprite_sheet":
                new_assets.append(_migrate_sprite_sheet(asset, label))
            elif kind == "vfx_sheet":
                new_assets.append(_migrate_vfx_sheet(asset, label))
            else:
                new_assets.append(_migrate_other_kind(asset, label))
        except MigrationBlocked as exc:
            problems.append(str(exc))
            new_assets.append(copy.deepcopy(asset))
    migrated["assets"] = new_assets
    return migrated, problems, True


def unified_diff(before, after):
    before_text = json.dumps(before, ensure_ascii=False, indent=2) + "\n"
    after_text = json.dumps(after, ensure_ascii=False, indent=2) + "\n"
    return "".join(
        difflib.unified_diff(
            before_text.splitlines(keepends=True),
            after_text.splitlines(keepends=True),
            fromfile="legacy manifest",
            tofile="opc-06 v2 proposal",
        )
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Dry-run migration from the legacy asset manifest to OPC-06 v2."
    )
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository root (default: auto-detect)")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="source manifest, relative to --root")
    parser.add_argument("--output", default=None,
                        help="write the proposed v2 manifest to this new path instead of printing a diff")
    parser.add_argument("--force", action="store_true",
                        help="replace --output if it already exists; the source manifest is never written")
    parser.add_argument("--show-json", action="store_true",
                        help="print the proposed v2 JSON instead of a diff (dry-run)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="no diff on success; useful for CI dry-run checks")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    source = (root / args.manifest.replace("\\", "/")).resolve()
    try:
        manifest = load_manifest(source)
    except MigrationBlocked as exc:
        print(f"MIGRATION BLOCKED: {exc}", file=sys.stderr)
        return 1

    migrated, problems, changed = migrate_manifest(manifest)
    if problems:
        print("MIGRATION BLOCKED:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print("No file was written. Resolve the blockers or author v2 fields manually.", file=sys.stderr)
        return 1
    if not changed:
        if not args.quiet:
            print(f"already v2: {source}")
        return 0

    if args.output:
        output = (root / args.output.replace("\\", "/")).resolve()
        try:
            output.relative_to(root)
        except ValueError:
            print(f"MIGRATION BLOCKED: --output must stay inside {root}", file=sys.stderr)
            return 1
        if output == source:
            print("MIGRATION BLOCKED: --output must not overwrite the source manifest", file=sys.stderr)
            return 1
        if output.exists() and not args.force:
            print(f"MIGRATION BLOCKED: output exists: {output} (use --force to replace it)", file=sys.stderr)
            return 1
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(migrated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {output}")
        return 0

    if args.show_json:
        print(json.dumps(migrated, ensure_ascii=False, indent=2))
    elif not args.quiet:
        print(unified_diff(manifest, migrated), end="")
    if not args.quiet:
        print("dry-run only: source manifest was not modified", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
