"""Synthetic contact tests, never game raster editing or pose acceptance."""
import unittest
from PIL import Image,ImageDraw
from prepare_foundation_candidates_20261115i import cool_body_contact
class FoundationContact(unittest.TestCase):
    def test_warm_brush_below_body_cannot_drag_ground(self):
        image=Image.new('RGBA',(160,160));draw=ImageDraw.Draw(image)
        draw.rectangle((40,20,119,110),fill=(170,190,210,255));draw.rectangle((130,60,138,150),fill=(180,120,40,255))
        draw.rectangle((128,60,129,150),fill=(20,20,20,255));draw.rectangle((139,60,140,150),fill=(20,20,20,255))
        self.assertEqual(cool_body_contact(image),(79.5,111))
    def test_flat_cloth_body_retains_ground_when_boots_are_occluded(self):
        image=Image.new('RGBA',(160,160));draw=ImageDraw.Draw(image)
        draw.rectangle((20,80,139,104),fill=(180,195,220,255))
        self.assertEqual(cool_body_contact(image),(79.5,105))
    def test_absent_body_requires_manual_landmark(self):
        image=Image.new('RGBA',(160,160));ImageDraw.Draw(image).rectangle((70,40,80,140),fill=(200,130,40,255))
        with self.assertRaisesRegex(AssertionError,'manual registration'):cool_body_contact(image)
if __name__=='__main__':unittest.main()
