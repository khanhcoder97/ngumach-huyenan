"""Nonuniform effect regions retain the same crop/empty/source gates."""
import tempfile,unittest
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect

class EffectGrid(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.image=Image.new('RGBA',(160,160));self.xx=[0,42,83,120,160];self.yy=[0,43,79,122,160]
        for f in range(16):
            for y in range(self.yy[f//4]+6,self.yy[f//4]+22):
                for x in range(self.xx[f%4]+7,self.xx[f%4]+20):self.image.putpixel((x,y),(20+f,150,190,255))
        self.image.save(self.root/'fixture.png')
        self.record=dict(id='sk_grid_fixture',source='fixture.png',columns=4,rows=4,componentOnly=True,
            layout='VISUALLY_VERIFIED_UNIFORM_GRID',layoutReviewNote='Synthetic test fixture, not production art.',
            gridEdges=dict(columns=self.xx,rows=self.yy))
    def test_reviewed_regions_keep_original_nonuniform_geometry(self):
        page=inspect(self.record,self.root);frames=page['directions'][0]['frames']
        self.assertEqual(len(frames),16);self.assertEqual(frames[0]['rect'],[0,0,42,43]);self.assertEqual(frames[-1]['rect'],[120,122,40,38])
    def test_effect_edges_require_review_and_valid_source_bounds(self):
        for change in (dict(layoutReviewNote=''),dict(gridEdges=dict(columns=[0,42,83,120,161],rows=self.yy)),dict(gridEdges=dict(columns=[0,83,42,120,160],rows=self.yy))):
            with self.assertRaises(AssertionError):inspect(dict(self.record,**change),self.root)
    def test_explicit_regions_do_not_suppress_clipped_pixel_gate(self):
        self.image.putpixel((41,18),(220,250,255,255));self.image.save(self.root/'fixture.png')
        with self.assertRaisesRegex(AssertionError,'clipped/overlapping'):inspect(self.record,self.root)

if __name__=='__main__':unittest.main()
