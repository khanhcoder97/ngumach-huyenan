"""Tests for the OPC-06 manifest v2 geometry and migration draft.

Run from the repository root:
    python -m unittest discover -s Implementation/Asset_Handoff/tests -v
"""

import copy
import json
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

import migrate_manifest_v2 as migration  # noqa: E402
import validate_asset_delivery as vad  # noqa: E402

SCHEMA_V1 = vad.load_json(HANDOFF_DIR / "asset_delivery_manifest.schema.json")
SCHEMA_V2 = vad.load_json(HANDOFF_DIR / "asset_delivery_manifest.v2.schema.json")
FIXTURES = HANDOFF_DIR / "fixtures" / "manifest_v2"
VALIDATOR = HANDOFF_DIR / "validate_asset_delivery.py"
MIGRATOR = HANDOFF_DIR / "migrate_manifest_v2.py"
REAL_MANIFEST = REPO_ROOT / "Client" / "Assets" / "ArtManifests" / "muse_delivery_manifest.json"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_real_manifest():
    return json.loads(REAL_MANIFEST.read_text(encoding="utf-8"))


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def make_png(width, height):
    scanline = b"\x00" + bytes(width * 4)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(scanline * height)) + chunk(b"IEND", b""))


def actor_asset(**overrides):
    asset = {
        "assetId": "CHR_MINH_KIEM_WALK",
        "path": "Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png",
        "kind": "sprite_sheet",
        "status": "draft",
        "pixelWidth": 288,
        "pixelHeight": 512,
        "pixelsPerUnit": 20,
        "pivot": "bottom_center",
        "isDirectional": True,
        "layout": "direction_rows",
        "frameSize": {"width": 48, "height": 64},
        "directions": list(vad.DIRECTIONS),
        "animations": [{"name": "walk", "framesPerDirection": 6, "fps": 8, "loop": True}],
        "previewPath": "Client/Assets/Art/Previews/minh_kiem_walk_preview_x4.png",
    }
    asset.update(overrides)
    return asset


def manifest_v2(assets, **overrides):
    doc = {
        "manifestVersion": 2,
        "assetPackId": "p1_minh_kiem_walk",
        "assetPackVersion": "v0.1.0",
        "owner": "Muse",
        "sourceLicense": "original",
        "assets": assets,
    }
    doc.update(overrides)
    return doc


class ManifestV2FixtureTests(unittest.TestCase):
    """The checked-in fixtures must stay valid or fail for the documented reason."""

    def validate_fixture(self, name):
        doc = load_fixture(name)
        return vad.validate_manifest(doc, SCHEMA_V2, REPO_ROOT, check_files=False)

    def assert_fixture_clean(self, name):
        errors, warnings = self.validate_fixture(name)
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual([], warnings, "\n".join(warnings))

    def assert_fixture_error(self, name, needle):
        errors, _ = self.validate_fixture(name)
        self.assertTrue(errors, f"{name} should fail but passed")
        joined = "\n".join(errors)
        self.assertIn(needle, joined, joined)
        return joined

    def test_valid_actor_8dir_passes(self):
        self.assert_fixture_clean("valid_actor_8dir.json")

    def test_valid_effect_single_direction_passes(self):
        self.assert_fixture_clean("valid_effect_single_direction.json")

    def test_valid_icon_static_passes(self):
        self.assert_fixture_clean("valid_icon_static.json")

    def test_valid_multi_animation_ranges_passes(self):
        self.assert_fixture_clean("valid_multi_animation_ranges.json")

    def test_missing_frame_size_is_rejected(self):
        self.assert_fixture_error("invalid_missing_frame_size.json", "frameSize")

    def test_grid_mismatch_is_rejected(self):
        self.assert_fixture_error("invalid_grid_mismatch.json", "not divisible")

    def test_duplicate_direction_is_rejected(self):
        self.assert_fixture_error("invalid_duplicate_direction.json", "duplicate direction")

    def test_direction_order_is_rejected(self):
        self.assert_fixture_error("invalid_direction_order.json", "direction order")

    def test_unsupported_version_is_rejected(self):
        joined = self.assert_fixture_error(
            "invalid_unsupported_version.json", "unsupported manifestVersion"
        )
        self.assertIn("supported versions are", joined)

    def test_overlapping_clips_are_rejected(self):
        self.assert_fixture_error("invalid_animation_overlap.json", "overlap")


