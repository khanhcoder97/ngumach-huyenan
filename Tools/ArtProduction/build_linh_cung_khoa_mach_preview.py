"""Assemble the east Khoa Mach shot, contact and reviewed target mark in Studio."""
import shutil

from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BUNDLE = ROOT / 'Implementation/Reports/Evidence/Actor_Assembly_20261117a/KhoaMach_E'
BODY = 'class_linh_cung_skill_01_e'
ARROW = 'sk_lc_01_projectile_component'
TAIL = 'sk_lc_01_leaf_dissipate_component'
TARGET = 'mob_waterroot_idle_s'
MARK = 'sk_lc_01_mark_component'


def make():
    project = BUNDLE / 'project.json'
    textures = BUNDLE / 'textures'
    textures.mkdir(parents=True, exist_ok=True)
    catalogue = {record['id']: record for record in read(ART / 'generation_records.json')}
    approval = next(item for item in read(ART / 'visual_review.json')['sourceApprovals'] if item['id'] == MARK)
    inputs = {}

    def source(identifier):
        if identifier in (BODY, ARROW, TAIL):
            registration = read(OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
            record, page = registration['record'], registration['page']
        else:
            record = catalogue[identifier]
            page = inspect(record)
        png = ART / record['source']
        source_sha = sha(png)
        assert source_sha == page['sha256']
        if identifier == MARK:
            assert source_sha == approval['sourceSha256'] and approval['reviewedSourceFrames'] == 16
        texture = textures / (source_sha + '.png')
        if not texture.exists():
            shutil.copyfile(png, texture)
        assert source_sha == sha(texture)
        inputs[identifier] = dict(source=record['source'], sha256=source_sha, texture='textures/' + texture.name)
        return page['directions'][0]

    body, arrow, tail, target, mark = (source(identifier) for identifier in (BODY, ARROW, TAIL, TARGET, MARK))
    body_x, target_x, floor_y = -112, 112, 36
    body_scale = 140 / body['referenceHeight']
    # The rightmost opaque arrow tip in authored draw frame 7 spans
    # source rows 175 to 178. Start the travelling effect on that axis.
    draw = body['frames'][7]
    muzzle_x = body_x + (draw['bounds'][2] - 1 - draw['pivot'][0]) * body_scale
    flight_y = floor_y + (176.5 - draw['pivot'][1]) * body_scale
    release, contact, end = 480, 800, 1840
    boundaries = sorted({0, end, *range(0, 961, 60), *range(release, contact + 1, 20),
                         *range(contact, 1201, 25), *range(contact, 1761, 60),
                         *range(0, end, 100)})
    # Five-millisecond subsegments only synchronize existing source clocks.
    durations = [right - left for left, right in zip(boundaries, boundaries[1:])]
    assert 5 <= min(durations) and len(durations) <= 120
    layers, tracks = [], []

    def bind(identifier, direction, scale, depth, at, centre=None):
        frames = direction['frames']
        assert len(frames) == 16
        keys = []
        for index, (start, stop) in enumerate(zip(boundaries, boundaries[1:])):
            t = (start + stop) / 2
            selected, px, py, alpha = at(t)
            frame = frames[selected]
            source_x, source_y = frame['pivot'] if centre is None else centre(frame)
            pose = dict(X=px, Y=py, PivotX=source_x, PivotY=source_y,
                        ScaleX=scale, ScaleY=scale, Alpha=alpha, Angle=0, SourceFrame=selected)
            keys.append(dict(Frame=index, Pose=pose))
        layers.append(dict(Id=identifier, Name=identifier, Kind='sprite', Z=depth,
                           Visible=True, Texture=inputs[identifier]['texture'],
                           Regions=[frame['rect'] for frame in frames], Rest=keys[0]['Pose']))
        tracks.append(dict(LayerId=identifier, Interpolate=False, Keys=keys))

    def projectile(t):
        visible = release <= t < contact
        progress = (t - release) / (contact - release) if visible else 0
        # Fix each authored silhouette to the preview trajectory at the
        # segment centre. The actual runtime motion follows the combat event.
        x = muzzle_x + (target_x - muzzle_x) * progress
        return int(progress * 16), x, flight_y, int(visible)

    def centre_of_bounds(frame):
        left, top, right, bottom = frame['bounds']
        return (left + right) / 2, (top + bottom) / 2

    bind(BODY, body, body_scale, 0, lambda t: (min(15, int(t // 60)), body_x, floor_y, 1))
    bind(TARGET, target, 88 / target['referenceHeight'], 0,
         lambda t: (int(t // 100) % 16, target_x, floor_y, 1))
    bind(ARROW, arrow, 50 / arrow['referenceHeight'], 4, projectile)
    bind(TAIL, tail, 48 / tail['referenceHeight'], 5,
         lambda t: (int((t - contact) // 25) if contact <= t < 1200 else 0,
                    target_x, flight_y, int(contact <= t < 1200)))
    bind(MARK, mark, 85 / mark['referenceHeight'], 2,
         lambda t: (int((t - contact) // 60) if contact <= t < 1760 else 0,
                    target_x, floor_y - 35, int(contact <= t < 1760)), centre_of_bounds)
    markers = [dict(Name=name, Kind='vfx', Frame=boundaries.index(time), X=x, Y=flight_y, Radius=0)
               for name, time, x in (('bow_release', release, muzzle_x),
                                     ('confirmed_contact_preview', contact, target_x))]
    data = dict(SchemaVersion=1, Scope='PRESENTATION_AUTHORING_ONLY', ProductionApproved=False,
                Name='Khóa Mạch · hướng Đông · ghép thử', Layers=layers, Sockets=[],
                Clips=[dict(Name='khoa_mach_contact', Direction='E', Loop=False, Tracks=tracks,
                            DurationsMs=durations, Markers=markers,
                            SourceNote='One bow release, one projectile and one target mark. The contact and timing are authored for Studio inspection.')])
    if project.exists():
        assert read(project) == data
    else:
        save(project, data)
    save(BUNDLE / 'assembly_descriptor.json',
         dict(sources=inputs, projectSha256=sha(project), releaseMs=release, contactMs=contact,
              releasePosition=[muzzle_x, flight_y], contactPosition=[target_x, flight_y],
              productionApproved=False))
    print(f'Assembled five editable layers on a {len(durations)}-segment Studio timeline.')


if __name__ == '__main__':
    make()
