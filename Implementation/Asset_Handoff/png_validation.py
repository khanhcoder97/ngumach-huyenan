#!/usr/bin/env python3
"""OPC-07: strict PNG structural validation (standard library only).

This module reads the complete PNG chunk stream, verifies every chunk CRC,
enforces the chunk ordering rules needed by Unity/import tooling, and inflates
the IDAT stream to confirm it is complete and exactly the expected size. It
does **not** use a third-party image library.

The checks intentionally fail closed:

* signature, IHDR, IDAT and IEND are required;
* every chunk CRC is checked over the chunk type **and** payload;
* chunk lengths are bounded and the file may not contain trailing bytes;
* IDAT chunks must be consecutive and form one complete zlib stream;
* the inflated scanline stream must match the dimensions declared by IHDR;
* every scanline filter byte must be a valid PNG filter (0..4);
* unknown critical chunks are rejected, unknown ancillary chunks are warned.

``validate_png`` returns a :class:`PNGInfo` object with the inflated (still
filtered) scanline bytes. ``png_alpha_check`` uses that buffer to prove actual
transparent-pixel evidence instead of only looking at the colour type.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"

# colour type -> (name, allowed bit depths, channels)
COLOUR_TYPES = {
    0: ("grayscale", (1, 2, 4, 8, 16), 1),
    2: ("RGB", (8, 16), 3),
    3: ("indexed", (1, 2, 4, 8), 1),
    4: ("grayscale+alpha", (8, 16), 2),
    6: ("RGBA", (8, 16), 4),
}

CRITICAL_CHUNKS = frozenset({b"IHDR", b"PLTE", b"IDAT", b"IEND"})
KNOWN_ANCILLARY = frozenset({
    b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"iCCP", b"sBIT", b"bKGD",
    b"hIST", b"pHYs", b"sPLT", b"tIME", b"tEXt", b"zTXt", b"iTXt",
    b"eXIf",
})

MAX_CHUNK_BYTES = 64 * 1024 * 1024
MAX_CHUNKS = 10000
MAX_DECOMPRESS_SIZE = 256 * 1024 * 1024

# Adam7 passes: (x_start, y_start, x_step, y_step)
ADAM7 = (
    (0, 0, 8, 8),
    (4, 0, 8, 8),
    (0, 4, 4, 8),
    (2, 0, 4, 4),
    (0, 2, 2, 4),
    (1, 0, 2, 2),
    (0, 1, 1, 2),
)


class PNGValidationProblem(Exception):
    """Raised when the PNG cannot be accepted for import."""


@dataclass
class PNGInfo:
    path: Path
    width: int
    height: int
    bit_depth: int
    colour_type: int
    interlace: int
    palette: Optional[bytes] = None
    trns: Optional[bytes] = None
    idat: bytes = b""
    raw: bytes = b""
    warnings: List[str] = field(default_factory=list)

    @property
    def colour_name(self) -> str:
        return COLOUR_TYPES[self.colour_type][0]

    @property
    def channels(self) -> int:
        return COLOUR_TYPES[self.colour_type][2]

    @property
    def has_alpha_channel(self) -> bool:
        return self.colour_type in (4, 6)


def _chunk_name(raw: bytes) -> str:
    return raw.decode("latin-1", "replace")


def _valid_chunk_type(raw: bytes) -> bool:
    if len(raw) != 4:
        return False
    return all(65 <= byte <= 90 or 97 <= byte <= 122 for byte in raw)


def _channels(colour_type: int) -> int:
    return COLOUR_TYPES[colour_type][2]


def _row_bytes(width: int, bit_depth: int, channels: int) -> int:
    return (width * channels * bit_depth + 7) // 8


def _bpp(bit_depth: int, channels: int) -> int:
    return max(1, (channels * bit_depth + 7) // 8)


def _pass_dimensions(width: int, height: int, x0: int, y0: int, dx: int, dy: int):
    if width <= x0 or height <= y0:
        return 0, 0
    return (width - x0 + dx - 1) // dx, (height - y0 + dy - 1) // dy


def iter_passes(info: PNGInfo):
    """Yield ``(pass_width, pass_height, row_bytes)`` descriptors."""
    channels = info.channels
    if not info.interlace:
        yield info.width, info.height, _row_bytes(info.width, info.bit_depth, channels)
        return
    for x0, y0, dx, dy in ADAM7:
        pw, ph = _pass_dimensions(info.width, info.height, x0, y0, dx, dy)
        if pw and ph:
            yield pw, ph, _row_bytes(pw, info.bit_depth, channels)


def _expected_raw_size(info: PNGInfo) -> int:
    total = 0
    for _pw, ph, row_bytes in iter_passes(info):
        total += ph * (row_bytes + 1)
    return total


def _parse_chunks(data: bytes):
    """Parse and CRC-check the chunk stream, returning (info fields, idat)."""
    warnings: List[str] = []
    offset = 8
    chunk_count = 0
    seen_ihdr = False
    seen_plte = False
    seen_trns = False
    seen_iend = False
    idat_parts: List[bytes] = []
    idat_state = 0  # 0=not seen, 1=inside run, 2=run ended
    palette: Optional[bytes] = None
    trns: Optional[bytes] = None
    width = height = bit_depth = colour_type = interlace = None

    while offset < len(data):
        if offset + 8 > len(data):
            raise PNGValidationProblem("PNG is truncated inside a chunk header")
        length = struct.unpack_from(">I", data, offset)[0]
        if length > MAX_CHUNK_BYTES:
            raise PNGValidationProblem(
                f"PNG chunk length {length} exceeds the {MAX_CHUNK_BYTES}-byte safety bound"
            )
        data_end = offset + 8 + length
        crc_end = data_end + 4
        if crc_end > len(data):
            raise PNGValidationProblem("PNG is truncated inside a chunk payload or CRC")
        chunk_type = data[offset + 4:offset + 8]
        if not _valid_chunk_type(chunk_type):
            raise PNGValidationProblem(f"invalid PNG chunk type bytes {chunk_type!r}")
        payload = data[offset + 8:data_end]
        stored_crc = struct.unpack_from(">I", data, data_end)[0]
        computed_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if computed_crc != stored_crc:
            raise PNGValidationProblem(
                f"CRC mismatch in {_chunk_name(chunk_type)} chunk "
                f"(stored {stored_crc:08x}, computed {computed_crc:08x})"
            )

        if not seen_ihdr:
            if chunk_type != b"IHDR":
                raise PNGValidationProblem(
                    f"first PNG chunk is {_chunk_name(chunk_type)}, expected IHDR"
                )
        elif chunk_type == b"IHDR":
            raise PNGValidationProblem("PNG contains more than one IHDR chunk")

        if idat_state == 1 and chunk_type != b"IDAT":
            idat_state = 2

        if chunk_type == b"IHDR":
            if length != 13:
                raise PNGValidationProblem(f"IHDR length {length} differs from 13 bytes")
            (width, height, bit_depth, colour_type,
             compression, filter_method, interlace) = struct.unpack(">IIBBBBB", payload)
            if width == 0 or height == 0:
                raise PNGValidationProblem(f"IHDR declares an empty image ({width}x{height})")
            if colour_type not in COLOUR_TYPES:
                raise PNGValidationProblem(f"unsupported PNG colour type {colour_type}")
            _name, allowed_depths, _channels_count = COLOUR_TYPES[colour_type]
            if bit_depth not in allowed_depths:
                raise PNGValidationProblem(
                    f"bit depth {bit_depth} is invalid for colour type {colour_type} "
                    f"({_name}); allowed {allowed_depths}"
                )
            if compression != 0:
                raise PNGValidationProblem(f"unsupported PNG compression method {compression}")
            if filter_method != 0:
                raise PNGValidationProblem(f"unsupported PNG filter method {filter_method}")
            if interlace not in (0, 1):
                raise PNGValidationProblem(f"unsupported PNG interlace method {interlace}")
            seen_ihdr = True
            if _expected_raw_size(PNGInfo(Path("."), width, height, bit_depth,
                                          colour_type, interlace)) > MAX_DECOMPRESS_SIZE:
                raise PNGValidationProblem(
                    "PNG inflated scanline size exceeds the 256 MB safety bound"
                )
        elif chunk_type == b"PLTE":
            if seen_plte:
                raise PNGValidationProblem("PNG contains more than one PLTE chunk")
            if idat_state:
                raise PNGValidationProblem("PLTE chunk appears after IDAT")
            if colour_type in (0, 4):
                raise PNGValidationProblem(f"PLTE is not allowed for colour type {colour_type}")
            if length == 0 or length % 3:
                raise PNGValidationProblem("PLTE length must be a non-zero multiple of 3")
            entries = length // 3
            if entries > 256:
                raise PNGValidationProblem(f"PLTE declares {entries} entries; maximum is 256")
            if colour_type == 3 and entries > (1 << bit_depth):
                raise PNGValidationProblem(
                    f"PLTE declares {entries} entries but bit depth {bit_depth} "
                    f"permits at most {1 << bit_depth}"
                )
            palette = payload
            seen_plte = True
        elif chunk_type == b"tRNS":
            if seen_trns:
                raise PNGValidationProblem("PNG contains more than one tRNS chunk")
            if idat_state:
                raise PNGValidationProblem("tRNS chunk appears after IDAT")
            if colour_type in (4, 6):
                raise PNGValidationProblem(f"tRNS is not allowed for colour type {colour_type}")
            if colour_type == 3:
                if not seen_plte:
                    raise PNGValidationProblem("indexed tRNS requires a preceding PLTE chunk")
                if len(payload) > len(palette) // 3:
                    raise PNGValidationProblem(
                        "tRNS has more alpha entries than the PLTE palette"
                    )
            elif colour_type == 0:
                if length != 2:
                    raise PNGValidationProblem("grayscale tRNS must be 2 bytes")
            elif colour_type == 2:
                if length != 6:
                    raise PNGValidationProblem("RGB tRNS must be 6 bytes")
            trns = payload
            seen_trns = True
        elif chunk_type == b"IDAT":
            if idat_state == 2:
                raise PNGValidationProblem("IDAT chunks are not consecutive")
            idat_state = 1
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            if length != 0:
                raise PNGValidationProblem(f"IEND length {length} differs from 0")
            seen_iend = True
            offset = crc_end
            if offset != len(data):
                raise PNGValidationProblem("PNG contains trailing bytes after IEND")
            break
        else:
            if idat_state == 1:
                idat_state = 2
            if chunk_type not in KNOWN_ANCILLARY:
                if not (chunk_type[0] & 0x20):
                    raise PNGValidationProblem(
                        f"unsupported critical PNG chunk {_chunk_name(chunk_type)}"
                    )
                warnings.append(
                    f"unknown ancillary PNG chunk {_chunk_name(chunk_type)} was not interpreted"
                )

        offset = crc_end
        chunk_count += 1
        if chunk_count > MAX_CHUNKS:
            raise PNGValidationProblem(
                f"PNG contains more than {MAX_CHUNKS} chunks; refusing to scan further"
            )

    if not seen_ihdr:
        raise PNGValidationProblem("PNG has no IHDR chunk")
    if not idat_parts:
        raise PNGValidationProblem("PNG has no IDAT chunk")
    if not seen_iend:
        raise PNGValidationProblem("PNG has no IEND chunk (file is truncated or incomplete)")
    if colour_type == 3 and palette is None:
        raise PNGValidationProblem("indexed PNG is missing the required PLTE chunk")

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "colour_type": colour_type,
        "interlace": interlace,
        "palette": palette,
        "trns": trns,
        "idat": b"".join(idat_parts),
        "warnings": warnings,
    }


def _inflate(info: PNGInfo) -> bytes:
    expected = _expected_raw_size(info)
    if expected > MAX_DECOMPRESS_SIZE:
        raise PNGValidationProblem(
            "PNG inflated scanline size exceeds the 256 MB safety bound"
        )
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(info.idat, expected + 1)
    except zlib.error as exc:
        raise PNGValidationProblem(f"IDAT is not a valid zlib stream ({exc})") from exc
    if len(raw) > expected:
        raise PNGValidationProblem(
            f"IDAT inflates to more than the expected {expected} scanline bytes"
        )
    if not decompressor.eof:
        raise PNGValidationProblem(
            "IDAT zlib stream is truncated or incomplete "
            "(compressed data ended before the stream terminator)"
        )
    if decompressor.unused_data:
        raise PNGValidationProblem("IDAT contains extra compressed bytes after the zlib stream")
    if len(raw) != expected:
        raise PNGValidationProblem(
            f"IDAT inflates to {len(raw)} bytes; expected {expected} for "
            f"{info.width}x{info.height} colour type {info.colour_type} "
            f"bit depth {info.bit_depth} interlace={info.interlace}"
        )
    return raw


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter_row(filter_type: int, row: bytearray, previous: bytes, bpp: int) -> None:
    if filter_type == 0:
        return
    if filter_type not in (1, 2, 3, 4):
        raise PNGValidationProblem(f"invalid PNG scanline filter type {filter_type}")
    for index in range(len(row)):
        left = row[index - bpp] if index >= bpp else 0
        above = previous[index]
        upper_left = previous[index - bpp] if index >= bpp else 0
        if filter_type == 1:
            row[index] = (row[index] + left) & 0xFF
        elif filter_type == 2:
            row[index] = (row[index] + above) & 0xFF
        elif filter_type == 3:
            row[index] = (row[index] + ((left + above) // 2)) & 0xFF
        else:
            row[index] = (row[index] + _paeth(left, above, upper_left)) & 0xFF


def validate_filters(info: PNGInfo) -> None:
    """Verify that every scanline starts with a valid filter byte."""
    offset = 0
    for _pw, ph, row_bytes in iter_passes(info):
        for _row_index in range(ph):
            if offset + 1 + row_bytes > len(info.raw):
                raise PNGValidationProblem("inflated IDAT ends inside a scanline")
            filter_type = info.raw[offset]
            if filter_type not in (0, 1, 2, 3, 4):
                raise PNGValidationProblem(
                    f"invalid PNG scanline filter type {filter_type} at offset {offset}"
                )
            offset += 1 + row_bytes
    if offset != len(info.raw):
        raise PNGValidationProblem(
            f"inflated IDAT has {len(info.raw) - offset} unexpected trailing bytes"
        )


def decode_rows(info: PNGInfo):
    """Yield ``(pass_width, pass_height, rows)`` with filters reversed.

    ``rows`` contains one ``bytes`` object per scanline with packed samples.
    Adam7 PNGs yield one tuple per non-empty pass.
    """
    channels = info.channels
    bpp = _bpp(info.bit_depth, channels)
    offset = 0
    for pass_width, pass_height, row_bytes in iter_passes(info):
        rows = []
        previous = bytes(row_bytes)
        for _row_index in range(pass_height):
            if offset + 1 + row_bytes > len(info.raw):
                raise PNGValidationProblem("inflated IDAT ends inside a scanline")
            filter_type = info.raw[offset]
            row = bytearray(info.raw[offset + 1:offset + 1 + row_bytes])
            offset += 1 + row_bytes
            _unfilter_row(filter_type, row, previous, bpp)
            rows.append(bytes(row))
            previous = rows[-1]
        yield pass_width, pass_height, rows
    if offset != len(info.raw):
        raise PNGValidationProblem("inflated IDAT has unexpected trailing bytes")


def validate_png(path: Path) -> PNGInfo:
    """Read and fully validate one PNG file.

    Raises :class:`PNGValidationProblem` for unreadable or structurally invalid
    files. The returned object has the inflated scanline buffer available for
    alpha/pixel inspection.
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PNGValidationProblem(
            f"file cannot be read ({exc.strerror or exc})"
        ) from exc

    if data.startswith(LFS_POINTER_PREFIX):
        raise PNGValidationProblem(
            "file is a Git LFS pointer; fetch the LFS object before validation"
        )
    if len(data) < 8 or not data.startswith(PNG_SIGNATURE):
        if data[0:2] == b"\xff\xd8":
            raise PNGValidationProblem(
                "file is a JPEG; deliver PNG for the pixel-art pipeline"
            )
        raise PNGValidationProblem("file does not start with the PNG signature")

    fields = _parse_chunks(data)
    info = PNGInfo(path=path, **fields)
    info.raw = _inflate(info)
    validate_filters(info)
    return info


def validate_png_structure(path: Path):
    """Backwards-compatible wrapper used by earlier OPC-07 callers.

    Returns ``(width, height, bit_depth, colour_type, interlace, warnings)``.
    """
    info = validate_png(path)
    return (
        info.width,
        info.height,
        info.bit_depth,
        info.colour_type,
        bool(info.interlace),
        list(info.warnings),
    )
