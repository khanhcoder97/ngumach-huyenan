"""Read-only inspection and metadata authoring; this tool never writes PNG pixels."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"Art_Source/BenMua_Concept_Rebuild_20261105"
RUNTIME=ROOT/"ClientGodot/assets/ben_mua_v3"

def inspect(write=False):
    definitions=json.loads((RUNTIME/"asset_definitions.json").read_text(encoding="utf-8"))
    assets={}
    for key,(file,rect) in definitions.items():
        p=RUNTIME/file
        with Image.open(p) as im:
            x,y,w,h=rect
            assert im.mode=="RGBA",key
            assert x>=0 and y>=0 and x+w<=im.width and y+h<=im.height,key
            alpha=im.getchannel("A").crop((x,y,x+w,y+h))
            bounds=alpha.point(lambda v:255 if v>128 else 0).getbbox()
            assert bounds,key
            # Explicit regions can have unequal width: never assume every atlas is a regular grid.
            assert bounds[0]>2 and bounds[1]>2 and bounds[2]<w-2 and bounds[3]<h-2,(key,bounds,rect)
            assets[key]=dict(file=file,rect=rect,contentBounds=list(bounds),
                pivot=[(bounds[0]+bounds[2])/2,bounds[3]])
    files=[]
    for p in sorted(ART.glob("*.png")):
        runtime=RUNTIME/p.name
        assert p.read_bytes()==runtime.read_bytes(),p.name
        with Image.open(p) as im:
            assert im.size==(1536,1024),p.name
            if p.name!="ground.png":
                assert im.mode=="RGBA"
                alpha=im.getchannel("A").histogram()
                assert sum(alpha[:8])>im.width*im.height*.25,p.name
            files.append(dict(file=p.name,size=list(im.size),mode=im.mode,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    layout=json.loads((RUNTIME/"layout.json").read_text(encoding="utf-8"))
    ids=[p["id"] for p in layout["placements"]]
    assert len(ids)==len(set(ids))
    assert all(p["asset"] in assets for p in layout["placements"])
    assert layout["canonicalGameMapUnchanged"] is True
    manifest=dict(schemaVersion=1,generator="built-in image_gen",stage="STRUCTURE_CHECKED_VISUAL_REVIEW_REQUIRED",
        assets=assets,files=files)
    path=RUNTIME/"asset_manifest.json"
    if write:
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (ART/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        assert manifest==json.loads(path.read_text(encoding="utf-8")),"Manifest stale"
    print(f"ENV_STRUCTURE PASS: {len(files)} PNG byte pairs, {len(assets)} padded regions, {len(ids)} unique placements")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--write-manifest",action="store_true")
    inspect(parser.parse_args().write_manifest)
