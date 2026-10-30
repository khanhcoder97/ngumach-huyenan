"""Reproduce producer acceptance failures against immutable Git objects.

No agent checkout is edited. Only synthetic temporary assets are served locally.
Exit 1 means acceptance failures; it is not a unit-test-suite success claim.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen
import zlib

ROOT = Path(__file__).resolve().parents[2]
OPC07 = "cf59102fc0600d05266bdf4b44e15a9825c5d711"
OPC08 = "2613f1be188b305f41ab58e4eb4240ca646db0e5"


def git_file(revision, path):
    return subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def chunk(kind, payload):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(
        ">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def png():
    header = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    return b"\x89PNG\r\n\x1a\n" + header + chunk(
        b"IDAT", zlib.compress(b"\0\xff\xff\xff\xff")) + chunk(b"IEND", b"")


def run():
    results = []

    def record(case, expected, actual, passed, revision):
        results.append(dict(case=case, revision=revision, expected=expected,
                            actual=actual, passed=bool(passed)))

    with tempfile.TemporaryDirectory(prefix="ngumach-producer-review-") as temp:
        scratch = Path(temp)
        code = scratch / "modules"
        code.mkdir()
        for name in ("png_validation", "png_alpha_check", "unity_meta_validation", "validate_import"):
            target = code / (name + ".py")
            target.write_bytes(git_file(OPC07, "Implementation/Asset_Handoff/" + name + ".py"))
        sys.path.insert(0, str(code))
        pv = module("png_validation", code / "png_validation.py")
        module("png_alpha_check", code / "png_alpha_check.py")
        um = module("unity_meta_validation", code / "unity_meta_validation.py")
        module("validate_import", code / "validate_import.py")

        valid = png()
        corrupt = bytearray(valid)
        corrupt[-13] ^= 1  # Last byte of the IDAT CRC, preserving all chunk lengths.
        samples = {"valid_png": (valid, True), "idat_crc_corrupted": (bytes(corrupt), False),
                   "missing_idat_iend": (valid[:33], False),
                   "truncated_idat": (valid[:45], False)}
        for name, (data, should_accept) in samples.items():
            target = scratch / (name + ".png")
            target.write_bytes(data)
            try:
                pv.validate_png_structure(target)
                accepted = True
            except Exception:
                accepted = False
            record(name, "accepted" if should_accept else "rejected",
                   "accepted" if accepted else "rejected", accepted == should_accept, OPC07)

        meta = scratch / "empty.png.meta"
        meta.write_text("fileFormatVersion: 2\nguid: " + "1" * 32 + "\nTextureImporter:\n")
        result = um.validate_meta(meta, "SYNTHETIC")
        record("missing_import_fields", "error or explicit unsupported",
               dict(errors=result.errors, warnings=result.warnings),
               bool(result.errors or result.warnings), OPC07)

        meta.write_text("""fileFormatVersion: 2
guid: 11111111111111111111111111111111
TextureImporter:
  spriteMode: 2
  spritePixelsToUnits: 20
  filterMode: 0
  enableMipMap: 0
  spriteSheet:
    sprites:
    - serializedVersion: 2
      name: synthetic_out_of_bounds
      rect:
        x: 900
        y: 900
        width: 48
        height: 64
      pivot: {x: 0.5, y: 0}
""")
        result = um.validate_meta(meta, "SYNTHETIC")
        record("multiline_unity_sprite_rect", "one parsed rect or explicit unsupported",
               dict(parsed=len(result.sprites), errors=result.errors, warnings=result.warnings),
               len(result.sprites) == 1 or bool(result.errors or result.warnings), OPC07)

        # CLI --root must resolve assets against the supplied root, not module location.
        asset_root = scratch / "assets"
        asset_root.mkdir()
        (asset_root / "pixel.png").write_bytes(valid)
        (asset_root / "pixel.png.meta").write_text("""guid: 11111111111111111111111111111111
TextureImporter:
  spriteMode: 1
  spritePixelsToUnits: 20
  filterMode: 0
  enableMipMap: 0
  pivot: {x: 0.5, y: 0}
""")
        (asset_root / "manifest.json").write_text(json.dumps(dict(assets=[dict(
            assetId="SYNTHETIC", kind="sprite_sheet", path="pixel.png")])) )
        process = subprocess.run([sys.executable, str(code / "validate_import.py"),
                                  "--root", str(asset_root), "--manifest", "manifest.json"],
                                 capture_output=True, text=True)
        record("cli_root_override", "valid external root does not crash",
               dict(exit=process.returncode, traceback="Traceback" in process.stderr),
               process.returncode == 0, OPC07)

        preview_path = code / "preview.py"
        preview_path.write_bytes(git_file(OPC08, "Tools/AssetPreview/server.py"))
        preview = module("producer_preview_probe", preview_path)
        handler = preview.AssetPreviewHandler
        handler.root_path = str(asset_root)
        handler.log_message = lambda *args: None
        actual_manifest = json.loads(git_file("f72b8b921c846808f518b8475213be1d933ac94c",
                                              "Client/Assets/ArtManifests/muse_delivery_manifest.json"))
        manifest_path = asset_root / "Client/Assets/ArtManifests/muse_delivery_manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(actual_manifest))
        nested_path = asset_root / "nested/pixel.png"
        nested_path.parent.mkdir()
        nested_path.write_bytes(valid)
        server = HTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def http(path):
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}" + path, timeout=3) as response:
                    return response.status
            except HTTPError as exc:
                return exc.code

        try:
            literal = http("/api/sprites/nested/pixel.png")
            encoded = http("/api/sprites/" + quote("nested/pixel.png", safe=""))
            record("preview_browser_encoded_path", "both image URLs return 200",
                   dict(literal=literal, browser_encoded=encoded), literal == encoded == 200, OPC08)
            layout = http("/api/layout/CHR_MINH_KIEM_WALK")
            record("preview_real_manifest_asset_id", "layout found by canonical assetId",
                   dict(http=layout), layout == 200, OPC08)
            # Self-authored marker only; no unrelated files are read or disclosed.
            outside = scratch / "cwd-only"
            outside.mkdir()
            (outside / "outside-marker.txt").write_text("synthetic-review-marker")
            prior_cwd = Path.cwd()
            try:
                os.chdir(outside)
                outside_status = http("/api/sprites/outside-marker.txt")
            finally:
                os.chdir(prior_cwd)
            record("preview_root_confinement", "outside configured root is not served",
                   dict(http=outside_status), outside_status != 200, OPC08)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    return dict(kind="PRODUCER_ACCEPTANCE_REPRODUCTION", date="2026-10-30",
                scope="Synthetic Python/HTTP probes; no browser or Unity evidence",
                cases=results, passed=sum(x["passed"] for x in results),
                failed=sum(not x["passed"] for x in results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(1 if report["failed"] else 0)
