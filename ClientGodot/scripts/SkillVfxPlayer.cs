using Godot;
using System;
using System.Collections.Generic;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Presentation only: no damage, cooldown, movement or grant decisions.</summary>
public partial class SkillVfxPlayer : Node2D
{
    private sealed class Playing
    {
        public Sprite2D Sprite=null!;
        public int Skill;
        public double Time;
    }
    private readonly List<Playing> _playing=new();
    private readonly HashSet<string> _seen=new();
    private readonly Queue<string> _seenOrder=new();
    private JsonDocument _manifest=null!;
    private Texture2D _texture=null!;
    public bool LowFx {get;set;}
    public bool ReviewFreeze {get;set;}
    public int ActiveCount=>_playing.Count;
    private static readonly float[] Widths={88,110,96,54,120,140};
    private static readonly double[] Durations={.28,.20,.36,4,.16,1.05};
    public static readonly string[] Names={"Phản Quang","Tầm Long","Kiếm Trận","Thiết Y","Bạch Hồng","Vạn Tượng Quy Nhất"};
    public override void _Ready()
    {
        _manifest=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        _texture=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_vfx.png");
    }
    public bool Play(int skill,Vector2 foot,Vector2 direction,string castToken)
    {
        if(skill<0||skill>=6||_seen.Contains(castToken))return false;
        _seen.Add(castToken);_seenOrder.Enqueue(castToken);
        while(_seenOrder.Count>256)_seen.Remove(_seenOrder.Dequeue());
        while(_playing.Count>=(LowFx?8:24)){_playing[0].Sprite.QueueFree();_playing.RemoveAt(0);}
        var face=direction==Vector2.Zero?Vector2.Right:direction.Normalized();
        var offset=skill switch{0=>face*18+new Vector2(0,-18),1=>-face*28+new Vector2(0,-12),
            2=>face*24+new Vector2(0,-14),3=>new Vector2(0,-19),4=>-face*35+new Vector2(0,-8),
            _=>face*70+new Vector2(0,-16)};
        var sprite=new Sprite2D{Texture=_texture,RegionEnabled=true,Centered=false,Position=foot+offset,
            Rotation=skill==3?0:face.Angle(),Scale=Vector2.One*(Widths[skill]/209f),
            TextureFilter=TextureFilterEnum.Nearest,Modulate=new Color(1,1,1,LowFx ? .65f : 1f)};
        AddChild(sprite);_playing.Add(new Playing{Sprite=sprite,Skill=skill});Frame(_playing[^1]);return true;
    }
    public override void _Process(double delta)
    {
        for(int i=_playing.Count-1;i>=0;i--)
        {
            var p=_playing[i];
            if(ReviewFreeze){p.Time=p.Skill==3 ? .25 : p.Skill==5 ? .73 : Durations[p.Skill]*.45;Frame(p);continue;}
            p.Time+=delta;
            if(p.Time>=Durations[p.Skill]){p.Sprite.QueueFree();_playing.RemoveAt(i);continue;}
            Frame(p);
        }
    }
    private void Frame(Playing p)
    {
        int index;
        if(p.Skill==3)index=p.Time<.24?Math.Min(2,(int)(p.Time/.08)):p.Time<3.75?2:3+Math.Min(2,(int)((p.Time-3.75)/.083));
        else if(p.Skill==5)index=p.Time<.7?Math.Min(2,(int)(p.Time/.234)):3+Math.Min(2,(int)((p.Time-.7)/.117));
        else index=Math.Clamp((int)(p.Time/Durations[p.Skill]*6),0,5);
        var frame=_manifest.RootElement.GetProperty("vfx")[p.Skill][index];var r=frame.GetProperty("rect");var pivot=frame.GetProperty("pivot");
        p.Sprite.RegionRect=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle());
        p.Sprite.Offset=-new Vector2(pivot[0].GetSingle(),pivot[1].GetSingle());
    }
    public void Clear()
    {
        foreach(var p in _playing)p.Sprite.QueueFree();
        _playing.Clear();
    }
    public override void _ExitTree(){_manifest?.Dispose();}
}
