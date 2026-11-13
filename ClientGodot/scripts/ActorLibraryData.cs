using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Visual catalogue only. Never provides stats, damage or progression.</summary>
public sealed class ActorLibraryData : IDisposable
{
    public const string Root="res://assets/actor_library_v1/";
    public sealed record Actor(string Id,string Name,string Kind,float Height,bool Mirror,string[] Clips);
    public sealed record Frame(string File,Rect2 Region,Vector2 Pivot);
    public sealed record Direction(string Name,bool Flip,float Height,Frame[] Frames,double[]? SourceFrameDurationsMs=null);
    public sealed record Page(string Id,string Status,Direction[] Directions,bool Approved,string VisualState,string Notes,string SourceSha256);
    public readonly Dictionary<string,Actor> Actors=new(StringComparer.Ordinal);
    public readonly Dictionary<string,Page> Pages=new(StringComparer.Ordinal);
    private readonly Dictionary<string,Texture2D> _textures=new(StringComparer.Ordinal);
    private readonly Queue<string> _order=new();
    public int CachedTextures=>_textures.Count;
    private readonly bool _reviewMode;
    public ActorLibraryData(bool reviewMode=false)
    {
        _reviewMode=reviewMode;
        using var catalog=JsonDocument.Parse(FileAccess.GetFileAsString(Root+"catalog.json"));
        foreach(var a in catalog.RootElement.GetProperty("actors").EnumerateArray())
        {
            var actor=new Actor(a.GetProperty("id").GetString()!,a.GetProperty("name").GetString()!,a.GetProperty("kind").GetString()!,
                a.GetProperty("renderHeightPx").GetSingle(),a.GetProperty("mirrorAllowed").GetBoolean(),a.GetProperty("requiredClips").EnumerateArray().Select(x=>x.GetString()!).ToArray());
            Actors.Add(actor.Id,actor);
        }
        foreach(var skill in catalog.RootElement.GetProperty("skills").EnumerateArray())
        {var id=skill.GetProperty("id").GetString()!;Actors.Add(id,new Actor(id,skill.GetProperty("name").GetString()!,"VFX",100,true,new[]{"full_timeline"}));}
        using var pages=JsonDocument.Parse(FileAccess.GetFileAsString(Root+"pages.json"));
        foreach(var p in pages.RootElement.GetProperty("pages").EnumerateArray())
        {
            string common=p.GetProperty("file").GetString()!;float height=p.GetProperty("referenceHeight").GetSingle();
            double[]? timing=p.TryGetProperty("sourceFrameDurationsMs",out var timingJson)?timingJson.EnumerateArray().Select(v=>v.GetDouble()).ToArray():null;
            if(timing!=null&&(timing.Length!=16||timing.Any(v=>!double.IsFinite(v)||v<1000d/60||v>10000)||timing.Sum()>60000))throw new InvalidOperationException("Invalid source-frame timing");
            var directions=new List<Direction>();
            foreach(var d in p.GetProperty("directions").EnumerateArray())
            {
                var frames=new List<Frame>();
                foreach(var f in d.GetProperty("frames").EnumerateArray())
                {var r=f.GetProperty("rect");var pivot=f.GetProperty("pivot");frames.Add(new Frame(f.TryGetProperty("file",out var file)?file.GetString()!:Root+common,new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle()),new Vector2(pivot[0].GetSingle(),pivot[1].GetSingle())));}
                if(frames.Count<16||frames.Count>20)throw new InvalidOperationException("Actor clip requires16–20actual frames");
                if(timing!=null&&timing.Length!=frames.Count)throw new InvalidOperationException("Source timing/frame count differs");
                directions.Add(new Direction(d.GetProperty("direction").GetString()!,d.GetProperty("flip").GetBoolean(),d.TryGetProperty("referenceHeight",out var h)?h.GetSingle():height,frames.ToArray(),timing));
            }
            var id=p.GetProperty("id").GetString()!;Pages.Add(id,new Page(id,p.GetProperty("status").GetString()!,directions.ToArray(),p.GetProperty("productionApproved").GetBoolean(),p.GetProperty("visualState").GetString()!,p.GetProperty("visualNotes").GetString()!,p.GetProperty("sha256").GetString()!));
        }
    }
    public bool Resolve(string actorId,string clip,int direction,out Direction? result)
    {
        result=null;if(!Actors.TryGetValue(actorId,out var actor))return false;
        string id=actorId.ToLowerInvariant()+"_"+clip;
        if(actor.Kind=="VFX")id=actorId.ToLowerInvariant().Replace('-','_')+"_vfx";
        string name=new[]{"N","NE","E","SE","S","SW","W","NW"}[Math.Clamp(direction,0,7)];
        bool mirrorOverride=false;string sourceName=name;
        // A separately authored angle repairs one block; allowed mirrors use that repair too.
        if(actor.Kind!="VFX")
        {
            string specific=id+"_"+name.ToLowerInvariant();
            if(Pages.ContainsKey(specific))id=specific;
            else if(direction>=5)
            {
                if(!actor.Mirror)return false;
                sourceName=new[]{"SE","E","NE"}[Math.Clamp(direction-5,0,2)];
                string source=id+"_"+sourceName.ToLowerInvariant();
                if(Pages.ContainsKey(source)){id=source;mirrorOverride=true;}
            }
        }
        if(!Pages.TryGetValue(id,out var page)||(!_reviewMode&&!page.Approved))return false;
        result=actor.Kind=="VFX"?page.Directions[0]:page.Directions.FirstOrDefault(d=>d.Name==(mirrorOverride?sourceName:name));
        if(mirrorOverride&&result!=null)result=result with{Name=name,Flip=!result.Flip};
        return result!=null;
    }
    public string ReviewStatus(string actorId,string clip)
    {
        string key=Actors[actorId].Kind=="VFX"?actorId.ToLowerInvariant().Replace('-','_')+"_vfx":actorId.ToLowerInvariant()+"_"+clip;
        var pages=Pages.Values.Where(p=>p.Id==key||new[]{"n","ne","e","se","s","sw","w","nw"}.Any(d=>p.Id==key+"_"+d)).ToArray();
        return pages.Length==0?"CHƯA CÓ DỮ LIỆU":string.Join("\n",pages.Select(p=>p.Id+": "+p.VisualState+(p.Notes.Length>0?" · "+p.Notes:"")));
    }
    public Texture2D Texture(string file)
    {
        if(_textures.TryGetValue(file,out var texture))return texture;
        while(_textures.Count>=8){string old=_order.Dequeue();if(_textures.Remove(old,out var resource))resource.Dispose();}
        texture=ResourceLoader.Load<Texture2D>(file,cacheMode:ResourceLoader.CacheMode.Ignore)??throw new InvalidOperationException("PNG unavailable or not imported: "+file);_textures.Add(file,texture);_order.Enqueue(file);return texture;
    }
    public static double Duration(string clip)=>clip switch{"idle"=>1,"walk"=>.8,"run"=>.64,"basic_attack"=>.6,"hurt"=>.3,"death"=>1.2,"dodge"=>.48,"turn"=>.5,"interact"=>1.6,_=>.9};
    // Presentation-only review profiles, never authoritative combat/hit windows.
    public static double Duration(string actorId,string clip)=>actorId switch
    {
        // Carpling tell/recovery follow the visual bible; .30 attack is a review assumption.
        "MOB_CARPLING"=>clip switch{"telegraph_01"=>.45,"attack_01"=>.30,"recovery_01"=>.50,_=>Duration(clip)},
        // .70 anticipation follows the visual bible's root cue. Attack/recovery
        // are editable presentation assumptions, not combat authority.
        "MOB_WATERROOT"=>clip switch{"telegraph_01"=>.70,"attack_01"=>.35,"recovery_01"=>.55,"telegraph_02"=>.70,"attack_02"=>.40,"recovery_02"=>.60,_=>Duration(clip)},
        // Full physical guard preview includes raise/settle. The authoritative
        // .4s parry window is not inferred from this .8s art-review timeline.
        "CLASS_MINH_KIEM"=>clip switch{"skill_01"=>.8,"skill_02"=>.59,"skill_03"=>.60,"skill_04"=>.8,"skill_05"=>.48,"skill_06"=>1.55,_=>Duration(clip)},
        _=>Duration(clip)
    };
    public static double Duration(string actor,string clip,Direction direction)=>direction.SourceFrameDurationsMs?.Sum()/1000??Duration(actor,clip);
    public static double TimeAt(string actor,string clip,Direction direction,int frame)
    {
        frame=Math.Clamp(frame,0,direction.Frames.Length-1);
        return direction.SourceFrameDurationsMs?.Take(frame).Sum()/1000??Duration(actor,clip)*frame/direction.Frames.Length;
    }
    public static int FrameAt(string actor,string clip,Direction direction,double seconds,bool loop)
    {
        double duration=Duration(actor,clip,direction);
        if(direction.SourceFrameDurationsMs==null)
        {int elapsed=(int)(Math.Max(0,seconds)/duration*direction.Frames.Length);return loop?elapsed%direction.Frames.Length:Math.Min(elapsed,direction.Frames.Length-1);}
        double local=loop?((seconds%duration+duration)%duration):Math.Clamp(seconds,0,duration);
        if(loop&&duration-local<1e-10)local=0;
        double ms=local*1000;
        for(int frame=0;frame<direction.SourceFrameDurationsMs.Length;frame++)
        {double step=direction.SourceFrameDurationsMs[frame];if(ms+1e-7<step)return frame;ms-=step;}
        return direction.Frames.Length-1;
    }
    public float ReferenceHeight(string id,int direction,Direction current)=>current.Height;
    public void Dispose(){foreach(var texture in _textures.Values)texture.Dispose();_textures.Clear();}
}

