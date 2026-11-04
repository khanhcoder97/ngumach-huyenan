#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using NguMach.Client.P1;

namespace Ngumach.VisualReboot;

/// <summary>Server entity projection only. Coordinates/life/HP are never simulated here.
/// Assets supply appearance; no decorative actor is promoted to an authoritative NPC.</summary>
public partial class NativeActorsView : Node2D
{
    private sealed class ActorVisual
    {
        public Node2D Root=null!;
        public Sprite2D Body=null!;
        public Label Name=null!;
        public Label Health=null!;
        public Polygon2D Bar=null!,Track=null!;
        public string SpriteKey="";
    }

    private readonly Dictionary<string,ActorVisual> _actors=new(StringComparer.Ordinal);
    private readonly Dictionary<string,Texture2D> _textures=new(StringComparer.Ordinal);
    private readonly Dictionary<string,(string NpcId,string Name)> _npcNames=new(StringComparer.Ordinal);
    private readonly Dictionary<string,string> _namesByNpc=new(StringComparer.Ordinal);
    private readonly HashSet<string> _missingArt=new(StringComparer.Ordinal);
    private Dictionary<string,string> _entityNames=new(StringComparer.Ordinal);
    private JsonDocument _manifest=null!,_generic=null!;
    private P1Entity[] _entities=Array.Empty<P1Entity>();
    private Dictionary<string,P1EntityV2> _v2=new(StringComparer.Ordinal);
    private bool _ready;
    private string? _targetId;
    private Vector2 _self;

    public string? TargetId
    {
        get=>_targetId;
        set{_targetId=value;QueueRedraw();}
    }

    public static Vector2 RenderPoint(double x,double y)=>new((float)(920+20*x),(float)(896-20*y));
    public static Vector2 WorldPoint(Vector2 render)=>new((render.X-920)/20,(896-render.Y)/20);

    public override void _Ready()
    {
        YSortEnabled=true;
        TextureFilter=TextureFilterEnum.Nearest;
        _manifest=Read("res://assets/combat_v1/manifest.json");
        _generic=Read("res://assets/ben_mua_v3/asset_manifest.json");
        _entityNames=JsonSerializer.Deserialize<Dictionary<string,string>>(FileAccess.GetFileAsString("res://assets/combat_v1/entity_names.json"))!;
        using var dialogue=Read("res://assets/combat_v1/dialogue_vi.json");
        if(dialogue.RootElement.TryGetProperty("npcs",out var npcs))
        foreach(var npc in npcs.EnumerateArray())
        {
            var id=npc.GetProperty("npcId").GetString()!;
            var name=npc.GetProperty("displayName").GetString()!;
            _npcNames[npc.GetProperty("entityId").GetString()!]=(id,name);
            _namesByNpc.TryAdd(id,name);
        }
        _ready=true;
    }

    private static JsonDocument Read(string path)=>
        JsonDocument.Parse(FileAccess.GetFileAsString(path).TrimStart('\uFEFF'));

    public void UpdateFrame(NativeOnlineFrame frame)
    {
        if(!_ready)return;
        var self=frame.World?.self??frame.WorldV2?.self;
        if(self!=null)_self=new Vector2((float)self.x,(float)self.y);
        _entities=frame.World?.entities??frame.WorldV2?.entities.Select(e=>new P1Entity{
            entityId=e.entityId,kind=e.kind,state=e.state,x=e.x,y=e.y,hp=e.hp,maxHp=e.maxHp,
            targetable=e.targetable,healthState=e.healthState,availability=e.availability
        }).ToArray()??Array.Empty<P1Entity>();
        _v2=frame.WorldV2?.entities.ToDictionary(e=>e.entityId,StringComparer.Ordinal)
            ??new Dictionary<string,P1EntityV2>(StringComparer.Ordinal);
        var present=new HashSet<string>(_entities.Select(e=>e.entityId),StringComparer.Ordinal);
        foreach(var id in _actors.Keys.Where(id=>!present.Contains(id)).ToArray())
        {
            _actors[id].Root.QueueFree();_actors.Remove(id);
        }
        if(_targetId!=null&&!present.Contains(_targetId))_targetId=null;
        foreach(var entity in _entities)
        {
            if(!_actors.TryGetValue(entity.entityId,out var visual))
            {
                visual=CreateVisual(entity.entityId);
                _actors.Add(entity.entityId,visual);
            }
            visual.Root.Position=RenderPoint(entity.x,entity.y);
            ApplyAppearance(entity,visual);
        }
        QueueRedraw();
    }

