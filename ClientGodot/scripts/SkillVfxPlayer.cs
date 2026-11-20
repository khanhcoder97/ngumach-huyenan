using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
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
        public bool KiemTranArc;
        public int SourceFrame=-1;
    }
    private readonly List<Playing> _playing=new();
    private readonly List<(Node2D Node,Tween Tween)> _transient=new();
    public int FeedbackCount=>_transient.Count;
    private readonly HashSet<string> _seen=new();
    private readonly Queue<string> _seenOrder=new();
    private JsonDocument _manifest=null!;
    private Texture2D _texture=null!;
    private ActorLibraryData.Direction? _kiemTranArc;
    private Texture2D? _kiemTranTexture;
    public bool LowFx {get;set;}
    public bool ReviewFreeze {get;set;}
    public int ActiveCount=>_playing.Count;
    public bool HasApprovedKiemTran=>_kiemTranArc!=null&&_kiemTranTexture!=null;
    internal int[] ArcFrames=>_playing.Where(p=>p.KiemTranArc).Select(p=>p.SourceFrame).ToArray();
    internal float[] ArcAngles=>_playing.Where(p=>p.KiemTranArc).Select(p=>p.Sprite.Rotation).ToArray();
    internal float[] ArcScales=>_playing.Where(p=>p.KiemTranArc).Select(p=>p.Sprite.Scale.X).ToArray();
    private static readonly float[] Widths={88,110,96,54,120,140};
    private static readonly double[] Durations={.28,.20,.36,4,.16,1.05};
    public static readonly string[] Names={"Phản Quang","Tầm Long","Kiếm Trận","Thiết Y","Bạch Hồng","Vạn Tượng Quy Nhất"};
    public override void _Ready()
    {
        _manifest=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        _texture=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_vfx.png");
        using var library=new ActorLibraryData();
        if(library.Pages.TryGetValue("sk_mk_03_arc_component",out var page)&&page.Approved&&page.Directions.Length==1&&page.Directions[0].Frames.Length==16)
        {
            string source=page.Directions[0].Frames[0].File;
            if(FileAccess.FileExists(source)&&Convert.ToHexString(SHA256.HashData(FileAccess.GetFileAsBytes(source))).ToLowerInvariant()==page.SourceSha256)
            {_kiemTranArc=page.Directions[0];_kiemTranTexture=GD.Load<Texture2D>(source);}
        }
    }
    public bool Play(int skill,Vector2 foot,Vector2 direction,string castToken)
    {
        if(skill<0||skill>=6||_seen.Contains(castToken))return false;
        _seen.Add(castToken);_seenOrder.Enqueue(castToken);
        while(_seenOrder.Count>256)_seen.Remove(_seenOrder.Dequeue());
        while(_playing.Count>=(LowFx?8:24)){_playing[0].Sprite.QueueFree();_playing.RemoveAt(0);}
        var face=direction==Vector2.Zero?Vector2.Right:direction.Normalized();
        if(skill==2&&HasApprovedKiemTran){PlayKiemTran(foot,face);return true;}
        var offset=skill switch{0=>face*18+new Vector2(0,-18),1=>-face*28+new Vector2(0,-12),
            2=>face*24+new Vector2(0,-14),3=>new Vector2(0,-19),4=>-face*35+new Vector2(0,-8),
            _=>face*70+new Vector2(0,-16)};
        var sprite=new Sprite2D{Texture=_texture,RegionEnabled=true,Centered=false,Position=foot+offset,
            Rotation=skill==3?0:face.Angle(),Scale=Vector2.One*(Widths[skill]/209f),
            TextureFilter=TextureFilterEnum.Nearest,Modulate=new Color(1,1,1,LowFx ? .65f : 1f)};
        AddChild(sprite);_playing.Add(new Playing{Sprite=sprite,Skill=skill});Frame(_playing[^1]);return true;
    }
    private void PlayKiemTran(Vector2 foot,Vector2 face)
    {
        double[] starts={0,.12,.26};float[] angles={0,-35,35};
        // Visual peaks at .10/.22/.36s. Each source arc lives .20s; damage remains server-owned.
        for(int i=0;i<3;i++)
        {
            while(_playing.Count>=(LowFx?8:24)){_playing[0].Sprite.QueueFree();_playing.RemoveAt(0);}
            var sprite=new Sprite2D{Texture=_kiemTranTexture,RegionEnabled=true,Centered=false,Position=foot+face*24+new Vector2(0,-14),
                Rotation=face.Angle()+Mathf.DegToRad(angles[i]),Scale=Vector2.One*(96/Math.Max(1,_kiemTranArc!.Height))*(i==2?1.25f:1),
                TextureFilter=TextureFilterEnum.Nearest,Modulate=new Color(1,1,1,LowFx ? .65f : 1f)};
            AddChild(sprite);var p=new Playing{Sprite=sprite,Skill=2,Time=-starts[i],KiemTranArc=true};_playing.Add(p);Frame(p);
        }
    }
    public void GuardCue(Vector2 foot,string castToken)
    {
        if(!_seen.Add("guard:"+castToken))return;
        _seenOrder.Enqueue("guard:"+castToken);while(_seenOrder.Count>256)_seen.Remove(_seenOrder.Dequeue());
        var sprite=new Sprite2D{Texture=MoonGlassIcons.Get("Guild"),Position=foot+new Vector2(0,-25),Scale=Vector2.One*.65f,Modulate=MoonGlassTheme.Blue};
        AddChild(sprite);var tween=CreateTween();TrackTransient(sprite,tween);tween.SetParallel();
        tween.TweenProperty(sprite,"position:y",sprite.Position.Y-8,.4);tween.TweenProperty(sprite,"modulate:a",0,.4);
        tween.Chain().TweenCallback(Callable.From(()=>ReleaseTransient(sprite)));
    }
    private void TrackTransient(Node2D node,Tween tween)
    {
        while(_transient.Count>=(LowFx?8:24)){var oldest=_transient[0];oldest.Tween.Kill();oldest.Node.QueueFree();_transient.RemoveAt(0);}
        _transient.Add((node,tween));
    }
    private void ReleaseTransient(Node2D node)
    {_transient.RemoveAll(x=>x.Node==node);if(GodotObject.IsInstanceValid(node))node.QueueFree();}
    public void Impact(NguMach.Client.P1.P1ImpactResultV2 result,Vector2 foot)
    {
        var root=new Node2D{Position=foot};AddChild(root);
        string text=result.immune?"Miễn nhiễm":!result.hit?"Trượt":result.hpDamage>0?(result.crit?"Chí mạng ":"")+result.hpDamage:
            result.absorbed>0?"Hấp thụ "+result.absorbed:"0";
        var label=new Label{Text=text,Position=new Vector2(-85,-55),Size=new Vector2(170,24),HorizontalAlignment=HorizontalAlignment.Center,MouseFilter=Control.MouseFilterEnum.Ignore};
        label.AddThemeFontSizeOverride("font_size",result.crit?19:16);
        label.AddThemeColorOverride("font_color",result.crit?MoonGlassTheme.Gold:result.immune?MoonGlassTheme.Blue:result.hit?MoonGlassTheme.Ink:MoonGlassTheme.Muted);
        label.AddThemeColorOverride("font_outline_color",new Color(.04f,.05f,.12f,.95f));label.AddThemeConstantOverride("outline_size",3);root.AddChild(label);
        if(result.hit&&!result.immune&&result.hpDamage>0&&!LowFx)
        {
            var points=new Vector2[25];for(int i=0;i<points.Length;i++)points[i]=Vector2.FromAngle(i*Mathf.Tau/24)*14;
            root.AddChild(new Line2D{Points=points,Width=1.5f,DefaultColor=result.crit?MoonGlassTheme.Gold:MoonGlassTheme.Hp});
        }
        var tween=CreateTween();TrackTransient(root,tween);tween.SetParallel();tween.TweenProperty(label,"position:y",-80,.65);
        tween.TweenProperty(root,"modulate:a",0,.65);tween.Chain().TweenCallback(Callable.From(()=>ReleaseTransient(root)));
    }
    public override void _Process(double delta)
    {
        for(int i=_playing.Count-1;i>=0;i--)
        {
            var p=_playing[i];
            if(ReviewFreeze){p.Time=p.KiemTranArc ? .10 : p.Skill==3 ? .25 : p.Skill==5 ? .73 : Durations[p.Skill]*.45;Frame(p);continue;}
            p.Time+=delta;
            if(p.Time>=(p.KiemTranArc ? .20 : Durations[p.Skill])){p.Sprite.QueueFree();_playing.RemoveAt(i);continue;}
            Frame(p);
        }
    }
    private void Frame(Playing p)
    {
        if(p.KiemTranArc)
        {
            p.Sprite.Visible=p.Time>=0;
            if(!p.Sprite.Visible){p.SourceFrame=-1;return;}
            p.SourceFrame=Math.Clamp((int)(p.Time/.20*16+1e-7),0,15);var f=_kiemTranArc!.Frames[p.SourceFrame];
            p.Sprite.RegionRect=f.Region;p.Sprite.Offset=-f.Pivot;return;
        }
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
        foreach(var item in _transient){item.Tween.Kill();if(GodotObject.IsInstanceValid(item.Node))item.Node.QueueFree();}
        _transient.Clear();
    }
    public override void _ExitTree(){_manifest?.Dispose();}
}