class ManifestV2RuleTests(unittest.TestCase):
    def validate(self, doc):
        return vad.validate_manifest(doc, SCHEMA_V2, REPO_ROOT, check_files=False)

    def test_requires_explicit_directionality(self):
        asset = actor_asset()
        asset.pop("isDirectional")
        errors, _ = self.validate(manifest_v2([asset]))
        self.assertTrue(errors)
        self.assertIn("isDirectional", "\n".join(errors))

    def test_vfx_directional_is_unsupported(self):
        asset = {
            "assetId": "VFX_FIXTURE_SLASH",
            "path": "Client/Assets/VFX/Fixtures/fixture_slash.png",
            "kind": "vfx_sheet",
            "status": "draft",
            "pixelWidth": 96,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "isDirectional": True,
            "layout": "strip",
            "frameSize": {"width": 24, "height": 64},
            "animations": [{"name": "slash", "frames": 4, "fps": 12}],
            "previewPath": "Client/Assets/VFX/Fixtures/fixture_slash_preview.png",
        }
        errors, _ = self.validate(manifest_v2([asset], assetPackId="p1_effect_fixture"))
        joined = "\n".join(errors)
        self.assertIn("single-direction", joined)

    def test_strip_requires_exactly_one_row(self):
        asset = load_fixture("valid_effect_single_direction.json")["assets"][0]
        asset["pixelHeight"] = 128
        errors, _ = self.validate(manifest_v2([asset]))
        self.assertIn("exactly one row", "\n".join(errors))

    def test_static_kind_rejects_frame_size(self):
        asset = load_fixture("valid_icon_static.json")["assets"][0]
        asset["frameSize"] = {"width": 32, "height": 32}
        errors, _ = self.validate(manifest_v2([asset]))
        self.assertIn("only sprite_sheet and vfx_sheet", "\n".join(errors))

    def test_legacy_v2_fields_without_version_marker_fail_v1_schema(self):
        doc = manifest_v2([actor_asset()])
        doc.pop("manifestVersion")
        errors, _ = vad.validate_manifest(doc, SCHEMA_V1, REPO_ROOT, check_files=False)
        joined = "\n".join(errors)
        self.assertIn("unexpected property", joined)

    def test_legacy_manifest_still_passes_v1(self):
        doc = load_real_manifest()
        self.assertNotIn("manifestVersion", doc)
        errors, warnings = vad.validate_manifest(doc, SCHEMA_V1, REPO_ROOT, check_files=False)
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual([], warnings, "\n".join(warnings))

    def test_boolean_version_is_not_treated_as_one(self):
        doc = load_real_manifest()
        doc["manifestVersion"] = True
        errors, _ = vad.validate_manifest(doc, SCHEMA_V1, REPO_ROOT, check_files=False)
        self.assertIn("unsupported manifestVersion", "\n".join(errors))

    def test_explicit_version_one_still_passes_v1(self):
        doc = load_real_manifest()
        doc["manifestVersion"] = 1
        errors, _ = vad.validate_manifest(doc, SCHEMA_V1, REPO_ROOT, check_files=False)
        self.assertEqual([], errors, "\n".join(errors))

    def test_out_of_bounds_clip_is_rejected(self):
        asset = actor_asset()
        asset["animations"] = [
            {"name": "walk", "framesPerDirection": 6, "fps": 8},
            {"name": "run", "framesPerDirection": 3, "fps": 10, "columnStart": 4},
        ]
        errors, _ = self.validate(manifest_v2([asset]))
        self.assertIn("covers columns", "\n".join(errors))

    def test_duplicate_animation_name_is_rejected(self):
        asset = actor_asset()
        asset["animations"] = [
            {"name": "walk", "framesPerDirection": 3, "fps": 8},
            {"name": "walk", "framesPerDirection": 3, "fps": 10, "columnStart": 3},
        ]
        errors, _ = self.validate(manifest_v2([asset]))
        self.assertIn("duplicate animation name", "\n".join(errors))


