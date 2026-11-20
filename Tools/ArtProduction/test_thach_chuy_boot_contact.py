import unittest
import hashlib,json,tempfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
from prepare_thach_chuy_candidates_20261116c import boot_contact,sash_landmark,neutral_foot_center
import prepare_thach_chuy_candidates_20261116c as registration
class HammerRootTest(unittest.TestCase):
    def test_steel_hammer_below_feet_does_not_pull_root(self):
        im=Image.new('RGBA',(160,160));d=ImageDraw.Draw(im)
        d.rectangle((45,100,64,115),fill=(90,60,35,255));d.rectangle((75,100,94,115),fill=(90,60,35,255))
        # Warm reflected steel/stone from the real pilot also looked brown to
        # the first mask; an exactly grey fixture did not expose that mistake.
        d.rectangle((0,120,35,150),fill=(105,90,75,255));d.rectangle((15,75,25,94),fill=(110,75,40,255))
        self.assertEqual(boot_contact(im,10,100),(69.5,116))
    def test_crouched_boots_keep_ground_with_same_neutral_body_height(self):
        im=Image.new('RGBA',(160,140));d=ImageDraw.Draw(im)
        d.rectangle((45,84,64,95),fill=(90,60,35,255));d.rectangle((75,84,94,95),fill=(90,60,35,255))
        d.rectangle((0,96,35,125),fill=(105,90,75,255))
        self.assertEqual(boot_contact(im,40,100),(69.5,96))
    def test_red_sash_reference_is_not_the_brown_shaft_or_warm_steel(self):
        im=Image.new('RGBA',(160,140));d=ImageDraw.Draw(im)
        d.rectangle((60,60,80,75),fill=(120,45,25,255))
        d.rectangle((5,60,25,80),fill=(110,75,40,255));d.rectangle((100,60,145,90),fill=(105,90,75,255))
        d.rectangle((0,50,2,100),fill=(200,0,0,255))
        self.assertEqual(sash_landmark(im,10,100),(70,336))
    def test_neutral_anchor_includes_both_boots_even_with_a_cold_toe_plate(self):
        im=Image.new('RGBA',(160,140));d=ImageDraw.Draw(im)
        d.rectangle((40,100,60,115),fill=(90,60,35,255));d.rectangle((80,100,100,115),fill=(80,80,80,255))
        d.rectangle((115,85,145,100),fill=(105,90,75,255))
        self.assertEqual(neutral_foot_center(im,116,100),70)
    def test_bad_late_source_does_not_replace_existing_review_projects(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);art=root/'art';art.mkdir();ev=root/'evidence'
            folder=art/('Candidates_'+registration.BATCH);folder.mkdir();records=[]
            for identifier in ('sk_first','sk_bad'):
                source=art/(identifier+'.png');source.write_bytes(b'unchanged-test-source')
                records.append(dict(id=identifier,source=source.name,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sourceFrameDurationsMs=[25]*16,componentOnly=True))
            (folder/'candidate_manifest.json').write_text(json.dumps(dict(expectedSourcePages=50,selected=2,records=records)))
            for name in ('generation_records.json','visual_review.json','structure_report.json'):(art/name).write_text('[]')
            project=ev/'Candidate_Studio/sk_first/project.json';project.parent.mkdir(parents=True);project.write_text('existing captured project')
            page=dict(sourceFrames=16,sha256=records[0]['sourceSha256'],directions=[dict(referenceHeight=100,frames=[dict(rect=[0,0,100,100],pivot=[50,50]) for _ in range(16)])])
            with patch.object(registration,'ROOT',root),patch.object(registration,'ART',art),patch.object(registration,'EV',ev),patch.object(registration,'inspect',side_effect=[page,AssertionError('rows expected 4, got 5')]):
                with self.assertRaisesRegex(AssertionError,'rows expected 4, got 5'):registration.prepare()
            self.assertEqual(project.read_text(),'existing captured project')
            self.assertFalse((project.parent/'source_registration.json').exists())
            self.assertFalse((ev/'candidate_review_plan.json').exists())
    def test_incremental_review_does_not_reuse_a_cache_with_old_source_timing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);art=root/'art';art.mkdir();ev=root/'evidence';folder=art/('Candidates_'+registration.BATCH);folder.mkdir()
            records=[]
            for identifier,timing in (('sk_changed',[30]*16),('sk_new',[25]*16)):
                source=art/(identifier+'.png');source.write_bytes(identifier.encode())
                records.append(dict(id=identifier,source=source.name,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sourceFrameDurationsMs=timing,componentOnly=True))
            (folder/'candidate_manifest.json').write_text(json.dumps(dict(expectedSourcePages=50,selected=2,records=records)))
            for name in ('generation_records.json','visual_review.json','structure_report.json'):(art/name).write_text('[]')
            old=dict(records[0],sourceFrameDurationsMs=[25]*16);bundle=ev/'Candidate_Studio/sk_changed';(bundle/'textures').mkdir(parents=True)
            (bundle/'textures/old.png').write_bytes(b'sk_changed');project=bundle/'project.json'
            project.write_text(json.dumps(dict(Layers=[dict(Texture='textures/old.png')],Clips=[dict(DurationsMs=[25]*16)])));before=project.read_bytes()
            (art/('body_registration_'+registration.BATCH+'.json')).write_text(json.dumps(dict(entries=[dict(record=old,page={})])))
            page=dict(sourceFrames=16,sha256=records[1]['sourceSha256'],directions=[dict(referenceHeight=100,frames=[dict(rect=[0,0,100,100],pivot=[50,50]) for _ in range(16)])])
            with patch.object(registration,'ROOT',root),patch.object(registration,'ART',art),patch.object(registration,'EV',ev),patch.object(registration,'inspect',return_value=page):registration.prepare(['sk_new'])
            plan=json.loads((ev/'candidate_review_plan.json').read_text())
            self.assertEqual([e['id'] for e in plan['entries']],['sk_new'])
            self.assertEqual(plan['missingCandidateIds'],['sk_changed'])
            self.assertEqual(project.read_bytes(),before)
if __name__=='__main__':unittest.main()
