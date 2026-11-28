"""Review-only trail/impact/stop origins, retaining the earlier native captures."""
import json
import shutil
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, EV, read, save, sha


def calibrate():
    path=ART/'registration_overrides_20261116c.json';overrides=read(path)
    sources={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    proposals=[]
    for part in ('dash_trail','hit_impact','stop_dust'):
        identifier='sk_tc_05_'+part+'_component'
        registration=EV/'Candidate_Studio'/identifier/'source_registration.json';entry=read(registration);record=entry['record']
        assert sha(ART/record['source'])==record['sourceSha256']==sources[identifier]['sourceSha256']
        pivots=[]
        for frame in entry['page']['directions'][0]['frames']:
            left,top,right,bottom=frame['bounds'];width,height=frame['rect'][2:]
            if part=='dash_trail':
                pivot=[right-1,bottom-1];method='BACKWARD_TRAIL_FRONT_RIGHT_BASELINE_PROPOSAL'
            elif part=='stop_dust':
                pivot=[(left+right)/2,bottom-1];method='SMALL_STOP_DUST_BASELINE_PROPOSAL'
            else:
                pivot=[(left+right)/2,(top+bottom)/2];method='RADIAL_IMPACT_ENVELOPE_CENTRE_PROPOSAL'
            assert 0<=pivot[0]<width and 0<=pivot[1]<height
            pivots.append(pivot)
        fields=dict(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots,registrationMethod=method+'_NOT_APPROVED')
        previous=next((e for e in overrides['entries'] if e['id']==identifier),None)
        if previous and previous['sourceSha256']==record['sourceSha256'] and previous['fields']==fields:continue
        archive=EV/'DashFxCellCentre0'/identifier;archive.mkdir(parents=True,exist_ok=True);pins=[]
        for source in list(EV.glob('raw_'+identifier+'*'))+[registration,registration.with_name('project.json')]:
            destination=archive/source.name
            if destination.exists():assert sha(destination)==sha(source),'Do not overwrite an older review archive'
            else:shutil.copyfile(source,destination)
            pins.append(dict(path=destination.relative_to(ROOT).as_posix(),sha256=sha(destination)))
        save(archive/'archive_receipt.json',dict(scope='SUPERSEDED_CELL_CENTRE_PREVIEW_NOT_ART_APPROVAL',files=pins))
        proposals.append(dict(id=identifier,sourceSha256=record['sourceSha256'],reviewNote='Original4x4 viewed. Cell-centre drift is replaced with a trail front/baseline or low radial footprint proposal. Source PNG stays immutable. Last asymmetric impact debris and exact emitter position may still need hand tuning in whole-skill assembly. No contact,damage,terrain or root authority is inferred from art.',fields=fields))
    for proposal in proposals:overrides['entries']=[e for e in overrides['entries'] if e['id']!=proposal['id']]+[proposal]
    save(path,overrides)
    print(json.dumps(dict(originProposals=len(proposals),originalPngsUnchanged=True,productionApproved=False)))


if __name__=='__main__':calibrate()
