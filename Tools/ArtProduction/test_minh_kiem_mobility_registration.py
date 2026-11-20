"""Warm boot registration must ignore the held silver jian and teal coat."""
import unittest
from PIL import Image,ImageDraw
from calibrate_minh_kiem_extended import brown_boot_landmark


class MinhKiemBootRegistration(unittest.TestCase):
    def fixture(self):
        image=Image.new('RGBA',(140,120));draw=ImageDraw.Draw(image)
        draw.rectangle((20,92,38,112),fill=(90,65,45,255));draw.rectangle((70,92,90,112),fill=(90,65,45,255))
        return image

    def test_both_boots_center_and_contact(self):
        anchor=brown_boot_landmark(self.fixture(),[10,10,135,118])
        self.assertEqual(anchor['centerX'],55);self.assertEqual(anchor['bottom'],114)

    def test_steel_gold_and_teal_cannot_extend_root(self):
        image=self.fixture();baseline=brown_boot_landmark(image,[10,10,135,118]);draw=ImageDraw.Draw(image)
        for x,color in ((96,(125,115,110,255)),(110,(210,160,65,255)),(124,(45,80,75,255))):
            draw.rectangle((x,92,x+8,115),fill=color)
        self.assertEqual(brown_boot_landmark(image,[10,10,135,118]),baseline)

    def test_raised_one_boot_does_not_select_only_lowest_foot(self):
        image=self.fixture();draw=ImageDraw.Draw(image);draw.rectangle((70,105,90,112),fill=(0,0,0,0))
        self.assertEqual(brown_boot_landmark(image,[10,10,135,118])['centerX'],55)

    def test_missing_boots_requires_manual_review(self):
        with self.assertRaises(AssertionError):brown_boot_landmark(Image.new('RGBA',(140,120)),[10,10,135,118])


if __name__=='__main__':unittest.main()
