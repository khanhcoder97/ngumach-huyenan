#!/usr/bin/env python3
"""OPC-08: Synthetic sprite sheet fixtures for testing Asset Preview server."""

import struct
import zlib
from pathlib import Path


def encode_png(width: int, height: int, data: list) -> bytes:
    """Encode raw RGBA pixel data to PNG using standard library only."""
    
    def make_chunk(chunk_type: bytes, payload: bytes) -> bytes:
        crc = struct.pack(">I", zlib.crc32(chunk_type + payload) & 0xffffffff)
        return struct.pack(">I", len(payload)) + chunk_type + payload + crc
    
    # IHDR
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    chunks = [make_chunk(b"IHDR", ihdr)]
    
    # IDAT - compress each scanline
    def process_scanline(row: list) -> bytes:
        # Add filter byte (0 = none)
        flat = [b"\x00"]
        for px in row:
            if isinstance(px, (list, tuple)):
                flat.extend([bytes(px)])
            else:
                raise ValueError(f"Invalid pixel: {px}")
        return zlib.compress(b"".join(flat))
    
    rows = [data[y] for y in range(height)]
    idat_data = b"".join(process_scanline(row) for row in rows)
    chunks.append(make_chunk(b"IDAT", idat_data))
    
    # IEND
    chunks.append(make_chunk(b"IEND", b""))
    
    return b"\x89PNG\r\n\x1a\n" + b"".join(chunks)


def create_sprite_fixture(output_dir: Path, name: str, 
                          frame_w: int, frame_h: int,
                          dirs: int = 8, frames: int = 6, fps: int = 8):
    """Create directional actor sprite sheet."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cols, rows = dirs, frames
    total_w, total_h = cols * frame_w, rows * frame_h
    
    # Create pixel grid
    pixels = []
    for y in range(total_h):
        row_pixels = []
        for x in range(total_w):
            r, g, b, a = 50, 80, 100, 255
            
            # Direction indicator (colored square)
            cx = (x // frame_w) * frame_w + frame_w // 2
            cy = (y // frame_h) * frame_h + frame_h // 2
            size = min(frame_w, frame_h) // 4
            dx, dy = x - cx, y - cy
            
            if abs(dx) < size and abs(dy) < size:
                colors = [(255,100,100),(255,150,100),(255,255,100),
                         (150,255,100),(100,255,100),(100,255,150),
                         (100,150,255),(100,100,255)]
                dir_idx = (y // frame_h) % 8
                r, g, b = colors[dir_idx]
            
            row_pixels.append((r, g, b, a))
        pixels.append(row_pixels)
    
    png_data = encode_png(total_w, total_h, pixels)
    png_path = output_dir / f"{name}.png"
    png_path.write_bytes(png_data)
    print(f"✓ {png_path} ({total_w}×{total_h})")
    
    # Write Unity .meta
    meta_content = f'''fileFormatVersion: 2
guid: 00000000000000000000000000000000
TextureImporter:
  spritePixelsToUnits: 20
  spriteMode: 2
  enableMipMap: 0
  filterMode: 0
  spriteSheet:
    sprites:
'''
    for dy in range(rows):
        for fx in range(frames):
            rect_x = fx * frame_w
            rect_y = dy * frame_h
            meta_content += f'''    - serializedVersion: 2
      name: {name}_d{dy}_f{fx}
      rect: {{x: {rect_x}, y: {rect_y}, width: {frame_w}, height: {frame_h}}}
      pivot: {{x: 0.5, y: 0}}
'''
    
    meta_path = output_dir / f"{name}.png.meta"
    meta_path.write_text(meta_content, encoding='utf-8-sig')
    print(f"  → {meta_path}")
    
    return {
        "id": f"FIX_{name.upper()}",
        "isDirectional": True,
        "framesPerDirection": frames,
        "totalSprites": frames * dirs
    }


def main():
    base = Path("Tools/AssetPreview/fixtures")
    base.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("OPC-08: Creating Sprite Fixtures")
    print("="*60)
    
    result = create_sprite_fixture(base, "actor_8dir_test", 48, 64, 8, 6, 8)
    
    print(f"\nResult: {result['id']} - {result['totalSprites']} sprites @ {result['animationFps'] if 'animationFps' in result else 8}fps")
    print("="*60)
    print("Test with: python Tools/AssetPreview/server.py --root .")
    print("="*60)


if __name__ == "__main__":
    main()
