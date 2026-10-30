#!/usr/bin/env python3
"""OPC-07: unified Unity import validation for delivered PNG assets.

Combines strict PNG structure checks, real transparent-pixel evidence and Unity
``.meta`` static import checks. Every finding names the asset id, file and field.

Usage (from the repository root):
  python Implementation/Asset_Handoff/validate_import.py [options]
    --root <dir>                repository/asset root (default: repo root)
    --manifest <path>           delivery manifest, relative to --root
    --report <path>             write findings under --root (optional)
    --expected-ppu <number>     expected spritePixelsToUnits (default: 20)

Exit codes:
  0  no errors (warnings are allowed)
  1  one or more validation errors
  2  environment error (missing root/manifest, unreadable JSON)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import png_alpha_check
import png_validation
import unity_meta_validation

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
IMAGE_KINDS = frozenset({
    "sprite",
    "sprite_sheet",
    "vfx_sheet",
    "tileset",
    "tilemap",
    "ui_texture",
    "animation",
})


class ImportReport:
    """Collect structured findings for multiple assets."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @staticmethod
    def _line(level: str, asset_id: str, file: str, field_name: str, message: str) -> str:
        return (
            f"{level:7s} [{asset_id or '-'}] file={file} "
            f"field={field_name} :: {message}"
        )

    def error(self, asset_id: str, file: str, field_name: str, message: str) -> None:
        self.errors.append(self._line("ERROR", asset_id, file, field_name, message))

    def warn(self, asset_id: str, file: str, field_name: str, message: str) -> None:
        self.warnings.append(self._line("WARN", asset_id, file, field_name, message))


def _relative_posix(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_under_root(root: Path, value: object) -> Path:
    """Resolve a manifest path and reject absolute, escaping or unsafe values."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a non-empty string")
    candidate = Path(value.replace("\\", "/"))
    if candidate.is_absolute():
        raise ValueError("absolute paths are not allowed; use a path relative to --root")
    if candidate.drive or candidate.root:
        raise ValueError("drive/UNC paths are not allowed")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes --root after resolution") from exc
    return resolved


def _manifest_asset_list(manifest: object) -> List[dict]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be a JSON object")
    assets = manifest.get("assets")
    if assets is None:
        return []
    if not isinstance(assets, list):
        raise ValueError("manifest 'assets' must be an array")
    return [asset for asset in assets if isinstance(asset, dict)]


def validate_one_asset(
    asset: dict,
    report: ImportReport,
    root: Path,
    expected_ppu: float = 20,
) -> Optional[str]:
    """Validate one manifest asset and return its ``.meta`` GUID, if any."""
    asset_id = asset.get("assetId")
    if not isinstance(asset_id, str) or not asset_id.strip():
        asset_id = ""

    path_value = asset.get("path")
    try:
        path = resolve_under_root(root, path_value)
    except ValueError as exc:
        report.error(asset_id, str(path_value or ""), "path", str(exc))
        return None
    rel_path = _relative_posix(path, root)

    kind = asset.get("kind")
    if not isinstance(kind, str):
        report.error(asset_id, rel_path, "kind", "kind must be a string")
        return None
    if kind not in IMAGE_KINDS:
        meta_path = Path(str(path) + ".meta")
        if meta_path.exists():
            meta_result = unity_meta_validation.validate_meta(
                meta_path, asset_id, expected_ppu
            )
            report.errors.extend(meta_result.errors)
            report.warnings.extend(meta_result.warnings)
            return meta_result.guid
        return None

    if not path.is_file():
        report.error(asset_id, rel_path, "path", "file does not exist under --root")
        return None

    try:
        info = png_validation.validate_png(path)
    except (png_validation.PNGValidationProblem, OSError) as exc:
        report.error(asset_id, rel_path, "png", str(exc))
        return None

    for warning in info.warnings:
        report.warn(asset_id, rel_path, "png", warning)

    declared_width = asset.get("pixelWidth")
    declared_height = asset.get("pixelHeight")
    if isinstance(declared_width, int) and declared_width != info.width:
        report.error(
            asset_id,
            rel_path,
            "pixelWidth",
            f"manifest says {declared_width}px but IHDR says {info.width}px",
        )
    if isinstance(declared_height, int) and declared_height != info.height:
        report.error(
            asset_id,
            rel_path,
            "pixelHeight",
            f"manifest says {declared_height}px but IHDR says {info.height}px",
        )

    alpha = png_alpha_check.alpha_summary(info)
    if not alpha.has_alpha_channel and not alpha.has_transparency:
        report.warn(
            asset_id,
            rel_path,
            "alpha",
            "no alpha channel and no tRNS transparency; verify the sheet has no baked background",
        )
    elif alpha.has_alpha_channel and not alpha.has_transparency:
        report.warn(
            asset_id,
            rel_path,
            "alpha",
            "alpha channel exists but every decoded pixel is opaque; "
            "there is no transparent-pixel evidence",
        )

    meta_path = Path(str(path) + ".meta")
    if not meta_path.is_file():
        report.error(asset_id, rel_path, "path", "Unity .meta file is missing")
        return None

    meta_result = unity_meta_validation.validate_meta(
        meta_path,
        asset_id,
        expected_ppu,
        image_size=(info.width, info.height),
    )
    report.errors.extend(meta_result.errors)
    report.warnings.extend(meta_result.warnings)
    return meta_result.guid


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ENVIRONMENT ERROR: --root is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        manifest_path = resolve_under_root(root, args.manifest)
    except ValueError as exc:
        print(f"ENVIRONMENT ERROR: invalid --manifest: {exc}", file=sys.stderr)
        return 2
    if not manifest_path.is_file():
        print(
            f"ENVIRONMENT ERROR: manifest not found at {manifest_path}",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        assets = _manifest_asset_list(manifest)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"ENVIRONMENT ERROR: cannot read/parse manifest ({exc})", file=sys.stderr)
        return 2

    report = ImportReport()
    if not assets:
        print(f"OK: no assets to import-validate in {_relative_posix(manifest_path, root)}")
        return 0

    seen_guids: Dict[str, str] = {}
    for asset in assets:
        guid = validate_one_asset(asset, report, root, args.expected_ppu)
        if not guid:
            continue
        asset_id = asset.get("assetId") or "-"
        path_value = asset.get("path") or "-"
        if guid in seen_guids:
            report.error(
                asset_id,
                str(path_value),
                "guid",
                f"duplicate guid {guid} already used by {seen_guids[guid]}",
            )
        else:
            seen_guids[guid] = f"{asset_id} ({path_value})"

    lines = list(report.errors) + list(report.warnings)
    if args.report:
        try:
            report_path = resolve_under_root(root, args.report)
        except ValueError as exc:
            print(f"ENVIRONMENT ERROR: invalid --report: {exc}", file=sys.stderr)
            return 2
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    if lines:
        print("\n".join(lines))
    if report.errors:
        print(
            f"\nFAIL: {len(report.errors)} error(s), "
            f"{len(report.warnings)} warning(s)"
        )
        return 1
    if report.warnings:
        print(
            f"OK (warnings only): {len(report.warnings)} warning(s); "
            "no validation errors"
        )
    else:
        print("OK: all imports validated")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate PNG structure, transparency evidence and Unity import metadata."
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="asset/repository root all paths are confined to (default: repo root)",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="delivery manifest, relative to --root",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="optional findings output path, relative to --root",
    )
    parser.add_argument(
        "--expected-ppu",
        type=float,
        default=20.0,
        help="expected spritePixelsToUnits (default: 20)",
    )
    return parser


if __name__ == "__main__":
    sys.exit(main())
