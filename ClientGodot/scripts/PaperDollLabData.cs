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

/// <summary>Unapproved authoring data. Never writes inventory, account state or production packs.</summary>
public sealed class PaperDollLabData
{
    public const string CataloguePath="res://assets/paperdoll_lab/catalog.json";
    public sealed record Source(string File,string Sha256);
    public sealed record Frame(int[] Region,int[] Offset,Dictionary<string,int[]> Anchors,string[] PaintOrder,string Fingerprint);
    public sealed record Body(string Id,string Name,string RigId,string Texture,int SourcePixelsPerUnit,Frame[] Frames);
    public sealed record PartDef(string Id,string Name,string Slot,string Anchor,string Category,int[] Region,int[] Offset,
        string Texture,int SourcePixelsPerUnit,string[] Hides,int UniqueSourceImages,bool Approved);
    public sealed record Catalogue(int SchemaVersion,string Scope,bool ProductionApproved,int[] Canvas,int[] Origin,
        string Direction,string Clip,double Seconds,int FrameCount,Source[] Sources,Body[] Bodies,PartDef[] Parts,string CatalogueFingerprint);
    public sealed class Draft
    {
        public int SchemaVersion {get;set;}=1;
        public string CatalogueFingerprint {get;set;}="";
        public Dictionary<string,Pixel[]> Offsets {get;set;}=new(StringComparer.Ordinal);
        public Dictionary<string,Pixel[]> Anchors {get;set;}=new(StringComparer.Ordinal);
    }
    private static readonly JsonSerializerOptions Json=new(){PropertyNameCaseInsensitive=true,WriteIndented=true};
    public Catalogue Data {get;}
    public Draft Edits {get;private set;}
    public PaperDollLabData()
    {
        string catalogueText=Godot.FileAccess.GetFileAsString(CataloguePath);
        Data=JsonSerializer.Deserialize<Catalogue>(catalogueText,Json)??throw new Exception("missing fit catalogue");
        using(var document=JsonDocument.Parse(catalogueText))
        {using var canonical=new MemoryStream();using(var writer=new Utf8JsonWriter(canonical,new JsonWriterOptions{Encoder=JavaScriptEncoder.UnsafeRelaxedJsonEscaping}))WriteCanonical(writer,document.RootElement,true);if(Hash(canonical.ToArray())!=Data.CatalogueFingerprint)throw new Exception("catalogue fingerprint mismatch");}
        if(Data.SchemaVersion!=1||Data.Scope!="FIT_LAB_ONLY"||Data.ProductionApproved||Data.FrameCount!=16||
           Data.Bodies.Length!=2||Data.Parts.Length!=16||Data.Direction!="S"||Data.Clip!="idle"||
           !Data.Canvas.SequenceEqual(new[]{96,96})||!Data.Origin.SequenceEqual(new[]{48,72})||Data.Bodies.Any(b=>b.Frames.Length!=16)||
           Data.Bodies.Select(b=>b.Id).Distinct(StringComparer.Ordinal).Count()!=2||Data.Parts.Select(p=>p.Id).Distinct(StringComparer.Ordinal).Count()!=16)throw new Exception("invalid review-only catalogue");
        foreach(var source in Data.Sources)
        {
            if(!source.File.StartsWith("res://assets/paperdoll_lab/",StringComparison.Ordinal)||
               source.File.Contains("..",StringComparison.Ordinal)||source.File.Contains('\\')||
               !Godot.FileAccess.FileExists(source.File)||Hash(Godot.FileAccess.GetFileAsBytes(source.File))!=source.Sha256)
                throw new Exception("source hash/path mismatch: "+source.File);
        }
        if(Data.Parts.Any(p=>p.Approved||p.UniqueSourceImages!=1))throw new Exception("study part cannot claim production approval");
        Edits=EmptyDraft();
    }
    public Draft EmptyDraft()=>new(){CatalogueFingerprint=Data.CatalogueFingerprint};
    public Body FindBody(string id)=>Data.Bodies.Single(b=>b.Id==id);
    public Pixel Offset(string body,string part,int frame)
    {
        string key=body+"/"+part;var def=Data.Parts.Single(p=>p.Id==part);
        return Edits.Offsets.TryGetValue(key,out var values)?values[frame]:ToPixel(def.Offset);
    }
    public Pixel Anchor(string body,string name,int frame)
    {
        string key=body+"/"+name;
        return Edits.Anchors.TryGetValue(key,out var values)?values[frame]:ToPixel(FindBody(body).Frames[frame].Anchors[name]);
    }
    public void SetOffset(string body,string part,int frame,Pixel value,bool all)
    {
        ValidateValue(value);if(frame<0||frame>=16)throw new ArgumentOutOfRangeException(nameof(frame));
        string key=body+"/"+part;
        if(!Edits.Offsets.ContainsKey(key))Edits.Offsets[key]=Enumerable.Range(0,16).Select(i=>Offset(body,part,i)).ToArray();
        if(all)Array.Fill(Edits.Offsets[key],value);else Edits.Offsets[key][frame]=value;
    }
    public void SetAnchor(string body,string name,int frame,Pixel value,bool all)
    {
        ValidateValue(value);if(frame<0||frame>=16||name=="ground")throw new ArgumentOutOfRangeException(nameof(frame));
        string key=body+"/"+name;
        if(!Edits.Anchors.ContainsKey(key))Edits.Anchors[key]=Enumerable.Range(0,16).Select(i=>Anchor(body,name,i)).ToArray();
        if(all)Array.Fill(Edits.Anchors[key],value);else Edits.Anchors[key][frame]=value;
    }
    public Look Build(string bodyId,IEnumerable<string> selected,long revision)
    {
        var body=FindBody(bodyId);
        var poses=body.Frames.Select((f,i)=>{
            var anchors=f.Anchors.ToDictionary(a=>a.Key,a=>Anchor(bodyId,a.Key,i),StringComparer.Ordinal);
            // Edits are new authoring candidates, never an approval of a previously fitted pack.
            string guide=string.Join(";",anchors.OrderBy(a=>a.Key,StringComparer.Ordinal).Select(a=>$"{a.Key}:{a.Value.X},{a.Value.Y}"));
            return new Pose(Hash(Encoding.UTF8.GetBytes(f.Fingerprint+"|"+guide)),anchors,
                new Dictionary<string,Slice>{{"body",new(body.Texture,ToRegion(f.Region),ToPixel(f.Offset))}},f.PaintOrder);
        }).ToArray();
        string poseSet=body.RigId+"/MK_LAB_IDLE_S";const string key="idle/S";
        var clip=new Clip(key,poseSet,Data.Seconds,true,poses);
        var parts=selected.Select(id=>{
            var p=Data.Parts.Single(d=>d.Id==id);
            var slices=Enumerable.Range(0,16).Select(i=>new Slice(p.Texture,ToRegion(p.Region),Offset(bodyId,id,i),
                p.Anchor,SourcePixelsPerUnit:p.SourcePixelsPerUnit)).ToArray();
            return new Part(id,p.Slot,body.RigId,p.Category=="WEAPON"?"JIAN":null,PartMode.AnchoredRigid,false,p.Hides,
                new Dictionary<string,Binding>{{key,new(poseSet,slices,poses.Select(f=>f.Fingerprint).ToArray())}});
        }).ToArray();
        return new Look(revision,new BodyPack(body.Id,"CLASS_MINH_KIEM",body.RigId,"JIAN",new(96,96),new(48,72),false,
            new Dictionary<string,Clip>{{key,clip}},body.SourcePixelsPerUnit),parts);
    }
    public string ExportDraft()=>JsonSerializer.Serialize(Edits,Json)+"\n";
    public bool TryImportDraft(string text,out string reason)
    {
        reason="";
        try
        {
            if(text.Length>128*1024)throw new Exception("draft quá lớn");
            var draft=JsonSerializer.Deserialize<Draft>(text,Json)??throw new Exception("draft rỗng");
            if(draft.SchemaVersion!=1||draft.CatalogueFingerprint!=Data.CatalogueFingerprint)throw new Exception("nguồn/guide đã đổi; cần fit lại");
            if(draft.Offsets==null||draft.Anchors==null||draft.Offsets.Count>32||draft.Anchors.Count>12)throw new Exception("draft sai giới hạn");
            foreach(var (key,frames) in draft.Offsets)
            {
                var tokens=key.Split('/');
                if(tokens.Length!=2||!Data.Bodies.Any(b=>b.Id==tokens[0])||!Data.Parts.Any(p=>p.Id==tokens[1]))throw new Exception("part/body không tồn tại");
                ValidateFrames(frames);
            }
            foreach(var (key,frames) in draft.Anchors)
            {
                var tokens=key.Split('/');
                if(tokens.Length!=2||tokens[1]=="ground"||!Data.Bodies.Any(b=>b.Id==tokens[0]&&b.Frames.All(f=>f.Anchors.ContainsKey(tokens[1]))))
                    throw new Exception("anchor không hợp lệ");
                ValidateFrames(frames);
            }
            // Compile all edited body/part bindings before changing editor state.
            var previous=Edits;Edits=draft;
            try
            {
                foreach(var body in Data.Bodies)foreach(var part in Data.Parts)
                    if(!TryCompile(Build(body.Id,new[]{part.Id},0),true,out _,out var error))throw new Exception(error);
            }
            finally {Edits=previous;}
            Edits=draft;return true;
        }
        catch(Exception e) when(e is JsonException or InvalidOperationException or ArgumentException or NullReferenceException||e.GetType()==typeof(Exception))
        {reason=e.Message;return false;}
    }
    public void Reset()=>Edits=EmptyDraft();
    private static void ValidateFrames(Pixel[] frames)
    {if(frames==null||frames.Length!=16)throw new Exception("draft phải có đủ16 placement");foreach(var v in frames)ValidateValue(v);}
    private static void ValidateValue(Pixel value)
    {if(Math.Abs((long)value.X)>96||Math.Abs((long)value.Y)>96)throw new ArgumentOutOfRangeException(nameof(value));}
    private static Pixel ToPixel(int[] a)=>new(a[0],a[1]);
    private static Region ToRegion(int[] a)=>new(a[0],a[1],a[2],a[3]);
    private static void WriteCanonical(Utf8JsonWriter writer,JsonElement value,bool root=false)
    {
        if(value.ValueKind==JsonValueKind.Object)
        {writer.WriteStartObject();foreach(var property in value.EnumerateObject().OrderBy(p=>p.Name,StringComparer.Ordinal)){if(root&&property.Name=="catalogueFingerprint")continue;writer.WritePropertyName(property.Name);WriteCanonical(writer,property.Value);}writer.WriteEndObject();}
        else if(value.ValueKind==JsonValueKind.Array){writer.WriteStartArray();foreach(var item in value.EnumerateArray())WriteCanonical(writer,item);writer.WriteEndArray();}
        else value.WriteTo(writer);
    }
    private static string Hash(byte[] bytes)=>Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
}
