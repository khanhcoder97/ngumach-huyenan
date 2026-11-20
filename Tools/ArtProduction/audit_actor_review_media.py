"""Decode selected native captures; movie FPS is not a gameplay performance result."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from inspect_actor_library import ROOT

def audit(batch,ffmpeg):
    assert batch.isalnum()
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch)
    files=[]
    for p in sorted(ev.glob('*.mp4')):
        result=subprocess.run([str(ffmpeg),'-v','error','-nostats','-i',str(p),'-map','0:v:0','-an','-progress','pipe:1','-f','null','-'],capture_output=True,text=True)
        counts=re.findall(r'^frame=(\d+)$',result.stdout,re.M)
        assert result.returncode==0 and not result.stderr and counts and 'progress=end' in result.stdout,'decode failed: '+p.name
        count=int(counts[-1]);expected=600 if p.stem=='mobility_chain' or p.stem.startswith('assembly_') else 180
        assert count==expected,'unexpected native capture length: '+p.name
        files.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),decodedFrames=count,decodedWithoutDiagnostics=True))
    assert files,'no selected native captures'
    superseded=list(ev.glob('Superseded*/*.mp4'))
    report=dict(scope='OFFLINE_NATIVE_SOURCE_REVIEW_NOT_GAMEPLAY_FPS',selectedVideos=len(files),supersededVideos=len(superseded),files=files)
    (ev/'native_media_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return dict(selectedVideos=len(files),supersededVideos=len(superseded),allDecoded=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--ffmpeg',type=Path,required=True);args=parser.parse_args()
    print(json.dumps(audit(args.batch,args.ffmpeg)))
