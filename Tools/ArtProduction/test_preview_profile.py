"""Presentation profiles cannot skip source poses or inherit stale visual approval."""
import unittest
from inspect_actor_library import preview_profile,binding_sha256


class PreviewProfile(unittest.TestCase):
    def setUp(self):
        self.record=dict(id='sk_test_component',componentOnly=True,previewDurationSeconds=.32,previewLoop=False)

    def test_optional_profile_preserves_old_binding_pin(self):
        self.assertEqual(preview_profile(dict(id='mob_test_idle')), {})
        page=dict(directions=[],referenceHeight=100)
        before=binding_sha256(page)
        page['previewDurationSeconds']=.32;page['previewLoop']=False
        self.assertNotEqual(before,binding_sha256(page))
        pinned=binding_sha256(page);page['previewLoop']=True
        self.assertNotEqual(pinned,binding_sha256(page))

    def test_only_components_can_declare_preview_timing(self):
        self.assertEqual(preview_profile(self.record),dict(previewDurationSeconds=.32,previewLoop=False))
        self.record['componentOnly']=False
        with self.assertRaises(AssertionError):preview_profile(self.record)

    def test_invalid_duration_and_untyped_loop_rejected(self):
        for duration in (0,.2,float('nan'),float('inf'),True,61):
            with self.subTest(duration=duration),self.assertRaises(AssertionError):
                preview_profile(dict(self.record,previewDurationSeconds=duration))
        for loop in (0,'false',None):
            with self.subTest(loop=loop),self.assertRaises(AssertionError):
                preview_profile(dict(self.record,previewLoop=loop))

    def test_incomplete_profile_rejected(self):
        self.record.pop('previewLoop')
        with self.assertRaises(AssertionError):preview_profile(self.record)


if __name__=='__main__':unittest.main()
