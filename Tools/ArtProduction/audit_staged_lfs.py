"""Read-only release guard for staged art: pointer, workspace and local LFS cache."""
import argparse,hashlib,io,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MEDIA={'.png','.mp4','.webm','.wav','.ogg','.mp3','.flac','.aseprite','.psd','.kra','.ogv'}


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def audit():
    raw=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z'],cwd=ROOT)
    files=[p for p in raw.decode('utf8').split('\0') if p and Path(p).suffix.lower() in MEDIA]
    assert files,'no staged media; refusing an empty integrity report'
    git_dir=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=ROOT,text=True).strip())
    if not git_dir.is_absolute():git_dir=(ROOT/git_dir).resolve()
    response=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(':'+p+'\n' for p in files).encode('utf8')))
    entries=[]
    for name in files:
        header=response.readline().decode().split();assert len(header)==3 and header[1]=='blob','missing staged media blob'
        blob=response.read(int(header[2]));assert response.read(1)==b'\n'
        assert blob.startswith(b'version https://git-lfs.github.com/spec/v1\n'),'media bypassed LFS: '+name
        oid_match=re.search(rb'^oid sha256:([0-9a-f]{64})$',blob,re.M);size_match=re.search(rb'^size ([0-9]+)$',blob,re.M)
        assert oid_match and size_match,'malformed staged LFS pointer: '+name
        oid=oid_match[1].decode();size=int(size_match[1]);source=ROOT/name
        assert source.is_file() and source.stat().st_size==size and sha(source)==oid,'workspace/pointer mismatch: '+name
        cache=git_dir/'lfs/objects'/oid[:2]/oid[2:4]/oid
        assert cache.is_file() and cache.stat().st_size==size and sha(cache)==oid,'corrupt or missing local LFS object: '+name
        entries.append(dict(file=name,oid=oid,bytes=size,workspaceMatches=True,localCacheMatches=True))
    return dict(scope='STAGED_MEDIA_INTEGRITY_NOT_VISUAL_APPROVAL',stagedMediaPaths=len(entries),uniqueObjects=len({e['oid'] for e in entries}),allMatch=True,repairsPerformed=0,files=entries)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=audit();args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ('stagedMediaPaths','uniqueObjects','allMatch','repairsPerformed')}))
