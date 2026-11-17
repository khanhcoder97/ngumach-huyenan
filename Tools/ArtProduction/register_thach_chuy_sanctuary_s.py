"""Register the viewed south sanctuary sheet while its hammer covers the sash."""
from PIL import Image

from prepare_thach_chuy_candidates_20261116c import (
    ART, boot_contact, head_landmark, inspect, neutral_foot_center, read, save, sha,
)


def set_override(identifier, source_sha, fields, note):
    path = ART / 'registration_overrides_20261116c.json'
    overrides = read(path)
    entry = dict(id=identifier, sourceSha256=source_sha, fields=fields, reviewNote=note)
    overrides['entries'] = [item for item in overrides['entries'] if item['id'] != identifier] + [entry]
    save(path, overrides)


def register_south():
    identifier = 'class_thach_chuy_skill_06_s'
    source_sha = 'cd4d43da5064a2b1f6a04b234c9ffc27f04ad6595af7471b589c1744f84bd4da'
    manifest = read(ART / 'Candidates_20261116c/candidate_manifest.json')
    record = next(item for item in manifest['records'] if item['id'] == identifier)
    source = ART / record['source']
    assert record['sourceSha256'] == sha(source) == source_sha
    frames = inspect(record)['directions'][0]['frames']
    height = frames[0]['bounds'][3] - frames[0]['bounds'][1]
    pivots = []
    with Image.open(source) as atlas:
        for index, frame in enumerate(frames):
            x, y, width, cell_height = frame['rect']
            region = atlas.crop((x, y, x + width, y + cell_height))
            head = head_landmark(region, frame['bounds'])
            root_x, sole_y = boot_contact(region, head['top'], height)
            if index == 0:
                neutral_bottom = frame['bounds'][3]
                sole_offset = neutral_bottom - sole_y
                assert sole_offset == 5
                center_offset = neutral_foot_center(region, neutral_bottom, height) - root_x
            # Both warm boot silhouettes are visible on either side of the
            # planted hammer in the original. Keep the low hammer out of Y.
            pivot = [root_x + center_offset, sole_y + sole_offset]
            assert 0 <= pivot[0] < width and 0 < pivot[1] <= cell_height
            pivots.append(pivot)
    assert len(pivots) == 16
    fields = dict(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=pivots,
                  bodyReferenceHeight=height,
                  registrationMethod='SOUTH_SANCTUARY_VISIBLE_BOOTS_PENDING_NATIVE_REVIEW')
    set_override(identifier, source_sha, fields, 'Both boots remain visible when the planted hammer covers the red sash. Use the reviewed boot envelope and neutral sole/centre offsets for this PNG. Confirm contact and idle transition in Studio before gameplay integration.')
    print(f'Registered {len(pivots)} south sanctuary pivot proposals.')


def register_southeast():
    identifier = 'class_thach_chuy_skill_06_se'
    source_sha = '29a189053cfbbfde100d5da37cbd16a3270a1ebfacfd2fad924fff384ceb9d5f'
    records = read(ART / 'Candidates_20261116c/candidate_manifest.json')['records']
    record = next(item for item in records if item['id'] == identifier)
    assert sha(ART / record['source']) == record['sourceSha256'] == source_sha
    frames = inspect(record)['directions'][0]['frames']
    # Local source-cell coordinates reviewed on the atlas. During the low
    # brace (8–11) the hammer obscures the far foot. Use the stance midpoint
    # and visible near sole, rather than moving the actor to that sole's X.
    pivots = [
        [189,245], [186,245], [184,245], [185,244],
        [188,244], [191,243], [189,244], [187,244],
        [179,237], [182,238], [175,239], [181,238],
        [185,241], [185,243], [183,242], [184,243],
    ]
    for frame, (x, y) in zip(frames, pivots, strict=True):
        left, _, right, bottom = frame['bounds']
        assert left < x < right and 0 <= bottom - y <= 8
    fields = dict(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=pivots,
                  bodyReferenceHeight=frames[0]['bounds'][3] - frames[0]['bounds'][1],
                  registrationMethod='SOUTHEAST_SANCTUARY_HAND_CHECKED_STANCE_PROPOSAL')
    set_override(identifier, source_sha, fields, 'Warm-mask X jumps from two boots to one when the hammer covers the far boot. These reviewed source-cell proposals keep the stance midpoint. Confirm contact and recovery in the native clip.')
    print(f'Registered {len(pivots)} southeast sanctuary pivot proposals.')


def register_northeast():
    identifier = 'class_thach_chuy_skill_06_ne'
    source_sha = '903a90565b57cb2442212c7909ca7b15343d74fb69b454f380b87cd38063bc13'
    records = read(ART / 'Candidates_20261116c/candidate_manifest.json')['records']
    record = next(item for item in records if item['id'] == identifier)
    assert sha(ART / record['source']) == record['sourceSha256'] == source_sha
    grid = dict(columns=[0,311,615,917,1230], rows=[0,291,638,933,1278])
    frames = inspect(dict(record, gridEdges=grid))['directions'][0]['frames']
    # Keep the stance centre between the boot silhouettes. During the
    # lowered brace, the near sole stays slightly below the trailing sole.
    pivots = [
        [124,262], [130,264], [134,264], [137,264],
        [130,292], [128,292], [129,293], [114,293],
        [114,242], [110,243], [108,243], [114,244],
        [120,275], [121,275], [122,276], [130,276],
    ]
    for frame, (x, y) in zip(frames, pivots, strict=True):
        left, _, right, bottom = frame['bounds']
        assert left < x < right and 0 <= bottom - y <= 3
    fields = dict(gridEdges=grid, pivotMode='SOURCE_FOOT_PIVOTS',
                  sourceFootPivots=pivots,
                  bodyReferenceHeight=frames[0]['bounds'][3] - frames[0]['bounds'][1],
                  registrationMethod='NORTHEAST_SANCTUARY_HAND_CHECKED_STANCE_PROPOSAL')
    set_override(identifier, source_sha, fields, 'The top of the raised hammer needs unequal row gutters. Warm-mask X alternates across boots. Use hand-checked stance centres and verify the low brace and recovery in Studio.')
    print(f'Registered {len(pivots)} northeast sanctuary pivot proposals.')


if __name__ == '__main__':
    register_south()
    register_southeast()
    register_northeast()
