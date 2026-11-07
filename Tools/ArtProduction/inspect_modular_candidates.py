"""Read-only structural checks for modular body candidates; never edits a bitmap."""
import argparse
import json
from pathlib import Path
from inspect_actor_library import inspect

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Modular_Characters_20261107'

def main(check=False,require_ready=False):
    plan=json.loads((ART/'modular_character_plan.json').read_text(encoding='utf8'))
    records=json.loads((ART/'generation_records.json').read_text(encoding='utf8'))
    profiles=plan['classBaseProfiles']
    assert len(profiles)==10 and len({p['baseId'] for p in profiles})==10
    assert len({p['classId'] for p in profiles})==5
    for p in profiles:
        assert p['sharedRigId']==('RIG_HUMAN_M_V1' if p['bodyFrame']=='HUMAN_M' else 'RIG_HUMAN_F_V1'),'profile/body rig mismatch'
    assert len({p['poseSetId'] for p in profiles})==10
    for class_id in {p['classId'] for p in profiles}:
        assert {p['bodyFrame'] for p in profiles if p['classId']==class_id}=={'HUMAN_M','HUMAN_F'}
    assert plan['framePolicy']['minimum']==16 and plan['framePolicy']['maximum']==20 and plan['framePolicy']['renderTargetFps']==60
    assert plan['framePolicy']['directions']==['N','NE','E','SE','S','SW','W','NW']
    assert len(plan['slotVisualBindings'])==12
    assert all(token in plan['renderParts'] for parts in plan['slotVisualBindings'].values() for token in parts)
    assert len(set(plan['renderParts']))==len(plan['renderParts'])
    pages=[]
    for record in records:
        page=inspect(record,ART)
        page.pop('file',None)  # There is no runtime export path for an unapproved master candidate.
        page.update(productionApproved=False,nativeGridReady=record['nativeGridReady'],layerFitApproved=record['layerFitApproved'])
        pages.append(page)
    required={(rig['rigId'],clip,d) for rig in plan['sharedRigs'] for clip in plan['authoring']['commonClipIds'] for d in plan['framePolicy']['directions']}
    native={(r['rigId'],r['clipId'],r['direction']) for r in records if r['nativeGridReady'] and r['layerFitApproved'] and r['productionApproved']}
    ready=bool(plan['productionReady']) and required<=native and all(p['productionApproved'] for p in profiles) and (ART/'layer_pack_registry.json').is_file()
    result=dict(scope='BASE_STYLE_CANDIDATES_NOT_APPROVED_POSE_MASTERS',classProfiles=10,sharedRigs=2,pages=pages,
        nativeCommonDirectionClipsReady=len(required&native),nativeCommonDirectionClipsRequired=len(required),
        missingWearablePackRegistry=not (ART/'layer_pack_registry.json').is_file(),productionReady=ready,
        note='Grid/hash pass is not anatomy,16-distinct-pose,layer-fit,native-grid or gameplay acceptance.')
    rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n';target=ART/'structure_report.json'
    if check:assert target.read_text(encoding='utf8')==rendered,'stale modular candidate report'
    else:target.write_text(rendered,encoding='utf8')
    print(json.dumps(dict(candidatePages=len(pages),classProfiles=10,sharedRigs=2,nativeCommonDirectionClipsReady=len(required&native),productionReady=ready)))
    if require_ready:assert ready,'modular character production pack is incomplete'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--require-ready',action='store_true');a=p.parse_args();main(a.check,a.require_ready)