    private ActorVisual CreateVisual(string id)
    {
        var node=new Node2D{Name=id};
        AddChild(node);
        var body=new Sprite2D{Centered=false,TextureFilter=TextureFilterEnum.Nearest};
        node.AddChild(body);
        var name=new Label{Position=new Vector2(-120,-66),Size=new Vector2(240,24),
            HorizontalAlignment=HorizontalAlignment.Center,MouseFilter=Control.MouseFilterEnum.Ignore,ZIndex=20};
        name.AddThemeFontSizeOverride("font_size",15);
        name.AddThemeColorOverride("font_color",Color.FromHtml("#f3e4b7"));
        name.AddThemeColorOverride("font_shadow_color",new Color(0,0,0,.95f));
        name.AddThemeConstantOverride("shadow_offset_x",1);name.AddThemeConstantOverride("shadow_offset_y",1);
        node.AddChild(name);
        var health=new Label{Position=new Vector2(-70,-47),Size=new Vector2(140,18),
            HorizontalAlignment=HorizontalAlignment.Center,MouseFilter=Control.MouseFilterEnum.Ignore,ZIndex=20};
        health.AddThemeFontSizeOverride("font_size",11);
        health.AddThemeColorOverride("font_shadow_color",Colors.Black);
        health.AddThemeConstantOverride("shadow_offset_y",1);
        node.AddChild(health);
        var track=new Polygon2D{Position=new Vector2(-27,-25),Polygon=BarPolygon(54),
            Color=new Color(.08f,.08f,.08f,.92f),ZIndex=19};
        node.AddChild(track);
        var bar=new Polygon2D{Position=new Vector2(-27,-25),Polygon=BarPolygon(54),
            Color=Color.FromHtml("#b5594c"),ZIndex=20};
        node.AddChild(bar);
        return new ActorVisual{Root=node,Body=body,Name=name,Health=health,Bar=bar,Track=track};
    }

