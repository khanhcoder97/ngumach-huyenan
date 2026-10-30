#!/usr/bin/env python3
"""OPC-10: one local command to run the full asset handoff pipeline.

The command is deterministic and exits non-zero on the first logical failure
while still running every independent check. It exercises the real tools
(not re-implemented logic):

1. OPC-05/06/07 validator unit tests
2. OPC-08 preview unit/HTTP tests
3. OPC-09 bundle audit/pack/unpack unit tests
4. Structural validation of the shipped example manifest
5. Deterministic audit: two runs must be byte-identical
6. Deterministic pack: two bundles must be byte-identical
7. pack -> verify -> unpack -> verify: all digests must agree
8. Negative gates: blocked/draft packs must not create a bundle
9. Preview server smoke: in-process server on an ephemeral port, real HTTP
   requests, truthful 6x8 / 48x64 layout assertion

No Unity, no .NET and no third-party Python packages are required.

Usage (from the repository root):
    python Tools/AssetPack/run_all_checks.py
    python Tools/AssetPack/run_all_checks.py --evidence-dir Tools/AssetPack/ci_evidence

Exit codes:
    0  all checks passed
    1  one or more checks failed
    2  environment / usage error

Refs #40, OPC-10. Not self-merging.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
ASSET_PREVIEW_DIR = REPO_ROOT / "Tools" / "AssetPreview"
DELIVERED_MANIFEST = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
ALLOWLIST = "Tools/AssetPack/allowlist.txt"
FAIL_MANIFEST = "Tools/AssetPack/fixtures/fail_manifest.json"
EXPECTED_ASSET_ID = "CHR_MINH_KIEM_WALK"
EXPECTED_LAYOUT = {
    "supported": True,
    "cols": 6,
    "rows": 8,
    "frameWidth": 48,
    "frameHeight": 64,
    "totalSprites": 48,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class CheckRunner:
    """Track logical checks and run CLI tools without hiding their output."""

    def __init__(self, evidence_dir: Path):
        self.evidence_dir = evidence_dir
        self.failures: list[str] = []
        self.checks = 0

    def record(self, name: str, passed: bool, detail: str = "") -> bool:
        self.checks += 1
        if passed:
            print(f"PASS: {name}")
        else:
            suffix = f" ({detail})" if detail else ""
            print(f"FAIL: {name}{suffix}")
            self.failures.append(name)
        return passed

    def run(
        self,
        cmd: list[str],
        description: str,
        expected: int = 0,
    ) -> subprocess.CompletedProcess:
        print(f"\n{'-' * 70}")
        print(f"> {description}")
        print(f"$ {' '.join(cmd)}")
        print(f"{'-' * 70}")
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
        self.record(
            description,
            proc.returncode == expected,
            f"expected exit {expected}, got {proc.returncode}",
        )
        return proc


def require_empty_dir(path: Path) -> None:
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise SystemExit(f"evidence directory must be absent or empty: {path}")


def test_preview_server(runner: CheckRunner) -> None:
    sys.path.insert(0, str(ASSET_PREVIEW_DIR))
    try:
        import server as preview_server
    finally:
        sys.path.pop(0)

    try:
        httpd = preview_server.create_server(
            "127.0.0.1", 0, REPO_ROOT, DELIVERED_MANIFEST
        )
    except (OSError, ValueError) as exc:
        runner.record("Preview server starts on an ephemeral port", False, str(exc))
        return
    runner.record("Preview server starts on an ephemeral port", True)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    base = f"http://127.0.0.1:{port}"
    try:
        with urllib.request.urlopen(f"{base}/", timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
            runner.record(
                "Preview root serves the canvas UI",
                response.status == 200 and 'id="spriteCanvas"' in body,
                f"status={response.status}",
            )

        encoded = (
            "Client%2FAssets%2FArt%2FCharacters%2FMinhKiem%2Fminh_kiem_walk.png"
        )
        with urllib.request.urlopen(f"{base}/api/sprites/{encoded}", timeout=10) as response:
            magic = response.read(8)
            runner.record(
                "Encoded sprite path returns PNG bytes",
                response.status == 200 and magic == b"\x89PNG\r\n\x1a\n",
                f"status={response.status} magic={magic!r}",
            )

        with urllib.request.urlopen(
            f"{base}/api/layout/{EXPECTED_ASSET_ID}", timeout=10
        ) as response:
            layout = json.loads(response.read().decode("utf-8"))
        frame = layout.get("frameSize") or {}
        grid = layout.get("grid") or {}
        actual = {
            "supported": layout.get("supported"),
            "cols": grid.get("cols"),
            "rows": grid.get("rows"),
            "frameWidth": frame.get("width"),
            "frameHeight": frame.get("height"),
            "totalSprites": layout.get("totalSprites"),
        }
        runner.record(
            "Layout API reports the canonical 6x8 / 48x64 matrix",
            actual == EXPECTED_LAYOUT,
            f"expected {EXPECTED_LAYOUT}, got {actual}",
        )
        runner.record(
            "Layout API keeps the canonical assetId and direction rows",
            layout.get("assetId") == EXPECTED_ASSET_ID
            and layout.get("directions") == ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            and layout.get("directionRows", {}).get("SW") == 5,
            f"assetId={layout.get('assetId')!r} directions={layout.get('directions')!r}",
        )
        runner.record(
            "Layout API exposes the walk animation without a 1-column full-row range",
            any(
                animation.get("name") == "walk"
                and animation.get("frames") == 6
                and animation.get("columnStart") == 0
                for animation in layout.get("animations", [])
            ),
            f"animations={layout.get('animations')!r}",
        )
    except Exception as exc:  # noqa: BLE001 - smoke test, report and continue
        runner.record("Preview HTTP smoke requests", False, f"{type(exc).__name__}: {exc}")
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=10)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the full OPC-05..10 asset handoff check suite."
    )
    parser.add_argument(
        "--evidence-dir",
        default=None,
        help="directory for reports/bundles (default: fresh temporary directory)",
    )
    parser.add_argument("--include-candidates", action="store_true",
                        help="also run OPC-11/12 tests and verify committed content/map candidates")
    parser.add_argument("--include-browser", action="store_true",
                        help="require real Chrome/Edge playback for the fixture and delivered Muse actor")
    args = parser.parse_args(argv)

    if args.evidence_dir:
        evidence_dir = Path(args.evidence_dir).expanduser().resolve()
        try:
            require_empty_dir(evidence_dir)
        except SystemExit as exc:
            print(f"ENVIRONMENT ERROR: {exc}", file=sys.stderr)
            return 2
        evidence_dir.mkdir(parents=True, exist_ok=True)
    else:
        evidence_dir = Path(tempfile.mkdtemp(prefix="opc10-evidence-"))

    print("=" * 70)
    print("OPC-10 asset handoff pipeline checks")
    print(f"Repository: {REPO_ROOT}")
    print(f"Evidence:   {evidence_dir}")
    print("=" * 70)

    runner = CheckRunner(evidence_dir)

    # 1..3: the real unit/integration suites.
    runner.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "Implementation/Asset_Handoff/tests",
            "-v",
        ],
        "OPC-05/06/07 validator unit tests",
    )
    runner.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "Tools/AssetPreview/tests",
            "-v",
        ],
        "OPC-08 preview unit/HTTP tests",
    )
    runner.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "Tools/AssetPack/tests",
            "-v",
        ],
        "OPC-09 bundle audit/pack/unpack tests",
    )

    # 4: manifest structure.
    runner.run(
        [
            sys.executable,
            "Implementation/Asset_Handoff/validate_asset_delivery.py",
            "--skip-file-checks",
            "--manifest",
            "Implementation/Asset_Handoff/muse_delivery_manifest.example.json",
        ],
        "Shipped example manifest structural validation",
    )

    # 5: deterministic audit (two independent runs, byte comparison).
    audit1 = evidence_dir / "audit1"
    audit2 = evidence_dir / "audit2"
    audit_cmd = [
        sys.executable,
        "Tools/AssetPack/audit_bundle.py",
        "--manifest",
        DELIVERED_MANIFEST,
        "--output",
    ]
    runner.run([*audit_cmd, str(audit1)], "Bundle audit run 1")
    runner.run([*audit_cmd, str(audit2)], "Bundle audit run 2")

    audit_report1 = audit1 / "bundle-audit-report.json"
    audit_report2 = audit2 / "bundle-audit-report.json"
    if audit_report1.is_file() and audit_report2.is_file():
        hash1 = sha256_file(audit_report1)
        hash2 = sha256_file(audit_report2)
        runner.record(
            "Audit reports are byte-identical",
            hash1 == hash2,
            f"{hash1} != {hash2}",
        )
        report1 = read_json(audit_report1)
        runner.record(
            "Audit covers the delivered asset with present coverage",
            report1.get("summary", {}).get("present") == 1
            and report1.get("summary", {}).get("totalAssets") == 1,
            f"summary={report1.get('summary')}",
        )
        print(f"audit report SHA-256: {hash1}")
        print(f"audit bundleDigest:   {report1.get('bundleDigest')}")
    else:
        runner.record("Audit reports were written", False)
        report1 = {}

    # 6: deterministic pack (two independent bundles, byte comparison).
    bundle1 = evidence_dir / "bundle1"
    bundle2 = evidence_dir / "bundle2"
    pack_cmd = [
        sys.executable,
        "Tools/AssetPack/pack_bundle.py",
        "--manifest",
        DELIVERED_MANIFEST,
        "--allowlist",
        ALLOWLIST,
        "--allow-draft",
        "--output",
    ]
    runner.run([*pack_cmd, str(bundle1)], "Bundle pack run 1 (allow draft)")
    runner.run([*pack_cmd, str(bundle2)], "Bundle pack run 2 (allow draft)")

    manifest1 = bundle1 / "bundle-manifest.json"
    manifest2 = bundle2 / "bundle-manifest.json"
    pack_digest = None
    if manifest1.is_file() and manifest2.is_file():
        hash1 = sha256_file(manifest1)
        hash2 = sha256_file(manifest2)
        runner.record(
            "Packed bundle manifests are byte-identical",
            hash1 == hash2,
            f"{hash1} != {hash2}",
        )
        bundle_manifest = read_json(manifest1)
        pack_digest = bundle_manifest.get("bundleDigest")
        pack_report = read_json(bundle1 / "bundle-pack-report.json")
        runner.record(
            "Pack report and bundle manifest agree on the digest",
            pack_report.get("bundleDigest") == pack_digest,
            f"report={pack_report.get('bundleDigest')} manifest={pack_digest}",
        )
        runner.record(
            "Packed bundle is marked draft with one included asset",
            bundle_manifest.get("draft") is True
            and len(bundle_manifest.get("assets", [])) == 1
            and bundle_manifest["assets"][0].get("assetId") == EXPECTED_ASSET_ID,
            f"draft={bundle_manifest.get('draft')} assets={len(bundle_manifest.get('assets', []))}",
        )
        runner.record(
            "Audit and pack digests match",
            report1.get("bundleDigest") == pack_digest,
            f"audit={report1.get('bundleDigest')} pack={pack_digest}",
        )
        print(f"bundle manifest SHA-256: {hash1}")
        print(f"bundleDigest:            {pack_digest}")
    else:
        runner.record("Materialised bundle manifests were written", False)

    # 7: verify -> unpack -> verify, including digest agreement.
    unpacked = evidence_dir / "unpacked"
    verify_report_path = evidence_dir / "unpacked-verify.json"
    if manifest1.is_file():
        runner.run(
            [
                sys.executable,
                "Tools/AssetPack/unpack_bundle.py",
                "--bundle",
                str(bundle1),
                "--output",
                str(unpacked),
                "--report",
                str(verify_report_path),
            ],
            "Verify, unpack and re-verify the bundle",
        )
        if verify_report_path.is_file():
            verify = read_json(verify_report_path)
            runner.record(
                "Unpacked copies re-verify with the same digest",
                verify.get("ok") is True
                and verify.get("outputOk") is True
                and verify.get("computedDigest") == pack_digest
                and verify.get("outputDigest") == pack_digest
                and not verify.get("outputErrors"),
                f"computed={verify.get('computedDigest')} output={verify.get('outputDigest')} "
                f"ok={verify.get('ok')} outputOk={verify.get('outputOk')}",
            )
            runner.record(
                "Bundle and unpacked manifest bytes are identical",
                (bundle1 / "bundle-manifest.json").read_bytes()
                == (unpacked / "bundle-manifest.json").read_bytes(),
            )
            print(f"unpacked outputDigest:   {verify.get('outputDigest')}")
        else:
            runner.record("Unpack verification report was written", False)
    else:
        runner.record("Unpack skipped because the pack failed", False)

    # 8: negative gates must not materialise a bundle.
    fail_out = evidence_dir / "negative_fail"
    fail_proc = runner.run(
        [
            sys.executable,
            "Tools/AssetPack/pack_bundle.py",
            "--manifest",
            FAIL_MANIFEST,
            "--output",
            str(fail_out),
        ],
        "Invalid manifest pack is blocked",
        expected=2,
    )
    if fail_proc.returncode == 2:
        report_path = fail_out / "bundle-pack-report.json"
        errors = ""
        if report_path.is_file():
            fail_report = read_json(report_path)
            errors = "\n".join(fail_report.get("errors", []))
            runner.record(
                "Invalid pack report names every defective asset",
                all(
                    name in errors
                    for name in ("CHR_MISSING_FILE", "CHR_DEPRECATED", "BAD_lowercase_id")
                ),
                errors,
            )
        runner.record(
            "Blocked pack creates no bundle manifest",
            not (fail_out / "bundle-manifest.json").exists(),
        )

    draft_out = evidence_dir / "negative_draft"
    draft_proc = runner.run(
        [
            sys.executable,
            "Tools/AssetPack/pack_bundle.py",
            "--manifest",
            DELIVERED_MANIFEST,
            "--allowlist",
            ALLOWLIST,
            "--output",
            str(draft_out),
        ],
        "Draft asset is blocked without --allow-draft",
        expected=2,
    )
    if draft_proc.returncode == 2:
        runner.record(
            "Blocked draft creates no bundle manifest",
            not (draft_out / "bundle-manifest.json").exists(),
        )

    # 9: preview server smoke, in-process and on an ephemeral port.
    test_preview_server(runner)

    if args.include_candidates:
        for directory, label in [
            ("Implementation/Tools/ContentPipeline/tests", "Candidate compiler tests"),
            ("Implementation/Tools/MuseMapAdapter/tests", "Muse map adapter tests"),
        ]:
            runner.run([sys.executable, "-m", "unittest", "discover", "-s", directory, "-v"], label)
        runner.run([sys.executable, "Implementation/Tools/ContentPipeline/cli.py", "check"],
                   "Committed content candidates match reviewed sources and compiler")
        runner.run([sys.executable, "Implementation/Tools/MuseMapAdapter/cli.py", "check", "--layout",
                    "Implementation/Tools/MuseMapAdapter/fixtures/synthetic_layout.json"],
                   "Committed synthetic map sidecar matches the adapter")
        runner.run([sys.executable, "Implementation/Asset_Handoff/coverage_audit.py", "--check"],
                   "Coverage report remains reproducible")
    else:
        print("OPC-11/12: NOT REQUESTED (use --include-candidates)")

    if args.include_browser:
        runner.run([sys.executable, "Tools/AssetPreview/browser_smoke.py", "--screenshot",
                    str(evidence_dir / "fixture-browser.png")], "Real browser synthetic animation playback")
        runner.run([sys.executable, "Tools/AssetPreview/browser_smoke.py", "--manifest", DELIVERED_MANIFEST,
                    "--asset-id", EXPECTED_ASSET_ID, "--path",
                    "Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png", "--screenshot",
                    str(evidence_dir / "muse-browser.png")], "Real browser delivered Muse animation playback")
    else:
        print("BROWSER: UNVERIFIED IN THIS RUN (use --include-browser)")
    print("UNITY/NATIVE/DEVICE: UNVERIFIED; candidate runtime activation remains OFF")

    print("\n" + "=" * 70)
    if runner.failures:
        print(f"SOME CHECKS FAILED ({len(runner.failures)} of {runner.checks})")
        for failure in runner.failures:
            print(f"  - {failure}")
        print(f"Evidence retained at: {evidence_dir}")
        print("=" * 70)
        return 1
    print(f"ALL CHECKS PASSED ({runner.checks} checks)")
    print(f"Evidence retained at: {evidence_dir}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
