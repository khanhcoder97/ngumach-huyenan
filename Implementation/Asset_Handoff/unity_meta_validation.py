#!/usr/bin/env python3
"""OPC-07: static Unity ``.meta`` import validation (standard library only).

The parser is deliberately focused on the text format Unity writes for texture
imports. It understands the two rect/pivot shapes that occur in real Muse
exports:

    rect: {x: 0, y: 448, width: 48, height: 64}
    rect:
      serializedVersion: 2
      x: 0
      y: 448
      width: 48
      height: 64

Validation rules:

* ``guid`` is required, unique inside the file and exactly 32 hex digits.
* ``TextureImporter`` must carry ``spritePixelsToUnits``, ``filterMode``,
  ``enableMipMap`` and ``spriteMode``. Missing fields are errors, never a
  silent pass.
* PPU is parsed as a decimal; ``20.5`` is reported as ``20.5`` and rejected.
* Point filter (0), mip maps disabled (0) and uncompressed
  ``textureCompression: 0`` are required for the pixel-art import baseline.
* ``spriteMode: 2`` must contain at least one sprite. Each sprite needs a name,
  a complete rect and numeric pivots. Rect bounds are checked against the PNG
  dimensions when the caller supplies them.
* Duplicate sprite names and duplicate sprite IDs are errors.
* Unknown/missing structures produce an explicit finding; the parser never
  returns a clean report just because it understood nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

GUID_RE = re.compile(r"^[0-9a-fA-F]{32}$")


@dataclass
class SpriteRect:
    name: str
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    pivot_x: Optional[float] = None
    pivot_y: Optional[float] = None
    alignment: Optional[int] = None
    sprite_id: Optional[str] = None

    @property
    def complete(self) -> bool:
        return None not in (self.x, self.y, self.width, self.height)


@dataclass
class MetaReport:
    """Findings for one ``.meta`` file, already in the shared report shape."""

    asset_id: str
    path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ppu: Optional[float] = None
    filter_mode_ok: bool = False
    mipmaps_disabled: bool = False
    alignment: Optional[int] = None
    pivot_x: Optional[float] = None
    pivot_y: Optional[float] = None
    sprite_mode: Optional[int] = None
    sprites: List[SpriteRect] = field(default_factory=list)
    guid: Optional[str] = None

    def _line(self, level: str, field_name: str, message: str) -> str:
        return (
            f"{level:7s} [{self.asset_id or '-'}] file={self.path} "
            f"field={field_name} :: {message}"
        )

    def error(self, field_name: str, message: str) -> None:
        self.errors.append(self._line("ERROR", field_name, message))

    def warn(self, field_name: str, message: str) -> None:
        self.warnings.append(self._line("WARN", field_name, message))


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_blank(line: str) -> bool:
    return not line.strip()


def _find_top_level(lines: List[str], key: str) -> List[int]:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$")
    return [index for index, line in enumerate(lines) if pattern.match(line)]


def _block_end(lines: List[str], start: int, parent_indent: int) -> int:
    """Return the first line index at or before ``parent_indent`` after start."""
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if _is_blank(line):
            continue
        if _indent(line) <= parent_indent:
            return index
    return len(lines)


def _extract_block(lines: List[str], start: int) -> Tuple[int, int]:
    """Find a ``key:`` line and return ``(start, end)`` for its child block."""
    parent_indent = _indent(lines[start])
    return start, _block_end(lines, start, parent_indent)


def _find_key_in_block(
    lines: List[str], start: int, end: int, key: str, indent: Optional[int] = None
) -> List[Tuple[int, str]]:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$")
    found: List[Tuple[int, str]] = []
    for index in range(start + 1, end):
        line = lines[index]
        if _is_blank(line):
            continue
        match = pattern.match(line)
        if not match:
            continue
        if indent is not None and _indent(line) != indent:
            continue
        found.append((index, match.group(1)))
    return found


def _parse_inline_mapping(value: str) -> Optional[Dict[str, str]]:
    value = value.strip()
    if not (value.startswith("{") and value.endswith("}")):
        return None
    body = value[1:-1]
    result: Dict[str, str] = {}
    for part in body.split(","):
        if ":" not in part:
            return None
        key, scalar = part.split(":", 1)
        result[key.strip()] = scalar.strip()
    return result


def _parse_child_mapping(
    lines: List[str], line_index: int, key: str
) -> Optional[Dict[str, str]]:
    """Parse either an inline ``key: {..}`` or a nested mapping block."""
    line = lines[line_index]
    match = re.match(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", line)
    if not match:
        return None
    inline = match.group(1).strip()
    if inline:
        return _parse_inline_mapping(inline)
    parent_indent = _indent(line)
    result: Dict[str, str] = {}
    child_indent: Optional[int] = None
    for index in range(line_index + 1, len(lines)):
        child = lines[index]
        if _is_blank(child):
            continue
        current_indent = _indent(child)
        if current_indent <= parent_indent:
            break
        if child_indent is None:
            child_indent = current_indent
        if current_indent != child_indent:
            continue
        item = re.match(r"^\s*([A-Za-z_][\w]*):\s*(.*?)\s*$", child)
        if item:
            result[item.group(1)] = item.group(2)
    return result


def _int_value(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value.strip().strip('"').strip("'"))
    except (TypeError, ValueError):
        return None


def _float_value(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value.strip().strip('"').strip("'"))
    except (TypeError, ValueError):
        return None


def _parse_guid(text: str, report: MetaReport) -> Optional[str]:
    lines = text.splitlines()
    matches = _find_top_level(lines, "guid")
    if not matches:
        report.error("guid", "missing top-level guid; .meta is incomplete or unsupported")
        return None
    if len(matches) > 1:
        report.error("guid", "multiple top-level guid fields; cannot determine asset identity")
        return None
    value = re.match(r"^guid:\s*(.*?)\s*$", lines[matches[0]]).group(1)
    if not GUID_RE.match(value):
        report.error("guid", f"guid={value!r} is not 32 hexadecimal digits")
        return None
    return value.lower()


def _importer_block(
    lines: List[str], report: MetaReport
) -> Optional[Tuple[int, int]]:
    starts = _find_top_level(lines, "TextureImporter")
    if not starts:
        report.error(
            "TextureImporter",
            "missing TextureImporter block; only Unity texture metas are supported",
        )
        return None
    if len(starts) > 1:
        report.error("TextureImporter", "multiple TextureImporter blocks")
        return None
    start = starts[0]
    end = _block_end(lines, start, _indent(lines[start]))
    if end == start + 1:
        report.error(
            "TextureImporter",
            "TextureImporter block is empty; required import fields are missing",
        )
    return start, end


def _direct_field(
    lines: List[str], start: int, end: int, key: str, report: MetaReport
) -> Optional[str]:
    found = _find_key_in_block(lines, start, end, key, indent=2)
    if not found:
        report.error(key, f"required TextureImporter field {key} is missing")
        return None
    values = {value for _index, value in found}
    if len(found) > 1 and len(values) > 1:
        report.error(key, f"duplicate {key} fields with conflicting values {sorted(values)}")
    return found[0][1]


def _nested_values(
    lines: List[str], start: int, end: int, key: str, minimum_indent: int = 3
) -> List[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$")
    values = []
    for index in range(start + 1, end):
        line = lines[index]
        match = pattern.match(line)
        if match and _indent(line) >= minimum_indent:
            values.append(match.group(1))
    return values


def _parse_sprites(
    lines: List[str], importer_start: int, importer_end: int, report: MetaReport
) -> List[SpriteRect]:
    sheet_matches = _find_key_in_block(
        lines, importer_start, importer_end, "spriteSheet"
    )
    if not sheet_matches:
        report.error("spriteSheet", "spriteMode=2 but no spriteSheet block was found")
        return []
    sheet_index = sheet_matches[0][0]
    sheet_end = _block_end(lines, sheet_index, _indent(lines[sheet_index]))
    sprites_matches = _find_key_in_block(lines, sheet_index, sheet_end, "sprites")
    if not sprites_matches:
        report.error("spriteSheet.sprites", "spriteMode=2 but no sprites list was found")
        return []
    sprites_index = sprites_matches[0][0]
    sprites_indent = _indent(lines[sprites_index])
    item_starts = [
        index
        for index in range(sprites_index + 1, sheet_end)
        if re.match(r"^\s*-\s+", lines[index])
        and _indent(lines[index]) == sprites_indent
    ]
    if not item_starts:
        report.error("spriteSheet.sprites", "spriteMode=2 but the sprites list is empty")
        return []

    results: List[SpriteRect] = []
    for position, item_start in enumerate(item_starts):
        item_end = (
            item_starts[position + 1]
            if position + 1 < len(item_starts)
            else sheet_end
        )
        name_values = _find_key_in_block(lines, item_start, item_end, "name")
        if not name_values:
            report.error(
                "spriteSheet.sprites.name",
                f"sprite entry #{position + 1} has no name",
            )
            name = f"<sprite {position + 1}>"
        else:
            name = name_values[0][1].strip().strip('"').strip("'")
            if not name:
                report.error(
                    "spriteSheet.sprites.name",
                    f"sprite entry #{position + 1} has an empty name",
                )
                name = f"<sprite {position + 1}>"

        sprite = SpriteRect(name=name)

        rect_values = _find_key_in_block(lines, item_start, item_end, "rect")
        if not rect_values:
            report.error("spriteSheet.sprites.rect", f"sprite {name!r} has no rect")
        else:
            rect_index = rect_values[0][0]
            mapping = _parse_child_mapping(lines, rect_index, "rect")
            if not mapping:
                report.error(
                    "spriteSheet.sprites.rect",
                    f"sprite {name!r} rect is missing or unsupported "
                    "(expected inline {x,y,width,height} or a nested mapping)",
                )
            else:
                sprite.x = _int_value(mapping.get("x"))
                sprite.y = _int_value(mapping.get("y"))
                sprite.width = _int_value(mapping.get("width"))
                sprite.height = _int_value(mapping.get("height"))
                missing = [
                    key
                    for key in ("x", "y", "width", "height")
                    if _int_value(mapping.get(key)) is None
                ]
                if missing:
                    report.error(
                        "spriteSheet.sprites.rect",
                        f"sprite {name!r} rect has missing/non-integer fields {missing}",
                    )
                else:
                    if sprite.width <= 0 or sprite.height <= 0:
                        report.error(
                            "spriteSheet.sprites.rect",
                            f"sprite {name!r} rect has non-positive size "
                            f"{sprite.width}x{sprite.height}",
                        )
                    if sprite.x < 0 or sprite.y < 0:
                        report.error(
                            "spriteSheet.sprites.rect",
                            f"sprite {name!r} rect origin ({sprite.x},{sprite.y}) is negative",
                        )

        pivot_values = _find_key_in_block(lines, item_start, item_end, "pivot")
        if not pivot_values:
            report.warn(
                "spriteSheet.sprites.pivot",
                f"sprite {name!r} has no pivot; Unity default pivot is unverified",
            )
        else:
            mapping = _parse_child_mapping(lines, pivot_values[0][0], "pivot")
            if not mapping:
                report.error(
                    "spriteSheet.sprites.pivot",
                    f"sprite {name!r} pivot is missing or unsupported",
                )
            else:
                sprite.pivot_x = _float_value(mapping.get("x"))
                sprite.pivot_y = _float_value(mapping.get("y"))
                if sprite.pivot_x is None or sprite.pivot_y is None:
                    report.error(
                        "spriteSheet.sprites.pivot",
                        f"sprite {name!r} pivot must contain numeric x and y",
                    )

        alignment_values = _find_key_in_block(
            lines, item_start, item_end, "alignment"
        )
        if alignment_values:
            sprite.alignment = _int_value(alignment_values[0][1])
            if sprite.alignment is None:
                report.error(
                    "spriteSheet.sprites.alignment",
                    f"sprite {name!r} alignment is not an integer",
                )

        id_values = _find_key_in_block(lines, item_start, item_end, "spriteID")
        if id_values:
            sprite.sprite_id = id_values[0][1].strip().strip('"').strip("'")
            if not re.match(r"^[0-9a-fA-F]{32}$", sprite.sprite_id):
                report.error(
                    "spriteSheet.sprites.spriteID",
                    f"sprite {name!r} spriteID={sprite.sprite_id!r} is not 32 hex digits",
                )

        results.append(sprite)
    return results


def _check_sprite_bounds(
    sprites: List[SpriteRect], image_size: Optional[Tuple[int, int]], report: MetaReport
) -> None:
    if image_size is None:
        return
    image_width, image_height = image_size
    for sprite in sprites:
        if not sprite.complete:
            continue
        if sprite.x + sprite.width > image_width or sprite.y + sprite.height > image_height:
            report.error(
                "spriteSheet.sprites.rect",
                f"sprite {sprite.name!r} rect "
                f"(x={sprite.x}, y={sprite.y}, width={sprite.width}, height={sprite.height}) "
                f"exceeds the {image_width}x{image_height} image bounds",
            )


def validate_meta(
    path: Path,
    asset_id: str,
    expected_ppu: float = 20,
    image_size: Optional[Tuple[int, int]] = None,
) -> MetaReport:
    """Parse a Unity texture ``.meta`` and return structured findings."""
    report = MetaReport(asset_id=asset_id, path=str(path))
    if not path.exists():
        report.error("path", f".meta file is missing at {path}")
        return report
    if not path.is_file():
        report.error("path", f".meta path is not a regular file: {path}")
        return report
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        report.error("path", f".meta cannot be read ({exc})")
        return report

    if not text.strip():
        report.error("path", ".meta file is empty")
        return report

    lines = text.splitlines()
    report.guid = _parse_guid(text, report)
    importer = _importer_block(lines, report)
    if importer is None:
        return report
    start, end = importer

    ppu_raw = _direct_field(lines, start, end, "spritePixelsToUnits", report)
    sprite_mode_raw = _direct_field(lines, start, end, "spriteMode", report)
    filter_values = _nested_values(lines, start, end, "filterMode")
    mipmap_values = _nested_values(lines, start, end, "enableMipMap")

    if not filter_values:
        report.error(
            "textureSettings.filterMode",
            "required filterMode field is missing (Point=0 expected)",
        )
    elif len(set(filter_values)) > 1:
        report.error(
            "textureSettings.filterMode",
            f"conflicting filterMode values {sorted(set(filter_values))}",
        )
    else:
        filter_mode = _int_value(filter_values[0])
        if filter_mode is None:
            report.error(
                "textureSettings.filterMode",
                f"filterMode={filter_values[0]!r} is not an integer",
            )
        else:
            report.filter_mode_ok = filter_mode == 0
            if filter_mode != 0:
                report.error(
                    "textureSettings.filterMode",
                    f"filterMode={filter_mode} (expected 0/Point for pixel art)",
                )

    if not mipmap_values:
        report.error(
            "mipmaps.enableMipMap",
            "required enableMipMap field is missing (disabled=0 expected)",
        )
    elif len(set(mipmap_values)) > 1:
        report.error(
            "mipmaps.enableMipMap",
            f"conflicting enableMipMap values {sorted(set(mipmap_values))}",
        )
    else:
        mipmap = _int_value(mipmap_values[0])
        if mipmap is None:
            report.error(
                "mipmaps.enableMipMap",
                f"enableMipMap={mipmap_values[0]!r} is not an integer",
            )
        else:
            report.mipmaps_disabled = mipmap == 0
            if mipmap != 0:
                report.error(
                    "mipmaps.enableMipMap",
                    "mipmaps are enabled (must be disabled for pixel art)",
                )

    if ppu_raw is not None:
        try:
            ppu = float(ppu_raw)
        except ValueError:
            report.error(
                "spritePixelsToUnits",
                f"spritePixelsToUnits={ppu_raw!r} is not numeric",
            )
        else:
            report.ppu = ppu
            if abs(ppu - expected_ppu) > 1e-9:
                report.error(
                    "spritePixelsToUnits",
                    f"spritePixelsToUnits={ppu_raw} differs from expected {expected_ppu}",
                )

    if sprite_mode_raw is not None:
        sprite_mode = _int_value(sprite_mode_raw)
        if sprite_mode is None:
            report.error("spriteMode", f"spriteMode={sprite_mode_raw!r} is not an integer")
        else:
            report.sprite_mode = sprite_mode
            if sprite_mode not in (0, 1, 2):
                report.error(
                    "spriteMode",
                    f"unsupported spriteMode={sprite_mode} (expected 0, 1 or 2)",
                )

    compression_values = _nested_values(lines, start, end, "textureCompression", 4)
    if not compression_values:
        report.warn(
            "platformSettings.textureCompression",
            "textureCompression is missing; lossless import is unverified",
        )
    else:
        for raw in sorted(set(compression_values)):
            value = _int_value(raw)
            if value is None:
                report.error(
                    "platformSettings.textureCompression",
                    f"textureCompression={raw!r} is not an integer",
                )
            elif value != 0:
                report.error(
                    "platformSettings.textureCompression",
                    f"textureCompression={value} is not lossless "
                    "(expected 0/Uncompressed)",
                )
    crunched_values = _nested_values(lines, start, end, "crunchedCompression", 4)
    for raw in sorted(set(crunched_values)):
        value = _int_value(raw)
        if value not in (0, None):
            report.error(
                "platformSettings.crunchedCompression",
                f"crunchedCompression={raw} must be 0 for lossless pixel art",
            )

    pivot_values = _find_key_in_block(lines, start, end, "spritePivot", indent=2)
    if not pivot_values:
        report.warn(
            "spritePivot",
            "top-level spritePivot is missing; Unity default pivot is unverified",
        )
    else:
        mapping = _parse_child_mapping(lines, pivot_values[0][0], "spritePivot")
        if not mapping:
            report.error("spritePivot", "spritePivot is missing or unsupported")
        else:
            report.pivot_x = _float_value(mapping.get("x"))
            report.pivot_y = _float_value(mapping.get("y"))
            if report.pivot_x is None or report.pivot_y is None:
                report.error("spritePivot", "spritePivot must contain numeric x and y")
            else:
                if not 0 <= report.pivot_x <= 1:
                    report.error(
                        "spritePivot", f"pivot.x={report.pivot_x} outside [0..1]"
                    )
                if not 0 <= report.pivot_y <= 1:
                    report.error(
                        "spritePivot", f"pivot.y={report.pivot_y} outside [0..1]"
                    )

    if report.sprite_mode == 2:
        sprites = _parse_sprites(lines, start, end, report)
        report.sprites = sprites
        seen_names: Dict[str, int] = {}
        seen_ids: Dict[str, int] = {}
        seen_rects: Dict[Tuple[int, int, int, int], str] = {}
        for sprite in sprites:
            seen_names[sprite.name] = seen_names.get(sprite.name, 0) + 1
            if sprite.sprite_id:
                seen_ids[sprite.sprite_id] = seen_ids.get(sprite.sprite_id, 0) + 1
            if sprite.complete:
                rect_key = (sprite.x, sprite.y, sprite.width, sprite.height)
                if rect_key in seen_rects:
                    report.warn(
                        "spriteSheet.sprites.rect",
                        f"sprites {seen_rects[rect_key]!r} and {sprite.name!r} "
                        f"share the same rect {rect_key}",
                    )
                else:
                    seen_rects[rect_key] = sprite.name
            if sprite.pivot_x is not None and not 0 <= sprite.pivot_x <= 1:
                report.error(
                    "spriteSheet.sprites.pivot",
                    f"sprite {sprite.name!r} pivot.x={sprite.pivot_x} outside [0..1]",
                )
            if sprite.pivot_y is not None and not 0 <= sprite.pivot_y <= 1:
                report.error(
                    "spriteSheet.sprites.pivot",
                    f"sprite {sprite.name!r} pivot.y={sprite.pivot_y} outside [0..1]",
                )
        for name, count in seen_names.items():
            if count > 1:
                report.error(
                    "spriteSheet.sprites.name",
                    f"duplicate sprite name {name!r} appears {count} times",
                )
        for sprite_id, count in seen_ids.items():
            if count > 1:
                report.error(
                    "spriteSheet.sprites.spriteID",
                    f"duplicate spriteID {sprite_id} appears {count} times",
                )
        _check_sprite_bounds(sprites, image_size, report)

    return report


def extract_guid(text: str) -> Optional[str]:
    """Compatibility helper used by older callers."""
    matches = _find_top_level(text.splitlines(), "guid")
    if len(matches) != 1:
        return None
    match = re.match(r"^guid:\s*(.*?)\s*$", text.splitlines()[matches[0]])
    value = match.group(1) if match else ""
    return value.lower() if GUID_RE.match(value) else None
