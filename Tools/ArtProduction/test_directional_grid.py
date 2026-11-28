"""Sparse blade pixels must survive a reviewed grid without bypassing crop gates."""
import tempfile,unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect,dark_boot_foot_pivot


class DirectionalGrid(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.image=Image.new('RGBA',(160,160))
        for f in range(16):
            x=(f%4)*40;y=(f//4)*40
            for yy in range(8,28):
                for xx in range(9,21):self.image.putpixel((x+xx,y+yy),(48+f,31,36,255))
            self.image.putpixel((x+33,y+16),(180,190,205,255))
        self.image.save(self.root/'actor.png')
        self.record=dict(id='class_anh_dao_grid_fixture',source='actor.png',columns=4,rows=4,direction='E',layout='VISUALLY_VERIFIED_DIRECTIONAL_GRID')

    def test_isolated_prop_is_retained_in_each_source_cell(self):
        page=inspect(self.record,self.root)
        self.assertEqual(page['sourceFrames'],16)
        self.assertTrue(all(f['bounds'][2]==34 for f in page['directions'][0]['frames']))

    def test_grid_still_rejects_clipped_prop(self):
        self.image.putpixel((39,16),(180,190,205,255));self.image.save(self.root/'actor.png')
        with self.assertRaisesRegex(AssertionError,'clipped/overlapping'):inspect(self.record,self.root)

    def test_grid_requires_actor_and_one_declared_direction(self):
        for change in (dict(id='sk_not_actor'),dict(direction='OMNI'),dict(columns=8)):
            with self.assertRaises(AssertionError):inspect(dict(self.record,**change),self.root)

    def test_explicit_edges_cannot_hide_outside_or_reverse_regions(self):
        for columns in ([0,40,80,120,161],[0,80,40,120,160],[0,40,80,160]):
            record=dict(self.record,gridEdges=dict(columns=columns,rows=[0,40,80,120,160]))
            with self.assertRaises(AssertionError):inspect(record,self.root)

    def test_dark_plum_soles_reject_downward_blade_contour(self):
        pixels=[(0,0,0,0)]*1600
        for y in range(26,35):
            for x in (*range(8,17),*range(23,32)):pixels[y*40+x]=(44,31,36,255)
        before=dark_boot_foot_pivot(pixels,40,40)
        for y in range(24,40):
            pixels[y*40+36]=(25,18,21,255)
            pixels[y*40+37]=(180,190,205,255)
        self.assertEqual(dark_boot_foot_pivot(pixels,40,40),before)
        self.assertEqual(before,[19.5,36])


if __name__=='__main__':unittest.main()