/// <summary>Frame-based sprite player; no skeletal warp or gameplay events.</summary>
public partial class ActorLibrarySprite : Sprite2D
{
    public ActorLibraryData Library=null!;
    public string ActorId="",Clip="idle";
    public int Facing=4,ManualFrame=-1,DisplayedFrame;
    public float DisplayHeight=72;
    public bool Paused,Loop=true;
    private double _clock;
    private ActorLibraryData.Frame? _shown;
    public bool Available=>Library!=null&&Library.Resolve(ActorId,Clip,Facing,out _);
    public void Restart(){_clock=0;_shown=null;}
    public void Seek(int frame)
    {if(Library!=null&&Library.Resolve(ActorId,Clip,Facing,out var direction)){ManualFrame=Math.Clamp(frame,0,direction!.Frames.Length-1);_clock=ActorLibraryData.TimeAt(ActorId,Clip,direction,ManualFrame);_shown=null;}}
    public override void _Ready(){RegionEnabled=true;Centered=false;TextureFilter=TextureFilterEnum.Nearest;}
    public override void _Process(double delta)
    {
        if(Library==null||!Library.Resolve(ActorId,Clip,Facing,out var direction)){Visible=false;return;}
        Visible=true;if(!Paused)_clock+=delta;
        int count=direction!.Frames.Length;
        int frame=ManualFrame>=0?Math.Clamp(ManualFrame,0,count-1):ActorLibraryData.FrameAt(ActorId,Clip,direction,_clock,Loop);
        DisplayedFrame=frame;var pose=direction.Frames[frame];
        if(ReferenceEquals(pose,_shown))return;_shown=pose;
        Texture=Library.Texture(pose.File);RegionRect=pose.Region;FlipH=direction.Flip;
        var pivot=pose.Pivot;if(FlipH)pivot.X=pose.Region.Size.X-pivot.X;
        Offset=-pivot;Scale=Vector2.One*DisplayHeight/Math.Max(1,Library.ReferenceHeight(ActorId,Facing,direction));
    }
}
