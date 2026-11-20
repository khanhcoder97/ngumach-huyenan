"""Decode/hash native review videos. Offline frame counts are never an FPS benchmark."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def audit(root, ffmpeg):
    root=root.resolve()
    files=sorted(root.rglob('*.mp4'))
    assert files,'no native review media'
    result=[]
    for path in files:
        process=subprocess.run([str(ffmpeg),'-v','error','-i',str(path),'-map','0:v:0','-f','null','-',
                                '-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
        assert not process.stderr.strip(),f'decode diagnostics: {path}: {process.stderr}'
        progress=dict(line.split('=',1) for line in process.stdout.splitlines() if '=' in line)
        assert progress.get('progress')=='end','incomplete decode'
        count=int(progress['frame']);seconds=int(progress['out_time_us'])/1_000_000
        assert count>0 and seconds>0,'empty decoded video'
        result.append(dict(file=path.relative_to(root).as_posix(),bytes=path.stat().st_size,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest(),decodedFrames=count,
                           decodedSeconds=seconds,offlineFramesPerSecond=count/seconds,
                           activeSelection=path.parent==root,decodedWithoutDiagnostics=True))
    return dict(scope='OFFLINE_NATIVE_VISUAL_REVIEW_NOT_GAMEPLAY_PERFORMANCE',
                selectedVideos=sum(r['activeSelection'] for r in result),
                supersededVideos=sum(not r['activeSelection'] for r in result),files=result,
                note='Source-sheet and native timeline checks are separate. Movie Maker is offline; these rates cannot certify real-time gameplay FPS.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--ffmpeg',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=audit(args.root,args.ffmpeg)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ('selectedVideos','supersededVideos')}))
