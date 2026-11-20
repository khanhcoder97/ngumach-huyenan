"""Register the 25 original I drawings and build isolated Studio projects; no approvals."""
import hashlib,json,shutil
from collections import Counter
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect,binary_projection
from calibrate_anh_dao_mobility import head_landmark
from calibrate_huyen_but_20261114f import gutter_edges
from calibrate_huyen_but_20261114g import boot_root
BATCH='20261115i';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def cool_body_contact(region):
    """Cool cloth/boots/hair contact, not the warm brush tip or a sparse outline."""
    width,height=region.size
    points=[(i%width,i//width) for i,(r,g,b,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and max(r,g,b)>=35 and b>=g-12 and b>=r-12]
    assert len(points)>=30,'No usable body contact; manual registration required'
    rows=Counter(y for x,y in points);threshold=max(5,int(max(rows.values())*.12));ground=max(y for y,n in rows.items() if n>=threshold)+1
    return (min(x for x,y in points)+max(x for x,y in points))/2,ground

def prepare():
    manifest=read(ART/('Candidates_'+BATCH)/'candidate_manifest.json');assert manifest['selected']==25 and manifest['remainingSourcePages']==0
    assert not any(r.get('batch')==BATCH for r in read(ART/'generation_records.json')),'Delivered metadata requires a new review'
    before={n:sha(ART/n) for n in ('generation_records.json','visual_review.json','structure_report.json')}
    EV.mkdir(parents=True,exist_ok=True);plan=[];registrations=[];issues=[]
    for original in manifest['records']:
        record=dict(original);source=ART/record['source'];assert sha(source)==record['sourceSha256']
        try:
            with Image.open(source) as image:
                try:page=inspect(record)
                except AssertionError as error:
                    assert 'clipped/overlapping' in str(error),str(error)
                    xs,ys=binary_projection(image.getchannel('A').point(lambda a:255 if a>=200 else 0));record['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));page=inspect(record)
                frames=page['directions'][0]['frames'];moving='_walk_' in record['id'];death='_death_' in record['id'];pivots=[];heads=[];neutral=None;offset=None
                for frame in frames:
                    x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,frame['bounds']);heads.append(head)
                    if neutral is None:
                        boot_x,ground,_=boot_root(region,head,frame['bounds'][3]-head['top'],moving);neutral=ground-head['top']
                        offset=boot_x-(cool_body_contact(region)[0] if death else head['centerX'])
                    if death:
                        center,ground=cool_body_contact(region);pivots.append([center+offset,ground])
                    else:
                        boot_x,ground,_=boot_root(region,head,neutral,moving);pivots.append([head['centerX']+offset if moving else boot_x,ground])
            method='COOL_BODY_CONTACT_FOOTPRINT_DEATH_PENDING_NATIVE_WORLD_ROOT_REVIEW' if death else 'NEUTRAL_HEAD_PROJECTED_X_COOL_BOOT_Y' if moving else 'COOL_BOOT_FOOT_ROOT'
            record.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral,registrationMethod=method)
            page=inspect(record);assert page['sourceFrames']==16 and page['sha256']==sha(source)
            bundle=EV/'Candidate_Studio'/record['id'];textures=bundle/'textures';textures.mkdir(parents=True,exist_ok=True);dest=textures/(page['sha256']+'.png')
            if dest.exists():assert sha(dest)==page['sha256']
            else:shutil.copyfile(source,dest)
            loop=any('_'+a+'_' in record['id'] for a in ('idle','walk'));keys=[dict(Frame=i,Pose=dict(X=0,Y=0,PivotX=f['pivot'][0],PivotY=f['pivot'][1],ScaleX=140/neutral,ScaleY=140/neutral,Angle=0,Alpha=1,SourceFrame=i)) for i,f in enumerate(page['directions'][0]['frames'])]
            layer=dict(Id='sprite',Name=record['id'],Kind='sprite',Texture='textures/'+dest.name,Regions=[f['rect'] for f in frames],Rest=keys[0]['Pose'],Z=0,Visible=True)
            clip=dict(Name=record['id'],Direction=record['direction'],Loop=loop,SourceNote='SOURCE_CANDIDATE_NOT_APPROVED; '+method,DurationsMs=record['sourceFrameDurationsMs'],Tracks=[dict(LayerId='sprite',Interpolate=False,Keys=keys)],Markers=[])
            project=bundle/'project.json';save(project,dict(SchemaVersion=1,Scope='PRESENTATION_AUTHORING_ONLY',Name=record['id'],ProductionApproved=False,Layers=[layer],Sockets=[],Clips=[clip]))
            registration=dict(record=record,page=page,headLandmarks=heads,method=method,originalPngUnchanged=True,productionApproved=False);save(bundle/'source_registration.json',registration);registrations.append(registration)
            plan.append(dict(id=record['id'],project=project.relative_to(ROOT).as_posix(),source=source.relative_to(ROOT).as_posix(),sourceSha256=page['sha256'],timing=record['sourceFrameDurationsMs'],loop=loop))
        except (AssertionError,OSError) as error:issues.append(dict(id=record['id'],reason=str(error),source=record['source']))
    assert before=={n:sha(ART/n) for n in before}
    save(EV/'candidate_review_plan.json',dict(batch=BATCH,selected=len(plan),expected=25,sourcePoses=len(plan)*16,catalogueUnchanged=True,scope='ISOLATED_STUDIO_SOURCE_REVIEW_NOT_RUNTIME_SELECTION',entries=plan))
    save(ART/('body_registration_'+BATCH+'.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',entries=registrations,issues=issues))
    save(EV/'candidate_registration_summary.json',dict(selected=25,registered=len(plan),sourcePoses=len(plan)*16,issues=issues,explicitGutterSources=[r['record']['id'] for r in registrations if r['record'].get('gridEdges')],rasterModified=False,productionApproved=False))
    print(json.dumps(dict(selected=25,registered=len(plan),issues=issues,catalogueUnchanged=True)))
    assert not issues,'Unregistered drawings need repair before full native capture'
if __name__=='__main__':prepare()
