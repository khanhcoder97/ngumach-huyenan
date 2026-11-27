#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using NguMach.Client.P1;
namespace Ngumach.VisualReboot;

public partial class NativeDialoguePanel
{
    public static readonly (string Id,string Label)[] Sections={
        ("Character","Nhân vật"),("Inventory","Túi đồ"),("Skills","Kỹ năng"),("Journal","Nhiệm vụ"),("WorldMap","Bản đồ"),
        ("Forge","Lò rèn"),("Guild","Bang hội"),("Activities","Hoạt động"),("Codex","Bách khoa"),("Appearance","Ngoại trang"),
        ("Social","Bạn bè"),("Mail","Thư tín"),("Settings","Cài đặt")};
    private ScrollContainer _sidebarScroll=null!;
    private VBoxContainer _sidebar=null!,_speakerArt=null!;
    private TextureRect _headerIcon=null!,_speakerPortrait=null!;
    private readonly Dictionary<string,Button> _nav=new();
    private readonly List<(Label Label,Func<string> Value)> _liveValues=new();
    private MoonMapView? _workspaceMap;
    private string _section="Inventory",_filter="Tất cả",_search="",_subTab="";
    private string? _selectedItem;
    private int _heroFacing=4;
    private bool _lowFx,_compact;
    private float _volume=.65f;
    private bool _loadingPrefs;
    public event Action<bool,bool>? DisplaySettingsChanged;
    public string CurrentSection=>_section;

