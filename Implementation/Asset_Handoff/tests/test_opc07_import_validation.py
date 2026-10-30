#!/usr/bin/env python3
"""Regression tests for OPC-07 PNG, alpha and Unity .meta validation.

Run from repo root:
    python -m unittest discover -s Implementation/Asset_Handoff/tests -v
"""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF_DIR = HERE.parent
REPO_ROOT = HANDOFF_DIR.parents[1]
if str(HANDOFF_DIR) not in sys.path:
    sys.path.insert(0, str(HANDOFF_DIR))

import png_alpha_check as palpha  # noqa: E402
import png_validation as pv  # noqa: E402
import unity_meta_validation as umv  # noqa: E402

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _pixel_bytes(
    width: int,
    colour_type: int,
    pixel_value: int,
    alpha_at=None,
    alpha_all=None,
    row_index: int = 0,
) -> bytes:
    out = bytearray()
    for x in range(width):
        if colour_type == 6:
            alpha = 255
            if alpha_all is not None:
                alpha = alpha_all
            if alpha_at == (row_index, x):
                alpha = 0
            out.extend((pixel_value, pixel_value, pixel_value, alpha))
        elif colour_type == 4:
            alpha = 255
            if alpha_all is not None:
                alpha = alpha_all
            if alpha_at == (row_index, x):
                alpha = 0
            out.extend((pixel_value, alpha))
        elif colour_type == 2:
            out.extend((pixel_value, pixel_value, pixel_value))
        else:
            out.append(pixel_value)
    return bytes(out)


def make_png(
    width=8,
    height=8,
    colour_type=6,
    bit_depth=8,
    pixel_value=1,
    alpha_at=None,
    alpha_all=None,
    trns=None,
    palette=None,
    filter_types=None,
    idat_transform=None,
    corrupt_idat_crc=False,
    corrupt_ihdr_crc=False,
    omit_idat=False,
    omit_iend=False,
    extra_chunks=None,
    trailing=b"",
) -> bytes:
    """Build a minimal but structurally complete PNG for tests."""
    channels = CHANNELS[colour_type]
    row_bytes = (width * channels * bit_depth + 7) // 8
    filter_types = filter_types or [0] * height
    raw = bytearray()
    for y in range(height):
        filter_type = filter_types[y % len(filter_types)]
        raw.append(filter_type)
        if bit_depth == 8:
            raw.extend(_pixel_bytes(width, colour_type, pixel_value, alpha_at, alpha_all, y))
        else:
            # Tests currently exercise 8-bit samples; keep a deterministic stub.
            raw.extend(bytes(row_bytes))
    ihdr = struct.pack(
        ">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, 0
    )
    ihdr_chunk = chunk(b"IHDR", ihdr)
    if corrupt_ihdr_crc:
        ihdr_chunk = ihdr_chunk[:-1] + bytes((ihdr_chunk[-1] ^ 1,))

    pieces = [b"\x89PNG\r\n\x1a\n", ihdr_chunk]
    if palette is not None:
        pieces.append(chunk(b"PLTE", palette))
    if trns is not None:
        pieces.append(chunk(b"tRNS", trns))
    for extra in extra_chunks or []:
        pieces.append(extra)
    if not omit_idat:
        compressed = zlib.compress(bytes(raw))
        if idat_transform is not None:
            compressed = idat_transform(compressed)
        idat_chunk = chunk(b"IDAT", compressed)
        if corrupt_idat_crc:
            idat_chunk = idat_chunk[:-1] + bytes((idat_chunk[-1] ^ 1,))
        pieces.append(idat_chunk)
    if not omit_iend:
        pieces.append(chunk(b"IEND", b""))
    return b"".join(pieces) + trailing


def make_sprite(
    name,
    x=0,
    y=0,
    width=4,
    height=4,
    pivot_x="0.5",
    pivot_y="0",
    sprite_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    inline_rect=False,
) -> str:
    if inline_rect:
        rect_lines = [
            f"      rect: {{x: {x}, y: {y}, width: {width}, height: {height}}}"
        ]
    else:
        rect_lines = [
            "      rect:",
            "        serializedVersion: 2",
            f"        x: {x}",
            f"        y: {y}",
            f"        width: {width}",
            f"        height: {height}",
        ]
    return "\n".join(
        [
            "    - serializedVersion: 2",
            f"      name: {name}",
            *rect_lines,
            "      alignment: 9",
            f"      pivot: {{x: {pivot_x}, y: {pivot_y}}}",
            f"      spriteID: {sprite_id}",
        ]
    )


