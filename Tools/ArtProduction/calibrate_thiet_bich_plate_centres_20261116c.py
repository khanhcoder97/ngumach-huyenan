"""Register centres of already drawn single-plate gain/sustain frames; PNGs stay immutable."""
import json
from inspect_actor_library import ART
from prepare_thach_chuy_candidates_20261116c import save,sha

def calibrate():
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    path=ART/'registration_overrides_20261116c.json';overrides=read(path)
    sources={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    registered={e['record']['id']:e for e in read(ART/'body_registration_20261116c.json')['entries']}
    identifiers=('sk_tc_03_plate_gain_component','sk_tc_03_plate_sustain_component')
    for identifier in identifiers:
        entry=registered[identifier];r=entry['record'];assert sha(ART/r['source'])==sources[identifier]['sourceSha256']==r['sourceSha256']
        frames=entry['page']['directions'][0]['frames'];assert len(frames)==16
        pivots=[[(f['bounds'][0]+f['bounds'][2])/2,(f['bounds'][1]+f['bounds'][3])/2] for f in frames]
        override=dict(id=identifier,sourceSha256=r['sourceSha256'],reviewNote='Whole original atlas viewed. One compact nearly symmetric plate forms or sustains at a fixed body socket. Initial gain native capture showed row-dependent cell-centre offset. Centre the actual plate/assembly envelope in each source cell; native per-pose and loop/phase seam review still required. Not a ground dust origin or an asymmetric travelling projectile.',fields=dict(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots,registrationMethod='SINGLE_PLATE_ENVELOPE_CENTRE_PENDING_NATIVE_REVIEW'))
        overrides['entries']=[e for e in overrides['entries'] if e['id']!=identifier]+[override]
    save(path,overrides);print(json.dumps(dict(plateSources=2,sourcePoses=32,rasterModified=False,productionApproved=False)))
if __name__=='__main__':calibrate()
