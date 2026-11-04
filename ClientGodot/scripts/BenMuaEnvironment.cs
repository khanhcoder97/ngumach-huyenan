using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Hand-authored district from the approved concept. Every building is placed by ID.
/// Terrain is layered geometry + standalone textures, not a flattened concept image.
/// This staging layout does not migrate canonical server navigation or NPC coordinates.</summary>
public partial class BenMuaEnvironment : Node2D
{
    private const string Root = "res://assets/ben_mua_v3/";
    public readonly Vector2 DistrictOrigin = new(640,536);
    public readonly Vector2 MapPixels = new(2560,1920);
    public Vector2 Spawn => DistrictOrigin + new Vector2(640,360);
    public readonly List<Rect2> SolidFootprints = new();
    public readonly List<Rect2> Piers = new();
    private readonly Dictionary<string,Texture2D> _textures = new();
    private readonly Dictionary<int,ShaderMaterial> _materials = new();
    private readonly List<(Sprite2D Sprite,Rect2 Bounds,Vector2 Foot)> _occluders = new();
    private JsonDocument _layout = null!, _assets = null!;
    private Vector2[] _upper = null!, _lower = null!, _water = null!;
    private Node2D _actors = null!, _shadows = null!;
    public int AuthoredPlacementCount { get; private set; }
    public int ShoreDetailCount { get; private set; }
    public Vector2[] WaterPolygon => _water;
    public Vector2 World(Vector2 local) => DistrictOrigin + local;

    public void Build(Node2D actors)
    {
        Name="BenMuaAuthoredEnvironment";
        _actors=actors;
        _layout=JsonDocument.Parse(FileAccess.GetFileAsString(Root+"layout.json"));
        _assets=JsonDocument.Parse(FileAccess.GetFileAsString(Root+"asset_manifest.json"));
        _upper=Smooth(ReadPoints(_layout.RootElement.GetProperty("river").GetProperty("upper")),12);
        _lower=Smooth(ReadPoints(_layout.RootElement.GetProperty("river").GetProperty("lower")),12);
        _water=_upper.Concat(_lower.Reverse()).ToArray();
        _shadows=new Node2D{Name="GroundShadows",ZIndex=-1};
        AddChild(_shadows);
        BuildGround();
        foreach(var item in _layout.RootElement.GetProperty("placements").EnumerateArray())
        {
            var at=ReadVector(item.GetProperty("at"));
            string key=item.GetProperty("asset").GetString()!;
            float width=item.GetProperty("width").GetSingle();
            bool solid=item.TryGetProperty("solid",out var s)&&s.GetBoolean();
            bool pier=item.TryGetProperty("pier",out var p)&&p.GetBoolean();
            float? height=item.TryGetProperty("height",out var h)?h.GetSingle():null;
            var sprite=Place(key,World(at),width,item.GetProperty("id").GetString()!,height);
            if(item.TryGetProperty("rotation",out var rotation)) sprite.Rotation=rotation.GetSingle();
            if(solid||pier)
            {
                var footprint=item.TryGetProperty("footprint",out var fp)
                    ?new Rect2(fp[0].GetSingle(),fp[1].GetSingle(),fp[2].GetSingle(),fp[3].GetSingle())
                    :new Rect2(-width*.34f,-width*.24f,width*.68f,width*.22f);
                footprint.Position+=World(at);
                if(pier) Piers.Add(footprint);
                else {SolidFootprints.Add(footprint);AddRectangleBody(footprint);}
            }
            if(key is "banyan" or "canopy" or "willow" or "bamboo")
            {
                var trunk=new Rect2(World(at)+new Vector2(-5,-8),new Vector2(10,8));
                SolidFootprints.Add(trunk);AddRectangleBody(trunk);
            }
            AuthoredPlacementCount++;
        }
        BuildShoreDetails();
        BuildWaterCollision();
        AddRectangleBody(new Rect2(-20,-20,20,MapPixels.Y+40));
        AddRectangleBody(new Rect2(MapPixels.X,-20,20,MapPixels.Y+40));
        AddRectangleBody(new Rect2(0,-20,MapPixels.X,20));
        AddRectangleBody(new Rect2(0,MapPixels.Y,MapPixels.X,20));
    }

