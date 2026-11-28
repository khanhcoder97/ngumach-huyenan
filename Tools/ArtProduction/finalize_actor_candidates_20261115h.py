"""Read native traces/decode original review movies; crops are evidence, never game assets."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261115h'
FFMPEG='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finalize():
    plan={p['Name']:p for p in read(EV/'capture_sample_plan.json')};assert len(plan)==3
    partial=read(EV/'capture_sample_plan.partial.json')
    for entry in ([partial] if isinstance(partial,dict) else partial):assert entry['Name'] in plan;plan[entry['Name']]=entry
    sources={e['id']:e for e in read(EV/'candidate_review_plan.json')['entries']};media=[];seams=[]
    for name,entry in plan.items():
        identifier=name[4:];assert identifier in sources
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(name+'.godot.log')).read_text(encoding='utf-8-sig'))]
        assert {b for a,b in ticks}==set(range(16))
        assert len(set(entry['NativeSampleIndices']))==16
        for phase,native in enumerate(entry['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==phase
        movie=EV/(name+'.mp4')
        decoded=subprocess.run([FFMPEG,'-v','error','-i',str(movie),'-map','0:v:0','-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
        assert not decoded.stderr.strip(),decoded.stderr
        assert int(re.findall(r'^frame=(\d+)$',decoded.stdout,re.M)[-1])==180
        media.append(dict(file=movie.name,sha256=sha(movie),decodedFrames=180,decodedWithoutDiagnostics=True,sourceSha256=sources[identifier]['sourceSha256']))
        if sources[identifier]['loop']:
            wrap=next(i for i in range(2,len(ticks)-1) if ticks[i-1][1]==15 and ticks[i][1]==0)
            chosen=[ticks[wrap-2][0]+1,ticks[wrap-1][0]+1,ticks[wrap][0]+1,ticks[wrap+1][0]+1]
            assert [max((a,b) for a,b in ticks if a<=n)[1] for n in chosen]==[14,15,0,1]
            select='+'.join('eq(n,'+str(n)+')' for n in chosen)
            proof=EV/(name+'_loop_seam.png')
            subprocess.run([FFMPEG,'-y','-v','error','-i',str(movie),'-vf',"select='"+select+"',crop=256:256:550:120,tile=4x1",'-frames:v','1',str(proof)],check=True)
            seams.append(dict(id=identifier,sourceFrames=[14,15,0,1],nativeFrames=chosen,actualWrap=True,file=proof.name,sha256=sha(proof)))
    save(EV/'capture_sample_plan.json',list(plan.values()));save(EV/'loop_seam_sample_plan.json',seams)
    archived=list(EV.glob('Superseded_Run_E_v*/raw_class_huyen_but_run_e.mp4'))
    save(EV/'native_media_audit.json',dict(selectedVideos=3,supersededVideos=len(archived),supersededFiles=[dict(file=p.relative_to(EV).as_posix(),sha256=sha(p)) for p in archived],files=media,sourceFramesMeasured=48,scope='ISOLATED_CANDIDATE_PROOFS_NOT_APPROVAL'))
    print(json.dumps(dict(selectedVideos=3,decodedFramesPerVideo=180,actualLoopWraps=len(seams),sourceFramesMeasured=48)))
if __name__=='__main__':finalize()
