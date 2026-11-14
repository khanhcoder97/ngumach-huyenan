"""Native histogram counts must preserve the prior pixel-loop grid exactly."""
import unittest
from PIL import Image
from inspect_actor_library import binary_projection


class BinaryProjection(unittest.TestCase):
    def compare(self,alpha):
        mask=alpha.point(lambda value:255 if value>=200 else 0)
        w,h=mask.size;xs=[0]*w;ys=[0]*h
        for y in range(h):
            for x in range(w):
                if mask.getpixel((x,y)):xs[x]+=1;ys[y]+=1
        self.assertEqual(binary_projection(mask),(xs,ys))

    def test_empty_full_and_single_axis_masks(self):
        for size in ((1,1),(1,21),(19,1),(37,23)):
            for value in (0,255):
                with self.subTest(size=size,value=value):self.compare(Image.new('L',size,value))

    def test_sparse_alpha_threshold_and_irregular_gutters(self):
        alpha=Image.new('L',(67,41));values=(0,1,128,199,200,254,255)
        alpha.putdata([values[(x*17+y*31)%len(values)] if x%13<9 and y%11<7 else 0
                       for y in range(41) for x in range(67)])
        self.compare(alpha)


if __name__=='__main__':unittest.main()
