"""Read-only inspection and original-byte copy for single-pose style masters."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Restored_Pixel_Style_20261110'
RUN=ROOT/'ClientGodot/assets/paperdoll_style_v3'
NAMES={'body_base_mf_v3':'Base nam/nữ','outfit_ivory_mf_v3':'Bộ trang phục theo base','appearance_ivory_mf_v3':'Mẫu diện mạo hoàn chỉnh'}
def main(check=False):
 records=json.loads((ART/'generation_records.json').read_text(encoding='utf8'));entries=[]
 for r in records:
  source=ART/r['source'];data=source.read_bytes()
  with Image.open(source) as im:
   assert im.mode=='RGBA','source must retain alpha'
   alpha=im.getchannel('A');assert alpha.getextrema()[0]==0,'source has no transparency'
   entry=dict(id=r['id'],name=NAMES[r['id']],file='res://assets/paperdoll_style_v3/'+source.name,
     sha256=hashlib.sha256(data).hexdigest(),size=list(im.size),alphaBounds=list(alpha.point(lambda x:255 if x>=200 else 0).getbbox()),
     posesPerActor=1,actors=2,direction='S',layerPackReady=False,animationReady=False,productionApproved=False)
  target=RUN/source.name
  if check:assert target.read_bytes()==data,'preview PNG differs from original'
  else:RUN.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  entries.append(entry)
 result=dict(schemaVersion=1,scope='STYLE_AND_PROPORTION_REVIEW_ONLY',preferredStyle='RESTORED_ILLUSTRATIVE_PIXEL_ART',
   rejectedStyle='PROCEDURAL_BLOCK_MASTER_V2',entries=entries,productionApproved=False,
   warning='Whole artwork masters only. Generated in sequence from the same base; no pixel-exact layer-fit or animation acceptance is claimed.')
 def save(p,v):
  text=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
  if check:assert p.read_text(encoding='utf8')==text,'stale style master metadata'
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
 save(RUN/'catalog.json',result);save(ART/'inspection.json',result)
 print(json.dumps(dict(masters=len(entries),posesPerActor=1,style=result['preferredStyle'],productionApproved=False)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)
