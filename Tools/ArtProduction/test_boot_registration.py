"""A downward sword tip must not become the character's floor anchor."""
import unittest
from inspect_actor_library import boot_foot_pivot


class BootRegistration(unittest.TestCase):
    def pixels(self):
        result=[(0,0,0,0)]*400
        for y in range(13,17):
            for x in (*range(4,8),*range(12,16)):result[y*20+x]=(80,60,40,255)
        return result

    def test_steel_tip_and_gold_hilt_do_not_drag_boots(self):
        one=self.pixels();two=self.pixels()
        for y in range(12,20):two[y*20+10]=(180,190,205,255)
        for x in range(7,12):two[19*20+x]=(220,175,60,255)
        self.assertEqual(boot_foot_pivot(one,20,20),boot_foot_pivot(two,20,20))
        self.assertEqual(boot_foot_pivot(one,20,20),[9.5,18])

    def test_small_brown_islands_and_transparent_noise_are_ignored(self):
        pixels=self.pixels();pixels[19*20]=(80,60,40,255);pixels[19*20+19]=(80,60,40,2)
        self.assertEqual(boot_foot_pivot(pixels,20,20),[9.5,18])

    def test_missing_boots_requires_review(self):
        with self.assertRaises(AssertionError):boot_foot_pivot([(180,190,205,255)]*400,20,20)


if __name__=='__main__':unittest.main()
