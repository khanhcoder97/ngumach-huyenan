"""Tests for the OPC-05 asset handoff validator.

Run from the repository root:
    python -m unittest discover -s Implementation/Asset_Handoff/tests -v
"""

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
if str(HANDOFF_DIR) not in sys.path:
    sys.path.insert(0, str(HANDOFF_DIR))

import validate_asset_delivery as vad  # noqa: E402  (path set above)

SCHEMA = vad.load_json(HANDOFF_DIR / "asset_delivery_manifest.schema.json")
EXAMPLE_MANIFEST = HANDOFF_DIR / "muse_delivery_manifest.example.json"
VALIDATOR = HANDOFF_DIR / "validate_asset_delivery.py"

SHEET_PATH = "Client/Assets/Art/Characters/hero_vanguard_idle.png"
SHEET_PREVIEW = "Client/Assets/Art/Previews/hero_vanguard_idle_preview.png"


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def make_png(width, height, *, bit_depth=8, color_type=6, interlace=0):
    """A real, minimal PNG whose IHDR carries the requested geometry."""
    bytes_per_pixel = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    scanline = b"\x00" + bytes(width * bytes_per_pixel)
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, interlace)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(scanline * height)) + chunk(b"IEND", b""))


def make_gif(width, height):
    return b"GIF89a" + struct.pack("<HH", width, height) + b"\x00" * 100


LFS_POINTER = (b"version https://git-lfs.github.com/spec/v1\r\n"
               b"oid sha256:0000000000000000000000000000000000000000000000000000000000000000\r\n"
               b"size 1234\r\n")


def sprite_asset(**overrides):
    """A small single sprite: the cheapest document that must pass every rule."""
    asset = {
        "assetId": "ICON_HERO_PORTAIT",
        "path": "Client/Assets/Art/Icons/hero_portrait.png",
        "kind": "icon",
        "status": "draft",
        "pixelWidth": 32,
        "pixelHeight": 32,
        "pixelsPerUnit": 20,
        "pivot": "center",
        "previewPath": "Client/Assets/Art/Previews/hero_portrait_preview.png",
    }
    asset.update(overrides)
    return asset


def sheet_asset(**overrides):
    """The reference 8-direction, 4-frame sheet from the shipped example manifest."""
    asset = {
        "assetId": "CHR_HERO_VANGUARD_IDLE",
        "path": SHEET_PATH,
        "kind": "sprite_sheet",
        "status": "draft",
        "pixelWidth": 384,
        "pixelHeight": 512,
        "pixelsPerUnit": 20,
        "pivot": "bottom_center",
        "directions": list(vad.DIRECTIONS),
        "animations": [{"name": "idle", "framesPerDirection": 4, "fps": 6, "loop": True}],
        "previewPath": SHEET_PREVIEW,
    }
    asset.update(overrides)
    return asset


def manifest_doc(assets, **overrides):
    doc = {
        "assetPackId": "p1_hero_vanguard",
        "assetPackVersion": "v0.1.0",
        "owner": "Muse",
        "sourceLicense": "original",
        "assets": assets,
    }
    doc.update(overrides)
    return doc


