"""Register and assemble original five-shot Liên Châu art for Studio."""
from math import cos, radians, sin
from statistics import median

from PIL import Image

from build_linh_cung_khoa_mach_preview import TARGET
from prepare_linh_cung_day_gai import FACINGS, document, layer, place_texture, pose
from prepare_linh_cung_khoa_mach_review import projectile_tip_pivots
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118c'
OUTPUT = ROOT / 'Implementation/Reports/Evidence' / ('Actor_Batch_' + BATCH)
ASSEMBLIES = OUTPUT / 'LienChau'
ARROW = 'sk_lc_03_volley_arrow_component'
NOCK = 'sk_lc_03_volley_nock_component'
SOURCE_MS = (70, 60, 50, 45, 25, 40, 45, 25, 40, 45, 65, 45, 65, 45, 65, 80)
RELEASE_POSES = (3, 6, 9, 11, 13)
RELEASE_MS = tuple(sum(SOURCE_MS[:i]) for i in RELEASE_POSES)
SPREAD = (0, -6, 6, -3, 3)

# The local source windows are centered on the visible bow-grip fist at
# each release. Alpha and warm highlights narrow the measured socket.
GRIPS = {
    'E': ('cd497363bfec92eb7c7ac84e40c66441a3e734b64d8cc6eb981ab773bb636e5c',
          ((243, 188), (243, 183), (242, 178), (246, 181), (244, 178))),
    'S': ('a94d0db27bae855f925ad4eb0d6bff319811e43afeebf03de1ae996c0327d914',
          ((233, 198), (234, 204), (238, 194), (232, 195), (238, 195))),
    'N': ('78c8076d30114861e1626809179a1c985f939efe92f4486a0d00c97718d6b239',
          ((77, 151), (77, 150), (80, 151), (79, 151), (79, 154))),
    'W': ('ff59d86e844fcf609b374ab2bf485be3b253f83575ab23f72bcac3805e32d46d',
          ((81, 199), (82, 198), (80, 197), (82, 196), (82, 194))),
    'SE': ('f6f34b4aa34fbcc978fe2121e77fa910461d62797c5c2362946dd05f9a60efd5',
           ((241, 216), (243, 213), (244, 201), (244, 200), (237, 190))),
    'SW': ('cc696cd1b9ceb21d40be0abd208b3909d8acd8aaebdaf025b008d32c9d56c7f8',
           ((69, 221), (65, 218), (63, 215), (64, 212), (68, 219))),
    'NE': ('1d19e73f23654c09ee41bfb942e9a01cf0d94679fa46ed3cb108e23e7b9c5de9',
           ((219, 125), (232, 120), (232, 118), (232, 120), (228, 154))),
    'NW': ('43047c72a57edbb1ec9b98c8f4f9649944e91dc00abce9b3d7de7d94f412a693',
           ((49, 164), (58, 149), (54, 146), (54, 149), (63, 141))),
}
EFFECT_PINS = {
    ARROW: '3b98da2dbcff586579cdc16c6f9c4582607fc3aae62bc540af2d01718c839b0b',
    NOCK: '84745457b8ddb86e5b694c9aa045cdefbd8394a3f80ccfb9af76d9f17e49b317',
}


