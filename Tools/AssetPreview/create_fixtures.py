#!/usr/bin/env python3
"""OPC-08: generate a deterministic synthetic 6-column × 8-row actor sheet.

The fixture mirrors the delivered Muse geometry: six animation frames across
the X axis and eight direction rows down the Y axis. The PNG is a single valid
zlib stream (not one stream per scanline), and the Unity ``.meta`` uses the same
bottom-up rect convention as the Muse exporter: N is the top row, NW the bottom.
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
DIRECTION_COLOURS = {
    "N": (255, 100, 100),
    "NE": (255, 150, 100),
    "E": (255, 255, 100),
    "SE": (150, 255, 100),
    "S": (100, 255, 100),
    "SW": (100, 255, 150),
    "W": (100, 150, 255),
    "NW": (100, 100, 255),
}


def make_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, rows: list[bytes]) -> bytes:
    """Encode RGBA scanlines (without filter bytes) into a valid PNG."""
    raw = bytearray()
    for row in rows:
        if len(row) != width * 4:
            raise ValueError(f"row has {len(row)} bytes; expected {width * 4}")
        raw.append(0)  # filter type None
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", ihdr)
        + make_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + make_chunk(b"IEND", b"")
    )


def create_sprite_fixture(
    output_dir: Path,
    name: str,
    frame_w: int = 48,
    frame_h: int = 64,
    directions: int = 8,
    frames: int = 6,
    fps: int = 8,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    total_w, total_h = frames * frame_w, directions * frame_h
    if directions != len(DIRECTIONS):
        raise ValueError("fixture expects the canonical eight directions")

    rows: list[bytes] = []
    for y in range(total_h):
        direction_index = y // frame_h
        direction = DIRECTIONS[direction_index]
        colour = DIRECTION_COLOURS[direction]
        row = bytearray()
        for x in range(total_w):
            frame_index = x // frame_w
            local_x = x % frame_w
            local_y = y % frame_h
            # A small direction-coloured body plus one bright pixel whose X
            # offset identifies the frame, so the preview can be inspected.
            body = (
                frame_w // 4 <= local_x < 3 * frame_w // 4
                and frame_h // 4 <= local_y < 7 * frame_h // 8
            )
            marker_x = 4 + frame_index * 6
            marker = local_y == 4 and marker_x <= local_x < marker_x + 3
            if body or marker:
                row.extend((*colour, 255))
            else:
                row.extend((0, 0, 0, 0))
        rows.append(bytes(row))

    png_path = output_dir / f"{name}.png"
    png_path.write_bytes(encode_png(total_w, total_h, rows))

    guid = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
    lines = [
        "fileFormatVersion: 2",
        f"guid: {guid}",
        "TextureImporter:",
        "  internalIDToNameTable: []",
        "  serializedVersion: 13",
        "  mipmaps:",
        "    mipMapMode: 0",
        "    enableMipMap: 0",
        "  textureSettings:",
        "    serializedVersion: 2",
        "    filterMode: 0",
        "  spriteMode: 2",
        "  spritePivot: {x: 0.5, y: 0}",
        "  spritePixelsToUnits: 20",
        "  platformSettings:",
        "  - serializedVersion: 3",
        "    buildTarget: DefaultTexturePlatform",
        "    maxTextureSize: 2048",
        "    textureFormat: -1",
        "    textureCompression: 0",
        "    compressionQuality: 50",
        "    crunchedCompression: 0",
        "  spriteSheet:",
        "    serializedVersion: 2",
        "    sprites:",
    ]
    for direction_index, direction in enumerate(DIRECTIONS):
        # Unity rect Y is measured from the bottom of the texture.
        rect_y = (directions - 1 - direction_index) * frame_h
        for frame_index in range(frames):
            lines.extend(
                [
                    "    - serializedVersion: 2",
                    f"      name: {name}_{direction}_{frame_index}",
                    "      rect:",
                    "        serializedVersion: 2",
                    f"        x: {frame_index * frame_w}",
                    f"        y: {rect_y}",
                    f"        width: {frame_w}",
                    f"        height: {frame_h}",
                    "      alignment: 9",
                    "      pivot: {x: 0.5, y: 0}",
                    f"      spriteID: {direction_index:02x}{frame_index:02x}" + "0" * 28,
                ]
            )
    meta_path = output_dir / f"{name}.png.meta"
    meta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "manifestVersion": 1,
        "assetPackId": "preview_fixture",
        "assetPackVersion": "v0.1.0",
        "owner": "OpenCode",
        "sourceLicense": "original",
        "assets": [
            {
                "assetId": f"FIX_{name.upper()}",
                "path": f"Tools/AssetPreview/fixtures/{name}.png",
                "kind": "sprite_sheet",
                "status": "draft",
                "pixelWidth": total_w,
                "pixelHeight": total_h,
                "pixelsPerUnit": 20,
                "pivot": "bottom_center",
                "directions": list(DIRECTIONS),
                "animations": [
                    {
                        "name": "walk",
                        "framesPerDirection": frames,
                        "fps": fps,
                        "loop": True,
                    }
                ],
            }
        ],
    }
    manifest_path = output_dir / "preview_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"✓ {png_path} ({total_w}×{total_h}, {frames} columns × {directions} rows)")
    print(f"  → {meta_path} ({frames * directions} sprites)")
    print(f"  → {manifest_path} (assetId FIX_{name.upper()})")
    return {
        "assetId": f"FIX_{name.upper()}",
        "path": f"Tools/AssetPreview/fixtures/{name}.png",
        "pixelWidth": total_w,
        "pixelHeight": total_h,
        "frameWidth": frame_w,
        "frameHeight": frame_h,
        "columns": frames,
        "rows": directions,
        "totalSprites": frames * directions,
    }


def main() -> int:
    base = Path(__file__).resolve().parent / "fixtures"
    print("=" * 60)
    print("OPC-08: creating synthetic 6×8 actor fixture")
    print("=" * 60)
    create_sprite_fixture(base, "actor_8dir_test")
    print("=" * 60)
    print("Test with: python Tools/AssetPreview/server.py --root .")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
