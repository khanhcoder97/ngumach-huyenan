"""Generation requests must respect creature anatomy rather than human fall poses."""
import unittest
from build_actor_library_plan import ACTION,creature_action


class CreaturePrompt(unittest.TestCase):
    def test_root_defeat_is_a_heap_not_a_kneeling_human(self):
        description=creature_action(dict(kind='MOB',id='MOB_WATERROOT'),'death',ACTION['death'])
        self.assertIn('wood-and-moss heap',description)
        self.assertNotIn('knees',description)
        self.assertNotIn('hand down',description)

    def test_serpent_fall_and_locomotion_do_not_invent_human_support(self):
        actor=dict(kind='BOSS',id='BOSS_MANG_COT')
        self.assertNotIn('knees',creature_action(actor,'death',ACTION['death']))
        self.assertIn('slither',creature_action(actor,'walk',ACTION['walk']))

    def test_human_template_is_preserved_for_characters(self):
        self.assertEqual(creature_action(dict(kind='CLASS',id='CLASS_MINH_KIEM'),'death',ACTION['death']),ACTION['death'])


if __name__=='__main__':unittest.main()
