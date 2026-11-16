"""Verify current isolated candidates and native receipts, with no art promotion."""
import argparse
import json
import re
import subprocess
from inspect_actor_library import ART, ROOT
from prepare_thach_chuy_candidates_20261116c import EV, read, save, sha


def audit(expected, ffmpeg):
    manifest = read(ART/'Candidates_20261116c/candidate_manifest.json')
    assert manifest['selected'] == len(manifest['records']) == expected
    assert manifest['expectedSourcePages']==50 and expected<=50
    current={r['id']:r for r in manifest['records']}
    registrations={r['record']['id']:r for r in read(ART/'body_registration_20261116c.json')['entries']}
    assert set(current)==set(registrations)
    previous_path=EV/'native_media_audit.current.json'
    previous=read(previous_path) if previous_path.exists() else {}
    previous_movies={e['file']:e for e in previous.get('files',[])}
    previous_seams={e['id']:e for e in previous.get('loopSeams',[])}
    files=[];capture_plan=[];wraps=[]
    for record in manifest['records']+manifest['history']:
        assert sha(ART/record['source'])==record['sourceSha256']
        assert (ART/record['prompt']).is_file()
        for source in record['generationInputs']:
            assert sha(ROOT/source['path'])==source['sourceSha256']
    for identifier,record in current.items():
        entry=registrations[identifier]
        assert entry['record']['sourceSha256']==record['sourceSha256'] and not entry['productionApproved']
        project=EV/'Candidate_Studio'/identifier/'project.json';document=read(project)
        assert len(document['Layers'])==len(document['Clips'])==1
        layer=document['Layers'][0];clip=document['Clips'][0]
        assert len(clip['Tracks'])==1
        track=clip['Tracks'][0]
        assert not document['ProductionApproved'] and not track['Interpolate']
        frames=entry['page']['directions'][0]['frames'];assert len(frames)==16
        assert len(track['Keys'])==16 and layer['Rest']==track['Keys'][0]['Pose']
        assert layer['Regions']==[f['rect'] for f in frames]
        scale=140/entry['page']['directions'][0]['referenceHeight']
        assert sha(project.parent/layer['Texture'])==record['sourceSha256']
        assert clip['DurationsMs']==record['sourceFrameDurationsMs']
        for i,(key,frame) in enumerate(zip(track['Keys'],frames)):
            pose=key['Pose'];assert key['Frame']==pose['SourceFrame']==i
            assert [pose['PivotX'],pose['PivotY']]==frame['pivot']
            assert pose['ScaleX']==pose['ScaleY']==scale
            assert pose['X']==pose['Y']==pose['Angle']==0 and pose['Alpha']==1
        name='raw_'+identifier;movie=EV/(name+'.mp4');receipt=read(EV/(name+'.capture_receipt.json'))
        assert receipt['sourceSha256']==record['sourceSha256'] and receipt['projectSha256']==sha(project)
        assert receipt['movieSha256']==sha(movie)
        log=(EV/(name+'.godot.log')).read_text(encoding='utf-8-sig')
        assert '\0' not in log and not re.search(r'^ERROR:',log,re.M)
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',log)]
        assert {s for _,s in ticks}==set(range(16))
        starts=[next(n for n,s in ticks if s==i) for i in range(16)]
        samples=[max(1,n+((starts[i+1]-1 if i<15 else n+1)-n)//2) for i,n in enumerate(starts)]
        assert len(set(samples))==16 and samples==sorted(samples)
        # These are the exact selections used by the native capture script.
        capture_plan.append(dict(Name=name,SourceDurationMs=sum(record['sourceFrameDurationsMs']),NativeSampleIndices=samples,RenderedSourceFramesVerified=16,Scope='SOURCE_REVIEW_NOT_GAMEPLAY_FPS'))
        decoded=subprocess.run([ffmpeg,'-v','error','-progress','pipe:1','-nostats','-i',str(movie),'-map','0:v:0','-f','null','-'],capture_output=True,text=True)
        assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
        decoded_frames=int(re.findall(r'^frame=(\d+)',decoded.stdout,re.M)[-1]);assert decoded_frames==180
        files.append(dict(file=movie.name,sha256=sha(movie),sourceSha256=record['sourceSha256'],portableProjectSha256=sha(project),decodedFrames=decoded_frames,decodedWithoutDiagnostics=True,renderedSourceFramesVerified=16))
        if record.get('previewLoop'):
            transition=next(i for i in range(2,len(ticks)-1) if ticks[i-2][1]==14 and ticks[i-1][1]==15 and ticks[i][1]==0 and ticks[i+1][1]==1)
            seam=[max(1,ticks[i][0]+1) for i in range(transition-2,transition+2)]
            output=EV/(name+'_loop_wrap.png')
            select='+'.join('eq(n,%d)'%n for n in seam)
            result=subprocess.run([ffmpeg,'-v','error','-y','-i',str(movie),'-vf',"select='"+select+"',crop=256:256:550:120,tile=4x1",'-frames:v','1',str(output)],capture_output=True,text=True)
            assert result.returncode==0,result.stderr
            previous_movie=previous_movies.get(movie.name,{})
            previous_seam=previous_seams.get(identifier,{})
            unchanged=previous_movie.get('sourceSha256')==record['sourceSha256'] and previous_movie.get('portableProjectSha256')==sha(project) and previous_movie.get('sha256')==sha(movie) and previous_seam.get('sha256')==sha(output) and previous_seam.get('nativeFrames')==seam
            wraps.append(dict(id=identifier,sourceFrames=[14,15,0,1],nativeFrames=seam,file=output.name,sha256=sha(output),manualViewed=bool(unchanged and previous_seam.get('manualViewed'))))
    for name in ('generation_records.json','visual_review.json','structure_report.json'):
        baseline=json.loads(subprocess.check_output(['git','show','HEAD:'+(ART/name).relative_to(ROOT).as_posix()],cwd=ROOT).decode('utf-8-sig'))
        assert baseline==read(ART/name),'Published catalogue changed'
    subprocess.run(['git','diff','--quiet','HEAD','--','ClientGodot/assets/actor_library_v1'],cwd=ROOT,check=True)
    native=dict(batch='20261116c',selectedVideos=expected,sourceFramesMeasured=16*expected,files=files,actualLoopWrapsExtracted=len(wraps),loopSeams=wraps,productionApproved=False)
    save(EV/'native_media_audit.current.json',native)
    save(EV/'capture_sample_plan.current.json',capture_plan)
    print(json.dumps(dict(selected=expected,sourcePoses=16*expected,nativeVideos=expected,decodedFrames=sum(e['decodedFrames'] for e in files),loopSeamsExtracted=len(wraps),publishedCatalogueUnchanged=True,runtimeLibraryUnchanged=True,productionApproved=False)))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--expected',type=int,required=True)
    parser.add_argument('--ffmpeg',default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    args=parser.parse_args();audit(args.expected,args.ffmpeg)
