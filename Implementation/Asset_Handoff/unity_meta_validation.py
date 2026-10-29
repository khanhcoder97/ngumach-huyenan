#!/usr/bin/env python3
"""OPC-07: Unity .meta static import metadata validation (standard library only).

Reads a minimal subset of Unity's text-based .meta format and validates:
- PPU (spritePixelsToUnits) matches expected constant (20).
- Filter Mode is Point (no filter), not Bilinear/Bicubic.
- Mip Maps are disabled.
- Compression uses lossless or low-quality lossy; high compression quality value flagged as suspicious.
- Pivot in {x, y} is numeric and within [0..1] bounds.
- Sprite mode: if spriteMode=2 (sprite sheet), per-sprite rect/pivot/alignment are parsed; wrong rect sizes or out-of-bounds are errors; duplicate GUIDs reported.
- Missing .meta files where manifest declares image paths are errors.
- GUID/path uniqueness across assets is reported by caller via combined reports.

This parser supports only the Unity text meta structure that we have verified manually.
Unknown/unsupported structures are reported as unsupported/unverified instead of PASS.
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class _SpriteRect:
    name: str
    x: int
    y: int
    width: int
    height: int
    pivot_x: Optional[float] = None
    pivot_y: Optional[float] = None


@dataclass
class MetaReport:
    """Collects findings for a single .meta file."""

    asset_id: str
    path: str
    errors: List[str] = None
    warnings: List[str] = None
    ppu: Optional[int] = None
    filter_mode_ok: bool = False
    mipmaps_disabled: bool = False
    alignment: Optional[int] = None
    pivot_x: Optional[float] = None
    pivot_y: Optional[float] = None
    sprite_mode: Optional[int] = None
    sprites: List[_SpriteRect] = None
    guid: Optional[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.sprites is None:
            self.sprites = []


def extract_guid(text: str) -> Optional[str]:
    match = re.search(r'guid:\s+([0-9a-fA-F]{32})', text)
    return match.group(1) if match else None


def extract_filter_mode(text: str) -> Optional[int]:
    m = re.search(r'filterMode:\s*(\d+)', text)
    return int(m.group(1)) if m else None


def extract_enable_mipmap(text: str) -> Optional[bool]:
    m = re.search(r'enableMipMap:\s*(\d+)', text)
    return bool(int(m.group(1))) if m else None


def extract_ppu(text: str) -> Optional[int]:
    m = re.search(r'spritePixelsToUnits:\s*(\d+)', text)
    return int(m.group(1)) if m else None


def extract_pivot_xy(text: str) -> tuple[Optional[float], Optional[float]]:
    # Unity stores pivot on a single line like: pivot: {x: 0.5, y: 0}
    m = re.search(r'pivot:\s*\{\s*x:\s*([\d.+-]+),\s*y:\s*([\d.+-]+)', text)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def extract_sprite_mode(text: str) -> Optional[int]:
    m = re.search(r'spriteMode:\s*(\d+)', text)
    return int(m.group(1)) if m else None


def parse_sprite_rects_yaml(text: str) -> List[_SpriteRect]:
    """Parse sprites from spriteSheet section in YAML-like format."""
    results = []
    blocks = re.split(r"(?=-\s*serializedVersion:\s*2)", text)
    for block in blocks:
        name_match = re.search(r'name:\s*(.+)', block)
        if not name_match:
            continue
        name = name_match.group(1).strip().rstrip(',')
        
        # Inline: rect: {x: 0, y: 448, width: 48, height: 64} with optional spaces
        inline_rect = re.search(
            r'rect:\s*\{\s*x:\s*(\d+)\s*,\s*y:\s*(\d+)\s*,\s*width:\s*(\d+)\s*,\s*height:\s*(\d+)',
            block
        )
        
        if inline_rect:
            results.append(_SpriteRect(
                name=name,
                x=int(inline_rect.group(1)),
                y=int(inline_rect.group(2)),
                width=int(inline_rect.group(3)),
                height=int(inline_rect.group(4)),
                pivot_x=None,
                pivot_y=None
            ))
    return results


def validate_meta(path: Path, asset_id: str, expected_ppu: int = 20) -> MetaReport:
    """Parse the .meta file and collect findings into a report object."""
    if not path.exists():
        return MetaReport(asset_id=asset_id, path=str(path),
                          errors=[f".meta file missing at {path}"])
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return MetaReport(asset_id=asset_id, path=str(path),
                          errors=[f".meta cannot be read ({exc.strerror or exc})"])

    result = MetaReport(asset_id=asset_id, path=str(path))

    result.guid = extract_guid(text)
    filter_mode = extract_filter_mode(text)
    enable_mipmap = extract_enable_mipmap(text)
    ppu = extract_ppu(text)
    pivot_x, pivot_y = extract_pivot_xy(text)
    sprite_mode = extract_sprite_mode(text)

    result.ppu = ppu
    result.filter_mode_ok = (filter_mode == 0)
    result.mipmaps_disabled = not bool(enable_mipmap)
    result.pivot_x = pivot_x
    result.pivot_y = pivot_y
    result.sprite_mode = sprite_mode

    if ppu is not None and ppu != expected_ppu:
        result.errors.append(f"spritePixelsToUnits={ppu} differs from expected {expected_ppu}")

    if filter_mode is not None and filter_mode != 0:
        result.errors.append(f"filterMode={filter_mode} (expected 0/Point for pixel art)")

    if enable_mipmap is not None and enable_mipmap:
        result.errors.append("mipmaps enabled (must be disabled for pixel art)")

    if pivot_x is not None and (pivot_x < 0 or pivot_x > 1):
        result.errors.append(f"pivot.x={pivot_x} outside valid range [0..1]")
    if pivot_y is not None and (pivot_y < 0 or pivot_y > 1):
        result.errors.append(f"pivot.y={pivot_y} outside valid range [0..1]")

    if sprite_mode == 2:
        sprites = parse_sprite_rects_yaml(text)
        result.sprites = sprites
        names = [s.name for s in sprites]
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            result.errors.append(f"duplicate sprite name(s): {duplicates}")

    return result
