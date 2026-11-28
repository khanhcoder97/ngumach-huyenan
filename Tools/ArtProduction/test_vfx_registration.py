"""A symmetric charge converges around its authored center across grid drift."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect


class SymmetricVfxRegistration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);image=Image.new('RGBA',(96,96))
        for f in range(16):
            cx=8+2*(f%4);cy=9+f//4;radius=2+f//4
            for x,y in ((cx-radius,cy),(cx+radius,cy),(cx,cy-radius),(cx,cy+radius)):
                image.putpixel(((f%4)*24+x,(f//4)*24+y),(240,240,225,255))
        image.save(self.root/'charge.png')
        self.record=dict(id='sk_charge_registration_fixture',source='charge.png',columns=4,rows=4,
                         layout='VISUALLY_VERIFIED_UNIFORM_GRID',direction='OMNI')

    def test_shifted_symmetric_source_centers_are_registered(self):
        page=inspect(dict(self.record,pivotMode='SYMMETRIC_BOUNDS_CENTER'),self.root)
        for f,frame in enumerate(page['directions'][0]['frames']):
            self.assertEqual(frame['pivot'],[8+2*(f%4)+.5,9+f//4+.5])

    def test_existing_cell_center_registration_remains_fixed(self):
        page=inspect(dict(self.record,pivotMode='CELL_CENTER'),self.root)
        self.assertTrue(all(f['pivot']==[12,12] for f in page['directions'][0]['frames']))


if __name__=='__main__':unittest.main()
