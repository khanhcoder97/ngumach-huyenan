"""Packing offsets and airborne feet must not redefine the visible ground root."""
import unittest
from PIL import Image,ImageDraw
from calibrate_anh_dao_mobility import run_ground_trace,both_boot_landmark
from audit_mobility_registration import hair_landmark


class MobilityRegistration(unittest.TestCase):
    def test_packed_frame_offsets_preserve_head_to_root_distance(self):
        heads=[[40+i*2,60+i*3] for i in range(16)]
        pivots=run_ground_trace(heads,90,114,0)
        for head,pivot in zip(heads,pivots):self.assertAlmostEqual(pivot[1]-head[1],30)

    def test_visible_opposite_contacts_and_closed_trace(self):
        heads=[[50,60] for _ in range(16)];pivots=run_ground_trace(heads,90,94,0)
        self.assertEqual(pivots[0][1],90);self.assertEqual(pivots[8][1],94)
        self.assertAlmostEqual(pivots[15][1]-pivots[0][1],.5)

    def test_airborne_boot_cannot_pull_root_upward(self):
        # In this fixture the head anchor is60, contact soles90, folded soles78.
        pivots=run_ground_trace([[50,60] for _ in range(16)],90,90,-3)
        self.assertEqual(pivots[3],[47,90]);self.assertLess(78,pivots[3][1])

    def test_one_raised_boot_does_not_switch_horizontal_root(self):
        centers=[]
        for right_bottom in (108,101):
            image=Image.new('RGBA',(120,120));draw=ImageDraw.Draw(image)
            draw.rectangle((20,88,38,108),fill=(90,60,65,255))
            draw.rectangle((70,88,90,right_bottom),fill=(90,60,65,255))
            centers.append(both_boot_landmark(image,[10,10,110,110])['centerX'])
        self.assertEqual(centers,[55,55])

    def test_thin_dark_blade_does_not_extend_boot_center(self):
        image=Image.new('RGBA',(120,120));draw=ImageDraw.Draw(image)
        draw.rectangle((20,92,38,112),fill=(90,60,65,255));draw.rectangle((70,92,90,112),fill=(90,60,65,255))
        baseline=both_boot_landmark(image,[10,10,110,118])['centerX']
        draw.rectangle((105,90,106,117),fill=(35,28,30,255))
        self.assertEqual(both_boot_landmark(image,[10,10,110,118])['centerX'],baseline)

    def test_warm_silver_blade_connected_to_boot_is_excluded(self):
        image=Image.new('RGBA',(140,120));draw=ImageDraw.Draw(image)
        draw.rectangle((20,92,38,112),fill=(90,60,65,255));draw.rectangle((70,92,90,112),fill=(90,60,65,255))
        baseline=both_boot_landmark(image,[10,10,135,118])['centerX']
        draw.rectangle((90,98,130,107),fill=(125,115,110,255))
        self.assertEqual(both_boot_landmark(image,[10,10,135,118])['centerX'],baseline)

    def test_raised_hilt_does_not_pull_hair_diagnostic(self):
        image=Image.new('RGBA',(160,180));draw=ImageDraw.Draw(image)
        draw.rectangle((30,12,90,60),fill=(80,60,65,255))
        baseline=hair_landmark(image,[20,10,150,170])
        draw.rectangle((125,38,140,65),fill=(90,65,60,255))
        self.assertEqual(hair_landmark(image,[20,10,150,170]),baseline)


if __name__=='__main__':unittest.main()
