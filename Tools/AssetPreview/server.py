#!/usr/bin/env python3
"""OPC-08: Lightweight asset preview server (standard library only).

Serves static HTML/CSS/JS from Tools/AssetPreview/ and provides JSON endpoints
for loading sprite sheets with v2 manifest metadata. No external dependencies.

Usage:
    python Tools/AssetPreview/server.py [--host 127.0.0.1] [--port 8080] [--root <path>]

Features:
- Serves index.html, styles.css, app.js statically
- /api/sprites/<path> - Proxy sprite sheet images
- /api/layout/<asset_id> - Return calculated sprite grid based on v2 manifest geometry
- Path traversal protection (../ in paths rejected)
- Cross-Origin Resource Sharing (CORS) headers for localhost testing
- Uses only Python stdlib (http.server, urllib, json, pathlib)

Not self-merging. Refs #40, OPC-08.
"""

import http.server
import json
import os
import posixpath
import socketserver
import urllib.parse
import urllib.request
import zlib
from pathlib import Path


class AssetPreviewHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with API endpoints and path safety checks."""

    root_path = None  # Set via --root argument

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Route requests to static files or API endpoints."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API endpoints
        if path == "/":
            self.serve_static("index.html")
        elif path.startswith("/styles.css"):
            self.serve_static("styles.css")
        elif path.startswith("/app.js"):
            self.serve_static("app.js")
        elif path.startswith("/api/sprites/"):
            self.handle_sprite_request(path)
        elif path.startswith("/api/layout/"):
            self.handle_layout_request(path)
        else:
            self.send_error(404, "Not Found")

    def handle_sprite_request(self, path):
        """Serve image from local filesystem."""
        relative = path[len("/api/sprites/"):]

        if not self.is_safe_path(relative):
            self.send_json_error(403, "Path traversal not allowed")
            return

        if self.root_path:
            file_path = Path(self.root_path) / relative
            if file_path.exists() and file_path.is_file():
                self.serve_file(str(file_path))
                return

        abs_path = Path(relative)
        if abs_path.exists():
            self.serve_file(str(abs_path))
            return

        self.send_error(404, f"Sprite not found: {relative}")

    def handle_layout_request(self, path):
        """Return sprite grid layout from manifest metadata."""
        asset_id = path[len("/api/layout/"):]

        if not asset_id:
            self.send_json_error(400, "asset_id required")
            return

        if not self.root_path:
            self.send_json_error(500, "Root path not configured")
            return

        manifest_path = Path(self.root_path) / "Client/Assets/ArtManifests/muse_delivery_manifest.json"
        if not manifest_path.exists():
            self.send_json_error(404, "Manifest not found")
            return

        try:
            manifest = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            self.send_json_error(500, f"Cannot parse manifest: {e}")
            return

        # Find asset entry
        asset = None
        for entry in manifest.get("assets", []):
            if entry.get("id") == asset_id:
                asset = entry
                break

        if not asset:
            self.send_json_error(404, f"Asset not found: {asset_id}")
            return

        layout = self.calculate_layout(asset)
        self.send_json_response(layout)

    def calculate_layout(self, asset: dict) -> dict:
        """Calculate sprite grid layout from v2 manifest data."""
        frame_size = asset.get("frameSize", {"width": 48, "height": 64})
        is_directional = asset.get("isDirectional", False)
        frames_per_direction = asset.get("framesPerDirection", 6)
        animation_fps = asset.get("animationFps", 8)

        width = frame_size["width"]
        height = frame_size["height"]

        result = {
            "assetId": asset.get("id"),
            "frameSize": {"width": width, "height": height},
            "directional": is_directional,
            "totalSprites": 0,
            "grid": {
                "rows": 0,
                "cols": 0,
                "pixelWidth": 0,
                "pixelHeight": 0
            },
            "animations": [],
            "unsupported": False
        }

        if is_directional:
            directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            cols_per_dir = len(directions)

            result["grid"]["rows"] = frames_per_direction
            result["grid"]["cols"] = cols_per_dir
            result["grid"]["pixelWidth"] = cols_per_dir * width
            result["grid"]["pixelHeight"] = frames_per_direction * height
            result["totalSprites"] = frames_per_direction * cols_per_dir

            result["animations"] = [
                {"name": f"{d}_walk", "direction": d, "frames": frames_per_direction, "fps": animation_fps}
                for d in directions
            ]
        else:
            result["grid"]["rows"] = 1
            result["grid"]["cols"] = frames_per_direction
            result["grid"]["pixelWidth"] = frames_per_direction * width
            result["grid"]["pixelHeight"] = height
            result["totalSprites"] = frames_per_direction

            result["animations"].append({
                "name": f"{asset.get('category', 'effect')}_anim",
                "frames": frames_per_direction,
                "fps": animation_fps
            })

        return result

    def serve_static(self, filename: str):
        """Serve a static file from Tools/AssetPreview/."""
        script_dir = Path(__file__).parent.resolve()
        file_path = script_dir / filename

        if not file_path.exists():
            self.send_error(404, f"File not found: {filename}")
            return

        content_type = self.guess_content_type(filename)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def serve_file(self, file_path: str):
        """Serve an arbitrary file (sprite image)."""
        content_type = self.guess_content_type(file_path)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def send_json_response(self, data: dict, status: int = 200):
        """Send JSON response with CORS headers."""
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_json_error(self, code: int, message: str):
        """Send JSON error response."""
        self.send_json_response({"error": message}, code)

    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Check for path traversal attempts."""
        normalized = path.replace("\\", "/")

        if "../" in normalized:
            return False

        if normalized.startswith("/"):
            return False

        if len(normalized) >= 2 and normalized[1] == ":":
            return False

        return True

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

    @staticmethod
    def guess_content_type(filename: str) -> str:
        if filename.lower().endswith(".html"):
            return "text/html; charset=utf-8"
        if filename.lower().endswith(".css"):
            return "text/css; charset=utf-8"
        if filename.lower().endswith(".js"):
            return "application/javascript; charset=utf-8"
        if filename.lower().endswith(".png"):
            return "image/png"
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            return "image/jpeg"
        if filename.lower().endswith(".gif"):
            return "image/gif"
        if filename.lower().endswith(".json"):
            return "application/json; charset=utf-8"
        return "application/octet-stream"


def main():
    host = "127.0.0.1"
    port = 8080
    root = None

    import sys
    args = sys.argv[1:]

    i = 0
    while i < len(args):
        if args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == "--root" and i + 1 < len(args):
            root = args[i + 1]
            AssetPreviewHandler.root_path = root
            i += 2
        else:
            i += 1

    with socketserver.TCPServer((host, port), AssetPreviewHandler) as httpd:
        print("=" * 60)
        print("Asset Preview Server (OPC-08)")
        print("=" * 60)
        print(f"Listening on: http://{host}:{port}")
        print(f"Serving from: {os.getcwd()}")
        if root:
            print(f"Root path for assets: {root}")
        print(f"API endpoints:")
        print(f"  GET / → preview UI")
        print(f"  GET /api/sprites/<path> → serve sprite image")
        print(f"  GET /api/layout/<asset_id> → calculate grid layout from manifest")
        print("-" * 60)
        print("Press Ctrl+C to stop")
        print("=" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
