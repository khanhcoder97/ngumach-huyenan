#!/usr/bin/env python3
"""Merge all 6 Bến Mưa tiledata strips into ONE Godot tilemap package.

Strips are disjoint column ranges of the same 450x60 grid (origin WU X =
0/64/128/192/256/320, cell 0.8 WU), so merging = placing each strip's cells
at its column offset in a shared atlas/id space. Output schema is identical
to the single-strip converter, so BenMuaTilemapBuilder consumes it unchanged.

Audit targets (from TILEDATA_README / BM audits): 27,000 cells total,
water 4,960, blocked 5,375 — asserted here, not just printed.
Also renders the full map (7200x960) + a downscaled preview from the merged
data alone, as a visual seam check.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_tiledata import build_tile_resolver, TILE
from PIL import Image

STRIPS = ['strip_000_064', 'strip_064_128', 'strip_128_192',
          'strip_192_256', 'strip_256_320', 'strip_320_360']

def main():
    tiledata_dir, kit_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    resolve = build_tile_resolver(kit_dir)

    strips = [json.load(open(os.path.join(tiledata_dir, f'{s}.json'))) for s in STRIPS]
    rows = strips[0]['rows']
    total_cols = sum(s['cols'] for s in strips)

    ids = []
    cells = {'ground': [], 'water': [], 'path': []}
    blocked = []
    per_strip = []
    offset = 0
    for data in strips:
        counts = {}
        sb = 0
        for layer in cells:
            n = 0
            for r in range(rows):
                for c in range(data['cols']):
                    v = data['layers'][layer][r][c]
                    if v:
                        if v not in ids:
                            ids.append(v)
                        cells[layer].append([offset + c, r, ids.index(v)])
                        n += 1
            counts[layer] = n
        for r in range(rows):
            for c in range(data['cols']):
                if data['layers']['blocked'][r][c] == 1:
                    blocked.append([offset + c, r])
                    sb += 1
        per_strip.append({'strip': data['strip'], 'colOffset': offset,
                          'layerCounts': counts, 'blocked': sb})
        print(f"{data['strip']}: offset={offset} {counts} blocked={sb}")
        offset += data['cols']

    atlas_cols = 8
    atlas_rows = (len(ids) + atlas_cols - 1) // atlas_cols
    atlas = Image.new('RGBA', (atlas_cols * TILE, atlas_rows * TILE), (0, 0, 0, 0))
    index = {}
    for i, tid in enumerate(ids):
        ax, ay = i % atlas_cols, i // atlas_cols
        atlas.paste(resolve(tid), (ax * TILE, ay * TILE))
        index[tid] = [ax, ay]
    atlas.save(os.path.join(out_dir, 'atlas.png'))

    layer_counts = {L: len(v) for L, v in cells.items()}
    meta = {
        'strip': 'FULL_MAP', 'originWU': [0.0, 36.0], 'cellWU': 0.8,
        'cols': total_cols, 'rows': rows, 'tilePx': TILE,
        'tileIds': ids, 'tileIndex': index,
        'layerCounts': layer_counts, 'blockedCount': len(blocked),
        'cells': cells, 'blocked': blocked, 'perStrip': per_strip,
    }
    with open(os.path.join(out_dir, 'tilemap.json'), 'w') as f:
        json.dump(meta, f)

    recon = Image.new('RGBA', (total_cols * TILE, rows * TILE), (0, 0, 0, 255))
    for layer in ('ground', 'water', 'path'):
        for c, r, ti in cells[layer]:
            recon.paste(resolve(ids[ti]), (c * TILE, r * TILE))
    recon.save(os.path.join(out_dir, 'reconstruction_full.png'))
    recon.resize((1800, 240), Image.NEAREST).save(os.path.join(out_dir, 'reconstruction_preview.png'))

    total = sum(layer_counts.values())
    print(f"FULL MAP: {total_cols}x{rows} = {total} cells, unique ids={len(ids)}")
    print(f"layers: {layer_counts}, blocked={len(blocked)}")
    assert total == 27000, total
    assert layer_counts['water'] == 4960, layer_counts['water']
    assert len(blocked) == 5375, len(blocked)
    print("FULL MAP CONVERT OK — totals match BM audit (27000 / water 4960 / blocked 5375)")

if __name__ == '__main__':
    main()
