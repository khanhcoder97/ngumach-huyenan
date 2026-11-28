"""Register original Phi Diệp sources and assemble editable retreat previews."""
from bisect import bisect_right
from itertools import accumulate
from statistics import median

from PIL import Image

from build_linh_cung_khoa_mach_preview import TARGET
from prepare_linh_cung_day_gai import FACINGS, document, layer, place_texture, pose
from prepare_linh_cung_khoa_mach_review import projectile_tip_pivots
from prepare_linh_cung_lien_chau import track, vector
from prepare_linh_cung_tan_hoa import release_socket
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118e'
OUTPUT = ROOT / 'Implementation/Reports/Evidence' / ('Actor_Batch_' + BATCH)
ASSEMBLIES = OUTPUT / 'PhiDiep'
ARROW = 'sk_lc_05_retreat_arrow_component'
HEEL = 'sk_lc_05_retreat_heel_component'
START_POSE = 4
RELEASE_POSE = 8
LANDING_POSE = 12
START_MS, RELEASE_MS, LANDING_MS = 200, 320, 480
SHORT_STOP_MS = 285
REVIEW_DISTANCE = 144

GRIPS = {
    'N': ('69a055c0c089f257545d5c988e00d306723b642efa8d702bcc3c6c12efa47b9b', (57, 134)),
    'NE': ('96f2ecbb3ddd194934983efc687f0e2d828ee9e757a75fba91575794d9f274fd', (257, 132)),
    'E': ('82fa6ca4d8b3cb1c9b625e9b26c7791b4796837e61a0caecf3386c8713b4828c', (283, 164)),
    'SE': ('e38a2f34e1d96197ff1d455526edd58ff4c672e0bf2a586f35bb25890d286883', (243, 195)),
    'S': ('23c3048c1deefb5b5f0cb0e224e5386818941c9f5ea8dfba022d27050d928f6b', (237, 205)),
    'SW': ('66894bfc6a8c8636d763b4b4c837b0615a46dd07e83b6410409c251617d24f79', (88, 224)),
    'W': ('e0319bd3d52812b734cc628d926f09d401e992543cc9ecd4df10139e482b7af4', (60, 172)),
    'NW': ('0b9c71fbef2395ea4ca585de68667191529e044edbddee14f6fbe9406ada65b3', (85, 116)),
}
EFFECT_PINS = {
    ARROW: '8ecf897b94df41fe67b18bc340ff277a6e45615a0e91fcbd51cb4ccf5728174d',
    HEEL: 'd43c3fd8549409daa0e6e7dbdf89cf02794d9b217b000b2bba65a074381fe2f8',
}


def register(record, source):
    facing, identifier = record.get('direction'), record['id']
    assert record['sourceSha256'] == sha(source) == (GRIPS[facing][0] if facing else EFFECT_PINS[identifier])
    if facing == 'E':
        record['gridEdges'] = dict(columns=[0, 321, 624, 922, 1263], rows=[0, 317, 622, 929, 1246])
    raw, = inspect(record)['directions']
    frames = raw['frames']
    with Image.open(source) as atlas:
        alpha = atlas.getchannel('A')
        halo = alpha.point(lambda value: 255 if value >= 64 else 0)
        for frame in frames:
            x, y, width, height = frame['rect']
            left, top, right, bottom = halo.crop((x, y, x + width, y + height)).getbbox()
            assert min(left, top, width - right, height - bottom) >= 2, identifier
        if facing:
            core = alpha.point(lambda value: 255 if value >= 200 else 0)
            feet = []
            for frame in frames:
                x, y, width, _ = frame['rect']
                bottom = frame['bounds'][3]
                # Include the raised boot in horizontal registration without
                # letting it pull the ground origin up off the planted foot.
                soles = core.crop((x, y + bottom - 38, x + width, y + bottom)).getbbox()
                assert soles
                feet.append([(soles[0] + soles[2]) / 2, bottom - 38 + soles[3]])
            record.update(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=feet,
                          bodyReferenceHeight=feet[0][1] - frames[0]['bounds'][1])
            return dict(releasePose=RELEASE_POSE,
                        releaseSourcePoint=release_socket(atlas, frames[RELEASE_POSE], GRIPS[facing][1]))
    if identifier == ARROW:
        pivots = projectile_tip_pivots(frames, source)
    else:
        # The quiet final flecks shrink inside the same ground-locked stamp.
        first_cells = [frame['bounds'] for frame in frames[:6]]
        origin = [median((bounds[axis] + bounds[axis + 2]) / 2 for bounds in first_cells) for axis in (0, 1)]
        pivots = [origin for _ in frames]
    record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots)
    return {}


def clip(name, direction, timing, tracks, markers=()):
    return dict(Name=name, Direction=direction, Loop=False, DurationsMs=timing, Tracks=tracks,
                Markers=list(markers), SourceNote='Phi Diệp · Bước lùi, hai dấu lá và một tên phản kích.')


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
        motion = track(identifier, (pose(frame, i, 140 / direction['referenceHeight']) for i, frame in enumerate(frames)))
        drawing = layer(identifier, frames, texture, motion['Keys'][0]['Pose'])
        path = document(bundle, identifier, [drawing], [clip(identifier, direction['direction'], timing, [motion])])
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


def progress(time):
    t = min(1, max(0, (time - START_MS) / (LANDING_MS - START_MS)))
    return t * t * (3 - 2 * t)