def calibrate(record, frames, source):
    identifier = record['id']
    facing = record.get('direction')
    with Image.open(source) as image:
        alpha = image.getchannel('A')
        halo = alpha.point(lambda value: 255 if value >= 64 else 0)
        for frame in frames:
            x, y, w, h = frame['rect']
            left, top, right, bottom = halo.crop((x, y, x + w, y + h)).getbbox()
            assert min(left, top, w - right, h - bottom) >= 2, identifier
        if facing:
            digest, grips = GRIPS[facing]
            assert digest == record['sourceSha256']
            mask = alpha.point(lambda value: 255 if value >= 200 else 0)
            pivots = []
            for frame in frames:
                x, y, width, _ = frame['rect']
                bottom = frame['bounds'][3]
                feet = mask.crop((x, y + bottom - 13, x + width, y + bottom)).getbbox()
                assert feet
                pivots.append([(feet[0] + feet[2]) / 2, bottom])
            release = []
            for frame_index, (centre_x, centre_y) in zip(RELEASE_POSES, grips):
                x, y, _, _ = frames[frame_index]['rect']
                margin = 18
                left, top = centre_x - margin, centre_y - margin
                patch = image.crop((x + left, y + top, x + centre_x + margin, y + centre_y + margin))
                pixels = patch.get_flattened_data() if hasattr(patch, 'get_flattened_data') else patch.getdata()
                skin = [(left + i % patch.width, top + i // patch.width) for i, (r, g, b, a) in enumerate(pixels)
                        if a >= 180 and r >= 163 and 12 <= r - g <= 67 and 5 <= g - b <= 60 and b >= 90]
                assert len(skin) >= 16, (identifier, frame_index)
                release.append([median(p[i] for p in skin) for i in (0, 1)])
            return dict(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=pivots,
                        bodyReferenceHeight=pivots[0][1] - frames[0]['bounds'][1]), release
    assert EFFECT_PINS[identifier] == record['sourceSha256']
    if identifier == ARROW:
        points = projectile_tip_pivots(frames, source)
    else:
        points = [[(left + right) / 2, (top + bottom) / 2] for left, top, right, bottom in
                  (frame['bounds'] for frame in frames)]
    return dict(pivotMode='SOURCE_PIVOTS', sourcePivots=points), []


def track(identifier, poses):
    # Step-evaluated holds only need a key when a value changes.
    keys = []
    for index, value in enumerate(poses):
        if not keys or value != keys[-1]['Pose']:
            keys.append(dict(Frame=index, Pose=value))
    return dict(LayerId=identifier, Interpolate=False, Keys=keys)


def make_clip(name, facing, durations, tracks, markers=(), loop=False):
    return dict(Name=name, Direction=facing, Loop=loop, DurationsMs=list(durations),
                Tracks=tracks, Markers=list(markers),
                SourceNote='Liên Châu · từng mũi tên và đốm tích tên có lớp riêng.')


def prepare():
    manifest = read(ART / ('Candidates_' + BATCH) / 'candidate_manifest.json')
    records, entries = {}, []
    for candidate in manifest['records']:
        record = dict(candidate)
        identifier = record['id']
        source = ART / record['source']
        digest = sha(source)
        assert digest == record['sourceSha256']
        raw, = inspect(record)['directions']
        geometry, release = calibrate(record, raw['frames'], source)
        record.update(geometry)
        page = inspect(record)
        direction, = page['directions']
        frames = direction['frames']
        timing = record['sourceFrameDurationsMs']
        bundle = OUTPUT / 'Candidate_Studio' / identifier
        texture = place_texture(bundle, source, digest)
        scale = 140 / direction['referenceHeight']
        layer_track = track(identifier, (pose(frame, index, scale) for index, frame in enumerate(frames)))
        drawing = layer(identifier, frames, texture, layer_track['Keys'][0]['Pose'])
        loop = record.get('previewLoop', False)
        project = document(bundle, identifier, [drawing],
                           [make_clip(identifier, direction['direction'], timing, [layer_track], loop=loop)])
        save(bundle / 'source_registration.json', dict(record=record, page=page, releaseSourcePoints=release,
                                                       productionApproved=False))
        entries.append(dict(id=identifier, project=project.relative_to(ROOT).as_posix(),
                            source=source.relative_to(ROOT).as_posix(), sourceSha256=digest,
                            timing=timing, loop=loop))
        records[identifier] = (source, digest, direction, release)
    assert len(records) == len(GRIPS) + len(EFFECT_PINS) == manifest['expectedSourcePages']
    save(OUTPUT / 'candidate_review_plan.json',
         dict(batch=BATCH, selected=len(entries), expected=manifest['expectedSourcePages'],
              catalogueUnchanged=True, entries=entries))
    return records


def vector(angle):
    return cos(radians(angle)), sin(radians(angle))


def assemble(facing, sources):
    bundle = ASSEMBLIES / facing
    body_id = 'class_linh_cung_skill_03_' + facing.lower()
    angle = -90 + FACINGS.index(facing) * 45
    forward = vector(angle)
    across = vector(angle + 90)
    body_scale = 110 / sources[body_id][2]['referenceHeight']
    caster = (-102 * forward[0], 30 - 80 * forward[1])
    body_frames = sources[body_id][2]['frames']
    release_points = []
    for phase, measured in zip(RELEASE_POSES, sources[body_id][3]):
        pivot = body_frames[phase]['pivot']
        release_points.append(tuple(caster[i] + (measured[i] - pivot[i]) * body_scale + forward[i] * 6
                                    for i in (0, 1)))
    # Range here is authored for review readability. All five effects have
    # distinct flights. Gameplay contact is evaluated separately.
    target_foot = (release_points[0][0] + 182 * forward[0], release_points[0][1] + 182 * forward[1] + 31)
    ends = [t + 320 for t in RELEASE_MS]
    boundaries = sorted({0, 70, 1040, *[sum(SOURCE_MS[:i]) for i in range(17)],
                         *[t + delta for t in RELEASE_MS for delta in range(0, 321, 20)],
                         *range(70, RELEASE_MS[-1], 30), *range(0, 1041, 100)})
    durations = [b - a for a, b in zip(boundaries, boundaries[1:])]
    assert len(durations) <= 120 and min(durations) >= 5
    centres = [(a + b) / 2 for a, b in zip(boundaries, boundaries[1:])]
    drawings, tracks = [], []

    def bind(identifier, source_id, z, scale, sample):
        source, digest, direction, _ = sources[source_id]
        frames = direction['frames']
        animation = track(identifier, (pose(frames[phase], phase, scale, point, alpha) | {'Angle': rotation}
                                       for phase, point, alpha, rotation in map(sample, centres)))
        texture = place_texture(bundle, source, digest)
        drawings.append(layer(identifier, frames, texture, animation['Keys'][0]['Pose'], z))
        tracks.append(animation)

    body_ends = [sum(SOURCE_MS[:i]) for i in range(1, 17)]
    bind(body_id, body_id, 0, body_scale,
         lambda t: (min(15, sum(t >= end for end in body_ends)), caster, 1, 0))
    bind(TARGET, TARGET, 0, 74 / sources[TARGET][2]['referenceHeight'],
         lambda t: (int(t // 100), target_foot, 1, 0))
    for i, (start, stop, move) in enumerate(zip(RELEASE_MS, ends, SPREAD)):
        start_point = release_points[i]
        facing_angle = angle + move
        path = vector(facing_angle)
        dot_point = tuple(release_points[0][axis] - 13 * forward[axis] + (i - 2) * 10 * across[axis]
                          for axis in (0, 1))

        def nock(t):
            return min(15, int(max(0, t - 70) // 30)), dot_point, int(70 <= t < start), 0

        def projectile(t):
            delta = max(0, t - start)
            point = tuple(start_point[axis] + 182 * path[axis] * delta / 320 for axis in (0, 1))
            return min(15, int(delta // 20)), point, int(start <= t < stop), facing_angle

        bind(f'nock_{i+1}', NOCK, 4, 9 / sources[NOCK][2]['referenceHeight'], nock)
        bind(f'arrow_{i+1}', ARROW, 4, 32 / sources[ARROW][2]['referenceHeight'], projectile)
    markers = [dict(Name=f'arrow_release_{i+1}', Kind='vfx', Frame=boundaries.index(start),
                    X=release_points[i][0], Y=release_points[i][1], Radius=0) for i, start in enumerate(RELEASE_MS)]
    path = document(bundle, 'Liên Châu · ' + facing, drawings,
                    [make_clip('Liên Châu', facing, durations, tracks, markers)])
    save(bundle / 'assembly_descriptor.json',
         dict(projectSha256=sha(path), releaseMs=list(RELEASE_MS), releaseSourcePose=list(RELEASE_POSES),
              releasePositions=[list(point) for point in release_points], spreadDegrees=list(SPREAD), reviewFlightMs=320,
              artOnly=True))


if __name__ == '__main__':
    assets = prepare()
    pins = {item['id']: item['sourceSha256'] for item in read(ART / 'visual_review.json')['sourceApprovals']}
    target = next(record for record in read(ART / 'generation_records.json') if record['id'] == TARGET)
    png = ART / target['source']
    digest = sha(png)
    assert digest == pins[TARGET]
    direction, = inspect(target)['directions']
    assets[TARGET] = (png, digest, direction, [])
    for view in FACINGS:
        assemble(view, assets)
    print('Registered ten original atlases and eight editable five-shot Liên Châu projects.')
