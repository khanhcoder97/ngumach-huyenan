#!/usr/bin/env python3
"""Converter: Bến Mưa tiledata JSON (BM-D prep) -> Godot 4 tilemap package.

Input : strip JSON with layers ground/water/path (tile ids) + blocked (0/1),
        kit tiles in ben_mua_bm_b/tiles16/ (16x16 px, tile = 0.8 WU at 20 PPU).
Output: <out>/atlas.png          - composited atlas, one 16x16 cell per tile id
        <out>/tilemap.json       - Godot-side metadata: id->atlas coord, per-layer
                                   cell lists (layer, x, y, tile index), blocked
                                   cell list, and audit counts.
        <out>/reconstruction.png - strip re-rendered from JSON alone, for a
                                   pixel-match check against the BM-C native
                                   render (props overlay explains the gap).

Tile ids follow TILEDATA_README: plain id = kit file name; derived ids use the
exact formulas from the strip build scripts; `id~flipv/~fliph/~rot90/180/270`
variants apply the transform to the base tile (rot = CCW, per README).
Collision is DATA-driven from the blocked layer, never inferred from tile
type: the strip contains grass tiles that are blocked (warehouse footprint).
"""
import json, os, sys
from PIL import Image

TILE = 16

DIRT_RAMP = [(0x55, 0x43, 0x2F), (0x6E, 0x59, 0x40), (0x86, 0x70, 0x4F), (0x9C, 0x85, 0x63)]
STONE_RAMP = [(0x43, 0x47, 0x4B), (0x62, 0x67, 0x6B), (0x83, 0x89, 0x8A), (0xA3, 0xA8, 0xA0)]

