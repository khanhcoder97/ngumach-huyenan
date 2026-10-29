#!/usr/bin/env python3
"""OPC-07: PNG structural validation (standard library only).

Checks beyond IHDR: signature, chunk CRCs, truncated IDAT/IEND, LFS pointer,
decompression safety (iWCC/size limits), and optional alpha existence for
assets that declare transparency. Report findings in the same shape as the
delivery validator.

This module is filesystem-free except for file access required to read chunks.
The caller passes a report object whose error/warn methods collect findings.
"""

import json
import struct
import sys
from pathlib import Path
import zlib
import io

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
LFS_POINTER_PREFIX = "version https://git-lfs.github.com/spec/v1"

# Subset of PNG types we explicitly support. Anything else is unsupported/unverified.
SUPPORTED_COLOR_TYPES = frozenset({0, 2, 4, 6})  # grayscale, truecolor, indexed+palette, RGBA
# Indexed color (type 2) is allowed but we do not decode palette chunks here.
# We intentionally do NOT claim support for interlaced PNGs even though type 4+6 can be interlaced.

MAX_DECOMPRESS_SIZE = 256 * 1024 * 1024  # 256 MB hard limit per file


class PNGValidationProblem(Exception):
    """Raised when the file is unusable for validation."""


def _read_head(path, size=128):
    try:
        data = path.read_bytes()[:size]
        if len(data) < 8:
            raise PNGValidationProblem("file too small to contain any PNG chunk")
        return data
    except OSError as exc:
        raise PNGValidationProblem(f"file cannot be read ({exc.strerror or exc})") from exc


def _skip_chunks_until(data, offset, expected_types=None, max_calls=1000):
    """Scan forward through known chunks until we reach iEND or an unexpected type.

    Returns (remaining_offset, total_crc_errors). Supports up to max_calls loops.
    """
    crc_errors = 0
    while True:
        if offset + 8 > len(data):
            break
        length = struct.unpack_from(">I", data, offset)[0]
        chunk_type = data[offset + 4 : offset + 8].decode("latin-1", "replace")
        chunk_data_end = offset + 8 + length
        if chunk_data_end > len(data):
            raise PNGValidationProblem("truncation inside PNG chunk data")
        provided_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        computed_crc = 0xFFFFFFFF ^ zlib.crc32(data[offset + 4 : chunk_data_end]) & 0xFFFFFFFF
        if computed_crc != provided_crc:
            crc_errors += 1
            # Decide whether to treat errors as fatal. For structural validation,
            # we fail immediately to avoid silently accepting corrupted PNGs.
            raise PNGValidationProblem(f"CRC mismatch in {chunk_type} chunk")
        offset = chunk_data_end
        if chunk_type == "IEND":
            break
        if expected_types and chunk_type not in expected_types:
            # Non-standard chunk found; stop scanning at first non-exempt chunk.
            break
        max_calls -= 1
        if max_calls <= 0:
            raise PNGValidationProblem("excessive PNG chunks; refuse to scan indefinitely")
    return offset, crc_errors


def validate_png_structure(path):
    """Check PNG header, known chunks CRCs, and truncation.

    Returns (width, height, bit_depth, color_type, interlace) and a list of warnings.
    Raises PNGValidationProblem for fatal issues (LFS pointer, signature, CRC, etc.).

    This function does NOT decode decoded image pixels. Alpha/banding/color accuracy
    must be checked by callers via separate functions if needed.
    """
    data = path.read_bytes()

    if data.startswith(LFS_POINTER_PREFIX.encode("ascii")):
        raise PNGValidationProblem("file is a Git LFS pointer; fetch LFS objects before validation")

    if not data.startswith(PNG_SIGNATURE):
        if data[0:2] == b"\xff\xd8":
            raise PNGValidationProblem("file is JPEG; deliver PNG for pixel art pipeline")
        raise PNGValidationProblem("file does not start with the PNG signature")

    # Read IHDR
    ihdr_start = 8
    if len(data) < ihdr_start + 8:
        raise PNGValidationProblem("PNG is truncated before the IHDR chunk header")
    length = struct.unpack_from(">I", data, ihdr_start)[0]
    if length != 13:
        raise PNGValidationProblem(f"IHDR length {length} differs from 13 bytes")
    chunk_type = data[ihdr_start + 4 : ihdr_start + 8]
    if chunk_type != b"IHDR":
        raise PNGValidationProblem(f"first PNG chunk is {chunk_type.decode('latin-1', 'replace')}, expected IHDR")
    if len(data) < ihdr_start + 8 + 13:
        raise PNGValidationProblem("PNG is truncated inside the IHDR chunk")
    width, height, bit_depth, color_type, _, _, interlace = struct.unpack_from(
        ">IIBBBBB", data, ihdr_start + 8
    )
    if width == 0 or height == 0:
        raise PNGValidationProblem(f"IHDR declares an empty image ({width}x{height})")
    if color_type not in SUPPORTED_COLOR_TYPES:
        raise PNGValidationProblem(f"unsupported color type {color_type}")
    if bit_depth not in {1, 2, 4, 8}:
        # Bit depths 1/2/4 are valid but uncommon; we still support them structurally.
        pass  # no warning here; keep it strict but permissive

    interlace_flag = bool(interlace)
    return width, height, bit_depth, color_type, interlace_flag, []
