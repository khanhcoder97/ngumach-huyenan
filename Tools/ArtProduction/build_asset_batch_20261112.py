"""Inventory the selected original sheets, explicit partial blocks and separate VFX components."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Actor_Library_20261107'


def build(batch='20261112'):
    records=[r for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8')) if r.get('batch')==batch]
    assert records,'unknown or empty batch'
    pages={p['id']:p for p in json.loads((ART/'structure_report.json').read_text(encoding='utf8'))['pages']}
    entries=[]
    for r in records:
        p=pages[r['id']]  # Fail instead of silently dropping rejected selections.
        source=ART/r['source'];runtime=ROOT/'ClientGodot/assets/actor_library_v1'/p['file']
        assert source.read_bytes()==runtime.read_bytes(),'runtime copy differs'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==p['sha256'],'source hash differs'
        assert (ART/r['prompt']).is_file(),'missing final prompt'
        native=[d for d in p['directions'] if not d['flip']]
        assert all(len(d['frames'])==16 for d in native),'wrong source-frame count'
        entries.append(dict(id=r['id'],source=r['source'],prompt=r['prompt'],runtime='ClientGodot/assets/actor_library_v1/'+p['file'],
                            sha256=p['sha256'],sourceCells=p['sourceFrames'],boundSourceCells=sum(len(d['frames']) for d in native),
                            unboundSourceCells=p.get('unboundSourceFrames',0),authoredDirections=[d['direction'] for d in native],
                            mirroredDirections=[d['direction'] for d in p['directions'] if d['flip']],componentOnly=bool(r.get('componentOnly')),
                            productionApproved=p['productionApproved'],visualState=p['visualState']))
    baseline=json.loads((ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json').read_text(encoding='utf8'))
    preserved=all((ROOT/r['file']).is_file() and hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['expectedSha256'] for r in baseline['files'])
    assert preserved,'owner-selected old sheet changed'
    coverage=json.loads((ART/'coverage.json').read_text(encoding='utf8'))
    return dict(schemaVersion=2,batch=batch,coverageSnapshotPolicy='CURRENT_CATALOG_AT_INVENTORY_BUILD',scope='CONTINUED_BAKED_CHIBI_ASSET_PRODUCTION',ownerStyleLocked=True,
                styleDecision='USER_20261112_CONTINUE_EXISTING_CHIBI_SPRITE_SHEETS',generator='built-in image_gen',
                originalsPreserved=len(baseline['files']),selectedSheets=len(entries),sourceCells=sum(e['sourceCells'] for e in entries),
                boundSourceCells=sum(e['boundSourceCells'] for e in entries),unusedSourceCells=sum(e['unboundSourceCells'] for e in entries),
                sourceFramesPerDirection=16,renderTargetFps=60,entries=entries,
                fullGameComplete=False,requiredJobs=coverage['requiredPages'],structurallyCompleteJobs=coverage['boundRequiredPages'],pendingJobs=coverage['pendingPages'],
                note='Cells/hashes do not certify anatomical pose uniqueness. Production approval remains per source/clip. Unbound cells are never padded into a sequence. Coverage fields describe the current catalogue, not historical progress on the batch date.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--batch',default='20261112');args=parser.parse_args()
    assert args.batch.isalnum(),'batch must be an alphanumeric identifier'
    target=ART/('batch_'+args.batch+'.json')
    result=build(args.batch);text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.check:assert target.read_text(encoding='utf8')==text,'stale batch inventory'
    else:target.write_text(text,encoding='utf8')
    print(json.dumps({k:result[k] for k in ['selectedSheets','sourceCells','boundSourceCells','unusedSourceCells','originalsPreserved','pendingJobs']}))
