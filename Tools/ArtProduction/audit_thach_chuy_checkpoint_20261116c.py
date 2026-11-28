"""Verify a partial candidate delivery. Never promotes sources or marks the library complete."""
import hashlib,json,subprocess
from pathlib import Path
from inspect_actor_library import ART,ROOT,inspect
from prepare_thach_chuy_candidates_20261116c import save
BATCH='20261116c';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def audit():
    folder=ART/('Candidates_'+BATCH);manifest=read(folder/'candidate_manifest.json');records=manifest['records'];identifiers={r['id'] for r in records}
    assert manifest['expectedSourcePages']==50 and len(records)==manifest['selected']==25
    assert manifest['generatedVariants']==len(records)+len(manifest['history'])==29
    registrations={e['record']['id']:e for e in read(ART/('body_registration_'+BATCH+'.json'))['entries']}
    observations={e['id']:e for e in read(EV/'manual_review_observations.json')['entries']}
    native=read(EV/'native_media_audit.pilot.json');movies={e['file'][4:-4]:e for e in native['files']}
    assert set(registrations)==set(observations)==set(movies)==identifiers
    assert native['selectedVideos']==25 and native['sourceFramesMeasured']==400 and native['actualLoopWraps']==1
    for r in records+manifest['history']:
        assert sha(ART/r['source'])==r['sourceSha256'] and (ART/r['prompt']).is_file()
        for reference in r['generationInputs']:assert sha(ROOT/reference['path'])==reference['sourceSha256']
    for r in records:
        identifier=r['id'];registration=registrations[identifier];assert registration['record']['sourceSha256']==r['sourceSha256']
        assert inspect(registration['record'])==registration['page']
        assert registration['page']['sourceFrames']==16 and not registration['productionApproved']
        job=read(folder/'Jobs'/(identifier+'.json'));assert job['prompt'].rstrip()==(ART/r['prompt']).read_text(encoding='utf8').rstrip()
        assert job['sourceSha256']==r['sourceSha256'] and not job.get('nativeSourceFile')
        project=EV/'Candidate_Studio'/identifier/'project.json';document=read(project)
        assert len(document['Layers'])==len(document['Clips'])==1 and not document['Sockets']
        layer=document['Layers'][0];clip=document['Clips'][0];direction=registration['page']['directions'][0];frames=direction['frames']
        assert sha(project.parent/layer['Texture'])==r['sourceSha256']
        assert layer['Regions']==[f['rect'] for f in frames] and layer['Visible'] and layer['Z']==0 and not layer.get('AttachSocket')
        assert clip['DurationsMs']==r['sourceFrameDurationsMs'] and not document['ProductionApproved']
        assert clip['Loop']==bool(r.get('previewLoop',False)) and len(clip['Tracks'])==1
        track=clip['Tracks'][0];assert track['LayerId']==layer['Id'] and not track['Interpolate'] and len(track['Keys'])==16
        scale=140/direction['referenceHeight']
        for index,(key,frame) in enumerate(zip(track['Keys'],frames)):
            pose=key['Pose'];assert key['Frame']==pose['SourceFrame']==index
            assert [pose['PivotX'],pose['PivotY']]==frame['pivot']
            assert pose['ScaleX']==pose['ScaleY']==scale and pose['X']==pose['Y']==pose['Angle']==0 and pose['Alpha']==1
        assert layer['Rest']==track['Keys'][0]['Pose']
        observation=observations[identifier];movie=movies[identifier]
        assert observation['sourceSha256']==movie['sourceSha256']==r['sourceSha256']
        assert observation['portableProjectSha256']==movie['portableProjectSha256']==sha(project)
        assert observation['movieSha256']==movie['sha256']==sha(EV/movie['file'])
        assert observation['montageSha256']==sha(EV/('raw_'+identifier+'_poses.png'))
        assert observation['nativePoseFramesInspected']==movie['renderedSourceFramesVerified']==16
        assert movie['decodedFrames']==180 and movie['decodedWithoutDiagnostics']
        assert not observation['productionApproved']
    portable=read(folder/'production_job_plan.json');assert len(portable['jobs'])==50 and portable['selected']==25 and portable['remaining']==25
    for name in ('generation_records.json','visual_review.json','structure_report.json'):
        repository_path=(ART/name).relative_to(ROOT).as_posix()
        baseline=json.loads(subprocess.check_output(['git','show','HEAD:'+repository_path],cwd=ROOT).decode('utf-8-sig'))
        assert baseline==read(ART/name),'Published catalogue changed during candidate authoring'
    subprocess.run(['git','diff','--quiet','HEAD','--','ClientGodot/assets/actor_library_v1'],cwd=ROOT,check=True)
    return dict(batch=BATCH,scope='PARTIAL_CANDIDATE_SOURCE_CHECKPOINT_NOT_PRODUCTION_ACCEPTANCE',selectedSources=25,sourcePoses=400,sourceVariants=29,supersededEarlierVariants=4,portableJobs=50,registeredProjects=25,nativeVideos=25,decodedNativeFrames=4500,actualLoopWraps=1,explicitManualNativeViews=25,actualProjectRegionsPivotsScalesAndSourceKeysMatchRegistration=True,sourceApprovalsApplied=0,publishedCatalogueUnchanged=True,runtimeLibraryUnchanged=True,remainingInFiftySourcePackage=25,fullLibraryComplete=False,productionApproved=False)

if __name__=='__main__':
    result=audit();save(EV/'checkpoint_audit.json',result);print(json.dumps(result))