def derive_flat(src, blend, ramp, flip=False):
    """Exact copy of derive_flat in the BM-C strip build scripts:
    blend toward the mean, snap every pixel to the nearest ramp color."""
    im = src.convert('RGB')
    px = list(im.getdata())
    mean = tuple(sum(p[i] for p in px) // len(px) for i in range(3))
    im = Image.blend(im, Image.new('RGB', im.size, mean), blend)
    out = Image.new('RGB', im.size)
    op, ip = out.load(), im.load()
    for y in range(16):
        for x in range(16):
            p = ip[x, y]
            op[x, y] = min(ramp, key=lambda q: sum((p[i] - q[i]) ** 2 for i in range(3)))
    if flip:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    return out.convert('RGBA')

def build_tile_resolver(kit_dir):
    kit = {n[:-4]: Image.open(os.path.join(kit_dir, n)).convert('RGBA')
           for n in os.listdir(kit_dir) if n.endswith('.png')}

    def make_field_a():
        """build_strip_256_360.py: dirt_plain_a + furrow shading rows."""
        im = derive_flat(kit['dirt_path_a'], 0.86, DIRT_RAMP).convert('RGB')
        px = im.load()
        for y in range(16):
            for x in range(16):
                r, g, b = px[x, y]
                if y % 5 == 4:
                    px[x, y] = (int(r * 0.78), int(g * 0.78), int(b * 0.78))
                elif y % 5 == 0:
                    px[x, y] = (min(255, int(r * 1.07)), min(255, int(g * 1.07)), min(255, int(b * 1.05)))
        return im.convert('RGBA')

    def make_field_b():
        """build_strip_256_360.py: grass_wet_a + dirt-tinted furrow row."""
        im = kit['grass_wet_a'].convert('RGB')
        px = im.load()
        dirt = (0x6E, 0x59, 0x40)
        for y in range(16):
            for x in range(16):
                if y % 5 == 2:
                    r, g, b = px[x, y]
                    px[x, y] = tuple(int(p * 0.55 + d * 0.45) for p, d in zip((r, g, b), dirt))
        return im.convert('RGBA')

    derived = {
        'dirt_plain_a': lambda: derive_flat(kit['dirt_path_a'], 0.86, DIRT_RAMP),
        'dirt_plain_b': lambda: derive_flat(kit['dirt_path_a'], 0.90, DIRT_RAMP, True),
        'arena_floor_a': lambda: derive_flat(kit['stone_paving_a'], 0.93, STONE_RAMP),
        'arena_floor_b': lambda: derive_flat(kit['stone_paving_a'], 0.96, STONE_RAMP, True),
        'field_a': make_field_a,
        'field_b': make_field_b,
        'path_grass_h': lambda: kit['path_grass_v'].rotate(-90, expand=True),
        'shore_mud_w':  lambda: kit['shore_mud_s'].rotate(-90, expand=True),
        'shore_mud_e':  lambda: kit['shore_mud_s'].rotate(90, expand=True),
        'shore_stone_n': lambda: kit['shore_stone_s'].transpose(Image.FLIP_TOP_BOTTOM),
        'shore_stone_w': lambda: kit['shore_stone_s'].rotate(-90, expand=True),
        'shore_stone_e': lambda: kit['shore_stone_s'].rotate(90, expand=True),
    }
    cache = {}
    def resolve(tile_id):
        if tile_id in cache:
            return cache[tile_id]
        base, _, variant = tile_id.partition('~')
        if base in kit:
            im = kit[base].copy()
        elif base in derived and derived[base] is not None:
            im = derived[base]()
        else:
            raise KeyError(f"cannot resolve tile id: {tile_id}")
        if variant == 'flipv':
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        elif variant == 'fliph':
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif variant == 'rot90':
            im = im.transpose(Image.ROTATE_90)
        elif variant == 'rot180':
            im = im.transpose(Image.ROTATE_180)
        elif variant == 'rot270':
            im = im.transpose(Image.ROTATE_270)
        elif variant:
            raise KeyError(f"unknown variant in tile id: {tile_id}")
        cache[tile_id] = im
        return im
    return resolve

def main():
    strip_json, kit_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(strip_json))
    cols, rows = data['cols'], data['rows']
    resolve = build_tile_resolver(kit_dir)

    # Collect ids in first-seen order for a stable atlas layout.
    ids = []
    for layer in ('ground', 'water', 'path'):
        for row in data['layers'][layer]:
            for v in row:
                if v and v not in ids:
                    ids.append(v)
    atlas_cols = 8
    atlas_rows = (len(ids) + atlas_cols - 1) // atlas_cols
    atlas = Image.new('RGBA', (atlas_cols * TILE, atlas_rows * TILE), (0, 0, 0, 0))
    index = {}
    for i, tid in enumerate(ids):
        ax, ay = i % atlas_cols, i // atlas_cols
        atlas.paste(resolve(tid), (ax * TILE, ay * TILE))
        index[tid] = [ax, ay]
    atlas.save(os.path.join(out_dir, 'atlas.png'))

    cells = {'ground': [], 'water': [], 'path': []}
    layer_counts = {}
    for layer in cells:
        n = 0
        for r in range(rows):
            for c in range(cols):
                v = data['layers'][layer][r][c]
                if v:
                    cells[layer].append([c, r, ids.index(v)])
                    n += 1
        layer_counts[layer] = n
    blocked = [[c, r] for r in range(rows) for c in range(cols)
               if data['layers']['blocked'][r][c] == 1]

    meta = {
        'strip': data['strip'], 'originWU': data['originWU'], 'cellWU': data['cellWU'],
        'cols': cols, 'rows': rows, 'tilePx': TILE,
        'tileIds': ids, 'tileIndex': index,
        'layerCounts': layer_counts, 'blockedCount': len(blocked),
        'cells': cells, 'blocked': blocked,
    }
    with open(os.path.join(out_dir, 'tilemap.json'), 'w') as f:
        json.dump(meta, f)

    # Reconstruction (audit): paste tiles per JSON only, no props/overlays.
    recon = Image.new('RGBA', (cols * TILE, rows * TILE), (0, 0, 0, 255))
    for layer in ('ground', 'water', 'path'):
        for r in range(rows):
            for c in range(cols):
                v = data['layers'][layer][r][c]
                if v:
                    recon.paste(resolve(v), (c * TILE, r * TILE))
    recon.save(os.path.join(out_dir, 'reconstruction.png'))

    total = sum(layer_counts.values())
    print(f"strip {data['strip']}: {cols}x{rows} cells, unique tile ids={len(ids)}")
    print(f"layer counts: {layer_counts} total={total} (grid={cols*rows})")
    print(f"blocked: {len(blocked)}")
    assert total == cols * rows, "every cell must have exactly one tile"
    print("CONVERT OK")

if __name__ == '__main__':
    main()
