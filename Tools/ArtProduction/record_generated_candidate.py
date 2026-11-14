"""Persist a native imagegen PNG and exact prompt; never modifies pixels."""
import argparse,hashlib,json,shutil
from pathlib import Path
from inspect_actor_library import ART,ROOT

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):
    pending=p.with_suffix(p.suffix+'.pending')
    pending.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    assert read(pending)==v
    pending.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def record(job):
    batch=job['batch'];identifier=job['id'];version=job.get('version',1);expected=job['expectedSourcePages']
    assert batch.isalnum() and identifier.replace('_','').isalnum() and type(version) is int and version>0
    assert type(expected) is int and expected>0 and job['prompt'].strip()
    seconds=job['seconds'];timing=job.get('timing',[seconds*1000/16]*16)
    assert len(timing)==16 and all(type(n) in (int,float) and n>0 for n in timing) and abs(sum(timing)-seconds*1000)<1e-5
    folder=ART/('Candidates_'+batch);folder.mkdir(exist_ok=True)
    stem=f'{identifier}_v{version}_{batch}';png=folder/(stem+'.png');prompt=folder/(stem+'.txt')
    native=Path(job['nativeSourceFile']);assert native.is_file() and native.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    if png.exists():assert sha(png)==sha(native),'different source at existing version'
    else:shutil.copyfile(native,png)
    assert sha(png)==sha(native)
    exact=job['prompt'].rstrip()+'\n'
    if prompt.exists():assert prompt.read_text(encoding='utf8')==exact,'prompt differs at existing version'
    else:prompt.write_text(exact,encoding='utf8')
    refs=job['references'];assert refs;inputs=[]
    for ref in refs:
        path=(ROOT/ref).resolve();assert path.is_relative_to(ROOT.resolve()) and path.is_file()
        inputs.append(dict(path=ref,sourceSha256=sha(path)))
    r=dict(id=identifier,source=png.relative_to(ART).as_posix(),prompt=prompt.relative_to(ART).as_posix(),columns=4,rows=4,
           batch=batch,generator='built-in image_gen',status='GENERATED_PENDING_SOURCE_NATIVE_REVIEW',reference=refs[0],
           additionalReferences=refs[1:],generationInputs=inputs,sourceSha256=sha(png),sourceFrameDurationsMs=timing)
    if job.get('direction'):
        r.update(direction=job['direction'],inputRole='OWNER_SELECTED_IDENTITY_AND_NEW_CHOREOGRAPHY_REFERENCE')
        if job.get('layoutVerified'):r.update(layout='VISUALLY_VERIFIED_DIRECTIONAL_GRID',layoutReviewNote='Whole original manually viewed as4x4 body poses; per-cell alpha/crop/duplicate checks retained.')
    else:r.update(componentOnly=True,scaleMode='LONGEST_AXIS',pivotMode='CELL_CENTER',previewDurationSeconds=seconds,
                  previewLoop=job.get('loop',False),inputRole='VFX_STYLE_OR_MECHANIC_REFERENCE')
    path=folder/'candidate_manifest.json'
    m=read(path) if path.exists() else dict(batch=batch,expectedSourcePages=expected,scope=job['scope'],records=[],history=[])
    assert m['expectedSourcePages']==expected
    old=next((i for i,e in enumerate(m['records']) if e['id']==identifier),None)
    if old is None:m['records'].append(r)
    elif m['records'][old]['source']==r['source']:
        assert m['records'][old]['sourceSha256']==r['sourceSha256'],'source recovery mismatch'
        return dict(id=identifier,recoveredExisting=True,selected=len(m['records']))
    else:m['history'].append(m['records'][old]);m['records'][old]=r
    m.update(selected=len(m['records']),generatedVariants=len(m['records'])+len(m['history']),remainingSourcePages=expected-len(m['records']),sourceCells=len(m['records'])*16,productionApproved=False)
    assert m['remainingSourcePages']>=0;save(path,m)
    return dict(id=identifier,file=str(png),selected=m['selected'],remaining=m['remainingSourcePages'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--job',type=Path,required=True);args=parser.parse_args();print(json.dumps(record(read(args.job))))
