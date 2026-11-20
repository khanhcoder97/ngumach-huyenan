using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace Ngumach.VisualReboot;

/// <summary>Paper-doll contract prototype. No stats, inventory writes or network authority.</summary>
public static class ModularCharacterModel
{
    public readonly record struct Pixel(int X,int Y)
    {public static Pixel operator +(Pixel a,Pixel b)=>new(a.X+b.X,a.Y+b.Y);public static Pixel operator -(Pixel a,Pixel b)=>new(a.X-b.X,a.Y-b.Y);}
    public readonly record struct Region(int X,int Y,int Width,int Height);
    public readonly record struct Point(double X,double Y);
    public readonly record struct PaintTransform(double PivotX,double PivotY,double Degrees,double Scale=1,bool FlipH=false,bool FlipV=false);
    public static readonly PaintTransform Identity=new(0,0,0,1);
    public sealed record Slice(string Texture,Region Region,Pixel Offset,string? Anchor=null,bool Hidden=false,int SourcePixelsPerUnit=0,PaintTransform? Transform=null);
    public sealed record Pose(string Fingerprint,IReadOnlyDictionary<string,Pixel> Anchors,IReadOnlyDictionary<string,Slice> Skin,string[] PaintOrder);
    public sealed record Clip(string Key,string PoseSet,double Seconds,bool Loop,Pose[] Poses);
    public sealed record BodyPack(string Id,string ClassId,string RigId,string WeaponFamily,Pixel Canvas,Pixel Origin,bool Approved,IReadOnlyDictionary<string,Clip> Clips,int SourcePixelsPerUnit=1);
    public enum PartMode {Deformable,AnchoredRigid}
    public sealed record Binding(string PoseSet,Slice[] Frames,string[] ExpectedBodyPoses);
    public sealed record Part(string Id,string Slot,string RigId,string? WeaponFamily,PartMode Mode,bool Approved,string[] Hides,IReadOnlyDictionary<string,Binding> Bindings);
    public sealed record Look(long Revision,BodyPack Body,Part[] Parts);
    public readonly record struct DrawCommand(string PartId,string Texture,Region Region,Pixel Position,int SourcePixelsPerUnit=1,PaintTransform? Transform=null);
    public sealed record ClipPlan(double Seconds,bool Loop,IReadOnlyList<IReadOnlyList<DrawCommand>> Frames);
    public sealed class PreparedLook
    {
        public long Revision {get;}
        public IReadOnlyDictionary<string,ClipPlan> Clips {get;}
        internal PreparedLook(long revision,Dictionary<string,ClipPlan> clips)
        {Revision=revision;Clips=new ReadOnlyDictionary<string,ClipPlan>(clips);}
    }
    public static readonly string[] Directions={"N","NE","E","SE","S","SW","W","NW"};
    public static readonly string[] RequiredActions={"idle","walk","run","hurt","death","dodge","interact","basic_attack","skill_01","skill_02","skill_03","skill_04","skill_05","skill_06"};
    private static readonly Dictionary<string,string> WeaponFamilies=new(StringComparer.Ordinal)
    {{"CLASS_MINH_KIEM","JIAN"},{"CLASS_ANH_DAO","DAO"},{"CLASS_HUYEN_BUT","BRUSH"},{"CLASS_THACH_CHUY","HAMMER"},{"CLASS_LINH_CUNG","BOW"}};

