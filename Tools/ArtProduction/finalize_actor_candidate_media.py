"""Verify actual native capture identities/phases and export video-only loop evidence."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FFMPEG='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finalize(batch,expected,pilot=False):
    assert batch.isalnum() and expected>0
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);plan=read(ev/('capture_sample_plan.partial.json' if pilot else 'capture_sample_plan.json'))
    if isinstance(plan,dict):plan=[plan]
    assert len(plan)==expected and len({e['Name'] for e in plan})==expected
    source_plan=read(ev/'candidate_review_plan.json');sources={e['id']:e for e in source_plan['entries']};media=[];seams=[]
    for capture in plan:
        name=capture['Name'];assert name.startswith('raw_');entry=sources[name[4:]]
        receipt=read(ev/(name+'.capture_receipt.json'));assert receipt['projectHashEncoding']=='UTF8_LF'
        assert sha(ROOT/entry['source'])==entry['sourceSha256']==receipt['sourceSha256']
        project=ROOT/entry['project'];portable=hashlib.sha256(project.read_text(encoding='utf-8-sig').encode('utf8')).hexdigest();assert portable==receipt['projectSha256']
        document=read(project);assert len(document['Layers'])==len(document['Clips'])==1
        clip=document['Clips'][0];assert clip['DurationsMs']==entry['timing'] and clip['Loop']==entry['loop']
        assert not clip['Tracks'][0]['Interpolate'] and [k['Pose']['SourceFrame'] for k in clip['Tracks'][0]['Keys']]==list(range(16))
        assert sha(project.parent/document['Layers'][0]['Texture'])==entry['sourceSha256']
        log=(ev/(name+'.godot.log')).read_text(encoding='utf-8-sig');assert not re.search(r'^ERROR:',log,re.M)
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',log)];assert {b for a,b in ticks}==set(range(16))
        assert len(set(capture['NativeSampleIndices']))==16
        for phase,native in enumerate(capture['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==phase
        movie=ev/(name+'.mp4');assert sha(movie)==receipt['movieSha256']
        decoded=subprocess.run([FFMPEG,'-v','error','-i',str(movie),'-map','0:v:0','-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
        assert not decoded.stderr.strip() and int(re.findall(r'^frame=(\d+)$',decoded.stdout,re.M)[-1])==180
        media.append(dict(file=movie.name,sha256=receipt['movieSha256'],sourceSha256=entry['sourceSha256'],portableProjectSha256=portable,decodedFrames=180,decodedWithoutDiagnostics=True,renderedSourceFramesVerified=16))
        if entry['loop']:
            wrap=next(i for i in range(2,len(ticks)-1) if ticks[i-1][1]==15 and ticks[i][1]==0)
            chosen=[ticks[wrap-2][0]+1,ticks[wrap-1][0]+1,ticks[wrap][0]+1,ticks[wrap+1][0]+1]
            assert [max((a,b) for a,b in ticks if a<=n)[1] for n in chosen]==[14,15,0,1]
            select='+'.join('eq(n,'+str(n)+')' for n in chosen);proof=ev/(name+'_loop_seam.png')
            subprocess.run([FFMPEG,'-y','-v','error','-i',str(movie),'-vf',"select='"+select+"',crop=256:256:550:120,tile=4x1",'-frames:v','1',str(proof)],check=True)
            seams.append(dict(id=entry['id'],sourceFrames=[14,15,0,1],nativeFrames=chosen,actualWrap=True,file=proof.name,sha256=sha(proof)))
    suffix='.pilot' if pilot else '';save(ev/('loop_seam_sample_plan'+suffix+'.json'),seams)
    report=dict(batch=batch,pilot=pilot,selectedVideos=len(media),sourceFramesMeasured=len(media)*16,actualLoopWraps=len(seams),files=media,scope='NATIVE_CAPTURE_IDENTITY_AND_PHASES_NOT_VISUAL_ACCEPTANCE')
    save(ev/('native_media_audit'+suffix+'.json'),report);print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--expected',required=True,type=int);parser.add_argument('--pilot',action='store_true');args=parser.parse_args();finalize(args.batch,args.expected,args.pilot)
