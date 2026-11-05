"""Export shared authoritative collision from authored map; does not edit bitmaps."""
import argparse, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LAYOUT=ROOT/'ClientGodot/assets/ben_mua_v3/layout.json'
CLIENT=ROOT/'ClientGodot/assets/ben_mua_v3/terrain.json'
SERVER=ROOT/'Implementation/Content/Maps/BenMua/terrain.json'

def smooth(points):
    out=[]
    for i in range(len(points)-1):
        p0,p1,p2,p3=points[max(i-1,0)],points[i],points[i+1],points[min(i+2,len(points)-1)]
        count=max(2,math.floor(math.dist(p1,p2)/12))
        for k in range(count):
            t=k/count;t2=t*t;t3=t2*t
            out.append([round(.5*(2*p1[a]+(-p0[a]+p2[a])*t+(2*p0[a]-5*p1[a]+4*p2[a]-p3[a])*t2+(-p0[a]+3*p1[a]-3*p2[a]+p3[a])*t3),4) for a in range(2)])
    return out+[points[-1]]

def build():
    layout=json.loads(LAYOUT.read_text(encoding='utf-8'))
    ox,oy=layout['districtOrigin']
    def point(p):return [round((ox+p[0]-560)/20,6),round((896-oy-p[1])/20,6)]
    def rect(x,y,w,h):
        p=point([x,y+h]);return [p[0],p[1],round(w/20,6),round(h/20,6)]
    solids=[];decks=[]
    for p in layout['placements']:
        x,y=p['at'];w=p['width']
        if p.get('solid') or p.get('pier'):
            a,b,c,d=p.get('footprint',[-w*.34,-w*.24,w*.68,w*.22])
            (decks if p.get('pier') else solids).append({'id':p['id'],'rect':rect(x+a,y+b,c,d)})
        if p['asset']=='garden':
            solids.append({'id':p['id']+'_RAISED_BED','rect':rect(x-w*.43,y-w*.52,w*.86,w*.52)})
        elif p['asset']=='jars':
            solids.append({'id':p['id']+'_BASE','rect':rect(x-w*.35,y-w*.2,w*.7,w*.2)})
        elif p['asset']=='fence':
            solids.append({'id':p['id']+'_RAIL','rect':rect(x-w*.45,y-4,w*.9,7)})
        if p['asset'] in ('banyan','canopy','willow','bamboo'):
            solids.append({'id':p['id']+'_TRUNK','rect':rect(x-5,y-8,10,8)})
    upper_pixels=smooth(layout['river']['upper']);lower_pixels=smooth(layout['river']['lower'])
    def at_bank(bank,x):
        x-=ox
        for a,b in zip(bank,bank[1:]):
            if b[0]>=x:return oy+a[1]+(b[1]-a[1])*((x-a[0])/max(1,b[0]-a[0]))
        return oy+bank[-1][1]
    for side,bank in enumerate([upper_pixels,lower_pixels]):
        for i in range(51):
            x=20+i*50+5*math.sin(i*2.4+side);y=at_bank(bank,x)+2*math.sin(i*1.7)+(5 if side==0 else -2)
            q=[(x-560)/20,(896-y)/20]
            if any(r['rect'][0]-1.35<=q[0]<=r['rect'][0]+r['rect'][2]+1.35 and r['rect'][1]-1.35<=q[1]<=r['rect'][1]+r['rect'][3]+1.35 for r in decks):continue
            width=57+(i*13%43)
            solids.append({'id':'ART_SHORE_%s_%s'%(side,i),'rect':rect(x-ox-width*.3,y-oy-width*.1,width*.6,width*.15)})
    upper=[point(p) for p in upper_pixels]
    lower=[point(p) for p in lower_pixels]
    return dict(schemaVersion=1,mapId='MAP_BEN_MUA',sourceSha256=hashlib.sha256(json.dumps(layout,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),
        coordinateSystem='CANONICAL_XY_WU',renderOrigin=[560,896],pixelsPerWU=20,bounds=[0,-12,360,72],
        upper=upper,lower=lower,water=upper+list(reversed(lower)),solids=solids,decks=decks)

def main(check):
    data=json.dumps(build(),ensure_ascii=False,indent=2)+'\n'
    if check:
        assert CLIENT.read_text(encoding='utf-8')==data,'stale client collision'
        assert SERVER.read_text(encoding='utf-8')==data,'stale server collision'
    else:
        CLIENT.write_text(data,encoding='utf-8');SERVER.parent.mkdir(parents=True,exist_ok=True);SERVER.write_text(data,encoding='utf-8')
    record=build();print('BEN_MUA_TERRAIN PASS: shared water polygon, %s solids, %s decks'%(len(record['solids']),len(record['decks'])))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)
