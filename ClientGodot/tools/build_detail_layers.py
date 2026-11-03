#!/usr/bin/env python3
"""Split the approved Bến Mưa detail composite (style-2 rollout, ART_REVIEW 2026-11-03) into two
runtime overlay layers for the Godot client, WITHOUT touching geometry:

  detail        = your_files/ben_mua_detail/rollout2_official/full_map_style2_native.png
  reconstruction= the Godot tilemap's own full-map render (same pixels the
                  TileMapLayers produce) — pixels where detail differs from
                  reconstruction are exactly the detail pass's contribution
                  (props, decals, texture work, shore foam...).
  blocked grid  = tilemap.json (450x60) decides the split:
                  diff pixels on WALKABLE cells -> detail_under (ground
                  decals, path wear, water sparkle under the player)
                  diff pixels on BLOCKED cells  -> detail_over (houses,
                  trees, fences — drawn above the player so he passes
                  behind roofs/canopies)

Outputs (into the Godot project):
  assets/tilemap/full_map/detail_under.png / detail_over.png (RGBA)
  assets/tilemap/full_map/detail_layers.json  (counts + alpha sample
  points + an occlusion screenshot spot, consumed by DetailTest)
"""
import json
import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path.home() / "workspace"
DETAIL = ROOT / "your_files/ben_mua_detail/rollout2_official/full_map_style2_native.png"
PROJ = ROOT / "godot-prototype/NgumachPrototype/assets/tilemap/full_map"
TOL = 12  # per-channel tolerance for "same pixel"
CELL = 16

detail = np.asarray(Image.open(DETAIL).convert("RGB")).astype(np.int16)
recon = np.asarray(Image.open(PROJ / "reconstruction_full.png").convert("RGB")).astype(np.int16)
assert detail.shape == recon.shape == (960, 7200, 3), (detail.shape, recon.shape)

data = json.loads((PROJ / "tilemap.json").read_text())
cols, rows = data["cols"], data["rows"]
blocked = np.zeros((rows, cols), dtype=bool)
for c, r in data["blocked"]:
    blocked[r, c] = True

diff = np.abs(detail - recon).max(axis=2) > TOL            # (960, 7200)
cell_blocked_px = np.repeat(np.repeat(blocked, CELL, axis=0), CELL, axis=1)
under_mask = diff & ~cell_blocked_px
over_mask = diff & cell_blocked_px

detail_rgb = np.asarray(Image.open(DETAIL).convert("RGB"))
def emit(mask, name):
    out = np.zeros((960, 7200, 4), dtype=np.uint8)
    out[..., :3] = detail_rgb
    out[..., 3] = np.where(mask, 255, 0).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(PROJ / name)
    return int(mask.sum())

under_px = emit(under_mask, "detail_under.png")
over_px = emit(over_mask, "detail_over.png")
same_px = int((~diff).sum())

def samples(mask, n=3):
    """First n pixel coords (scan order) where the mask is set, spaced out."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return []
    idx = np.linspace(0, len(xs) - 1, n).astype(int)
    return [[int(xs[i]), int(ys[i])] for i in idx]

# Occlusion spot: a blocked cell rich in over-pixels whose two cells below
# are walkable — the player stands there and the prop must cover his head.
shot_spot = None
over_cells = over_mask.reshape(rows, CELL, cols, CELL).sum(axis=(1, 3))
for r in range(rows - 2):
    for c in range(cols):
        if blocked[r, c] and over_cells[r, c] >= 200 and not blocked[r + 1, c] and not blocked[r + 2, c]:
            shot_spot = {
                "blocked_cell": [c, r],
                "player_px": [c * CELL + 8, (r + 2) * CELL + 14],
            }
            break
    if shot_spot:
        break

manifest = {
    "tolerance": TOL,
    "total_px": 7200 * 960,
    "same_px": same_px,
    "under_px": under_px,
    "over_px": over_px,
    "under_samples": samples(under_mask),
    "over_samples": samples(over_mask),
    "shot_spot": shot_spot,
}
(PROJ / "detail_layers.json").write_text(json.dumps(manifest, indent=1))
total = 7200 * 960
print(f"same {same_px/total:.1%}  under {under_px} ({under_px/total:.1%})  over {over_px} ({over_px/total:.1%})")
print("shot_spot:", shot_spot)
print("under_samples:", manifest["under_samples"], " over_samples:", manifest["over_samples"])
