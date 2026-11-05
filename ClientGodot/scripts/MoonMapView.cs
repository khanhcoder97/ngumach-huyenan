#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Cartography from authored layout plus authoritative live actor positions.
/// The painted art layout is not used as a server navigation graph.</summary>
public partial class MoonMapView : Control
{
    public NativeOnlineFrame? Frame;
    public bool Overview;
    public Vector2 Facing=Vector2.Up;
    private JsonDocument? _layout;
    public override void _Ready(){ClipContents=true;MouseFilter=MouseFilterEnum.Ignore;_layout=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/ben_mua_v3/layout.json"));QueueRedraw();}
    private double _refresh;
    public override void _Process(double delta){_refresh+=delta;if(_refresh>=.2){_refresh=0;QueueRedraw();}}
    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero,Size),new Color(.13f,.16f,.28f,.94f));
        if(_layout==null)return;
        var self=Frame?.World?.self;
        Vector2 center=Overview?new Vector2(38,1):self!=null?new Vector2((float)self.x,(float)self.y):new Vector2(36,0);
        var span=Overview?new Vector2(110,62):new Vector2(75,48);
        float sx=Size.X/span.X,sy=Size.Y/span.Y;
        Vector2 Point(Vector2 p)=>Size/2+new Vector2((p.X-center.X)*sx,-(p.Y-center.Y)*sy);
        Vector2 Art(JsonElement p)=>NativeActorsView.WorldPoint(new Vector2(640+p[0].GetSingle(),536+p[1].GetSingle()));
        for(int i=0;i<12;i++){float x=i*Size.X/11;DrawLine(new Vector2(x,0),new Vector2(x,Size.Y),new Color(.58f,.64f,.84f,.045f));}
        var river=_layout.RootElement.GetProperty("river");
        var upper=river.GetProperty("upper").EnumerateArray().Select(p=>Point(Art(p))).ToArray();
        var lower=river.GetProperty("lower").EnumerateArray().Select(p=>Point(Art(p))).Reverse().ToArray();
        DrawColoredPolygon(upper.Concat(lower).ToArray(),new Color(.27f,.53f,.65f,.8f));
        DrawPolyline(upper,new Color(.57f,.8f,.87f,.65f),1.2f,true);
        if(_layout.RootElement.TryGetProperty("roads",out var roads))
        foreach(var road in roads.EnumerateArray())
        {
            if(!road.TryGetProperty("points",out var points))continue;
            var path=points.EnumerateArray().Select(p=>Point(Art(p))).ToArray();
            if(path.Length>1)DrawPolyline(path,new Color(.79f,.74f,.72f,.72f),Overview?3:2,true);
        }
        foreach(var p in _layout.RootElement.GetProperty("placements").EnumerateArray())
        {
            string key=p.GetProperty("asset").GetString()!;
            if(key is not("hall" or "townhouse" or "cottage" or "workshop"))continue;
            var at=Point(Art(p.GetProperty("at")));float w=Math.Clamp(p.GetProperty("width").GetSingle()/20*sx*.65f,4,18);
            DrawRect(new Rect2(at-new Vector2(w/2,6),new Vector2(w,7)),new Color(.63f,.61f,.82f,.65f));
        }
        if(Frame?.World is {} world)
        foreach(var e in world.entities)
        {
            var at=Point(new Vector2((float)e.x,(float)e.y));
            if(!new Rect2(Vector2.One*4,Size-Vector2.One*8).HasPoint(at))continue;
            if(e.kind=="NPC")DrawCircle(at,Overview?3.5f:2.4f,MoonGlassTheme.Gold);
            else if(e.kind=="INTERACTABLE"&&e.state!="DEPLETED")
                DrawPolyline(new[]{at+new Vector2(0,-4),at+new Vector2(3,0),at+new Vector2(0,4),at+new Vector2(-3,0),at+new Vector2(0,-4)},MoonGlassTheme.Violet,1.2f);
            else if(e.targetable==true)DrawCircle(at,2,Color.FromHtml("#ee8ba4"));
        }
        var player=self!=null?Point(new Vector2((float)self.x,(float)self.y)):Point(new Vector2(36,0));
        DrawCircle(player,7,new Color(.65f,.8f,1,.15f));DrawCircle(player,3.1f,Colors.White);
        var face=Facing==Vector2.Zero?Vector2.Up:Facing.Normalized();
        DrawColoredPolygon(new[]{player+face*9,player+face.Rotated(2.4f)*3,player+face.Rotated(-2.4f)*3},MoonGlassTheme.Blue);
    }
    public override void _ExitTree()=>_layout?.Dispose();
}
