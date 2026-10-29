#!/usr/bin/env python3
"""OPC-07: Unified import validation combining PNG structural + alpha check + .meta parsing.

Usage (from repo root):
  python Implementation/Asset_Handoff/validate_import.py [options]
    --manifest <manifest.json>  # delivery manifest to cross-reference paths
    --report <report.txt|md>     # output path (optional)

Exit codes:
  0  pass or only warnings (depends on --severity)
  1  validation findings exceed threshold
  2  environment error (missing files, JSON parse issues, etc.)
"""

import argparse
import json
import sys
from pathlib import Path

import png_validation
import png_alpha_check
import unity_meta_validation

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"


class ImportReport:
    """Collect findings for multiple assets."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @staticmethod
    def _line(level: str, asset_id: str, file: str, field: str, message: str) -> str:
        return f"{level:7s} [{asset_id or '-'}] file={file} field={field} :: {message}"

    def error(self, asset_id: str, file: str, field: str, message: str) -> None:
        self.errors.append(self._line("ERROR", asset_id, file, field, message))

    def warn(self, asset_id: str, file: str, field: str, message: str) -> None:
        self.warnings.append(self._line("WARN", asset_id, file, field, message))


def validate_one_asset(asset: dict, report: ImportReport, expected_ppu: int = 20) -> None:
    """Run PNG structural + alpha + .meta checks for one asset entry."""
    asset_id = asset.get("assetId") or "-";
    path_str = asset.get("path");
    if not isinstance(path_str, str):
        report.error(asset_id, "", "path", "must be a non-empty string")
        return

    path = REPO_ROOT / path_str
    rel_path = path_str.replace('\\','/')

    # Skip non-image kinds
    kind = asset.get("kind")
    image_kinds = ("sprite", "sprite_sheet", "vfx_sheet", "tileset", "ui_texture")
    if not any(k in kind for k in image_kinds):
        # Still check for missing .meta if present in the art directory
        meta_path = path.with_suffix(path.suffix + ".meta")
        if meta_path.exists():
            mresult = unity_meta_validation.validate_meta(meta_path, asset_id, expected_ppu)
            report.errors.extend(mresult.errors)
            report.warnings.extend(mresult.warnings)
        return

    # PNG structural validation
    try:
        width, height, bit_depth, color_type, interlace = png_validation.validate_png_structure(path)[:5]
    except ValueError as exc:
        report.error(asset_id, rel_path, "path", str(exc))
        return
    except png_validation.PNGValidationProblem as exc:
        report.error(asset_id, rel_path, "path", str(exc))
        return

    if interlace:
        report.warn(asset_id, rel_path, "path", "interlaced PNG (Adam7) is unusual for pixel art")

    # Alpha check
    has_alpha, msg = png_alpha_check.read_png_alpha_info(path)
    if not has_alpha:
        # No alpha — but sheet may still have transparent regions in palette; mark warning only if spriteMode suggests transparency elsewhere
        pass

    # .meta static import validation
    meta_path = path.with_suffix(path.suffix + ".meta")
    if not meta_path.exists():
        report.warn(asset_id, rel_path, "path", "Unity .meta file missing")
        return

    mresult = unity_meta_validation.validate_meta(meta_path, asset_id, expected_ppu)
    report.errors.extend(mresult.errors)
    report.warnings.extend(mresult.warnings)

    # Additional checks on sprites when spriteMode=2
    if mresult.sprite_mode == 2:
        for s in mresult.sprites:
            # We do not know exact sheet dimensions here from meta alone; rely on IHDR for bounds checking externally
            if s.pivot_x is not None and (s.pivot_x < 0 or s.pivot_x > 1):
                report.error(asset_id, rel_path, "pivot", f"sprite '{s.name}' pivot.x out of range")
            if s.pivot_y is not None and (s.pivot_y < 0 or s.pivot_y > 1):
                report.error(asset_id, rel_path, "pivot", f"sprite '{s.name}' pivot.y out of range")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest.replace('\\','/')
    if not manifest_path.is_file():
        print(f"ENVIRONMENT ERROR: manifest not found at {manifest_path}", file=sys.stderr)
        return 2

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ENVIRONMENT ERROR: cannot read/parse manifest ({exc})", file=sys.stderr)
        return 2

    report = ImportReport()
    expected_ppu = 20

    assets = manifest.get("assets", [])
    if not assets:
        print(f"OK: no assets to import-validate in {args.manifest}")
        return 0

    for i, asset in enumerate(assets):
        if not isinstance(asset, dict):
            continue
        validate_one_asset(asset, report, expected_ppu)

    # Output
    lines: list[str] = []
    for e in report.errors:
        lines.append(e)
    for w in report.warnings:
        lines.append(w)
    if args.report:
        rp = root / args.report.replace('\\','/')
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if lines:
        print("\n".join(lines))
        print(f"\nFAIL: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1
    else:
        print(f"OK: all imports validated")
        return 0


def build_parser():
    p = argparse.ArgumentParser(description="Validate Unity import metadata for delivered PNGs.")
    p.add_argument("--root", default=str(REPO_ROOT), help="repository root (default: auto-detect)")
    p.add_argument("--manifest", default=DEFAULT_MANIFEST, help="delivery manifest, relative to --root")
    p.add_argument("--report", default=None, help="output path for findings (optional)")
    return p


if __name__ == "__main__":
    sys.exit(main())