def assemble(facing, sources):
    bundle = ASSEMBLIES / facing
    body = 'class_linh_cung_skill_05_' + facing.lower()
    _, _, body_data, timing, body_metadata = sources[body]
    body_ends = list(accumulate(timing))
    assert [body_ends[index - 1] for index in (START_POSE, RELEASE_POSE, LANDING_POSE)] == [
        START_MS, RELEASE_MS, LANDING_MS]
    arrow_ends = [RELEASE_MS + t for t in accumulate(sources[ARROW][3])]
    heel_ends = [[start + t for t in accumulate(sources[HEEL][3])] for start in (START_MS, RELEASE_MS)]
    times = {0, START_MS, RELEASE_MS, LANDING_MS, SHORT_STOP_MS, arrow_ends[-1] + 130,
             *arrow_ends, *heel_ends[0], *heel_ends[1], *range(100, arrow_ends[-1], 100)}
    # Studio needs at least five milliseconds per event cell. Coalesce an
    # adjacent body boundary by at most four milliseconds for these previews.
    for index, end in enumerate(body_ends):
        closest = min(times, key=lambda time: (abs(time - end), time))
        if abs(closest - end) < 5:
            body_ends[index] = closest
        else:
            times.add(end)
    for instant in range(START_MS, arrow_ends[-1], 10):
        if min(abs(instant - t) for t in times) >= 5:
            times.add(instant)
    bounds = sorted(times)
    durations = [end - start for start, end in zip(bounds, bounds[1:])]
    assert len(durations) <= 120 and min(durations) >= 5
    angle = -90 + FACINGS.index(facing) * 45
    forward, across = vector(angle), vector(angle + 90)
    start = (26 * forward[0], 26 + 26 * forward[1])
    target = (start[0] + 98 * forward[0], start[1] + 98 * forward[1] + 18)
    body_scale = 102 / body_data['referenceHeight']
    grip = body_metadata['releaseSourcePoint']
    foot = body_data['frames'][RELEASE_POSE]['pivot']
    drawings, clips, examples = [], [], []
    mappings = [(body, body, 2), (TARGET, TARGET, 0), ('heel_1', HEEL, 1), ('heel_2', HEEL, 1), (ARROW, ARROW, 3)]

    for name, stop in (('Lùi đủ', LANDING_MS), ('Lùi ngắn', SHORT_STOP_MS)):
        def root_at(time):
            travel = REVIEW_DISTANCE * progress(min(time, stop))
            return tuple(start[i] - forward[i] * travel for i in range(2))

        cast_root = root_at(RELEASE_MS)
        muzzle = tuple(cast_root[i] + (grip[i] - foot[i]) * body_scale + forward[i] * 5 for i in range(2))
        heel_sites = [tuple(root_at(time)[i] + across[i] * side for i in range(2))
                      for time, side in ((START_MS, -8), (RELEASE_MS, 8))]
        motion = []
        for identifier, source_id, depth in mappings:
            source, digest, data, _, _ = sources[source_id]
            frames = data['frames']
            samples = []
            for time in bounds[:-1]:
                if identifier == body:
                    phase, where, size, alpha, rot = bisect_right(body_ends, time), root_at(time), body_scale, 1, 0
                elif identifier == TARGET:
                    phase, where, size, alpha, rot = time // 100, target, 55 / data['referenceHeight'], 1, 0
                elif identifier == ARROW:
                    phase = bisect_right(arrow_ends, time)
                    flight = max(0, time - RELEASE_MS) / (arrow_ends[-1] - RELEASE_MS)
                    where = tuple(origin + forward[i] * 220 * flight for i, origin in enumerate(muzzle))
                    size, alpha, rot = 32 / data['referenceHeight'], int(RELEASE_MS <= time < arrow_ends[-1]), angle
                else:
                    i = int(identifier[-1]) - 1
                    phase = bisect_right(heel_ends[i], time)
                    where, size, rot = heel_sites[i], 25 / data['referenceHeight'], angle
                    alpha = int((START_MS, RELEASE_MS)[i] <= time < heel_ends[i][-1])
                phase = min(15, phase)
                samples.append(pose(frames[phase], phase, size, where, alpha) | dict(Angle=rot))
            animation = track(identifier, samples)
            if not clips:
                texture = place_texture(bundle, source, digest)
                drawings.append(layer(identifier, frames, texture, animation['Keys'][0]['Pose'], depth))
            motion.append(animation)
        markers = [dict(Name=label, Kind=kind, Frame=bounds.index(time), X=point[0], Y=point[1], Radius=0)
                   for label, kind, time, point in (
                       ('retreat_start', 'footstep', START_MS, heel_sites[0]),
                       ('arrow_release', 'vfx', RELEASE_MS, muzzle),
                       ('retreat_stop', 'footstep', stop, root_at(stop)))]
        markers.sort(key=lambda marker: marker['Frame'])
        clips.append(clip(name, facing, durations, motion, markers))
        examples.append(dict(name=name, stopMs=stop, start=list(start), finish=list(root_at(stop)),
                             releaseOrigin=list(muzzle), retreatDistance=round(REVIEW_DISTANCE * progress(stop), 2)))
    path = document(bundle, 'Phi Diệp · ' + facing, drawings, clips)
    save(bundle / 'assembly_descriptor.json', dict(projectSha256=sha(path), retreatStartMs=START_MS,
                                                   releaseMs=RELEASE_MS, releaseSourcePose=RELEASE_POSE,
                                                   modes=examples, artOnly=True))


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
    print('Registered ten Phi Diệp atlases and sixteen editable retreat timelines.')