def make_meta(
    guid="0123456789abcdef0123456789abcdef",
    ppu="20",
    filter_mode=0,
    mipmap=0,
    sprite_mode=0,
    sprites=None,
    compression=0,
    crunched=0,
    include_pivot=True,
    importer_body=None,
) -> str:
    if importer_body is not None:
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "TextureImporter:\n"
            f"{importer_body}"
        )
    lines = [
        "fileFormatVersion: 2",
        f"guid: {guid}",
        "TextureImporter:",
        "  internalIDToNameTable: []",
        "  serializedVersion: 13",
        "  mipmaps:",
        "    mipMapMode: 0",
        f"    enableMipMap: {mipmap}",
        "  textureSettings:",
        "    serializedVersion: 2",
        f"    filterMode: {filter_mode}",
        "  compressionQuality: 50",
        f"  spriteMode: {sprite_mode}",
    ]
    if include_pivot:
        lines.append("  spritePivot: {x: 0.5, y: 0}")
    lines.extend(
        [
            f"  spritePixelsToUnits: {ppu}",
            "  platformSettings:",
            "  - serializedVersion: 3",
            "    buildTarget: DefaultTexturePlatform",
            "    maxTextureSize: 2048",
            "    textureFormat: -1",
            f"    textureCompression: {compression}",
            "    compressionQuality: 50",
            f"    crunchedCompression: {crunched}",
        ]
    )
    if sprite_mode == 2:
        lines.extend(["  spriteSheet:", "    serializedVersion: 2", "    sprites:"])
        lines.extend(sprites or [])
    return "\n".join(lines) + "\n"


def write_asset_fixture(
    root: Path,
    png_bytes: bytes,
    meta_text: str,
    path="art/test.png",
    asset_id="TEST_SPRITE",
    meta_path=None,
) -> None:
    image_path = root / path
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(png_bytes)
    Path(meta_path or (str(image_path) + ".meta")).write_text(meta_text, encoding="utf-8")


def write_manifest(root: Path, assets) -> None:
    import json

    (root / "manifest.json").write_text(
        json.dumps({"assets": assets}, indent=2) + "\n", encoding="utf-8"
    )


def asset_entry(path="art/test.png", asset_id="TEST_SPRITE", width=8, height=8):
    return {
        "assetId": asset_id,
        "path": path,
        "kind": "sprite_sheet",
        "pixelWidth": width,
        "pixelHeight": height,
        "pixelsPerUnit": 20,
        "status": "draft",
    }


