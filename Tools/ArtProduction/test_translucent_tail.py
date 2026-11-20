"""Deliberate RGBA fading is distinct from a missing/transparent source pose."""
import tempfile,unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect


class TranslucentTail(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.image=Image.new('RGBA',(96,96))
        for f in range(16):
            for y in range(9,13):
                for x in range(9,13):self.image.putpixel(((f%4)*24+x,(f//4)*24+y),(90+f,20,35,100 if f>=14 else 255))
        self.save()
        self.record=dict(id='sk_expiry_tail_fixture',source='tail.png',columns=4,rows=4,layout='VISUALLY_VERIFIED_UNIFORM_GRID',componentOnly=True,direction='OMNI',translucentTailFromFrame=14)

    def save(self):self.image.save(self.root/'tail.png')

    def test_translucent_authored_tail_is_not_missing_pose(self):
        page=inspect(self.record,self.root);frames=page['directions'][0]['frames']
        self.assertEqual(len(frames),16)
        self.assertEqual(frames[-1]['boundsAlphaThreshold'],64)
        with self.assertRaises(AssertionError):inspect({k:v for k,v in self.record.items() if k!='translucentTailFromFrame'},self.root)

    def test_fully_transparent_last_cell_still_fails(self):
        self.image.paste((0,0,0,0),(72,72,96,96));self.save()
        with self.assertRaises(AssertionError):inspect(self.record,self.root)

    def test_missing_middle_pose_cannot_use_tail_exception(self):
        self.image.paste((0,0,0,0),(24,24,48,48));self.save()
        with self.assertRaises(AssertionError):inspect(self.record,self.root)

    def test_tail_cannot_hide_actor_frames_or_early_missing_effect(self):
        for change in (dict(id='class_anh_dao_tail'),dict(componentOnly=False),dict(translucentTailFromFrame=4)):
            with self.assertRaises(AssertionError):inspect(dict(self.record,**change),self.root)

    def test_translucent_tail_still_cannot_cross_cell_edge(self):
        self.image.putpixel((95,82),(90,20,35,100));self.save()
        with self.assertRaisesRegex(AssertionError,'clipped/overlapping'):inspect(self.record,self.root)


if __name__=='__main__':unittest.main()
