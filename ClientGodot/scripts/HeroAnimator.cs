using Godot;
using System;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Only full-body frames. The foot pivot, not image bounds, anchors the actor.</summary>
public partial class HeroAnimator : Sprite2D
{
    private JsonDocument _clips=null!,_idle=null!;
    private Texture2D _idleTexture=null!,_walkTexture=null!,_attackTexture=null!;
    private int _direction=4;
    private bool _moving,_attacking;
    private double _clock,_attackClock;
    public int DisplayedFrame {get;private set;}
    public bool IsAttacking=>_attacking;
    public override void _Ready()
    {
        RegionEnabled=true;Centered=false;TextureFilter=TextureFilterEnum.Nearest;
        _clips=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        _idle=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/reboot/manifest.json"));
        _idleTexture=GD.Load<Texture2D>("res://assets/reboot/hero_idle_body.png");
        _walkTexture=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_walk.png");
        _attackTexture=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_attack.png");
        RenderFrame();
    }
    public void SetFacing(int direction)=>_direction=((direction%8)+8)%8;
    public void SetMoving(bool moving)=>_moving=moving;
    public void Attack(){_attacking=true;_attackClock=0;}
    public override void _Process(double delta)
    {
        _clock+=delta;
        if(_attacking){_attackClock+=delta;if(_attackClock>=.48)_attacking=false;}
        RenderFrame();
    }
    private void RenderFrame()
    {
        if(_clips==null)return;
        JsonElement frame;float scale;
        if(_attacking)
        {
            DisplayedFrame=Math.Min(3,(int)(_attackClock/.12));
            frame=_clips.RootElement.GetProperty("attack")[DisplayedFrame*8+_direction];
            Texture=_attackTexture;scale=36f/112f;
        }
        else if(_moving)
        {
            DisplayedFrame=(int)(_clock*8)%4;
            frame=_clips.RootElement.GetProperty("walk")[DisplayedFrame*8+_direction];
            Texture=_walkTexture;scale=36f/208f;
        }
        else
        {
            DisplayedFrame=0;
            frame=_idle.RootElement.GetProperty("heroFrames")[_direction];
            Texture=_idleTexture;scale=36f/372f;
        }
        var r=frame.GetProperty("rect");var p=frame.GetProperty("pivot");
        RegionRect=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle());
        Offset=-new Vector2(p[0].GetSingle(),p[1].GetSingle());Scale=Vector2.One*scale;
    }
    public override void _ExitTree(){_clips?.Dispose();_idle?.Dispose();}
}
