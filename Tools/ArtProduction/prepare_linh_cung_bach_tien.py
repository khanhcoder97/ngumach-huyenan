"""Register the original Bách Tiễn sources and build editable rain timelines."""
from bisect import bisect_right
from itertools import accumulate
from math import cos, sin
from statistics import median

from PIL import Image

from build_linh_cung_khoa_mach_preview import TARGET
from prepare_linh_cung_day_gai import FACINGS, document, layer, place_texture, pose
from prepare_linh_cung_lien_chau import track, vector
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261119a'
OUTPUT = ROOT / 'Implementation/Reports/Evidence' / ('Actor_Batch_' + BATCH)
ASSEMBLIES = OUTPUT / 'BachTien'
RING = 'sk_lc_06_rain_telegraph_component'
ARROW = 'sk_lc_06_rain_arrow_component'
FLECKS = 'sk_lc_06_rain_impact_component'
WARNING_MS = 1200
WAVE_SPACING_MS = 200
CONTACT_POSE = 7
RELEASE_POSE = 9
RADIUS = 120
PATTERN = ((-.36, -.27), (.31, .21), (.19, -.41), (-.62, .21), (.52, .43), (.60, -.27))
GRID_EDGES = {
    'E': dict(columns=[0, 298, 589, 898, 1243], rows=[0, 316, 625, 934, 1265]),
    'SW': dict(columns=[0, 327, 620, 929, 1235], rows=[0, 314, 624, 945, 1274]),
    'NW': dict(columns=[0, 333, 629, 931, 1230], rows=[0, 312, 619, 930, 1278]),
}
SOURCE_PINS = {
    'N': 'bfbacbcbab623e9f6a451c315ddcef4ffe008efc3d77e304c57c0a944d876bb4',
    'NE': '9d872116337f4d2c4caf7b6e4cd59ddb6bdd62afab94fd516666f2178986d51c',
    'E': 'e828117a05a1a9f8f8f8285b4c2f865400a627d9f4bc50ca58f990505be78d1f',
    'SE': '69aca958a1a0a48e58fa0af9e4807d4ce7469b2f0b95aacb3621172f4ef101f3',
    'S': '9df0693bd1dabfb79c11c350f8b53014fe0244c107e86e79cbbbbc430dfefc18',
    'SW': '63f02af1c0dc5bd63eca4d04e6f9e80c0b999598712a3930e14d479efac343af',
    'W': '946711638d0ede2f0ed5f3098f64b7e977dc4f9a428e9d820066fb7fed049fd5',
    'NW': '69b420f2284afe07bd540a321a539ddd4e1529831495b0793294175825093e1e',
    RING: 'ddd1f6204bd1c34bfaafae11f700081095716b6f93b46d27c871a388fafb1eb4',
    ARROW: '269fd998a2eec0fbae0f06e58b5990871211cf17cb20f0ac90cce626bb9a9409',
    FLECKS: 'fa906abad2074b033222a2f1eb5b289ddf83354ec9ed9569e0d6a94183327b97',
}


def centre(bounds):
    left, top, right, bottom = bounds
    return [(left + right) / 2, (top + bottom) / 2]


def register(record, source):
    facing, identifier = record.get('direction'), record['id']
    assert record['sourceSha256'] == sha(source) == SOURCE_PINS[facing or identifier], identifier
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
        core = alpha.point(lambda value: 255 if value >= 200 else 0)
        if facing:
            feet = []
            for frame in frames:
                x, y, width, _ = frame['rect']
                bottom = frame['bounds'][3]
                soles = core.crop((x, y + bottom - 18, x + width, y + bottom)).getbbox()
                assert soles
                feet.append([(soles[0] + soles[2]) / 2, bottom - 18 + soles[3]])
            record.update(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=feet,
                          bodyReferenceHeight=feet[0][1] - frames[0]['bounds'][1])
            return {}
        if identifier == ARROW:
            pivots = []
            for frame in frames:
                x, y, width, _ = frame['rect']
                mid, bottom = width // 2, frame['bounds'][3]
                l, _, r, b = core.crop((x + mid - 18, y + bottom - 15, x + mid + 18, y + bottom)).getbbox()
                pivots.append([mid - 18 + (l + r) / 2, bottom - 15 + b])
            record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots)
            return dict(contactPose=CONTACT_POSE)

    bounds = [frame['bounds'] for frame in frames]
    record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=[centre(box) for box in bounds])
    if identifier == RING:
        widths = [r - l for l, _, r, _ in bounds]
        heights = [b - t for _, t, _, b in bounds]
        width, height = median(widths), median(heights)
        assert max(widths) - min(widths) <= 9 and max(heights) - min(heights) <= 9
        return dict(sourceWidth=width, ratioY=width / height)
    return {}


def clip(name, direction, durations, tracks, markers=()):
    return dict(Name=name, Direction=direction, Loop=False, DurationsMs=durations, Tracks=tracks,
                Markers=list(markers), SourceNote='Bách Tiễn Quy Tông · Vòng rêu và bốn đợt mưa tên.')


