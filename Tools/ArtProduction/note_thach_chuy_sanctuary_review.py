"""Record the nine viewed Sơn Thần Giáng Thế sheets and their native evidence."""
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha

BODY = 'class_thach_chuy_skill_06_'
FX = 'sk_tc_06_'
NOTES = {
    BODY + 's': 'One lift and planted hammer in all 16 views. Boots stay on the ground reference while the hammer drops below them. Check the neutral hand and foot transition against owner idle.',
    BODY + 'e': 'Right-facing profile with one hammer, one plant and a readable standing recovery. Check the forward lean against the gameplay camera and the initial idle grip.',
    BODY + 'se': 'Sixteen down-right poses viewed. The hammer partly hides the far boot during the low brace, so a hand-checked stance pivot holds the centre. Confirm its transition to the owner idle.',
    BODY + 'ne': 'Upper-right rear-quarter lean and one connected hammer throughout the set. Unequal row gutters preserve the overhead pose. Verify the hand-checked stance pivot against idle and world scale.',
    BODY + 'n': 'V2 removes the second hammer silhouette at the plant. One head and shaft are readable throughout. Phase 11 leans away from the registered centre and needs a fixed-camera root check.',
    FX + 'zone_charge_component': 'Sparse footing marks accumulate around the rim and clear as the stones rise. Lower opening stays empty. The fixed footprint avoids recentering when only three upper markers are drawn.',
    FX + 'plate_gain_component': 'One shallow footing emerges from small grains. The bottom aligns through the rise and settle. Validate how its ending shape meets the sustained stones.',
    FX + 'open_zone_sustain_component': 'Sixteen quiet gold-rim phases viewed. The bottom gap stays open at the wrap from phase 15 to phase 0. Validate the full-width rim in the assembled view.',
    FX + 'zone_end_component': 'Starts with a low open rim and dissolves once into small chips around it. The inner area and closest opening stay clear. Verify the handoff from the last sustained pose.',
}


def record_views():
    manifest = read(ART / 'Candidates_20261116c/candidate_manifest.json')
    sources = {record['id']: record for record in manifest['records']}
    audit_path = EV / 'native_media_audit.current.json'
    native = read(audit_path)
    movies = {item['file']: item for item in native['files']}
    observations_path = EV / 'manual_review_observations.json'
    observations = read(observations_path)
    entries = []
    bindings = []
    for identifier, note in NOTES.items():
        source_sha = sources[identifier]['sourceSha256']
        project = EV / 'Candidate_Studio' / identifier / 'project.json'
        movie = EV / f'raw_{identifier}.mp4'
        montage = EV / f'raw_{identifier}_poses.png'
        captured = movies[movie.name]
        assert captured['sourceSha256'] == sha(ART / sources[identifier]['source']) == source_sha
        assert captured['portableProjectSha256'] == sha(project) and captured['sha256'] == sha(movie)
        assert captured['renderedSourceFramesVerified'] == 16
        binding = dict(id=identifier, sourceSha256=source_sha, portableProjectSha256=sha(project),
                       movieSha256=sha(movie), montageSha256=sha(montage))
        bindings.append(binding)
        entries.append(dict(**binding, originalAtlasViewed=True, nativePoseFramesInspected=16,
                            visualNotes=note, status='SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED',
                            productionApproved=False))

    seam = next(item for item in native['loopSeams'] if item['id'] == FX + 'open_zone_sustain_component')
    assert sha(EV / seam['file']) == seam['sha256']
    binding_path = EV / 'manual_view_bindings.sanctuary_20261118.json'
    packet = dict(scope='LOCKED_MANUAL_SANCTUARY_SOURCE_VIEW', entries=bindings,
                  loopSeam={key: seam[key] for key in ('id', 'file', 'sha256', 'nativeFrames')})
    if binding_path.exists():
        assert read(binding_path) == packet, 'Review the changed evidence and use a new observation packet'
    else:
        save(binding_path, packet)
    seam['manualViewed'] = True
    observations['entries'] = [item for item in observations['entries'] if item['id'] not in NOTES] + entries
    save(observations_path, observations)
    save(audit_path, native)
    print(f'Recorded {len(entries)} reviewed sources and the sanctuary sustain loop wrap.')


if __name__ == '__main__':
    record_views()
