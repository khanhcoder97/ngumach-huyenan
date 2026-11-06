"""Regression: a documentation update cannot restore six-frame production art."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coverage_audit import ART_STANDARD, parse_art_standard

ROOT = Path(__file__).resolve().parents[3]


class CurrentArtPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = parse_art_standard((ROOT / ART_STANDARD).read_text(encoding="utf-8-sig"))

    def parse_changed(self, **changes):
        policy = copy.deepcopy(self.policy)
        policy.update(changes)
        return parse_art_standard("<!-- actor-animation-policy -->\n```json\n" + json.dumps(policy) + "\n```")

    def test_current_document_separates_pose_cadence_from_render_fps(self):
        self.assertEqual((16, 20), (self.policy["framesPerDirectionMin"], self.policy["framesPerDirectionMax"]))
        self.assertEqual(16, self.policy["walkFrames"])
        self.assertEqual(20, self.policy["walkFps"])
        self.assertEqual(60, self.policy["renderTargetFps"])
        self.assertTrue(self.policy["cellIsNominalLegacyGrid"])

    def test_twenty_authored_frames_remain_valid(self):
        policy = self.parse_changed(walkFrames=20)
        self.assertEqual(25, policy["walkFps"])
        self.assertEqual(60, policy["renderTargetFps"])

    def test_old_six_frame_policy_cannot_pass(self):
        with self.assertRaises(ValueError):
            self.parse_changed(walkFrames=6)

    def test_missing_policy_does_not_fall_back_to_old_prose(self):
        with self.assertRaises(ValueError):
            parse_art_standard("Walk: 6 frame/hướng ở 8 fps")

    def test_invalid_timeline_and_boolean_count_are_rejected(self):
        for changes in [{"walkDurationSeconds": 0}, {"walkDurationSeconds": True}, {"walkFrames": True}, {"renderTargetFps": 16}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.parse_changed(**changes)

    def test_direction_order_cannot_drift(self):
        with self.assertRaises(ValueError):
            self.parse_changed(directions=["S", "N"])


if __name__ == "__main__":
    unittest.main()
