"""Merge actual capture traces, decode media, and sample genuine loop wraps; no asset edits."""
import hashlib,json,re,subprocess
from pathlib import Path
from inspect_actor_library import ROOT
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g'
FFMPEG=Path('D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def finalize():
    plan={p['Name']:p for p in read(EV/'capture_sample_plan.json')};assert len(plan)==43
    for name in ('capture_sample_plan.support_final.json','capture_sample_plan.partial.json'):
        for entry in read(EV/name):assert entry['Name'] in plan;plan[entry['Name']]=entry
    for entry in plan.values():
        if entry['Name'].startswith('raw_'):
            ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(entry['Name']+'.godot.log')).read_text(encoding='utf-8-sig'))]
            assert set(b for a,b in ticks)==set(range(16))
            assert len(set(entry['NativeSampleIndices']))==16
            for source,native in enumerate(entry['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==source
    save(EV/'capture_sample_plan.json',list(plan.values()))
    seams=[]
    for identifier in ('class_huyen_but_run_ne','class_huyen_but_run_se','class_huyen_but_run_s','sk_hb_04_rain_component'):
        name='raw_'+identifier
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(name+'.godot.log')).read_text(encoding='utf-8-sig'))]
        wrap=next(i for i in range(2,len(ticks)-1) if ticks[i-1][1]==15 and ticks[i][1]==0)
        chosen=[ticks[wrap-2][0]+1,ticks[wrap-1][0]+1,ticks[wrap][0]+1,ticks[wrap+1][0]+1]
        assert [max((a,b) for a,b in ticks if a<=n)[1] for n in chosen]==[14,15,0,1]
        selection='+'.join('eq(n,'+str(n)+')' for n in chosen)
        subprocess.run([str(FFMPEG),'-y','-v','error','-i',str(EV/(name+'.mp4')),'-vf',"select='"+selection+"',crop=256:256:550:120,tile=4x1",'-frames:v','1',str(EV/(name+'_loop_seam.png'))],check=True,capture_output=True)
        seams.append(dict(id=identifier,sourceFrames=[14,15,0,1],nativeSampleIndices=chosen,actualWrap=True))
    save(EV/'loop_seam_sample_plan.json',seams)
    media=[]
    for file in sorted(EV.glob('*.mp4')):
        result=subprocess.run([str(FFMPEG),'-hide_banner','-nostdin','-i',str(file),'-map','0:v:0','-f','null','-'],capture_output=True,text=True)
        (EV/(file.stem+'.final_decode.log')).write_text(result.stderr,encoding='utf8')
        assert result.returncode==0,'Decode failed: '+file.name
        frames=re.findall(r'frame=\s*(\d+)',result.stderr);assert frames and int(frames[-1])==180
        media.append(dict(file=file.name,sha256=sha(file),decodedFrames=180,decodedWithoutDiagnostics=not re.search(r'corrupt|Invalid data|Error while|decode error',result.stderr,re.I)))
        assert media[-1]['decodedWithoutDiagnostics'];print('DECODED '+file.stem,flush=True)
    assert len(media)==43
    # The run_s* snapshot glob also retained the unchanged run_se video.
    # Keep that harmless snapshot, but do not count it as a superseded trial.
    archived=list(EV.glob('Superseded_*/*.mp4'))
    snapshots=[f for f in archived if (EV/f.name).is_file() and sha(f)==sha(EV/f.name)]
    superseded=[f for f in archived if f not in snapshots]
    assert len(superseded)==5 and len(snapshots)==1
    save(EV/'native_media_audit.json',dict(scope='OFFLINE_NATIVE_SOURCE_REVIEW_NOT_GAMEPLAY_FPS',selectedVideos=43,supersededVideos=len(superseded),archivedVideoFiles=len(archived),unchangedActiveSnapshots=[f.relative_to(EV).as_posix() for f in snapshots],files=media))
    print(json.dumps(dict(selectedVideos=43,supersededVideos=len(superseded),unchangedSnapshots=len(snapshots),rawPoseTraces=36,genuineLoopSeams=len(seams))))

if __name__=='__main__':finalize()
