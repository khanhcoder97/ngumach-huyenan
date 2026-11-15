"""Portable native review bundles for whole-body candidates; catalogue/PNGs stay unchanged."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect,binary_projection
from calibrate_anh_dao_mobility import head_landmark
from calibrate_huyen_but_20261114f import gutter_edges
from calibrate_huyen_but_20261114g import boot_root

def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(batch,expected):
    assert batch.isalnum() and expected>0
    manifest=read(ART/('Candidates_'+batch)/'candidate_manifest.json')
    assert manifest['selected']==expected and manifest['remainingSourcePages']==0
    output=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch)
    output.mkdir(parents=True,exist_ok=True);plan=[]
    before={name:sha(ART/name) for name in ('generation_records.json','structure_report.json','visual_review.json')}
    for original in manifest['records']:
        record=dict(original);assert record['id'].startswith('class_huyen_but_') and record['direction'] in ('N','NE','E','SE','S')
        source=ART/record['source'];original_hash=sha(source)
        assert original_hash==record['sourceSha256']
        with Image.open(source) as image:
            try:page=inspect(record)
            except AssertionError as error:
                assert 'clipped/overlapping' in str(error),str(error)
                x,y=binary_projection(image.getchannel('A').point(lambda a:255 if a>=200 else 0))
                record['gridEdges']=dict(columns=gutter_edges(x),rows=gutter_edges(y));page=inspect(record)
            frames=page['directions'][0]['frames'];assert len(frames)==16
            pivots=[];heads=[];neutral=None;offset=None;moving='_run_' in record['id']
            for frame in frames:
                x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,frame['bounds']);heads.append(head)
                boot_x,ground,low=boot_root(region,head,frame['bounds'][3]-head['top'] if neutral is None else neutral,moving)
                if neutral is None:neutral=ground-head['top'];offset=boot_x-head['centerX']
                pivots.append([head['centerX']+offset if moving else boot_x,ground])
        record.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral)
        page=inspect(record);assert page['sha256']==original_hash
        bundle=output/'Candidate_Studio'/record['id'];textures=bundle/'textures';textures.mkdir(parents=True,exist_ok=True)
        dest=textures/(original_hash+'.png')
        if dest.exists():assert sha(dest)==original_hash
        else:shutil.copyfile(source,dest)
        assert sha(dest)==original_hash
        keys=[]
        for index,frame in enumerate(page['directions'][0]['frames']):
            keys.append(dict(Frame=index,Pose=dict(X=0,Y=0,PivotX=frame['pivot'][0],PivotY=frame['pivot'][1],ScaleX=140/neutral,ScaleY=140/neutral,Angle=0,Alpha=1,SourceFrame=index)))
        layer=dict(Id='sprite',Name=record['id'],Kind='sprite',Texture='textures/'+dest.name,Regions=[f['rect'] for f in frames],Rest=keys[0]['Pose'],Z=0,Visible=True)
        clip=dict(Name=record['id'],Direction=record['direction'],Loop=moving,SourceNote='CANDIDATE_PENDING_NATIVE_REVIEW_NOT_CATALOGUE_APPROVAL',DurationsMs=record['sourceFrameDurationsMs'],Tracks=[dict(LayerId='sprite',Interpolate=False,Keys=keys)],Markers=[])
        project=bundle/'project.json'
        save(project,dict(SchemaVersion=1,Scope='PRESENTATION_AUTHORING_ONLY',Name=record['id'],ProductionApproved=False,Layers=[layer],Sockets=[],Clips=[clip]))
        save(bundle/'source_registration.json',dict(record=record,page=page,headLandmarks=heads,originalPngUnchanged=True,productionApproved=False))
        plan.append(dict(id=record['id'],project=project.relative_to(ROOT).as_posix(),source=source.relative_to(ROOT).as_posix(),sourceSha256=original_hash,timing=record['sourceFrameDurationsMs'],loop=moving))
        assert sha(source)==original_hash
    assert before=={name:sha(ART/name) for name in before},'Candidate review must not mutate catalogue or approvals'
    save(output/'candidate_review_plan.json',dict(batch=batch,selected=len(plan),sourcePoses=len(plan)*16,scope='ISOLATED_STUDIO_CANDIDATE_REVIEW_NOT_RUNTIME_SELECTION',catalogueUnchanged=True,entries=plan))
    print(json.dumps(dict(selected=len(plan),sourcePoses=len(plan)*16,catalogueUnchanged=True)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--expected',required=True,type=int);args=parser.parse_args();prepare(args.batch,args.expected)
