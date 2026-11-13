"""Apply a completed source/native ledger; geometry alone cannot approve artwork."""
import argparse,hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def apply(batch):
    assert batch.isalnum(),'invalid batch'
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch)
    baseline=read(ev/'baseline_preservation.json');ledger=read(ev/'source_native_review.json');review=read(ART/'visual_review.json')
    assert ledger['manualReviewComplete'] is True and ledger['batch']==batch
    assert review['sourceApprovals']==baseline['approvedSourcePins'],'Ledger already applied or prior pins changed'
    records=read(ART/'generation_records.json');selected=[r for r in records if r.get('batch')==batch]
    entries={e['id']:e for e in ledger['entries']};structure=read(ART/'structure_report.json');pages={p['id']:p for p in structure['pages']}
    assert len(entries)==len(selected) and set(entries)=={r['id'] for r in selected} and selected
    checked={}
    # Validate the complete ledger before writing approval state.
    for r in selected:
        p=pages[r['id']];e=entries[r['id']]
        assert e['sourceSha256']==p['sha256']==sha(ART/r['source'])
        assert e['bindingSha256']==p['bindingSha256']==binding_sha256(p)
        assert e['reviewedSourceFrames']==p['sourceFrames']==16 and e['nativeReviewed'] and e['visualNotes']
        assert type(e['productionApproved']) is bool and e['id'] not in review['productionApproved']
        assert set(e['nativeEvidence'])==set(e['nativeEvidenceSha256'])
        for f in e['nativeEvidence']:
            path=(ROOT/f).resolve();assert path.is_relative_to(ev.resolve()) and path.is_file(),'evidence outside batch'
            if f not in checked:checked[f]=sha(path)
            assert checked[f]==e['nativeEvidenceSha256'][f],'native evidence changed after review'
    for r in selected:
        p=pages[r['id']];e=entries[r['id']]
        if e['productionApproved']:
            review['productionApproved'].append(r['id'])
            review['sourceApprovals'].append(dict(id=r['id'],sourceSha256=p['sha256'],bindingSha256=p['bindingSha256'],
                reviewedSourceFrames=16,sourceSheet=e['sourceSheet'],nativeEvidence=e['nativeEvidence'],nativeEvidenceSha256=e['nativeEvidenceSha256'],
                scope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE',evidence=e['nativeEvidence'][2],
                method=e['visualNotes'],reviewScale=ledger['reviewScale'],batch=batch,reviewDate=ledger['reviewDate']))
            for h in [h for h in review['holds'] if h['id']==r['id']]:
                review['historicalHolds'].append({**h,'resolvedByBatch':batch,'replacementSourceSha256':p['sha256'],'resolution':e['visualNotes']})
            review['holds']=[h for h in review['holds'] if h['id']!=r['id']]
            p.update(productionApproved=True,visualState='APPROVED',visualNotes='');r['status']='SOURCE_NATIVE_VISUAL_REVIEWED'
        else:
            review['holds']=[h for h in review['holds'] if h['id']!=r['id']]+[dict(id=r['id'],reason=e['visualNotes'])]
            p.update(productionApproved=False,visualState='HOLD',visualNotes=e['visualNotes']);r['status']='SOURCE_NATIVE_REVIEW_HOLD'
    save(ART/'generation_records.json',records);save(ART/'visual_review.json',review);save(ART/'structure_report.json',structure)
    save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json')
    coverage.update(productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage)
    receipt=read(ART/('candidate_'+batch+'_receipt.json'));receipt.update(sourceReviewPending=False,
        newSourceApprovals=sum(e['productionApproved'] for e in entries.values()),newSourceHolds=sum(not e['productionApproved'] for e in entries.values()),
        heldIds=[e['id'] for e in entries.values() if not e['productionApproved']],nativeReview='Implementation/Reports/Evidence/Actor_Batch_'+batch+'/source_native_review.json')
    save(ART/('candidate_'+batch+'_receipt.json'),receipt)
    print(json.dumps(dict(batch=batch,newSourceApprovals=receipt['newSourceApprovals'],newSourceHolds=receipt['newSourceHolds'],sourcePins=len(review['sourceApprovals']),sourceReviewedJobs=coverage['productionApprovedPages'])))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);args=parser.parse_args();apply(args.batch)
