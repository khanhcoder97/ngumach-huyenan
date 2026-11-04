"""Inspect atlas pixels without editing bitmaps. Writes explicit frame/pivot metadata."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"Art_Source/Combat_Visuals_20261105"
RUN=ROOT/"ClientGodot/assets/combat_v1"
def bounds(im,rect):
    x,y,w,h=rect
    return im.getchannel("A").crop((x,y,x+w,y+h)).point(lambda a:255 if a>128 else 0).getbbox()
def frames(path):
    im=Image.open(path); assert im.size==(1536,1024) and im.mode=="RGBA"
    alpha=im.getchannel("A").point(lambda a:255 if a>128 else 0)
    result=[]
    for row in range(4):
        top=row*256
        band=alpha.crop((0,top,1536,top+256))
        projection=[band.crop((x,0,x+1,256)).getbbox() is not None for x in range(1536)]
        cuts=[0]
        for c in range(1,8):
            nominal=c*192; runs=[]; begin=None
            for x in range(nominal-48,nominal+49):
                if not projection[x] and begin is None:begin=x
                if projection[x] and begin is not None:
                    if x-begin>=2:runs.append((begin,x))
                    begin=None
            if begin is not None:runs.append((begin,nominal+49))
            assert runs,(path.name,row,c,"no separation; reject overlapping people")
            a,b=min(runs,key=lambda r:abs((r[0]+r[1])/2-nominal))
            cuts.append((a+b)//2)
        cuts.append(1536)
        for c in range(8):
            x0,x1=cuts[c:c+2];rect=[x0,top,x1-x0,256]
            content=bounds(im,rect);assert content,(row,c)
            assert content[0]>0 and content[2]<rect[2],(path.name,row,c,content,"clipped body")
            center=c*192+96
            boots=alpha.crop((center-42,top+180,center+42,top+256)).getbbox()
            assert boots,(row,c,"missing foot anchor")
            result.append(dict(direction=["N","NE","E","SE","S","SW","W","NW"][c],
                phase=row,rect=rect,pivot=[center-x0,180+boots[3]],contentBounds=list(content)))
    return result
def attack_frames(path):
    im=Image.open(path); assert im.size==(1536,1024) and im.mode=="RGBA"
    result=[]
    for phase in range(4):
        for direction in range(8):
            x,y=phase*384,direction*128
            rect=[x,y,384,128];bb=bounds(im,rect)
            assert bb and bb[0]>2 and bb[2]<382 and bb[1]>0 and bb[3]<128,(phase,direction,bb)
            a=im.getchannel("A").crop((x+154,y+80,x+230,y+128)).point(lambda v:255 if v>128 else 0).getbbox()
            assert a
            result.append(dict(direction=["N","NE","E","SE","S","SW","W","NW"][direction],
                phase=phase,rect=rect,pivot=[192,80+a[3]],contentBounds=list(bb)))
    return result

def inspect(write=False):
    records=[]
    mapping={"minh_kiem_walk.png":"Characters/minh_kiem_walk_v1.png",
             "minh_kiem_attack.png":"Characters/minh_kiem_attack_v2.png",
             "minh_kiem_vfx.png":"VFX/minh_kiem_vfx_v1.png",
             "ben_mua_questkit.png":"Characters/ben_mua_questkit_v1.png",
             "ben_mua_mobs.png":"Characters/ben_mua_mobs_v1.png",
             "ben_mua_nodes.png":"Nodes/ben_mua_nodes_v1.png",
             "minh_kiem_skill_icons.png":"UI/minh_kiem_skill_icons_v1.png"}
    for runtime,source in mapping.items():
        data=(RUN/runtime).read_bytes();assert data==(ART/source).read_bytes(),runtime
        with Image.open(RUN/runtime) as im:
            assert im.mode=="RGBA"
            records.append(dict(file=runtime,sha256=hashlib.sha256(data).hexdigest(),size=list(im.size)))
    walk=frames(RUN/"minh_kiem_walk.png");attack=attack_frames(RUN/"minh_kiem_attack.png")
    vfx=[]
    with Image.open(RUN/"minh_kiem_vfx.png") as im:
        assert im.size==(1254,1254)
        for row in range(6):
            clip=[]
            for c in range(6):
                rect=[c*209,row*209,209,209];bb=bounds(im,rect)
                assert bb and bb[0]>0 and bb[2]<209,(row,c,"clipped effect")
                clip.append(dict(rect=rect,pivot=[104.5,104.5]))
            vfx.append(clip)
    actors={}
    with Image.open(RUN/"ben_mua_questkit.png") as im:
        assert im.size==(1536,1024)
        for i,key in enumerate(["NPC_LYAN","NPC_TA_VAN_KHANH","NPC_MEDIC_BEN","PACKAGE","EQ-MK-CHEST-T1-R-COMMON","COIN"]):
            # Generated people are taller than the requested grid: keep whole bodies.
            top,h=(0,608) if i<3 else (608,416)
            rect=[i%3*512,top,512,h];bb=bounds(im,rect)
            assert bb and min(bb[0],bb[1],512-bb[2],h-bb[3])>8,(key,bb)
            actors[key]=dict(rect=rect,pivot=[(bb[0]+bb[2])/2,bb[3]],contentBounds=list(bb))
    mobs={}
    with Image.open(RUN/"ben_mua_mobs.png") as im:
        assert im.size==(1536,1024)
        for i,key in enumerate(["CARPLING_IDLE","CARPLING_ATTACK","CARPLING_DEAD","WATERROOT_IDLE","WATERROOT_ATTACK","WATERROOT_DEAD"]):
            rect=[i%3*512,i//3*512,512,512];bb=bounds(im,rect)
            assert bb and min(bb[0],bb[1],512-bb[2],512-bb[3])>2,(key,bb)
            mobs[key]=dict(rect=rect,pivot=[(bb[0]+bb[2])/2,bb[3]],contentBounds=list(bb))
    nodes={}
    with Image.open(RUN/"ben_mua_nodes.png") as im:
        assert im.size==(1536,1024)
        for i,key in enumerate(["ORE_01","ORE_02","HERB_01","WOOD_01","HERB_02","FRAGMENT"]):
            rect=[i%3*512,i//3*512,512,512];bb=bounds(im,rect)
            assert bb and min(bb[0],bb[1],512-bb[2],512-bb[3])>2,(key,bb)
            nodes[key]=dict(rect=rect,pivot=[(bb[0]+bb[2])/2,bb[3]],contentBounds=list(bb))
    icons=[]
    with Image.open(RUN/"minh_kiem_skill_icons.png") as im:
        assert im.size==(1536,1024)
        for i in range(6):
            rect=[i%3*512,i//3*512,512,512];bb=bounds(im,rect)
            assert bb and min(bb[0],bb[1],512-bb[2],512-bb[3])>2,(i,bb)
            icons.append(dict(skillId="SK-MK-0"+str(i+1),rect=rect,contentBounds=list(bb)))
    manifest=dict(schemaVersion=1,status="NATIVE_REVIEW_CANDIDATE",sourceBodyHeight=208,attackSourceBodyHeight=112,
        walk=walk,attack=attack,vfx=vfx,questKit=actors,mobs=mobs,nodes=nodes,uiIcons=icons,files=records)
    target=RUN/"manifest.json"
    if write:
        target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        (ART/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    else:assert json.loads(target.read_text(encoding="utf8"))==manifest,"stale metadata"
    print("COMBAT_ART PASS: 7 byte-identical source pairs,64 whole-body frames,36 VFX frames,6 quest sprites,6 mob poses,6 nodes,6 HUD icons")
    print("Structural result; gait/art quality still needs native visual review.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--write-manifest",action="store_true");inspect(p.parse_args().write_manifest)
