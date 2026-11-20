"""A forward fall can put feet above the head; the head must not become its root."""
import hashlib,tempfile,unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect,binding_sha256


class AuthoredFootPivots(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);im=Image.new('RGBA',(96,96))
        for f in range(16):
            for y in range(5,21):
                for x in range(9,15):im.putpixel((f%4*24+x,f//4*24+y),(80+f,45,35,255))
        im.save(self.root/'fall.png')
        self.record=dict(id='class_foot_fixture',source='fall.png',columns=4,rows=4,direction='S',
                         layout='VISUALLY_VERIFIED_DIRECTIONAL_GRID',bodyReferenceHeight=20,
                         pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=[[12,21] if f<8 else [12,9] for f in range(16)])

    def test_occluded_foot_origin_is_separate_from_lowest_pixel(self):
        before=hashlib.sha256((self.root/'fall.png').read_bytes()).hexdigest();page=inspect(self.record,self.root)
        self.assertTrue(all(d['referenceHeight']==20 for d in page['directions']))
        self.assertEqual(page['directions'][0]['frames'][15]['pivot'],[12,9])
        self.assertGreater(page['directions'][0]['frames'][15]['bounds'][3],9)
        self.assertEqual(before,hashlib.sha256((self.root/'fall.png').read_bytes()).hexdigest())
        changed=dict(self.record,sourceFootPivots=[[12,21]]*16)
        self.assertNotEqual(binding_sha256(page),binding_sha256(inspect(changed,self.root)))

    def test_actor_foot_contract_rejects_wrong_kind_scale_or_coordinates(self):
        changes=[dict(id='sk_foot_fixture',componentOnly=True),dict(componentOnly=True),dict(scaleMode='LONGEST_AXIS'),
                 dict(pivotMode='SOURCE_PIVOTS'),dict(sourceFootPivots=None),dict(sourceFootPivots=[[12,9]]*15),
                 dict(sourceFootPivots=[[True,9]]*16),dict(sourceFootPivots=[[12,float('inf')]]*16),
                 dict(sourceFootPivots=[[24,9]]*16),dict(sourceFootPivots=[[12,-1]]*16)]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(AssertionError):inspect(dict(self.record,**change),self.root)
        without_height={k:v for k,v in self.record.items() if k!='bodyReferenceHeight'}
        with self.assertRaises(AssertionError):inspect(without_height,self.root)


if __name__=='__main__':unittest.main()
