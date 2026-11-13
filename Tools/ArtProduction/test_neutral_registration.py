"""Low-start clips retain their authored compression rather than growing on switch."""
import unittest
from inspect_actor_library import registered_height


class NeutralRegistration(unittest.TestCase):
    frames=[dict(bounds=[0,0,120,90])]*3+[dict(bounds=[0,0,100,150])]*13

    def test_crouched_start_keeps_neutral_scale(self):
        height=registered_height({'bodyReferenceHeight':150},self.frames,256)
        self.assertEqual(height,150)
        self.assertEqual(90/height,.6)
        self.assertEqual(registered_height({},self.frames,256),90)

    def test_old_moss_value_is_preserved(self):
        self.assertEqual(registered_height({'pivotMode':'MOSS_CORE_ROOT','bodyReferenceHeight':180.5},self.frames,256),180.5)
        with self.assertRaises(AssertionError):registered_height({'pivotMode':'MOSS_CORE_ROOT'},self.frames,256)
        with self.assertRaises(AssertionError):registered_height({'pivotMode':'BOOT_CORE_FOOT'},self.frames,256)

    def test_invalid_override_fails(self):
        for value in (True,None,'150',0,15,257,float('nan'),float('inf')):
            with self.subTest(value=value),self.assertRaises(AssertionError):
                registered_height({'bodyReferenceHeight':value},self.frames,256)
        with self.assertRaises(AssertionError):registered_height({'bodyReferenceHeight':150},self.frames,256,True)
        with self.assertRaises(AssertionError):registered_height({'bodyReferenceHeight':150,'scaleMode':'LONGEST_AXIS'},self.frames,256)

    def test_narrow_vfx_uses_largest_span_only_when_opted_in(self):
        frames=[dict(bounds=[4,8,244,26])]*15+[dict(bounds=[4,8,324,22])]
        self.assertEqual(registered_height({'scaleMode':'LONGEST_AXIS'},frames,256,True),320)
        self.assertEqual(registered_height({},frames,256,True),18)

    def test_tall_vfx_keeps_vertical_span_in_longest_mode(self):
        self.assertEqual(registered_height({'scaleMode':'LONGEST_AXIS'},self.frames,256,True),150)


if __name__=='__main__':unittest.main()
