"""Read-only independent .aseprite source validator; does not create/edit bitmap data."""
import argparse, hashlib, json, re, struct, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Registered_Master_20261110'
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(path,expected):
 data=path.read_bytes()
 size,magic,frames,w,h,depth=struct.unpack_from('<IHHHHH',data)
 assert size==len(data) and magic==0xA5E0 and (frames,w,h,depth)==(16,96,96,32),'invalid ASE header'
 layers=[];references=[];unique={};position=128;tags=[]
 for frame in range(frames):
  start=position;length,magic,old_count,duration,reserved,count=struct.unpack_from('<IHHHHI',data,start)
  assert magic==0xF1FA and duration==100 and start+length<=len(data)
  count=count or old_count;position+=16;cels={}
  for _ in range(count):
   length_chunk,kind=struct.unpack_from('<IH',data,position)
   assert length_chunk>=6 and position+length_chunk<=start+length
   chunk=data[position+6:position+length_chunk]
   if kind==0x2004:
    assert frame==0
    flags,layer_type,level,dw,dh,blend,opacity=struct.unpack_from('<HHHHHHB',chunk)
    name_size=struct.unpack_from('<H',chunk,16)[0];name=chunk[18:18+name_size].decode('utf8')
    assert layer_type==0 and level==0 and blend==0 and opacity==255
    layers.append(dict(name=name,visible=bool(flags&1)))
   elif kind==0x2005:
    index,x,y,opacity,cel_type,order=struct.unpack_from('<HhhBHh',chunk)
    cw,ch=struct.unpack_from('<HH',chunk,16)
    assert index<len(layers) and (x,y,opacity,cel_type,order,cw,ch)==(0,0,255,2,0,96,96)
    stream=zlib.decompressobj();rgba=stream.decompress(chunk[20:],cw*ch*4+1)
    assert len(rgba)==cw*ch*4 and stream.eof and set(rgba[3::4])<={0,255}
    assert index not in cels
    cels[index]=rgba;unique.setdefault(layers[index]['name'],set()).add(sha(rgba))
   elif kind==0x2018:
    assert struct.unpack_from('<H',chunk)[0]==1
    first,last=struct.unpack_from('<HH',chunk,10);assert (first,last)==(0,15)
    tags.append('IDLE_S_16_MASTER')
   else:raise AssertionError('unexpected source chunk')
   position+=length_chunk
  assert position==start+length and len(cels)==len(layers)
  result=bytearray(w*h*4)
  for i,layer in enumerate(layers):
   if not layer['visible']:continue
   source=cels[i]
   for pixel in range(w*h):
    at=pixel*4
    if source[at+3]:result[at:at+4]=source[at:at+4]
  references.append(sha(result))
 assert position==len(data) and len(layers)==20 and tags==['IDLE_S_16_MASTER']
 assert references==expected['referenceRgbaSha256'],'source flatten differs from master'
 assert len(set(references))==16,'duplicate composite poses'
 assert unique['BODY_BASE'] and len(unique['BODY_BASE'])==16
 assert len(unique['OUTFIT_IVORY'])==16 and len(unique['OUTFIT_INDIGO'])==16,'outfit does not follow all poses'
 assert [l['name'] for l in layers if l['visible']]==expected['visibleLayers']
 return dict(file=path.name,frames=16,layers=20,celCount=16*20,uniqueBodyPoses=16,
             uniqueIvoryOutfitPoses=16,uniqueIndigoOutfitPoses=16,
             sourceFlattenMatches=True,productionApproved=False)
def main(check=False):
 manifest=json.loads((ART/'source_manifest.json').read_text(encoding='utf8'))
 renderer=(ROOT/'ClientGodot/scripts/RegisteredPaperDollMaster.cs').read_text(encoding='utf8')
 definition=(ROOT/'ClientGodot/assets/paperdoll_master/master.json').read_text(encoding='utf8')
 algorithm=re.search(r'const string Algorithm="([^"]+)"',renderer)[1]
 assert sha((renderer+'|'+algorithm+'|'+definition).encode())==manifest['sourceFingerprint'],'source export stale'
 result=[]
 for item in manifest['files']:
  path=ART/item['file'];assert sha(path.read_bytes())==item['sha256'],'ASE bytes changed without review'
  result.append(parse(path,item))
 report=dict(kind='REGISTERED_LAYER_SOURCE_STRUCTURE_NOT_ART_ACCEPTANCE',files=result,approvedNativeGameplayClips=0,
             note='Checks native layer/frame source and lossless reference reconstruction; not aesthetic approval, eight-direction completeness or gameplay.')
 text=json.dumps(report,ensure_ascii=False,indent=2)+'\n';target=ART/'structure_report.json'
 if check:assert target.read_text(encoding='utf8')==text,'stale native source report'
 else:target.write_text(text,encoding='utf8')
 print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)
