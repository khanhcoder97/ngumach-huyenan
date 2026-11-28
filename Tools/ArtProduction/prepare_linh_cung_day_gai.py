"""Register the original Dây Gai atlases and build editable Studio timelines."""
import shutil

from PIL import Image

from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118b'
OUTPUT = ROOT / 'Implementation/Reports/Evidence' / ('Actor_Batch_' + BATCH)
ASSEMBLIES = OUTPUT / 'DayGai'
FACINGS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
EFFECTS = tuple('sk_lc_02_trap_' + stage + '_component' for stage in ('seed', 'grow', 'armed', 'retract'))

# SHA-bound local-cell boot windows, hand attachment point and release pose.
# In NE and NW the open hand is visible one pose earlier than in the front views.
BODY = {
    'E': ('66a1ce44a1a2dad78dc7dc879ca31c7634435a392584989ef327370953485ebb', (92, 163),
          {5: 273, 6: 274, 7: 274}, (183, 273), 8, (61, 17)),
    'S': ('b3fd8e8c55b15f48b0b3ec711694ef04af502f97f27c09518b5249e033d8b230', (120, 228),
          {6: 289, 7: 289, 8: 273}, (145, 268), 8, (-13, 48)),
    'N': ('030a931963f9bcbb8d68ad79cadd14b2cc08ac81061ab63eef9b4d6dee6ab656', (105, 204),
          {}, (243, 139), 8, (31, -45)),
    'W': ('ef39b80d6147ae6a3254a348fed96a46b86304f43e3bdcbded09130047efcd67', (129, 216),
          {}, (96, 248), 8, (-62, 17)),
    'SE': ('516fd35d7ce1c3064bf5119c1a4596e7cd473aa1a9d9c6f98c7a09c3f926c5b2', (83, 154),
           {6: 285, 7: 285, 8: 286}, (164, 283), 8, (43, 43)),
    'NE': ('4cd70ddc48a5ceae00dce585518af39646d6797235e147cf82244900b6f0e3ff', (83, 171),
           {}, (241, 257), 7, (60, -24)),
    'SW': ('dbb922a0e7ea922ffec73b69d1a73d149817af1d958e0cdfcd3fddd8c99c728b', (115, 203),
           {}, (86, 277), 8, (-49, 40)),
    'NW': ('661dafbfb81ed2c1e511a31ff6b98bb5e115fd0847fd131b39fc014b91f92cc1', (133, 243),
           {}, (92, 202), 7, (-61, -30)),
}
EFFECT_PINS = {
    EFFECTS[0]: '80540f749da1493678c55f815f2f7330c2389c8133f6c3d0abc3e46664779001',
    EFFECTS[1]: '94581b4e1703b5ef50837b4b050b52d45ed87ec72e077c35c4e070f85221d080',
    EFFECTS[2]: 'caa6f6d2d95170be7b7f1c47d9de6bafde97ae0814e373d8e0010a2dbb0ca90d',
    EFFECTS[3]: '0cb9b0e57c669d3d35e63d8a43978971e70263933a2f197a59c3bd59b1d25790',
}


def measured_geometry(record, frames, source):
    identifier = record['id']
    facing = record.get('direction')
    with Image.open(source) as atlas:
        alpha = atlas.getchannel('A')
        # The opaque core is validated by inspect(). Also reject translucent
        # halos that fill a gutter but fall below its core threshold.
        halo = alpha.point(lambda value: 255 if value >= 64 else 0)
        for frame in frames:
            x, y, w, h = frame['rect']
            limits = halo.crop((x, y, x + w, y + h)).getbbox()
            assert limits and min(limits[0], limits[1], w - limits[2], h - limits[3]) >= 2, identifier
        if facing:
            digest, (left, right), floor_overrides, _, _, _ = BODY[facing]
            assert record['sourceSha256'] == digest
            mask = alpha.point(lambda value: 255 if value >= 200 else 0)
            pivots = []
            for i, frame in enumerate(frames):
                x, y, _, _ = frame['rect']
                bottom = frame['bounds'][3]
                band = mask.crop((x + left, y + bottom - 45, x + right, y + bottom)).getbbox()
                assert band
                floor = floor_overrides.get(i, bottom - 45 + band[3])
                soles = mask.crop((x + left, y + floor - 10, x + right, y + floor)).getbbox()
                assert soles
                pivots.append([left + (soles[0] + soles[2]) / 2, floor])
            first = frames[0]['bounds']
            return dict(pivotMode='SOURCE_FOOT_PIVOTS', sourceFootPivots=pivots,
                        bodyReferenceHeight=pivots[0][1] - first[1])
    assert record['sourceSha256'] == EFFECT_PINS[identifier]
    pivots = []
    for i, frame in enumerate(frames):
        left, _, right, bottom = frame['bounds']
        if identifier == EFFECTS[0]:
            # The solid seed is centered at these columns; flecks do not
            # redefine its centre during contact.
            pivots.append([[185, 161, 137, 113][i % 4], bottom - 3])
        else:
            # Ground origin lies behind the front edge of the open ring.
            # The offset narrows to the seed during growth and retraction.
            pivots.append([(left + right) / 2, round(bottom - (right - left) * .14, 2)])
    return dict(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots)


