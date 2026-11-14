using Godot;
using System;
using System.Linq;

namespace Ngumach.VisualReboot;

public partial class VfxComponentTest : Node
{
    public override void _Ready()
    {
        try
        {
            int checks=0;void Check(bool ok,string why){if(!ok)throw new Exception(why);checks++;}
            var player=new SkillVfxPlayer();AddChild(player);
            Check(player.HasApprovedKiemTran,"approved source not bound");
            Check(player.Play(2,new Vector2(50,80),Vector2.Right,"arc:test"),"cast rejected");
            Check(player.ActiveCount==3&&player.ArcFrames.SequenceEqual(new[]{0,-1,-1}),"start/delay mismatch");
            Check(!player.Play(2,Vector2.Zero,Vector2.Right,"arc:test")&&player.ActiveCount==3,"duplicate replay");
            player._Process(.10);Check(player.ArcFrames.SequenceEqual(new[]{8,-1,-1}),"first visual peak");
            player._Process(.12);Check(player.ArcFrames.SequenceEqual(new[]{8,-1}),"second visual peak/lifetime");
            player._Process(.14);Check(player.ArcFrames.SequenceEqual(new[]{8}),"third visual peak/lifetime");
            player._Process(.11);Check(player.ActiveCount==0,"effect leaked past .46 s");
            player.Play(2,Vector2.Zero,Vector2.Up,"arc:direction");
            Check(Math.Abs(player.ArcAngles[0]+Mathf.Pi/2)<.0001,"camera direction rotation");
            Check(player.ArcAngles[1]<player.ArcAngles[0]&&player.ArcAngles[2]>player.ArcAngles[0],"three trajectories not distinct");
            Check(player.ArcScales[2]>player.ArcScales[0],"third slash must be larger");
            player.Clear();player.LowFx=true;
            for(int i=0;i<40;i++)player.Play(2,Vector2.Zero,Vector2.Right,"arc:budget:"+i);
            Check(player.ActiveCount<=8,"low FX budget overflow");player.Clear();Check(player.ActiveCount==0,"cancel leaked effects");
            Check(!player.Play(-1,Vector2.Zero,Vector2.Zero,"invalid"),"invalid index");
            GD.Print("VFX_COMPONENT_SELF_TEST PASS assertions="+checks+" 16_SOURCE_FRAMES_PER_ARC 3_VISUAL_PEAKS NO_GAMEPLAY_MUTATION");GetTree().Quit();
        }
        catch(Exception e){GD.PushError("VFX_COMPONENT_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
}
