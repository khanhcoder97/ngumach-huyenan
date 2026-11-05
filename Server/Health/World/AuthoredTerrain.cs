using System.Text.Json;
namespace Server.Health.World;

/// <summary>Shared authored district collision. Loaded only by hosts supplying the matching content file.</summary>
public sealed class AuthoredTerrain
{
    public sealed record Rect(string Id,double X,double Y,double W,double H)
    {public bool Contains(double x,double y)=>x>=X&&x<=X+W&&y>=Y&&y<=Y+H;}
    public string MapId {get;}
    public IReadOnlyList<TopologyPoint> Water {get;}
    public IReadOnlyList<Rect> Solids {get;}
    public IReadOnlyList<Rect> Decks {get;}
    public AuthoredTerrain(string path)
    {
        using var json=JsonDocument.Parse(File.ReadAllText(path));var root=json.RootElement;
        if(root.GetProperty("schemaVersion").GetInt32()!=1||root.GetProperty("coordinateSystem").GetString()!="CANONICAL_XY_WU")throw new InvalidDataException("Unsupported authored terrain");
        MapId=root.GetProperty("mapId").GetString()!;
        Water=root.GetProperty("water").EnumerateArray().Select(p=>new TopologyPoint(p[0].GetDouble(),p[1].GetDouble())).ToArray();
        Rect[] Read(string name)=>root.GetProperty(name).EnumerateArray().Select(e=>{var r=e.GetProperty("rect");return new Rect(e.GetProperty("id").GetString()!,r[0].GetDouble(),r[1].GetDouble(),r[2].GetDouble(),r[3].GetDouble());}).ToArray();
        Solids=Read("solids");Decks=Read("decks");
        if(Water.Count<3||Solids.Count==0||Decks.Count==0||Water.Any(p=>!double.IsFinite(p.X)||!double.IsFinite(p.Y))||Solids.Concat(Decks).Any(r=>!double.IsFinite(r.X+r.Y+r.W+r.H)||r.W<=0||r.H<=0))throw new InvalidDataException("Invalid terrain geometry");
    }
    private bool WaterAt(double x,double y)=>GeometryMath.PointInPolygon(Water,x,y)&&!Decks.Any(d=>d.Contains(x,y));
    public bool Walkable(double x,double y,double radius)
    {
        if(!double.IsFinite(x)||!double.IsFinite(y)||!double.IsFinite(radius)||radius<0)return false;
        foreach(var r in Solids)
        {
            double dx=x-Math.Clamp(x,r.X,r.X+r.W),dy=y-Math.Clamp(y,r.Y,r.Y+r.H);
            if(r.Contains(x,y)||dx*dx+dy*dy<radius*radius-1e-9)return false;
        }
        if(WaterAt(x,y))return false;
        for(int i=0;i<16&&radius>0;i++){double a=i*Math.PI/8;if(WaterAt(x+Math.Cos(a)*radius,y+Math.Sin(a)*radius))return false;}
        return true;
    }
    public LineOfSightResult Walk(double ax,double ay,double bx,double by,double radius)
    {
        if(!double.IsFinite(ax+ay+bx+by+radius)||radius<0)return new(LineOfSightStatus.Blocked,"invalid_authored_move");
        int steps=Math.Max(1,(int)Math.Ceiling(Math.Sqrt((bx-ax)*(bx-ax)+(by-ay)*(by-ay))/.1));
        if(steps>10000)return new(LineOfSightStatus.Blocked,"authored_move_too_long");
        for(int i=0;i<=steps;i++){double t=i/(double)steps;if(!Walkable(ax+(bx-ax)*t,ay+(by-ay)*t,radius))return new(LineOfSightStatus.Blocked,"authored_terrain");}
        return new(LineOfSightStatus.Allowed,null);
    }
    public LineOfSightResult Sight(double ax,double ay,double bx,double by)
    {
        if(!double.IsFinite(ax+ay+bx+by))return new(LineOfSightStatus.Blocked,"nonfinite");
        foreach(var r in Solids.Where(r=>!r.Id.EndsWith("_TRUNK",StringComparison.Ordinal)))
        {
            TopologyPoint[] points={new(r.X,r.Y),new(r.X+r.W,r.Y),new(r.X+r.W,r.Y+r.H),new(r.X,r.Y+r.H)};
            if(r.Contains(ax,ay)||r.Contains(bx,by)||GeometryMath.SegmentIntersectsPolygon(points,ax,ay,bx,by))return new(LineOfSightStatus.Blocked,"authored_building");
        }
        return new(LineOfSightStatus.Allowed,null);
    }
}

public sealed class AuthoredWorldGeometry : IWorldGeometryService
{
    private readonly IWorldGeometryService _fallback;
    private readonly AuthoredTerrain _terrain;
    public AuthoredWorldGeometry(IWorldGeometryService fallback,AuthoredTerrain terrain){_fallback=fallback;_terrain=terrain;}
    public LineOfSightResult CheckLineOfSight(string mapId,string floorId,double ax,double ay,double bx,double by)=>
        mapId==_terrain.MapId?(floorId=="OVERWORLD"?_terrain.Sight(ax,ay,bx,by):new(LineOfSightStatus.Blocked,"floor")):_fallback.CheckLineOfSight(mapId,floorId,ax,ay,bx,by);
    public LineOfSightResult CheckWalkSegment(string mapId,string floorId,double ax,double ay,double bx,double by,double radius)=>
        mapId==_terrain.MapId?(floorId=="OVERWORLD"?_terrain.Walk(ax,ay,bx,by,radius):new(LineOfSightStatus.Blocked,"floor")):_fallback.CheckWalkSegment(mapId,floorId,ax,ay,bx,by,radius);
}