def place_texture(bundle, source, digest):
    path = bundle / 'textures' / (digest + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        shutil.copyfile(source, path)
    assert sha(path) == digest
    return 'textures/' + path.name


def pose(frame, index, scale, where=(0, 0), alpha=1):
    return dict(X=where[0], Y=where[1], PivotX=frame['pivot'][0], PivotY=frame['pivot'][1],
                ScaleX=scale, ScaleY=scale, Alpha=alpha, Angle=0, SourceFrame=index)


def layer(identifier, frames, texture, rest, z=0):
    return dict(Id=identifier, Kind='sprite', Name=identifier, Visible=True, Z=z,
                Texture=texture, Regions=[frame['rect'] for frame in frames], Rest=rest)


def document(bundle, name, layers, clips):
    data = dict(SchemaVersion=1, Scope='PRESENTATION_AUTHORING_ONLY', Name=name,
                ProductionApproved=False, Layers=layers, Sockets=[], Clips=clips)
    path = bundle / 'project.json'
    if path.exists():
        assert read(path) == data, 'Preserve the edited project and build a separate revision'
    else:
        save(path, data)
    return path


def clip(name, facing, durations, tracks, markers=(), loop=False):
    return dict(Name=name, Direction=facing, Loop=loop, DurationsMs=durations, Tracks=tracks,
                Markers=list(markers), SourceNote='Dây Gai · 16 tư thế gốc mỗi lớp. Timeline xem thử trong Studio.')


def timeline(identifier, frames, scale, samples):
    keys = [dict(Frame=i, Pose=pose(frames[frame], frame, scale, point, alpha))
            for i, (frame, point, alpha) in enumerate(samples)]
    return dict(LayerId=identifier, Interpolate=False, Keys=keys)


def prepare():
    manifest = read(ART / ('Candidates_' + BATCH) / 'candidate_manifest.json')
    entries, sources = [], {}
    for original in manifest['records']:
        record = dict(original)
        identifier = record['id']
        source = ART / record['source']
        digest = sha(source)
        assert digest == record['sourceSha256']
        raw, = inspect(record)['directions']
        record.update(measured_geometry(record, raw['frames'], source))
        page = inspect(record)
        direction, = page['directions']
        frames = direction['frames']
        timing = record['sourceFrameDurationsMs']
        bundle = OUTPUT / 'Candidate_Studio' / identifier
        texture = place_texture(bundle, source, digest)
        scale = 140 / direction['referenceHeight']
        track = timeline(identifier, frames, scale, ((i, (0, 0), 1) for i in range(16)))
        drawing = layer(identifier, frames, texture, track['Keys'][0]['Pose'])
        loop = record.get('previewLoop', False)
        project = document(bundle, identifier, [drawing],
                           [clip(identifier, direction['direction'], timing, [track], loop=loop)])
        save(bundle / 'source_registration.json', dict(record=record, page=page, productionApproved=False))
        entries.append(dict(id=identifier, project=project.relative_to(ROOT).as_posix(),
                            source=source.relative_to(ROOT).as_posix(), sourceSha256=digest,
                            timing=timing, loop=loop))
        sources[identifier] = (source, digest, direction)
    assert len(sources) == len(FACINGS) + len(EFFECTS) == manifest['expectedSourcePages']
    save(OUTPUT / 'candidate_review_plan.json',
         dict(batch=BATCH, selected=len(entries), expected=manifest['expectedSourcePages'],
              catalogueUnchanged=True, entries=entries))
    return sources


def assemble(facing, sources):
    body_id = 'class_linh_cung_skill_02_' + facing.lower()
    order = (body_id, *EFFECTS)
    bundle = ASSEMBLIES / facing
    body = sources[body_id][2]
    _, _, _, hand, release_index, ground = BODY[facing]
    height = 112
    body_scale = height / body['referenceHeight']
    stance = body['frames'][release_index]['pivot']
    hand_pos = [(hand[i] - stance[i]) * body_scale for i in range(2)]
    seed_frames = sources[EFFECTS[0]][2]['frames']
    sx, sy = seed_frames[0]['pivot']
    sl, st, sr, _ = seed_frames[0]['bounds']
    seed_scale = 20 / (seed_frames[-1]['bounds'][2] - seed_frames[-1]['bounds'][0])
    # The first seed silhouette starts at the open hand. During its fall,
    # its authored vertical motion meets the fixed center of the trap.
    initial = (hand_pos[0] - ((sl + sr) / 2 - sx) * seed_scale, hand_pos[1] - (st + 22 - sy) * seed_scale)
    scales = {body_id: body_scale, EFFECTS[0]: seed_scale}
    for identifier, frame_index in zip(EFFECTS[1:], (15, 0, 0)):
        left, _, right, _ = sources[identifier][2]['frames'][frame_index]['bounds']
        scales[identifier] = 118 / (right - left)
    release = 70 * release_index
    grow = release + 480
    armed = grow + 640
    clips = []
    for ending, arm_time in (('trigger', 980), ('expire', 2240)):
        retract = armed + arm_time
        end = retract + 640
        boundaries = sorted({*range(0, 1121, 70), *range(release, grow + 1, 30),
                             *range(grow, armed + 1, 40), *range(armed, retract, 70),
                             *range(retract, end + 1, 40)})
        durations = [right - left for left, right in zip(boundaries, boundaries[1:])]
        assert len(durations) <= 120 and min(durations) >= 10
        clocks = ((0, 1120, 70), (release, grow, 30), (grow, armed, 40),
                  (armed, retract, 70), (retract, end, 40))
        tracks = []
        for index, (identifier, (start, stop, step)) in enumerate(zip(order, clocks)):
            samples = []
            for a, b in zip(boundaries, boundaries[1:]):
                t = (a + b) / 2
                selected = int(max(0, t - start) // step)
                visible = start <= t < stop
                if index == 0:
                    samples.append((min(15, selected), (0, 0), 1))
                elif index == 1:
                    settle = min(1, max(0, (t - start) / 210))
                    point = tuple(initial[i] + (ground[i] - initial[i]) * settle for i in range(2))
                    samples.append((min(15, selected), point, int(visible)))
                else:
                    phase = selected % 16 if index == 3 else min(15, selected)
                    alpha = min(1, (stop - t) / 100) if index == 4 and visible else int(visible)
                    samples.append((phase, ground, alpha))
            tracks.append(timeline(identifier, sources[identifier][2]['frames'], scales[identifier], samples))
        markers = [dict(Name=name, Kind='vfx', Frame=boundaries.index(at), X=ground[0], Y=ground[1], Radius=0)
                   for name, at in (('seed_release', release), ('trap_growth', grow), ('trap_armed', armed),
                                    ('trap_' + ending, retract))]
        clips.append(clip('Dây Gai · ' + ending, facing, durations, tracks, markers))
    layers = []
    depth = -2 if facing in ('N', 'NW', 'NE') else 2
    for index, identifier in enumerate(order):
        source, digest, direction = sources[identifier]
        texture = place_texture(bundle, source, digest)
        rest = clips[0]['Tracks'][index]['Keys'][0]['Pose']
        z = 0 if index == 0 else 3 if index == 1 else depth
        layers.append(layer(identifier, direction['frames'], texture, rest, z))
    return document(bundle, 'Dây Gai · ' + facing, layers, clips)


if __name__ == '__main__':
    assets = prepare()
    for facing in FACINGS:
        assemble(facing, assets)
    print(f'Registered {len(assets)} original atlases and built eight editable two-ending Dây Gai previews.')