    private Texture2D Texture(string file)
    {
        if(!_textures.TryGetValue(file,out var texture))
        { texture=GD.Load<Texture2D>(Root+file);_textures.Add(file,texture); }
        return texture;
    }

    private ShaderMaterial GroundMaterial(int tile)
    {
        if(!_materials.TryGetValue(tile,out var material))
        {
            material=new ShaderMaterial{Shader=GD.Load<Shader>("res://shaders/terrain_repeat.gdshader")};
            material.SetShaderParameter("terrain_atlas",Texture("ground.png"));
            material.SetShaderParameter("atlas_cell",new Vector2(tile%3,tile/3));
            material.SetShaderParameter("world_period",tile==2?128f:160f);
            _materials.Add(tile,material);
        }
        return material;
    }

    private void Surface(Vector2[] polygon,int tile,string name)
    {
        var surface=new Polygon2D{Name=name,Polygon=polygon,Material=GroundMaterial(tile)};
        AddChild(surface);
        // Ground stays behind the shadow and actor layers regardless of creation order.
        surface.ZIndex=-10;
    }

    private void BuildGround()
    {
        // Chunked TileMapLayer base; shader uses world pixel coordinates for continuous repeats.
        var source=new TileSetAtlasSource{Texture=Texture("ground.png"),TextureRegionSize=new Vector2I(512,512)};
        for(int y=0;y<2;y++)for(int x=0;x<3;x++)source.CreateTile(new Vector2I(x,y));
        var tiles=new TileSet{TileSize=new Vector2I(512,512)};tiles.AddSource(source,0);
        var ground=new TileMapLayer{Name="BaseGrassTiles",TileSet=tiles,Scale=Vector2.One*.25f,
            Material=GroundMaterial(0),ZIndex=-20};
        AddChild(ground);
        for(int y=0;y<15;y++)for(int x=0;x<20;x++)ground.SetCell(new Vector2I(x,y),0,Vector2I.Zero);
        // Subtle damp meadow patches beneath the tree clusters.
        foreach(var item in _layout.RootElement.GetProperty("placements").EnumerateArray())
        {
            var key=item.GetProperty("asset").GetString();
            if(key is "banyan" or "canopy" or "willow" or "bamboo")
            {
                var at=World(ReadVector(item.GetProperty("at")));
                float radius=item.GetProperty("width").GetSingle()*.47f;
                Surface(OrganicOval(at+new Vector2(0,-12),new Vector2(radius,radius*.43f),7),4,"MossPatch");
            }
        }
        // A narrow earth bank under the river surface, rather than a straight blue band.
        var sand=_upper.Select(p=>p+new Vector2(0,-5)).Concat(_lower.Reverse().Select(p=>p+new Vector2(0,5))).ToArray();
        Surface(sand,1,"RiverSilt");
        Surface(_water,3,"JadeRiver");
        foreach(var road in _layout.RootElement.GetProperty("roads").EnumerateArray())
        {
            var points=Smooth(ReadPoints(road.GetProperty("points")),8);
            float width=road.GetProperty("width").GetSingle();
            string name=road.GetProperty("id").GetString()!;
            Surface(Ribbon(points,width+7,3),1,name+"_Verge");
            Surface(Ribbon(points,width,2),road.GetProperty("tile").GetInt32(),name);
        }
        foreach(var item in _layout.RootElement.GetProperty("placements").EnumerateArray())
        {
            if(!item.TryGetProperty("solid",out var solid)||!solid.GetBoolean())continue;
            string key=item.GetProperty("asset").GetString()!;
            if(key is "well" or "jars")continue;
            var at=World(ReadVector(item.GetProperty("at")));
            float width=item.GetProperty("width").GetSingle();
            Surface(OrganicOval(at+new Vector2(0,-5),new Vector2(width*.56f,width*.22f),4),1,"Courtyard_"+key);
        }
        // Fenced rice gardens on the far bank; world continues beyond this viewport.
        Surface(new[]{World(new Vector2(925,640)),World(new Vector2(1278,551)),World(new Vector2(1430,700)),
            World(new Vector2(1030,801))},5,"FarBankRiceField");
    }

