using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Encodings.Web;
using System.IO;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Appearance authoring only. No inventory, stats, ownership or equipment-slot mutation.</summary>
public sealed class PaperDollLabData
{
    public const string CataloguePath="res://assets/paperdoll_lab/catalog.json";
    public sealed record Source(string File,string Sha256);
    public sealed record Frame(int[] Region,int[] Offset,Dictionary<string,int[]> Anchors,string[] PaintOrder,string Fingerprint,int[] HandRegion,int[] HandOffset);
    public sealed record Body(string Id,string Name,string RigId,string Texture,int SourcePixelsPerUnit,Frame[] Frames);
    public sealed record PartDef(string Id,string Name,string Slot,string Anchor,string Category,int[] Region,int[] Offset,
        string Texture,int SourcePixelsPerUnit,string[] Hides,int UniqueSourceImages,bool Approved,string? RigId,PaintTransform Transform,int HeadCoverClipTopPixels,int[][]? FrameRegions=null,PaintTransform[]? FrameTransforms=null);
    public sealed record Catalogue(int SchemaVersion,string Scope,bool ProductionApproved,int[] Canvas,int[] Origin,
        string Direction,string Clip,double Seconds,int FrameCount,Source[] Sources,Body[] Bodies,PartDef[] Parts,string CatalogueFingerprint);
    public sealed class Draft
    {
        public int SchemaVersion {get;set;}=2;
        public string CatalogueFingerprint {get;set;}="";
        public Dictionary<string,Pixel[]> Offsets {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,Pixel[]> Anchors {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,PaintTransform[]> Transforms {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,string[]> Attachments {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,bool[]> Hidden {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,string[][]> Orders {get;set;}=new(StringComparer.Ordinal);
    }
    private static readonly JsonSerializerOptions Json=new(){PropertyNameCaseInsensitive=true,WriteIndented=true};
    public Catalogue Data {get;}
    public Draft Edits {get;private set;}
    public bool Registered {get;}
    public PaperDollLabData(bool registered=false)
    {
        Registered=registered;
        if(registered){Data=RegisteredPaperDollMaster.CreateCatalogue();Edits=EmptyDraft();return;}
        string text=Godot.FileAccess.GetFileAsString(CataloguePath);
        Data=JsonSerializer.Deserialize<Catalogue>(text,Json)??throw new Exception("missing catalogue");
        using(var document=JsonDocument.Parse(text))
        {using var canonical=new MemoryStream();using(var writer=new Utf8JsonWriter(canonical,new JsonWriterOptions{Encoder=JavaScriptEncoder.UnsafeRelaxedJsonEscaping}))WriteCanonical(writer,document.RootElement,true);if(Hash(canonical.ToArray())!=Data.CatalogueFingerprint)throw new Exception("catalogue fingerprint mismatch");}
        if(Data.SchemaVersion!=2||Data.Scope!="FIT_LAB_ONLY"||Data.ProductionApproved||Data.FrameCount!=16||
           Data.Bodies.Length!=2||Data.Parts.Length!=18||Data.Direction!="S"||Data.Clip!="idle"||
           !Data.Canvas.SequenceEqual(new[]{96,96})||!Data.Origin.SequenceEqual(new[]{48,72})||Data.Bodies.Any(b=>b.Frames.Length!=16)||
           Data.Bodies.Select(b=>b.Id).Distinct(StringComparer.Ordinal).Count()!=2||Data.Parts.Select(p=>p.Id).Distinct(StringComparer.Ordinal).Count()!=18)
            throw new Exception("invalid fit catalogue");
        foreach(var source in Data.Sources)
            if(!source.File.StartsWith("res://assets/paperdoll_lab/",StringComparison.Ordinal)||source.File.Contains("..",StringComparison.Ordinal)||
               source.File.Contains('\\')||!Godot.FileAccess.FileExists(source.File)||Hash(Godot.FileAccess.GetFileAsBytes(source.File))!=source.Sha256)
                throw new Exception("source hash/path mismatch: "+source.File);
        if(Data.Parts.Any(p=>p.Approved||p.UniqueSourceImages!=1||p.Hides.Length!=0||p.HeadCoverClipTopPixels<0||p.HeadCoverClipTopPixels>=p.Region[3]))throw new Exception("invalid static study approval/hair policy");
        Edits=EmptyDraft();
    }
    public Draft EmptyDraft()=>new(){CatalogueFingerprint=Data.CatalogueFingerprint};
    public Body FindBody(string id)=>Data.Bodies.Single(b=>b.Id==id);
    public PartDef FindPart(string id)=>Data.Parts.Single(p=>p.Id==id);
    public bool Compatible(string body,string part)=>FindPart(part).RigId is not string rig||rig==FindBody(body).RigId;
    private static string Key(string body,string part)=>body+"/"+part;
    public Pixel Offset(string body,string part,int frame)=>Edits.Offsets.TryGetValue(Key(body,part),out var a)?a[frame]:ToPixel(FindPart(part).Offset);
    public Pixel Anchor(string body,string name,int frame)=>Edits.Anchors.TryGetValue(Key(body,name),out var a)?a[frame]:ToPixel(FindBody(body).Frames[frame].Anchors[name]);
    public PaintTransform Transform(string body,string part,int frame)=>Edits.Transforms.TryGetValue(Key(body,part),out var a)?a[frame]:FindPart(part).FrameTransforms is PaintTransform[] frames?frames[frame]:FindPart(part).Transform;
    public int[] Region(string part,int frame)=>FindPart(part).FrameRegions is int[][] frames?frames[frame]:FindPart(part).Region;
    public string Attachment(string body,string part,int frame)=>Edits.Attachments.TryGetValue(Key(body,part),out var a)?a[frame]:FindPart(part).Anchor;
    public bool IsHidden(string body,string part,int frame)=>Edits.Hidden.TryGetValue(Key(body,part),out var a)&&a[frame];
    public string[] Order(string body,int frame)=>Edits.Orders.TryGetValue(body,out var a)?a[frame].ToArray():FindBody(body).Frames[frame].PaintOrder.ToArray();
    public Pixel AbsolutePosition(string body,string part,int frame)=>Offset(body,part,frame)+Anchor(body,Attachment(body,part,frame),frame);
    private static void FrameIndex(int frame){if(frame<0||frame>=16)throw new ArgumentOutOfRangeException(nameof(frame));}
    private static void Set<T>(Dictionary<string,T[]> map,string key,int frame,T value,bool all,Func<int,T> seed)
    {FrameIndex(frame);if(!map.ContainsKey(key))map[key]=Enumerable.Range(0,16).Select(seed).ToArray();if(all)Array.Fill(map[key],value);else map[key][frame]=value;}
    public void SetOffset(string body,string part,int frame,Pixel value,bool all)
    {ValidateValue(value);Set(Edits.Offsets,Key(body,part),frame,value,all,i=>Offset(body,part,i));}
    public void SetAnchor(string body,string name,int frame,Pixel value,bool all)
    {ValidateValue(value);if(name is "ground" or "canvas")throw new ArgumentException("immutable root anchor");Set(Edits.Anchors,Key(body,name),frame,value,all,i=>Anchor(body,name,i));}
    public void SetTransform(string body,string part,int frame,PaintTransform value,bool all)
    {if(!ValidTransform(value))throw new ArgumentOutOfRangeException(nameof(value));Set(Edits.Transforms,Key(body,part),frame,value,all,i=>Transform(body,part,i));}
    public void SetPivotPreservingPlacement(string body,string part,int frame,double x,double y,bool all)
    {
        FrameIndex(frame);foreach(int i in all?Enumerable.Range(0,16):new[]{frame})
        {var t=Transform(body,part,i);var c=new DrawCommand("pivot","",new(0,0,1,1),new(0,0),1,t);var shift=ToActor(c,x,y);var offset=Offset(body,part,i)+new Pixel((int)Math.Round(shift.X),(int)Math.Round(shift.Y));SetTransform(body,part,i,t with{PivotX=x,PivotY=y},false);SetOffset(body,part,i,offset,false);}
    }
    public void SetHidden(string body,string part,int frame,bool value,bool all)
        =>Set(Edits.Hidden,Key(body,part),frame,value,all,i=>IsHidden(body,part,i));
    public void SetAttachment(string body,string part,int frame,string anchor,bool all)
    {
        FrameIndex(frame);if(!FindBody(body).Frames.All(f=>f.Anchors.ContainsKey(anchor)))throw new ArgumentException("unknown anchor");
        foreach(int i in all?Enumerable.Range(0,16):new[]{frame})
        {Pixel absolute=AbsolutePosition(body,part,i);Set(Edits.Attachments,Key(body,part),i,anchor,false,j=>Attachment(body,part,j));SetOffset(body,part,i,absolute-Anchor(body,anchor,i),false);}
    }
    public void MoveLayer(string body,string slot,int frame,int delta,bool all)
    {
        FrameIndex(frame);
        if(!Edits.Orders.ContainsKey(body))Edits.Orders[body]=Enumerable.Range(0,16).Select(i=>Order(body,i)).ToArray();
        foreach(int i in all?Enumerable.Range(0,16):new[]{frame})
        {var order=Edits.Orders[body][i];int from=Array.IndexOf(order,slot);if(from<0)throw new ArgumentException("unknown layer");int to=Math.Clamp(from+delta,0,order.Length-1);(order[from],order[to])=(order[to],order[from]);}
    }
    public Look Build(string bodyId,IEnumerable<string> selected,long revision)
    {
        var body=FindBody(bodyId);var ids=selected.ToArray();
        if(ids.Any(id=>!Compatible(bodyId,id)))throw new ArgumentException("outfit/body rig mismatch");
        if(ids.Count(id=>FindPart(id).Slot=="outfit")>1)throw new ArgumentException("one complete outfit at a time");
        var poses=body.Frames.Select((f,i)=>{
            var anchors=f.Anchors.ToDictionary(a=>a.Key,a=>Anchor(bodyId,a.Key,i),StringComparer.Ordinal);var order=Order(bodyId,i);
            string guide=string.Join(";",anchors.OrderBy(a=>a.Key,StringComparer.Ordinal).Select(a=>$"{a.Key}:{a.Value.X},{a.Value.Y}"))+"|"+string.Join(",",order);
            return new Pose(Hash(Encoding.UTF8.GetBytes(f.Fingerprint+"|"+guide)),anchors,
                new Dictionary<string,Slice>{{"body",new(body.Texture,ToRegion(f.Region),ToPixel(f.Offset))},
                    {"hand_near",new(body.Texture,ToRegion(f.HandRegion),ToPixel(f.HandOffset))}},order);
        }).ToArray();
        string poseSet=body.RigId+"/MK_LAB_IDLE_S";const string key="idle/S";
        var parts=ids.Select(id=>{
            var p=FindPart(id);
            var slices=Enumerable.Range(0,16).Select(i=>{
                var region=ToRegion(Region(id,i));var transform=Transform(bodyId,id,i);
                bool covered=ids.Contains("HAT_TRAVELLER",StringComparer.Ordinal)&&!IsHidden(bodyId,"HAT_TRAVELLER",i);
                int clip=covered?p.HeadCoverClipTopPixels:0;
                if(clip>0){region=region with{Y=region.Y+clip,Height=region.Height-clip};transform=transform with{PivotY=transform.PivotY-(double)clip/p.SourcePixelsPerUnit};}
                string attachment=Attachment(bodyId,id,i);
                return new Slice(p.Texture,region,Offset(bodyId,id,i),Registered&&p.Category=="OUTFIT"&&attachment=="canvas"?null:attachment,Hidden:IsHidden(bodyId,id,i),SourcePixelsPerUnit:p.SourcePixelsPerUnit,Transform:transform);
            }).ToArray();
            return new Part(id,p.Slot,body.RigId,p.Category=="WEAPON"?"JIAN":null,Registered&&p.Category=="OUTFIT"?PartMode.Deformable:PartMode.AnchoredRigid,false,p.Hides,
                new Dictionary<string,Binding>{{key,new(poseSet,slices,poses.Select(f=>f.Fingerprint).ToArray())}});
        }).ToArray();
        return new Look(revision,new BodyPack(body.Id,"CLASS_MINH_KIEM",body.RigId,"JIAN",new(96,96),new(48,72),false,
            new Dictionary<string,Clip>{{key,new(key,poseSet,Data.Seconds,true,poses)}},body.SourcePixelsPerUnit),parts);
    }
    public string ExportDraft()=>JsonSerializer.Serialize(Edits,Json)+"\n";
    public bool TryImportDraft(string text,out string reason)
    {
        reason="";
        try
        {
            if(text.Length>256*1024)throw new Exception("draft quá lớn");
            var draft=JsonSerializer.Deserialize<Draft>(text,Json)??throw new Exception("draft rỗng");
            if(draft.SchemaVersion!=2||draft.CatalogueFingerprint!=Data.CatalogueFingerprint)throw new Exception("nguồn/schema/guide đã đổi; cần fit lại");
            if(draft.Offsets==null||draft.Anchors==null||draft.Transforms==null||draft.Attachments==null||draft.Hidden==null||draft.Orders==null||
               draft.Offsets.Count>36||draft.Anchors.Count>12||draft.Transforms.Count>36||draft.Attachments.Count>36||draft.Hidden.Count>36||draft.Orders.Count>2)
                throw new Exception("draft sai giới hạn");
            void PartKey(string key){var a=key.Split('/');if(a.Length!=2||!Data.Bodies.Any(b=>b.Id==a[0])||!Data.Parts.Any(p=>p.Id==a[1])||!Compatible(a[0],a[1]))throw new Exception("part/body không tương thích");}
            foreach(var (key,a) in draft.Offsets){PartKey(key);ValidateFrames(a);foreach(var v in a)ValidateValue(v);}
            foreach(var (key,a) in draft.Anchors)
            {var t=key.Split('/');if(t.Length!=2||t[1] is "ground" or "canvas"||!Data.Bodies.Any(b=>b.Id==t[0]&&b.Frames.All(f=>f.Anchors.ContainsKey(t[1]))))throw new Exception("anchor không hợp lệ");ValidateFrames(a);foreach(var v in a)ValidateValue(v);}
            foreach(var (key,a) in draft.Transforms){PartKey(key);ValidateFrames(a);if(a.Any(t=>!ValidTransform(t)))throw new Exception("transform không hợp lệ");}
            foreach(var (key,a) in draft.Hidden){PartKey(key);ValidateFrames(a);}
            foreach(var (key,a) in draft.Attachments)
            {PartKey(key);ValidateFrames(a);string b=key.Split('/')[0];if(a.Any(n=>!FindBody(b).Frames.All(f=>f.Anchors.ContainsKey(n))))throw new Exception("attachment không hợp lệ");}
            foreach(var (body,a) in draft.Orders)
            {if(!Data.Bodies.Any(b=>b.Id==body))throw new Exception("unknown body");ValidateFrames(a);for(int i=0;i<16;i++){var expected=FindBody(body).Frames[i].PaintOrder;if(a[i]==null||a[i].Length!=expected.Length||!a[i].OrderBy(x=>x,StringComparer.Ordinal).SequenceEqual(expected.OrderBy(x=>x,StringComparer.Ordinal)))throw new Exception("paint order phải đủ lớp, không trùng");}}
            var previous=Edits;Edits=draft;
            try{foreach(var body in Data.Bodies)foreach(var part in Data.Parts.Where(p=>p.RigId==null||p.RigId==body.RigId))
                if(!TryCompile(Build(body.Id,new[]{part.Id},0),true,out _,out var error))throw new Exception(error);}
            finally{Edits=previous;}
            Edits=draft;return true;
        }
        catch(Exception e) when(e is JsonException or InvalidOperationException or ArgumentException or NullReferenceException||e.GetType()==typeof(Exception))
        {reason=e.Message;return false;}
    }
    public void Reset()=>Edits=EmptyDraft();
    private static void ValidateFrames<T>(T[] a){if(a==null||a.Length!=16)throw new Exception("cần đủ16 placement");}
    private static void ValidateValue(Pixel p){if(Math.Abs((long)p.X)>192||Math.Abs((long)p.Y)>192)throw new ArgumentOutOfRangeException(nameof(p));}
    private static Pixel ToPixel(int[] a)=>new(a[0],a[1]);
    private static Region ToRegion(int[] a)=>new(a[0],a[1],a[2],a[3]);
    private static void WriteCanonical(Utf8JsonWriter w,JsonElement v,bool root=false)
    {if(v.ValueKind==JsonValueKind.Object){w.WriteStartObject();foreach(var p in v.EnumerateObject().OrderBy(p=>p.Name,StringComparer.Ordinal)){if(root&&p.Name=="catalogueFingerprint")continue;w.WritePropertyName(p.Name);WriteCanonical(w,p.Value);}w.WriteEndObject();}else if(v.ValueKind==JsonValueKind.Array){w.WriteStartArray();foreach(var i in v.EnumerateArray())WriteCanonical(w,i);w.WriteEndArray();}else v.WriteTo(w);}
    private static string Hash(byte[] b)=>Convert.ToHexString(SHA256.HashData(b)).ToLowerInvariant();
}
