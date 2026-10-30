#!/usr/bin/env python3
"""OPC-08: lightweight, read-only asset preview server (standard library only).

The server has one explicit contract:

* the browser percent-encodes the **whole** asset path once;
* the server percent-decodes it once, then confines the decoded path to
  ``--root`` and serves only recognised image types.

There is no CWD fallback and no wildcard CORS header. Unknown paths, absolute
paths, drive/UNC paths, ``..`` components and symlink/reparse escapes are
rejected before any file is read.

Endpoints:

    GET /                         preview UI
    GET /styles.css               preview styles
    GET /app.js                   preview script
    GET /api/sprites/<path>       image bytes (single URL decode)
    GET /api/layout/<assetId>     layout JSON from the delivery manifest

Layouts support both the legacy v1 manifest (derive frame size from pixel size,
direction count and ``framesPerDirection``) and v2 ``frameSize``/``layout``
metadata. A missing or inconsistent field yields ``supported: false`` with
explicit reasons; the server never invents an 8x6/6x8 grid.

Usage:
    python Tools/AssetPreview/server.py --root . [--host 127.0.0.1] [--port 8080]
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
DEFAULT_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
SHEET_KINDS = frozenset({"sprite_sheet", "vfx_sheet", "animation"})
STATIC_KINDS = frozenset({"sprite", "icon", "ui_texture", "tileset", "tilemap"})
IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
MAX_FILE_BYTES = 64 * 1024 * 1024
VIEWPORT_WIDTH = 720
VIEWPORT_HEIGHT = 560


def positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def non_negative_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def frame_count(animation: dict):
    for key in ("framesPerDirection", "frames", "frameCount"):
        value = animation.get(key)
        if positive_int(value):
            return value
    return None


def _unsupported(reason: str) -> dict:
    return {
        "assetId": None,
        "manifestVersion": None,
        "supported": False,
        "unsupportedReasons": [reason],
        "warnings": [],
        "layout": None,
        "directional": False,
        "frameSize": None,
        "directions": [],
        "directionRows": {},
        "grid": None,
        "animations": [],
        "totalSprites": 0,
        "image": None,
    }


def calculate_layout(asset: dict, manifest_version: Optional[int] = None) -> dict:
    """Return a truthful layout description for one manifest asset.

    ``manifest_version`` should be the manifest's top-level value (1 when
    absent). Unsupported metadata never produces guessed frame rectangles.
    """
    if not isinstance(asset, dict):
        return _unsupported("asset entry is not an object")

    reasons: List[str] = []
    warnings: List[str] = []
    asset_id = asset.get("assetId") or asset.get("id")
    if not isinstance(asset_id, str) or not asset_id:
        asset_id = None
        warnings.append("asset has no assetId")

    path = asset.get("path")
    kind = asset.get("kind")
    pixel_width = asset.get("pixelWidth")
    pixel_height = asset.get("pixelHeight")
    image_known = positive_int(pixel_width) and positive_int(pixel_height)
    if not image_known:
        reasons.append("pixelWidth and pixelHeight must be positive integers")

    if manifest_version is None:
        manifest_version = 2 if (
            asset.get("frameSize") is not None or asset.get("layout") is not None
        ) else 1

    animations_raw = asset.get("animations")
    if animations_raw is None:
        animations_raw = []
    if not isinstance(animations_raw, list):
        reasons.append("animations must be an array")
        animations_raw = []

    is_directional = asset.get("isDirectional")
    directions = asset.get("directions")
    if is_directional is None:
        is_directional = isinstance(directions, list) and len(directions) > 1

    direction_list: List[str] = []
    direction_rows: Dict[str, int] = {}
    if is_directional:
        if not isinstance(directions, list) or not directions:
            reasons.append(
                "isDirectional=true requires an explicit directions array; "
                "rows cannot be assigned safely"
            )
        else:
            direction_list = [str(item) for item in directions]
            if tuple(direction_list) != DIRECTIONS:
                reasons.append(
                    "directions must be the canonical order "
                    f"{list(DIRECTIONS)}; got {direction_list}"
                )
            else:
                direction_rows = {direction: index for index, direction in enumerate(direction_list)}
    else:
        direction_list = []
        direction_rows = {}

    layout_name = asset.get("layout")
    if layout_name is None:
        layout_name = "direction_rows" if is_directional else "strip"
    if layout_name not in ("direction_rows", "strip"):
        reasons.append(f"unsupported layout {layout_name!r}")
    elif layout_name == "direction_rows" and not is_directional:
        reasons.append("layout=direction_rows but isDirectional is false")
    elif layout_name == "strip" and is_directional:
        reasons.append("layout=strip but isDirectional is true")

    declared_frame = asset.get("frameSize")
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None
    if declared_frame is not None:
        if not isinstance(declared_frame, dict):
            reasons.append("frameSize must be an object with width/height")
        else:
            frame_width = declared_frame.get("width")
            frame_height = declared_frame.get("height")
            if not positive_int(frame_width) or not positive_int(frame_height):
                reasons.append("frameSize.width and frameSize.height must be positive integers")
                frame_width = frame_height = None
    elif manifest_version == 2 and kind in SHEET_KINDS:
        reasons.append(
            "manifestVersion 2 sheet is missing frameSize; "
            "the preview will not derive a grid from undocumented fields"
        )

    direction_count: Optional[int] = None
    if is_directional:
        direction_count = len(direction_list) if direction_list else None
    else:
        direction_count = 1

    if frame_width is None and image_known and kind in SHEET_KINDS:
        first_frames = frame_count(animations_raw[0]) if animations_raw and isinstance(animations_raw[0], dict) else None
        if first_frames and pixel_width % first_frames == 0:
            frame_width = pixel_width // first_frames
            warnings.append(
                "legacy v1 layout: frame width derived from pixelWidth/framesPerDirection"
            )
        elif first_frames:
            reasons.append(
                f"pixelWidth={pixel_width} is not divisible by frame count {first_frames}"
            )
    if frame_height is None and image_known and direction_count:
        if pixel_height % direction_count == 0:
            frame_height = pixel_height // direction_count
            if manifest_version == 1:
                warnings.append(
                    "legacy v1 layout: frame height derived from pixelHeight/directionCount"
                )
        else:
            reasons.append(
                f"pixelHeight={pixel_height} is not divisible by "
                f"direction count {direction_count}"
            )

    columns: Optional[int] = None
    rows: Optional[int] = None
    if frame_width is not None and frame_height is not None and image_known:
        if pixel_width % frame_width:
            reasons.append(
                f"pixelWidth={pixel_width} is not divisible by frame width {frame_width}"
            )
        if pixel_height % frame_height:
            reasons.append(
                f"pixelHeight={pixel_height} is not divisible by frame height {frame_height}"
            )
        if pixel_width % frame_width == 0 and pixel_height % frame_height == 0:
            columns = pixel_width // frame_width
            rows = pixel_height // frame_height
            if is_directional and direction_count is not None and rows != direction_count:
                reasons.append(
                    f"frame grid has {rows} rows but {direction_count} directions "
                    "are declared"
                )
            if not is_directional and rows != 1:
                reasons.append(
                    f"strip layout has {rows} frame rows; expected exactly 1"
                )

    animations: List[dict] = []
    for index, animation in enumerate(animations_raw):
        if not isinstance(animation, dict):
            reasons.append(f"animations[{index}] is not an object")
            continue
        name = animation.get("name")
        if not isinstance(name, str) or not name.strip():
            reasons.append(f"animations[{index}] has no name")
            name = f"animation[{index}]"
        frames = frame_count(animation)
        column_start = animation.get("columnStart", 0)
        if not non_negative_int(column_start):
            reasons.append(f"animation {name!r} columnStart must be a non-negative integer")
            column_start = 0
        if frames is None:
            reasons.append(
                f"animation {name!r} has no framesPerDirection/frames/frameCount"
            )
            continue
        fps = animation.get("fps")
        if not isinstance(fps, (int, float)) or isinstance(fps, bool) or fps <= 0 or fps > 60:
            reasons.append(f"animation {name!r} has invalid fps={fps!r}")
        if columns is not None and column_start + frames > columns:
            reasons.append(
                f"animation {name!r} covers columns {column_start}.."
                f"{column_start + frames - 1} but the sheet has {columns} columns"
            )
        animations.append(
            {
                "name": name,
                "frames": frames,
                "fps": fps if isinstance(fps, (int, float)) and not isinstance(fps, bool) else None,
                "loop": bool(animation.get("loop", False)),
                "columnStart": column_start,
                "columnEnd": column_start + frames - 1,
            }
        )

    if kind in SHEET_KINDS and not animations and not reasons:
        reasons.append("sheet has no usable animation entries")
    if kind in STATIC_KINDS and not animations and frame_width is None and image_known:
        frame_width, frame_height = pixel_width, pixel_height
        columns, rows = 1, 1
        warnings.append("static asset: treated as a single frame")

    supported = not reasons
    result = {
        "assetId": asset_id,
        "manifestVersion": manifest_version,
        "supported": supported,
        "unsupportedReasons": reasons,
        "warnings": warnings,
        "path": path if isinstance(path, str) else None,
        "kind": kind if isinstance(kind, str) else None,
        "layout": layout_name,
        "directional": bool(is_directional),
        "frameSize": (
            {"width": frame_width, "height": frame_height}
            if frame_width is not None and frame_height is not None
            else None
        ),
        "directions": direction_list,
        "directionRows": direction_rows,
        "grid": (
            {
                "cols": columns,
                "rows": rows,
                "pixelWidth": pixel_width,
                "pixelHeight": pixel_height,
            }
            if supported and columns is not None and rows is not None
            else None
        ),
        "animations": animations if supported else [],
        "totalSprites": columns * rows if supported and columns and rows else 0,
        "image": (
            {"width": pixel_width, "height": pixel_height}
            if image_known
            else None
        ),
    }
    if not supported:
        result["animations"] = []
    return result


def _decode_component(value: str) -> str:
    """Decode exactly one URL layer and reject NUL bytes."""
    decoded = urllib.parse.unquote(value)
    if "\x00" in decoded:
        raise ValueError("NUL bytes are not allowed")
    return decoded


def resolve_under_root(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a non-empty relative path")
    candidate = Path(value.replace("\\", "/"))
    if candidate.is_absolute() or candidate.drive or candidate.root:
        raise ValueError("absolute, drive and UNC paths are not allowed")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes the configured root") from exc
    return resolved


class AssetPreviewHandler(http.server.BaseHTTPRequestHandler):
    """Configured handler class; ``create_server`` supplies root/manifest."""

    root_path = Path(".").resolve()
    manifest_rel = DEFAULT_MANIFEST
    server_version = "AssetPreview/2.0"

    def do_GET(self):  # noqa: N802 - stdlib handler API
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path
        if route in ("/", "/index.html"):
            self._serve_static("index.html")
        elif route == "/styles.css":
            self._serve_static("styles.css")
        elif route == "/app.js":
            self._serve_static("app.js")
        elif route == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif route.startswith("/api/sprites/"):
            self._handle_sprite(route[len("/api/sprites/"):])
        elif route == "/api/sprites":
            self._send_json_error(400, "sprite path is required")
        elif route.startswith("/api/layout/"):
            self._handle_layout(route[len("/api/layout/"):])
        elif route == "/api/layout":
            self._send_json_error(400, "assetId is required")
        else:
            self._send_json_error(404, "not found")

    def _serve_static(self, name: str) -> None:
        file_path = Path(__file__).resolve().parent / name
        if not file_path.is_file():
            self._send_json_error(404, f"static file not found: {name}")
            return
        try:
            data = file_path.read_bytes()
        except OSError as exc:
            self._send_json_error(500, f"cannot read static file: {exc}")
            return
        self._send_bytes(200, data, self._content_type(name))

    def _handle_sprite(self, encoded: str) -> None:
        try:
            relative = _decode_component(encoded)
        except ValueError as exc:
            self._send_json_error(400, str(exc))
            return
        if not relative:
            self._send_json_error(400, "sprite path is required")
            return
        try:
            file_path = resolve_under_root(self.root_path, relative)
        except ValueError as exc:
            self._send_json_error(403, str(exc))
            return
        if not file_path.is_file():
            self._send_json_error(404, "sprite not found under the configured root")
            return
        suffix = file_path.suffix.lower()
        if suffix not in IMAGE_TYPES:
            self._send_json_error(403, f"unsupported sprite type {suffix or '<none>'}")
            return
        try:
            size = file_path.stat().st_size
            if size > MAX_FILE_BYTES:
                self._send_json_error(413, "sprite exceeds the 64 MB preview limit")
                return
            data = file_path.read_bytes()
        except OSError as exc:
            self._send_json_error(500, f"cannot read sprite: {exc}")
            return
        self._send_bytes(200, data, IMAGE_TYPES[suffix])

    def _load_manifest(self) -> Tuple[Optional[dict], Optional[str]]:
        try:
            manifest_path = resolve_under_root(self.root_path, self.manifest_rel)
        except ValueError as exc:
            return None, str(exc)
        if not manifest_path.is_file():
            return None, f"manifest not found under root: {self.manifest_rel}"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, f"cannot read/parse manifest: {exc}"
        if not isinstance(manifest, dict):
            return None, "manifest root must be an object"
        return manifest, None

    def _find_asset(self, manifest: dict, asset_id: str):
        canonical = None
        legacy = None
        for entry in manifest.get("assets", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("assetId") == asset_id:
                canonical = entry
                break
            if entry.get("id") == asset_id and legacy is None:
                legacy = entry
        return canonical, legacy

    def _handle_layout(self, encoded: str) -> None:
        try:
            asset_id = _decode_component(encoded).strip()
        except ValueError as exc:
            self._send_json_error(400, str(exc))
            return
        if not asset_id or "/" in asset_id or "\\" in asset_id:
            self._send_json_error(400, "invalid assetId")
            return
        manifest, error = self._load_manifest()
        if error:
            self._send_json_error(404, error)
            return
        canonical, legacy = self._find_asset(manifest, asset_id)
        asset = canonical or legacy
        if asset is None:
            self._send_json_error(404, f"assetId not found in manifest: {asset_id}")
            return
        manifest_version = manifest.get("manifestVersion", 1)
        if manifest_version not in (1, 2):
            manifest_version = 1
        layout = calculate_layout(asset, manifest_version)
        if legacy is not None and canonical is None:
            layout["warnings"].append(
                "asset matched the legacy 'id' field; add assetId to the manifest"
            )
        layout["manifestPath"] = self.manifest_rel
        self._send_json(200, layout)

    def _send_bytes(self, status: int, data: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def _send_json_error(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    @staticmethod
    def _content_type(name: str) -> str:
        suffix = Path(name).suffix.lower()
        return {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }.get(suffix, "application/octet-stream")

    def log_message(self, format, *args):  # noqa: A002 - stdlib API
        if os.environ.get("ASSET_PREVIEW_VERBOSE") == "1":
            super().log_message(format, *args)


def create_server(
    host: str,
    port: int,
    root: Path,
    manifest_rel: str = DEFAULT_MANIFEST,
) -> http.server.ThreadingHTTPServer:
    root = Path(root).expanduser().resolve()
    try:
        manifest_path = resolve_under_root(root, manifest_rel)
    except ValueError as exc:
        raise ValueError(f"invalid manifest path: {exc}") from exc
    handler = type(
        "ConfiguredAssetPreviewHandler",
        (AssetPreviewHandler,),
        {
            "root_path": root,
            "manifest_rel": manifest_path.relative_to(root).as_posix(),
        },
    )
    server = http.server.ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    return server


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Local-only sprite sheet preview server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--root", default=".", help="asset root; all paths are confined here")
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="delivery manifest relative to --root",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: --root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        server = create_server(args.host, args.port, root, args.manifest)
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot start preview server: {exc}", file=sys.stderr)
        return 2

    print("=" * 60)
    print("Asset Preview Server (OPC-08)")
    print("=" * 60)
    print(f"Listening on: http://{args.host}:{server.server_address[1]}")
    print(f"Asset root:   {root}")
    print(f"Manifest:     {args.manifest} (relative to root)")
    print("Endpoints:")
    print("  GET /                        preview UI")
    print("  GET /api/sprites/<path>      image bytes (one URL decode)")
    print("  GET /api/layout/<assetId>    truthful layout JSON")
    print("-" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