    private void ApplyAppearance(P1Entity e,ActorVisual visual)
    {
        string? npc=NpcId(e.entityId);
        string name=_npcNames.TryGetValue(e.entityId,out var n)?n.Name:
            npc!=null&&_namesByNpc.TryGetValue(npc,out var named)?named:
            e.entityId.Contains("OBJ_BM_PACKAGE_",StringComparison.Ordinal)?"Kiện hàng":
            MobFamily(e.entityId)=="CARPLING"?"Cá Linh":
            MobFamily(e.entityId)=="WATERROOT"?"Rễ Nước":
            _entityNames.TryGetValue(e.entityId,out var entityName)?entityName:
            e.kind=="GATHER_NODE"?"Điểm thu thập":HostileName(e.kind);
        string state=_v2.TryGetValue(e.entityId,out var v2)?v2.state:e.state;
        string? healthState=v2?.healthState??e.healthState;
        bool dead=healthState=="DEAD"||state=="DEAD";
        bool depleted=state=="DEPLETED"||e.availability=="COOLDOWN";
        bool hostile=e.kind is "MOB" or "BOSS";
        JsonElement region=default;
        string file="",key="";
        float wantedHeight=38,wantedWidth=0,referenceHeight=0;
        if(npc!=null)
        {
            if(_manifest.RootElement.GetProperty("questKit").TryGetProperty(npc,out region))
            {file="res://assets/combat_v1/ben_mua_questkit.png";key=npc;wantedHeight=npc=="NPC_TA_VAN_KHANH"?42:38;}
            else
            {
                string archetype=npc.Contains("FISHER",StringComparison.Ordinal)||npc.Contains("BOAT",StringComparison.Ordinal)?"villager_0":
                    npc.Contains("TRIAL",StringComparison.Ordinal)?"villager_5":"villager_4";
                region=_generic.RootElement.GetProperty("assets").GetProperty(archetype);
                file="res://assets/ben_mua_v3/"+region.GetProperty("file").GetString();key=archetype;
            }
        }
        else if(e.kind=="INTERACTABLE"&&e.entityId.Contains("OBJ_BM_PACKAGE_",StringComparison.Ordinal))
        {
            region=_manifest.RootElement.GetProperty("questKit").GetProperty("PACKAGE");
            file="res://assets/combat_v1/ben_mua_questkit.png";key="PACKAGE";wantedWidth=22;
        }
        else if(e.kind=="GATHER_NODE"&&NodeKey(e.entityId) is string nodeKey)
        {
            region=_manifest.RootElement.GetProperty("nodes").GetProperty(nodeKey);
            file="res://assets/combat_v1/ben_mua_nodes.png";key=nodeKey;
            wantedWidth=nodeKey.StartsWith("HERB",StringComparison.Ordinal)?25:nodeKey=="WOOD_01"?34:36;
        }
        else if(hostile&&MobFamily(e.entityId) is string family&&
            _manifest.RootElement.TryGetProperty("mobs",out var mobs))
        {
            key=family+"_"+(dead?"DEAD":state=="ATTACK"?"ATTACK":"IDLE");
            if(mobs.TryGetProperty(key,out region))
            {
                file="res://assets/combat_v1/ben_mua_mobs.png";wantedHeight=family=="CARPLING"?30:46;
                if(mobs.TryGetProperty(family+"_IDLE",out var idle)){var b=idle.GetProperty("contentBounds");referenceHeight=b[3].GetSingle()-b[1].GetSingle();}
            }
        }
        if(region.ValueKind==JsonValueKind.Object&&file.Length>0)
        {
            var rect=region.GetProperty("rect");var pivot=region.GetProperty("pivot");var bounds=region.GetProperty("contentBounds");
            float w=bounds[2].GetSingle()-bounds[0].GetSingle(),h=bounds[3].GetSingle()-bounds[1].GetSingle();
            float scale=wantedWidth>0?wantedWidth/w:wantedHeight/(referenceHeight>0?referenceHeight:h);
            if(visual.SpriteKey!=key+"|"+file)
            {
                if(!_textures.TryGetValue(file,out var texture)){texture=GD.Load<Texture2D>(file);_textures[file]=texture;}
                visual.Body.Texture=new AtlasTexture{Atlas=texture,Region=new Rect2(rect[0].GetSingle(),rect[1].GetSingle(),rect[2].GetSingle(),rect[3].GetSingle()),FilterClip=true};
                visual.SpriteKey=key+"|"+file;
            }
            visual.Body.Offset=-new Vector2(pivot[0].GetSingle(),pivot[1].GetSingle());
            visual.Body.Scale=Vector2.One*scale;
            visual.Body.Visible=true;
            float bodyHeight=h*scale;
            visual.Name.Position=new Vector2(-120,-bodyHeight-(hostile?39:25));
            visual.Health.Position=new Vector2(-70,-bodyHeight-22);
            visual.Bar.Position=new Vector2(-27,-bodyHeight-5);
            visual.Track.Position=visual.Bar.Position;
        }
        else
        {
            visual.Body.Visible=false;
            if(_missingArt.Add(e.entityId))GD.Print("NATIVE_ENTITY_ART_UNRESOLVED "+e.entityId);
        }
        visual.Root.Modulate=new Color(1,1,1,depleted?.32f:healthState=="BLOCKED"?.5f:1f);
        visual.Name.Text=name;
        bool selected=e.entityId==_targetId;
        visual.Name.Visible=hostile?selected||DistanceSquared(e,_self)<=64:
            e.kind!="GATHER_NODE"||DistanceSquared(e,_self)<=49;
        visual.Track.Visible=hostile&&e.maxHp>0;
        visual.Bar.Visible=hostile&&e.maxHp>0&&e.hp>0;
        visual.Health.Visible=hostile&&e.maxHp>0&&selected;
        if(e.maxHp>0)
        {
            visual.Bar.Polygon=BarPolygon(54*Math.Clamp(e.hp/(float)e.maxHp,0,1));
            visual.Health.Text=e.hp+" / "+e.maxHp;
        }
    }

