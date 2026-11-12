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
        public Rect2 HitBounds;
        public readonly AuthoritativeMotion Motion=new();
        public long LifeId=-1;
        public double HitFlash;
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
    private int _lastRipplePhase=-1;
    private string? _targetId;
    private Vector2 _self;
    private (string Session,string Instance,string Floor,string Phase)? _context;
    private long _revision=-1;
    private long _selectedLife=-1;
    public event Action? TargetChanged;
    public int VisualCount=>_actors.Count;

    public string? TargetId
    {
        get=>_targetId;
        set
        {
            if(value!=null&&!_entities.Any(e=>e.entityId==value&&Selectable(e)))value=null;
            if(_targetId==value)return;_targetId=value;
            _selectedLife=value!=null&&_v2.TryGetValue(value,out var life)?life.lifeId:-1;
            foreach(var entity in _entities)if(_actors.TryGetValue(entity.entityId,out var visual))ApplyAppearance(entity,visual);
            DeclutterLabels();QueueRedraw();TargetChanged?.Invoke();
        }
    }
    public Vector2[] OcclusionFocus {get;private set;}=Array.Empty<Vector2>();

    // Presentation origin aligns canonical first-quest x18..64 with the authored
    // village's east-west street. It changes no server coordinate/navigation.
    public static Vector2 RenderOrigin=>new(560,896);
    public static Vector2 RenderPoint(double x,double y)=>RenderOrigin+new Vector2((float)(20*x),(float)(-20*y));
    public static Vector2 WorldPoint(Vector2 render)=>new((render.X-RenderOrigin.X)/20,(RenderOrigin.Y-render.Y)/20);

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

    public override void _Process(double delta)
    {
        if(!_ready)return;
        int phase=(int)(Godot.Time.GetTicksMsec()/180%4);
        if(phase==_lastRipplePhase)return;
        _lastRipplePhase=phase;
        var r=_manifest.RootElement.GetProperty("questMarkers").GetProperty("RIPPLE_"+phase).GetProperty("rect");
        foreach(var v in _actors.Values)
            if(v.SpriteKey.StartsWith("RIPPLE_",StringComparison.Ordinal)&&v.Body.Texture is AtlasTexture atlas)
                atlas.Region=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle());
    }

    public void UpdateFrame(NativeOnlineFrame frame)
    {
        if(!_ready)return;
        var world=frame.WorldV2;
        var context=(frame.SessionId,world?.mapInstanceId??frame.World?.mapId??"",world?.floorId??"",world?.phase??"");
        if(_context!=context){ResetActors();_context=context;_revision=-1;}
        if(world!=null&&world.revision<_revision)return;
        if(world!=null)_revision=world.revision;
        var self=frame.World?.self??frame.WorldV2?.self;
        if(self!=null)_self=new Vector2((float)self.x,(float)self.y);
        _entities=frame.World?.entities??frame.WorldV2?.entities.Select(e=>new P1Entity{
            entityId=e.entityId,kind=e.kind,state=e.state,x=e.x,y=e.y,hp=e.hp,maxHp=e.maxHp,
            targetable=e.targetable,healthState=e.healthState,availability=e.availability
        }).ToArray()??Array.Empty<P1Entity>();
        _v2=frame.WorldV2?.entities.ToDictionary(e=>e.entityId,StringComparer.Ordinal)
            ??new Dictionary<string,P1EntityV2>(StringComparer.Ordinal);
        OcclusionFocus=_entities.Where(e=>e.kind=="NPC"&&DistanceSquared(e,_self)<=49)
            .Select(e=>RenderPoint(e.x,e.y)).ToArray();
        var present=new HashSet<string>(_entities.Select(e=>e.entityId),StringComparer.Ordinal);
        foreach(var id in _actors.Keys.Where(id=>!present.Contains(id)).ToArray())
        {
            _actors[id].Root.QueueFree();_actors.Remove(id);
        }
        if(_targetId!=null&&!present.Contains(_targetId))TargetId=null;
        foreach(var entity in _entities)
        {
            if(!_actors.TryGetValue(entity.entityId,out var visual))
            {
                visual=CreateVisual(entity.entityId);
                _actors.Add(entity.entityId,visual);
            }
            bool newLife=_v2.TryGetValue(entity.entityId,out var life)&&visual.LifeId!=life.lifeId;
            bool first=visual.SpriteKey.Length==0;
            bool warp=visual.Root.Position.DistanceTo(RenderPoint(entity.x,entity.y))>240;
            visual.Motion.Push(RenderPoint(entity.x,entity.y),frame.SampleTime>0?frame.SampleTime:AuthoritativeMotion.Now,first||newLife||warp);
            if(first||newLife||warp){visual.Root.Position=RenderPoint(entity.x,entity.y);visual.Root.ResetPhysicsInterpolation();visual.HitFlash=0;visual.Body.Modulate=Colors.White;}
            if(life!=null)visual.LifeId=life.lifeId;
            ApplyAppearance(entity,visual);
        }
        if(_targetId!=null&&(!_entities.Any(e=>e.entityId==_targetId&&Selectable(e))||
            (_selectedLife>=0&&(!_v2.TryGetValue(_targetId,out var selected)||selected.lifeId!=_selectedLife))))TargetId=null;
        DeclutterLabels();QueueRedraw();
    }

    private void DeclutterLabels()
    {
        var occupied=new List<Rect2>();
        Vector2? selected=_targetId!=null&&_actors.TryGetValue(_targetId,out var picked)?picked.Root.Position:null;
        foreach(var e in _entities.OrderBy(e=>e.entityId==_targetId?0:e.kind=="NPC"&&DistanceSquared(e,_self)<=25?1:2).ThenBy(e=>DistanceSquared(e,_self)).ThenBy(e=>e.entityId,StringComparer.Ordinal))
        {
            if(!_actors.TryGetValue(e.entityId,out var visual))continue;
            if(e.entityId!=_targetId&&selected is {} foot&&e.kind is "MOB" or "BOSS"&&visual.Root.Position.DistanceSquaredTo(foot)<32*32)
            {visual.Bar.Visible=false;visual.Track.Visible=false;}
            if(!visual.Name.Visible)continue;
            float width=Math.Min(220,visual.Name.Text.Length*9+12);
            var rect=new Rect2(visual.Root.Position+new Vector2(-width/2,visual.Name.Position.Y),new Vector2(width,22));
            if(e.entityId!=_targetId&&occupied.Any(r=>r.Intersects(rect))){visual.Name.Visible=false;continue;}
            occupied.Add(rect.Grow(3));
            if(e.entityId==_targetId)occupied.Add(new Rect2(visual.Root.Position+visual.Health.Position,new Vector2(140,20)));
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        bool moved=false;double now=AuthoritativeMotion.Now;
        foreach(var visual in _actors.Values)
        {
            var previous=visual.Root.Position;var position=visual.Motion.Sample(now,previous);
            if(position.DistanceSquaredTo(previous)>.000001f){visual.Root.Position=position;moved=true;}
            if(visual.HitFlash>0){visual.HitFlash=Math.Max(0,visual.HitFlash-delta);if(visual.HitFlash<=0)visual.Body.Modulate=Colors.White;}
        }
        // Stationary actors and rings keep their cached draw commands.
        if(moved)QueueRedraw();
    }

    private void ResetActors()
    {
        foreach(var visual in _actors.Values)visual.Root.QueueFree();
        _actors.Clear();_entities=Array.Empty<P1Entity>();_v2.Clear();TargetId=null;OcclusionFocus=Array.Empty<Vector2>();
    }

    public P1EntityV2? EntityLife(string id)=>_v2.TryGetValue(id,out var life)?life:null;
    public Vector2 VisualPosition(string id)=>_actors.TryGetValue(id,out var visual)?visual.Root.Position:Vector2.Zero;
    public void FlashImpact(string id){if(_actors.TryGetValue(id,out var visual)){visual.HitFlash=.13;visual.Body.Modulate=new Color(1,.57f,.68f);}}

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
            e.entityId.StartsWith("ALPHA_OBJ_BM_RIPPLE_",StringComparison.Ordinal)?"Gợn nước lạ":
            e.entityId.StartsWith("ALPHA_OBJ_BM_VILLAGER_",StringComparison.Ordinal)?"Người dân mắc kẹt":
            e.entityId=="ALPHA_OBJ_BM_FRAGMENT"?"Mảnh ấn":
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
        else if(e.kind=="INTERACTABLE"&&QuestMarkerKey(e.entityId) is string marker)
        {
            region=_manifest.RootElement.GetProperty("questMarkers").GetProperty(marker);
            file="res://assets/combat_v1/ben_mua_quest_markers.png";key=marker;
            if(marker.StartsWith("RIPPLE_",StringComparison.Ordinal))wantedWidth=40;
            else wantedHeight=36;
        }
        else if(e.kind=="INTERACTABLE"&&e.entityId=="ALPHA_OBJ_BM_FRAGMENT")
        {
            region=_manifest.RootElement.GetProperty("nodes").GetProperty("FRAGMENT");
            file="res://assets/combat_v1/ben_mua_nodes.png";key="FRAGMENT";wantedWidth=25;
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
            visual.HitBounds=new Rect2((new Vector2(bounds[0].GetSingle(),bounds[1].GetSingle())+visual.Body.Offset)*scale,new Vector2(w,h)*scale).Grow(5);
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
    private static string? QuestMarkerKey(string id)=>id switch{
        "ALPHA_OBJ_BM_RIPPLE_01" or "ALPHA_OBJ_BM_RIPPLE_02" or "ALPHA_OBJ_BM_RIPPLE_03"=>"RIPPLE_0",
        "ALPHA_OBJ_BM_VILLAGER_01"=>"VILLAGER_01_WAIT",
        "ALPHA_OBJ_BM_VILLAGER_02"=>"VILLAGER_02_WAIT",_=>null};
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

    private bool Selectable(P1Entity e)=>e.kind is "MOB" or "BOSS"&&e.targetable==true&&e.healthState=="ALIVE"&&e.hp>0&&
        _actors.TryGetValue(e.entityId,out var visual)&&visual.Body.Visible;
    private bool VisibleIn(P1Entity e,Rect2 view)=>_actors.TryGetValue(e.entityId,out var visual)&&
        view.Intersects(new Rect2(visual.Root.Position+visual.HitBounds.Position,visual.HitBounds.Size));
    public P1Entity? NearestTargetable(Vector2 canonicalSelf)=>
        _entities.Where(Selectable).OrderBy(e=>DistanceSquared(e,canonicalSelf)).ThenBy(e=>e.entityId,StringComparer.Ordinal).FirstOrDefault();
    public P1Entity? CombatTarget(Rect2 view)
    {
        var selected=_entities.FirstOrDefault(e=>e.entityId==_targetId&&Selectable(e));
        if(selected!=null)return selected;
        var nearest=_entities.Where(e=>Selectable(e)&&VisibleIn(e,view)).OrderBy(e=>DistanceSquared(e,_self)).ThenBy(e=>e.entityId,StringComparer.Ordinal).FirstOrDefault();
        TargetId=nearest?.entityId;return nearest;
    }
    public bool SelectAt(Vector2 point,Rect2 view)
    {
        var hit=_entities.Where(e=>Selectable(e)&&VisibleIn(e,view)&&_actors[e.entityId].HitBounds.HasPoint(point-_actors[e.entityId].Root.Position))
            .OrderBy(e=>(point-_actors[e.entityId].Root.Position-_actors[e.entityId].HitBounds.GetCenter()).LengthSquared())
            .ThenBy(e=>e.entityId,StringComparer.Ordinal).FirstOrDefault();
        if(hit==null)return false;TargetId=hit.entityId;return true;
    }
    public void CycleTarget(Rect2 view,bool reverse=false)
    {
        var candidates=_entities.Where(e=>Selectable(e)&&VisibleIn(e,view)).OrderBy(e=>DistanceSquared(e,_self)).ThenBy(e=>e.entityId,StringComparer.Ordinal).ToArray();
        if(candidates.Length==0){TargetId=null;return;}
        int current=Array.FindIndex(candidates,e=>e.entityId==_targetId);
        int next=current<0?(reverse?candidates.Length-1:0):(current+(reverse?-1:1)+candidates.Length)%candidates.Length;
        TargetId=candidates[next].entityId;
    }
    public CombatTargetInfo? TargetInfo
    {
        get
        {
            var e=_entities.FirstOrDefault(e=>e.entityId==_targetId&&Selectable(e));if(e==null)return null;
            return new CombatTargetInfo(e.entityId,_selectedLife,_actors[e.entityId].Name.Text,e.kind,e.hp,e.maxHp,Math.Sqrt(DistanceSquared(e,_self)),e.state);
        }
    }

    public override void _Draw()
    {
        foreach(var e in _entities)
        {
            bool selected=e.entityId==_targetId;
            if(!selected&&e.kind!="NPC"&&e.kind!="INTERACTABLE")continue;
            var at=_actors.TryGetValue(e.entityId,out var visual)?visual.Root.Position:RenderPoint(e.x,e.y);
            var color=selected?Color.FromHtml("#f3c66b"):new Color(.57f,.77f,.64f,.35f);
            DrawArc(at,selected?14:10,0,Mathf.Tau,32,color,selected?2:1);
        }
    }

    public override void _ExitTree(){_ready=false;_manifest?.Dispose();_generic?.Dispose();}
}
