"""Assemble Khoa Mach shots, impact and the reviewed target mark in Studio."""
import argparse
import shutil
from math import cos, radians, sin

from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BUNDLE = ROOT / 'Implementation/Reports/Evidence/Actor_Assembly_20261117a/KhoaMach_E'
BODY = 'class_linh_cung_skill_01_e'
ARROW = 'sk_lc_01_projectile_component'
TAIL = 'sk_lc_01_leaf_dissipate_component'
TARGET = 'mob_waterroot_idle_s'
MARK = 'sk_lc_01_mark_component'
# Body root, last drawn arrowhead (local atlas pixels), flight angle, and shot
# length are calibrated against each authored pose, with Y increasing down.
FACING_LAYOUTS = {
    'S': ((0, -18), (151, 262), 90, 138, 8, 'Nam'),
    'SE': ((-115, -14), (254, 287), 44, 156, 8, 'Đông Nam'),
    'N': ((20, 113), (104, 51), -90, 100, 8, 'Bắc'),
    'NE': ((-105, 88), (281, 71), -39, 146, 9, 'Đông Bắc'),
    'W': ((112, 36), (40, 174), 180, 148, 8, 'Tây'),
    'SW': ((115, -14), (15, 257), 146, 156, 8, 'Tây Nam'),
    'NW': ((105, 88), (20, 73), -147, 146, 8, 'Tây Bắc'),
}


def make(facing='E'):
    body_id = 'class_linh_cung_skill_01_' + facing.lower()
    bundle = BUNDLE.with_name('KhoaMach_' + facing)
    project = bundle / 'project.json'
    textures = bundle / 'textures'
    textures.mkdir(parents=True, exist_ok=True)
    catalogue = {record['id']: record for record in read(ART / 'generation_records.json')}
    approval = next(item for item in read(ART / 'visual_review.json')['sourceApprovals'] if item['id'] == MARK)
    inputs = {}

    def source(identifier):
        if identifier in (body_id, ARROW, TAIL):
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

    body, arrow, tail, target, mark = (source(identifier) for identifier in (body_id, ARROW, TAIL, TARGET, MARK))
    body_scale = 140 / body['referenceHeight']
    if facing == 'E':
        draw = body['frames'][7]
        body_x, floor_y = -112, 36
        tip_x, tip_y = draw['bounds'][2] - 1, 176.5
        target_x, target_y, angle, release_frame, facing_name = 112, 36, 0, 8, 'Đông'
    else:
        (body_x, floor_y), (tip_x, tip_y), angle, travel, release_frame, facing_name = FACING_LAYOUTS[facing]
        draw = body['frames'][release_frame - 1]
    muzzle_x = body_x + (tip_x - draw['pivot'][0]) * body_scale
    muzzle_y = floor_y + (tip_y - draw['pivot'][1]) * body_scale
    impact_y = muzzle_y
    if facing != 'E':
        target_x = muzzle_x + travel * cos(radians(angle))
        impact_y = muzzle_y + travel * sin(radians(angle))
        target_y = impact_y + 38
    release = release_frame * 60
    contact, tail_end, mark_end, end = release + 320, release + 720, release + 1280, release + 1360
    boundaries = sorted({0, end, *range(0, 961, 60), *range(release, contact + 1, 20),
                         *range(contact, tail_end + 1, 25), *range(contact, mark_end + 1, 60),
                         *range(0, end, 100)})
    # Five-millisecond subsegments only synchronize existing source clocks.
    durations = [right - left for left, right in zip(boundaries, boundaries[1:])]
    assert 5 <= min(durations) and len(durations) <= 120
    layers, tracks = [], []

    def bind(identifier, direction, scale, depth, at, centre=None, rotation=0):
        frames = direction['frames']
        assert len(frames) == 16
        keys = []
        for index, (start, stop) in enumerate(zip(boundaries, boundaries[1:])):
            t = (start + stop) / 2
            selected, px, py, alpha = at(t)
            frame = frames[selected]
            source_x, source_y = frame['pivot'] if centre is None else centre(frame)
            pose = dict(X=px, Y=py, PivotX=source_x, PivotY=source_y,
                        ScaleX=scale, ScaleY=scale, Alpha=alpha, Angle=rotation, SourceFrame=selected)
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
        y = muzzle_y + (impact_y - muzzle_y) * progress if facing != 'E' else muzzle_y
        return int(progress * 16), x, y, int(visible)

    def centre_of_bounds(frame):
        left, top, right, bottom = frame['bounds']
        return (left + right) / 2, (top + bottom) / 2

    bind(body_id, body, body_scale, 0, lambda t: (min(15, int(t // 60)), body_x, floor_y, 1))
    bind(TARGET, target, 88 / target['referenceHeight'], 0,
         lambda t: (int(t // 100) % 16, target_x, target_y, 1))
    bind(ARROW, arrow, 50 / arrow['referenceHeight'], 4, projectile, rotation=angle)
    bind(TAIL, tail, 48 / tail['referenceHeight'], 5,
         lambda t: (int((t - contact) // 25) if contact <= t < tail_end else 0,
                    target_x, impact_y, int(contact <= t < tail_end)),
         rotation=angle)
    bind(MARK, mark, 85 / mark['referenceHeight'], 2,
         lambda t: (int((t - contact) // 60) if contact <= t < mark_end else 0,
                    target_x, target_y - 35, int(contact <= t < mark_end)), centre_of_bounds)
    markers = [dict(Name=name, Kind='vfx', Frame=boundaries.index(time), X=x, Y=y, Radius=0)
               for name, time, x, y in (('bow_release', release, muzzle_x, muzzle_y),
                                        ('confirmed_contact_preview', contact, target_x, impact_y))]
    data = dict(SchemaVersion=1, Scope='PRESENTATION_AUTHORING_ONLY', ProductionApproved=False,
                Name=f'Khóa Mạch · hướng {facing_name} · ghép thử', Layers=layers, Sockets=[],
                Clips=[dict(Name='khoa_mach_contact', Direction=facing, Loop=False, Tracks=tracks,
                            DurationsMs=durations, Markers=markers,
                            SourceNote='One bow release, one projectile and one target mark. The contact and timing are authored for Studio inspection.')])
    if project.exists():
        assert read(project) == data
    else:
        save(project, data)
    save(bundle / 'assembly_descriptor.json',
         dict(sources=inputs, projectSha256=sha(project), releaseMs=release, contactMs=contact,
              releasePosition=[muzzle_x, muzzle_y], contactPosition=[target_x, impact_y],
              productionApproved=False))
    print(f'Assembled five editable layers on a {len(durations)}-segment Studio timeline.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--facing', choices=('E', *FACING_LAYOUTS), default='E')
    make(parser.parse_args().facing)
