"""Flexible leaf fins/tail must not drag a fish's registered silver torso."""
import unittest
from inspect_actor_library import silver_core_pivot


class FishRegistration(unittest.TestCase):
    def pixels(self):
        result=[(0,0,0,0)]*64
        for y in (2,3,4):
            for x in (2,3,4):result[y*8+x]=(180,190,225,255)
        return result

    def test_green_tail_motion_does_not_move_torso(self):
        one=self.pixels();two=self.pixels()
        for x in range(8):one[7*8+x]=(60,150,160,255);two[x]=(60,150,160,255)
        self.assertEqual(silver_core_pivot(one,8),[3,3])
        self.assertEqual(silver_core_pivot(one,8),silver_core_pivot(two,8))

    def test_transparent_light_noise_does_not_move_torso(self):
        pixels=self.pixels();pixels[0]=(255,255,255,1)
        self.assertEqual(silver_core_pivot(pixels,8),[3,3])

    def test_no_silver_core_requires_manual_registration(self):
        with self.assertRaises(AssertionError):silver_core_pivot([(60,150,160,255)]*64,8)


if __name__=='__main__':unittest.main()
