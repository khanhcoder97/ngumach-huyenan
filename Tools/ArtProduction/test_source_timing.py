"""Unequal phase timing preserves each source pose without changing combat windows."""
import unittest
from inspect_actor_library import source_timing,binding_sha256


class SourceTiming(unittest.TestCase):
    def test_tam_long_phases(self):
        values=[37.5]*4+[100/3]*6+[40]*6
        self.assertAlmostEqual(sum(values[:4]),150)
        self.assertAlmostEqual(sum(values[:10]),350)
        self.assertAlmostEqual(sum(values),590)
        self.assertEqual(source_timing({'sourceFrameDurationsMs':values}),{'sourceFrameDurationsMs':values})

    def test_missing_timing_keeps_old_binding(self):
        self.assertEqual(source_timing({}),{})
        before=binding_sha256({'directions':[]})
        self.assertNotEqual(before,binding_sha256({'directions':[],'sourceFrameDurationsMs':[20]*16}))

    def test_invalid_or_too_short_source_timings_fail(self):
        for values in (None,tuple([20]*16),[20]*15,[20]*17,[True]*16,[float('nan')]*16,[float('inf')]*16,[10]*16,[10001]*16,[4000]*16):
            with self.subTest(values=values),self.assertRaises(AssertionError):source_timing({'sourceFrameDurationsMs':values})

    def test_component_profile_must_agree(self):
        self.assertTrue(source_timing({'sourceFrameDurationsMs':[20]*16,'previewDurationSeconds':.32}))
        with self.assertRaises(AssertionError):source_timing({'sourceFrameDurationsMs':[20]*16,'previewDurationSeconds':.5})


if __name__=='__main__':unittest.main()
