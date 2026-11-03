#!/usr/bin/env python3
"""Per-class HUD portraits: the board-06 portrait ring filled with each
class's face, using the exact round-2 recipe (build_hud_r2.py):
  head = idle sheet S-row frame 0, crop (8,0)-(40,32); ring interior found
  by colour test + connected component at the centre + 2px dilation;
  backdrop (23,33,47); head x14 NEAREST anchored crop-point (20,15) onto
  ring centre (367,358), clipped to the interior mask.
Minh Kiem keeps the original approved portrait_ring_filled.png (copied).
Outputs: NgumachPrototype/assets/hud/portraits/portrait_<class>.png
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from pathlib import Path
import shutil

ROOT = Path.home() / "workspace"
PROJ = ROOT / "godot-prototype/NgumachPrototype"
RING = ROOT / "your_files/hud_board06/portrait_ring.png"
OUT = PROJ / "assets/hud/portraits"
OUT.mkdir(parents=True, exist_ok=True)

shutil.copy(ROOT / "your_files/hud_board06/portrait_ring_filled.png",
            OUT / "portrait_minh_kiem.png")

ring = Image.open(RING).convert("RGBA")
W, H = ring.size
cx, cy = 367, 358
a = np.array(ring).astype(int)
interior_test = (a[:, :, 3] > 200) & (a[:, :, 2] > a[:, :, 0]) & (a[:, :, 2] < 110) & (a[:, :, 0] < 80)
lab, _ = ndimage.label(interior_test)
mask = lab == lab[cy, cx]
mask = ndimage.binary_dilation(mask, iterations=2)
mask_img = Image.fromarray((mask * 255).astype(np.uint8))

for cls in ["anh_dao", "huyen_but", "thach_chuy", "linh_cung"]:
    idle = Image.open(PROJ / f"assets/chars/{cls}/idle.png").convert("RGBA")
    frame_s = idle.crop((0, 4 * 64, 48, 5 * 64))
    head = frame_s.crop((8, 0, 40, 32))
    filled = ring.copy()
    bd = Image.new("RGBA", (W, H), (23, 33, 47, 255))
    filled.paste(bd, (0, 0), mask_img)
    big = head.resize((32 * 14, 32 * 14), Image.NEAREST)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(big, (cx - 20 * 14, cy - 15 * 14), big)
    filled.paste(layer, (0, 0), mask_img)
    filled.save(OUT / f"portrait_{cls}.png")
    print("portrait", cls)
print("done")
