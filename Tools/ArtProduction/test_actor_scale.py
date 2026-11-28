"""A top-down quadruped must not grow when its long axis turns horizontally."""
import unittest
from inspect_actor_library import reference_height


class ActorScale(unittest.TestCase):
    def test_quarter_turn_preserves_long_axis_scale(self):
        north = [dict(bounds=[10, 20, 90, 200])] * 3
        east = [dict(bounds=[20, 10, 200, 90])] * 3
        self.assertEqual(reference_height(north, 'LONGEST_AXIS'), reference_height(east, 'LONGEST_AXIS'))
        self.assertNotEqual(reference_height(north), reference_height(east))

    def test_end_pose_does_not_recalibrate_whole_action(self):
        standing = [dict(bounds=[0, 0, 80, 180])] * 3
        collapsed = [dict(bounds=[0, 0, 130, 60])] * 13
        self.assertEqual(reference_height(standing + collapsed, 'LONGEST_AXIS'), 180)

    def test_unknown_scale_policy_rejected(self):
        with self.assertRaises(AssertionError):
            reference_height([dict(bounds=[0, 0, 80, 180])], 'STRETCH_TO_FIT')


if __name__ == '__main__':
    unittest.main()
