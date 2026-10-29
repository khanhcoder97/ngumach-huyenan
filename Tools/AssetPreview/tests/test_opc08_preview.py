#!/usr/bin/env python3
"""Tests for OPC-08 Asset Preview server."""

import unittest
from pathlib import Path
import sys

# Add Tools/AssetPreview to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ServerTests(unittest.TestCase):
    """Test path safety and layout calculation."""

    def test_path_traversal_blocked(self):
        """Verify ../ and absolute paths are rejected."""
        from server import AssetPreviewHandler
        
        # Valid relative path
        self.assertTrue(AssetPreviewHandler.is_safe_path("Client/Assets/test.png"))
        
        # Path traversal attempts - these MUST be blocked
        self.assertFalse(AssetPreviewHandler.is_safe_path("../secret/file.txt"))
        self.assertFalse(AssetPreviewHandler.is_safe_path("..\\Windows\\System32"))
        self.assertFalse(AssetPreviewHandler.is_safe_path("/etc/passwd"))

    def test_layout_calculation(self):
        """Test v2 manifest geometry rules."""
        from server import AssetPreviewHandler
        
        handler = AssetPreviewHandler.__new__(AssetPreviewHandler)
        
        # Directional actor (8×6)
        asset_dir = {
            "id": "ACTOR",
            "frameSize": {"width": 48, "height": 64},
            "isDirectional": True,
            "framesPerDirection": 6,
            "animationFps": 8
        }
        layout = handler.calculate_layout(asset_dir)
        
        self.assertEqual(8, layout["grid"]["cols"])
        self.assertEqual(6, layout["grid"]["rows"])
        self.assertEqual(384, layout["grid"]["pixelWidth"])   # 8*48
        self.assertEqual(384, layout["grid"]["pixelHeight"]) # 6*64
        self.assertEqual(48, layout["totalSprites"])

        # VFX strip (1×8)
        asset_strip = {
            "id": "VFX",
            "frameSize": {"width": 64, "height": 64},
            "isDirectional": False,
            "framesPerDirection": 8,
            "animationFps": 12
        }
        layout_strip = handler.calculate_layout(asset_strip)
        
        self.assertEqual(8, layout_strip["grid"]["cols"])
        self.assertEqual(1, layout_strip["grid"]["rows"])
        self.assertEqual(512, layout_strip["grid"]["pixelWidth"])
        self.assertEqual(64, layout_strip["grid"]["pixelHeight"])


class FixtureTests(unittest.TestCase):
    """Test fixture generation."""

    def test_png_generated(self):
        """Verify synthetic fixture was created."""
        png = Path("Tools/AssetPreview/fixtures/actor_8dir_test.png")
        
        if png.exists():
            data = png.read_bytes()
            
            # Check PNG signature
            self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
            print(f"✓ PNG valid: {png.stat().st_size} bytes")
        else:
            self.fail("Fixture not found. Run: python create_fixtures.py")

    def test_meta_generated(self):
        """Verify Unity .meta file created."""
        meta = Path("Tools/AssetPreview/fixtures/actor_8dir_test.png.meta")
        
        if meta.exists():
            content = meta.read_text(encoding='utf-8-sig')
            
            # Required fields
            self.assertIn("guid:", content)
            self.assertIn("filterMode:", content)
            self.assertIn("spritePixelsToUnits:", content)
            self.assertIn("spriteMode: 2", content)
            
            print(f"✓ Meta valid: {content.count('name:')} entries")
        else:
            self.fail(".meta file not found")


if __name__ == "__main__":
    unittest.main()