    private static Vector2[] OrganicOval(Vector2 center,Vector2 radius,int seed)
    {
        var points=new Vector2[24];
        for(int i=0;i<points.Length;i++)
        {float a=i*Mathf.Tau/points.Length;float k=1+.05f*Mathf.Sin(i*2.7f+seed);points[i]=(center+new Vector2(Mathf.Cos(a)*radius.X*k,Mathf.Sin(a)*radius.Y*k)).Round();}
        return points;
    }

    private static Vector2[] Ribbon(Vector2[] points,float width,int seed)
    {
        var left=new List<Vector2>();var right=new List<Vector2>();
        for(int i=0;i<points.Length;i++)
        {
            var tangent=points[Math.Min(i+1,points.Length-1)]-points[Math.Max(i-1,0)];
            var normal=new Vector2(-tangent.Y,tangent.X).Normalized();
            float half=width*.5f*(1+.09f*Mathf.Sin(i*.79f+seed));
            float jitter=1.5f*Mathf.Sin(i*2.3f+seed);
            left.Add((points[i]+normal*(half+jitter)).Round());
            right.Add((points[i]-normal*(half-jitter)).Round());
        }
        right.Reverse();return left.Concat(right).ToArray();
    }

    private Vector2[] ReadPoints(JsonElement source)=>source.EnumerateArray().Select(p=>World(ReadVector(p))).ToArray();
    private static Vector2 ReadVector(JsonElement v)=>new(v[0].GetSingle(),v[1].GetSingle());
    private static Vector2[] Smooth(Vector2[] points,float step)
    {
        var result=new List<Vector2>();
        for(int i=0;i<points.Length-1;i++)
        {
            var p0=points[Math.Max(i-1,0)];var p1=points[i];var p2=points[i+1];var p3=points[Math.Min(i+2,points.Length-1)];
            int count=Math.Max(2,(int)(p1.DistanceTo(p2)/step));
            for(int k=0;k<count;k++)
            {
                float t=k/(float)count,t2=t*t,t3=t2*t;
                result.Add((.5f*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3)).Round());
            }
        }
        result.Add(points[^1]);return result.ToArray();
    }

    private Sprite2D Place(string key,Vector2 position,float width,string name,float? height=null)
    {
        var asset=_assets.RootElement.GetProperty("assets").GetProperty(key);
        var rect=asset.GetProperty("rect");var bounds=asset.GetProperty("contentBounds");var pivot=asset.GetProperty("pivot");
        var region=new Rect2(rect[0].GetSingle(),rect[1].GetSingle(),rect[2].GetSingle(),rect[3].GetSingle());
        float contentWidth=bounds[2].GetSingle()-bounds[0].GetSingle();
        float contentHeight=bounds[3].GetSingle()-bounds[1].GetSingle();
        float scale=height.HasValue?height.Value/contentHeight:width/contentWidth;
        var texture=new AtlasTexture{Atlas=Texture(asset.GetProperty("file").GetString()!),Region=region,FilterClip=true};
        var offset=-new Vector2(pivot[0].GetSingle(),pivot[1].GetSingle());
        var sprite=new Sprite2D{Name=name,Texture=texture,Centered=false,Offset=offset,Position=position.Round(),Scale=Vector2.One*scale};
        _actors.AddChild(sprite);
        bool tall=key is "banyan" or "canopy" or "willow" or "bamboo" or "hall" or "townhouse" or "cottage" or "workshop";
        if(tall)
        {
            var shadow=new Sprite2D{Texture=texture,Centered=false,Offset=offset,Position=position+new Vector2(7,4),
                Scale=new Vector2(scale,scale*.16f),Modulate=new Color(.12f,.18f,.07f,.24f)};
            _shadows.AddChild(shadow);
            _occluders.Add((sprite,new Rect2(position+new Vector2(-contentWidth*scale/2,-contentHeight*scale),
                new Vector2(contentWidth*scale,contentHeight*scale)),position));
        }
        return sprite;
    }

    public void UpdateOcclusion(Vector2 player)
    {
        foreach(var entry in _occluders)
        {
            bool hiding=entry.Bounds.Grow(6).HasPoint(player+new Vector2(0,-16))&&player.Y<entry.Foot.Y-8;
            entry.Sprite.Modulate=new Color(1,1,1,hiding?.48f:1f);
        }
    }

    private static float BankAt(Vector2[] bank,float x)
    {
        for(int i=1;i<bank.Length;i++)
            if(bank[i].X>=x)
            {float t=(x-bank[i-1].X)/Math.Max(1,bank[i].X-bank[i-1].X);return Mathf.Lerp(bank[i-1].Y,bank[i].Y,t);}
        return bank[^1].Y;
    }

    private void BuildShoreDetails()
    {
        for(int side=0;side<2;side++)
        {
            var bank=side==0?_upper:_lower;
            for(int i=0;i<51;i++)
            {
                float x=20+i*50+5*Mathf.Sin(i*2.4f+side);float y=BankAt(bank,x)+2*Mathf.Sin(i*1.7f);
                var at=new Vector2(x,y+(side==0?5:-2));
                if(Piers.Any(r=>r.Grow(27).HasPoint(at)))continue;
                var rock=Place("rocks",at,57+(i*13%43),"ART_SHORE_"+side+"_"+i);
                rock.FlipH=(i%2)==0;
                ShoreDetailCount++;
                if(i%3!=1)
                {
                    Place(i%3==0?"reeds":"flowers",at+new Vector2(17,side==0?-8:24),i%3==0?43:27,
                        "ART_BANK_PLANT_"+side+"_"+i);
                    ShoreDetailCount++;
                }
            }
        }
    }

    private void AddRectangleBody(Rect2 rect)
    {
        var body=new StaticBody2D{Position=rect.GetCenter(),CollisionLayer=1};
        body.AddChild(new CollisionShape2D{Shape=new RectangleShape2D{Size=rect.Size}});AddChild(body);
    }

    private void BuildWaterCollision()
    {
        var parts=new List<Vector2[]>{_water};
        foreach(var pier in Piers)
        {
            var cut=new[]{pier.Position,pier.Position+new Vector2(pier.Size.X,0),pier.End,pier.Position+new Vector2(0,pier.Size.Y)};
            parts=parts.SelectMany(poly=>Geometry2D.ClipPolygons(poly,cut)).ToList();
        }
        foreach(var poly in parts)
        {
            var body=new StaticBody2D{CollisionLayer=1,Name="RiverCollision"};
            body.AddChild(new CollisionPolygon2D{Polygon=poly});AddChild(body);
        }
    }

    public bool IsWalkable(Vector2 point)
    {
        if(point.X<6||point.Y<6||point.X>MapPixels.X-6||point.Y>MapPixels.Y-6)return false;
        if(SolidFootprints.Any(r=>r.Grow(5).HasPoint(point)))return false;
        bool WaterAt(Vector2 p)=>Geometry2D.IsPointInPolygon(p,_water)&&!Piers.Any(r=>r.HasPoint(p));
        return !WaterAt(point)&&!WaterAt(point+new Vector2(5,0))&&!WaterAt(point-new Vector2(5,0))
            &&!WaterAt(point+new Vector2(0,5))&&!WaterAt(point-new Vector2(0,5));
    }

    public HashSet<Vector2I> Reachable(Vector2 start)
    {
        const int step=16;
        var found=new HashSet<Vector2I>();var queue=new Queue<Vector2I>();
        var first=new Vector2I(Mathf.RoundToInt(start.X/step),Mathf.RoundToInt(start.Y/step));
        found.Add(first);queue.Enqueue(first);
        var delta=new[]{Vector2I.Left,Vector2I.Right,Vector2I.Up,Vector2I.Down};
        while(queue.Count>0)
        {
            var current=queue.Dequeue();
            foreach(var d in delta)
            {
                var next=current+d;
                if(found.Contains(next)||!IsWalkable(new Vector2(next.X*step,next.Y*step)))continue;
                found.Add(next);queue.Enqueue(next);
            }
        }
        return found;
    }

    public override void _ExitTree(){_layout?.Dispose();_assets?.Dispose();}
}
