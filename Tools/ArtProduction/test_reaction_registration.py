"""Sole registration must keep dark boots and exclude hair/thin held steel."""
import unittest
from PIL import Image
from calibrate_anh_dao_reactions import dark_points


class ReactionRegistration(unittest.TestCase):
    def test_two_boot_colors_survive_while_hair_and_thin_blade_do_not(self):
        im=Image.new('RGBA',(48,48))
        im.paste((40,25,35,255),(10,2,38,18))
        im.paste((18,17,26,255),(10,32,20,44))
        im.paste((85,50,30,255),(28,32,38,44))
        im.paste((90,90,90,255),(42,30,43,48))
        points=dark_points(im,[0,30,48,48])
        self.assertTrue(any(x<20 for x,y in points) and any(28<=x<38 for x,y in points))
        self.assertTrue(all(y>=30 and x!=42 for x,y in points))

    def test_faint_color_residue_cannot_define_a_foot(self):
        im=Image.new('RGBA',(48,48),(20,15,20,3))
        self.assertEqual(dark_points(im,[0,0,48,48]),[])


if __name__=='__main__':unittest.main()
