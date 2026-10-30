# OPC-09/OPC-10 — Asset bundle audit, pack, verify and full pipeline checks

Standard-library-only tooling for Muse asset deliveries. It never modifies the
source art tree and never claims Unity runtime/playback verification.

## Tools

| Tool | Purpose |
|------|---------|
| `audit_bundle.py` | Read-only per-asset size/SHA-256/coverage/license/dependency report |
| `pack_bundle.py` | Allowlist/dependency-gated deterministic pack (dry-run by default) |
| `unpack_bundle.py` | Verify a packed bundle, then copy it to a fresh directory and verify the copies |
| `bundle_format.py` | Shared path confinement, canonical JSON and digest implementation |
| `run_all_checks.py` | One command for tests, deterministic audit/pack, pack→unpack verification and the preview smoke |

## Clean clone → full verification

```bash
git clone https://github.com/khanhcoder97/ngumach-huyenan.git
cd ngumach-huyenan
git lfs pull

python Tools/AssetPack/run_all_checks.py
```

`run_all_checks.py` performs, in order:

1. OPC-05/06/07 validator unit tests (`Implementation/Asset_Handoff/tests`)
2. OPC-08 preview unit/HTTP tests (`Tools/AssetPreview/tests`)
3. OPC-09 audit/pack/unpack tests (`Tools/AssetPack/tests`)
4. Structural validation of the shipped example manifest
5. **Audit twice** and require byte-identical reports
6. **Pack twice** and require byte-identical `bundle-manifest.json`
7. **Verify → unpack → verify** and require the audit, pack, bundle and unpacked
   digests to match, with byte-identical bundle/unpacked manifests
8. Negative gates: an invalid fixture and a draft-without-`--allow-draft` pack
   must exit `2` and create **no** `bundle-manifest.json`
9. Preview smoke on an **ephemeral port** (no fixed port, no `sleep`): real
   HTTP requests for the UI, an encoded sprite path and the truthful
   `CHR_MINH_KIEM_WALK` 6×8 / 48×64 layout

Pass `--evidence-dir Tools/AssetPack/ci_evidence` to keep reports and bundles
for inspection/upload. Exit codes: `0` all checks passed, `1` a check failed,
`2` environment/usage error.

## Individual tools

```bash
# 1. Audit the delivered manifest (deterministic output)
python Tools/AssetPack/audit_bundle.py \
    --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
    --output Tools/AssetPack/audit_out --copy-bundle

# 2. Validate a pack without writing bundle files
python Tools/AssetPack/pack_bundle.py \
    --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
    --allowlist Tools/AssetPack/allowlist.txt --allow-draft --dry-run

# 3. Materialise, verify and unpack
python Tools/AssetPack/pack_bundle.py \
    --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json \
    --allowlist Tools/AssetPack/allowlist.txt --allow-draft \
    --output Tools/AssetPack/bundle_out

python Tools/AssetPack/unpack_bundle.py \
    --bundle Tools/AssetPack/bundle_out \
    --output Tools/AssetPack/unpacked_out \
    --report Tools/AssetPack/verify-report.json
```

`--root` confines the manifest, allowlist and asset paths. Relative `--output`
paths are resolved under `--root`; absolute output paths are accepted. The pack
refuses a non-empty output directory instead of overwriting it.

## Pack gating

A bundle is written only when **all** checks pass:

* `assetId` matches `^[A-Z0-9_]+$` and is unique;
* `path` is a safe forward-slash relative path under `Client/Assets/` and an
  agreed art root, with no duplicate paths;
* required metadata is present and typed (`kind`, `status`, positive
  `pixelWidth`/`pixelHeight`, `pixelsPerUnit == 20`, `previewPath`);
* `status` is `approved`, or `draft` with `--allow-draft` (bundle marked
  `draft`);
* the declared file exists, is not a Git LFS pointer, and is hashable;
* every `dependencies[]` / `replacesAssetId` entry exists, is included in the
  same pack, is not self-referential and is not deprecated;
* every included path is on the allowlist, or the allowlist file is absent.

Validation happens before any bundle file is written, so a failed pack leaves no
partial bundle (only the deterministic pack report is written). The reproducible
failure fixture is documented in `fixtures/README.md`.

## Determinism and digest

