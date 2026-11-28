"""Read-only paper-doll fit export. PNGs are copied byte-identically, never edited."""
import argparse, hashlib, json, math, shutil
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect, locate

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Modular_Characters_20261107'
RUN=ROOT/'ClientGodot/assets/paperdoll_lab'
PREFIX='res://assets/paperdoll_lab/'
ORDER=['cape_back','body','outfit','boots','weapon_near','hand_near','eyes','hair_front','hat_front']
LEGACY=[
 ('HAIR_CHESTNUT','Tóc ngắn hạt dẻ','hair_front','head','HAIR',0),
 ('HAIR_TOPKNOT','Tóc búi huyền','hair_front','head','HAIR',1),
 ('EYES_JADE','Mắt ngọc','eyes','face','EYES',2),
 ('EYES_AMBER','Mắt hổ phách','eyes','face','EYES',3),
 ('BOOTS_BROWN','Hài nâu','boots','ground','BOOTS',8),
 ('BOOTS_SILVER','Hài bạc','boots','ground','BOOTS',9),
 ('HAT_CIRCLET','Trán quan ngọc','hat_front','head','HAT',12),
 ('HAT_TRAVELLER','Nón hành lữ','hat_front','head','HAT',13),
 ('CAPE_JADE','Choàng ngọc','cape_back','chest','CAPE',14),
 ('CAPE_INDIGO','Choàng chàm','cape_back','chest','CAPE',15)]
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def save(path,data,check):
 text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 if check:assert path.read_text(encoding='utf8')==text,'stale export: '+str(path)
 else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf8')
def rect(f):
 x,y,_,_=f['rect'];l,t,r,b=f['bounds'];return [x+l,y+t,r-l,b-t]
def copy(relative,name,check):
 src=ART/relative;target=RUN/name
 if check:assert target.read_bytes()==src.read_bytes(),'PNG differs: '+name
 else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 return dict(file=PREFIX+name,sha256=sha(src.read_bytes()))
