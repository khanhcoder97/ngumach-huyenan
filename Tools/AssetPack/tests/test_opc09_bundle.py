#!/usr/bin/env python3
"""Tests for OPC-09 bundle audit and pack tools.

Run from repo root:
    python -m unittest Tools.AssetPack.tests.test_opc09_bundle -v
"""

import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import audit_bundle as ab
import pack_bundle as pb


def make_png(width, height, color_type=6, bit_depth=8):
    """Return a minimal valid PNG bytes buffer (stdlib only)."""
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    ihdr_chunk = (struct.pack(">I", 13) + b"IHDR" + ihdr
                  + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xffffffff))
    scanline = b"\x00" + (width * 4 * b"\x00")
    idat_data = zlib.compress(scanline * height)
    idat_chunk = (struct.pack(">I", len(idat_data)) + b"IDAT" + idat_data
                  + struct.pack(">I", zlib.crc32(b"IDAT" + idat_data) & 0xffffffff))
    iend_chunk = (struct.pack(">I", 0) + b"IEND"
                  + struct.pack(">I", zlib.crc32(b"IEND") & 0xffffffff))
    return b"\x89PNG\r\n\x1a\n" + ihdr_chunk + idat_chunk + iend_chunk


class AuditTests(unittest.TestCase):
    """Tests for audit_bundle.py coverage verdicts and determinism."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="opc09_audit_"))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        (self.root / "Client" / "Assets" / "Art" / "Characters" / "MinhKiem").mkdir(parents=True)
        (self.root / "Client" / "Assets" / "ArtManifests").mkdir(parents=True)

    def _write_manifest(self, assets, pack_id="PK_TEST", version="v1.0.0"):
        manifest = {
            "assetPackId": pack_id,
            "assetPackVersion": version,
            "owner": "Muse",
            "sourceLicense": "original",
            "assets": assets,
        }
        mpath = self.root / "Client" / "Assets" / "ArtManifests" / "test_manifest.json"
        mpath.write_text(json.dumps(manifest), encoding="utf-8")
        return mpath

    def _write_png(self, rel, width=48, height=64):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(make_png(width, height))
        return p

    def test_present_asset_gets_sha_and_size(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/walk.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_WALK",
            "path": "Client/Assets/Art/Characters/MinhKiem/walk.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/walk_preview.png",
        }])
        report = ab.audit_bundle(json.loads(manifest.read_text()), self.root,
                                 "Client/Assets/ArtManifests/test_manifest.json")
        self.assertEqual(1, report["summary"]["present"])
        rec = report["assets"][0]
        self.assertEqual(ab.COVERAGE_PRESENT, rec["coverage"])
        self.assertIsNotNone(rec["sha256"])
        self.assertIsNotNone(rec["sizeBytes"])
        self.assertTrue(rec["sha256"].startswith(""))
        self.assertGreaterEqual(len(rec["sha256"]), 64)

    def test_absent_asset(self):
        manifest = self._write_manifest([{
            "assetId": "CHR_MISSING",
            "path": "Client/Assets/Art/Characters/MinhKiem/nonexistent.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = ab.audit_bundle(json.loads(manifest.read_text()), self.root,
                                 "Client/Assets/ArtManifests/test_manifest.json")
        self.assertEqual(1, report["summary"]["absent"])
        self.assertEqual(ab.COVERAGE_ABSENT, report["assets"][0]["coverage"])

    def test_lfs_pointer_is_unverified(self):
        p = self.root / "Client" / "Assets" / "Art" / "Characters" / "MinhKiem" / "lfs.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\nsize 123\n")
        manifest = self._write_manifest([{
            "assetId": "CHR_LFS",
            "path": "Client/Assets/Art/Characters/MinhKiem/lfs.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = ab.audit_bundle(json.loads(manifest.read_text()), self.root,
                                 "Client/Assets/ArtManifests/test_manifest.json")
        self.assertEqual(1, report["summary"]["unverified"])
        self.assertEqual(ab.COVERAGE_UNVERIFIED, report["assets"][0]["coverage"])

    def test_deterministic_output(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/walk.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_DET",
            "path": "Client/Assets/Art/Characters/MinhKiem/walk.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        m = json.loads(manifest.read_text())
        r1 = ab.audit_bundle(m, self.root, "Client/Assets/ArtManifests/test_manifest.json")
        r2 = ab.audit_bundle(m, self.root, "Client/Assets/ArtManifests/test_manifest.json")
        self.assertEqual(r1["bundleDigest"], r2["bundleDigest"])
        self.assertEqual(r1["assets"][0]["sha256"], r2["assets"][0]["sha256"])

    def test_unknown_when_no_path(self):
        manifest = self._write_manifest([{
            "assetId": "CHR_NOPATH",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = ab.audit_bundle(json.loads(manifest.read_text()), self.root,
                                 "Client/Assets/ArtManifests/test_manifest.json")
        self.assertEqual(ab.COVERAGE_UNKNOWN, report["assets"][0]["coverage"])


class PackTests(unittest.TestCase):
    """Tests for pack_bundle.py gating rules."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="opc09_pack_"))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        (self.root / "Client" / "Assets" / "Art" / "Characters" / "MinhKiem").mkdir(parents=True)
        (self.root / "Client" / "Assets" / "ArtManifests").mkdir(parents=True)

    def _write_manifest(self, assets, pack_id="PK_TEST", version="v1.0.0"):
        manifest = {
            "assetPackId": pack_id,
            "assetPackVersion": version,
            "owner": "Muse",
            "sourceLicense": "original",
            "assets": assets,
        }
        mpath = self.root / "Client" / "Assets" / "ArtManifests" / "test_manifest.json"
        mpath.write_text(json.dumps(manifest), encoding="utf-8")
        return mpath

    def _write_png(self, rel, width=48, height=64):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(make_png(width, height))
        return p

    def test_dry_run_includes_valid_asset(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/walk.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_WALK",
            "path": "Client/Assets/Art/Characters/MinhKiem/walk.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/walk_preview.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertTrue(report["ok"])
        self.assertEqual(1, report["includedCount"])
        self.assertEqual(0, report["errorCount"])
        # Dry run must not write anything.
        self.assertFalse((self.tmp / "out").exists())

    def test_deprecated_asset_fails(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/old.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_OLD",
            "path": "Client/Assets/Art/Characters/MinhKiem/old.png",
            "kind": "sprite_sheet",
            "status": "deprecated",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertFalse(report["ok"])
        self.assertGreaterEqual(1, report["errorCount"])
        self.assertEqual(0, report["includedCount"])

    def test_draft_blocked_without_allow_draft(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/draft.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_DRAFT",
            "path": "Client/Assets/Art/Characters/MinhKiem/draft.png",
            "kind": "sprite_sheet",
            "status": "draft",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_draft_allowed_with_flag(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/draft.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_DRAFT",
            "path": "Client/Assets/Art/Characters/MinhKiem/draft.png",
            "kind": "sprite_sheet",
            "status": "draft",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=True, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertTrue(report["ok"])
        self.assertEqual(1, report["includedCount"])

    def test_missing_file_fails(self):
        manifest = self._write_manifest([{
            "assetId": "CHR_MISSING",
            "path": "Client/Assets/Art/Characters/MinhKiem/gone.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_lfs_pointer_fails(self):
        p = self.root / "Client" / "Assets" / "Art" / "Characters" / "MinhKiem" / "lfs.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\nsize 123\n")
        manifest = self._write_manifest([{
            "assetId": "CHR_LFS",
            "path": "Client/Assets/Art/Characters/MinhKiem/lfs.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_allowlist_excludes_off_list_asset(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/walk.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_WALK",
            "path": "Client/Assets/Art/Characters/MinhKiem/walk.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }])
        allowlist = self.root / "allowlist.txt"
        allowlist.write_text("Client/Assets/Art/Other/other.png\n", encoding="utf-8")
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=set(allowlist.read_text().splitlines()),
                                allow_draft=False, dry_run=True,
                                output_dir=self.tmp / "out")
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_materialise_writes_files(self):
        self._write_png("Client/Assets/Art/Characters/MinhKiem/walk.png", 48, 64)
        manifest = self._write_manifest([{
            "assetId": "CHR_WALK",
            "path": "Client/Assets/Art/Characters/MinhKiem/walk.png",
            "kind": "sprite_sheet",
            "status": "approved",
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/walk_preview.png",
        }])
        out = self.tmp / "bundle_out"
        report = pb.pack_bundle(json.loads(manifest.read_text()), self.root,
                                "Client/Assets/ArtManifests/test_manifest.json",
                                allowlist=None, allow_draft=False, dry_run=False,
                                output_dir=out)
        self.assertTrue(report["ok"])
        self.assertTrue((out / "Client/Assets/Art/Characters/MinhKiem/walk.png").is_file())
        self.assertTrue((out / "bundle-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