class PNGStructureTests(unittest.TestCase):
    def test_valid_rgba_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.png"
            path.write_bytes(make_png(16, 16))
            info = pv.validate_png(path)
            self.assertEqual((16, 16), (info.width, info.height))
            self.assertEqual(8, info.bit_depth)
            self.assertEqual(6, info.colour_type)
            self.assertFalse(info.interlace)
            self.assertEqual([], info.warnings)

    def test_valid_filter_types_0_to_4(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "filters.png"
            path.write_bytes(make_png(8, 8, filter_types=[0, 1, 2, 3, 4, 1, 2, 3]))
            info = pv.validate_png(path)
            self.assertEqual(8, info.width)

    def test_corrupted_idat_crc_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_crc.png"
            path.write_bytes(make_png(8, 8, corrupt_idat_crc=True))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "CRC mismatch in IDAT"):
                pv.validate_png(path)

    def test_corrupted_ihdr_crc_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_ihdr_crc.png"
            path.write_bytes(make_png(8, 8, corrupt_ihdr_crc=True))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "CRC mismatch in IHDR"):
                pv.validate_png(path)

    def test_signature_and_ihdr_only_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "header_only.png"
            ihdr = struct.pack(">IIBBBBB", 8, 8, 8, 6, 0, 0, 0)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "no IDAT|no IEND"):
                pv.validate_png(path)

    def test_missing_idat_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no_idat.png"
            path.write_bytes(make_png(8, 8, omit_idat=True))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "no IDAT"):
                pv.validate_png(path)

    def test_missing_iend_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no_iend.png"
            path.write_bytes(make_png(8, 8, omit_iend=True))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "no IEND"):
                pv.validate_png(path)

    def test_truncated_file_inside_idat_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = make_png(8, 8)
            idat = data.index(b"IDAT")
            path = Path(tmp) / "truncated.png"
            path.write_bytes(data[: idat + 8 + 3])
            with self.assertRaisesRegex(pv.PNGValidationProblem, "truncated"):
                pv.validate_png(path)

    def test_truncated_zlib_stream_with_valid_crc_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "truncated_stream.png"
            path.write_bytes(make_png(8, 8, idat_transform=lambda data: data[:-2]))
            with self.assertRaisesRegex(
                pv.PNGValidationProblem, "truncated or incomplete|not a valid zlib"
            ):
                pv.validate_png(path)

    def test_decompressed_size_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "short_stream.png"
            path.write_bytes(make_png(8, 8, idat_transform=lambda data: zlib.compress(b"\x00" * 5)))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "expected .* scanline bytes|IDAT inflates"):
                pv.validate_png(path)

    def test_unknown_critical_chunk_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unknown_critical.png"
            path.write_bytes(make_png(8, 8, extra_chunks=[chunk(b"ABCD", b"")]))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "unsupported critical"):
                pv.validate_png(path)

    def test_trailing_bytes_after_iend_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trailing.png"
            path.write_bytes(make_png(8, 8, trailing=b"junk"))
            with self.assertRaisesRegex(pv.PNGValidationProblem, "trailing bytes"):
                pv.validate_png(path)

    def test_lfs_pointer_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lfs.png"
            path.write_text(
                "version https://git-lfs.github.com/spec/v1\noid sha256:...\nsize 123\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(pv.PNGValidationProblem, "LFS"):
                pv.validate_png(path)


class AlphaCheckTests(unittest.TestCase):
    def test_opaque_rgba_has_no_transparent_pixel_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "opaque.png"
            path.write_bytes(make_png(8, 8, alpha_all=255))
            summary = palpha.read_png_alpha_summary(path)
            self.assertTrue(summary.has_alpha_channel)
            self.assertFalse(summary.has_transparency)
            self.assertEqual(0, summary.transparent_pixels)
            self.assertIn("0/64", summary.message)

    def test_rgba_with_one_transparent_pixel(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alpha.png"
            path.write_bytes(make_png(8, 8, alpha_at=(0, 0)))
            summary = palpha.read_png_alpha_summary(path)
            self.assertTrue(summary.has_transparency)
            self.assertEqual(1, summary.transparent_pixels)
            self.assertEqual(0, summary.min_alpha)
            self.assertIn("1/64", summary.message)

    def test_rgb_trns_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rgb_trns.png"
            path.write_bytes(
                make_png(
                    8,
                    8,
                    colour_type=2,
                    pixel_value=7,
                    trns=struct.pack(">HHH", 7, 7, 7),
                )
            )
            summary = palpha.read_png_alpha_summary(path)
            self.assertFalse(summary.has_alpha_channel)
            self.assertTrue(summary.has_transparency)
            self.assertEqual(64, summary.transparent_pixels)

    def test_indexed_trns_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "indexed_trns.png"
            path.write_bytes(
                make_png(
                    8,
                    8,
                    colour_type=3,
                    pixel_value=0,
                    palette=b"\x00\x00\x00\xff\xff\xff",
                    trns=b"\x00",
                )
            )
            summary = palpha.read_png_alpha_summary(path)
            self.assertFalse(summary.has_alpha_channel)
            self.assertTrue(summary.has_transparency)
            self.assertEqual(64, summary.transparent_pixels)

    def test_rgb_without_trns_has_no_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rgb.png"
            path.write_bytes(make_png(8, 8, colour_type=2, pixel_value=7))
            has_alpha, message = palpha.read_png_alpha_info(path)
            self.assertFalse(has_alpha)
            self.assertIn("no alpha channel and no tRNS", message)

    def test_grayscale_without_trns_has_no_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gray.png"
            path.write_bytes(make_png(8, 8, colour_type=0, pixel_value=1))
            has_alpha, _message = palpha.read_png_alpha_info(path)
            self.assertFalse(has_alpha)


class MetaValidatorTests(unittest.TestCase):
    def test_valid_multiline_sprite_rects_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sheet.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[
                        make_sprite("frame_0", 0, 0, 4, 4),
                        make_sprite("frame_1", 4, 0, 4, 4,
                                    sprite_id="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
                    ],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "TEST", 20, image_size=(8, 8))
            self.assertEqual([], result.errors, result.errors)
            self.assertEqual(2, len(result.sprites))
            self.assertEqual("frame_0", result.sprites[0].name)
            self.assertEqual((0, 0, 4, 4), (
                result.sprites[0].x,
                result.sprites[0].y,
                result.sprites[0].width,
                result.sprites[0].height,
            ))
            self.assertEqual(20.0, result.ppu)
            self.assertTrue(result.mipmaps_disabled)
            self.assertTrue(result.filter_mode_ok)

    def test_inline_rects_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sheet.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[make_sprite("inline", inline_rect=True)],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "TEST", 20)
            self.assertEqual([], result.errors, result.errors)
            self.assertEqual(1, len(result.sprites))
            self.assertEqual(4, result.sprites[0].width)

    def test_empty_meta_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.png.meta"
            path.write_text("", encoding="utf-8")
            result = umv.validate_meta(path, "EMPTY", 20)
            self.assertTrue(result.errors)
            self.assertIn("empty", result.errors[0].lower())

    def test_empty_texture_importer_reports_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty_importer.png.meta"
            path.write_text(
                "fileFormatVersion: 2\n"
                "guid: 0123456789abcdef0123456789abcdef\n"
                "TextureImporter:\n",
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "EMPTY_IMPORTER", 20)
            combined = "\n".join(result.errors)
            self.assertIn("TextureImporter block is empty", combined)
            self.assertIn("spritePixelsToUnits", combined)
            self.assertIn("filterMode", combined)
            self.assertIn("spriteMode", combined)

    def test_fractional_ppu_is_not_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fractional.png.meta"
            path.write_text(make_meta(ppu="20.5"), encoding="utf-8")
            result = umv.validate_meta(path, "FRACTIONAL", 20)
            combined = "\n".join(result.errors)
            self.assertIn("20.5", combined)
            self.assertNotIn("spritePixelsToUnits=20 ", combined)
            self.assertEqual(20.5, result.ppu)

    def test_sprite_rect_outside_image_bounds_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bounds.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[make_sprite("outside", 6, 0, 4, 4)],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "BOUNDS", 20, image_size=(8, 8))
            combined = "\n".join(result.errors)
            self.assertIn("exceeds the 8x8 image bounds", combined)
            self.assertIn("outside", combined)

    def test_duplicate_sprite_names_are_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicates.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[
                        make_sprite("same_name", 0, 0, 4, 4),
                        make_sprite(
                            "same_name", 4, 0, 4, 4,
                            sprite_id="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                        ),
                    ],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "DUP", 20)
            self.assertTrue(any("duplicate sprite name" in e for e in result.errors))

    def test_duplicate_sprite_ids_are_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate_ids.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[
                        make_sprite("a", 0, 0, 4, 4),
                        make_sprite("b", 4, 0, 4, 4),
                    ],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "DUP_ID", 20)
            self.assertTrue(any("duplicate spriteID" in e for e in result.errors))

    def test_sprite_mode_two_without_sprites_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no_sprites.png.meta"
            path.write_text(make_meta(sprite_mode=2, sprites=[]), encoding="utf-8")
            result = umv.validate_meta(path, "NO_SPRITES", 20)
            self.assertTrue(any("sprites list is empty" in e for e in result.errors))

    def test_sprite_pivot_outside_range_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pivot.png.meta"
            path.write_text(
                make_meta(
                    sprite_mode=2,
                    sprites=[make_sprite("bad_pivot", pivot_x="1.5")],
                ),
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "PIVOT", 20)
            self.assertTrue(any("pivot.x=1.5" in e for e in result.errors))

    def test_non_lossless_texture_compression_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "compressed.png.meta"
            path.write_text(make_meta(compression=1), encoding="utf-8")
            result = umv.validate_meta(path, "COMPRESSED", 20)
            self.assertTrue(any("not lossless" in e for e in result.errors))

    def test_missing_guid_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no_guid.png.meta"
            path.write_text(
                "fileFormatVersion: 2\nTextureImporter:\n  spriteMode: 0\n",
                encoding="utf-8",
            )
            result = umv.validate_meta(path, "NO_GUID", 20)
            self.assertTrue(any("missing top-level guid" in e for e in result.errors))

    def test_real_muse_meta_is_parsed_without_bounds_errors(self):
        meta_path = REPO_ROOT / "Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png.meta"
        if not meta_path.exists():
            self.skipTest("real Muse .meta is not present in this checkout")
        result = umv.validate_meta(
            meta_path, "CHR_MINH_KIEM_WALK", 20, image_size=(288, 512)
        )
        self.assertEqual(20.0, result.ppu)
        self.assertEqual(2, result.sprite_mode)
        self.assertEqual(48, len(result.sprites))
        self.assertFalse(any("image bounds" in e for e in result.errors), result.errors)
        # Muse currently ships Bilinear; that is a real finding, not a parser gap.
        self.assertTrue(any("filterMode=1" in e for e in result.errors))