class AssetRepositoryFixture(unittest.TestCase):
    """Provides a throwaway repository tree plus helpers to run the validator."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixture helpers -----------------------------------------------------
    def write(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        return path

    def write_files_for(self, *assets):
        for asset in assets:
            path = asset.get("path")
            if isinstance(path, str) and path.lower().endswith(".png"):
                self.write(path, make_png(asset["pixelWidth"], asset["pixelHeight"]))
            elif isinstance(path, str):
                self.write(path, b"placeholder")
            preview = asset.get("previewPath")
            if isinstance(preview, str):
                data = (make_gif(16, 16) if preview.lower().endswith(".gif")
                        else make_png(16, 16))
                self.write(preview, data)

    def validate(self, doc, *, changed=None, check_files=True):
        return vad.validate_manifest(doc, SCHEMA, self.root,
                                     check_files=check_files, changed=changed)

    def assert_clean(self, doc, **kwargs):
        errors, warnings = self.validate(doc, **kwargs)
        self.assertEqual([], errors, "\n".join(errors))
        self.assertEqual([], warnings, "\n".join(warnings))
        return warnings

    def assert_error(self, doc, needle, **kwargs):
        errors, _ = self.validate(doc, **kwargs)
        self.assertTrue(errors, "expected a failure but the validator reported none")
        joined = "\n".join(errors)
        self.assertIn(needle, joined, joined)
        return errors


class StructuralTests(AssetRepositoryFixture):
    """Requirement 1 and 6: schema conformance and precise findings."""

    def test_valid_minimal_manifest_passes(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        self.assert_clean(manifest_doc([asset]))

    def test_valid_eight_direction_sheet_passes(self):
        asset = sheet_asset()
        self.write_files_for(asset)
        self.assert_clean(manifest_doc([asset]))

    def test_multiple_assets_and_statuses_pass(self):
        first, second = sprite_asset(), sheet_asset(
            assetId="CHR_HERO_VANGUARD_RUN",
            path="Client/Assets/Art/Characters/hero_vanguard_run.png",
            previewPath="Client/Assets/Art/Previews/hero_vanguard_run_preview.png",
            animations=[{"name": "run", "framesPerDirection": 6, "fps": 12, "loop": True}],
            pixelWidth=576, pixelHeight=512, status="approved")
        self.write_files_for(first, second)
        self.assert_clean(manifest_doc([first, second]))

    def test_shipped_example_manifest_is_valid(self):
        example = vad.load_json(EXAMPLE_MANIFEST)
        errors, warnings = self.validate(example, check_files=False)
        self.assertEqual([], errors, "\n".join(errors))

    def test_schema_rejects_lower_case_asset_id(self):
        asset = sprite_asset(assetId="icon_hero_portait")
        errors, _ = self.validate(manifest_doc([asset]), check_files=False)
        self.assertTrue(any("assetId" in error for error in errors), errors)

    def test_schema_rejects_unknown_field(self):
        asset = sprite_asset(frameWidth=32)
        self.write_files_for(asset)
        self.assert_error(manifest_doc([asset]), "unexpected property 'frameWidth'", check_files=False)

    def test_schema_rejects_wrong_pixels_per_unit(self):
        asset = sprite_asset(pixelsPerUnit=16)
        self.write_files_for(asset)
        self.assert_error(manifest_doc([asset]), "pixelsPerUnit", check_files=False)

    def test_schema_rejects_bad_kind_and_missing_preview(self):
        asset = sprite_asset(previewPath=None)
        asset["kind"] = "spriteheet"
        errors, _ = self.validate(manifest_doc([asset]), check_files=False)
        self.assertTrue(any("kind" in error for error in errors), errors)

    def test_schema_rejects_unknown_top_level_field(self):
        self.assert_error(manifest_doc([sprite_asset()], notes="hello"),
                          "unexpected property 'notes'", check_files=False)

    def test_non_original_license_fails(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        self.assert_error(manifest_doc([asset], sourceLicense="reference_clone"), "sourceLicense")

    def test_missing_required_asset_field_is_reported(self):
        asset = sprite_asset()
        del asset["pixelHeight"]
        errors, _ = self.validate(manifest_doc([asset]), check_files=False)
        self.assertTrue(any("pixelHeight" in error for error in errors), errors)

    def test_error_line_names_asset_file_and_field(self):
        asset = sprite_asset(pixelWidth=64)
        self.write_files_for(sheet_asset())
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        errors, _ = self.validate(manifest_doc([asset]))
        line = errors[0]
        self.assertIn(asset["assetId"], line)
        self.assertIn(asset["path"], line)
        self.assertIn("field=pixelWidth", line)


class IdentityAndPathTests(AssetRepositoryFixture):
    """Requirement 2 and 4: uniqueness, containment and real files."""

    def test_duplicate_asset_id(self):
        first, second = sprite_asset(), sprite_asset(
            path="Client/Assets/Art/Icons/hero_portrait_b.png",
            previewPath="Client/Assets/Art/Previews/hero_portrait_b_preview.png")
        self.write_files_for(first, second)
        self.assert_error(manifest_doc([first, second]), "duplicate assetId")

    def test_duplicate_path(self):
        first, second = sprite_asset(), sprite_asset(assetId="ICON_HERO_PORTRAIT_B")
        self.write_files_for(first, second)
        self.assert_error(manifest_doc([first, second]), "duplicate path")

    def test_path_traversal_is_rejected(self):
        asset = sprite_asset(path="Client/Assets/../../Outside/hero.png")
        self.assert_error(manifest_doc([asset]), "must not contain")

    def test_parent_escape_in_preview_is_rejected(self):
        asset = sprite_asset(previewPath="Client/Assets/Art/../Secret/preview.png")
        self.write_files_for(asset)
        self.assert_error(manifest_doc([asset]), "previewPath")

    def test_absolute_and_backslash_paths_are_rejected(self):
        for bad in ("/etc/passwd", "C:\\Temp\\hero.png", "Client\\Assets\\Art\\hero.png"):
            with self.subTest(path=bad):
                errors, _ = self.validate(manifest_doc([sprite_asset(path=bad)]), check_files=False)
                self.assertTrue(errors, f"expected a failure for {bad}")

    def test_missing_asset_file(self):
        asset = sprite_asset()
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "declared file does not exist")

    def test_missing_preview_file(self):
        asset = sprite_asset()
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.assert_error(manifest_doc([asset]), "preview file does not exist")

    def test_path_outside_repo_root_is_rejected(self):
        asset = sprite_asset(path="Server/Assets/hero.png")
        self.assert_error(manifest_doc([asset]), "pattern")

    def test_path_outside_art_roots_is_rejected(self):
        asset = sprite_asset(path="Client/Assets/Textures/hero.png")
        self.assert_error(manifest_doc([asset]), "art roots")

    def test_ui_art_root_is_allowed(self):
        asset = sprite_asset(path="Client/Assets/UI/Art/hud_panel.png", pixelWidth=64, pixelHeight=32)
        self.write(asset["path"], make_png(64, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_clean(manifest_doc([asset]))

    def test_case_only_difference_is_rejected(self):
        first = sprite_asset()
        second = sprite_asset(assetId="ICON_HERO_PORTRAIT_B",
                              path="Client/Assets/Art/Icons/HERO_PORTRAIT.png",
                              previewPath="Client/Assets/Art/Previews/hero_b_preview.png")
        self.write_files_for(first, second)
        self.assert_error(manifest_doc([first, second]), "differs only by case")

    def test_non_image_kind_may_deliver_non_png(self):
        asset = sprite_asset(assetId="TILE_THANG_LONG_CHUNK", kind="tilemap",
                             path="Client/Assets/Tilemaps/thang_long_chunk.asset",
                             pixelWidth=16, pixelHeight=16, tileSize="16x16")
        self.write(asset["path"], b"%YAML% placeholder")
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_clean(manifest_doc([asset]))

    def test_sprite_kind_must_be_png(self):
        asset = sprite_asset(kind="sprite", path="Client/Assets/Art/Sprites/hero.jpg",
                             pixelWidth=32, pixelHeight=32)
        self.assert_error(manifest_doc([asset]), "must deliver a PNG file", check_files=False)

    def test_upper_case_file_name_is_a_warning_only(self):
        asset = sprite_asset(path="Client/Assets/Art/Icons/Hero_Portrait.png")
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        errors, warnings = self.validate(manifest_doc([asset]))
        self.assertEqual([], errors, "\n".join(errors))
        self.assertTrue(any("snake_case" in warning for warning in warnings), warnings)

    def test_replaces_asset_id_warning(self):
        asset = sprite_asset(replacesAssetId="CHR_OLD_HERO")
        self.write_files_for(asset)
        errors, warnings = self.validate(manifest_doc([asset]))
        self.assertEqual([], errors, "\n".join(errors))
        self.assertTrue(any("replacesAssetId" in warning for warning in warnings), warnings)


class PngTests(AssetRepositoryFixture):
    """Requirement 3: IHDR must agree with the manifest, LFS pointers must fail."""

    def test_pixel_width_mismatch(self):
        asset = sprite_asset(pixelWidth=64)
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "IHDR says 32px")

    def test_pixel_height_mismatch(self):
        asset = sprite_asset(pixelHeight=48)
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "pixelHeight")

    def test_lfs_pointer_is_rejected(self):
        asset = sprite_asset()
        self.write(asset["path"], LFS_POINTER)
        self.write(asset["previewPath"], LFS_POINTER)
        self.assert_error(manifest_doc([asset]), "Git LFS pointer")

    def test_truncated_png_is_rejected(self):
        asset = sprite_asset()
        self.write(asset["path"], b"\x89PNG\r\n\x1a\n\x00\x00")
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "unreadable PNG")

    def test_wrong_first_chunk_is_rejected(self):
        asset = sprite_asset()
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"bKGD", b"\x00\x00\x00")
        self.write(asset["path"], data)
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "expected IHDR")

    def test_jpeg_with_png_extension_is_rejected(self):
        asset = sprite_asset()
        self.write(asset["path"], b"\xff\xd8\xff\xe0" + b"\x00" * 40)
        self.write(asset["previewPath"], make_png(16, 16))
        self.assert_error(manifest_doc([asset]), "file is JPEG")

    def test_interlaced_sheet_warns(self):
        asset = sprite_asset()
        self.write(asset["path"], make_png(32, 32, interlace=1))
        self.write(asset["previewPath"], make_png(16, 16))
        errors, warnings = self.validate(manifest_doc([asset]))
        self.assertEqual([], errors, "\n".join(errors))
        self.assertTrue(any("interlaced" in warning.lower() for warning in warnings), warnings)

    def test_gif_preview_is_accepted(self):
        asset = sprite_asset(previewPath="Client/Assets/Art/Previews/hero_portrait.gif")
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_gif(16, 16))
        self.assert_clean(manifest_doc([asset]))

    def test_broken_gif_preview_fails(self):
        asset = sprite_asset(previewPath="Client/Assets/Art/Previews/hero_portrait.gif")
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], LFS_POINTER)
        self.assert_error(manifest_doc([asset]), "previewPath")

    def test_lfs_pointer_manifest_is_an_environment_error(self):
        path = self.write("manifest.json", LFS_POINTER)
        with self.assertRaises(vad.EnvironmentProblem):
            vad.load_json(path)


class DirectionTests(AssetRepositoryFixture):
    """Requirement 4: eight directions in the locked order."""

    def test_missing_directions_on_sheet(self):
        asset = sheet_asset()
        del asset["directions"]
        self.write(asset["previewPath"], make_png(16, 16))
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.assert_error(manifest_doc([asset]), "must list the eight directions")

    def test_seven_directions_reported(self):
        asset = sheet_asset(directions=list(vad.DIRECTIONS[:7]))
        self.write(asset["previewPath"], make_png(16, 16))
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.assert_error(manifest_doc([asset]), "missing ['NW']")

    def test_wrong_order_reported(self):
        asset = sheet_asset(directions=["S", "SE", "E", "NE", "N", "NW", "W", "SW"])
        self.write(asset["previewPath"], make_png(16, 16))
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.assert_error(manifest_doc([asset]), "direction order must be")

    def test_unknown_direction_value_reported(self):
        asset = sheet_asset(directions=["N", "NE", "E", "SE", "S", "SW", "W", "DOWN"])
        self.write(asset["previewPath"], make_png(16, 16))
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        # the delivery schema owns the direction enum, so the schema layer reports it
        self.assert_error(manifest_doc([asset]), "not in enum", check_files=False)

    def test_duplicate_direction_reported(self):
        asset = sheet_asset(directions=["N", "N", "NE", "E", "SE", "S", "SW", "W"])
        self.write(asset["previewPath"], make_png(16, 16))
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.assert_error(manifest_doc([asset]), "duplicate direction")

    def test_directions_optional_for_single_sprite(self):
        asset = sprite_asset(directions=["S"])
        self.write_files_for(asset)
        self.assert_clean(manifest_doc([asset]))

    def test_sheet_that_does_not_tile_warns_only(self):
        asset = sheet_asset(pixelWidth=390)
        self.write(asset["path"], make_png(390, 512))
        self.write(asset["previewPath"], make_png(16, 16))
        errors, warnings = self.validate(manifest_doc([asset]))
        self.assertEqual([], errors, "\n".join(errors))
        self.assertTrue(any("do not tile" in warning for warning in warnings), warnings)


class AnimationTests(AssetRepositoryFixture):
    """Requirement 5: name, frame count and fps, without forcing equal frame counts."""

    def sheet_with(self, animations):
        return sheet_asset(animations=animations)

    def prepare(self, asset):
        self.write(asset["path"], make_png(asset["pixelWidth"], asset["pixelHeight"]))
        self.write(asset["previewPath"], make_png(16, 16))
        return asset

    def test_different_frame_counts_are_allowed(self):
        asset = self.prepare(self.sheet_with([
            {"name": "idle", "framesPerDirection": 4, "fps": 6, "loop": True},
            {"name": "run", "framesPerDirection": 8, "fps": 12, "loop": True},
        ]))
        asset["pixelWidth"] = 768
        self.write(asset["path"], make_png(768, 512))
        errors, warnings = self.validate(manifest_doc([asset]))
        self.assertEqual([], errors, "\n".join(errors))

    def test_animation_without_name(self):
        asset = self.prepare(self.sheet_with([{"framesPerDirection": 4, "fps": 6}]))
        self.assert_error(manifest_doc([asset]), "non-empty name")

    def test_animation_without_frame_count(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "fps": 6}]))
        self.assert_error(manifest_doc([asset]), "needs a frame count")

    def test_animation_without_fps(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "framesPerDirection": 4}]))
        self.assert_error(manifest_doc([asset]), "needs an fps value")

    def test_zero_fps_rejected(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "framesPerDirection": 4, "fps": 0}]))
        self.assert_error(manifest_doc([asset]), "fps must be greater than 0")

    def test_absurd_fps_rejected(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "framesPerDirection": 4, "fps": 240}]))
        self.assert_error(manifest_doc([asset]), "at most 60")

    def test_zero_frames_rejected(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "framesPerDirection": 0, "fps": 6}]))
        self.assert_error(manifest_doc([asset]), "integer >= 1")

    def test_boolean_loop_rejected(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "framesPerDirection": 4, "fps": 6,
                                               "loop": "yes"}]))
        self.assert_error(manifest_doc([asset]), "loop must be a boolean")

    def test_frames_alias_is_accepted(self):
        asset = self.prepare(self.sheet_with([{"name": "idle", "frames": 4, "fps": 6}]))
        self.assert_clean(manifest_doc([asset]))


class ChangedFileTests(AssetRepositoryFixture):
    """Integration with a PR change set."""

    def test_changed_png_without_manifest_entry_fails(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        changed = [asset["path"], "Client/Assets/Art/Icons/unlisted_hero.png"]
        self.assert_error(manifest_doc([asset]), "not referenced by any manifest", changed=changed)

    def test_changed_png_covered_by_manifest_passes(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        errors, _ = self.validate(manifest_doc([asset]), changed=[asset["path"], asset["previewPath"]])
        self.assertEqual([], errors, "\n".join(errors))

    def test_changed_files_outside_art_are_ignored(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        self.assert_clean(manifest_doc([asset]),
                          changed=["Implementation/Tools/json_schema.py", "Server/Program.cs"])


class CommandLineTests(AssetRepositoryFixture):
    """Requirement 6: exit codes and report file."""

    def run_cli(self, *extra):
        command = [sys.executable, str(VALIDATOR), "--root", str(self.root),
                   "--schema", str(HANDOFF_DIR / "asset_delivery_manifest.schema.json")]
        command += [str(argument) for argument in extra]
        return subprocess.run(command, capture_output=True, text=True)

    def write_manifest(self, doc, rel="Client/Assets/ArtManifests/muse_delivery_manifest.json"):
        self.write(rel, json.dumps(doc))
        return rel

    def test_cli_passes_on_valid_delivery(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        result = self.run_cli("--manifest", self.write_manifest(manifest_doc([asset])))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_cli_fails_and_writes_report(self):
        asset = sprite_asset(pixelWidth=64)
        self.write(asset["path"], make_png(32, 32))
        self.write(asset["previewPath"], make_png(16, 16))
        report = self.root / "report.txt"
        result = self.run_cli("--manifest", self.write_manifest(manifest_doc([asset])),
                              "--report", str(report))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL: 1 problem(s)", result.stdout)
        self.assertIn("field=pixelWidth", report.read_text(encoding="utf-8"))

    def test_cli_environment_error_when_manifest_missing(self):
        result = self.run_cli()
        self.assertEqual(2, result.returncode)
        self.assertIn("asset manifest not found", result.stderr)

    def test_cli_allows_missing_manifest_before_first_delivery(self):
        result = self.run_cli("--allow-missing-manifest")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("no asset manifest", result.stdout.lower())

    def test_cli_requires_manifest_when_art_changed(self):
        changed = self.write("changed.txt", "Client/Assets/Art/Icons/hero.png\n")
        result = self.run_cli("--allow-missing-manifest", "--changed-files", changed)
        self.assertEqual(2, result.returncode)
        self.assertIn("art PNG file(s) changed", result.stderr)

    def test_cli_quiet_mode_hides_findings_on_success(self):
        asset = sprite_asset()
        self.write_files_for(asset)
        result = self.run_cli("--manifest", self.write_manifest(manifest_doc([asset])), "-q")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("WARN", result.stdout)

    def test_cli_validates_the_shipped_example_without_files(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--skip-file-checks",
             "--manifest", str(EXAMPLE_MANIFEST)],
            capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
