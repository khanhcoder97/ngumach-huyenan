"""Centre compact symmetric threat symbols; preserve source PNGs and prior proof."""
import json
import shutil
from inspect_actor_library import ART, ROOT
from prepare_thach_chuy_candidates_20261116c import read, save, sha, EV


def calibrate():
    path = ART / 'registration_overrides_20261116c.json'
    overrides = read(path)
    records = {r['id']:r for r in read(ART / 'Candidates_20261116c/candidate_manifest.json')['records']}
    ids = ('sk_tc_04_caster_pulse_component','sk_tc_04_target_chevron_component','sk_tc_04_target_status_component')
    for identifier in ids:
        registration = EV / 'Candidate_Studio' / identifier / 'source_registration.json'
        entry = read(registration)
        record = entry['record']
        assert sha(ART / record['source']) == records[identifier]['sourceSha256'] == record['sourceSha256']
        frames = entry['page']['directions'][0]['frames']
        assert len(frames) == 16
        pivots = [[(f['bounds'][0]+f['bounds'][2])/2, (f['bounds'][1]+f['bounds'][3])/2] for f in frames]
        fields = dict(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots, registrationMethod='COMPACT_THREAT_SYMBOL_ENVELOPE_CENTRE_PENDING_NATIVE_REVIEW')
        previous = next((e for e in overrides['entries'] if e['id']==identifier),None)
        if previous and previous['sourceSha256']==record['sourceSha256'] and previous['fields']==fields:
            continue
        # Only the pulse had an earlier cell-centre capture. Keep its full proof
        # and project before replacing the metadata and recording a fresh view.
        captures = list(EV.glob('raw_'+identifier+'*'))
        if captures:
            archive = EV / 'TauntSymbolCellCentre0' / identifier
            archive.mkdir(parents=True,exist_ok=True)
            pins = []
            for source in captures + [registration,registration.with_name('project.json')]:
                destination = archive / source.name
                if destination.exists():
                    assert sha(destination)==sha(source), 'Do not overwrite an older archive'
                else:
                    shutil.copyfile(source,destination)
                pins.append(dict(path=destination.relative_to(ROOT).as_posix(),sha256=sha(destination)))
            save(archive/'archive_receipt.json',dict(scope='SUPERSEDED_CELL_CENTRE_REVIEW_NOT_ASSET_APPROVAL',files=pins))
        override = dict(id=identifier, sourceSha256=record['sourceSha256'],
            reviewNote='Whole original4x4 visually inspected. Thin elliptical pulse and compact direction/status glyphs are centred envelopes, not moving projectiles. Cell-centre capture drifted vertically by source row. This metadata centres each visible symbol; actual target/caster anchoring, scale and wide-camera readability remain unaccepted.',fields=fields)
        overrides['entries']=[e for e in overrides['entries'] if e['id']!=identifier]+[override]
    save(path,overrides)
    print(json.dumps(dict(symbolSources=3,rasterModified=False,productionApproved=False)))


if __name__=='__main__':
    calibrate()