    public static bool TryCompile(Look look,bool reviewMode,out PreparedLook? prepared,out string reason)
    {
        prepared=null;reason="";
        try
        {
            var body=look.Body;
            Require(look.Revision>=0,"negative appearance revision");
            Require(WeaponFamilies.TryGetValue(body.ClassId,out var family)&&family==body.WeaponFamily,"unknown class/weapon family");
            Require(body.RigId is "RIG_HUMAN_M_V1" or "RIG_HUMAN_F_V1" or "RIG_HUMAN_M_V2" or "RIG_HUMAN_F_V2","unknown body rig");
            Require(body.Canvas==new Pixel(96,96)&&body.Origin==new Pixel(48,72),"master canvas/origin mismatch");
            Require(reviewMode||body.Approved,"body is not production approved");
            Require(body.SourcePixelsPerUnit>=1&&body.SourcePixelsPerUnit<=16,"invalid source pixel scale");
            Require(reviewMode||body.SourcePixelsPerUnit==1,"production requires native pixel master");
            Require(body.Clips.Count>0,"body has no clips");
            if(!reviewMode)foreach(string action in RequiredActions)foreach(string direction in Directions)
                Require(body.Clips.ContainsKey(action+"/"+direction),"missing production body clip "+action+"/"+direction);
            Require(look.Parts.Select(p=>p.Slot).Distinct(StringComparer.Ordinal).Count()==look.Parts.Length,"duplicate visual slot");
            foreach(var part in look.Parts)
            {
                Require(part.RigId==body.RigId,"part/body rig mismatch: "+part.Id);
                Require(reviewMode||part.Approved,"part is not production approved: "+part.Id);
                Require(part.WeaponFamily==null||part.WeaponFamily==body.WeaponFamily,"weapon family mismatch");
                Require(!part.Hides.Contains("body",StringComparer.Ordinal),"a wearable cannot hide the whole body");
            }
            var plans=new Dictionary<string,ClipPlan>(StringComparer.Ordinal);
            foreach(var (key,clip) in body.Clips)
            {
                Require(key==clip.Key&&key.Split('/').Length==2&&Directions.Contains(key.Split('/')[1],StringComparer.Ordinal),"invalid clip key");
                int count=clip.Poses.Length;
                Require(count>=16&&count<=20,"body clip requires16–20authored poses");
                Require(double.IsFinite(clip.Seconds)&&clip.Seconds>0,"invalid duration");
                Require(clip.Poses.All(p=>!string.IsNullOrWhiteSpace(p.Fingerprint))&&clip.Poses.Select(p=>p.Fingerprint).Distinct(StringComparer.Ordinal).Count()==count,"duplicate/missing body pose fingerprints");
                // Hash uniqueness is a structural check only. Approved art still needs human motion/fit QA.
                foreach(var part in look.Parts)
                {
                    Require(part.Bindings.TryGetValue(key,out var binding),"missing part clip: "+part.Id+" "+key);
                    Require(binding!.PoseSet==clip.PoseSet&&binding.Frames.Length==count,"part pose-set/frame-count mismatch: "+part.Id);
                    Require(binding.ExpectedBodyPoses.SequenceEqual(clip.Poses.Select(p=>p.Fingerprint)),"body pose changed since this part was fitted: "+part.Id);
                }
                var hidden=new HashSet<string>(look.Parts.SelectMany(p=>p.Hides),StringComparer.Ordinal);
                var frames=new IReadOnlyList<DrawCommand>[count];
                for(int i=0;i<count;i++)
                {
                    var pose=clip.Poses[i];
                    Require(pose.Anchors.TryGetValue("ground",out var ground)&&ground==body.Origin,"ground anchor drift");
                    Require(pose.Skin.ContainsKey("body")&&!pose.Skin["body"].Hidden,"missing body pass");
                    Require(pose.PaintOrder.Distinct(StringComparer.Ordinal).Count()==pose.PaintOrder.Length,"duplicate painter-order token");
                    Require(!hidden.Overlaps(pose.Skin.Keys),"wearable hides a body skin pass");
                    var slices=new Dictionary<string,Slice>(pose.Skin,StringComparer.Ordinal);
                    foreach(var part in look.Parts)
                    {
                        Require(!slices.ContainsKey(part.Slot),"wearable overwrites base skin slot");
                        var slice=part.Bindings[key].Frames[i];
                        Require(part.Mode!=PartMode.Deformable||slice.Anchor==null||reviewMode,"deformable uses master-canvas coordinates");
                        Require(part.Mode!=PartMode.AnchoredRigid||slice.Hidden||slice.Anchor!=null,"rigid part lacks anchor");
                        slices.Add(part.Slot,slice);
                    }
                    Require(slices.Keys.All(s=>pose.PaintOrder.Contains(s,StringComparer.Ordinal)),"missing painter-order token");
                    var commands=new List<DrawCommand>();
                    foreach(string slot in pose.PaintOrder)
                    {
                        if(!slices.TryGetValue(slot,out var slice)||slice.Hidden||hidden.Contains(slot))continue;
                        Require(slice.Region.X>=0&&slice.Region.Y>=0&&slice.Region.Width>0&&slice.Region.Height>0,"invalid source rect");
                        Require(reviewMode||slice.Texture.StartsWith("res://assets/modular_character_v1/",StringComparison.Ordinal),"unapproved asset root");
                        int sourceScale=slice.SourcePixelsPerUnit==0?body.SourcePixelsPerUnit:slice.SourcePixelsPerUnit;
                        Require(sourceScale>=1&&sourceScale<=16,"invalid layer source scale");
                        Require(reviewMode||sourceScale==1,"production layer requires native pixel master");
                        Pixel position=slice.Offset;
                        if(slice.Anchor!=null)
                        {Require(pose.Anchors.TryGetValue(slice.Anchor,out var anchor),"missing anchor: "+slice.Anchor);position+=anchor;}
                        var transform=slice.Transform??Identity;
                        Require(ValidTransform(transform),"invalid part transform");
                        Require(Math.Abs(transform.PivotX)<=96&&Math.Abs(transform.PivotY)<=96&&Math.Abs(transform.Degrees)<=180,"transform out of range");
                        Require(reviewMode||transform==Identity,"runtime transform is review-only; production requires authored angles");
                        var command=new DrawCommand(slot,slice.Texture,slice.Region,position-body.Origin,sourceScale,transform);
                        Require(Corners(command).All(p=>p.X+body.Origin.X>=-.001&&p.Y+body.Origin.Y>=-.001&&p.X+body.Origin.X<=body.Canvas.X+.001&&p.Y+body.Origin.Y<=body.Canvas.Y+.001),"layer outside shared canvas");
                        commands.Add(command);
                    }
                    frames[i]=Array.AsReadOnly(commands.ToArray());
                }
                plans.Add(key,new ClipPlan(clip.Seconds,clip.Loop,Array.AsReadOnly(frames)));
            }
            prepared=new PreparedLook(look.Revision,plans);return true;
        }
        catch(InvalidOperationException e){reason=e.Message;return false;}
    }
    public static bool ValidTransform(PaintTransform t)=>double.IsFinite(t.PivotX)&&double.IsFinite(t.PivotY)&&double.IsFinite(t.Degrees)&&double.IsFinite(t.Scale)&&t.Scale>=.25&&t.Scale<=2&&Math.Abs(t.PivotX)<=96&&Math.Abs(t.PivotY)<=96&&Math.Abs(t.Degrees)<=180;
    public static Point ToActor(DrawCommand command,double x,double y)
    {
        var t=command.Transform??Identity;double a=t.Degrees*Math.PI/180,c=Math.Cos(a),s=Math.Sin(a);
        x=(x-t.PivotX)*t.Scale*(t.FlipH?-1:1);y=(y-t.PivotY)*t.Scale*(t.FlipV?-1:1);
        return new(command.Position.X+x*c-y*s,command.Position.Y+x*s+y*c);
    }
    public static Point FromActor(DrawCommand command,double x,double y)
    {
        var t=command.Transform??Identity;double a=-t.Degrees*Math.PI/180,c=Math.Cos(a),s=Math.Sin(a);
        x-=command.Position.X;y-=command.Position.Y;double rx=x*c-y*s,ry=x*s+y*c;
        return new(rx/t.Scale*(t.FlipH?-1:1)+t.PivotX,ry/t.Scale*(t.FlipV?-1:1)+t.PivotY);
    }
    public static Point[] Corners(DrawCommand command)
    {double w=(double)command.Region.Width/command.SourcePixelsPerUnit,h=(double)command.Region.Height/command.SourcePixelsPerUnit;return new[]{ToActor(command,0,0),ToActor(command,w,0),ToActor(command,w,h),ToActor(command,0,h)};}
    private static void Require(bool condition,string reason){if(!condition)throw new InvalidOperationException(reason);}

