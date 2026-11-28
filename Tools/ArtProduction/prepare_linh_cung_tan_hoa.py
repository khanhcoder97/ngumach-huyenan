"""Register the authored Tán Hoa sources and eight editable Godot timelines."""
from bisect import bisect_right
from itertools import accumulate
from math import atan2, degrees, hypot
from statistics import median

from PIL import Image

from build_linh_cung_khoa_mach_preview import TARGET
from prepare_linh_cung_day_gai import FACINGS, document, layer, place_texture, pose
from prepare_linh_cung_lien_chau import track, vector
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118d'
OUTPUT = ROOT / 'Implementation/Reports/Evidence' / ('Actor_Batch_' + BATCH)
ASSEMBLIES = OUTPUT / 'TanHoa'
FAN = 'sk_lc_04_fan_open_component'
FALL = 'sk_lc_04_fan_fall_component'
RELEASE_POSE = 6
FULL_POSE = 7
FALL_DELAY_MS = 420
SECTOR_DEGREES = 100
REVIEW_REACH = 144

# Local coordinates at cast frame 6. These follow the visible pale skin of
# the bow fist, including the considerably foreshortened southern view.
GRIPS = {
    'N': ('c7f1cb8bff73a0fed486bf108ec5fe11aa45ae325bc58945cbe2ab04f9cf7034', (33, 123)),
    'NE': ('1550895f479b2fb38657348dd209416d1a7fca0102c0df3b7fa975b49f1186ea', (259, 97)),
    'E': ('1999d2e9d9c170afa16c711c35d4564128e3400c6c3e1908d9f0dea2625cafd9', (277, 150)),
    'SE': ('cd1a80c924912a4b52683ec644951ec1c617ab6762f08ba337b7781e97d64998', (261, 192)),
    'S': ('b82b2d1f300b95021988e39080cc3098c0d9cb6d4d44ef5781369282d98f8774', (210, 195)),
    'SW': ('962beb8530a7c4b244971502f1395a47481314d774b1d8b8b2a9f81a6769b798', (49, 223)),
    'W': ('59008423a5cb35b99cd0d3711b764eea44992a15cf6e156a9727cdee3f0157c9', (35, 175)),
    'NW': ('e012e9ae6eb9d7854f09e08bb4fc96d051511b418118236777cc83f238782ab0', (37, 124)),
}
GRID_EDGES = {
    'E': dict(columns=[0, 306, 601, 915, 1243], rows=[0, 318, 627, 936, 1265]),
    'SW': dict(columns=[0, 310, 605, 927, 1267], rows=[0, 308, 620, 935, 1241]),
}
EFFECT_PINS = {
    FAN: 'b0f99c3ef21aa0eeee175271ec49bdd4b497fe4988e830f6c987a2af59f99b02',
    FALL: '563c402cf49e5198562c6432aea9e1af5418ac0e1539f7547e24d5de2ded9b07',
}