* No `packedAt`/`auditedAt` wall-clock fields.
* JSON keys are sorted and written with a trailing newline.
* Bundle assets are sorted by `(path, assetId)`.
* `bundleDigest` = SHA-256 over canonical JSON of the sorted records
  `{assetId, path, sizeBytes, sha256}`.
* Audit and pack use the same function (`bundle_format.compute_bundle_digest`),
  so the audit digest equals the pack digest for the same asset set.
* Repeated runs on unchanged input produce byte-identical reports and
  `bundle-manifest.json`; `run_all_checks.py` asserts this on every run.

## Verification and unpacking

`unpack_bundle.py` re-reads `bundle-manifest.json` and checks:

* `bundleFormat` is `1`;
* asset IDs/paths are unique, relative and confined to the bundle;
* no asset path uses a symlink;
* every file exists and its real size and SHA-256 match the declaration;
* the recomputed `bundleDigest` equals the declared digest;
* extra files are reported as warnings because they are not covered by the
  digest.

Unpacking only starts after source verification passes. It writes to a fresh
directory, copies only verified assets plus the bundle/source manifests, then
re-runs the same verification on the copies.

Exit codes: `0` success, `1` environment/usage error, `2` audit manifest or
bundle verification failure.

## CI wiring

`.github/workflows/asset-handoff-validation.yml` checks out with LFS, validates
the delivered manifest against the changed files, then runs the same
`run_all_checks.py --evidence-dir Tools/AssetPack/ci_evidence`. It explicitly
asserts that both packed bundles, the unpacked bundle, the verify report and
byte-identical bundle/unpacked manifests exist, and uploads the evidence
artifact. A separate `asset-preview-validation.yml` runs the headless-browser
screenshot smoke; the preview's own unit tests run here too.

There is no fixed port and no arbitrary `sleep`: the preview server is started
in-process on port `0`, its assigned port is used for the HTTP requests, and it
is shut down in `finally`.

## Verification evidence

Local Windows run (Python 3.14.6):

```text
python Tools/AssetPack/run_all_checks.py --evidence-dir %TEMP%\opc10-evidence-local
Ran 63 tests ... OK            (OPC-05/06/07)
Ran 29 tests ... OK (skipped=1) (OPC-08, Windows symlink privilege)
Ran 37 tests ... OK (skipped=2) (OPC-09, Windows symlink privilege)
ALL CHECKS PASSED (28 checks)
```

Real delivered manifest (`muse_delivery_manifest.json`):

```text
audit report SHA-256: 04900f5d7eec2ac661423415128b016685cc9aace3a324671b0338f8010b705c
audit bundleDigest:   8998eb214a5fe778e56b6c7eb1f68251889b41e3023f2ff1cf53ad32c0a94051
pack bundleDigest:    8998eb214a5fe778e56b6c7eb1f68251889b41e3023f2ff1cf53ad32c0a94051
unpack outputDigest:  8998eb214a5fe778e56b6c7eb1f68251889b41e3023f2ff1cf53ad32c0a94051
bundle manifest SHA-256: 187e78b0f6e164754d8858024d250365038c4785b52fb565f1004c759e656ae8
```

Asset identity: `CHR_MINH_KIEM_WALK`, 185988 bytes, SHA-256
`bbec07fba1e9c598fc4cfdb1bf2e225cd4dc7038f55911b5de948b30d9b0582d`.

The preview smoke asserts `supported=true`, 6 columns × 8 rows, 48×64 frames,
48 sprites, canonical directions with `SW` on row 5, and a 6-frame `walk`
animation starting at column 0. This is static tooling validation only — **no
Unity import, animation or in-game playback claim** is made.

Refs #40, OPC-09/OPC-10. Not self-merging.
# Codex tiếp nhận và mở rộng OPC-11/12

Toàn bộ tooling OpenCode nay do Codex phụ trách (work order15). Chạy cả asset pipeline,
candidate compiler/map adapter và real-browser checks bằng:

```sh
python Tools/AssetPack/run_all_checks.py --include-candidates --include-browser
```

Không dùng flags sẽ chỉ chạy phạm vi OPC-05..10 và ghi rõ những lớp chưa được yêu cầu.
Candidate JSON có thể structurally valid nhưng còn BLOCKED_UNRESOLVED; runtime activation
luôn OFF. Xem README trong `Implementation/Tools/ContentPipeline` và `MuseMapAdapter`.