    /// <summary>One clock for the whole avatar. Pure-data staging happens before an atomic swap.</summary>
    public sealed class Session
    {
        public PreparedLook? Current {get;private set;}
        public string ClipKey {get;private set;}="idle/S";
        public double Elapsed {get;private set;}
        public int FrameIndex=>Current==null?0:Index(Current.Clips[ClipKey],Elapsed);
        public IReadOnlyList<DrawCommand> Commands=>Current==null?Array.Empty<DrawCommand>():Current.Clips[ClipKey].Frames[FrameIndex];
        public bool TryApply(Look look,bool reviewMode,Func<ClipPlan,bool> resourcesReady,out string reason)
        {
            reason="";if(Current!=null&&look.Revision<=Current.Revision){reason="stale appearance revision";return false;}
            if(!TryCompile(look,reviewMode,out var prepared,out reason))return false;
            string stagedClip=ClipKey;
            if(!prepared!.Clips.TryGetValue(stagedClip,out var clip)){reason="current action missing in new appearance";return false;}
            if(!resourcesReady(clip)){reason="texture pages not ready; previous appearance retained";return false;}
            // Do not reset the action or body clock when gear changes.
            if(Current!=null&&look.Revision<=Current.Revision){reason="appearance superseded while loading";return false;}
            if(ClipKey!=stagedClip){reason="action changed while preparing appearance; retry current action";return false;}
            Current=prepared;return true;
        }
        public bool TryPlay(string key,Func<ClipPlan,bool> resourcesReady,bool preservePhase=false,bool restart=false)
        {
            if(Current==null||!Current.Clips.TryGetValue(key,out var next))return false;
            if(key==ClipKey&&!restart)return true;
            var stagedLook=Current;string stagedClip=ClipKey;
            if(!resourcesReady(next))return false;
            if(!ReferenceEquals(Current,stagedLook)||ClipKey!=stagedClip)return false;
            double phase=preservePhase?Elapsed/Current.Clips[ClipKey].Seconds:0;
            ClipKey=key;Elapsed=phase*next.Seconds;return true;
        }
        public bool SeekFrame(int frame)
        {if(Current==null)return false;var clip=Current.Clips[ClipKey];if(frame<0||frame>=clip.Frames.Count)return false;Elapsed=(frame+.25)/clip.Frames.Count*clip.Seconds;return true;}
        public void Advance(double delta)
        {if(!double.IsFinite(delta)||delta<0)throw new ArgumentOutOfRangeException(nameof(delta));if(Current==null)return;var clip=Current.Clips[ClipKey];Elapsed=clip.Loop?(Elapsed+delta)%clip.Seconds:Math.Min(Elapsed+delta,clip.Seconds);}
        private static int Index(ClipPlan clip,double elapsed)=>Math.Clamp((int)(elapsed/clip.Seconds*clip.Frames.Count),0,clip.Frames.Count-1);
    }
}
