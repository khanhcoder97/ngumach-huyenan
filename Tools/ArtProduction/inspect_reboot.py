"""Read-only PNG inspection; never resizes, masks or writes bitmap pixels."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Art_Source/Visual_Reboot_20261104"
RUNTIME = ROOT / "ClientGodot/assets/reboot"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(write_manifest=False):
    files = []
    for path in sorted(SOURCE.rglob("*.png")):
        with Image.open(path) as image:
            files.append(dict(path=path.relative_to(SOURCE).as_posix(),
                dimensions=list(image.size), mode=image.mode, sha256=sha(path),
                status="CANDIDATE"))
    selected = {
        "hero_idle_body.png": SOURCE/"Characters/MinhKiem/idle_body_8dir_candidate_v2.png",
        "terrain.png": SOURCE/"Terrain/terrain_24_candidate_v2.png",
        "props.png": SOURCE/"Props/props_6_topdown_candidate_v2.png",
    }
    records = []
    for name, source in selected.items():
        runtime = RUNTIME/name
        assert sha(source) == sha(runtime), f"runtime bytes differ: {name}"
        with Image.open(runtime) as image:
            records.append(dict(path=name,sha256=sha(runtime),dimensions=list(image.size),mode=image.mode))
    frames = []
    with Image.open(RUNTIME/"hero_idle_body.png") as image:
        assert image.mode == "RGBA"
        for i, direction in enumerate(["N","NE","E","SE","S","SW","W","NW"]):
            x0, x1 = round(i%4*image.width/4), round((i%4+1)*image.width/4)
            y0, y1 = round(i//4*image.height/2), round((i//4+1)*image.height/2)
            # Read-only threshold locates the substantial body, not low-alpha fringes.
            bounds = image.getchannel("A").crop((x0,y0,x1,y1)).point(
                lambda value: 255 if value > 128 else 0).getbbox()
            assert bounds and min(bounds[0],bounds[1],x1-x0-bounds[2],y1-y0-bounds[3]) >= 20
            frames.append(dict(direction=direction,rect=[x0,y0,x1-x0,y1-y0],
                pivot=[(bounds[0]+bounds[2])/2,bounds[3]],alphaBounds=list(bounds)))
    for name in ["terrain.png","props.png"]:
        with Image.open(RUNTIME/name) as image:
            assert image.size == (1536,1024), f"grid mismatch: {name}"
            if name == "props.png":
                assert image.mode == "RGBA"
                assert image.getchannel("A").getextrema()[0] == 0
    manifest = dict(schemaVersion=1,stage="STRUCTURE_CHECKED_NOT_FINAL_ART",
        mapId="ART_BM_STAGING_A1",projection="orthographic_2d_topdown",
        pixelsPerWU=20,defaultVisibleWU=[64,36],heroFrames=frames,files=records)
    if write_manifest:
        (RUNTIME/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (SOURCE/"source_inventory.json").write_text(json.dumps(
            dict(schemaVersion=1,generator="built-in image_gen",files=files),
            ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        saved = json.loads((RUNTIME/"manifest.json").read_text(encoding="utf-8"))
        assert saved == manifest, "manifest stale; regenerate explicitly"
    print(f"ART_STRUCTURE PASS: {len(files)} source PNGs, 3 byte-identical runtime assets, 8 padded frame rects")
    print("Visual quality, seam continuity and animation completeness are NOT implied by this result.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest",action="store_true")
    inspect(parser.parse_args().write_manifest)
