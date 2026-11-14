"""Reaching feet must not shrink the head at locomotion transitions."""
import math,unittest
from calibrate_anh_dao_locomotion import head_registered_height


class LocomotionRegistration(unittest.TestCase):
    def test_same_head_has_same_scale_despite_longer_stride(self):
        self.assertEqual(head_registered_height(200,100,100),200)

    def test_different_source_resolution_preserves_display_head_size(self):
        for source_span in (70,100,150):
            height=head_registered_height(200,100,source_span)
            self.assertAlmostEqual(100/200,source_span/height)

    def test_invalid_measurements_fail_instead_of_silently_scaling(self):
        for invalid in (0,-1,math.nan,math.inf):
            with self.assertRaises(AssertionError):head_registered_height(200,100,invalid)


if __name__=='__main__':unittest.main()
