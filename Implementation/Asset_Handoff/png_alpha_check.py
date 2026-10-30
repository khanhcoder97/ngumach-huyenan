#!/usr/bin/env python3
"""OPC-07: transparent-pixel evidence for delivered PNGs.

Earlier drafts only inspected the IHDR colour type. That is not evidence that a
sprite actually contains transparency: an RGBA image can be fully opaque. This
module inflates the PNG, reverses scanline filters and inspects real samples.

Supported colour types (terminology follows the PNG specification):

* 0 = grayscale, 2 = RGB, 3 = indexed palette, 4 = grayscale+alpha, 6 = RGBA.
* Indexed transparency is expressed by a tRNS palette-alpha chunk.
* RGB/grayscale transparency is expressed by a tRNS sample value.

The returned summary distinguishes an alpha *channel* from actual transparent
*pixels*, and reports the exact pixel count so reports cannot over-claim.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import png_validation


@dataclass
class AlphaSummary:
    colour_type: int
    bit_depth: int
    has_alpha_channel: bool
    has_transparency: bool
    transparent_pixels: int
    total_pixels: int
    min_alpha: Optional[int]
    message: str


def _max_value(bit_depth: int) -> int:
    return (1 << bit_depth) - 1


def _sample(row: bytes, x: int, channel: int, bit_depth: int, channels: int) -> int:
    if bit_depth == 8:
        return row[x * channels + channel]
    if bit_depth == 16:
        offset = (x * channels + channel) * 2
        return (row[offset] << 8) | row[offset + 1]
    # Sub-byte samples only occur for single-channel grayscale/indexed images.
    bits_per_pixel = channels * bit_depth
    bit_offset = x * bits_per_pixel + channel * bit_depth
    byte = row[bit_offset // 8]
    shift = 8 - bit_depth - (bit_offset % 8)
    return (byte >> shift) & _max_value(bit_depth)


def _trns_gray(trns: bytes) -> int:
    return struct.unpack(">H", trns)[0]


def _trns_rgb(trns: bytes) -> Tuple[int, int, int]:
    return struct.unpack(">HHH", trns)


def alpha_summary(info: png_validation.PNGInfo) -> AlphaSummary:
    """Inspect every decoded pixel and return transparency evidence."""
    bit_depth = info.bit_depth
    channels = info.channels
    colour_type = info.colour_type
    max_value = _max_value(bit_depth)
    alpha_limit = 255 if colour_type == 3 else max_value
    transparent = 0
    total = 0
    min_alpha: Optional[int] = None

    palette_trns = info.trns if colour_type == 3 else None
    gray_trns = _trns_gray(info.trns) if colour_type == 0 and info.trns else None
    rgb_trns = _trns_rgb(info.trns) if colour_type == 2 and info.trns else None

    for pass_width, pass_height, rows in png_validation.decode_rows(info):
        for row in rows:
            for x in range(pass_width):
                total += 1
                alpha = alpha_limit
                if colour_type == 6:
                    alpha = _sample(row, x, 3, bit_depth, channels)
                elif colour_type == 4:
                    alpha = _sample(row, x, 0, bit_depth, channels)
                elif colour_type == 3:
                    index = _sample(row, x, 0, bit_depth, channels)
                    if palette_trns is not None and index < len(palette_trns):
                        alpha = palette_trns[index]
                elif colour_type == 0 and gray_trns is not None:
                    if _sample(row, x, 0, bit_depth, channels) == gray_trns:
                        alpha = 0
                elif colour_type == 2 and rgb_trns is not None:
                    rgb = (
                        _sample(row, x, 0, bit_depth, channels),
                        _sample(row, x, 1, bit_depth, channels),
                        _sample(row, x, 2, bit_depth, channels),
                    )
                    if rgb == rgb_trns:
                        alpha = 0
                if min_alpha is None or alpha < min_alpha:
                    min_alpha = alpha
                if alpha < alpha_limit:
                    transparent += 1

    has_alpha_channel = info.has_alpha_channel
    if has_alpha_channel:
        message = (
            f"colourType={colour_type} ({info.colour_name}), bitDepth={bit_depth}: "
            f"alpha channel present; {transparent}/{total} pixels have alpha<{alpha_limit}"
        )
    elif info.trns is not None:
        message = (
            f"colourType={colour_type} ({info.colour_name}), bitDepth={bit_depth}: "
            f"tRNS transparency present; {transparent}/{total} pixels are transparent"
        )
    else:
        message = (
            f"colourType={colour_type} ({info.colour_name}), bitDepth={bit_depth}: "
            f"no alpha channel and no tRNS chunk; 0/{total} pixels transparent"
        )

    return AlphaSummary(
        colour_type=colour_type,
        bit_depth=bit_depth,
        has_alpha_channel=has_alpha_channel,
        has_transparency=transparent > 0,
        transparent_pixels=transparent,
        total_pixels=total,
        min_alpha=min_alpha,
        message=message,
    )


def read_png_alpha_summary(path: Path) -> AlphaSummary:
    """Validate and decode the PNG, then summarize real transparency."""
    try:
        info = png_validation.validate_png(path)
    except png_validation.PNGValidationProblem:
        raise
    except OSError as exc:
        raise ValueError(f"file cannot be read ({exc.strerror or exc})") from exc
    return alpha_summary(info)


def read_png_alpha_info(path: Path) -> Tuple[bool, str]:
    """Compatibility wrapper: ``(has_transparent_pixels, message)``.

    ``has_transparent_pixels`` is true only when decoded samples prove at least
    one non-opaque pixel. An alpha channel with no transparent pixel returns
    false and the message says so explicitly.
    """
    summary = read_png_alpha_summary(path)
    return summary.has_transparency, summary.message
