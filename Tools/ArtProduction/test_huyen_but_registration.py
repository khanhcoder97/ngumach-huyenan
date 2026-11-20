"""Synthetic geometry fixtures only; never paints game assets."""
import unittest
from PIL import Image,ImageDraw
from calibrate_huyen_but_20261114f import belt_root_x,gutter_edges,cool_boot_x,component_registration

class Registration(unittest.TestCase):
    def test_belt_outweighs_a_moving_thin_brush(self):
        im=Image.new('RGBA',(100,160));head=dict(centerX=50,span=60,top=0)
        for y in range(85,110):im.putpixel((35,y),(90,50,25,255))
        for y in range(94,98):
            for x in range(40,65):im.putpixel((x,y),(100,60,35,255))
        self.assertEqual(belt_root_x(im,head,160),52)
    def test_a_brush_alone_is_not_a_pelvis_anchor(self):
        im=Image.new('RGBA',(100,160));head=dict(centerX=50,span=60,top=0)
        for y in range(80,125):im.putpixel((45,y),(90,50,25,255))
        self.assertIsNone(belt_root_x(im,head,160))
    def test_gutters_cannot_cut_an_occupied_source(self):
        values=[1]*400
        with self.assertRaisesRegex(AssertionError,'no intact common gutter'):gutter_edges(values)
        for centre in (110,205,290):values[centre-5:centre+5]=[0]*10
        self.assertEqual(gutter_edges(values),[0,110,205,290,400])
    def test_stationary_boot_anchor_ignores_a_crossing_brown_brush(self):
        im=Image.new('RGBA',(100,160));head=dict(centerX=50,span=60,top=0)
        for y in range(140,150):
            for x in range(40,61):im.putpixel((x,y),(30,30,35,255))
            for x in range(25,35):im.putpixel((x,y),(80,45,20,255))
        self.assertEqual(cool_boot_x(im,head,150),50)
    def test_forming_rim_keeps_its_centre_despite_unequal_cell_padding(self):
        im=Image.new('RGBA',(400,400));draw=ImageDraw.Draw(im);frames=[];expected=[]
        for i in range(16):
            col,row=i%4,i//4;cx,cy=50+col*4,45-row*2;x,y=col*100,row*100
            box=(x+cx-20,y+cy-20,x+cx+20,y+cy+20)
            if i>=12:draw.ellipse(box,outline=(80,200,220,255),width=1)
            else:draw.arc(box,start=45-i*9,end=135+i*9,fill=(80,200,220,255),width=1)
            frames.append(dict(rect=[x,y,100,100],bounds=list(im.crop((x,y,x+100,y+100)).getbbox())))
            expected.append([cx+.5,cy+.5])
        mode,pivots,method=component_registration('sk_hb_03_gain_component',frames,im)
        self.assertEqual(mode,'SOURCE_PIVOTS')
        for actual,want in zip(pivots,expected):
            self.assertAlmostEqual(actual[0],want[0],delta=1);self.assertAlmostEqual(actual[1],want[1],delta=1)
    def test_dissolving_rim_does_not_average_away_unequal_row_origins(self):
        im=Image.new('RGBA',(400,400));draw=ImageDraw.Draw(im);frames=[];expected=[]
        for i in range(16):
            col,row=i%4,i//4;cx,cy=50,(40,60,42,44)[row];x,y=col*100,row*100
            draw.ellipse((x+cx-20,y+cy-20,x+cx+20,y+cy+20),outline=(80,200,220,255),width=1)
            frames.append(dict(rect=[x,y,100,100],bounds=list(im.crop((x,y,x+100,y+100)).getbbox())))
            expected.append([cx+.5,cy+.5])
        mode,pivots,method=component_registration('sk_hb_03_break_component',frames,im)
        for actual,want in zip(pivots[:12],expected[:12]):self.assertEqual(actual,want)

if __name__=='__main__':unittest.main()
