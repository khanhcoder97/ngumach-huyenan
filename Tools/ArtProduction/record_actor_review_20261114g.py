"""Serialize the completed manual observations; apply them with the separate guarded tool."""
import hashlib,json
from inspect_actor_library import ART,ROOT
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g'
HOLDS={
 'class_huyen_but_run_n':'HOLD: Native16 poses repeat very similar leading-foot/arm silhouettes at0 and8. The intended opposite support remains ambiguous behind the robe; redraw readable alternating contacts. Pixel uniqueness does not prove a16-phase stride.',
 'class_huyen_but_run_e':'HOLD: Native side-view16 poses return to a very similar front-boot/empty-fist configuration at0 and8. Opposite anatomical supports for the intended single stride are not clear enough; redraw leg passing/contact shapes before approval.',
 'class_huyen_but_interact_ne':'HOLD: Around sources5..10 the idle rear-left dangling hand remains visible while another empty palm reaches in front and the right hand holds the brush. This reads as three hands; remove the retained idle hand and redraw proper far-arm occlusion.'}
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def note(identifier):
    if identifier in HOLDS:return HOLDS[identifier]
    facing=identifier.rsplit('_',1)[-1].upper()
    if '_basic_attack_02_' in identifier:return 'PASS source '+facing+': all16 native poses inspected. One connected right-hand brush follows a rising flick, empty left hand balances, facing and costume retained, stable boot root and return. Eight-facing comparison inspected; strike/VFX timing in gameplay remains unaccepted.'
    if '_basic_attack_03_' in identifier:return 'PASS source '+facing+': all16 native poses inspected. Distinct lift, low downward stroke and recoil/return; knees/shoulder/brush drawings change through the action, only one brush, no left-hand tip or cropped limb. Native eight-facing comparison inspected; full combat assembly unaccepted.'
    if '_dodge_' in identifier:return 'PASS source '+facing+': all16 native poses inspected. Low staggered quickstep, cloth/braid follow-through, connected limbs and right brush, recover to standing. Compressed-pose boot origins remain stable; E background halo absent in native view. In-place source only, not world displacement or collision acceptance.'
    if '_interact_' in identifier:return 'PASS source '+facing+': all16 native poses inspected. Courteous bow then one empty left-palm extension and return while right hand keeps the brush. Two hands only, face/facing retained, no invented pickup prop, stable source root. Dialogue/quest interaction is outside this source review.'
    if identifier in ('class_huyen_but_run_ne','class_huyen_but_run_se'):
        return 'PASS source '+facing+': all16 native poses and actual14/15/0/1 loop wrap inspected. Opposite leg extensions and arm/brush counter-motion readable; narrow boots remain connected, rear/front diagonal stays distinct from N/E. No borrowed cells or mirrored authored pose claims. Source-loop approval only; in-world gait speed/root motion unaccepted.'
    if identifier=='class_huyen_but_run_s':return 'PASS v3 source S: all16 final native poses plus actual14/15/0/1 wrap and updated eight-facing comparison inspected. Opposite0/8 forward-boot shapes now separate outside the hem; dark plain boots/brown belt restored after the rejected armour-contaminated v2. One right brush, empty left hand, stable measured root. Cross-action style transitions and world travel remain unaccepted.'
    if identifier=='class_huyen_but_skill_03_n':return 'PASS repaired shield-cast N source: all16 native poses inspected. Right brush stays connected or naturally occluded during the chest crossover, left palm remains visibly empty; old left-sleeve handoff ambiguity removed. Rear view and boot root stable; full shield/target/confirmed-event assembly unaccepted.'
    if identifier=='class_huyen_but_skill_04_n':return 'PASS repaired rain-cast N source: all16 native poses inspected. Low brush ellipse then lift/settle, empty left hand, one cream tip including source9; old duplicate tip removed. Stable rear root; per-facing source-clock/presentation alignment and heal-zone mechanics unaccepted.'
    notes={
      'sk_hb_04_rain_component':'Sparse ivory-core droplets and separate landing rings now read clearly on native grid. All16 phases and actual14/15/0/1 loop wrap inspected; no opaque veil/whole-field jump. Zone density/scaling with actors and server heal ticks still unaccepted.',
      'sk_hb_05_departure_component':'Two low diagonal water strokes draw and release into beads over16 phases; no vertical cloud, solid badge or cropped tip. Fixed emitter registration inspected. Source preview0.32s visits16 phases at60Hz and does not change server mobility duration.',
      'sk_hb_05_trail_component':'First low wake then staggered second wake, development and small fading beads readable through16 phases. Separate grounded marks with a clear path axis, no character/solid haze; module only, not proof of path/collision or all-direction trail assembly.',
      'sk_hb_05_expire_component':'Selected v2 begins with developed paired shallow crescents then only fragments/shrinks into beads over16 phases; rejected v1 buildup not used. Fixed ground footprint remains stable; no late bright reactivation.',
      'sk_hb_06_tell_component':'Final16 native poses inspected after complete-triangle row383 correction. Three jade nodes/arcs remain grouped per cell; centroid of persistent nodes holds the source origin as arcs close. Empty centre, no borrowed next-row nodes. Gameplay radius/telegraph readability still requires assembly.',
      'sk_hb_06_wave_component':'All16 native phases inspected: small low ellipse expands to a broad rim then fragments; open centre, restrained bright leading edge, no opaque dome or screen fog. Stable ellipse centre. Module is not an8m gameplay hitbox or confirmed heal event.',
      'sk_hb_06_ally_heal_component':'Final16 native poses inspected after measured early-row foot origins replace unequal cell84percent anchors. Two narrow separate ribbons develop from feet then rise/break into beads, centre remains open; no row-boundary emitter jump. Ally attach/scaling and actual heal confirmation unaccepted.',
      'sk_hb_06_cleanse_component':'All16 native phases inspected: a few dull violet motes split under two crisp outward jade sweeps, then fade. Open centre, no opaque poison cloud, skull/cross badge or stun-removal claim; effect cannot remove a status without a confirmed server event.',
      'sk_hb_06_expire_component':'Final v3 all16 native poses inspected after row876 complete-triangle correction. Same three-node motif as preparation; arcs shorten and three bead groups fade at a stable origin, without an extra next-row top node or background tint. Transition with the complete ultimate still needs assembly.'}
    assert identifier in notes,'No manual observation for '+identifier
    return 'PASS source component: '+notes[identifier]

