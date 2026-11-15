"""Synthetic read-only landmark regression fixtures, never game image generation."""
import unittest
from PIL import Image,ImageDraw
from calibrate_huyen_but_20261114g import boot_root
from refine_huyen_but_g_support import three_node_origin

class LowDodgeRegistration(unittest.TestCase):
    def test_compressed_feet_behind_head_remain_detectable(self):
        image=Image.new('RGBA',(160,160))
        drawing=ImageDraw.Draw(image)
        drawing.rectangle((90,10,130,65),fill=(25,25,25,255))
        drawing.rectangle((45,60,110,85),fill=(180,190,210,255))
        drawing.rectangle((40,86,61,95),fill=(35,38,44,255))
        drawing.rectangle((85,87,104,95),fill=(35,38,44,255))
        x,y,low=boot_root(image,dict(top=10,centerX=110,span=70),140,True)
        self.assertTrue(low);self.assertEqual(y,96);self.assertEqual(x,72)

    def test_warm_brush_below_boots_cannot_extend_ground(self):
        image=Image.new('RGBA',(160,160));drawing=ImageDraw.Draw(image)
        drawing.rectangle((60,0,100,60),fill=(25,25,25,255))
        drawing.rectangle((60,80,98,105),fill=(180,190,210,255))
        drawing.rectangle((65,110,95,121),fill=(35,38,44,255))
        drawing.rectangle((100,105,106,150),fill=(110,65,25,255))
        x,y,low=boot_root(image,dict(top=0,centerX=80,span=70),122,False)
        self.assertEqual(y,122);self.assertEqual(x,80)

    def test_missing_boots_requires_manual_review(self):
        image=Image.new('RGBA',(160,160));drawing=ImageDraw.Draw(image)
        drawing.rectangle((60,10,100,60),fill=(25,25,25,255))
        drawing.rectangle((60,80,100,125),fill=(180,190,210,255))
        with self.assertRaisesRegex(AssertionError,'boot'):
            boot_root(image,dict(top=10,centerX=80,span=70),115,False)

    def test_three_node_centroid_keeps_forming_arc_origin(self):
        image=Image.new('RGBA',(120,120));drawing=ImageDraw.Draw(image)
        for x,y in ((60,20),(30,80),(90,80)):
            drawing.rectangle((x-3,y-3,x+3,y+3),fill=(80,220,100,255))
        origin,nodes=three_node_origin(image,[20,10,100,90])
        self.assertEqual(len(nodes),3)
        self.assertAlmostEqual(origin[0],60);self.assertAlmostEqual(origin[1],60)

if __name__=='__main__':unittest.main()