class IntegrationCLITests(unittest.TestCase):
    def run_cli(self, root: Path, *arguments, cwd=None):
        cmd = [
            sys.executable,
            str(HANDOFF_DIR / "validate_import.py"),
            "--root",
            str(root),
            *arguments,
        ]
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd or root),
        )

    def _valid_root(self, root: Path):
        write_asset_fixture(
            root,
            make_png(8, 8, alpha_at=(0, 0)),
            make_meta(
                sprite_mode=2,
                sprites=[make_sprite("frame_0", 0, 0, 4, 4)],
            ),
        )
        write_manifest(root, [asset_entry()])

    def test_valid_fixture_passes_from_alternate_root_and_cwd(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            root = Path(tmp)
            self._valid_root(root)
            result = self.run_cli(root, "--manifest", "manifest.json", cwd=Path(other))
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("all imports validated", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_corrupted_idat_crc_fails_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_asset_fixture(
                root,
                make_png(8, 8, corrupt_idat_crc=True),
                make_meta(sprite_mode=0),
            )
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("CRC mismatch in IDAT", result.stdout)

    def test_signature_ihdr_only_fails_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ihdr = struct.pack(">IIBBBBB", 8, 8, 8, 6, 0, 0, 0)
            write_asset_fixture(
                root,
                b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr),
                make_meta(sprite_mode=0),
            )
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("no IDAT", result.stdout)

    def test_truncated_idat_fails_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = make_png(8, 8)
            cut = data[: data.index(b"IDAT") + 11]
            write_asset_fixture(root, cut, make_meta(sprite_mode=0))
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("truncated", result.stdout)

    def test_empty_texture_importer_fails_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_asset_fixture(
                root,
                make_png(8, 8),
                make_meta(importer_body=""),
            )
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("spritePixelsToUnits", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_multiline_rects_pass_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_asset_fixture(
                root,
                make_png(8, 8, alpha_at=(0, 0)),
                make_meta(sprite_mode=2, sprites=[make_sprite("frame_0", 0, 0, 4, 4)]),
            )
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("all imports validated", result.stdout)

    def test_fractional_ppu_fails_via_cli_with_original_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_asset_fixture(
                root,
                make_png(8, 8),
                make_meta(ppu="20.5", sprite_mode=0),
            )
            write_manifest(root, [asset_entry()])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("spritePixelsToUnits=20.5", result.stdout)

    def test_duplicate_guid_across_assets_fails_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared_guid = "0123456789abcdef0123456789abcdef"
            for index, name in enumerate(("a.png", "b.png")):
                write_asset_fixture(
                    root,
                    make_png(8, 8),
                    make_meta(guid=shared_guid, sprite_mode=0),
                    path=f"art/{name}",
                    asset_id=f"TEST_{index}",
                )
            write_manifest(
                root,
                [
                    asset_entry("art/a.png", "TEST_0"),
                    asset_entry("art/b.png", "TEST_1"),
                ],
            )
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("duplicate guid", result.stdout)

    def test_path_escape_is_reported_not_traced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(root, [asset_entry("../outside.png")])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("escapes --root", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_png_is_reported_not_traced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(root, [asset_entry("art/missing.png")])
            result = self.run_cli(root, "--manifest", "manifest.json")
            self.assertEqual(1, result.returncode)
            self.assertIn("does not exist under --root", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_report_is_written_under_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._valid_root(root)
            result = self.run_cli(
                root, "--manifest", "manifest.json", "--report", "reports/import.txt"
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((root / "reports" / "import.txt").exists())


if __name__ == "__main__":
    unittest.main()
