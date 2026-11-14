"""The source queue must cover the canonical three-hit combo, run and interaction."""
import unittest
from build_actor_library_plan import build,class_basic_action


class ClassActionScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.catalog,cls.jobs=build()

    def test_every_class_has_all_three_hit_jobs_and_movement_interaction(self):
        classes=[a for a in self.catalog['actors'] if a['kind']=='CLASS'];self.assertEqual(len(classes),5)
        for actor in classes:
            self.assertTrue({'run','interact','basic_attack','basic_attack_02','basic_attack_03'}<=set(actor['requiredClips']))
            own={j['clip']:j for j in self.jobs if j['ownerId']==actor['id']}
            for stage,clip in enumerate(('basic_attack','basic_attack_02','basic_attack_03'),1):
                self.assertEqual(own[clip]['comboStage'],stage)
                self.assertEqual(own[clip]['framesPerDirection'],16)
                self.assertIn('exactly ONE hit motion',own[clip]['prompt'])

    def test_hammer_first_hit_matches_horizontal_canon(self):
        self.assertIn('horizontal',class_basic_action('CLASS_THACH_CHUY',1))
        self.assertIn('low',class_basic_action('CLASS_THACH_CHUY',2))
        self.assertIn('vertical overhead',class_basic_action('CLASS_THACH_CHUY',3))

    def test_no_phantom_combo_variants_on_creatures_or_npcs(self):
        for job in self.jobs:
            if job['kind']!='CLASS':self.assertNotIn('comboStage',job)


if __name__=='__main__':unittest.main()
