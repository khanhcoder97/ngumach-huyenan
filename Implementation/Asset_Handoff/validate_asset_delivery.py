#!/usr/bin/env python3
"""Validate a Muse asset delivery manifest without Unity, .NET or third-party packages.

Standard library only. The checks follow OPC-05 in
Implementation/Work_Orders/02_OPENCODE_CLIENT.md:

  1. Manifest structure is validated against
     Implementation/Asset_Handoff/asset_delivery_manifest.schema.json using the shared
     minimal schema validator in Implementation/Tools/json_schema.py.
  2. ``assetId`` and ``path`` values are unique; every ``path`` and ``previewPath`` stays
     inside the repository and points at a file that really exists.
  3. PNG size metadata is compared with the real image by reading the IHDR header. A
     committed Git LFS pointer instead of image content is rejected.
  4. ``pixelsPerUnit`` equals the schema constant (20), asset paths live under an agreed
     art root, ``sourceLicense`` is ``original`` and sprite sheets carry the eight
     canonical directions in the locked order.
  5. Animation entries carry a name, a frame count and a sane FPS. Animations are not
     required to share a frame count.
  6. Every finding names the asset id, the file and the field, and the exit code is
     non-zero when anything fails.

Usage (from the repository root):
  python Implementation/Asset_Handoff/validate_asset_delivery.py
  python Implementation/Asset_Handoff/validate_asset_delivery.py --allow-missing-manifest
  python Implementation/Asset_Handoff/validate_asset_delivery.py --skip-file-checks \
      --manifest Implementation/Asset_Handoff/muse_delivery_manifest.example.json
  git diff --name-only origin/main...HEAD > changed.txt
  python Implementation/Asset_Handoff/validate_asset_delivery.py --changed-files changed.txt

Exit codes:
  0  everything passed (warnings are allowed)
  1  validation failures found
  2  environment or usage error (missing schema, unreadable manifest, bad JSON)
"""

import argparse
import json
import re
import struct
import sys
from pathlib import Path

import manifest_geometry

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
DEFAULT_SCHEMA = "Implementation/Asset_Handoff/asset_delivery_manifest.schema.json"
V2_SCHEMA = "Implementation/Asset_Handoff/asset_delivery_manifest.v2.schema.json"

# The locked eight-direction order of the pixel art standard (clockwise from north).
DIRECTIONS = manifest_geometry.DIRECTIONS
DIRECTION_REQUIRED_KINDS = ("sprite_sheet",)
# Kinds whose delivered file is not an image, so no IHDR comparison is possible.
NON_IMAGE_KINDS = ("tilemap", "animation")
IMAGE_SUFFIXES = (".png",)
PREVIEW_SUFFIXES = (".png", ".gif")
FRAME_COUNT_KEYS = ("framesPerDirection", "frames", "frameCount")
MAX_FPS = 60.0

# Roots where Muse delivers art, per Implementation/Asset_Handoff/GITHUB_COLLABORATION.md.
ART_ROOTS = (
    "Client/Assets/Art",
    "Client/Assets/UI/Art",
    "Client/Assets/Tilemaps",
    "Client/Assets/VFX",
    "Client/Assets/Animation",
)

LFS_POINTER_PREFIX = "version https://git-lfs.github.com/spec/v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PATH_CHARS_RE = re.compile(r"^[A-Za-z0-9._~/-]+$")
SNAKE_CASE_RE = re.compile(r"^[a-z0-9][a-z0-9_.~-]*$")

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_ENVIRONMENT = 2


class EnvironmentProblem(Exception):
    """A tooling or input problem the manifest author cannot fix."""


