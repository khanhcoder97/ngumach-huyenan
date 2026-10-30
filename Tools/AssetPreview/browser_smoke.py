#!/usr/bin/env python3
"""OPC-08: real headless-browser smoke check for the preview UI.

Starts the preview server, loads the page in headless Chrome/Edge with
``?assetId=...&direction=SE&play=1``, waits for the layout fetch, then verifies
the DOM data attributes and writes a screenshot as evidence.

This is intentionally separate from the unit tests because it needs a browser
binary. Run from the repository root::

    python Tools/AssetPreview/browser_smoke.py
    python Tools/AssetPreview/browser_smoke.py --browser "C:/.../chrome.exe"

Exit codes: 0 pass, 1 assertion/evidence failure, 2 environment error.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import server  # noqa: E402

DEFAULT_MANIFEST = "Tools/AssetPreview/fixtures/preview_manifest.json"
DEFAULT_ASSET = "FIX_ACTOR_8DIR_TEST"
DEFAULT_PATH = "Tools/AssetPreview/fixtures/actor_8dir_test.png"


def find_browser(explicit: str | None) -> str | None:
    if explicit:
        return explicit if Path(explicit).is_file() else None
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def data_attribute(dom: str, name: str) -> str | None:
    match = re.search(rf'data-{re.escape(name)}="([^"]*)"', dom)
    return match.group(1) if match else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Headless browser smoke check for OPC-08.")
    parser.add_argument("--browser", default=None, help="explicit Chrome/Edge executable")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="manifest relative to repo root")
    parser.add_argument("--asset-id", default=DEFAULT_ASSET)
    parser.add_argument("--path", default=DEFAULT_PATH)
    parser.add_argument("--direction", default="SE")
    parser.add_argument("--screenshot", default=None, help="evidence path (default: temp dir)")
    parser.add_argument("--window-size", default="1280,1600", help="headless window size")
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args(argv)

    browser = find_browser(args.browser)
    if not browser:
        print("ENVIRONMENT ERROR: no Chrome/Edge binary found; pass --browser", file=sys.stderr)
        return 2

    root = REPO_ROOT.resolve()
    try:
        httpd = server.create_server("127.0.0.1", 0, root, args.manifest)
    except (OSError, ValueError) as exc:
        print(f"ENVIRONMENT ERROR: cannot start preview server: {exc}", file=sys.stderr)
        return 2
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    temp_dir = Path(tempfile.mkdtemp(prefix="opc08-browser-"))
    screenshot = Path(args.screenshot).resolve() if args.screenshot else temp_dir / "preview.png"
    screenshot.parent.mkdir(parents=True, exist_ok=True)
    profile = temp_dir / "profile"
    url = (
        f"http://127.0.0.1:{port}/?assetId={args.asset_id}"
        f"&path={args.path}&direction={args.direction}&play=1"
    )

    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        f"--window-size={args.window_size}",
        f"--user-data-dir={profile}",
        "--virtual-time-budget=10000",
        f"--screenshot={screenshot}",
        "--dump-dom",
        url,
    ]
    print(f"browser: {browser}")
    print(f"url:     {url}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: browser did not finish before the timeout", file=sys.stderr)
        return 1
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    dom = result.stdout or ""
    checks = {
        "layout-supported": "true",
        "layout-cols": "6",
        "layout-rows": "8",
        "frame-width": "48",
        "frame-height": "64",
        "current-direction": args.direction,
        "animation": "walk",
    }
    failures = []
    observed = {}
    for name, expected in checks.items():
        value = data_attribute(dom, name)
        observed[name] = value
        if value != expected:
            failures.append(f"data-{name}: expected {expected!r}, got {value!r}")
    frame = data_attribute(dom, "current-frame")
    observed["current-frame"] = frame
    if frame is None or not frame.isdigit() or not 0 <= int(frame) <= 5:
        failures.append(f"data-current-frame: expected 0..5, got {frame!r}")

    print("DOM data attributes:")
    for name, value in observed.items():
        print(f"  data-{name}={value!r}")
    if result.returncode != 0:
        failures.append(f"browser exited with code {result.returncode}")
    if not screenshot.is_file() or screenshot.stat().st_size < 1000:
        failures.append(f"screenshot missing or too small: {screenshot}")
    else:
        size = screenshot.stat().st_size
        print(f"screenshot: {screenshot} ({size} bytes)")

    if failures:
        print("\nFAIL:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        if result.stderr:
            print("browser stderr:\n" + result.stderr[-4000:], file=sys.stderr)
        return 1
    print("\nPASS: headless browser rendered the 6-column x 8-row layout and played 'walk'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
