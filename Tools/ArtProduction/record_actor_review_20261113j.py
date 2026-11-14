"""Apply a separately completed human/model visual-review ledger, never infer approval from geometry."""
import hashlib,json
from pathlib import Path
from inspect_actor_library import binding_sha256,covers
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';RUN=ROOT/'ClientGodot/assets/actor_library_v1';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113j'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':
    review=read(ART/'visual_review.json');baseline=read(EV/'baseline_preservation.json')
    assert review['sourceApprovals']==baseline['approvedSourcePins'],'One-time ledger already applied or prior pins changed'
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'] is True
    records=read(ART/'generation_records.json');selected=[r for r in records if r.get('batch')=='20261113j']
    structure=read(ART/'structure_report.json');pages={p['id']:p for p in structure['pages']};entries={e['id']:e for e in ledger['entries']}
    assert len(selected)==len(entries)==21 and set(entries)=={r['id'] for r in selected}
    # Validate every entry before changing any source approval.
    for r in selected:
        p=pages[r['id']];e=entries[r['id']]
        assert e['sourceSha256']==p['sha256']==hashlib.sha256((ART/r['source']).read_bytes()).hexdigest()
        assert e['bindingSha256']==p['bindingSha256']==binding_sha256(p)
        assert e['reviewedSourceFrames']==16 and e['nativeReviewed'] and e['visualNotes']
        assert all((ROOT/f).is_file() for f in e['nativeEvidence'])
    for r in selected:
        p=pages[r['id']];e=entries[r['id']]
        if e['productionApproved']:
            assert r['id'] not in review['productionApproved']
            review['productionApproved'].append(r['id'])
            review['sourceApprovals'].append(dict(id=r['id'],sourceSha256=p['sha256'],bindingSha256=p['bindingSha256'],
                reviewedSourceFrames=16,sourceSheet=e['sourceSheet'],nativeEvidence=e['nativeEvidence'],
                scope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE',evidence=e['nativeEvidence'][2],
                method=e['visualNotes'],reviewScale='88px library;100px mobility chain;Studio fit plus native pixel-scale canvas crop',
                batch='20261113j',reviewDate=ledger['reviewDate']))
            for hold in [h for h in review['holds'] if h['id']==r['id']]:
                review['historicalHolds'].append({**hold,'resolvedByBatch':'20261113j','replacementSourceSha256':p['sha256'],
                    'resolution':e['visualNotes'],'originalHeldSource':'Sheets/class_anh_dao_walk_e_v1_20261113i.png'})
            review['holds']=[h for h in review['holds'] if h['id']!=r['id']]
            p.update(productionApproved=True,visualState='APPROVED',visualNotes='');r['status']='SOURCE_NATIVE_VISUAL_REVIEWED'
        else:
            p.update(productionApproved=False,visualState='HOLD',visualNotes=e['visualNotes']);r['status']='SOURCE_NATIVE_REVIEW_HOLD'
            review['holds']=[h for h in review['holds'] if h['id']!=r['id']]+[dict(id=r['id'],reason=e['visualNotes'])]
    save(ART/'generation_records.json',records);save(ART/'visual_review.json',review)
    save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json')
    coverage.update(productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage)
    receipt=read(ART/'candidate_20261113j_receipt.json');receipt.update(sourceReviewPending=False,newSourceApprovals=sum(e['productionApproved'] for e in entries.values()),
        newSourceHolds=sum(not e['productionApproved'] for e in entries.values()),heldIds=[e['id'] for e in entries.values() if not e['productionApproved']],
        nativeReview='Implementation/Reports/Evidence/Actor_Batch_20261113j/source_native_review.json')
    save(ART/'candidate_20261113j_receipt.json',receipt)
    print(json.dumps(dict(sourcePins=len(review['sourceApprovals']),approvedJobs=coverage['productionApprovedPages'],newApprovals=receipt['newSourceApprovals'],newHolds=receipt['newSourceHolds'])))
