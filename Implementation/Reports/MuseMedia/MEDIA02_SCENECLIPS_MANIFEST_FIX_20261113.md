# MEDIA-02 — SCENE-CLIPS export-manifest reconciliation (2026-11-13)

Bookkeeping block closing the 8 pre-existing `validate_media_deliveries`
mismatches disclosed in the PROLOGUE V1 FIX report (2026-11-13). Owner ordered
the block in the main chat ("làm tiếp khối kia đi", 2026-11-13 ~03:50 JST).
Media-only scope; no media bytes changed.

## Root cause

WO37 M-C CP5 edited the timing of CIN_005/009/017/020 (continuity staging
fields). M-G CP7 (fix commit `9cd5808`) synced the three timing FILE mirrors
and the runtime cinematics manifest was regenerated — but the four
`scene_export_manifest_v1.json` records were never updated. They still carried
the pre-CP5 timing `sha256`/`sizeBytes`, so the validator reported, per scene:
`timing sha mismatch` + `runtime manifest files != export manifest files`
(2 × 4 = 8 mismatches, present since CP5/CP7, unrelated to the prologue fix).

## Change (content commit `53472cf11b10fc7400ce58692ef4be42af124274`)

In each of the 4 export manifests, ONLY `files.timing.sha256` and
`files.timing.sizeBytes` were set to the real current timing-file values —
which equal both the runtime manifest entry and the Narrative/Deliveries
source file (all three byte-verified):

| scene | before (sha prefix / bytes) | after (sha prefix / bytes) |
|---|---|---|
| CIN_005 | b82b2582f238 / 2377 | 4437df319bac / 2850 |
| CIN_009 | 0f49fc20b67f / 2381 | c8a567d67168 / 2836 |
| CIN_017 | 64a630bd18ba / 2397 | 8ce15679c56e / 2745 |
| CIN_020 | 064ac1818ade / 2345 | 0e6667dcda9f / 2972 |

Plus the dedicated checker
`Tools/MediaProduction/Muse/check_sceneclips_manifest_fix_v1.py`.

## Verification (from real bytes)

- Dedicated checker: **PASS 92/92** — all 20 scenes: export `files` == runtime
  `files`; recorded timing sha/size == real runtime timing file == Deliveries
  source; the 4 reconciled manifests differ from base `be9ccb8` ONLY inside
  `files.timing` (deep-compare).
- `validate_media_deliveries.py` (full): **verdict PASS** — 0 mismatches
  (previously MISMATCHES_FOUND with exactly the 8 above). Report:
  `MEDIA02_SCENECLIPS_MANIFEST_FIX_VALIDATION_20261113.json`.
- `verify_runtime_delivery.py`: **verdict PASS** (runtime audio 783; campaign
  20 scenes / 63 shots / 378 s / 21 cues — unchanged).
- Scope audit: block 5 paths / 0 violations; cumulative vs merge-base
  `cf17178` reported in the report commit message.

## Limits

Bookkeeping only: no audio/video/image bytes were created or modified, no
timing content changed (the CP5 timing bytes were already canonical — this
block only repairs the records describing them). All media remains
DRAFT_NOT_FINAL / NOT_AUDITIONED. PR #119 stays HOLD; Muse does not
self-merge.