def prepare():
    manifest = read(ART / ('Candidates_' + BATCH) / 'candidate_manifest.json')
    entries, sources = [], {}
    for original in manifest['records']:
        record = dict(original)
        identifier, digest = record['id'], record['sourceSha256']
        source = ART / record['source']
        geometry = register(record, source)
        page = inspect(record)
        direction, = page['directions']
        frames, timing = direction['frames'], record['sourceFrameDurationsMs']
        bundle = OUTPUT / 'Candidate_Studio' / identifier
        texture = place_texture(bundle, source, digest)
        motion = track(identifier, (pose(f, i, 140 / direction['referenceHeight']) for i, f in enumerate(frames)))
        drawing = layer(identifier, frames, texture, motion['Keys'][0]['Pose'])
        path = document(bundle, identifier, [drawing], [clip(identifier, direction['direction'], timing, [motion])])
        save(bundle / 'source_registration.json', dict(record=record, page=page, **geometry,
                                                       productionApproved=False))
        entries.append(dict(id=identifier, project=path.relative_to(ROOT).as_posix(),
                            source=source.relative_to(ROOT).as_posix(), sourceSha256=digest,
                            timing=timing, loop=False))
        sources[identifier] = (source, digest, direction, timing, geometry)
    assert len(sources) == manifest['expectedSourcePages'] == len(FACINGS) + 3
    save(OUTPUT / 'candidate_review_plan.json', dict(batch=BATCH, selected=len(entries), expected=len(entries),
                                                    catalogueUnchanged=True, entries=entries))
    return sources


def assemble(facing, sources):
    bundle = ASSEMBLIES / facing
    body = 'class_linh_cung_skill_06_' + facing.lower()
    forward = vector(-90 + FACINGS.index(facing) * 45)
    zone = (58 * forward[0], 35 + 48 * forward[1])
    caster = tuple(zone[i] - 178 * forward[i] for i in range(2))
    target = (zone[0] + 21, zone[1] + 14)
    starts = [WARNING_MS + WAVE_SPACING_MS * wave for wave in range(4)]
    contact_delay = sum(sources[ARROW][3][:CONTACT_POSE])
    contacts = [t + contact_delay for t in starts]
    assert sum(sources[RING][3]) == WARNING_MS
    end = contacts[-1] + sum(sources[FLECKS][3])
    layers, tracks, descriptors = [], [], {}
    timelines = {
        body: list(accumulate(sources[body][3])),
        TARGET: list(range(100, end + 1, 100)),
        RING: list(accumulate(sources[RING][3])),
        **{f'wave_{i + 1}': [t + step for step in accumulate(sources[ARROW][3])] for i, t in enumerate(starts)},
        **{f'ground_{i + 1}': [t + step for step in accumulate(sources[FLECKS][3])] for i, t in enumerate(contacts)},
    }
    endpoints = sorted({0, end + 140, *starts, *contacts, *[t for times in timelines.values() for t in times]})
    timing = [b - a for a, b in zip(endpoints, endpoints[1:])]
    assert len(timing) <= 120 and min(timing) >= 5
    interval = endpoints[:-1]

    def add(identifier, source_id, schedule, site, size, depth, active_from=0, height=0, ratio_y=1):
        source, digest, direction, _, _ = sources[source_id]
        frames = direction['frames']
        poses = []
        for t in interval:
            phase = min(15, bisect_right(schedule, t))
            active = active_from <= t < schedule[-1] if identifier not in (TARGET, body) else True
            lift = height * (1 - min(1, max(0, t - active_from) / contact_delay)) if height else 0
            item = pose(frames[phase], phase, size, (site[0], site[1] - lift), int(active))
            item['ScaleY'] *= ratio_y
            poses.append(item)
        animation = track(identifier, poses)
        texture = place_texture(bundle, source, digest)
        layers.append(layer(identifier, frames, texture, animation['Keys'][0]['Pose'], depth))
        tracks.append(animation)
        descriptors[identifier] = source_id

    add(body, body, timelines[body], caster, 88 / sources[body][2]['referenceHeight'], 2)
    add(TARGET, TARGET, timelines[TARGET], target, 50 / sources[TARGET][2]['referenceHeight'], 2)
    ring_geometry = sources[RING][4]
    add(RING, RING, timelines[RING], zone, 2 * RADIUS / ring_geometry['sourceWidth'], 0,
        ratio_y=ring_geometry['ratioY'])
    for wave, (start, contact) in enumerate(zip(starts, contacts, strict=True)):
        a, b = cos(.79 * wave), sin(.79 * wave)
        for i, (x, y) in enumerate(PATTERN):
            site = (zone[0] + (x * a - y * b) * RADIUS, zone[1] + (x * b + y * a) * RADIUS)
            add(f'arrow_{wave + 1}_{i + 1}', ARROW, timelines[f'wave_{wave + 1}'], site,
                28 / sources[ARROW][2]['referenceHeight'], 4, start, 45 + (i % 3) * 8)
            if i < 2:
                add(f'flecks_{wave + 1}_{i + 1}', FLECKS, timelines[f'ground_{wave + 1}'], site,
                    18 / sources[FLECKS][2]['referenceHeight'], 3, contact)
    marks = [('warning', 0, zone, RADIUS), ('release_up', timelines[body][RELEASE_POSE - 1], caster, 0)]
    marks += [(f'wave_{i + 1}_drop', t, zone, RADIUS) for i, t in enumerate(starts)]
    marks += [(f'wave_{i + 1}_contact', t, zone, RADIUS) for i, t in enumerate(contacts)]
    marks.sort(key=lambda entry: entry[1])
    marker_list = [dict(Name=name, Kind='vfx', Frame=endpoints.index(t), X=point[0], Y=point[1], Radius=radius)
                   for name, t, point, radius in marks]
    path = document(bundle, 'Bách Tiễn Quy Tông · ' + facing, layers,
                    [clip('Bách Tiễn Quy Tông', facing, timing, tracks, marker_list)])
    save(bundle / 'assembly_descriptor.json', dict(projectSha256=sha(path), warningMs=WARNING_MS, radius=RADIUS,
                                                   waveStarts=starts, waveContacts=contacts,
                                                   layerSources=descriptors, artOnly=True))


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
    print('Registered eleven Bách Tiễn source atlases and eight editable rain timelines.')
