"""Read-only alpha/frame inspection. No bitmap editing or resampling."""
import argparse,hashlib,json,statistics
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Motion_16F_20261106';RUN=ROOT/'ClientGodot/assets/motion16'

def grid(file,cols,rows):
    with Image.open(RUN/file) as im:
        assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0,(file,'no clear alpha')
        w,h=im.size;alpha=im.getchannel('A').point(lambda a:255 if a>=160 else 0)
        result=[];hashes=[]
        for row in range(rows):
            for col in range(cols):
                x,y,x1,y1=round(col*w/cols),round(row*h/rows),round((col+1)*w/cols),round((row+1)*h/rows)
                bb=alpha.crop((x,y,x1,y1)).getbbox();assert bb,(file,row,col,'empty')
                margin=min(bb[0],bb[1],x1-x-bb[2],y1-y-bb[3])
                assert margin>1,(file,row,col,bb,'clipped sprite')
                feet=alpha.crop((x+int((x1-x)*.3),y+int((y1-y)*.65),x+int((x1-x)*.7),y1)).getbbox();assert feet
                px=int((x1-x)*.3)+(feet[0]+feet[2])/2;py=int((y1-y)*.65)+feet[3]
                result.append(dict(file=file,rect=[x,y,x1-x,y1-y],pivot=[px,py],bounds=list(bb)))
                hashes.append(hashlib.sha256(im.crop((x,y,x1,y1)).tobytes()).hexdigest())
        assert len(set(hashes))==cols*rows,(file,'duplicate image cells')
        return result

def build():
    clips={};files=[]
    records=json.loads((ART/'generation_records.json').read_text(encoding='utf-8'))
    assert len(records)==20 and {p.name for p in RUN.glob('*.png')}=={r['runtime'] for r in records},'unexpected runtime sheet set'
    for r in records:
        data=(RUN/r['runtime']).read_bytes();assert data==(ART/r['source']).read_bytes()
        files.append(dict(file=r['runtime'],source=r['source'],sha256=hashlib.sha256(data).hexdigest()))
    for action,duration in [('idle',1.6),('walk',.8),('attack',.6),('cast',.64)]:
        clips[action]=[]
        for d in range(8):
            direction=['n','ne','e','se','s','se','e','ne'][d];name=action+'_'+direction
            frames=grid(name+'.png',4,4)
            for f in frames:f['flip']=d>=5
            height=frames[0]['bounds'][3]-frames[0]['bounds'][1]
            clips[action].append(dict(duration=duration,sourceHeight=height,frames=frames))
    return dict(schemaVersion=1,framesPerDirection=16,directionOrder=['N','NE','E','SE','S','SW','W','NW'],
        sourceNote='Original generated frames. W/NW/SW action sheets mirror E/NE/SE at render time; all action sheets use the same declared mirroring metadata. No duplicate-four-frame expansion.',clips=clips,files=files)

def main(write):
    result=build();target=RUN/'manifest.json'
    if write:target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:assert json.loads(target.read_text(encoding='utf-8'))==result,'stale manifest'
    print('MOTION16 PASS:20 source/runtime byte pairs,4 actions x8 directions x16 frame references;3 mirrored directions declared')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-manifest',action='store_true');main(p.parse_args().write_manifest)
