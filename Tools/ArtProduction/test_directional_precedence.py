"""Coverage must follow the same replacement/approval precedence as the client."""
import unittest
from inspect_actor_library import covers


def page(name,directions,approved=True):
    return dict(id=name,productionApproved=approved,directions=[dict(direction=d,flip=False) for d in directions])


class DirectionalCoverageTests(unittest.TestCase):
    def setUp(self):
        self.job=dict(id='class_minh_kiem_walk',directions=['N','NE','E','SE','S'])
        self.legacy=page(self.job['id'],self.job['directions'])

    def test_unreviewed_replacement_shadows_approved_legacy(self):
        replacement=page(self.job['id']+'_e',['E'],False)
        self.assertTrue(covers(self.job,[self.legacy,replacement]))
        self.assertFalse(covers(self.job,[self.legacy,replacement],True))

    def test_order_does_not_restore_shadowed_legacy(self):
        replacement=page(self.job['id']+'_e',['E'],False)
        self.assertFalse(covers(self.job,[replacement,self.legacy],True))

    def test_approved_replacement_and_remaining_legacy_cover(self):
        self.assertTrue(covers(self.job,[self.legacy,page(self.job['id']+'_e',['E'])],True))

    def test_partial_directions_do_not_complete_action(self):
        self.assertFalse(covers(self.job,[page(self.job['id']+'_e',['E'])],True))

    def test_mirror_is_not_an_authored_direction(self):
        p=page(self.job['id'],self.job['directions'][:-1])
        p['directions'].append(dict(direction='S',flip=True))
        self.assertFalse(covers(self.job,[p]))

    def test_omni_effect_and_unrelated_ids(self):
        effect=dict(id='sk_test_vfx',directions=['OMNI_OR_ROTATED'])
        self.assertTrue(covers(effect,[page(effect['id'],['OMNI'])],True))
        self.assertFalse(covers(effect,[page(effect['id']+'_unrelated',['OMNI'])],True))


if __name__=='__main__':unittest.main()
