"""A Waterroot's brown whip cannot pull the registered moss/stump body."""
import unittest
from inspect_actor_library import moss_body_pivot,clear_gutter_edges


class RootRegistration(unittest.TestCase):
    def pixels(self):
        result=[(0,0,0,0)]*64
        for y in (2,3,4):
            for x in (2,3,4):result[y*8+x]=(80,140,60,255)
        return result

    def test_brown_whip_does_not_drag_stump(self):
        one=self.pixels();two=self.pixels()
        for x in range(8):one[7*8+x]=(140,80,50,255);two[x]=(140,80,50,255)
        self.assertEqual(moss_body_pivot(one,8,20,[.1,.5]),[5,13])
        self.assertEqual(moss_body_pivot(one,8,20,[.1,.5]),moss_body_pivot(two,8,20,[.1,.5]))

    def test_transparent_noise_is_not_moss(self):
        pixels=self.pixels();pixels[0]=(80,140,60,3)
        self.assertEqual(moss_body_pivot(pixels,8,20,[0,0]),[3,3])

    def test_missing_core_requires_manual_review(self):
        with self.assertRaises(AssertionError):moss_body_pivot([(140,80,50,255)]*64,8,20,[0,.5])

    def test_invalid_scale_or_offset_is_rejected(self):
        for height,offset in [(float('nan'),[0,0]),(0,[0,0]),(20,[0,float('inf')]),(20,[0,2]),(20,[0])]:
            with self.assertRaises(AssertionError):moss_body_pivot(self.pixels(),8,height,offset)

    def test_thin_whip_tip_is_not_cut_at_projection_midpoint(self):
        values=[1]*24+[0]*4+[1]*12
        self.assertEqual(clear_gutter_edges([(2,14),(28,38)],40,values),[0,26,40])

    def test_touching_source_cells_are_rejected(self):
        with self.assertRaises(AssertionError):clear_gutter_edges([(2,14),(28,38)],40,[1]*40)


if __name__=='__main__':unittest.main()
