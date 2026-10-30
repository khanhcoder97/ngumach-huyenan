# OPC-09 — Deterministic asset bundle audit, pack and verify

Standard-library-only tooling for Muse asset deliveries. It never modifies the
source art tree and never claims Unity runtime/playback verification.

## Tools

| Tool | Purpose |
|------|---------|
| `audit_bundle.py` | Read-only per-asset size/SHA-256/coverage/license/dependency report |
| `pack_bundle.py` | Allowlist/dependency-gated deterministic pack (dry-run by default) |
| `unpack_bundle.py` | Verify a packed bundle, then copy it to a fresh directory and verify the copies |
| `bundle_format.py` | Shared path confinement, canonical JSON and digest implementation |

## Quick start (from the repository root)

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
partial bundle (only the deterministic pack report is written).

## Determinism and digest

* No `packedAt`/`auditedAt` wall-clock fields.
* JSON keys are sorted and written with a trailing newline.
* Bundle assets are sorted by `(path, assetId)`.
* `bundleDigest` = SHA-256 over canonical JSON of the sorted records
  `{assetId, path, sizeBytes, sha256}`.
* Audit and pack use the same function (`bundle_format.compute_bundle_digest`),
  so the audit digest equals the pack digest for the same asset set.
* Repeated runs on unchanged input produce byte-identical reports and
  `bundle-manifest.json`.

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

## Verification evidence

```text
python -m unittest discover -s Tools/AssetPack/tests -v
Ran 37 tests in 3.044s
OK (skipped=2: Windows symlink privileges)
```

Real delivered manifest:

```text
audit:  bundleDigest=8998eb214a5fe778e56b6c7eb1f68251889b41e3023f2ff1cf53ad32c0a94051
pack:   included=1 errors=0 draft=True bundleDigest=8998eb...a94051
verify: assets=1 verified=1 digest=8998eb...a94051
unpack: outputDigest=8998eb...a94051 outputOk=True
```

Two independent audit runs produced the same SHA-256 for
`bundle-audit-report.json` (`04900f5d...0b705c`). CI wiring lives in
`.github/workflows/asset-handoff-validation.yml` (OPC-10); the complete
clean-clone command is `python Tools/AssetPack/run_all_checks.py`.

Refs #40, OPC-09. Not self-merging.
