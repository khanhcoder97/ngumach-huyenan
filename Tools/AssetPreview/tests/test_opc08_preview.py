#!/usr/bin/env python3
"""Tests for OPC-08 asset preview server and UI contract.

Run from the repository root:
    python -m unittest discover -s Tools/AssetPreview/tests -v
"""

from __future__ import annotations

import http.client
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIEW_DIR = HERE.parent
REPO_ROOT = PREVIEW_DIR.parents[1]
FIXTURES = PREVIEW_DIR / "fixtures"
REAL_MANIFEST = REPO_ROOT / "Client/Assets/ArtManifests/muse_delivery_manifest.json"
if str(PREVIEW_DIR) not in sys.path:
    sys.path.insert(0, str(PREVIEW_DIR))

import server  # noqa: E402

DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"


def real_asset():
    manifest = json.loads(REAL_MANIFEST.read_text(encoding="utf-8"))
    return manifest, manifest["assets"][0]


class LayoutTests(unittest.TestCase):
    def test_real_v1_muse_manifest_is_6_columns_by_8_rows(self):
        _manifest, asset = real_asset()
        layout = server.calculate_layout(asset, 1)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual(6, layout["grid"]["cols"])
        self.assertEqual(8, layout["grid"]["rows"])
        self.assertEqual({"width": 48, "height": 64}, layout["frameSize"])
        self.assertEqual(288, layout["grid"]["pixelWidth"])
        self.assertEqual(512, layout["grid"]["pixelHeight"])
        self.assertEqual(48, layout["totalSprites"])
        self.assertTrue(layout["directional"])
        self.assertEqual(0, layout["directionRows"]["N"])
        self.assertEqual(7, layout["directionRows"]["NW"])
        self.assertEqual("walk", layout["animations"][0]["name"])
        self.assertEqual(6, layout["animations"][0]["frames"])
        self.assertEqual(0, layout["animations"][0]["columnStart"])

    def test_v2_multi_animation_column_ranges(self):
        asset = {
            "assetId": "CHR_MINH_KIEM_WALK",
            "path": "Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png",
            "kind": "sprite_sheet",
            "pixelWidth": 288,
            "pixelHeight": 512,
            "isDirectional": True,
            "layout": "direction_rows",
            "frameSize": {"width": 48, "height": 64},
            "directions": DIRECTIONS,
            "animations": [
                {"name": "walk", "framesPerDirection": 3, "fps": 8, "columnStart": 0},
                {"name": "run", "framesPerDirection": 3, "fps": 12, "columnStart": 3},
            ],
        }
        layout = server.calculate_layout(asset, 2)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual(6, layout["grid"]["cols"])
        self.assertEqual(8, layout["grid"]["rows"])
        self.assertEqual([0, 3], [a["columnStart"] for a in layout["animations"]])
        self.assertEqual([2, 5], [a["columnEnd"] for a in layout["animations"]])

    def test_v2_missing_frame_size_is_unsupported_not_guessed(self):
        asset = {
            "assetId": "MISSING_FRAME",
            "path": "art/missing.png",
            "kind": "sprite_sheet",
            "pixelWidth": 288,
            "pixelHeight": 512,
            "isDirectional": True,
            "layout": "direction_rows",
            "directions": DIRECTIONS,
            "animations": [{"name": "walk", "framesPerDirection": 6, "fps": 8}],
        }
        layout = server.calculate_layout(asset, 2)
        self.assertFalse(layout["supported"])
        self.assertIsNone(layout["grid"])
        self.assertEqual([], layout["animations"])
        self.assertTrue(any("missing frameSize" in reason for reason in layout["unsupportedReasons"]))

    def test_inconsistent_frame_grid_is_unsupported(self):
        asset = {
            "assetId": "BAD_GRID",
            "path": "art/bad.png",
            "kind": "sprite_sheet",
            "pixelWidth": 288,
            "pixelHeight": 512,
            "isDirectional": True,
            "layout": "direction_rows",
            "frameSize": {"width": 40, "height": 64},
            "directions": DIRECTIONS,
            "animations": [{"name": "walk", "framesPerDirection": 6, "fps": 8}],
        }
        layout = server.calculate_layout(asset, 2)
        self.assertFalse(layout["supported"])
        self.assertTrue(any("not divisible" in reason for reason in layout["unsupportedReasons"]))

    def test_wrong_direction_order_is_unsupported(self):
        asset = {
            "assetId": "BAD_ORDER",
            "path": "art/bad.png",
            "kind": "sprite_sheet",
            "pixelWidth": 288,
            "pixelHeight": 512,
            "isDirectional": True,
            "layout": "direction_rows",
            "frameSize": {"width": 48, "height": 64},
            "directions": ["N", "E", "NE", "SE", "S", "SW", "W", "NW"],
            "animations": [{"name": "walk", "framesPerDirection": 6, "fps": 8}],
        }
        layout = server.calculate_layout(asset, 2)
        self.assertFalse(layout["supported"])
        self.assertTrue(any("canonical order" in reason for reason in layout["unsupportedReasons"]))

    def test_strip_layout_has_one_row(self):
        asset = {
            "assetId": "VFX_STRIP",
            "path": "art/vfx.png",
            "kind": "vfx_sheet",
            "pixelWidth": 96,
            "pixelHeight": 64,
            "isDirectional": False,
            "layout": "strip",
            "frameSize": {"width": 24, "height": 64},
            "animations": [{"name": "slash", "frames": 4, "fps": 12}],
        }
        layout = server.calculate_layout(asset, 2)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual(4, layout["grid"]["cols"])
        self.assertEqual(1, layout["grid"]["rows"])
        self.assertFalse(layout["directional"])

    def test_static_icon_is_single_frame(self):
        asset = {
            "assetId": "ICON",
            "path": "art/icon.png",
            "kind": "icon",
            "pixelWidth": 32,
            "pixelHeight": 32,
        }
        layout = server.calculate_layout(asset, 2)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual(1, layout["grid"]["cols"])
        self.assertEqual(1, layout["grid"]["rows"])
        self.assertEqual([], layout["animations"])

    def test_resolve_under_root_rejects_escapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "inside.png").write_bytes(b"x")
            self.assertEqual(
                (root / "inside.png").resolve(),
                server.resolve_under_root(root, "inside.png"),
            )
            for value in ("../outside.png", "..\\outside.png", "C:/Windows/win.ini", "\\\\server\\share\\x.png", "/etc/passwd"):
                with self.assertRaises(ValueError, msg=value):
                    server.resolve_under_root(root, value)


