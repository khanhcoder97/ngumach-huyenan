#!/usr/bin/env python3
"""Tests for OPC-09 deterministic bundle audit, pack, unpack and verify.

Run from repo root:
    python -m unittest discover -s Tools/AssetPack/tests -v
"""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import audit_bundle as ab  # noqa: E402
import bundle_format as bf  # noqa: E402
import pack_bundle as pb  # noqa: E402
import unpack_bundle as ub  # noqa: E402


def make_png(width=48, height=64, color_type=6, bit_depth=8):
    """Return a minimal valid PNG buffer (stdlib only)."""
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    ihdr_chunk = (
        struct.pack(">I", 13)
        + b"IHDR"
        + ihdr
        + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF)
    )
    scanline = b"\x00" + (width * 4 * b"\x00")
    idat_data = zlib.compress(scanline * height)
    idat_chunk = (
        struct.pack(">I", len(idat_data))
        + b"IDAT"
        + idat_data
        + struct.pack(">I", zlib.crc32(b"IDAT" + idat_data) & 0xFFFFFFFF)
    )
    iend_chunk = (
        struct.pack(">I", 0)
        + b"IEND"
        + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    )
    return b"\x89PNG\r\n\x1a\n" + ihdr_chunk + idat_chunk + iend_chunk


class BundleFixture(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory(prefix="opc09_")
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp = Path(self._tmpdir.name)
        self.root = self.tmp / "repo"
        (self.root / "Client/Assets/Art/Characters/MinhKiem").mkdir(parents=True)
        (self.root / "Client/Assets/ArtManifests").mkdir(parents=True)
        self.manifest_rel = "Client/Assets/ArtManifests/test_manifest.json"

    def write_manifest(self, assets, pack_id="PK_TEST", version="v1.0.0"):
        manifest = {
            "assetPackId": pack_id,
            "assetPackVersion": version,
            "owner": "Muse",
            "sourceLicense": "original",
            "assets": assets,
        }
        path = self.root / self.manifest_rel
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path, manifest

    def write_png(self, rel, width=48, height=64):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(make_png(width, height))
        return path

    @staticmethod
    def asset(
        asset_id="CHR_WALK",
        path="Client/Assets/Art/Characters/MinhKiem/walk.png",
        status="approved",
        **overrides,
    ):
        entry = {
            "assetId": asset_id,
            "path": path,
            "kind": "sprite_sheet",
            "status": status,
            "pixelWidth": 48,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "previewPath": "Client/Assets/Art/Previews/x.png",
        }
        entry.update(overrides)
        return entry

    def pack(self, manifest, output=None, allowlist=None, allow_draft=False,
             dry_run=True):
        return pb.pack_bundle(
            manifest,
            self.root,
            self.manifest_rel,
            allowlist=allowlist,
            allow_draft=allow_draft,
            dry_run=dry_run,
            output_dir=output or (self.tmp / "unused"),
        )


class AuditTests(BundleFixture):
    def test_present_asset_gets_sha_and_size(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(1, report["summary"]["present"])
        record = report["assets"][0]
        self.assertEqual(ab.COVERAGE_PRESENT, record["coverage"])
        self.assertEqual(64, len(record["sha256"]))
        self.assertGreater(record["sizeBytes"], 0)

    def test_absent_asset(self):
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/none.png")]
        )
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(1, report["summary"]["absent"])
        self.assertEqual(ab.COVERAGE_ABSENT, report["assets"][0]["coverage"])

    def test_lfs_pointer_is_unverified(self):
        path = self.root / "Client/Assets/Art/Characters/MinhKiem/lfs.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\nsize 1\n",
            encoding="utf-8",
        )
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/lfs.png")]
        )
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(1, report["summary"]["unverified"])
        self.assertEqual(ab.COVERAGE_UNVERIFIED, report["assets"][0]["coverage"])

    def test_report_is_byte_deterministic(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        first = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        second = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(first, second)
        out1 = self.tmp / "audit1"
        out2 = self.tmp / "audit2"
        ab.write_report(first, out1, False, self.root)
        ab.write_report(second, out2, False, self.root)
        self.assertEqual(
            (out1 / "bundle-audit-report.json").read_bytes(),
            (out2 / "bundle-audit-report.json").read_bytes(),
        )
        self.assertEqual(
            (out1 / "bundle-audit-summary.txt").read_bytes(),
            (out2 / "bundle-audit-summary.txt").read_bytes(),
        )
        self.assertNotIn("auditedAt", first)

    def test_unknown_when_no_path(self):
        asset = self.asset()
        asset.pop("path")
        _path, manifest = self.write_manifest([asset])
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(ab.COVERAGE_UNKNOWN, report["assets"][0]["coverage"])

    def test_duplicate_asset_id_and_path_are_reported(self):
        path = "Client/Assets/Art/Characters/MinhKiem/walk.png"
        self.write_png(path)
        _path, manifest = self.write_manifest(
            [
                self.asset("CHR_DUP", path),
                self.asset("CHR_DUP", "Client/Assets/Art/Characters/MinhKiem/other.png"),
                self.asset("CHR_OTHER", path),
            ]
        )
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(["CHR_DUP"], report["duplicateAssetIds"])
        self.assertEqual([path], report["duplicatePaths"])
        self.assertEqual(1, report["summary"]["duplicateAssetIds"])
        self.assertEqual(1, report["summary"]["duplicatePaths"])
        self.assertTrue(
            any("duplicate path" in finding
                for record in report["assets"]
                for finding in record["findings"])
        )

    def test_dependencies_are_recorded(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest(
            [self.asset(dependencies=["CHR_BASE"], replacesAssetId="CHR_OLD")]
        )
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(
            ["CHR_BASE", "CHR_OLD"], report["assets"][0]["dependencies"]
        )

    def test_symlink_escape_is_not_hashed(self):
        outside = self.tmp / "outside.png"
        outside.write_bytes(make_png())
        link = self.root / "Client/Assets/Art/Characters/MinhKiem/link.png"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is not permitted on this platform")
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/link.png")]
        )
        report = ab.audit_bundle(manifest, self.root, self.manifest_rel)
        self.assertEqual(ab.COVERAGE_UNKNOWN, report["assets"][0]["coverage"])
        self.assertTrue(
            any("escapes the repository root" in finding
                for finding in report["assets"][0]["findings"])
        )


class PackTests(BundleFixture):
    def test_dry_run_includes_valid_asset_and_writes_nothing(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        out = self.tmp / "out"
        report = self.pack(manifest, output=out)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(1, report["includedCount"])
        self.assertFalse(out.exists())

    def test_deprecated_asset_fails(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/old.png")
        _path, manifest = self.write_manifest(
            [self.asset(status="deprecated",
                        path="Client/Assets/Art/Characters/MinhKiem/old.png")]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_draft_blocked_without_allow_draft(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/draft.png")
        _path, manifest = self.write_manifest(
            [self.asset(status="draft",
                        path="Client/Assets/Art/Characters/MinhKiem/draft.png")]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_draft_allowed_marks_bundle_draft(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/draft.png")
        _path, manifest = self.write_manifest(
            [self.asset(status="draft",
                        path="Client/Assets/Art/Characters/MinhKiem/draft.png")]
        )
        out = self.tmp / "draft_out"
        report = self.pack(manifest, output=out, allow_draft=True, dry_run=False)
        self.assertTrue(report["ok"], report["errors"])
        self.assertTrue(report["draft"])
        bundle_manifest = json.loads(
            (out / "bundle-manifest.json").read_text(encoding="utf-8")
        )
        self.assertTrue(bundle_manifest["draft"])

    def test_missing_file_fails(self):
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/gone.png")]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_lfs_pointer_fails(self):
        path = self.root / "Client/Assets/Art/Characters/MinhKiem/lfs.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\nsize 1\n",
            encoding="utf-8",
        )
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/lfs.png")]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertIn("lfs pointer", report["skipped"][0]["reason"])

    def test_allowlist_excludes_off_list_asset(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        report = self.pack(
            manifest,
            allowlist={"Client/Assets/Art/Characters/MinhKiem/other.png"},
        )
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["includedCount"])

    def test_parent_and_absolute_paths_fail(self):
        _path, manifest = self.write_manifest(
            [
                self.asset("CHR_PARENT", "../outside.png"),
                self.asset("CHR_ABS", "C:/Windows/win.ini"),
            ]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(any("invalid path" in item["reason"]
                            for item in report["skipped"]))

    def test_allowlist_traversal_entry_is_rejected(self):
        allowlist = self.tmp / "allowlist.txt"
        allowlist.write_text("../outside.png\n", encoding="utf-8")
        with self.assertRaises(pb.BundlePackError):
            pb.load_allowlist(allowlist)

    def test_duplicate_asset_id_fails(self):
        path = "Client/Assets/Art/Characters/MinhKiem/walk.png"
        self.write_png(path)
        _path, manifest = self.write_manifest(
            [
                self.asset("CHR_DUP", path),
                self.asset("CHR_DUP",
                           "Client/Assets/Art/Characters/MinhKiem/other.png"),
            ]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(any("duplicate assetId" in e for e in report["errors"]))

    def test_duplicate_path_fails(self):
        path = "Client/Assets/Art/Characters/MinhKiem/walk.png"
        self.write_png(path)
        _path, manifest = self.write_manifest(
            [self.asset("CHR_A", path), self.asset("CHR_B", path)]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(any("duplicate path" in e for e in report["errors"]))

    def test_valid_dependency_is_included_and_recorded(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/base.png")
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest(
            [
                self.asset("CHR_BASE",
                           "Client/Assets/Art/Characters/MinhKiem/base.png"),
                self.asset(dependencies=["CHR_BASE"]),
            ]
        )
        report = self.pack(manifest)
        self.assertTrue(report["ok"], report["errors"])
        child = next(
            entry for entry in report["included"] if entry["assetId"] == "CHR_WALK"
        )
        self.assertEqual(["CHR_BASE"], child["dependencies"])

    def test_missing_dependency_fails(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest(
            [self.asset(dependencies=["CHR_MISSING"])]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(any("does not exist" in e for e in report["errors"]))

    def test_self_dependency_fails(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest(
            [self.asset(dependencies=["CHR_WALK"])]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(any("cannot reference itself" in e for e in report["errors"]))

    def test_dependency_on_blocked_draft_fails(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/base.png")
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest(
            [
                self.asset("CHR_BASE",
                           "Client/Assets/Art/Characters/MinhKiem/base.png",
                           status="draft"),
                self.asset(dependencies=["CHR_BASE"]),
            ]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(
            any("not included in this pack" in e for e in report["errors"])
        )

    def test_blocked_pack_creates_no_bundle_manifest(self):
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/gone.png")]
        )
        out = self.tmp / "blocked_out"
        report = self.pack(manifest, output=out, dry_run=False)
        self.assertFalse(report["ok"])
        self.assertFalse((out / "bundle-manifest.json").exists())

    def test_materialise_is_deterministic(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        out1 = self.tmp / "bundle1"
        out2 = self.tmp / "bundle2"
        first = self.pack(manifest, output=out1, dry_run=False)
        second = self.pack(manifest, output=out2, dry_run=False)
        self.assertTrue(first["ok"], first["errors"])
        self.assertEqual(first["bundleDigest"], second["bundleDigest"])
        self.assertEqual(
            (out1 / "bundle-manifest.json").read_bytes(),
            (out2 / "bundle-manifest.json").read_bytes(),
        )
        self.assertNotIn("packedAt", first)
        self.assertEqual(
            (out1 / "Client/Assets/Art/Characters/MinhKiem/walk.png").read_bytes(),
            (out2 / "Client/Assets/Art/Characters/MinhKiem/walk.png").read_bytes(),
        )

    def test_non_empty_output_directory_is_rejected(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        out = self.tmp / "not_empty"
        out.mkdir()
        (out / "keep.txt").write_text("do not overwrite", encoding="utf-8")
        with self.assertRaises(pb.BundlePackError):
            self.pack(manifest, output=out, dry_run=False)

    def test_symlink_escape_fails(self):
        outside = self.tmp / "outside.png"
        outside.write_bytes(make_png())
        link = self.root / "Client/Assets/Art/Characters/MinhKiem/link.png"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is not permitted on this platform")
        _path, manifest = self.write_manifest(
            [self.asset(path="Client/Assets/Art/Characters/MinhKiem/link.png")]
        )
        report = self.pack(manifest)
        self.assertFalse(report["ok"])
        self.assertTrue(
            any("escapes the repository root" in e for e in report["errors"])
        )


class UnpackTests(BundleFixture):
    def _packed_bundle(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        _path, manifest = self.write_manifest([self.asset()])
        out = self.tmp / "bundle"
        report = self.pack(manifest, output=out, dry_run=False)
        self.assertTrue(report["ok"], report["errors"])
        return out, report

    def test_pack_verify_unpack_roundtrip(self):
        bundle, pack_report = self._packed_bundle()
        verified = ub.verify_bundle(bundle)
        self.assertTrue(verified["ok"], verified["errors"])
        self.assertEqual(pack_report["bundleDigest"], verified["computedDigest"])

        unpacked = self.tmp / "unpacked"
        result = ub.unpack_bundle(bundle, unpacked)
        self.assertTrue(result["ok"], result["errors"] + result.get("outputErrors", []))
        self.assertEqual(pack_report["bundleDigest"], result["outputDigest"])
        self.assertTrue(
            (unpacked / "Client/Assets/Art/Characters/MinhKiem/walk.png").is_file()
        )

    def test_tampered_asset_fails_digest_and_size(self):
        bundle, _report = self._packed_bundle()
        asset = bundle / "Client/Assets/Art/Characters/MinhKiem/walk.png"
        asset.write_bytes(asset.read_bytes() + b"tampered")
        result = ub.verify_bundle(bundle)
        self.assertFalse(result["ok"])
        self.assertTrue(any("size mismatch" in e for e in result["errors"]))
        self.assertTrue(any("sha256 mismatch" in e for e in result["errors"]))

    def test_tampered_bundle_digest_fails(self):
        bundle, _report = self._packed_bundle()
        manifest_path = bundle / "bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bundleDigest"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = ub.verify_bundle(bundle)
        self.assertFalse(result["ok"])
        self.assertTrue(any("bundleDigest mismatch" in e for e in result["errors"]))

    def test_path_escape_in_bundle_manifest_fails(self):
        bundle, _report = self._packed_bundle()
        manifest_path = bundle / "bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"][0]["path"] = "../outside.png"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = ub.verify_bundle(bundle)
        self.assertFalse(result["ok"])
        self.assertTrue(any("must not contain" in e or "path:" in e
                            for e in result["errors"]))

    def test_duplicate_path_in_bundle_manifest_fails(self):
        bundle, _report = self._packed_bundle()
        manifest_path = bundle / "bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"].append(dict(manifest["assets"][0]))
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = ub.verify_bundle(bundle)
        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate" in e for e in result["errors"]))

    def test_failed_verification_creates_no_unpack_output(self):
        bundle, _report = self._packed_bundle()
        asset = bundle / "Client/Assets/Art/Characters/MinhKiem/walk.png"
        asset.write_bytes(b"corrupted")
        output = self.tmp / "should_not_exist"
        result = ub.unpack_bundle(bundle, output)
        self.assertFalse(result["ok"])
        self.assertFalse(output.exists())

    def test_non_empty_unpack_output_is_rejected(self):
        bundle, _report = self._packed_bundle()
        output = self.tmp / "not_empty"
        output.mkdir()
        (output / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(ub.BundleUnpackError):
            ub.unpack_bundle(bundle, output)


class CliTests(BundleFixture):
    def run_cli(self, script, *arguments, cwd=None):
        return subprocess.run(
            [sys.executable, str(TOOL_DIR / script), *arguments],
            capture_output=True,
            text=True,
            cwd=str(cwd or self.tmp),
        )

    def test_audit_and_pack_from_alternate_root_and_cwd(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        self.write_manifest([self.asset()])
        allowlist = self.root / "allowlist.txt"
        allowlist.write_text(
            "Client/Assets/Art/Characters/MinhKiem/walk.png\n", encoding="utf-8"
        )
        audit_out = self.tmp / "audit_cli"
        audit = self.run_cli(
            "audit_bundle.py",
            "--root", str(self.root),
            "--manifest", self.manifest_rel,
            "--output", str(audit_out),
        )
        self.assertEqual(0, audit.returncode, audit.stdout + audit.stderr)
        self.assertIn("bundleDigest=", audit.stdout)
        self.assertNotIn("Traceback", audit.stderr)

        bundle_out = self.tmp / "bundle_cli"
        pack = self.run_cli(
            "pack_bundle.py",
            "--root", str(self.root),
            "--manifest", self.manifest_rel,
            "--allowlist", "allowlist.txt",
            "--output", str(bundle_out),
        )
        self.assertEqual(0, pack.returncode, pack.stdout + pack.stderr)
        self.assertTrue((bundle_out / "bundle-manifest.json").is_file())

        unpacked = self.tmp / "unpacked_cli"
        unpack = self.run_cli(
            "unpack_bundle.py",
            "--bundle", str(bundle_out),
            "--output", str(unpacked),
        )
        self.assertEqual(0, unpack.returncode, unpack.stdout + unpack.stderr)
        self.assertIn("OK: bundle verified", unpack.stdout)
        self.assertTrue(
            (unpacked / "Client/Assets/Art/Characters/MinhKiem/walk.png").is_file()
        )

    def test_cli_blocked_pack_exits_2_without_bundle(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        self.write_manifest([self.asset(status="draft")])
        out = self.tmp / "blocked_cli"
        result = self.run_cli(
            "pack_bundle.py",
            "--root", str(self.root),
            "--manifest", self.manifest_rel,
            "--allowlist", "missing-allowlist.txt",
            "--output", str(out),
        )
        # Missing allowlist means "all allowed"; draft is still blocked.
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertFalse((out / "bundle-manifest.json").exists())
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_verify_detects_tampering(self):
        self.write_png("Client/Assets/Art/Characters/MinhKiem/walk.png")
        self.write_manifest([self.asset()])
        out = self.tmp / "bundle_tamper"
        pack = self.run_cli(
            "pack_bundle.py",
            "--root", str(self.root),
            "--manifest", self.manifest_rel,
            "--allowlist", "missing-allowlist.txt",
            "--output", str(out),
        )
        self.assertEqual(0, pack.returncode, pack.stdout + pack.stderr)
        target = out / "Client/Assets/Art/Characters/MinhKiem/walk.png"
        target.write_bytes(target.read_bytes() + b"x")
        verify = self.run_cli("unpack_bundle.py", "--bundle", str(out))
        self.assertEqual(2, verify.returncode, verify.stdout + verify.stderr)
        self.assertIn("sha256 mismatch", verify.stdout)


if __name__ == "__main__":
    unittest.main()
