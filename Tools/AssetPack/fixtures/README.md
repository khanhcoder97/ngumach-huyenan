# OPC-10 reproducible fail input

`fail_manifest.json` is intentionally invalid. It exercises the pipeline's
failure path without touching the delivered manifest:

1. `CHR_MISSING_FILE` — declared PNG does not exist (pack fails).
2. `CHR_DEPRECATED` — status is `deprecated` (pack fails).
3. `BAD_lowercase_id` — assetId violates `^[A-Z0-9_]+$` (pack fails).

Run the failing demo from the repository root:

```bash
python Tools/AssetPack/pack_bundle.py \
    --manifest Tools/AssetPack/fixtures/fail_manifest.json \
    --output Tools/AssetPack/demo_fail_out
```

Expected: exit code `2`, findings naming all three asset IDs, and **no**
`bundle-manifest.json` in the output directory. The deterministic pack report
is still written so the findings can be inspected.

`run_all_checks.py` runs this case automatically and asserts that no bundle was
materialised.
