"""Preserve a SHA-bound current review before replacing its source or registration."""
import argparse
import json
import re
import shutil
from prepare_thach_chuy_candidates_20261116c import ART, EV, ROOT, read, save, sha


def archive(identifier, name):
    assert re.fullmatch(r'[a-z0-9_]+',identifier)
    assert re.fullmatch(r'[A-Za-z0-9]{1,12}',name),'Use a short archive token to avoid Windows path limits'
    record=next(r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records'] if r['id']==identifier)
    bundle=EV/'Candidate_Studio'/identifier;project=bundle/'project.json';document=read(project)
    registration=bundle/'source_registration.json'
    assert read(registration)['record']['sourceSha256']==record['sourceSha256']==sha(ART/record['source'])
    texture=(bundle/document['Layers'][0]['Texture']).resolve()
    assert texture.is_relative_to(bundle.resolve()) and sha(texture)==record['sourceSha256']
    receipt=read(EV/('raw_'+identifier+'.capture_receipt.json'))
    assert receipt['projectSha256']==sha(project) and receipt['sourceSha256']==record['sourceSha256']
    assert receipt['movieSha256']==sha(EV/('raw_'+identifier+'.mp4'))
    destination=EV/name;destination.mkdir(exist_ok=True)
    assert destination.resolve().is_relative_to(EV.resolve())
    pairs=[(project,destination/'project.json'),(registration,destination/'source_registration.json'),(texture,destination/document['Layers'][0]['Texture'])]
    pairs.extend((p,destination/p.name) for p in EV.glob('raw_'+identifier+'*') if p.is_file())
    pins=[]
    for source,target in pairs:
        assert len(str(target.resolve()))<255,'Choose a shorter archive path'
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert sha(target)==sha(source),'Never replace a different archived artifact'
        else:shutil.copyfile(source,target)
        assert sha(target)==sha(source)
        pins.append(dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target)))
    result=dict(scope='SUPERSEDED_NATIVE_REVIEW_ARCHIVE_NOT_APPROVAL',id=identifier,sourceSha256=record['sourceSha256'],projectSha256=sha(project),movieSha256=receipt['movieSha256'],files=pins,originalPngUnchanged=True)
    save(destination/'archive_receipt.json',result)
    print(json.dumps(dict(id=identifier,archive=destination.relative_to(ROOT).as_posix(),files=len(pins),allHashesMatch=True)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--id',required=True);parser.add_argument('--name',required=True)
    args=parser.parse_args();archive(args.id,args.name)
