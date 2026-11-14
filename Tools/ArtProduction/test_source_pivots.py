"""Attachment metadata must not modify original RGBA or bypass source gates."""
import hashlib,tempfile,unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect,binding_sha256


class SourcePivots(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);image=Image.new('RGBA',(96,96))
        for f in range(16):
            for y in range(9,13):
                for x in range(9,13):image.putpixel(((f%4)*24+x,(f//4)*24+y),(150+f,40,20,255))
        image.save(self.root/'fx.png')
        self.record=dict(id='sk_attachment_fixture',componentOnly=True,source='fx.png',columns=4,rows=4,
                         layout='VISUALLY_VERIFIED_UNIFORM_GRID',direction='OMNI',pivotMode='SOURCE_PIVOTS',
                         sourcePivots=[[8+f/16,15] for f in range(16)])

    def test_metadata_moves_attachment_without_reencoding(self):
        before=hashlib.sha256((self.root/'fx.png').read_bytes()).hexdigest()
        page=inspect(self.record,self.root)
        self.assertEqual([f['pivot'] for f in page['directions'][0]['frames']],self.record['sourcePivots'])
        self.assertEqual(before,hashlib.sha256((self.root/'fx.png').read_bytes()).hexdigest())
        changed=dict(self.record,sourcePivots=[[10,15]]*16)
        self.assertNotEqual(binding_sha256(page),binding_sha256(inspect(changed,self.root)))

    def test_invalid_attachment_contract_rejected(self):
        for change in (dict(id='class_fake'),dict(componentOnly=False),dict(pivotMode='CELL_CENTER'),
                       dict(sourcePivots=None),dict(sourcePivots=[[8,15]]*15),dict(sourcePivots=[[float('nan'),15]]*16),
                       dict(sourcePivots=[[True,15]]*16),dict(sourcePivots=[[24,15]]*16),dict(sourcePivots=[[-1,15]]*16)):
            with self.subTest(change=change),self.assertRaises(AssertionError):inspect(dict(self.record,**change),self.root)

    def test_custom_attachment_cannot_hide_empty_pose(self):
        image=Image.open(self.root/'fx.png');image.paste((0,0,0,0),(72,72,96,96));image.save(self.root/'fx.png')
        with self.assertRaisesRegex(AssertionError,'empty frame'):inspect(self.record,self.root)


if __name__=='__main__':unittest.main()
