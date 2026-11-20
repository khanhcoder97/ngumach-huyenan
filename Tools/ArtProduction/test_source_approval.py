"""An old review cannot approve changed artwork or altered sprite registration."""
import copy
import unittest
from inspect_actor_library import binding_sha256,source_approval_matches


class SourceApproval(unittest.TestCase):
    def setUp(self):
        self.page=dict(sha256='original',referenceHeight=100,pivotMode='FOOT',directions=[dict(direction='N',flip=False,frames=[dict(rect=[0,0,20,40],pivot=[10,38])])])
        self.approval=dict(sourceSha256='original',bindingSha256=binding_sha256(self.page))

    def test_review_matches_unchanged_art_and_registration(self):
        self.assertTrue(source_approval_matches(self.page,self.approval))

    def test_new_art_does_not_inherit_review(self):
        self.page['sha256']='replacement'
        self.assertFalse(source_approval_matches(self.page,self.approval))

    def test_same_png_new_pivot_requires_review(self):
        changed=copy.deepcopy(self.page);changed['directions'][0]['frames'][0]['pivot'][0]+=1
        self.assertFalse(source_approval_matches(changed,self.approval))

    def test_same_png_new_scale_requires_review(self):
        self.page['referenceHeight']=120
        self.assertFalse(source_approval_matches(self.page,self.approval))

    def test_direction_relabel_requires_review(self):
        self.page['directions'][0]['direction']='S'
        self.assertFalse(source_approval_matches(self.page,self.approval))

    def test_missing_registration_pin_is_not_approval(self):
        self.approval.pop('bindingSha256')
        self.assertFalse(source_approval_matches(self.page,self.approval))


if __name__=='__main__':unittest.main()