class ManifestV2CliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *arguments],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

    def test_cli_auto_selects_v2_schema(self):
        result = self.run_cli(
            "--manifest",
            "Implementation/Asset_Handoff/fixtures/manifest_v2/valid_actor_8dir.json",
            "--skip-file-checks",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_cli_reports_v2_failure(self):
        result = self.run_cli(
            "--manifest",
            "Implementation/Asset_Handoff/fixtures/manifest_v2/invalid_missing_frame_size.json",
            "--skip-file-checks",
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("frameSize", result.stdout)

    def test_cli_legacy_manifest_still_defaults_to_v1(self):
        result = self.run_cli(
            "--manifest",
            "Client/Assets/ArtManifests/muse_delivery_manifest.json",
            "--skip-file-checks",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class MigrationTests(unittest.TestCase):
    def test_real_manifest_migrates_to_48x64(self):
        source = load_real_manifest()
        migrated, problems, changed = migration.migrate_manifest(source)
        self.assertEqual([], problems)
        self.assertTrue(changed)
        self.assertEqual(2, migrated["manifestVersion"])
        asset = migrated["assets"][0]
        self.assertTrue(asset["isDirectional"])
        self.assertEqual("direction_rows", asset["layout"])
        self.assertEqual({"width": 48, "height": 64}, asset["frameSize"])
        self.assertEqual(6, asset["animations"][0]["framesPerDirection"])
        self.assertNotIn("frames", asset["animations"][0])

    def test_migration_does_not_mutate_source(self):
        source = load_real_manifest()
        before = copy.deepcopy(source)
        migration.migrate_manifest(source)
        self.assertEqual(before, source)

    def test_migrated_manifest_passes_v2_validation(self):
        source = load_real_manifest()
        migrated, problems, _ = migration.migrate_manifest(source)
        self.assertEqual([], problems)
        errors, warnings = vad.validate_manifest(
            migrated, SCHEMA_V2, REPO_ROOT, check_files=False
        )
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual([], warnings, "\n".join(warnings))

    def test_multiple_animations_are_not_guessed(self):
        source = load_real_manifest()
        source["assets"][0]["animations"].append(
            {"name": "run", "framesPerDirection": 6, "fps": 12}
        )
        migrated, problems, _ = migration.migrate_manifest(source)
        self.assertTrue(problems, migrated)
        self.assertIn("exactly one animation", "\n".join(problems))

    def test_vfx_sheet_without_explicit_layout_is_blocked(self):
        source = manifest_v2([], assetPackId="p1_effect_fixture")
        source.pop("manifestVersion")
        source["assets"] = [{
            "assetId": "VFX_FIXTURE_SLASH",
            "path": "Client/Assets/VFX/Fixtures/fixture_slash.png",
            "kind": "vfx_sheet",
            "status": "draft",
            "pixelWidth": 96,
            "pixelHeight": 64,
            "pixelsPerUnit": 20,
            "animations": [{"name": "slash", "frames": 4, "fps": 12}],
            "previewPath": "Client/Assets/VFX/Fixtures/fixture_slash_preview.png",
        }]
        _, problems, _ = migration.migrate_manifest(source)
        self.assertTrue(problems)
        self.assertIn("requires explicit", "\n".join(problems))

    def test_static_icon_only_gets_version_marker(self):
        source = manifest_v2([], assetPackId="p1_icon_fixture")
        source.pop("manifestVersion")
        source["assets"] = [load_fixture("valid_icon_static.json")["assets"][0]]
        migrated, problems, _ = migration.migrate_manifest(source)
        self.assertEqual([], problems)
        self.assertEqual(2, migrated["manifestVersion"])
        self.assertEqual(source["assets"][0], migrated["assets"][0])

    def test_static_kind_with_directions_is_blocked(self):
        source = manifest_v2([], assetPackId="p1_icon_fixture")
        source.pop("manifestVersion")
        icon = copy.deepcopy(load_fixture("valid_icon_static.json")["assets"][0])
        icon["directions"] = ["N"]
        source["assets"] = [icon]
        _, problems, _ = migration.migrate_manifest(source)
        self.assertTrue(problems)
        self.assertIn("must not declare directions", "\n".join(problems))

    def test_diff_mentions_frame_size(self):
        source = load_real_manifest()
        migrated, problems, _ = migration.migrate_manifest(source)
        self.assertEqual([], problems)
        diff = migration.unified_diff(source, migrated)
        self.assertIn("manifestVersion", diff)
        self.assertIn("frameSize", diff)
        self.assertIn('"width": 48', diff)

    def test_dry_run_does_not_touch_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(load_real_manifest()), encoding="utf-8")
            before = manifest.read_bytes()
            result = subprocess.run(
                [sys.executable, str(MIGRATOR), "--root", str(root),
                 "--manifest", "manifest.json", "--quiet"],
                capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(before, manifest.read_bytes())

    def test_output_refuses_source_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(load_real_manifest()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MIGRATOR), "--root", str(root),
                 "--manifest", "manifest.json", "--output", "manifest.json"],
                capture_output=True, text=True,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("must not overwrite", result.stderr)

    def test_output_writes_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(load_real_manifest()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MIGRATOR), "--root", str(root),
                 "--manifest", "manifest.json", "--output", "out/manifest_v2.json"],
                capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            target = root / "out" / "manifest_v2.json"
            self.assertTrue(target.is_file())
            self.assertEqual(2, json.loads(target.read_text(encoding="utf-8"))["manifestVersion"])


if __name__ == "__main__":
    unittest.main()
