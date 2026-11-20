"""Read-only candidate geometry/alpha evidence. Never edits pixels or approves animation."""
import argparse,hashlib,json
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def preflight(batch,allow_partial=False):
    assert batch.isalnum();manifest=read(ART/('Candidates_'+batch)/'candidate_manifest.json')
    assert manifest['selected']==len(manifest['records']) and manifest['remainingSourcePages']==manifest['expectedSourcePages']-manifest['selected']
    assert allow_partial or manifest['remainingSourcePages']==0,'Generation incomplete; use --allow-partial for a labelled pilot'
    baseline={f:sha(ART/f) for f in ('generation_records.json','structure_report.json','visual_review.json')};entries=[]
    for record in manifest['records']:
        path=ART/record['source'];original=sha(path);assert original==record['sourceSha256']
        with Image.open(path) as image:
            assert image.mode=='RGBA';hist=image.getchannel('A').histogram()
            entry=dict(id=record['id'],source=record['source'],sourceSha256=original,imageSize=list(image.size),alphaZeroPixels=hist[0],softAlphaPixels=sum(hist[1:200]),solidAlphaPixels=sum(hist[200:]),cornerAlpha=[image.getpixel(p)[3] for p in ((0,0),(image.width-1,0),(0,image.height-1),(image.width-1,image.height-1))])
        try:
            page=inspect(record);entry.update(geometryReady=True,sourceFrames=page['sourceFrames'])
        except (AssertionError,OSError) as error:entry.update(geometryReady=False,reason=str(error))
        assert sha(path)==original;entries.append(entry)
    assert baseline=={f:sha(ART/f) for f in baseline},'Preflight may not change catalogue or approvals'
    output=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);output.mkdir(parents=True,exist_ok=True)
    result=dict(batch=batch,selected=len(entries),expected=manifest['expectedSourcePages'],pilot=manifest['remainingSourcePages']>0,geometryReady=sum(e['geometryReady'] for e in entries),catalogueUnchanged=True,rasterModified=False,scope='READ_ONLY_GEOMETRY_ALPHA_NOT_VISUAL_OR_NATIVE_ACCEPTANCE',entries=entries)
    (output/('preflight_pilot.json' if result['pilot'] else 'preflight.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='entries'}))
    for e in entries:
        if not e['geometryReady']:print(json.dumps(e))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--allow-partial',action='store_true');args=parser.parse_args();preflight(args.batch,args.allow_partial)
