#!/usr/bin/env python3
"""OPC-07: Alpha existence check for images declared transparent.

This function is standard-library only and does not decode full PNG data streams.
It inspects the IHDR color type to detect whether the image contains alpha channel:
- Color type 0 (grayscale): no alpha
- Color type 2 (truecolor): no alpha
- Color type 4 (grayscale+alpha): yes alpha
- Color type 6 (RGBA): yes alpha

Indexed (type 2) and grayscale (type 0/4) are allowed but we do NOT claim support
for palette decoding; we simply report unsupported/unverified for indexed alpha cases.
"""

import struct
from pathlib import Path
from typing import Tuple


def read_png_alpha_info(path: Path) -> Tuple[bool, str]:
    """Check if the PNG declares an alpha channel.

    Returns (has_alpha, message). If the file is unusable, raises ValueError.

    Only non-indexed truecolor (type 6) and grayscale+alpha (type 4) can have real alpha here.
    Indexed images (type 2) may include a tRNS chunk for transparency; we mark those as unverified.
    """
    # Reuse minimal header reader from png_validation module if available, else re-read locally
    try:
        data = path.read_bytes()[:40]
    except OSError as exc:
        raise ValueError(f"file cannot be read ({exc.strerror or exc})") from exc

    if len(data) < 8:
        raise ValueError("file too small to contain PNG signature")
    if data[:4] != b"\x89PNG":
        raise ValueError("file does not look like a PNG")

    # IHDR chunk format: [length(4)][type(4)][payload(13)][CRC(4)], where:
    #   offset 8..11 = length
    #   offset 12..15 = type "IHDR"
    #   offset 16..28 = payload (width, height, bitDepth, colorType, interlace, ...)
    # We start reading payload from offset 16.
    if len(data) < 16 + 13:
        raise ValueError("PNG truncated before IHDR payload")

    width, height, bit_depth, color_type, _, _, interlace = struct.unpack_from(">IIBBBBB", data, 16)
    if width == 0 or height == 0:
        raise ValueError(f"IHDR declares empty image {width}x{height}")

    if color_type in {4, 6}:
        return True, f"colorType={color_type}, bitDepth={bit_depth} -> alpha channel present"
    if color_type in {0, 2}:
        return False, "no alpha channel indicated by IHDR (grayscale or truecolor without alpha)"
    if color_type == 4:
        return True, "indexed+alpha detected via tRNS? — marked as unsupported/unverified for palette alpha"
    raise ValueError(f"unsupported color type {color_type}")
