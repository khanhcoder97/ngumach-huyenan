#!/usr/bin/env python3
"""Tests for OPC-07 import metadata validation.

Run from repo root:
    python -m unittest discover -s Implementation/Asset_Handoff/tests -v
"""

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

import png_validation as pv
import png_alpha_check as palpha
import unity_meta_validation as umv


def chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def make_png(width=8, height=8, bit_depth=8, color_type=6, interlace=0,
             corrupted_crc=False):
    """Return a minimal PNG buffer."""
    ihdr_data = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, interlace)
    ihdr = chunk(b"IHDR", ihdr_data)
    scanline = b"\x00" + (width * 4 * b"\x00")
    idat = chunk(b"IDAT", zlib.compress(scanline * height))
    iend = chunk(b"IEND", b"")
    if corrupted_crc:
        # Flip last byte of IDAT CRC to trigger error in validate_png_structure
        idat = idat[:-1] + bytes((idat[-1] ^ 1,))
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


class PNGStructureTests(unittest.TestCase):
    def test_valid_rgba_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.png"
            path.write_bytes(make_png(16, 16, 8, 6))
            w, h, bd, ct, interlace, warnings = pv.validate_png_structure(path)
            self.assertEqual(16, w)
            self.assertEqual(16, h)
            self.assertEqual(8, bd)
            self.assertEqual(6, ct)
            self.assertFalse(interlace)
            self.assertEqual([], warnings)

    def test_truncated_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trunc.png"
            path.write_bytes(make_png(8, 8)[:24])  # cut mid IDAT
            with self.assertRaises(pv.PNGValidationProblem):
                pv.validate_png_structure(path)

    def test_lfs_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lfs.png"
            path.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:...\nsize 123\n")
            with self.assertRaises(pv.PNGValidationProblem):
                pv.validate_png_structure(path)


class AlphaCheckTests(unittest.TestCase):
    def test_rgba_has_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rgba.png"
            path.write_bytes(make_png(16, 16, 8, 6))
            has_alpha, msg = palpha.read_png_alpha_info(path)
            self.assertTrue(has_alpha, f"expected alpha for RGBA; got {msg}")

    def test_grayscale_no_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gray.png"
            path.write_bytes(make_png(16, 16, 8, 0))
            has_alpha, msg = palpha.read_png_alpha_info(path)
            self.assertFalse(has_alpha, "grayscale should have no alpha")

    def test_rgb_no_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rgb.png"
            path.write_bytes(make_png(16, 16, 8, 2))
            has_alpha, msg = palpha.read_png_alpha_info(path)
            self.assertFalse(has_alpha, "truecolor without alpha should have none")


class MetaValidatorTests(unittest.TestCase):
    def test_valid_meta_reads_ppu_and_mipmaps(self):
        MINH_KIEM_META_PATH = REPO_ROOT / "Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png.meta"
        if not MINH_KIEM_META_PATH.exists():
            self.skipTest("real meta file not present")
        result = umv.validate_meta(MINH_KIEM_META_PATH, "CHR_MINH_KIEM_WALK", 20)
        self.assertEqual(20, result.ppu)
        self.assertTrue(result.mipmaps_disabled)
        self.assertEqual(2, result.sprite_mode)
        self.assertIsNotNone(result.guid)
        # Real Muse asset uses Bilinear (filterMode=1); we detect this as a finding for pixel art review
        self.assertFalse(result.filter_mode_ok)

    def test_duplicate_sprite_names_inline_format(self):
        """Verify that duplicate names in inline rect format are detected."""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.png.meta"
            # Unity's .meta includes serializedVersion on each sprite entry
            p.write_text("""guid: 00000000000000000000000000000000
TextureImporter:
  filterMode: 0
  enableMipMap: 0
  spritePixelsToUnits: 20
  spriteMode: 2
  spriteSheet:
    sprites:
    - serializedVersion: 2
      name: unique_name_A
      rect: {x: 0, y: 448, width: 8, height: 8}
    - serializedVersion: 2
      name: unique_name_A
      rect: {x: 8, y: 448, width: 8, height: 8}
""")
            result = umv.validate_meta(p, "BAD_META", 20)
            errors_lower = [e.lower() for e in result.errors]
            self.assertTrue(any("duplicate" in e for e in errors_lower), f"errors={result.errors}")


class IntegrationCLITests(unittest.TestCase):
    def run_cli(self, *arguments):
        cmd = [sys.executable, str(HANDOFF_DIR / "validate_import.py"), *arguments]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))

    def test_cli_reports_filter_mode_finding(self):
        """Real Muse .meta uses Bilinear; validator reports this as an error."""
        r = self.run_cli("--manifest", "Client/Assets/ArtManifests/muse_delivery_manifest.json")
        self.assertEqual(1, r.returncode, "expected failure due to Bilinear detection")
        self.assertIn("filterMode=1", r.stdout)


if __name__ == "__main__":
    unittest.main()