def record():
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114g'];assert len(records)==36
    pages={p['id']:p for p in read(ART/'structure_report.json')['pages']}
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==43
    assert len(read(ART/'visual_review.json')['sourceApprovals'])==329,'Do not rewrite an applied ledger'
    old=read(EV/'manual_review_working.json');historical=list(old.get('historicalSourceObservations',[]))
    for entry in old['entries']:
        if entry['sourceSha256']!=pages[entry['id']]['sha256']:
            assert entry['id']=='class_huyen_but_run_s'
            proof=EV/'Superseded_Run_S1'/('raw_'+entry['id']+'_poses.png');assert sha(proof)==entry['nativePoseProofSha256']
            historical.append({**entry,'nativePoseProof':proof.relative_to(ROOT).as_posix(),'supersededBySource':pages[entry['id']]['source']})
    entries=[]
    for source in records:
        identifier=source['id'];page=pages[identifier];prefix='raw_'+identifier
        files=[prefix+'.mp4',prefix+'.png',prefix+'_poses.png',prefix+'_source_samples.png',prefix+'_samples.png']
        if source.get('direction'):
            clip=identifier[len('class_huyen_but_'):].rsplit('_',1)[0]
            files += [clip+'_eight_angles'+suffix for suffix in ('.mp4','.png','_samples.png')]
        if (EV/(prefix+'_loop_seam.png')).is_file():files.append(prefix+'_loop_seam.png')
        evidence=[(EV/f).relative_to(ROOT).as_posix() for f in files]
        entries.append(dict(id=identifier,sourceSheet=(ART/source['source']).relative_to(ROOT).as_posix(),sourceSha256=page['sha256'],bindingSha256=page['bindingSha256'],productionApproved=identifier not in HOLDS,nativeReviewed=True,reviewedSourceFrames=16,visualNotes=note(identifier),nativeEvidence=evidence,nativeEvidenceSha256={f:sha(ROOT/f) for f in evidence}))
    assert sum(e['productionApproved'] for e in entries)==33
    ledger=dict(batch='20261114g',manualReviewComplete=True,reviewDate='2026-11-15',reviewScale='ORIGINAL_ATLAS_AND_256PX_NATIVE_STAGE_16_REAL_PHASES_PLUS_8_FACINGS_AND_LOOP_WRAPS',scope='SOURCE_CLIP_VISUAL_REVIEW_NOT_CLASS_SKILL_ASSEMBLY_OR_GAMEPLAY_ACCEPTANCE',entries=entries)
    save(EV/'source_native_review.json',ledger)
    save(EV/'manual_review_working.json',dict(**ledger,historicalSourceObservations=historical,browserStatusHeaders='Captured before final ledger application; HOLD counts there are not the final catalogue status.'))
    print(json.dumps(dict(selected=36,sourceApprovals=33,sourceHolds=3,heldIds=list(HOLDS),ledgerPreparedNotApplied=True)))

if __name__=='__main__':record()
