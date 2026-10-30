# Manifest v2 fixtures (OPC-06 draft)

These manifests are **structural fixtures** for the draft v2 contract. They are
not runtime catalogue entries and must not be copied into `Client/Assets/ArtManifests/`.

- `valid_actor_8dir.json` — 288×512 walk sheet, 6 columns × 8 direction rows,
  frame 48×64, 8 FPS, `layout=direction_rows`.
- `valid_effect_single_direction.json` — synthetic 96×64 VFX strip, frame 24×64,
  4 frames, `layout=strip`, `isDirectional=false`. The PNG is intentionally absent;
  validate it with `--skip-file-checks` until Muse delivers a real effect fixture.
- `valid_icon_static.json` — 32×32 icon with no frame geometry.
- `valid_multi_animation_ranges.json` — two clips with explicit `columnStart`
  ranges; demonstrates that multiple animations are never checked with a single
  max-frame-count formula.
- `invalid_*.json` — negative fixtures: missing frame size, grid mismatch,
  duplicate direction, wrong direction order, overlapping clips, unsupported
  manifest version.

Validate one fixture from the repository root:

```bash
python Implementation/Asset_Handoff/validate_asset_delivery.py \
  --manifest Implementation/Asset_Handoff/fixtures/manifest_v2/valid_actor_8dir.json \
  --skip-file-checks
```

The invalid fixtures are exercised by `tests/test_manifest_v2.py`; CI runs the
unit tests rather than treating these files as a delivery bundle.
