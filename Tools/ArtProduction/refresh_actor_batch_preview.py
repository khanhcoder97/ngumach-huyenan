"""Refresh selected source metadata for native review without granting approval."""
import argparse,hashlib,json,shutil
from inspect_actor_library import ART,RUN,inspect,binding_sha256,source_approval_matches,covers


def refresh(batch):
    assert batch.isalnum()
    def read(path):return json.loads(path.read_text(encoding='utf8'))
    def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')==batch];assert records,'empty batch'
    review=read(ART/'visual_review.json');approved=set(review['productionApproved']);pins={p['id']:p for p in review['sourceApprovals']}
    holds={h['id']:h['reason'] for h in review['holds']};components={p['id']:p.get('sourceSha256') for p in review.get('componentApprovals',[])}
    structure=read(ART/'structure_report.json');updates={}
    for record in records:
        page=inspect(record);page['bindingSha256']=binding_sha256(page)
        changed=(page['id'] in pins and not source_approval_matches(page,pins[page['id']])) or (page['id'] in components and page['sha256']!=components[page['id']])
        page['productionApproved']=page['id'] in approved and not changed
        page['visualState']='HOLD' if changed else 'APPROVED' if page['productionApproved'] else 'HOLD' if page['id'] in holds else 'AWAITING_VISUAL_REVIEW'
        page['visualNotes']='Approved source or registration changed; native visual review required again.' if changed else holds.get(page['id'],'')
        updates[page['id']]=page
    assert set(updates)<={p['id'] for p in structure['pages']},'promote new IDs before refreshing'
    for r in records:
        page=updates[r['id']];shutil.copyfile(ART/r['source'],RUN/page['file'])
        assert hashlib.sha256((RUN/page['file']).read_bytes()).hexdigest()==page['sha256']
    structure['pages']=[updates.get(p['id'],p) for p in structure['pages']]
    save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json');pages=structure['pages']
    pending=[j['id'] for j in jobs if not covers(j,pages)]
    coverage.update(structurePassed=len(pages),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,
                    productionApprovedPages=sum(covers(j,pages,True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in pages),
                    complete=all(covers(j,pages,True) for j in jobs) and not structure['rejected'])
    save(ART/'coverage.json',coverage)
    print(json.dumps(dict(batch=batch,refreshed=len(updates),approved=sum(p['productionApproved'] for p in updates.values()),note='Native review required; approval pins unchanged. Full final inspector check remains required.')))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);args=parser.parse_args();refresh(args.batch)
