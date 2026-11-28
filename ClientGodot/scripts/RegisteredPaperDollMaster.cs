using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Native pixel authoring proof: every body/garment uses the same anatomical pose.
/// Not production-approved art. No generated PNG geometry is used here.</summary>
public static class RegisteredPaperDollMaster
{
    private const int N=96;
    private const string Algorithm="REGISTERED_MASTER_DRAW_R2";
    private static readonly Dictionary<string,Texture2D> Textures=new(StringComparer.Ordinal);
    private static readonly Dictionary<string,uint[][]> Frames=new(StringComparer.Ordinal);
    private static readonly Dictionary<string,string> IdPaths=new(StringComparer.Ordinal);
    private static readonly uint Edge=C("292333"),Skin=C("EDBC92"),SkinShade=C("CF956F"),SkinLight=C("FFE0B3");
    private static string _fingerprint="";
    public static string Fingerprint=>_fingerprint;
    private static readonly string[] Order={"cape_back","body","outfit","boots","weapon_near","hand_near","eyes","hair_front","hat_front"};
    private static uint C(string rgb){uint v=Convert.ToUInt32(rgb,16);return (v>>16&255)|((v>>8&255)<<8)|((v&255)<<16)|0xff000000;}
    private sealed class Canvas
    {
        public readonly uint[] Pixels=new uint[N*N];
        public void Dot(int x,int y,uint c){if(x>=0&&y>=0&&x<N&&y<N)Pixels[y*N+x]=c;}
        public void Rect(int x,int y,int w,int h,uint c){for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)Dot(xx,yy,c);}
        public void Disc(int x,int y,int r,uint c){for(int dy=-r;dy<=r;dy++)for(int dx=-r;dx<=r;dx++)if(dx*dx+dy*dy<=r*r+.5)Dot(x+dx,y+dy,c);}
        public void Line(int x0,int y0,int x1,int y1,uint c,int radius=0)
        {int dx=Math.Abs(x1-x0),sx=x0<x1?1:-1,dy=-Math.Abs(y1-y0),sy=y0<y1?1:-1,err=dx+dy;while(true){Disc(x0,y0,radius,c);if(x0==x1&&y0==y1)break;int e=err*2;if(e>=dy){err+=dy;x0+=sx;}if(e<=dx){err+=dx;y0+=sy;}}}
        public void Stroke((int X,int Y) a,(int X,int Y) b,int radius,uint fill)
        {Line(a.X,a.Y,b.X,b.Y,Edge,radius);Line(a.X,a.Y,b.X,b.Y,fill,Math.Max(0,radius-1));}
        public void Poly(uint fill,params (int X,int Y)[] p)
        {
            int minX=p.Min(v=>v.X),maxX=p.Max(v=>v.X),minY=p.Min(v=>v.Y),maxY=p.Max(v=>v.Y);
            for(int y=minY;y<=maxY;y++)for(int x=minX;x<=maxX;x++)
            {bool inside=false;for(int i=0,j=p.Length-1;i<p.Length;j=i++){var a=p[i];var b=p[j];if((a.Y>y+.5)!=(b.Y>y+.5)&&(x+.5)<(double)(b.X-a.X)*(y+.5-a.Y)/(b.Y-a.Y)+a.X)inside=!inside;}if(inside)Dot(x,y,fill);}
            for(int i=0;i<p.Length;i++)Line(p[i].X,p[i].Y,p[(i+1)%p.Length].X,p[(i+1)%p.Length].Y,Edge);
        }
    }
    private sealed record Pose(int NearDx,int NearDy,int FarDx,int FarDy,int HeadDy,int ShoulderDy,int WaistDy)
    {
        public int Head=>18+HeadDy;
        public int Shoulder=>34+ShoulderDy;
        public int Waist=>48+WaistDy;
        public (int X,int Y) Near=>(62+NearDx,51+NearDy);
        public (int X,int Y) Far=>(34+FarDx,51+FarDy);
        public Dictionary<string,int[]> Anchors()=>new(StringComparer.Ordinal)
        {{"canvas",new[]{0,0}},{"ground",new[]{48,72}},{"head",new[]{48,Head}},{"face",new[]{48,Head+8}},
         {"chest",new[]{48,Shoulder}},{"hip",new[]{48,51+WaistDy}},{"hand_near",new[]{Near.X,Near.Y}}};
    }
    private static Canvas Body(Pose p,bool female)
    {
        var b=new Canvas();
        b.Stroke((44,51+p.WaistDy),(43,69),2,Skin);b.Stroke((52,51+p.WaistDy),(53,69),2,Skin);
        b.Rect(40,69,7,3,Edge);b.Rect(41,69,5,2,SkinLight);b.Rect(50,69,7,3,Edge);b.Rect(51,69,5,2,SkinLight);
        b.Stroke((39,p.Shoulder),(35,43),2,Skin);b.Stroke((35,43),p.Far,2,Skin);
        b.Stroke((57,p.Shoulder),(61,43),2,Skin);b.Stroke((61,43),p.Near,2,Skin);
        int waist=female?5:7;
        b.Poly(Skin,(39,p.Shoulder-1),(57,p.Shoulder-1),(48+waist,p.Waist),(55,52),(41,52),(48-waist,p.Waist));
        b.Rect(46,p.Head+11,5,p.Shoulder-p.Head-10,SkinShade);b.Rect(47,p.Head+11,3,p.Shoulder-p.Head-10,Skin);
        b.Poly(C("7D8590"),(42,p.Shoulder+4),(54,p.Shoulder+4),(48+waist,p.Waist),(48-waist,p.Waist));
        b.Line(43,p.Shoulder+5,43,p.Waist-1,C("A0A8AF"));
        b.Poly(C("687482"),(41,p.Waist),(55,p.Waist),(55,54),(49,54),(48,51),(47,54),(41,54));
        int h=p.Head;
        b.Poly(Skin,(44,h),(51,h),(54,h+3),(54,h+8),(51,h+11),(44,h+11),(41,h+8),(41,h+3));
        b.Line(43,h+3,43,h+8,SkinLight);b.Line(52,h+4,52,h+9,SkinShade);
        b.Dot(48,h+9,SkinShade);b.Dot(48,h+10,C("A76556"));
        return b;
    }
    private static Canvas Outfit(Pose p,bool female,bool indigo)
    {
        var b=new Canvas();uint cloth=indigo?C("625D87"):C("E5DDC7"),shade=indigo?C("43405F"):C("B4AB92"),
            light=indigo?C("928AAE"):C("FFF0CD"),trim=indigo?C("AEBBD2"):C("438777"),gold=indigo?C("CCD0E3"):C("D1AA63");
        b.Stroke((44,51+p.WaistDy),(43,67),3,shade);b.Stroke((52,51+p.WaistDy),(53,67),3,cloth);
        b.Line(43,55,42,65,light);b.Line(52,55,53,65,light);b.Line(41,66,45,66,trim);b.Line(51,66,55,66,trim);
        var leftCuff=(p.Far.X,p.Far.Y-2);var rightCuff=(p.Near.X,p.Near.Y-2);
        b.Stroke((39,p.Shoulder),(35,43),3,cloth);b.Stroke((35,43),leftCuff,3,cloth);
        b.Stroke((57,p.Shoulder),(61,43),3,shade);b.Stroke((61,43),rightCuff,3,cloth);
        b.Line(leftCuff.Item1-2,leftCuff.Item2,leftCuff.Item1+2,leftCuff.Item2,trim);
        b.Line(rightCuff.Item1-2,rightCuff.Item2,rightCuff.Item1+2,rightCuff.Item2,trim);
        int waist=female?6:8;
        b.Poly(cloth,(38,p.Shoulder-1),(44,p.Shoulder-2),(48,p.Shoulder),(52,p.Shoulder-2),(58,p.Shoulder-1),
            (48+waist,p.Waist),(56,56),(49,55),(48,52),(47,55),(40,56),(48-waist,p.Waist));
        b.Line(40,p.Shoulder,41,p.Waist-2,light);b.Line(54,p.Shoulder+3,55,p.Waist-1,shade);
        b.Line(43,p.Shoulder-1,49,p.Shoulder+8,trim);b.Line(53,p.Shoulder-1,47,p.Shoulder+8,trim);
        b.Line(44,p.Shoulder,49,p.Shoulder+7,light);b.Line(52,p.Shoulder,47,p.Shoulder+7,light);
        b.Rect(40,p.Waist-1,17,3,Edge);b.Rect(41,p.Waist-1,15,2,C("715342"));b.Rect(46,p.Waist-2,5,4,gold);b.Rect(47,p.Waist-1,3,2,shade);
        b.Line(48,p.Waist+2,48,p.Waist+7,gold);b.Dot(48,p.Waist+7,trim);b.Line(41,54,45,55,trim);b.Line(51,55,55,54,trim);
        return b;
    }
    private static Canvas Part(string id,Pose p)
    {
        var b=new Canvas();int h=p.Head;
        if(id.StartsWith("HAIR_",StringComparison.Ordinal))
        {
            bool knot=id=="HAIR_TOPKNOT";uint hair=knot?C("34313D"):C("654332"),high=knot?C("585362"):C("A07048");
            if(knot){b.Disc(49,h-3,3,Edge);b.Disc(49,h-3,2,hair);b.Rect(46,h-1,6,1,C("BD995D"));}
            b.Poly(hair,(43,h),(45,h-1),(51,h-1),(54,h+1),(55,h+5),(54,h+9),(52,h+5),(50,h+7),(48,h+3),(46,h+7),(44,h+5),(42,h+9),(40,h+6),(41,h+2));
            b.Line(43,h+1,46,h,high);b.Line(49,h,52,h+2,high);b.Dot(42,h+4,high);
        }
        else if(id.StartsWith("EYES_",StringComparison.Ordinal))
        {uint color=id=="EYES_JADE"?C("5CA58B"):C("C6A251");b.Rect(44,h+7,2,3,Edge);b.Rect(50,h+7,2,3,Edge);b.Dot(45,h+8,color);b.Dot(50,h+8,color);b.Dot(44,h+7,C("FFF1DE"));b.Dot(51,h+7,C("FFF1DE"));}
        else if(id.StartsWith("BOOTS_",StringComparison.Ordinal))
        {uint brown=id=="BOOTS_BROWN"?C("78583E"):C("525568"),hi=id=="BOOTS_BROWN"?C("AF8760"):C("929BB0");
         foreach(int x in new[]{40,50}){b.Rect(x,65,7,7,Edge);b.Rect(x+1,65,5,6,brown);b.Rect(x+1,66,5,1,hi);b.Rect(x+1,69,3,1,hi);b.Rect(x,71,7,1,Edge);}}
        else if(id=="HAT_TRAVELLER")
        {b.Poly(C("49546A"),(48,h-4),(35,h+4),(61,h+4));b.Line(36,h+4,60,h+4,C("D2AE63"));b.Line(47,h-3,39,h+2,C("8396A3"));b.Dot(48,h-4,C("D2AE63"));}
        else if(id=="HAT_CIRCLET")
        {b.Rect(41,h+3,14,2,C("B18C50"));b.Rect(42,h+3,12,1,C("E2C184"));b.Disc(48,h+3,2,Edge);b.Disc(48,h+3,1,C("70B5A1"));}
        else if(id.StartsWith("CAPE_",StringComparison.Ordinal))
        {uint color=id=="CAPE_JADE"?C("346C65"):C("454463");b.Poly(color,(39,p.Shoulder-1),(57,p.Shoulder-1),(60,59),(53,57),(48,60),(43,57),(36,59));b.Line(39,p.Shoulder,38,56,C("85927A"));b.Line(56,p.Shoulder,58,56,C("85927A"));}
        else if(id.StartsWith("JIAN_",StringComparison.Ordinal))
        {
            bool left=id.EndsWith("LEFT",StringComparison.Ordinal),jade=id.Contains("JADE",StringComparison.Ordinal);int d=left?-1:1,x=p.Near.X,y=p.Near.Y;
            b.Stroke((x-d*2,y-2),(x+d*2,y+2),1,C("6A4E42"));
            b.Line(x+d*2-d*2,y+2+2,x+d*2+d*2,y+2-2,C("D1AB62"),1);
            b.Line(x+d*3,y+3,x+d*12,y+14,Edge,1);
            b.Line(x+d*3,y+3,x+d*11,y+13,jade?C("75A995"):C("CFD7DF"));
            b.Line(x+d*4,y+3,x+d*12,y+13,C("F3E9CF"));
            b.Dot(x-d*2,y-2,C("D1AB62"));
        }
        return b;
    }
    private static int[] Bounds(uint[] a)
    {
        int x0=N,y0=N,x1=0,y1=0;
        for(int y=0;y<N;y++)for(int x=0;x<N;x++)if(a[y*N+x]!=0){x0=Math.Min(x0,x);y0=Math.Min(y0,y);x1=Math.Max(x1,x+1);y1=Math.Max(y1,y+1);}
        if(x1<=x0||y1<=y0)throw new Exception("empty native master pass");return new[]{x0,y0,x1-x0,y1-y0};
    }
    private static byte[] Bytes(uint[] pixels)
    {var a=new byte[pixels.Length*4];for(int i=0;i<pixels.Length;i++){uint c=pixels[i];a[i*4]=(byte)c;a[i*4+1]=(byte)(c>>8);a[i*4+2]=(byte)(c>>16);a[i*4+3]=(byte)(c>>24);}return a;}
    private static string Hash(byte[] bytes)=>Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static void Register(string id,uint[][] frames)
    {
        string path="master://"+_fingerprint+"/"+id;IdPaths[id]=path;Frames[id]=frames;
        var pixels=new uint[N*4*N*4];
        for(int i=0;i<16;i++)for(int y=0;y<N;y++)Array.Copy(frames[i],y*N,pixels,((i/4*N+y)*N*4+i%4*N),N);
        using var image=Image.CreateFromData(N*4,N*4,false,Image.Format.Rgba8,Bytes(pixels));
        Textures[path]=ImageTexture.CreateFromImage(image);
    }
    public static Texture2D? Texture(string path)=>Textures.TryGetValue(path,out var texture)?texture:null;
    public static PaperDollLabData.Catalogue CreateCatalogue()
    {
        string text=FileAccess.GetFileAsString("res://assets/paperdoll_master/master.json").Replace("\r\n","\n",StringComparison.Ordinal);
        using var doc=JsonDocument.Parse(text);var root=doc.RootElement;
        if(root.GetProperty("standingHeight").GetInt32()!=54||root.GetProperty("headHeight").GetInt32()!=12)throw new Exception("master proportion contract changed");
        var poses=root.GetProperty("poses").EnumerateArray().Select(v=>{var a=v.EnumerateArray().Select(n=>n.GetInt32()).ToArray();return new Pose(a[0],a[1],a[2],a[3],a[4],a[5],a[6]);}).ToArray();
        if(poses.Length!=16)throw new Exception("master requires sixteen authored joint poses");
        _fingerprint=Hash(Encoding.UTF8.GetBytes(FileAccess.GetFileAsString("res://scripts/RegisteredPaperDollMaster.cs").Replace("\r\n","\n",StringComparison.Ordinal)+"|"+Algorithm+"|"+text));var bodies=new List<PaperDollLabData.Body>();var parts=new List<PaperDollLabData.PartDef>();
        foreach(bool female in new[]{false,true})
        {
            string gender=female?"F":"M",id="BODY_"+gender;
            var frames=poses.Select(p=>Body(p,female).Pixels).ToArray();Register(id,frames);
            if(frames.Select(f=>Hash(Bytes(f))).Distinct(StringComparer.Ordinal).Count()!=16)throw new Exception("body source poses duplicated");
            var result=new List<PaperDollLabData.Frame>();
            for(int i=0;i<16;i++)
            {
                var bounds=Bounds(frames[i]);var anchors=poses[i].Anchors();int cellX=i%4*N,cellY=i/4*N;
                int hx=poses[i].Near.X-2,hy=poses[i].Near.Y-2;
                result.Add(new PaperDollLabData.Frame(new[]{cellX+bounds[0],cellY+bounds[1],bounds[2],bounds[3]},new[]{bounds[0],bounds[1]},anchors,Order,
                    Hash(Bytes(frames[i]).Concat(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(anchors))).ToArray()),
                    new[]{cellX+hx,cellY+hy,5,5},new[]{hx,hy}));
            }
            bodies.Add(new PaperDollLabData.Body("MK_"+gender,"Minh Kiếm · "+(female?"Nữ":"Nam")+" · master 4,5 đầu","RIG_HUMAN_"+gender+"_V2",IdPaths[id],1,result.ToArray()));
            foreach(bool indigo in new[]{false,true})
            {
                string outfit="OUTFIT_"+(indigo?"INDIGO":"IVORY")+"_"+gender;
                Register(outfit,poses.Select(p=>Outfit(p,female,indigo).Pixels).ToArray());
                AddPart(outfit,"Bộ giao lĩnh "+(indigo?"chàm":"ngà"),"outfit","canvas","OUTFIT","RIG_HUMAN_"+gender+"_V2",0);
            }
        }
        foreach(var spec in new[]{
            ("HAIR_CHESTNUT","Tóc hạt dẻ","hair_front","head","HAIR",2),("HAIR_TOPKNOT","Tóc búi","hair_front","head","HAIR",7),
            ("EYES_JADE","Mắt ngọc","eyes","face","EYES",0),("EYES_AMBER","Mắt hổ phách","eyes","face","EYES",0),
            ("BOOTS_BROWN","Hài nâu","boots","ground","BOOTS",0),("BOOTS_SILVER","Hài bạc","boots","ground","BOOTS",0),
            ("HAT_CIRCLET","Trán quan ngọc","hat_front","head","HAT",0),("HAT_TRAVELLER","Nón hành lữ","hat_front","head","HAT",0),
            ("CAPE_JADE","Choàng ngọc","cape_back","chest","CAPE",0),("CAPE_INDIGO","Choàng chàm","cape_back","chest","CAPE",0),
            ("JIAN_STEEL_LEFT","Kiếm thép · chéo trái","weapon_near","hand_near","WEAPON",0),("JIAN_JADE_LEFT","Kiếm ngọc · chéo trái","weapon_near","hand_near","WEAPON",0),
            ("JIAN_STEEL_RIGHT","Kiếm thép · chéo phải","weapon_near","hand_near","WEAPON",0),("JIAN_JADE_RIGHT","Kiếm ngọc · chéo phải","weapon_near","hand_near","WEAPON",0)})
        {
            Register(spec.Item1,poses.Select(p=>Part(spec.Item1,p).Pixels).ToArray());
            AddPart(spec.Item1,spec.Item2,spec.Item3,spec.Item4,spec.Item5,null,spec.Item6);
        }
        return new PaperDollLabData.Catalogue(2,"FIT_LAB_ONLY",false,new[]{N,N},new[]{48,72},"S","idle",1.6,16,
            Array.Empty<PaperDollLabData.Source>(),bodies.ToArray(),parts.ToArray(),_fingerprint);

        void AddPart(string id,string name,string slot,string anchor,string category,string? rig,int clip)
        {
            var regions=new int[16][];var transforms=new PaintTransform[16];
            for(int i=0;i<16;i++)
            {
                var bb=Bounds(Frames[id][i]);regions[i]=new[]{i%4*N+bb[0],i/4*N+bb[1],bb[2],bb[3]};var a=poses[i].Anchors()[anchor];
                transforms[i]=new PaintTransform(a[0]-bb[0],a[1]-bb[1],0,1);
            }
            // Glyph reuse and per-pose deformation are distinct; report actual full-source variants honestly.
            int unique=Frames[id].Select(f=>Hash(Bytes(f))).Distinct(StringComparer.Ordinal).Count();
            parts.Add(new PaperDollLabData.PartDef(id,name,slot,anchor,category,regions[0],new[]{0,0},IdPaths[id],1,
                Array.Empty<string>(),unique,false,rig,transforms[0],clip,regions,transforms));
        }
    }
    public static int UncoveredBaseGarmentPixels(string body,string outfit,int frame)
    {var b=Frames[body=="MK_M"?"BODY_M":"BODY_F"][frame];var o=Frames[outfit][frame];var coverage=new[]{C("7D8590"),C("A0A8AF"),C("687482")};return Enumerable.Range(0,b.Length).Count(i=>coverage.Contains(b[i])&&o[i]==0);}
    public static void ExportSources(string folder)
    {
        System.IO.Directory.CreateDirectory(folder);var files=new List<object>();
        foreach(string sex in new[]{"M","F"})
        {
            var layers=new List<(string Name,bool Visible,uint[][] Frames)>();
            void Add(string name,bool visible,string id)=>layers.Add((name,visible,Frames[id]));
            Add("CAPE_JADE",false,"CAPE_JADE");Add("CAPE_INDIGO",false,"CAPE_INDIGO");
            Add("BODY_BASE",true,"BODY_"+sex);Add("OUTFIT_IVORY",true,"OUTFIT_IVORY_"+sex);Add("OUTFIT_INDIGO",false,"OUTFIT_INDIGO_"+sex);
            Add("BOOTS_BROWN",true,"BOOTS_BROWN");Add("BOOTS_SILVER",false,"BOOTS_SILVER");
            foreach(string id in new[]{"JIAN_STEEL_LEFT","JIAN_JADE_LEFT","JIAN_STEEL_RIGHT","JIAN_JADE_RIGHT"})Add(id,id=="JIAN_STEEL_RIGHT",id);
            var hands=Frames["BODY_"+sex].Select(pixels=>{
                var a=new uint[N*N]; // Hand positions are recovered from the registered body's cel metadata.
                return a;
            }).ToArray();
            using(var document=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/paperdoll_master/master.json")))
            {
                int i=0;foreach(var v in document.RootElement.GetProperty("poses").EnumerateArray())
                {int x=62+v[0].GetInt32()-2,y=51+v[1].GetInt32()-2;for(int yy=y;yy<y+5;yy++)for(int xx=x;xx<x+5;xx++)hands[i][yy*N+xx]=Frames["BODY_"+sex][i][yy*N+xx];i++;}
            }
            layers.Add(("HAND_NEAR",true,hands));
            Add("EYES_JADE",true,"EYES_JADE");Add("EYES_AMBER",false,"EYES_AMBER");
            Add("HAIR_CHESTNUT",true,"HAIR_CHESTNUT");Add("HAIR_TOPKNOT",false,"HAIR_TOPKNOT");
            foreach(var (id,clip) in new[]{("HAIR_CHESTNUT",2),("HAIR_TOPKNOT",7)})
            {
                var covered=Frames[id].Select(pixels=>{var a=pixels.ToArray();int top=Bounds(a)[1]+clip;for(int y=0;y<top;y++)Array.Clear(a,y*N,N);return a;}).ToArray();
                layers.Add((id+"_UNDER_HAT",false,covered));
            }
            Add("HAT_TRAVELLER",false,"HAT_TRAVELLER");Add("HAT_CIRCLET",false,"HAT_CIRCLET");
            using var all=new System.IO.MemoryStream();using var output=new System.IO.BinaryWriter(all,Encoding.UTF8,true);
            output.Write(new byte[128]);
            for(int frame=0;frame<16;frame++)
            {
                var chunks=new List<byte[]>();
                if(frame==0)
                {
                    foreach(var layer in layers)chunks.Add(Chunk(0x2004,w=>{
                        w.Write((ushort)(layer.Visible?3:2));for(int j=0;j<5;j++)w.Write((ushort)0);
                        w.Write((byte)255);w.Write(new byte[3]);String(w,layer.Name);
                    }));
                    chunks.Add(Chunk(0x2018,w=>{w.Write((ushort)1);w.Write(new byte[8]);w.Write((ushort)0);w.Write((ushort)15);w.Write((byte)0);w.Write((ushort)0);w.Write(new byte[6]);w.Write(new byte[3]);w.Write((byte)0);String(w,"IDLE_S_16_MASTER");}));
                }
                for(int layer=0;layer<layers.Count;layer++)
                {
                    int index=layer;
                    chunks.Add(Chunk(0x2005,w=>{
                        w.Write((ushort)index);w.Write((short)0);w.Write((short)0);w.Write((byte)255);w.Write((ushort)2);w.Write((short)0);w.Write(new byte[5]);w.Write((ushort)N);w.Write((ushort)N);
                        using var compressed=new System.IO.MemoryStream();using(var z=new System.IO.Compression.ZLibStream(compressed,System.IO.Compression.CompressionLevel.SmallestSize,true))z.Write(Bytes(layers[index].Frames[frame]));
                        w.Write(compressed.ToArray());
                    }));
                }
                output.Write((uint)(16+chunks.Sum(c=>c.Length)));output.Write((ushort)0xF1FA);output.Write((ushort)chunks.Count);output.Write((ushort)100);output.Write((ushort)0);output.Write((uint)chunks.Count);
                foreach(var chunk in chunks)output.Write(chunk);
            }
            long size=all.Length;all.Position=0;
            output.Write((uint)size);output.Write((ushort)0xA5E0);output.Write((ushort)16);output.Write((ushort)N);output.Write((ushort)N);output.Write((ushort)32);output.Write((uint)1);output.Write((ushort)100);
            output.Write(new byte[8]);output.Write((byte)0);output.Write(new byte[3]);output.Write((ushort)0);output.Write((byte)1);output.Write((byte)1);output.Write((short)0);output.Write((short)0);output.Write((ushort)1);output.Write((ushort)1);output.Write(new byte[84]);
            string name="minh_kiem_"+sex.ToLowerInvariant()+"_registered_master.aseprite";byte[] file=all.ToArray();System.IO.File.WriteAllBytes(System.IO.Path.Combine(folder,name),file);
            var reference=new List<string>();for(int frame=0;frame<16;frame++)
            {var rgba=new uint[N*N];foreach(var layer in layers.Where(l=>l.Visible))for(int i=0;i<rgba.Length;i++)if(layer.Frames[frame][i]!=0)rgba[i]=layer.Frames[frame][i];reference.Add(Hash(Bytes(rgba)));}
            files.Add(new{file=name,sha256=Hash(file),frames=16,layers=layers.Count,visibleLayers=layers.Where(l=>l.Visible).Select(l=>l.Name).ToArray(),referenceRgbaSha256=reference});
        }
        var manifest=new{kind="REGISTERED_MASTER_SOURCE_PROOF_NOT_APPROVED_ART",rigVersion=2,sourceFingerprint=_fingerprint,canvas=new[]{N,N},standingHeight=54,headHeight=12,productionApproved=false,files};
        System.IO.File.WriteAllText(System.IO.Path.Combine(folder,"source_manifest.json"),JsonSerializer.Serialize(manifest,new JsonSerializerOptions{WriteIndented=true})+"\n",new UTF8Encoding(false));
    }
    private static byte[] Chunk(ushort type,Action<System.IO.BinaryWriter> write)
    {using var data=new System.IO.MemoryStream();using var w=new System.IO.BinaryWriter(data,Encoding.UTF8,true);w.Write((uint)0);w.Write(type);write(w);long size=data.Length;data.Position=0;w.Write((uint)size);return data.ToArray();}
    private static void String(System.IO.BinaryWriter writer,string text)
    {byte[] bytes=Encoding.UTF8.GetBytes(text);writer.Write((ushort)bytes.Length);writer.Write(bytes);}

    /// <summary>Compare a monolithic reference assembled directly from master layers with the
    /// atlas regions and transforms emitted by the paper-doll compiler, pixel for pixel.</summary>
    public static int RegistrationMismatch(PaperDollLabData data,string body,string[] selected,int frame)
    {
        var expected=new uint[N*N];var ids=new Dictionary<string,string>{{"body",body=="MK_M"?"BODY_M":"BODY_F"},{"hand_near",body=="MK_M"?"BODY_M":"BODY_F"}};
        foreach(string id in selected)ids[data.FindPart(id).Slot]=id;
        foreach(string slot in data.Order(body,frame))
        {
            if(!ids.TryGetValue(slot,out string? id))continue;var pixels=Frames[id][frame];
            int top=0;if(slot=="hair_front"&&selected.Contains("HAT_TRAVELLER",StringComparer.Ordinal))top=Bounds(pixels)[1]+data.FindPart(id).HeadCoverClipTopPixels;
            var f=data.FindBody(body).Frames[frame];int handX=f.Anchors["hand_near"][0]-2,handY=f.Anchors["hand_near"][1]-2;
            for(int y=0;y<N;y++)for(int x=0;x<N;x++)
            {
                if(slot=="hand_near"&&(x<handX||x>=handX+5||y<handY||y>=handY+5))continue;
                if(slot=="hair_front"&&y<top)continue;uint c=pixels[y*N+x];if(c!=0)expected[y*N+x]=c;
            }
        }
        if(!TryCompile(data.Build(body,selected,1),true,out var look,out var reason))throw new Exception(reason);
        var actual=new uint[N*N];
        foreach(var command in look!.Clips["idle/S"].Frames[frame])
        {
            string id=IdPaths.Single(p=>p.Value==command.Texture).Key;var pixels=Frames[id][frame];var t=command.Transform??Identity;
            if(t.Scale!=1||t.Degrees!=0||t.FlipH||t.FlipV)throw new Exception("reference comparison requires default master transform");
            for(int y=0;y<command.Region.Height;y++)for(int x=0;x<command.Region.Width;x++)
            {
                int sx=command.Region.X%N+x,sy=command.Region.Y%N+y;uint c=pixels[sy*N+sx];if(c==0)continue;
                var point=ToActor(command,x,y);int dx=(int)Math.Round(point.X+48),dy=(int)Math.Round(point.Y+72);
                if(dx<0||dy<0||dx>=N||dy>=N)throw new Exception("registered pixel outside canvas");actual[dy*N+dx]=c;
            }
        }
        return expected.Zip(actual).Count(p=>p.First!=p.Second);
    }
}