def load_json(path):
    """Read a JSON file, rejecting a Git LFS pointer with an explicit message."""
    if not path.is_file():
        raise EnvironmentProblem(f"file not found: {path}")
    raw = path.read_bytes()
    if raw.startswith(LFS_POINTER_PREFIX.encode("ascii")):
        raise EnvironmentProblem(
            f"{path}: Git LFS pointer instead of file content "
            "(fetch the LFS objects, in CI use actions/checkout with lfs: true)"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EnvironmentProblem(f"{path}: not valid UTF-8 ({exc})") from exc
    try:
        return json.loads(text)
    except ValueError as exc:
        raise EnvironmentProblem(f"{path}: invalid JSON ({exc})") from exc


def schema_validator():
    """Import the shared minimal JSON Schema validator shipped in Implementation/Tools."""
    tools = str(REPO_ROOT / "Implementation" / "Tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    try:
        import json_schema
    except ImportError as exc:  # pragma: no cover - depends on repository layout
        raise EnvironmentProblem(f"cannot import Implementation/Tools/json_schema.py: {exc}") from exc
    return json_schema.validate


class PngInfo:
    """Geometry and header flags taken from the PNG IHDR chunk."""

    __slots__ = ("width", "height", "bit_depth", "color_type", "interlace")

    def __init__(self, width, height, bit_depth, color_type, interlace):
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        self.color_type = color_type
        self.interlace = interlace

    def __repr__(self):  # pragma: no cover - debugging aid
        return (f"PngInfo(width={self.width}, height={self.height}, bit_depth={self.bit_depth}, "
                f"color_type={self.color_type}, interlace={self.interlace})")


def _read_head(path, size=64):
    try:
        with path.open("rb") as handle:
            return handle.read(size)
    except OSError as exc:
        raise ValueError(f"file cannot be read ({exc.strerror or exc})") from exc


def read_png_ihdr(path):
    """Return the PNG geometry, or raise ValueError explaining why the file is unusable."""
    head = _read_head(path)
    if head.startswith(LFS_POINTER_PREFIX.encode("ascii")):
        raise ValueError("file is a Git LFS pointer, not an image (LFS objects were not fetched)")
    if not head.startswith(PNG_SIGNATURE):
        if head[:2] == b"\xff\xd8":
            raise ValueError("file is JPEG; the pixel art pipeline delivers PNG")
        raise ValueError("file does not start with the PNG signature")
    offset = len(PNG_SIGNATURE)
    if len(head) < offset + 8:
        raise ValueError("PNG is truncated before the IHDR chunk header")
    (chunk_length,) = struct.unpack_from(">I", head, offset)
    chunk_type = head[offset + 4:offset + 8]
    if chunk_type != b"IHDR":
        raise ValueError(f"first PNG chunk is {chunk_type.decode('latin-1', 'replace')}, expected IHDR")
    if chunk_length < 13:
        raise ValueError(f"IHDR chunk length {chunk_length} is shorter than 13 bytes")
    if len(head) < offset + 8 + 13:
        raise ValueError("PNG is truncated inside the IHDR chunk")
    width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack_from(
        ">IIBBBBB", head, offset + 8)
    if width == 0 or height == 0:
        raise ValueError(f"IHDR declares an empty image ({width}x{height})")
    return PngInfo(width, height, bit_depth, color_type, interlace)


def read_gif_size(path):
    head = _read_head(path)
    if head.startswith(LFS_POINTER_PREFIX.encode("ascii")):
        raise ValueError("file is a Git LFS pointer, not an image (LFS objects were not fetched)")
    if head[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("file does not start with a GIF signature")
    if len(head) < 13:
        raise ValueError("GIF is truncated before the logical screen descriptor")
    return struct.unpack_from("<HH", head, 6)


def inspect_repo_path(value):
    """Return (normalised path, problem) for a manifest path string."""
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


def resolve_inside_root(root, rel):
    """Join a repo-relative path and refuse to leave the repository."""
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def under_art_root(rel):
    return any(rel == root or rel.startswith(root + "/") for root in ART_ROOTS)


class Report:
    """Collects findings in the required 'asset id / file / field' shape."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    @staticmethod
    def _line(level, asset_id, file, field, message):
        return f"{level:7s} [{asset_id or '-'}] file={file or '-'} field={field or '-'} :: {message}"

    def error(self, asset_id, file, field, message):
        self.errors.append(self._line("ERROR", asset_id, file, field, message))

    def warn(self, asset_id, file, field, message):
        self.warnings.append(self._line("WARN", asset_id, file, field, message))


def schema_constants(schema):
    """Take the shared limits from the delivery schema instead of duplicating them."""
    item = schema["properties"]["assets"]["items"]["properties"]
    pixels_per_unit = item["pixelsPerUnit"].get("const", 20)
    path_pattern = item["path"].get("pattern", "^Client/Assets/")
    kinds = tuple(item["kind"]["enum"])
    return pixels_per_unit, path_pattern, kinds


def frame_count_of(animation):
    for key in FRAME_COUNT_KEYS:
        if key in animation:
            return key, animation[key]
    return None, None


def check_directions(label, asset, report):
    directions = asset.get("directions")
    kind = asset.get("kind")
    path = asset.get("path")
    if directions is None:
        if kind in DIRECTION_REQUIRED_KINDS:
            report.error(label, path, "directions",
                         f"kind '{kind}' must list the eight directions {list(DIRECTIONS)}")
        return
    if not isinstance(directions, list):
        report.error(label, path, "directions", "must be an array of direction codes")
        return
    unknown = [d for d in directions if d not in DIRECTIONS]
    if unknown:
        report.error(label, path, "directions",
                     f"unknown direction(s) {unknown}; allowed are {list(DIRECTIONS)}")
    duplicates = sorted({d for d in directions if list(directions).count(d) > 1})
    if duplicates:
        report.error(label, path, "directions", f"duplicate direction(s) {duplicates}")
    if kind in DIRECTION_REQUIRED_KINDS and not unknown and not duplicates:
        if len(directions) != len(DIRECTIONS):
            missing = [d for d in DIRECTIONS if d not in directions]
            report.error(label, path, "directions",
                         f"expected {len(DIRECTIONS)} directions, found {len(directions)} "
                         f"(missing {missing})")
        elif tuple(directions) != DIRECTIONS:
            report.error(label, path, "directions",
                         f"direction order must be {list(DIRECTIONS)}, found {list(directions)}")


def check_animations(label, asset, report):
    animations = asset.get("animations")
    path = asset.get("path")
    if animations is None:
        return
    if not isinstance(animations, list):
        report.error(label, path, "animations", "must be an array")
        return
    for index, animation in enumerate(animations):
        field = f"animations[{index}]"
        if not isinstance(animation, dict):
            report.error(label, path, field, "animation entry is not an object")
            continue
        name = animation.get("name")
        if not isinstance(name, str) or not name.strip():
            report.error(label, path, f"{field}.name", "animation needs a non-empty name")
        key, frames = frame_count_of(animation)
        if frames is None:
            report.error(label, path, field,
                         f"animation needs a frame count ({' or '.join(FRAME_COUNT_KEYS)})")
        elif isinstance(frames, bool) or not isinstance(frames, int) or frames < 1:
            report.error(label, path, f"{field}.{key}",
                         f"frame count must be an integer >= 1, found {frames!r}")
        fps = animation.get("fps")
        if fps is None:
            report.error(label, path, f"{field}.fps", "animation needs an fps value")
        elif isinstance(fps, bool) or not isinstance(fps, (int, float)) or not 0 < float(fps) <= MAX_FPS:
            report.error(label, path, f"{field}.fps",
                         f"fps must be greater than 0 and at most {MAX_FPS:g}, found {fps!r}")
        if "loop" in animation and not isinstance(animation["loop"], bool):
            report.error(label, path, f"{field}.loop", "loop must be a boolean")


def check_asset_file(label, asset, target, rel, info, report, *, version=1):
    """Compare manifest geometry and frame grid with the real PNG header."""
    width, height = asset.get("pixelWidth"), asset.get("pixelHeight")
    if isinstance(width, int) and width != info.width:
        report.error(label, rel, "pixelWidth",
                     f"manifest says {width}px but the PNG IHDR says {info.width}px")
    if isinstance(height, int) and height != info.height:
        report.error(label, rel, "pixelHeight",
                     f"manifest says {height}px but the PNG IHDR says {info.height}px")
    if info.interlace:
        report.warn(label, rel, "path", "interlaced PNG (Adam7) is unusual for pixel art")
    if info.bit_depth not in (1, 2, 4, 8):
        report.warn(label, rel, "path", f"unusual PNG bit depth {info.bit_depth}")
    if version == 1:
        _check_frame_grid(label, rel, asset, info, report)


def _check_frame_grid(label, rel, asset, info, report):
    """Advisory only: the delivery schema has no frame width/height field yet."""
    directions, animations = asset.get("directions"), asset.get("animations")
    if not isinstance(directions, list) or not directions:
        return
    if not isinstance(animations, list) or not animations:
        return
    counts = [value for animation in animations if isinstance(animation, dict)
              for _, value in [frame_count_of(animation)]
              if isinstance(value, int) and not isinstance(value, bool) and value > 0]
    if not counts:
        return
    frames, rows = max(counts), len(directions)
    if info.width % frames == 0 and info.height % rows == 0:
        return
    report.warn(label, rel, "animations",
                f"{frames} frame(s) x {rows} direction(s) do not tile the "
                f"{info.width}x{info.height} sheet on whole pixels; frame size is not "
                "part of the delivery schema yet (see the integration request)")


def validate_manifest(manifest, schema, root, *, check_files=True, changed=None,
                      manifest_rel=DEFAULT_MANIFEST):
    """Validate a manifest document; returns (errors, warnings) lists of strings.

    ``manifestVersion`` absent or 1 selects the legacy v1 rules; 2 selects the
    OPC-06 v2 geometry rules. The caller picks the matching schema; this function
    still rejects unsupported versions before schema validation so the message is
    precise instead of a bare ``const`` mismatch.
    """
    report = Report()
    version = manifest.get("manifestVersion", 1)
    if isinstance(version, bool) or version not in (1, 2):
        report.error(
            None,
            manifest_rel,
            "manifestVersion",
            f"unsupported manifestVersion {version!r}; supported versions are "
            "1 (legacy, may be omitted) and 2",
        )
        return report.errors, report.warnings
    validate = schema_validator()
    schema_errors = []
    validate(manifest, schema, "manifest", schema_errors)
    for message in schema_errors:
        report.error(_asset_label(manifest, message), None, None, message)
    if schema_errors:
        return report.errors, report.warnings

    pixels_per_unit, path_pattern, _kinds = schema_constants(schema)
    if manifest.get("sourceLicense") != "original":
        report.error(None, manifest_rel, "sourceLicense", "must be 'original'")
    if manifest.get("owner") != "Muse":
        report.error(None, manifest_rel, "owner", "asset packs are delivered by Muse")

    seen_ids, seen_paths, seen_paths_ci, seen_previews = {}, {}, {}, {}
    for index, asset in enumerate(manifest.get("assets") or []):
        if not isinstance(asset, dict):
            report.error(None, None, f"assets[{index}]", "asset entry is not an object")
            continue
        label = asset.get("assetId") or f"assets[{index}]"
        raw_path = asset.get("path")
        rel, problem = inspect_repo_path(raw_path)
        if problem:
            report.error(label, raw_path if isinstance(raw_path, str) else None, "path", problem)

        if isinstance(asset.get("assetId"), str):
            if asset["assetId"] in seen_ids:
                report.error(label, rel, "assetId",
                             f"duplicate assetId, first declared at assets[{seen_ids[asset['assetId']]}]")
            else:
                seen_ids[asset["assetId"]] = index

        ppu = asset.get("pixelsPerUnit")
        if ppu != pixels_per_unit:
            report.error(label, rel, "pixelsPerUnit", f"expected {pixels_per_unit}, found {ppu!r}")

        kind = asset.get("kind")
        target = None
        if rel is not None:
            if not re.match(path_pattern, rel):
                report.error(label, rel, "path", f"must match the manifest pattern {path_pattern}")
            if not under_art_root(rel):
                report.error(label, rel, "path",
                             "asset must live under one of the agreed art roots: "
                             + ", ".join(ART_ROOTS))
            target = resolve_inside_root(root, rel)
            if target is None:
                report.error(label, rel, "path", "path escapes the repository root")
            elif rel in seen_paths:
                report.error(label, rel, "path",
                             f"duplicate path, already used by assetId {seen_paths[rel]}")
            else:
                seen_paths[rel] = label
                folded = rel.lower()
                if folded in seen_paths_ci:
                    report.error(label, rel, "path",
                                 f"path differs only by case from assetId {seen_paths_ci[folded]}")
                seen_paths_ci[folded] = label
                base = rel.rsplit("/", 1)[-1]
                if not SNAKE_CASE_RE.match(base):
                    report.warn(label, rel, "path",
                                "file name is not lowercase snake_case (naming convention)")
            if isinstance(kind, str) and kind not in NON_IMAGE_KINDS and not rel.lower().endswith(IMAGE_SUFFIXES):
                report.error(label, rel, "path",
                             f"kind '{kind}' must deliver a PNG file")

        if rel is not None and target is not None and check_files:
            if not target.is_file():
                report.error(label, rel, "path", "declared file does not exist in the repository")
            elif rel.lower().endswith(IMAGE_SUFFIXES):
                try:
                    info = read_png_ihdr(target)
                except ValueError as exc:
                    report.error(label, rel, "path", f"unreadable PNG: {exc}")
                else:
                    check_asset_file(label, asset, target, rel, info, report, version=version)

        preview = asset.get("previewPath")
        preview_rel, preview_problem = inspect_repo_path(preview)
        if preview_problem:
            report.error(label, preview if isinstance(preview, str) else None, "previewPath",
                         preview_problem)
        elif preview_rel is not None:
            if not preview_rel.startswith("Client/Assets/"):
                report.error(label, preview_rel, "previewPath",
                             "preview must live under Client/Assets/")
            preview_target = resolve_inside_root(root, preview_rel)
            if preview_target is None:
                report.error(label, preview_rel, "previewPath", "preview path escapes the repository root")
            elif preview_rel in seen_previews:
                report.warn(label, preview_rel, "previewPath",
                            f"preview shared with assetId {seen_previews[preview_rel]}")
            else:
                seen_previews[preview_rel] = label
            if not preview_rel.lower().endswith(PREVIEW_SUFFIXES):
                report.warn(label, preview_rel, "previewPath", "preview is neither PNG nor GIF")
            if check_files and preview_target is not None:
                if not preview_target.is_file():
                    report.error(label, preview_rel, "previewPath",
                                 "declared preview file does not exist")
                else:
                    lower = preview_rel.lower()
                    try:
                        if lower.endswith(".gif"):
                            read_gif_size(preview_target)
                        elif lower.endswith(IMAGE_SUFFIXES):
                            read_png_ihdr(preview_target)
                    except ValueError as exc:
                        report.error(label, preview_rel, "previewPath", f"unreadable preview: {exc}")

        if version == 2:
            manifest_geometry.validate_v2_asset(label, asset, report)
        else:
            check_directions(label, asset, report)
        check_animations(label, asset, report)

    _check_cross_references(manifest, report)
    if changed is not None:
        check_changed_files(manifest, changed, report, manifest_rel)
    return report.errors, report.warnings


def _check_cross_references(manifest, report):
    known = {asset.get("assetId") for asset in manifest.get("assets") or [] if isinstance(asset, dict)}
    for index, asset in enumerate(manifest.get("assets") or []):
        if not isinstance(asset, dict):
            continue
        replaced = asset.get("replacesAssetId")
        if isinstance(replaced, str) and replaced and replaced not in known:
            report.warn(asset.get("assetId") or f"assets[{index}]", asset.get("path"),
                        "replacesAssetId",
                        f"'{replaced}' is not declared in this manifest "
                        "(it must exist in an earlier pack)")


def check_changed_files(manifest, changed, report, manifest_rel):
    """Every art PNG touched by the change set must be described by the manifest."""
    listed = {manifest_rel}
    for asset in manifest.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        for field in ("path", "previewPath"):
            value, _ = inspect_repo_path(asset.get(field))
            if value:
                listed.add(value)
    for raw in changed:
        rel = (raw or "").strip().replace("\\", "/")
        if not rel or not rel.lower().endswith(".png"):
            continue
        if under_art_root(rel) and rel not in listed:
            report.error(None, rel, "assets",
                         "changed PNG is not referenced by any manifest 'path' or 'previewPath'")


def _asset_label(manifest, message):
    """Best-effort assetId for a schema error keyed by array index."""
    match = re.search(r"assets\[(\d+)\]", message)
    if not match:
        return None
    assets = manifest.get("assets") or []
    index = int(match.group(1))
    if index < len(assets) and isinstance(assets[index], dict):
        return assets[index].get("assetId")
    return None


def schema_path_for(manifest):
    """Pick the schema that matches the manifest version marker."""
    version = manifest.get("manifestVersion", 1)
    if version == 1:
        return DEFAULT_SCHEMA
    if version == 2:
        return V2_SCHEMA
    return None


def build_parser():
    parser = argparse.ArgumentParser(description="Validate a Muse asset delivery manifest.")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository root (default: auto-detect)")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="manifest path, relative to --root")
    parser.add_argument("--schema", default=None,
                        help="explicit schema path; default: select v1 or v2 from manifestVersion")
    parser.add_argument("--changed-files", default=None,
                        help="file with one repo-relative path per line, or '-' for stdin")
    parser.add_argument("--allow-missing-manifest", action="store_true",
                        help="exit 0 when no manifest exists yet and no art PNG changed")
    parser.add_argument("--skip-file-checks", action="store_true",
                        help="check structure and metadata only, do not read asset files")
    parser.add_argument("--report", default=None, help="write all findings to this file")
    parser.add_argument("-q", "--quiet", action="store_true", help="print findings only on failure")
    return parser


def read_changed_files(argument):
    if not argument:
        return None
    if argument == "-":
        return [line for line in sys.stdin.read().splitlines() if line.strip()]
    path = Path(argument)
    if not path.is_file():
        raise EnvironmentProblem(f"--changed-files: file not found: {path}")
    return [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def art_png_changes(changed):
    return [line.strip().replace("\\", "/") for line in (changed or [])
            if line.strip().replace("\\", "/").lower().endswith(".png")
            and under_art_root(line.strip().replace("\\", "/"))]


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    manifest_rel = args.manifest.replace("\\", "/")
    try:
        changed = read_changed_files(args.changed_files)
        manifest_path = root / manifest_rel
        if not manifest_path.is_file():
            touched = art_png_changes(changed)
            if args.allow_missing_manifest and not touched:
                print(f"OK: no asset manifest at {manifest_rel} yet and no art PNG changed")
                return EXIT_OK
            detail = (f" ({len(touched)} art PNG file(s) changed)" if touched
                      else " (use --allow-missing-manifest when no art has been delivered)")
            raise EnvironmentProblem(f"asset manifest not found at {manifest_rel}{detail}")
        manifest = load_json(manifest_path)
        version = manifest.get("manifestVersion", 1)
        if isinstance(version, bool) or version not in (1, 2):
            print(f"ERROR   [-] file={manifest_rel} field=manifestVersion :: "
                  f"unsupported manifestVersion {version!r}; supported versions are "
                  "1 (legacy, may be omitted) and 2")
            print(f"FAIL: 1 problem(s) in {manifest_rel}")
            return EXIT_VALIDATION
        schema_rel = (args.schema.replace("\\", "/") if args.schema
                      else schema_path_for(manifest))
        schema = load_json(root / schema_rel)
    except EnvironmentProblem as exc:
        print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    errors, warnings = validate_manifest(
        manifest, schema, root,
        check_files=not args.skip_file_checks, changed=changed, manifest_rel=manifest_rel)

    findings = errors + warnings
    if args.report:
        Path(args.report).write_text("".join(line + "\n" for line in findings), encoding="utf-8")
    if not args.quiet or errors:
        for line in findings:
            print(line)
    assets = manifest.get("assets") or []
    print(f"SUMMARY assetPackId={manifest.get('assetPackId', '?')} "
          f"version={manifest.get('assetPackVersion', '?')} assets={len(assets)} "
          f"errors={len(errors)} warnings={len(warnings)}")
    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {manifest_rel}")
        return EXIT_VALIDATION
    print(f"OK: {manifest_rel} passed asset handoff validation")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