    public void ShowMenu(string section,NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _section=Sections.Any(s=>s.Id==section)?section:"Character";
        _frame=frame;_inventory=true;_journal=_section=="Journal";_entry=null;_waitingKind=null;_replyOpen=false;
        IsOpen=true;_root.Visible=true;_subTab="";ResizePanel();Render();
    }
    private void BuildNavigation()
    {
        foreach(var section in Sections)
        {
            string id=section.Id;
            var b=MoonGlassTheme.Button(section.Label,149);b.Icon=MoonGlassIcons.Get(id);b.ExpandIcon=true;
            b.AddThemeConstantOverride("icon_max_width",18);b.Alignment=HorizontalAlignment.Left;
            b.Pressed+=()=>{_section=id;_journal=id=="Journal";_subTab="";_scroll.ScrollVertical=0;Render();};
            _sidebar.AddChild(b);_nav[id]=b;
        }
    }
    private void UpdateLiveWorkspace()
    {
        foreach(var binding in _liveValues)if(GodotObject.IsInstanceValid(binding.Label))binding.Label.Text=binding.Value();
        if(_workspaceMap!=null&&GodotObject.IsInstanceValid(_workspaceMap))_workspaceMap.Frame=_frame;
    }
    private void RenderWorkspace()
    {
        _back.Visible=false;_next.Visible=false;_action.Visible=false;_pageInfo.Text="";
        _headerIcon.Texture=MoonGlassIcons.Get(_section);_liveValues.Clear();_workspaceMap=null;
        foreach(var c in _inventoryRows.GetChildren()){_inventoryRows.RemoveChild(c);c.QueueFree();}
        foreach(var entry in _nav)entry.Value.AddThemeStyleboxOverride("normal",MoonGlassTheme.Box(
            entry.Key==_section?new Color(.4f,.39f,.65f,.8f):new Color(.22f,.24f,.39f,.28f),
            entry.Key==_section?MoonGlassTheme.Silver:new Color(.56f,.62f,.85f,.15f),6,8));
        var active=_nav[_section];Callable.From(()=>{if(_ready&&GodotObject.IsInstanceValid(active))_sidebarScroll.EnsureControlVisible(active);}).CallDeferred();
        _title.Text=Sections.First(s=>s.Id==_section).Label;
        switch(_section)
        {
            case "Inventory":RenderBag();break;
            case "Character":RenderCharacter();break;
            case "Journal":RenderJournal();break;
            case "Skills":RenderSkills();break;
            case "WorldMap":RenderMap();break;
            case "Settings":RenderSettings();break;
            case "Codex":RenderCodex();break;
            case "Appearance":RenderAppearance();break;
            default:RenderService();break;
        }
        UpdateLiveWorkspace();
    }
    public void AuditWorkspaceBounds()
    {
        if(!GetViewport().GetVisibleRect().Encloses(_panel.GetGlobalRect()))throw new InvalidOperationException("Workspace outside viewport: "+_section);
        if(_inventory&&!_sidebarScroll.GetGlobalRect().Grow(2).Encloses(_nav[_section].GetGlobalRect()))throw new InvalidOperationException("Selected navigation clipped: "+_section);
    }
    private HBoxContainer Tabs(IEnumerable<string> names,Action<string> choose,string? selected=null)
    {
        var row=new HBoxContainer();row.AddThemeConstantOverride("separation",6);
        foreach(var name in names)
        {var b=MoonGlassTheme.Button(name,0,selected==name);b.Pressed+=()=>choose(name);row.AddChild(b);}
        _inventoryRows.AddChild(row);return row;
    }
    private void Intro(string title,string subtitle)
    {var row=new VBoxContainer();row.AddChild(MoonGlassTheme.Label(title,19,MoonGlassTheme.Gold));row.AddChild(MoonGlassTheme.Label(subtitle,13,MoonGlassTheme.Muted));_inventoryRows.AddChild(row);}
    private static VBoxContainer Column(int width=0)
    {var v=new VBoxContainer{CustomMinimumSize=new Vector2(width,0),SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};v.AddThemeConstantOverride("separation",9);return v;}
    private void Live(VBoxContainer parent,string label,Func<string> value)
    {
        var row=new HBoxContainer();row.AddChild(MoonGlassTheme.Label(label,14,MoonGlassTheme.Muted));
        var l=MoonGlassTheme.Label(value(),15);l.HorizontalAlignment=HorizontalAlignment.Right;row.AddChild(l);parent.AddChild(row);_liveValues.Add((l,value));
    }
    private P1Self? Self=>_frame.World?.self;
    private TextureRect HeroPreview(Vector2 size)=>MoonGlassTheme.Image(MoonGlassTheme.Hero(_heroFacing),size);
    private void AddHeroCard(HBoxContainer main,bool compact=false)
    {
        var card=MoonGlassTheme.Card(new Color(.23f,.24f,.4f,.5f));card.CustomMinimumSize=new Vector2(compact?210:250,0);card.SizeFlagsHorizontal=Control.SizeFlags.ShrinkBegin;
        var c=Column();card.AddChild(c);c.AddChild(MoonGlassTheme.Label("MINH KIẾM",19,MoonGlassTheme.Ink));c.AddChild(MoonGlassTheme.Label("Kiếm khách · Ngũ Mạch",12,MoonGlassTheme.Silver));
        var art=HeroPreview(new Vector2(compact?170:210,210));c.AddChild(art);
        var rotate=new HBoxContainer();var left=MoonGlassTheme.Button("‹",42);var right=MoonGlassTheme.Button("›",42);
        left.Pressed+=()=>{_heroFacing=(_heroFacing+7)%8;art.Texture=MoonGlassTheme.Hero(_heroFacing);};right.Pressed+=()=>{_heroFacing=(_heroFacing+1)%8;art.Texture=MoonGlassTheme.Hero(_heroFacing);};
        rotate.AddChild(left);rotate.AddChild(MoonGlassTheme.Label("Xoay nhân vật",11,MoonGlassTheme.Muted));rotate.AddChild(right);c.AddChild(rotate);
        // Current HP/MP belong in the status HUD; keep the dressing preview wholly visible.
        main.AddChild(card);
    }
    private void RenderCharacter()
    {
        Tabs(new[]{"Thông tin","Trang bị","Thuộc tính"},s=>{_subTab=s;Render();},_subTab.Length==0?"Thông tin":_subTab);
        var main=new HBoxContainer();main.AddThemeConstantOverride("separation",18);_inventoryRows.AddChild(main);AddHeroCard(main);
        var right=Column();main.AddChild(right);
        if(_subTab is "" or "Thông tin" or "Thuộc tính")
        {
            var stats=MoonGlassTheme.Card();var c=Column();stats.AddChild(c);c.AddChild(MoonGlassTheme.Label("Thuộc tính nhân vật",18,MoonGlassTheme.Gold));
            Live(c,"Môn phái",()=>Self!=null?"Minh Kiếm":"—");Live(c,"Kiếm ý",()=>Self?.swordIntent.ToString()??"—");
            Live(c,"Khí huyết tối đa",()=>Self?.maxHp.ToString()??"—");Live(c,"Linh lực tối đa",()=>Self?.maxMp.ToString()??"—");
            Live(c,"Tọa độ",()=>Self!=null?$"{Self.x:0.0}, {Self.y:0.0}":"—");Live(c,"Vật phẩm đang mặc",()=>_frame.Inventory?.items.Count(i=>i.location=="EQUIPPED").ToString()??"—");right.AddChild(stats);
        }
        if(_subTab!="Trang bị")
        {
            var view=MoonGlassTheme.Button("Xem trang bị",150);view.Pressed+=()=>{_subTab="Trang bị";Render();};right.AddChild(view);return;
        }
        var gear=MoonGlassTheme.Card();var gc=Column();gear.AddChild(gc);gc.AddChild(MoonGlassTheme.Label("Trang bị",18,MoonGlassTheme.Gold));
        var grid=new GridContainer{Columns=4};grid.AddThemeConstantOverride("h_separation",8);grid.AddThemeConstantOverride("v_separation",8);
        string[] slots={"HAT","CHEST","LEGS","WEAPON","GLOVES","BOOTS","NECK","RING_L","RING_R","PENDANT","CLOAK","SEAL"};
        string[] labels={"Mũ","Áo","Quần","Vũ khí","Găng","Giày","Dây chuyền","Nhẫn trái","Nhẫn phải","Ngọc bội","Áo choàng","Ấn"};
        for(int i=0;i<slots.Length;i++)
        {
            var item=_frame.Inventory?.items.FirstOrDefault(it=>it.location=="EQUIPPED"&&it.slot==slots[i]);
            var box=Column();var b=ItemTile(item,62);b.TooltipText=labels[i]+(item==null?" · Chưa có dữ liệu trang bị":" · "+ItemName(item.templateId));box.AddChild(b);box.AddChild(MoonGlassTheme.Label(labels[i],10,MoonGlassTheme.Muted));grid.AddChild(box);
        }
        gc.AddChild(grid);right.AddChild(gear);
    }
    private bool ItemMatches(P1Item item)
    {
        bool category=_filter=="Tất cả"||_filter=="Trang bị"&&item.templateId.StartsWith("EQ-",StringComparison.Ordinal)||
            _filter=="Vật dụng"&&item.templateId.StartsWith("POT-",StringComparison.Ordinal)||_filter=="Nguyên liệu"&&item.templateId.StartsWith("MAT-",StringComparison.Ordinal);
        return category&&(_search.Length==0||ItemName(item.templateId).Contains(_search,StringComparison.OrdinalIgnoreCase));
    }
    private Button ItemTile(P1Item? item,int size=60)
    {
        var b=MoonGlassTheme.Button("",size);b.CustomMinimumSize=new Vector2(size,size);b.SizeFlagsHorizontal=Control.SizeFlags.ShrinkBegin;
        Color border=item==null?new Color(.55f,.6f,.8f,.22f):item.templateId.Contains("LEGEND",StringComparison.Ordinal)?MoonGlassTheme.Gold:item.templateId.Contains("EPIC",StringComparison.Ordinal)?MoonGlassTheme.Violet:MoonGlassTheme.Silver;
        b.AddThemeStyleboxOverride("normal",MoonGlassTheme.Box(new Color(.16f,.18f,.34f,.64f),_selectedItem==item?.instanceId&&item!=null?MoonGlassTheme.Gold:border,7,5));
        if(item!=null)
        {
            b.TooltipText=ItemName(item.templateId);
            if(_icons.TryGetValue(item.templateId,out var art)){var image=MoonGlassTheme.Image(art,new Vector2(size-12,size-12));b.AddChild(image);image.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);image.OffsetLeft=6;image.OffsetTop=5;image.OffsetRight=-6;image.OffsetBottom=-8;}
            else{b.Icon=MoonGlassIcons.Get(item.templateId.StartsWith("EQ-",StringComparison.Ordinal)?"Appearance":"Inventory");b.ExpandIcon=true;b.AddThemeConstantOverride("icon_max_width",28);}
            var count=MoonGlassTheme.Label("×"+item.stack,11);count.Position=new Vector2(5,size-20);count.Size=new Vector2(size-10,15);count.HorizontalAlignment=HorizontalAlignment.Right;count.MouseFilter=Control.MouseFilterEnum.Ignore;b.AddChild(count);
            b.Pressed+=()=>{_selectedItem=item.instanceId;Render();};
        }
        else{b.Text="·";b.AddThemeFontSizeOverride("font_size",20);b.AddThemeColorOverride("font_color",new Color(.57f,.61f,.79f,.28f));b.TooltipText="Ô trống";}
        return b;
    }
    private void RenderBag()
    {
        _title.Text="Túi đồ";Tabs(new[]{"Tất cả","Trang bị","Vật dụng","Nguyên liệu"},s=>{_filter=s;Render();},_filter);
        var inv=_frame.Inventory;
        var main=new HBoxContainer();main.AddThemeConstantOverride("separation",14);_inventoryRows.AddChild(main);AddHeroCard(main,true);
        var bag=Column();main.AddChild(bag);
        var find=new LineEdit{PlaceholderText="Tìm trong túi đồ…",Text=_search,CustomMinimumSize=new Vector2(0,38)};
        find.TextSubmitted+=s=>{_search=s.Trim();Render();};bag.AddChild(find);
        var money=new HBoxContainer();if(_icons.TryGetValue("COIN",out var coin))money.AddChild(MoonGlassTheme.Image(coin,new Vector2(24,24)));
        money.AddChild(MoonGlassTheme.Label("Đồng  "+(inv?.currencies.FirstOrDefault(c=>c.currencyId=="COIN")?.amount.ToString()??"—"),16,MoonGlassTheme.Gold));bag.AddChild(money);
        var items=inv?.items.Where(ItemMatches).ToArray()??Array.Empty<P1Item>();
        if(!items.Any(i=>i.instanceId==_selectedItem))_selectedItem=items.FirstOrDefault()?.instanceId;
        if(inv==null)bag.AddChild(MoonGlassTheme.Label("Chưa có dữ liệu túi đồ. Chọn Làm mới để đọc lại.",13,MoonGlassTheme.Muted));
        else if(inv.items.Length==0)bag.AddChild(MoonGlassTheme.Label("Túi đồ đang trống.",13,MoonGlassTheme.Muted));
        var grid=new GridContainer{Columns=5};grid.AddThemeConstantOverride("h_separation",7);grid.AddThemeConstantOverride("v_separation",7);bag.AddChild(grid);
        for(int i=0;i<Math.Max(20,items.Length);i++)grid.AddChild(ItemTile(i<items.Length?items[i]:null,54));
        bag.AddChild(MoonGlassTheme.Label(items.Length+" vật phẩm được đồng bộ",11,MoonGlassTheme.Muted));
        var detail=MoonGlassTheme.Card();detail.CustomMinimumSize=new Vector2(190,0);var dc=Column();detail.AddChild(dc);main.AddChild(detail);
        var selected=items.FirstOrDefault(i=>i.instanceId==_selectedItem)??items.FirstOrDefault();
        dc.AddChild(MoonGlassTheme.Label("Chi tiết vật phẩm",16,MoonGlassTheme.Gold));
        if(selected==null){dc.AddChild(MoonGlassTheme.Label("Chọn một vật phẩm để xem thông tin.",14,MoonGlassTheme.Muted));return;}
        if(_icons.TryGetValue(selected.templateId,out var icon))dc.AddChild(MoonGlassTheme.Image(icon,new Vector2(96,96)));
        dc.AddChild(MoonGlassTheme.Label(ItemName(selected.templateId)+"  ×"+selected.stack,17));
        dc.AddChild(MoonGlassTheme.Label(selected.location=="EQUIPPED"?"Đang mặc":selected.location=="BANK"?"Trong kho":"Trong túi",13,MoonGlassTheme.Silver));
        dc.AddChild(MoonGlassTheme.Label("Độ bền  "+selected.durability,13,MoonGlassTheme.Muted));
        var equip=MoonGlassTheme.Button("Trang bị",0,true);equip.Disabled=true;equip.TooltipText="Chưa khả dụng trong phiên này";dc.AddChild(equip);
    }
    private void RenderSkills()
    {
        Tabs(new[]{"Chủ động","Nội tại","Bộ kỹ năng"},s=>{_subTab=s;Render();},_subTab.Length==0?"Chủ động":_subTab);
        if(_subTab is "Nội tại" or "Bộ kỹ năng"){Empty("Kỹ năng Minh Kiếm","Chưa có thông tin để hiển thị trong mục này.","Skills");return;}
        using var doc=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));var tex=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_skill_icons.png");
        for(int i=0;i<6;i++)
        {
            var card=MoonGlassTheme.Card();var row=new HBoxContainer();row.AddThemeConstantOverride("separation",15);card.AddChild(row);
            var e=doc.RootElement.GetProperty("uiIcons")[i];var r=e.GetProperty("rect");var icon=new AtlasTexture{Atlas=tex,Region=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle())};row.AddChild(MoonGlassTheme.Image(icon,new Vector2(60,60)));
            var c=Column();c.AddChild(MoonGlassTheme.Label(SkillVfxPlayer.Names[i],18));
            c.AddChild(MoonGlassTheme.Label(new[]{"Đỡ đòn và phản công","Áp sát mục tiêu","Chém quét diện rộng","Khiên bảo hộ","Lướt di chuyển","Tuyệt kỹ tập trung"}[i],14,MoonGlassTheme.Silver));
            c.AddChild(MoonGlassTheme.Label("Phím "+(i+1)+" · "+(i<3?"Kỹ năng chủ động":"Chưa khả dụng trong phiên này"),13,MoonGlassTheme.Muted));row.AddChild(c);
            _inventoryRows.AddChild(card);
        }
    }
    private void RenderMap()
    {
        Intro("Bến Mưa","Ký hiệu nhân vật và đối tượng được cập nhật theo phiên chơi.");
        _workspaceMap=new MoonMapView{CustomMinimumSize=new Vector2(0,280),SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,Overview=true,Frame=_frame};_inventoryRows.AddChild(_workspaceMap);
        _inventoryRows.AddChild(MoonGlassTheme.Label("● Bạn    ● Người dân / NPC    ◇ Điểm tương tác    ● Mục tiêu",13,MoonGlassTheme.Muted));
        Live(_inventoryRows,"Vị trí hiện tại",()=>Self!=null?$"{Self.x:0.0}, {Self.y:0.0}":"—");
    }
    private void RenderCodex()
    {
        Tabs(new[]{"Tất cả","Vật phẩm","Nhân vật","Kỹ năng"},s=>{_subTab=s;Render();},_subTab.Length==0?"Tất cả":_subTab);
        Intro("Bách khoa hành trình","Tra cứu tên gọi đã có trong thế giới Ngũ Mạch.");
        if(_subTab=="Nhân vật")foreach(var npc in _npcs.Where(n=>n.MapId=="MAP_BEN_MUA").DistinctBy(n=>n.NpcId))
        {var p=MoonGlassTheme.Card();var c=Column();p.AddChild(c);c.AddChild(MoonGlassTheme.Label(npc.Name,17));c.AddChild(MoonGlassTheme.Label("Bến Mưa",12,MoonGlassTheme.Muted));_inventoryRows.AddChild(p);}
        else if(_subTab=="Kỹ năng")foreach(var name in SkillVfxPlayer.Names)
        {var p=MoonGlassTheme.Card();p.AddChild(MoonGlassTheme.Label(name,17));_inventoryRows.AddChild(p);}
        else
        {
            var search=new LineEdit{PlaceholderText="Tên vật phẩm…",Text=_search,CustomMinimumSize=new Vector2(0,38)};search.TextSubmitted+=s=>{_search=s.Trim();Render();};_inventoryRows.AddChild(search);
            var entries=_itemNames.Where(p=>_search.Length>0?p.Value.Contains(_search,StringComparison.OrdinalIgnoreCase):_frame.Inventory?.items.Any(i=>i.templateId==p.Key)==true).Take(30).ToArray();
            if(entries.Length==0)Empty("Tra cứu vật phẩm","Nhập tên để tìm trong bách khoa.","Codex");
            foreach(var e in entries){var p=MoonGlassTheme.Card();p.AddChild(MoonGlassTheme.Label(e.Value,15));_inventoryRows.AddChild(p);}
        }
    }
    private void RenderAppearance()
    {
        Tabs(new[]{"Ngoại trang","Vật phẩm hỗ trợ","Lệnh bài"},s=>{_subTab=s;Render();},_subTab.Length==0?"Ngoại trang":_subTab);
        var row=new HBoxContainer();row.AddThemeConstantOverride("separation",16);_inventoryRows.AddChild(row);AddHeroCard(row);
        var c=Column();row.AddChild(c);c.AddChild(MoonGlassTheme.Label(_subTab.Length==0?"Ngoại trang nhân vật":_subTab,21,MoonGlassTheme.Gold));
        c.AddChild(MoonGlassTheme.Label("Chưa có bộ sưu tập được đồng bộ trong phiên này.",15,MoonGlassTheme.Muted));
        var grid=new GridContainer{Columns=4};for(int i=0;i<12;i++)grid.AddChild(ItemTile(null));c.AddChild(grid);
    }
    private void Empty(string title,string message,string icon)
    {
        var p=MoonGlassTheme.Card(new Color(.29f,.3f,.46f,.45f));var c=Column();p.AddChild(c);c.AddChild(MoonGlassTheme.Image(MoonGlassIcons.Get(icon),new Vector2(58,58),false));
        c.AddChild(MoonGlassTheme.Label(title,20,MoonGlassTheme.Gold));c.AddChild(MoonGlassTheme.Label(message,15,MoonGlassTheme.Muted));_inventoryRows.AddChild(p);
    }
    private void RenderService()
    {
        string[] tabs=_section switch{
            "Forge"=>new[]{"Rèn trang bị","Cường hóa","Chế tạo"},"Guild"=>new[]{"Tổng quan","Thành viên","Hoạt động"},
            "Activities"=>new[]{"Lịch hoạt động","Đấu trường","Phần thưởng"},"Social"=>new[]{"Bạn bè","Tổ đội","Gần đây"},
            "Mail"=>new[]{"Hộp thư","Đã nhận"},_=>new[]{"Tổng quan"}};
        Tabs(tabs,s=>{_subTab=s;Render();},_subTab.Length==0?tabs[0]:_subTab);
        string title=Sections.First(s=>s.Id==_section).Label;
        string detail=_section switch{"Forge"=>"Đến gặp thợ rèn để xem các dịch vụ khả dụng.","Guild"=>"Chưa có thông tin bang hội được đồng bộ.","Activities"=>"Chưa có lịch hoạt động được đồng bộ.","Social"=>"Chưa có danh sách bạn bè hoặc tổ đội.","Mail"=>"Chưa có dữ liệu hộp thư.",_=>"Chưa có dữ liệu để hiển thị."};
        Empty(title,detail,_section);
        var row=new HBoxContainer();
        foreach(var label in _section=="Forge"?new[]{"Chọn nguyên liệu","Xem công thức"}:_section=="Guild"?new[]{"Tìm bang hội","Tạo bang hội"}:new[]{"Làm mới"})
        {var b=MoonGlassTheme.Button(label,130);if(label=="Làm mới")b.Pressed+=()=>CommandRequested?.Invoke("REFRESH","","");else{b.Disabled=true;b.TooltipText="Chưa khả dụng trong phiên này";}row.AddChild(b);}
        _inventoryRows.AddChild(row);
    }
    private void RenderSettings()
    {
        Tabs(new[]{"Hiển thị","Âm thanh","Điều khiển"},s=>{_subTab=s;Render();},_subTab.Length==0?"Hiển thị":_subTab);
        Intro("Cài đặt của bạn","Điều chỉnh giao diện và trải nghiệm chơi.");
        void Toggle(string label,bool current,Action<bool> change)
        {var p=MoonGlassTheme.Card();var row=new HBoxContainer();p.AddChild(row);row.AddChild(MoonGlassTheme.Label(label,16));var b=new CheckButton{Text=current?"Bật":"Tắt",ButtonPressed=current};b.Toggled+=v=>{b.Text=v?"Bật":"Tắt";change(v);SavePreferences();};row.AddChild(b);_inventoryRows.AddChild(p);}
        if(_subTab is "" or "Hiển thị")
        {
            Toggle("Giảm hiệu ứng kỹ năng",_lowFx,v=>{_lowFx=v;DisplaySettingsChanged?.Invoke(_lowFx,_compact);});
            Toggle("Góc nhìn gọn 48 × 27",_compact,v=>{_compact=v;DisplaySettingsChanged?.Invoke(_lowFx,_compact);});
            _inventoryRows.AddChild(MoonGlassTheme.Label("Góc nhìn rộng mặc định: 64 × 36. Giao diện giữ nguyên vị trí khi đổi góc nhìn.",13,MoonGlassTheme.Muted));
        }
        else if(_subTab=="Âm thanh")
        {
            var card=MoonGlassTheme.Card();var c=Column();card.AddChild(c);var amount=MoonGlassTheme.Label("Âm lượng tổng · "+(int)(_volume*100)+"%",17);
            c.AddChild(amount);var slider=new HSlider{MinValue=0,MaxValue=100,Step=1,Value=_volume*100,CustomMinimumSize=new Vector2(0,38)};
            slider.ValueChanged+=value=>{_volume=(float)value/100;amount.Text="Âm lượng tổng · "+(int)value+"%";ApplyVolume();SavePreferences();};c.AddChild(slider);_inventoryRows.AddChild(card);
        }
        else
        {
            foreach(var pair in new[]{("Di chuyển","W A S D / Phím mũi tên"),("Tương tác","E"),("Tấn công","Space"),("Kỹ năng","1 – 6"),("Nhật ký","J"),("Túi đồ","I"),("Nhân vật / Kỹ năng","C / K"),("Bản đồ / Cài đặt","M / F10"),("Đóng cửa sổ","Esc")})
            {var p=MoonGlassTheme.Card();var row=new HBoxContainer();p.AddChild(row);row.AddChild(MoonGlassTheme.Label(pair.Item1));var key=MoonGlassTheme.Label(pair.Item2,15,MoonGlassTheme.Gold);key.HorizontalAlignment=HorizontalAlignment.Right;row.AddChild(key);_inventoryRows.AddChild(p);}
        }
    }
    private void ApplyVolume(){int bus=AudioServer.GetBusIndex("Master");if(bus>=0){AudioServer.SetBusMute(bus,_volume<=0);AudioServer.SetBusVolumeDb(bus,Mathf.LinearToDb(Math.Max(.001f,_volume)));}}
    public void ApplySavedPreferences()
    {
        _loadingPrefs=true;var config=new ConfigFile();if(config.Load("user://moonglass_ui.cfg")==Error.Ok)
        {_lowFx=config.GetValue("display","low_fx",false).AsBool();_compact=config.GetValue("display","compact",false).AsBool();_volume=Math.Clamp((float)config.GetValue("audio","master",.65f).AsDouble(),0,1);}
        _loadingPrefs=false;ApplyVolume();DisplaySettingsChanged?.Invoke(_lowFx,_compact);
    }
    private void SavePreferences()
    {if(_loadingPrefs)return;var c=new ConfigFile();c.SetValue("display","low_fx",_lowFx);c.SetValue("display","compact",_compact);c.SetValue("audio","master",_volume);c.Save("user://moonglass_ui.cfg");}
}