class FixtureTests(unittest.TestCase):
    def test_fixture_png_is_288x512(self):
        png = FIXTURES / "actor_8dir_test.png"
        data = png.read_bytes()
        self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
        width, height = struct.unpack_from(">II", data, 16)
        self.assertEqual((288, 512), (width, height))

    def test_fixture_meta_has_48_sprites(self):
        meta = FIXTURES / "actor_8dir_test.png.meta"
        text = meta.read_text(encoding="utf-8")
        self.assertIn("spriteMode: 2", text)
        self.assertIn("filterMode: 0", text)
        self.assertIn("spritePixelsToUnits: 20", text)
        self.assertEqual(48, text.count("      name: "))
        self.assertIn("name: actor_8dir_test_N_0", text)
        self.assertIn("y: 448", text)

    def test_fixture_manifest_geometry_is_canonical(self):
        manifest = json.loads((FIXTURES / "preview_manifest.json").read_text(encoding="utf-8"))
        asset = manifest["assets"][0]
        # The synthetic manifest intentionally declares v1 so the server derives
        # 48x64 from 288/6 and 512/8.
        layout = server.calculate_layout(asset, 1)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual((6, 8), (layout["grid"]["cols"], layout["grid"]["rows"]))

    def test_app_js_has_single_direction_panel_and_real_playback(self):
        source = (PREVIEW_DIR / "app.js").read_text(encoding="utf-8")
        self.assertEqual(1, source.count("function showDirectionsPanel"))
        self.assertIn("animation.columnStart", source)
        self.assertIn("currentRow()", source)
        self.assertIn("directionRows", source)
        self.assertNotIn("colsPerDir = 8", source)

    def test_app_js_wires_query_parameters_and_clears_stale_layout(self):
        source = (PREVIEW_DIR / "app.js").read_text(encoding="utf-8")
        self.assertIn("new URLSearchParams", source)
        self.assertIn("params.get('assetId')", source)
        self.assertIn("params.get('path')", source)
        self.assertIn("params.get('direction')", source)
        self.assertIn("params.get('play')", source)
        self.assertIn("keepLayout", source)
        self.assertIn("clearLayout()", source)
        self.assertIn("updateDatasets()", source)
        self.assertIn("dataset.layoutSupported", source)
        self.assertIn("dataset.layoutCols", source)
        self.assertIn("dataset.layoutRows", source)

    def test_index_sets_fixed_canvas_viewport(self):
        html = (PREVIEW_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="spriteCanvas" width="720" height="560"', html)
        self.assertEqual(1, html.count('id="directionsPanel"'))
        self.assertNotIn('class="directions" id="directionsPanel" class="hidden"', html)

    def test_app_js_syntax_when_node_is_available(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        result = subprocess.run(
            [node, "--check", str(PREVIEW_DIR / "app.js")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)


class HttpFixture:
    def __init__(self, root: Path, manifest_rel: str = DEFAULT_MANIFEST):
        self.root = root
        self.manifest_rel = manifest_rel
        self.server = server.create_server("127.0.0.1", 0, root, manifest_rel)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def request(self, path: str):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            body = response.read()
            headers = {key.lower(): value for key, value in response.getheaders()}
            return response.status, headers, body
        finally:
            connection.close()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class HttpServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "art/nested").mkdir(parents=True)
        shutil.copyfile(FIXTURES / "actor_8dir_test.png", self.root / "art/nested/pixel.png")
        (self.root / "art/secret.txt").write_text("not an image", encoding="utf-8")
        self.outside_marker = self.root.parent / "outside-preview-marker.png"
        self.outside_marker.write_bytes(b"OUTSIDE-MARKER")
        self.manifest = {
            "assetPackId": "preview_test",
            "assetPackVersion": "v0.1.0",
            "owner": "Muse",
            "sourceLicense": "original",
            "assets": [
                {
                    "assetId": "TEST_ACTOR",
                    "path": "art/nested/pixel.png",
                    "kind": "sprite_sheet",
                    "status": "draft",
                    "pixelWidth": 288,
                    "pixelHeight": 512,
                    "pixelsPerUnit": 20,
                    "directions": DIRECTIONS,
                    "animations": [
                        {"name": "walk", "framesPerDirection": 6, "fps": 8, "loop": True}
                    ],
                },
                {
                    "id": "LEGACY_ACTOR",
                    "path": "art/nested/pixel.png",
                    "kind": "sprite_sheet",
                    "pixelWidth": 288,
                    "pixelHeight": 512,
                    "directions": DIRECTIONS,
                    "animations": [
                        {"name": "walk", "framesPerDirection": 6, "fps": 8}
                    ],
                },
            ],
        }
        manifest_path = self.root / DEFAULT_MANIFEST
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.http = HttpFixture(self.root)

    def tearDown(self):
        self.http.close()
        self.tmp.cleanup()
        try:
            self.outside_marker.unlink()
        except OSError:
            pass

    def test_encoded_nested_path_is_served(self):
        status, headers, body = self.http.request("/api/sprites/art%2Fnested%2Fpixel.png")
        self.assertEqual(200, status)
        self.assertEqual("image/png", headers.get("content-type"))
        self.assertEqual((FIXTURES / "actor_8dir_test.png").read_bytes(), body)

    def test_literal_nested_path_is_served(self):
        status, _headers, body = self.http.request("/api/sprites/art/nested/pixel.png")
        self.assertEqual(200, status)
        self.assertEqual((FIXTURES / "actor_8dir_test.png").read_bytes(), body)

    def test_encoded_traversal_is_blocked(self):
        status, _headers, body = self.http.request("/api/sprites/%2e%2e%2Foutside-preview-marker.png")
        self.assertEqual(403, status)
        self.assertNotIn(b"OUTSIDE-MARKER", body)

    def test_encoded_backslash_traversal_is_blocked(self):
        status, _headers, body = self.http.request("/api/sprites/..%5Coutside-preview-marker.png")
        self.assertEqual(403, status)
        self.assertNotIn(b"OUTSIDE-MARKER", body)

    def test_double_encoded_traversal_is_not_served(self):
        status, _headers, body = self.http.request("/api/sprites/%252e%252e%252Foutside-preview-marker.png")
        self.assertIn(status, (403, 404))
        self.assertNotIn(b"OUTSIDE-MARKER", body)

    def test_cwd_fallback_is_removed(self):
        status, _headers, body = self.http.request("/api/sprites/Tools/AssetPreview/server.py")
        self.assertEqual(404, status)
        self.assertNotIn(b"#!/usr/bin/env python3", body)

    def test_absolute_path_is_blocked(self):
        status, _headers, body = self.http.request("/api/sprites/%2Fetc%2Fpasswd")
        self.assertEqual(403, status)
        self.assertNotIn(b"root:", body)

    def test_non_image_extension_is_blocked(self):
        status, _headers, body = self.http.request("/api/sprites/art/secret.txt")
        self.assertEqual(403, status)
        self.assertNotIn(b"not an image", body)

    def test_no_wildcard_cors_header(self):
        _status, headers, _body = self.http.request("/api/sprites/art/nested/pixel.png")
        self.assertNotIn("access-control-allow-origin", headers)

    def test_layout_lookup_uses_canonical_asset_id(self):
        status, headers, body = self.http.request("/api/layout/TEST_ACTOR")
        self.assertEqual(200, status)
        self.assertIn("application/json", headers.get("content-type"))
        layout = json.loads(body)
        self.assertTrue(layout["supported"], layout["unsupportedReasons"])
        self.assertEqual(6, layout["grid"]["cols"])
        self.assertEqual(8, layout["grid"]["rows"])
        self.assertEqual({"width": 48, "height": 64}, layout["frameSize"])

    def test_layout_lookup_legacy_id_is_warned(self):
        status, _headers, body = self.http.request("/api/layout/LEGACY_ACTOR")
        self.assertEqual(200, status)
        layout = json.loads(body)
        self.assertTrue(any("legacy 'id'" in warning for warning in layout["warnings"]))

    def test_layout_unknown_asset_is_404(self):
        status, _headers, body = self.http.request("/api/layout/NOT_IN_MANIFEST")
        self.assertEqual(404, status)
        self.assertIn("not found", json.loads(body)["error"])

    def test_static_index_and_script(self):
        status, headers, body = self.http.request("/")
        self.assertEqual(200, status)
        self.assertIn("text/html", headers.get("content-type"))
        self.assertIn(b"OPC-08", body)
        status, _headers, body = self.http.request("/app.js")
        self.assertEqual(200, status)
        self.assertEqual(1, body.count(b"function showDirectionsPanel"))

    def test_symlink_escape_is_blocked(self):
        link = self.root / "art/link.png"
        target = self.root.parent / "outside-preview-marker.png"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is not permitted on this platform")
        status, _headers, body = self.http.request("/api/sprites/art/link.png")
        self.assertEqual(403, status)
        self.assertNotIn(b"OUTSIDE-MARKER", body)


if __name__ == "__main__":
    unittest.main()
