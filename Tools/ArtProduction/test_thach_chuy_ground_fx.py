import unittest
from PIL import Image,ImageDraw
from calibrate_thach_chuy_ground_fx_20261116c import bright_crack_hub

class CrackOriginTest(unittest.TestCase):
    def test_ochre_side_branch_and_invisible_matte_do_not_steal_the_hit_origin(self):
        image=Image.new('RGBA',(120,100));draw=ImageDraw.Draw(image)
        draw.rectangle((5,35,55,50),fill=(205,165,90,255))
        draw.rectangle((73,38,87,52),fill=(250,225,170,255))
        draw.rectangle((0,0,119,20),fill=(255,255,255,0))
        (x,y),count=bright_crack_hub(image)
        self.assertAlmostEqual(x,80);self.assertAlmostEqual(y,45)
        self.assertGreater(count,100)

    def test_fading_last_source_can_keep_a_small_warm_remnant(self):
        image=Image.new('RGBA',(40,30));ImageDraw.Draw(image).rectangle((18,14,20,15),fill=(225,180,115,255))
        self.assertEqual(bright_crack_hub(image),([19,14.5],6))

if __name__=='__main__':unittest.main()