def release_socket(atlas, frame, centre):
    x, y, width, height = frame['rect']
    cx, cy = centre
    left, top = max(0, cx - 22), max(0, cy - 24)
    region = atlas.crop((x + left, y + top, x + min(width, cx + 23), y + min(height, cy + 25)))
    pixels = region.get_flattened_data() if hasattr(region, 'get_flattened_data') else region.getdata()
    skin = [(left + i % region.width, top + i // region.width)
            for i, (r, g, b, a) in enumerate(pixels)
            if a >= 180 and r >= 163 and 12 <= r - g <= 67 and 5 <= g - b <= 60 and b >= 90]
    assert len(skin) >= 250
    return [median(axis) for axis in zip(*skin)]


def measure_effect(alpha, frames, identifier):
    if identifier == FALL:
        return [[frame['rect'][2] * .27, frame['rect'][3] * .50] for frame in frames], {}
    pivots = []
    core = alpha.point(lambda value: 255 if value >= 200 else 0)
    for frame in frames:
        x, y, _, height = frame['rect']
        left = frame['bounds'][0]
        root = core.crop((x + left, y, x + left + 13, y + height)).getbbox()
        assert root, 'The fan needs a solid root in its leading edge strip'
        pivots.append([left + 5, (root[1] + root[3]) / 2])

    # Measure the demonstrated opening using the solid outer petals. The
    # canvas transform corrects the aspect/centre and leaves PNG pixels intact.
    x, y, width, height = frames[FULL_POSE]['rect']
    ox, oy = pivots[FULL_POSE]
    cell = core.crop((x, y, x + width, y + height))
    pixels = cell.get_flattened_data() if hasattr(cell, 'get_flattened_data') else cell.getdata()
    points = [(i % width - ox, i // width - oy) for i, value in enumerate(pixels)
              if value and i % width - ox > 28]
    reach = max(hypot(px, py) for px, py in points)
    rim = [(px, py) for px, py in points if hypot(px, py) >= .72 * reach]
    assert min(py for _, py in rim) < 0 < max(py for _, py in rim)
    lower = min(py / px for px, py in rim)
    upper = max(py / px for px, py in rim)
    low, high = .5, 2.5
    for _ in range(30):
        ratio = (low + high) / 2
        if degrees(atan2(upper * ratio, 1) - atan2(lower * ratio, 1)) < SECTOR_DEGREES:
            low = ratio
        else:
            high = ratio
    ratio = round((low + high) / 2, 5)
    minimum, maximum = (degrees(atan2(slope * ratio, 1)) for slope in (lower, upper))
    span = round(maximum - minimum, 2)
    assert abs(span - SECTOR_DEGREES) <= .05
    return pivots, dict(fanRatioY=ratio, sourceAngleCorrection=round(-(minimum + maximum) / 2, 5),
                        sourceReach=round(max(hypot(px, py * ratio) for px, py in points), 4),
                        measuredSectorDegrees=span)


def register(record, source):
    facing = record.get('direction')
    identifier = record['id']
    assert record['sourceSha256'] == sha(source) == (GRIPS[facing][0] if facing else EFFECT_PINS[identifier])
    if facing in GRID_EDGES:
        record['gridEdges'] = GRID_EDGES[facing]
    raw, = inspect(record)['directions']
    frames = raw['frames']
    with Image.open(source) as atlas:
        alpha = atlas.getchannel('A')
        halo = alpha.point(lambda value: 255 if value >= 64 else 0)
        for frame in frames:
            x, y, width, height = frame['rect']
            left, top, right, bottom = halo.crop((x, y, x + width, y + height)).getbbox()
            assert min(left, top, width - right, height - bottom) >= 2, identifier
        if not facing:
            pivots, evidence = measure_effect(alpha, frames, identifier)
            record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots)
            return evidence
        core = alpha.point(lambda value: 255 if value >= 200 else 0)
        feet = []
        for frame in frames:
            x, y, width, _ = frame['rect']
            bottom = frame['bounds'][3]
            soles = core.crop((x, y + bottom - 11, x + width, y + bottom)).getbbox()
            assert soles
            feet.append([(soles[0] + soles[2]) / 2, bottom - 11 + soles[3]])
        record.update(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=feet,
                      bodyReferenceHeight=feet[0][1] - frames[0]['bounds'][1])
        return dict(releasePose=RELEASE_POSE,
                    releaseSourcePoint=release_socket(atlas, frames[RELEASE_POSE], GRIPS[facing][1]))


def make_clip(name, direction, timing, tracks, markers=()):
    return dict(Name=name, Direction=direction, Loop=False, DurationsMs=list(timing), Tracks=tracks,
                Markers=list(markers), SourceNote='Tán Hoa · Quét cung, quạt cánh gỗ và mảnh lá rơi.')


def prepare():
    manifest = read(ART / ('Candidates_' + BATCH) / 'candidate_manifest.json')
    entries, sources = [], {}
    for original in manifest['records']:
        record = dict(original)
        identifier, digest = record['id'], record['sourceSha256']
        source = ART / record['source']
        metadata = register(record, source)
        page = inspect(record)
        direction, = page['directions']
        frames, timing = direction['frames'], record['sourceFrameDurationsMs']
        bundle = OUTPUT / 'Candidate_Studio' / identifier
        texture = place_texture(bundle, source, digest)
        scale = 140 / direction['referenceHeight']
        motion = track(identifier, (pose(frame, i, scale) for i, frame in enumerate(frames)))
        drawing = layer(identifier, frames, texture, motion['Keys'][0]['Pose'])
        path = document(bundle, identifier, [drawing],
                        [make_clip(identifier, direction['direction'], timing, [motion])])
        save(bundle / 'source_registration.json', dict(record=record, page=page, **metadata,
                                                       productionApproved=False))
        entries.append(dict(id=identifier, project=path.relative_to(ROOT).as_posix(),
                            source=source.relative_to(ROOT).as_posix(), sourceSha256=digest,
                            timing=timing, loop=False))
        sources[identifier] = (source, digest, direction, timing, metadata)
    assert len(sources) == manifest['expectedSourcePages'] == len(FACINGS) + len(EFFECT_PINS)
    save(OUTPUT / 'candidate_review_plan.json', dict(batch=BATCH, selected=len(entries), expected=len(entries),
                                                    catalogueUnchanged=True, entries=entries))
    return sources


def assemble(facing, sources):
    bundle = ASSEMBLIES / facing
    body = 'class_linh_cung_skill_04_' + facing.lower()
    _, _, body_data, body_timing, body_metadata = sources[body]
    _, _, _, fan_timing, geometry = sources[FAN]
    fall_timing = sources[FALL][3]
    angle = -90 + FACINGS.index(facing) * 45
    forward = vector(angle)
    body_scale = 110 / body_data['referenceHeight']
    caster = (-71 * forward[0], 30 - 58 * forward[1])
    pivot = body_data['frames'][RELEASE_POSE]['pivot']
    grip = body_metadata['releaseSourcePoint']
    origin = tuple(caster[i] + (grip[i] - pivot[i]) * body_scale + 7 * forward[i] for i in range(2))
    target = (origin[0] + 120 * forward[0], origin[1] + 120 * forward[1] + 24)
    fall_origin = tuple(origin[i] + 77 * forward[i] for i in range(2))
    release = sum(body_timing[:RELEASE_POSE])
    peak = release + sum(fan_timing[:FULL_POSE])
    fall = release + FALL_DELAY_MS
    body_ends = list(accumulate(body_timing))
    fan_ends = [release + offset for offset in accumulate(fan_timing)]
    fall_ends = [fall + offset for offset in accumulate(fall_timing)]
    boundaries = sorted({0, release, peak, fall, fall_ends[-1] + 95,
                         *body_ends, *fan_ends, *fall_ends, *range(100, fall_ends[-1], 100)})
    centers = [(start + end) / 2 for start, end in zip(boundaries, boundaries[1:])]
    timing = [end - start for start, end in zip(boundaries, boundaries[1:])]
    assert len(timing) <= 120 and min(timing) >= 5
    drawings, tracks = [], []

    def add(identifier, ends, where, size, z, start=0, rotation=0, ratio=1):
        source, digest, data, _, _ = sources[identifier]
        frames = data['frames']
        keys = []
        for instant in centers:
            i = min(15, bisect_right(ends, instant))
            visible = int(start <= instant < ends[-1]) if start else 1
            item = pose(frames[i], i, size, where, visible)
            keys.append(item | dict(Angle=rotation, ScaleY=size * ratio))
        motion = track(identifier, keys)
        texture = place_texture(bundle, source, digest)
        drawings.append(layer(identifier, frames, texture, motion['Keys'][0]['Pose'], z))
        tracks.append(motion)

    add(body, body_ends, caster, body_scale, 2)
    add(TARGET, list(range(100, 1601, 100)), target, 58 / sources[TARGET][2]['referenceHeight'], 0)
    add(FAN, fan_ends, origin, REVIEW_REACH / geometry['sourceReach'], 1 if forward[1] < -.1 else 3,
        release, angle + geometry['sourceAngleCorrection'], geometry['fanRatioY'])
    add(FALL, fall_ends, fall_origin, 55 / sources[FALL][2]['referenceHeight'], 3, fall, angle)
    markers = [dict(Name=name, Kind='vfx', Frame=boundaries.index(t), X=p[0], Y=p[1], Radius=0)
               for name, t, p in (('fan_release', release, origin), ('fan_full', peak, origin), ('leaves_fall', fall, fall_origin))]
    path = document(bundle, 'Tán Hoa · ' + facing, drawings, [make_clip('Tán Hoa', facing, timing, tracks, markers)])
    save(bundle / 'assembly_descriptor.json', dict(projectSha256=sha(path), releaseMs=release, fullMs=peak,
                                                   fallMs=fall, sectorDegrees=geometry['measuredSectorDegrees'],
                                                   origin=list(origin), fallOrigin=list(fall_origin), artOnly=True))


if __name__ == '__main__':
    media = prepare()
    approvals = {item['id']: item['sourceSha256'] for item in read(ART / 'visual_review.json')['sourceApprovals']}
    target = next(item for item in read(ART / 'generation_records.json') if item['id'] == TARGET)
    source = ART / target['source']
    digest = sha(source)
    assert digest == approvals[TARGET]
    direction, = inspect(target)['directions']
    media[TARGET] = (source, digest, direction, [100] * 16, {})
    for view in FACINGS:
        assemble(view, media)
    print('Registered ten Tán Hoa source atlases and eight editable fan timelines.')