    // World-space four-pixel bars avoid Control theme minimum-height expansion.
    private static Vector2[] BarPolygon(float width)=>new[]{Vector2.Zero,new Vector2(width,0),new Vector2(width,4),new Vector2(0,4)};

    private static string HostileName(string kind)=>kind=="BOSS"?"Thủ lĩnh":kind=="MOB"?"Yêu thú":"Người dân";
    private static string? NodeKey(string id)
    {
        foreach(var key in new[]{"ORE_01","ORE_02","HERB_01","HERB_02","WOOD_01"})
            if(id.EndsWith("NODE_BM_"+key,StringComparison.Ordinal))return key;
        return null;
    }

    private string? NpcId(string entity)
    {
        if(_npcNames.TryGetValue(entity,out var npc))return npc.NpcId;
        int i=entity.IndexOf("NPC_",StringComparison.Ordinal);
        return i>=0?entity[i..]:null;
    }

    // Source: canonical BM runtime entity templates, homogeneous groups only.
    // Mixed SPAWN_BM_04 is deliberately unresolved without a per-member catalog binding.
    private static string? MobFamily(string id)
    {
        if(id.Contains("SPAWN_BM_01",StringComparison.Ordinal)||id.Contains("SPAWN_BM_02",StringComparison.Ordinal)||
           id.Contains("WAVE_BM_ESCORT_A",StringComparison.Ordinal))return "CARPLING";
        if(id.Contains("SPAWN_BM_03",StringComparison.Ordinal)||id.Contains("WAVE_BM_ESCORT_B",StringComparison.Ordinal))return "WATERROOT";
        return null;
    }

    private static double DistanceSquared(P1Entity e,Vector2 self)=>
        (e.x-self.X)*(e.x-self.X)+(e.y-self.Y)*(e.y-self.Y);

    public P1Entity? NearestInteractable(Vector2 canonicalSelf,float maxWu=5)=>
        _entities.Where(e=>e.kind is "NPC" or "INTERACTABLE" or "GATHER_NODE")
            .Where(e=>e.state!="DEPLETED"&&e.availability!="COOLDOWN"&&DistanceSquared(e,canonicalSelf)<=maxWu*maxWu)
            .OrderBy(e=>DistanceSquared(e,canonicalSelf)).FirstOrDefault();

    public P1Entity? NearestTargetable(Vector2 canonicalSelf)=>
        _entities.Where(e=>e.targetable==true&&e.healthState=="ALIVE"&&e.hp>0)
            .OrderBy(e=>DistanceSquared(e,canonicalSelf)).FirstOrDefault();

    public override void _Draw()
    {
        foreach(var e in _entities)
        {
            bool selected=e.entityId==_targetId;
            if(!selected&&e.kind!="NPC"&&e.kind!="INTERACTABLE")continue;
            var at=RenderPoint(e.x,e.y);
            var color=selected?Color.FromHtml("#f3c66b"):new Color(.57f,.77f,.64f,.35f);
            DrawArc(at,selected?14:10,0,Mathf.Tau,32,color,selected?2:1);
        }
    }

    public override void _ExitTree(){_ready=false;_manifest?.Dispose();_generic?.Dispose();}
}
