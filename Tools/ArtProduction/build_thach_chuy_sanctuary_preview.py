"""Build a five-facing editable Studio preview from the sanctuary sources."""
import shutil
from pathlib import Path

from prepare_thach_chuy_candidates_20261116c import ART, EV, ROOT, read, save, sha

BUNDLE = ROOT / 'Implementation/Reports/Evidence/Actor_Assembly_20261117a/Sanctuary_TC06_v2'
FACINGS = ('S', 'SE', 'E', 'NE', 'N')
# These are presentation review times. The gameplay state controls duration.
PHASES = {
    'charge': ('zone_charge', 0, 640, 40),
    'sustain': ('open_zone_sustain', 920, 4120, 100),
    'end': ('zone_end', 4120, 4760, 40),
}
PLATE_START, PLATE_END, PLATE_STEP = 560, 1040, 30
FADE_START, FADE_END = 920, 1040
PREVIEW_ORIGIN_Y = 36
CLIP_END = 5120


def make(destination):
    manifest = read(ART / 'Candidates_20261116c/candidate_manifest.json')
    records = {record['id']: record for record in manifest['records']}
    textures = destination / 'textures'
    textures.mkdir(parents=True, exist_ok=True)
    layers = []
    inputs = {}
    schedules = {}

    def add_layer(identifier, source_id, depth, rest, schedule, socket=''):
        record = records[source_id]
        registration_path = EV / 'Candidate_Studio' / source_id / 'source_registration.json'
        registration = read(registration_path)
        assert source_id == registration['record']['id']
        assert sha(ART / record['source']) == record['sourceSha256'] == registration['record']['sourceSha256']
        texture = textures / (record['sourceSha256'] + '.png')
        if texture.exists():
            assert sha(texture) == record['sourceSha256']
        else:
            shutil.copyfile(ART / record['source'], texture)
        frames = registration['page']['directions'][0]['frames']
        assert len(frames) == 16
        inputs[source_id] = dict(pngSha256=record['sourceSha256'], registrationSha256=sha(registration_path))
        pose = dict(X=0, Y=0 if socket else PREVIEW_ORIGIN_Y,
                    PivotX=frames[0]['pivot'][0], PivotY=frames[0]['pivot'][1],
                    ScaleX=rest, ScaleY=rest, Alpha=0, Angle=0, SourceFrame=0)
        layer = dict(Id=identifier, Name=identifier, Kind='sprite', Texture='textures/' + texture.name,
                     Regions=[frame['rect'] for frame in frames], Z=depth, Visible=True, Rest=pose)
        if socket:
            layer['AttachSocket'] = socket
        layers.append(layer)
        schedules[identifier] = (frames, schedule)

    boundaries = {0, CLIP_END, *range(0, 1281, 80)}
    for _, start, end, step in PHASES.values():
        boundaries.update(range(start, end + 1, step))
    boundaries.update(range(PLATE_START, PLATE_END + 1, PLATE_STEP))
    boundaries.update(range(FADE_START, FADE_END + 1, 20))
    times = sorted(boundaries)
    segments = list(zip(times, times[1:]))
    durations = [end - start for start, end in segments]
    assert len(durations) <= 120 and min(durations) >= 5

    def body_schedule(time, facing, owner):
        return min(15, time // 80), int(facing == owner)

    def phase_schedule(time, start, end, step):
        if start <= time < end:
            return ((time - start) // step) % 16, 1
        return 0, 0

    def fade_progress(time):
        return max(0, min(1, (time - FADE_START) / (FADE_END - FADE_START)))

    def zone_schedule(time, part, start, end, step):
        pose_index, alpha = phase_schedule(time, start, end, step)
        return pose_index, alpha * fade_progress(time) if part == 'sustain' else alpha

    def plate_schedule(time):
        pose_index, alpha = phase_schedule(time, PLATE_START, PLATE_END, PLATE_STEP)
        return pose_index, alpha * (1 - fade_progress(time))

    for facing in FACINGS:
        source_id = 'class_thach_chuy_skill_06_' + facing.lower()
        registration = read(EV / 'Candidate_Studio' / source_id / 'source_registration.json')
        height = registration['record']['bodyReferenceHeight']
        add_layer('body_' + facing, source_id, 0, 140 / height,
                  lambda time, owner, facing=facing: body_schedule(time, facing, owner))

    # Align the maximum charge and intact end footprint with the same
    # projected 300 px rim. Per-frame offsets stay in the source pivots.
    footprint_references = {'charge': 12, 'sustain': 0, 'end': 0}
    for part, (suffix, start, end, step) in PHASES.items():
        source_id = 'sk_tc_06_' + suffix + '_component'
        registration = read(EV / 'Candidate_Studio' / source_id / 'source_registration.json')
        reference = registration['page']['directions'][0]['frames'][footprint_references[part]]
        left, _, right, _ = reference['bounds']
        add_layer(part, source_id, -2, 300 / (right - left),
                  lambda time, _, part=part, start=start, end=end, step=step: zone_schedule(time, part, start, end, step))

    plate_source = 'sk_tc_06_plate_gain_component'
    plate_registration = read(EV / 'Candidate_Studio' / plate_source / 'source_registration.json')
    left, _, right, _ = plate_registration['page']['directions'][0]['frames'][15]['bounds']
    sockets = []
    for name, x, y in (('plate_back', 0, -73), ('plate_left', -95, -48), ('plate_right', 95, -48)):
        sockets.append(dict(Id=name, Name=name, LayerId='', X=x, Y=y + PREVIEW_ORIGIN_Y))
        add_layer(name, plate_source, -1, 42 / (right - left),
                  lambda time, _: plate_schedule(time), name)

    clips = []
    for facing in FACINGS:
        tracks = []
        for layer in layers:
            frames, schedule = schedules[layer['Id']]
            keys = []
            for index, (start, end) in enumerate(segments):
                pose_index, alpha = schedule((start + end) // 2, facing)
                px, py = frames[pose_index]['pivot']
                keys.append(dict(Frame=index, Pose=dict(layer['Rest'], Alpha=alpha,
                                                        SourceFrame=pose_index, PivotX=px, PivotY=py)))
            tracks.append(dict(LayerId=layer['Id'], Interpolate=False, Keys=keys))

        markers = [
            dict(Name='charge', Kind='vfx', Frame=0, X=0, Y=0, Radius=0),
            dict(Name='plate_gain', Kind='vfx', Frame=times.index(PLATE_START), X=0, Y=0, Radius=0),
            dict(Name='sustain', Kind='vfx', Frame=times.index(PHASES['sustain'][1]), X=0, Y=0, Radius=0),
            dict(Name='end', Kind='vfx', Frame=times.index(PHASES['end'][1]), X=0, Y=0, Radius=0),
        ]
        clips.append(dict(Name='son_than_giang_the', Direction=facing, Loop=False,
                          DurationsMs=durations, Tracks=tracks, Markers=markers,
                          SourceNote='Studio phase preview. Body plays 16 authored poses, then holds the last pose for inspection. The zone remains aligned to the camera with the south gap.'))

    project_path = destination / 'project.json'
    document = dict(SchemaVersion=1, Scope='PRESENTATION_AUTHORING_ONLY',
                    Name='Sơn Thần Giáng Thế · 5 hướng', ProductionApproved=False,
                    Layers=layers, Sockets=sockets, Clips=clips)
    if project_path.exists():
        assert read(project_path) == document, 'Keep manual edits and choose a new preview folder'
    else:
        save(project_path, document)
    save(destination / 'assembly_descriptor.json',
         dict(scope='SANCTUARY_FIVE_FACING_STUDIO_PREVIEW', projectSha256=sha(project_path),
              sourceInputs=inputs, directionalClips=list(FACINGS), phaseReferenceFrames=footprint_references,
              previewOriginY=PREVIEW_ORIGIN_Y, plateToSustainFadeMs=[FADE_START, FADE_END],
              timelineSegments=len(durations), durationMs=CLIP_END, productionApproved=False))
    print(f'Built {len(clips)} editable clips from {len(inputs)} sources with {len(durations)} timeline segments.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=BUNDLE)
    make(parser.parse_args().destination)
