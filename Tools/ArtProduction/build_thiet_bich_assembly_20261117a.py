"""Build an editable phase/socket preview from unchanged authored PNGs; no gameplay authority."""
import copy,hashlib,json,math,shutil
from pathlib import Path
from PIL import Image
from inspect_actor_library import ART,ROOT
from prepare_thach_chuy_candidates_20261116c import save
EV=ROOT/'Implementation/Reports/Evidence/Actor_Assembly_20261117a'
SOURCE=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261116c/Candidate_Studio'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf8'))

def make():
    identifiers={'body':'class_thach_chuy_skill_03_s',**{part:'sk_tc_03_plate_'+part+'_component' for part in ('gain','sustain','crack_overlay','end')}}
    inputs={part:read(SOURCE/identifier/'source_registration.json') for part,identifier in identifiers.items()}
    for part,entry in inputs.items():assert sha(ART/entry['record']['source'])==entry['record']['sourceSha256']
    bundle=EV/'ThietBich_S_trial1';textures=bundle/'textures';textures.mkdir(parents=True,exist_ok=True)
    for entry in inputs.values():
        original=ART/entry['record']['source'];destination=textures/(entry['record']['sourceSha256']+'.png')
        if destination.exists():assert sha(destination)==sha(original)
        else:shutil.copyfile(original,destination)
    # This is an authoring demo clock, not a buff duration or a gameplay lock.
    # Keep persisted values JSON-native: the atomic writer verifies a decoded
    # round trip before replacing the destination (tuples decode as lists).
    windows={'gain':[240,720,30],'sustain':[720,2320,80],'crack_overlay':[1920,2320,25],'end':[2320,2720,25]}
    boundaries={0,3040,*range(0,961,60)}
    for start,end,step in windows.values():boundaries.update(range(start,end+1,step));boundaries.add(end)
    times=sorted(boundaries);durations=[b-a for a,b in zip(times,times[1:])];assert len(durations)<=120 and min(durations)>=5
    body=inputs['body'];body_frames=body['page']['directions'][0]['frames'];height=body['record']['bodyReferenceHeight'];scale=140/height;world_height=140
    diagnostics=body['bodyRootDiagnostics'];assert len(diagnostics)==16
    positions=[];anchor_notes=[]
    with Image.open(ART/body['record']['source']) as image:
        for frame,note in zip(body_frames,diagnostics):
            root_x,root_y=frame['pivot'];head=note['head'];head_x=(head['centerX']-root_x)*scale;head_top=(head['top']-root_y)*scale
            x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h))
            knee=[(i%w,i//w) for i,(r,g,b,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and 30<=r<=160 and r-g>=12 and g-b>=5 and r-b>=40 and r-g>=g-b and i%w>root_x+.04*height and root_y-.22*height<=i//w<=root_y-.08*height]
            if len(knee)>=8:
                knee_point=[(sum(x for x,y in knee)/len(knee)-root_x)*scale,(sum(y for x,y in knee)/len(knee)-root_y)*scale];method='VISIBLE_WARM_RIGHT_LEG_BAND'
            else:knee_point=[head_x+.16*world_height,-.17*world_height];method='NOMINAL_KNEE_PENDING_HAND_REVIEW'
            positions.append(dict(guard_shoulder=[head_x+.24*world_height,head_top+.50*world_height],back=[head_x-.02*world_height,head_top+.60*world_height],guard_knee=knee_point))
            anchor_notes.append(dict(kneePixels=len(knee),kneeMethod=method,productionApproved=False))
    roles={'guard_shoulder':(.18,2),'back':(.16,-4),'guard_knee':(.13,4)}
    layers=[];tracks=[];sockets=[dict(Id=role,Name=role,LayerId='',X=positions[0][role][0],Y=positions[0][role][1]) for role in roles]
    body_layer=dict(Id='body',Name='Thạch Chùy · Thiết Bích · S',Kind='sprite',Texture='textures/'+body['record']['sourceSha256']+'.png',Regions=[f['rect'] for f in body_frames],Z=0,Visible=True)
    body_keys=[]
    for index,(a,b) in enumerate(zip(times,times[1:])):
        source_frame=min(15,int(((a+b)/2)//60));frame=body_frames[source_frame]
        body_keys.append(dict(Frame=index,Pose=dict(X=0,Y=0,PivotX=frame['pivot'][0],PivotY=frame['pivot'][1],ScaleX=scale,ScaleY=scale,Angle=0,Alpha=1,SourceFrame=source_frame)))
    body_layer['Rest']=body_keys[0]['Pose'];layers.append(body_layer);tracks.append(dict(LayerId='body',Interpolate=False,Keys=body_keys))
    phase_references={}
    for part,entry in inputs.items():
        if part=='body':continue
        frames=entry['page']['directions'][0]['frames'];reference=frames[15 if part in ('gain','crack_overlay') else 0];left,top,right,bottom=reference['bounds']
        reference_width=right-left;origin=[(left+right)/2/reference['rect'][2],(top+bottom)/2/reference['rect'][3]]
        phase_references[part]=dict(referenceSourceFrame=15 if part in ('gain','crack_overlay') else 0,visibleWidth=reference_width,parentOriginFraction=origin,footprintFactor=.82 if part=='crack_overlay' else 1)
        for role,(fraction,z) in roles.items():
            layer_id=role+'_'+part;target_width=fraction*world_height*(.82 if part=='crack_overlay' else 1);unit_scale=target_width/reference_width;keys=[]
            start,end,step=windows[part]
            for index,(a,b) in enumerate(zip(times,times[1:])):
                midpoint=(a+b)/2;active=start<=midpoint<end;body_index=min(15,int(midpoint//60))
                source_frame=(int((midpoint-start)//step)%16 if part=='sustain' else min(15,max(0,int((midpoint-start)//step)))) if active else 0
                frame=frames[source_frame]
                # Whole plate gain/sustain centres are registered. A growing
                # fracture retains a fixed parent footprint; centring its tiny
                # first mark would make the pattern slide across the plate.
                pivot=frame['pivot'] if part in ('gain','sustain') else [origin[0]*frame['rect'][2],origin[1]*frame['rect'][3]]
                current=positions[body_index][role];base=positions[0][role]
                keys.append(dict(Frame=index,Pose=dict(X=current[0]-base[0],Y=current[1]-base[1],PivotX=pivot[0],PivotY=pivot[1],ScaleX=unit_scale,ScaleY=unit_scale,Angle=0,Alpha=1 if active else 0,SourceFrame=source_frame)))
            layer=dict(Id=layer_id,Name=role+' · '+part,Kind='sprite',Texture='textures/'+entry['record']['sourceSha256']+'.png',Regions=[f['rect'] for f in frames],Rest=keys[0]['Pose'],AttachSocket=role,Z=z+(1 if part=='crack_overlay' else 0),Visible=True)
            layers.append(layer);tracks.append(dict(LayerId=layer_id,Interpolate=False,Keys=keys))
    markers=[dict(Name=part+'_preview_only',Kind='vfx',Frame=times.index(start),X=0,Y=0,Radius=0) for part,(start,end,step) in windows.items()]
    document=dict(SchemaVersion=1,Scope='PRESENTATION_AUTHORING_ONLY',Name='Thiết Bích · 3 socket · S · thử ghép 1',ProductionApproved=False,Layers=layers,Sockets=sockets,Clips=[dict(Name='thiet_bich_s_phase_chain',Direction='S',Loop=False,SourceNote='PREVIEW ONLY: one16pose body activation,then final-pose hold for FX inspection. Timeline segments synchronize layers; they are not extra authored body frames. Three independent socket instances. No buff/damage/collision or server timing.',DurationsMs=durations,Tracks=tracks,Markers=markers)])
    project=bundle/'project.json'
    if project.exists():assert read(project)==document,'Manual trial edits present; create a new trial instead of overwriting'
    else:save(project,document)
    descriptor=dict(scope='THREE_SOCKET_PHASE_ALIGNMENT_TRIAL_NOT_GAMEPLAY_OR_SOURCE_ACCEPTANCE',projectSha256=sha(project),bodySourcePoses=16,componentSourcePoses=64,timelineSegments=len(durations),durationMs=sum(durations),bodyAfterActivation='FINAL_POSE_HOLD_FOR_INSPECTION_NOT_GAMEPLAY_IDLE',socketRoles=list(roles),sourceInputs={part:dict(id=entry['record']['id'],pngSha256=entry['record']['sourceSha256'],registrationSha256=sha(SOURCE/identifiers[part]/'source_registration.json')) for part,entry in inputs.items()},phaseReferenceFootprints=phase_references,phaseWindowsMs=windows,sourcePoseAnchorNotes=anchor_notes,productionApproved=False)
    save(bundle/'assembly_descriptor.json',descriptor)
    print(json.dumps(dict(project=project.relative_to(ROOT).as_posix(),layers=len(layers),sockets=len(sockets),sourcePngs=5,timelineSegments=len(durations),durationMs=sum(durations),originalPngsUnchanged=True,productionApproved=False)))
if __name__=='__main__':make()
