"""Source-specific, review-only boot registration; never changes pixels."""
import json
from inspect_actor_library import ART, inspect
from prepare_thach_chuy_candidates_20261116c import read, save, sha

identifier = 'class_thach_chuy_skill_04_ne'
manifest = read(ART / 'Candidates_20261116c/candidate_manifest.json')
record = next(r for r in manifest['records'] if r['id'] == identifier)
assert record['source'].endswith('class_thach_chuy_skill_04_ne_v1_20261116c.png')
assert sha(ART / record['source']) == record['sourceSha256']
frames = inspect(record)['directions'][0]['frames']
# Original whole atlas manually inspected. These lower boot envelopes include
# the dark outline which the shared saturated-warm classifier misses. Hammer
# pixels are excluded from the near-boot band. Contact still needs native QA.
lower_boot_bands = [
    [242,177,212], [241,172,206], [243,169,202], [242,166,224],
    [244,168,224], [241,167,203], [241,167,204], [241,167,200],
    [241,171,208], [241,172,208], [241,171,206], [241,169,203],
    [240,173,210], [240,173,211], [240,174,212], [240,175,212],
]
pivots = [[(left+right)/2, bottom+1] for bottom,left,right in lower_boot_bands]
for frame, (x,y) in zip(frames,pivots):
    assert 0 <= x < frame['rect'][2] and 0 < y <= frame['rect'][3]
    assert abs(y-frame['bounds'][3]) <= 3
fields = dict(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=pivots,
              bodyReferenceHeight=frames[0]['bounds'][3]-frames[0]['bounds'][1],
              registrationMethod='SOURCE_SPECIFIC_NEAR_BOOT_DARK_SOLE_BAND_PENDING_FIXED_CAMERA_NATIVE_REVIEW')
entry = dict(id=identifier, sourceSha256=record['sourceSha256'],
             reviewNote='Original4x4 manually viewed. Automatic neutral sole guard failed: warm colour detection omitted9px of dark sole. Source-specific boot-band proposals preserve immutable PNG. This only fixes geometry registration; root sway, far-boot balance and cross-action seam remain unaccepted.',
             fields=fields)
path = ART / 'registration_overrides_20261116c.json'
overrides = read(path)
overrides['entries'] = [e for e in overrides['entries'] if e['id'] != identifier] + [entry]
save(path,overrides)
print(json.dumps(dict(id=identifier, sourceSha256=record['sourceSha256'], pivots=pivots, productionApproved=False)))
