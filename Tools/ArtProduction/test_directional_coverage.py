"""Coverage must follow actual authored directions, never file count or mirrored placeholders."""
import unittest
from inspect_actor_library import covers


def page(id, directions, approved=False, flipped=()):
    return dict(id=id, productionApproved=approved,
                directions=[dict(direction=d, flip=d in flipped) for d in directions])


class DirectionalCoverage(unittest.TestCase):
    def setUp(self):
        self.job = dict(id='class_minh_kiem_dodge', directions=['N', 'NE', 'E', 'SE', 'S'])

    def test_partial_four_angles_is_not_complete(self):
        self.assertFalse(covers(self.job, [page(self.job['id'], ['N', 'NE', 'E', 'SE'])]))

    def test_original_plus_south_repair_completes_structure(self):
        self.assertTrue(covers(self.job, [page(self.job['id'], ['N', 'NE', 'E', 'SE']), page(self.job['id']+'_s', ['S'])]))

    def test_unapproved_repair_does_not_complete_production(self):
        self.assertFalse(covers(self.job, [page(self.job['id'], ['N', 'NE', 'E', 'SE'], True), page(self.job['id']+'_s', ['S'])], True))

    def test_mirror_is_not_authored_angle(self):
        job = dict(id='npc_asymmetric_idle_nw', directions=['NW'])
        self.assertFalse(covers(job, [page(job['id'], ['NW'], True, ['NW'])]))

    def test_component_is_not_full_skill(self):
        job = dict(id='sk_mk_03_vfx', directions=['OMNI_OR_ROTATED'])
        self.assertFalse(covers(job, [page('sk_mk_03_arc_component', ['OMNI'], True)]))

    def test_omni_effect_can_complete_its_own_job(self):
        job = dict(id='sk_mk_03_vfx', directions=['OMNI_OR_ROTATED'])
        self.assertTrue(covers(job, [page(job['id'], ['OMNI'], True)], True))

    def test_foreign_repair_does_not_fill_missing_direction(self):
        self.assertFalse(covers(self.job, [page(self.job['id'], ['N', 'NE', 'E', 'SE']), page('class_anh_dao_dodge_s', ['S'])]))

    def test_all_five_source_angles_complete(self):
        self.assertTrue(covers(self.job, [page(self.job['id'], self.job['directions'])]))


if __name__ == '__main__':
    unittest.main()