def static_parts(path,columns,rows):
 with Image.open(path) as im:
  assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
  w,h=im.size;mask=im.getchannel('A').point(lambda v:255 if v>=200 else 0);pixels=mask.load()
  xx=[sum(bool(pixels[x,y]) for y in range(h)) for x in range(w)]
  yy=[sum(bool(pixels[x,y]) for x in range(w)) for y in range(h)]
  cols=locate(xx,columns,max(2,w//100));rr=locate(yy,rows,max(2,h//120))
  assert len(cols)==columns and len(rr)==rows,'static atlas layout mismatch'
  edges=lambda groups,end:[0]+[round((a[1]+b[0])/2) for a,b in zip(groups,groups[1:])]+[end]
  xs,ys=edges(cols,w),edges(rr,h);frames=[]
  for row in range(rows):
   for col in range(columns):
    x,y,x1,y1=xs[col],ys[row],xs[col+1],ys[row+1];bb=mask.crop((x,y,x1,y1)).getbbox()
    assert bb and min(bb[0],bb[1],x1-x-bb[2],y1-y-bb[3])>=2,'clipped/empty part'
    frames.append(dict(rect=[x,y,x1-x,y1-y],bounds=list(bb)))
  return frames,[w,h]
def main(check=False):
 bodies=[];sources=[];parts=[]
 for sex in ['male','female']:
  source='Corrections_20261110/male_base_v2.png' if sex=='male' else 'Sheets/body_human_female_idle_s_v1.png'
  actual=inspect(dict(id='body_'+sex,source=source,columns=4,rows=4,direction='S'),ART)
  tex=copy(source,sex+'_idle_s.png',check);sources.append(tex);frames=[]
  for f in actual['directions'][0]['frames']:
   region=rect(f);l,t,_,_=f['bounds'];px,py=f['pivot']
   offset=[48-round((px-l)/6),72-math.ceil((py-t)/6)];top=offset[1]
   anchors=dict(canvas=[0,0],ground=[48,72],head=[48,top+1],face=[48,top+10],
                chest=[48,top+16],hip=[48,top+26],hand_near=[58,top+26])
   # Exact source-region copy for foreground hand; align crop to the same 6-pixel source grid.
   hx=region[0]+round((px+f['rect'][0]+(region[2]*.30)-region[0])/6)*6
   hy=region[1]+round((py+f['rect'][1]-72-region[1])/6)*6
   hand_region=[hx,hy,30,30];hand_offset=[offset[0]+(hx-region[0])//6,offset[1]+(hy-region[1])//6]
   assert hx>=0 and hy>=0 and hx+30<=actual['imageSize'][0] and hy+30<=actual['imageSize'][1], 'hand source rect outside PNG'
   assert all(0<=v<=91 for v in hand_offset), 'hand offset mixed source-cell and atlas coordinates'
   anchors['hand_near']=[hand_offset[0]+3,hand_offset[1]+3]
   guide=dict(region=region,offset=offset,anchors=anchors,paintOrder=ORDER,
              handRegion=hand_region,handOffset=hand_offset)
   frames.append(dict(**guide,fingerprint=sha(canonical(dict(sourceSha256=tex['sha256'],**guide)))))
  bodies.append(dict(id='MK_'+('M' if sex=='male' else 'F'),name='Minh Kiếm · '+('Nam' if sex=='male' else 'Nữ'),
                     rigId='RIG_HUMAN_'+('M' if sex=='male' else 'F')+'_V1',texture=tex['file'],sourcePixelsPerUnit=6,frames=frames))
 old=inspect(dict(id='mk_s_parts_v1',source='Wardrobe_Study/mk_s_parts_v1.png',columns=4,rows=4,direction='S'),ART)
 tex=copy('Wardrobe_Study/mk_s_parts_v1.png','mk_s_parts_v1.png',check);sources.append(tex)
 def part(id_,name,slot,anchor,category,region,texture,ppu,offset,rig=None,transform=None):
  parts.append(dict(id=id_,name=name,slot=slot,anchor=anchor,category=category,region=region,offset=offset,
   texture=texture,sourcePixelsPerUnit=ppu,headCoverClipTopPixels=(54 if id_=='HAIR_TOPKNOT' else 18 if id_=='HAIR_CHESTNUT' else 0),hides=[],uniqueSourceImages=1,approved=False,rigId=rig,
   transform=transform or dict(pivotX=0,pivotY=0,degrees=0,scale=1,flipH=False,flipV=False)))
 for id_,name,slot,anchor,cat,index in LEGACY:
  r=rect(old['directions'][0]['frames'][index]);off=[-round(r[2]/24),0]
  if slot=='hair_front':off[1]=-5 if id_=='HAIR_TOPKNOT' else -1
  elif slot=='hat_front':off[1]=4 if id_=='HAT_CIRCLET' else -3
  elif slot=='boots':off[1]=-math.ceil(r[3]/12)
  elif slot=='cape_back':off[1]=-2
  part(id_,name,slot,anchor,cat,r,tex['file'],12,off)
 new_frames,size=static_parts(ART/'Corrections_20261110/outfits_swords_v2.png',4,2)
 tex=copy('Corrections_20261110/outfits_swords_v2.png','outfits_swords_v2.png',check);sources.append(tex)
 for i,(gender,palette) in enumerate([('M','IVORY'),('M','INDIGO'),('F','IVORY'),('F','INDIGO')]):
  r=rect(new_frames[i])
  part('OUTFIT_'+palette+'_'+gender,'Bộ giao lĩnh '+('ngà' if palette=='IVORY' else 'chàm'),
       'outfit','chest','OUTFIT',r,tex['file'],16,[-round(r[2]/32),-1],'RIG_HUMAN_'+gender+'_V1')
 for i,(palette,direction) in enumerate([('STEEL','LEFT'),('JADE','LEFT'),('STEEL','RIGHT'),('JADE','RIGHT')],4):
  r=rect(new_frames[i]);pivot_x=(r[2]-30 if direction=='LEFT' else 30)/16
  part('JIAN_'+palette+'_'+direction,('Kiếm thép' if palette=='STEEL' else 'Kiếm ngọc')+' · chéo '+('trái' if direction=='LEFT' else 'phải'),
       'weapon_near','hand_near','WEAPON',r,tex['file'],16,[0,0],transform=dict(pivotX=pivot_x,pivotY=30/16,degrees=0,scale=.75,flipH=False,flipV=False))
 cat=dict(schemaVersion=2,scope='FIT_LAB_ONLY',productionApproved=False,canvas=[96,96],origin=[48,72],
          direction='S',clip='idle',seconds=1.2,frameCount=16,sources=sources,bodies=bodies,parts=parts,
          outfitVisualOnly=True,equipmentSlotsUnchanged=True,ownerRejectedLegacyPng=True,
          limitations=['S/idle candidate only. Static outfit is one connected shirt/trouser visual, not equipment changes.',
                       'Foreground hand is an exact source-region redraw; master skin passes still need native authoring.',
                       'Transforms and source calibration are review-only. 16 placements are not 16 garment artworks.'])
 cat['catalogueFingerprint']=sha(canonical(cat));save(RUN/'catalog.json',cat,check)
 save(ART/'Corrections_20261110/inspection.json',dict(size=size,staticParts=8,productionApproved=False,
      sourceSha256=tex['sha256'],outfits=4,diagonalSwords=4,maleBaseSourceSha256=sources[0]['sha256']),check)
 print(json.dumps(dict(scope='FIT_LAB_ONLY',bodies=2,parts=len(parts),outfitVariants=4,diagonalSwords=4,productionApproved=False)))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');main(parser.parse_args().check)
