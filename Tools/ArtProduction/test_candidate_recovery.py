"""Recovery must not duplicate a job, erase calibration or replace prior pixels."""
import json,tempfile,unittest
from pathlib import Path
from PIL import Image
import record_generated_candidate as writer

class CandidateRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        old=(writer.ROOT,writer.ART);self.addCleanup(lambda:setattr(writer,'ROOT',old[0]));self.addCleanup(lambda:setattr(writer,'ART',old[1]))
        writer.ROOT=self.root;writer.ART=self.root/'art';writer.ART.mkdir()
        self.native=self.root/'native.png';Image.new('RGBA',(8,8),(20,90,180,255)).save(self.native)
        (self.root/'reference.png').write_bytes(self.native.read_bytes())
        self.job=dict(batch='recovery',id='sk_fixture',expectedSourcePages=1,scope='TEST_ONLY',seconds=.32,prompt='Synthetic persistence fixture.',nativeSourceFile=str(self.native),references=['reference.png'])
        self.manifest=writer.ART/'Candidates_recovery/candidate_manifest.json'
    def test_replay_preserves_calibration_and_single_selection(self):
        writer.record(self.job);m=writer.read(self.manifest);m['records'][0]['status']='NATIVE_REVIEW_HOLD';m['records'][0]['sourcePivots']=[[4,4]]*16;writer.save(self.manifest,m)
        self.assertTrue(writer.record(self.job)['recoveredExisting']);self.assertEqual(writer.read(self.manifest),m)
    def test_same_version_cannot_replace_different_native_bytes(self):
        first=writer.record(self.job);original=Path(first['file']).read_bytes()
        Image.new('RGBA',(8,8),(180,90,20,255)).save(self.native)
        with self.assertRaisesRegex(AssertionError,'different source'):writer.record(self.job)
        self.assertEqual(Path(first['file']).read_bytes(),original)
    def test_new_version_archives_selection_without_deleting_original(self):
        first=writer.record(self.job);original=Path(first['file']).read_bytes();Image.new('RGBA',(8,8),(40,120,220,255)).save(self.native)
        writer.record(dict(self.job,version=2));m=writer.read(self.manifest)
        self.assertEqual((m['selected'],m['generatedVariants'],len(m['history'])),(1,2,1));self.assertEqual(Path(first['file']).read_bytes(),original)

if __name__=='__main__':unittest.main()
