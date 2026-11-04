#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using NguMach.Client.P1;

namespace Ngumach.VisualReboot;

/// <summary>Read-only narrative pages and actual inventory. Only an explicit final
/// page button emits a command; page/reply navigation never changes gameplay.</summary>
public partial class NativeDialoguePanel : CanvasLayer
{
    private sealed record Reply(string Label,string Text);
    private sealed record Entry(string Id,string QuestId,string Speaker,string State,string Command,
        string Title,string[] Pages,string[] Committed,Reply[] Replies,string[] Maps,string? Checkpoint);
    private sealed record Npc(string EntityId,string NpcId,string MapId,string Name);
    private readonly List<Entry> _entries=new();
    private readonly List<Npc> _npcs=new();
    private readonly Dictionary<string,string> _itemNames=new(StringComparer.Ordinal);
    private readonly Dictionary<string,Texture2D> _icons=new(StringComparer.Ordinal);
    private Control _root=null!;
    private PanelContainer _panel=null!;
    private VBoxContainer _content=null!,_inventoryRows=null!,_replyButtons=null!;
    private RichTextLabel _body=null!;
    private ScrollContainer _scroll=null!;
    private Label _title=null!,_status=null!,_pageInfo=null!;
    private Button _back=null!,_next=null!,_action=null!,_refresh=null!,_retry=null!;
    private NativeOnlineFrame _frame=new();
    private Entry? _entry;
    private string _npcId="",_fingerprint="";
    private string[] _pages=Array.Empty<string>();
    private int _page;
    private bool _inventory,_committed,_replyOpen,_ready;
    private string? _replyText,_waitingKind;

    public bool IsOpen {get;private set;}
    public event Action<string,string,string>? CommandRequested;
    public event Action? Closed;

    public override void _Ready()
    {
        Layer=100;
        LoadSource();
        BuildUi();
        GetViewport().SizeChanged+=ResizePanel;
        ResizePanel();
        _ready=true;
        _root.Visible=false;
    }

    private static JsonDocument Read(string path)=>
        JsonDocument.Parse(FileAccess.GetFileAsString(path).TrimStart('\uFEFF'));
    private static string Str(JsonElement e,string key)=>
        e.TryGetProperty(key,out var p)&&p.ValueKind==JsonValueKind.String?p.GetString()!:"";
    private static string[] Strings(JsonElement e,string key)=>
        e.TryGetProperty(key,out var p)&&p.ValueKind==JsonValueKind.Array?
        p.EnumerateArray().Select(v=>v.GetString()??"").ToArray():Array.Empty<string>();

    private void LoadSource()
    {
        using var data=Read("res://assets/combat_v1/dialogue_vi.json");
        foreach(var e in data.RootElement.GetProperty("entries").EnumerateArray())
        {
            var replies=e.TryGetProperty("replies",out var r)?r.EnumerateArray()
                .Select(x=>new Reply(Str(x,"label"),Str(x,"text"))).ToArray():Array.Empty<Reply>();
            string checkpoint=Str(e,"requiredCheckpoint");
            _entries.Add(new Entry(Str(e,"nodeId"),Str(e,"questId"),Str(e,"speakerId"),
                Str(e,"questState"),Str(e,"command"),Str(e,"title"),Strings(e,"pages"),
                Strings(e,"committedPages"),replies,Strings(e,"allowedMapIds"),
                string.IsNullOrEmpty(checkpoint)?null:checkpoint));
        }
        foreach(var n in data.RootElement.GetProperty("npcs").EnumerateArray())
            _npcs.Add(new Npc(Str(n,"entityId"),Str(n,"npcId"),Str(n,"mapId"),Str(n,"displayName")));
        if(FileAccess.FileExists("res://assets/combat_v1/item_names.json"))
        {
            using var names=Read("res://assets/combat_v1/item_names.json");
            if(names.RootElement.ValueKind==JsonValueKind.Object)
            foreach(var item in names.RootElement.EnumerateObject())
                if(item.Value.ValueKind==JsonValueKind.String)_itemNames[item.Name]=item.Value.GetString()!;
        }
        using var manifest=Read("res://assets/combat_v1/manifest.json");
        if(manifest.RootElement.TryGetProperty("questKit",out var kit))
        {
            var sheet=GD.Load<Texture2D>("res://assets/combat_v1/ben_mua_questkit.png");
            foreach(var item in kit.EnumerateObject())
            {
                var r=item.Value.GetProperty("rect");
                _icons[item.Name]=new AtlasTexture{Atlas=sheet,Region=new Rect2(
                    r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle()),FilterClip=true};
            }
        }
    }

    private void BuildUi()
    {
        _root=new Control{MouseFilter=Control.MouseFilterEnum.Stop};
        AddChild(_root);_root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        var backdrop=new ColorRect{Color=new Color(.015f,.025f,.025f,.78f),MouseFilter=Control.MouseFilterEnum.Stop};
        _root.AddChild(backdrop);backdrop.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _panel=new PanelContainer{MouseFilter=Control.MouseFilterEnum.Stop};
        _panel.AddThemeStyleboxOverride("panel",Box(Color.FromHtml("#152320"),Color.FromHtml("#ba9559"),2,12,18));
        _root.AddChild(_panel);
        _content=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};
        _content.AddThemeConstantOverride("separation",9);
        _panel.AddChild(_content);
        var header=new HBoxContainer();
        _title=new Label{Text="Hội thoại",SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,
            AutowrapMode=TextServer.AutowrapMode.WordSmart};
        _title.AddThemeFontSizeOverride("font_size",20);
        _title.AddThemeColorOverride("font_color",Color.FromHtml("#e7c783"));
        header.AddChild(_title);
        var close=Button("×",48);close.Pressed+=HidePanel;header.AddChild(close);
        _content.AddChild(header);
        _status=new Label{AutowrapMode=TextServer.AutowrapMode.WordSmart};
        _status.AddThemeFontSizeOverride("font_size",14);
        _status.AddThemeColorOverride("font_color",Color.FromHtml("#b7c4b4"));
        _content.AddChild(_status);
        _scroll=new ScrollContainer{SizeFlagsVertical=Control.SizeFlags.ExpandFill,
            HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled,CustomMinimumSize=new Vector2(0,150)};
        _content.AddChild(_scroll);
        var scrollContent=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};
        _scroll.AddChild(scrollContent);
        _body=new RichTextLabel{BbcodeEnabled=false,FitContent=true,ScrollActive=false,
            SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(0,120)};
        _body.AddThemeFontSizeOverride("normal_font_size",18);
        _body.AddThemeColorOverride("default_color",Color.FromHtml("#f0ead8"));
        scrollContent.AddChild(_body);
        _inventoryRows=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};
        _inventoryRows.AddThemeConstantOverride("separation",12);
        scrollContent.AddChild(_inventoryRows);
        _replyButtons=new VBoxContainer();
        _replyButtons.AddThemeConstantOverride("separation",5);
        _content.AddChild(_replyButtons);
        var nav=new HBoxContainer();
        nav.AddThemeConstantOverride("separation",8);
        _back=Button("Trước",90);_back.Pressed+=Back;nav.AddChild(_back);
        _pageInfo=new Label{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,HorizontalAlignment=HorizontalAlignment.Center,
            VerticalAlignment=VerticalAlignment.Center};
        _pageInfo.AddThemeFontSizeOverride("font_size",14);nav.AddChild(_pageInfo);
        _next=Button("Tiếp",90);_next.Pressed+=Next;nav.AddChild(_next);
        _action=Button("Đóng hội thoại",180);_action.Pressed+=FinalAction;nav.AddChild(_action);
        _content.AddChild(nav);
        var network=new HBoxContainer();network.AddThemeConstantOverride("separation",8);
        _refresh=Button("Làm mới",110);
        _refresh.Pressed+=()=>
        {
            if(_frame.ConnectionState==P1ConnectionState.Ready)_waitingKind=null;
            CommandRequested?.Invoke("REFRESH","","");Render();
        };
        network.AddChild(_refresh);
        _retry=Button("Thử lại thao tác",190);
        _retry.Pressed+=()=>CommandRequested?.Invoke("RETRY","","");
        network.AddChild(_retry);
        var spacer=new Control{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};network.AddChild(spacer);
        var leave=Button("Rời đi",100);leave.Pressed+=HidePanel;network.AddChild(leave);
        _content.AddChild(network);
    }

    private static StyleBoxFlat Box(Color fill,Color border,int thickness,int radius,int margin=8)=>new()
    {
        BgColor=fill,BorderColor=border,BorderWidthLeft=thickness,BorderWidthRight=thickness,
        BorderWidthTop=thickness,BorderWidthBottom=thickness,CornerRadiusTopLeft=radius,
        CornerRadiusTopRight=radius,CornerRadiusBottomLeft=radius,CornerRadiusBottomRight=radius,
        ContentMarginLeft=margin,ContentMarginRight=margin,ContentMarginTop=margin,ContentMarginBottom=margin
    };
    private static Button Button(string text,float width)
    {
        var button=new Button{Text=text,CustomMinimumSize=new Vector2(width,40)};
        button.AddThemeFontSizeOverride("font_size",17);
        button.AddThemeColorOverride("font_color",Color.FromHtml("#eee4c9"));
        button.AddThemeColorOverride("font_disabled_color",Color.FromHtml("#7f8e87"));
        button.AddThemeStyleboxOverride("normal",Box(Color.FromHtml("#25372e"),Color.FromHtml("#9a7e49"),1,6));
        button.AddThemeStyleboxOverride("hover",Box(Color.FromHtml("#3b4c37"),Color.FromHtml("#ddc284"),2,6));
        button.AddThemeStyleboxOverride("pressed",Box(Color.FromHtml("#485a40"),Color.FromHtml("#e8cc88"),2,6));
        button.AddThemeStyleboxOverride("disabled",Box(Color.FromHtml("#1b2724"),Color.FromHtml("#53604e"),1,6));
        return button;
    }

    private void ResizePanel()
    {
        if(_panel==null)return;
        var size=GetViewport().GetVisibleRect().Size;
        float w=Math.Min(700,Math.Max(280,size.X-40));
        float h=Math.Min(660,Math.Max(280,size.Y-40));
        _panel.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.Center);
        _panel.OffsetLeft=-w/2;_panel.OffsetRight=w/2;
        _panel.OffsetTop=-h/2;_panel.OffsetBottom=h/2;
    }

    public void ShowNpc(string npcId,NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _frame=frame;_inventory=false;_committed=false;_replyOpen=false;_replyText=null;
        _waitingKind=null;_entry=null;_page=0;
        _npcId=_npcs.FirstOrDefault(n=>n.EntityId==npcId)?.NpcId??npcId;
        SelectEntry(true);
        IsOpen=true;_root.Visible=true;ResizePanel();Render();
    }

    public void ShowInventory(NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _frame=frame;_inventory=true;_entry=null;_waitingKind=null;_replyOpen=false;
        IsOpen=true;_root.Visible=true;ResizePanel();Render();
    }

    public void HidePanel()
    {
        if(!IsOpen)return;
        IsOpen=false;_root.Visible=false;_waitingKind=null;_replyOpen=false;
        Closed?.Invoke();
    }

    private string? QuestState(string id)=>_frame.Quests.FirstOrDefault(q=>q.questId==id)?.state;

    private void SelectEntry(bool force)
    {
        string map=_frame.World?.mapId??_frame.WorldV2?.mapId??"";
        var candidates=_entries.Where(e=>e.QuestId=="P00-01"&&e.Speaker==_npcId&&e.Checkpoint==null&&
            (e.Maps.Length==0||e.Maps.Contains(map,StringComparer.Ordinal)))
            .Select(e=>(Entry:e,State:QuestState(e.QuestId)))
            .Where(x=>x.State==x.Entry.State||(x.State=="COMPLETED"&&x.Entry.Command=="TURN_IN"&&x.Entry.Committed.Length>0))
            .OrderByDescending(x=>x.State=="READY_TO_TURN_IN"?4:x.State=="ACTIVE"?3:x.State=="AVAILABLE"?2:1);
        var selected=candidates.FirstOrDefault();
        if(selected.Entry==null)
        {
            if(force||_entry!=null){_entry=null;_pages=Array.Empty<string>();_page=0;_committed=false;}
            return;
        }
        bool committed=selected.State=="COMPLETED";
        if(force||_entry?.Id!=selected.Entry.Id||_committed!=committed)
        {
            _entry=selected.Entry;_committed=committed;
            _pages=committed?_entry.Committed:_entry.Pages;_page=0;_replyOpen=false;_replyText=null;
        }
    }

    public void ApplyFrame(NativeOnlineFrame frame)
    {
        _frame=frame;
        if(!IsOpen||!_ready)return;
        if(!_inventory&&_entry!=null)
        {
            if(_waitingKind=="TURNIN"&&QuestState(_entry.QuestId)=="COMPLETED")
            {
                _waitingKind=null;_committed=true;_pages=_entry.Committed;_page=0;_replyOpen=false;
            }
            else if(_waitingKind=="ACCEPT"&&QuestState(_entry.QuestId)=="ACTIVE")
            {
                _waitingKind=null;SelectEntry(true);
            }
            else if(_waitingKind==null&&!_committed)SelectEntry(false);
        }
        string fingerprint=Fingerprint();
        if(fingerprint!=_fingerprint)Render();
    }

    private string Fingerprint()=>string.Join("|",_inventory,_npcId,_entry?.Id,_committed,_page,_replyOpen,
        _waitingKind,_frame.ConnectionState,_frame.Message,_frame.Inventory?.inventoryRevision,
        string.Join(";",_frame.Quests.Select(q=>q.questId+":"+q.state+":"+q.revision)),NpcInRange());

    private bool NpcInRange()
    {
        var self=_frame.World?.self??_frame.WorldV2?.self;
        if(self==null||_npcId.Length==0)return false;
        string map=_frame.World?.mapId??_frame.WorldV2?.mapId??"";
        var ids=new HashSet<string>(_npcs.Where(n=>n.NpcId==_npcId&&n.MapId==map).Select(n=>n.EntityId),StringComparer.Ordinal);
        if(_frame.World!=null)return _frame.World.entities.Any(e=>ids.Contains(e.entityId)&&
            (e.x-self.x)*(e.x-self.x)+(e.y-self.y)*(e.y-self.y)<=25);
        return _frame.WorldV2?.entities.Any(e=>ids.Contains(e.entityId)&&
            (e.x-self.x)*(e.x-self.x)+(e.y-self.y)*(e.y-self.y)<=25)==true;
    }

    private void Render()
    {
        _fingerprint=Fingerprint();
        _status.Text=_waitingKind!=null?"Đang chờ máy chủ xác nhận… "+_frame.Message:_frame.Message;
        _refresh.Disabled=string.IsNullOrEmpty(_frame.SessionId);
        _retry.Visible=_frame.ConnectionState==P1ConnectionState.UncertainMutation;
        _retry.Disabled=string.IsNullOrEmpty(_frame.SessionId);
        _body.Visible=!_inventory;_inventoryRows.Visible=_inventory;
        foreach(var child in _replyButtons.GetChildren()){_replyButtons.RemoveChild(child);child.QueueFree();}
        if(_inventory){RenderInventory();return;}
        string name=_npcs.FirstOrDefault(n=>n.NpcId==_npcId)?.Name??_npcId;
        _title.Text=name+(_entry==null?"":" · "+_entry.Title);
        if(_entry==null)
        {
            _body.Text="Không có hội thoại phù hợp với tiến độ hiện tại.";
            _pageInfo.Text="";_back.Visible=false;_next.Visible=false;
            _action.Visible=true;_action.Text="Đóng hội thoại";_action.Disabled=false;
            return;
        }
        _body.Text=_replyOpen?_replyText??"":_pages.Length>0?_pages[Math.Clamp(_page,0,_pages.Length-1)]:"";
        _pageInfo.Text=_replyOpen?"Lựa chọn":(_page+1)+" / "+Math.Max(1,_pages.Length);
        _back.Visible=_replyOpen||_page>0;
        _back.Text=_replyOpen?"Trở lại":"Trước";
        _next.Visible=!_replyOpen&&_page<_pages.Length-1;
        bool final=!_replyOpen&&_page>=_pages.Length-1;
        bool actionable=final&&!_committed&&_entry.Command is "ACCEPT" or "TURN_IN";
        _action.Visible=final;
        _action.Text=actionable?(_entry.Command=="ACCEPT"?"Nhận nhiệm vụ":"Xác nhận giao nhận"):"Đóng hội thoại";
        _action.Disabled=actionable&&(_waitingKind!=null||_frame.ConnectionState!=P1ConnectionState.Ready||
            QuestState(_entry.QuestId)!=_entry.State||!NpcInRange());
        if(final&&!_committed)
        foreach(var reply in _entry.Replies)
        {
            var button=Button(reply.Label,0);
            button.Pressed+=()=>{_replyOpen=true;_replyText=reply.Text;Render();_scroll.ScrollVertical=0;};
            _replyButtons.AddChild(button);
        }
    }

    private void Back()
    {
        if(_replyOpen){_replyOpen=false;_replyText=null;}
        else _page=Math.Max(0,_page-1);
        Render();_scroll.ScrollVertical=0;
    }
    private void Next(){if(_replyOpen||_page>=_pages.Length-1)return;_page++;Render();_scroll.ScrollVertical=0;}
    private void FinalAction()
    {
        if(_entry==null||_committed||_entry.Command=="NONE"){HidePanel();return;}
        if(_replyOpen||_page<_pages.Length-1||_waitingKind!=null||
            _frame.ConnectionState!=P1ConnectionState.Ready||QuestState(_entry.QuestId)!=_entry.State||!NpcInRange())return;
        string kind=_entry.Command=="TURN_IN"?"TURNIN":_entry.Command=="ACCEPT"?"ACCEPT":"";
        if(kind.Length==0){HidePanel();return;}
        _waitingKind=kind;
        CommandRequested?.Invoke(kind,_npcId,_entry.QuestId);
        Render();
    }

    private string ItemName(string id)
    {
        if(_itemNames.TryGetValue(id,out var name))return name;
        int variant=id.IndexOf("-R-",StringComparison.Ordinal);
        if(variant>0&&_itemNames.TryGetValue(id[..variant],out name))return name;
        return id;
    }

    private void RenderInventory()
    {
        _title.Text="Túi đồ";
        _back.Visible=false;_next.Visible=false;_action.Visible=false;_pageInfo.Text="";
        foreach(var child in _inventoryRows.GetChildren()){_inventoryRows.RemoveChild(child);child.QueueFree();}
        var inventory=_frame.Inventory;
        if(inventory==null){InventoryRow("Chưa có dữ liệu túi đồ. Chọn Làm mới để đọc lại.","");return;}
        foreach(var currency in inventory.currencies)InventoryRow(ItemName(currency.currencyId)+"  "+currency.amount,currency.currencyId);
        if(inventory.items.Length==0)InventoryRow("Túi đồ đang trống.","");
        foreach(var item in inventory.items)
        {
            string location=item.location switch{"BAG"=>"Trong túi","EQUIPPED"=>"Đang mặc","BANK"=>"Trong kho",_=>item.location};
            InventoryRow(ItemName(item.templateId)+"  ×"+item.stack+"\n"+location+" · Độ bền "+item.durability,item.templateId);
        }
    }

    private void InventoryRow(string text,string iconKey)
    {
        var row=new HBoxContainer();row.AddThemeConstantOverride("separation",12);
        if(_icons.TryGetValue(iconKey,out var texture))
        {
            row.AddChild(new TextureRect{Texture=texture,CustomMinimumSize=new Vector2(48,48),
                ExpandMode=TextureRect.ExpandModeEnum.IgnoreSize,StretchMode=TextureRect.StretchModeEnum.KeepAspectCentered,
                TextureFilter=Control.TextureFilterEnum.Nearest,MouseFilter=Control.MouseFilterEnum.Ignore});
        }
        var label=new Label{Text=text,AutowrapMode=TextServer.AutowrapMode.WordSmart,
            SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};
        label.AddThemeFontSizeOverride("font_size",18);
        label.AddThemeColorOverride("font_color",Color.FromHtml("#ece4ce"));
        row.AddChild(label);_inventoryRows.AddChild(row);
    }

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if(!IsOpen)return;
        if(@event is InputEventKey key&&key.Pressed&&key.Keycode==Key.Escape)HidePanel();
        GetViewport().SetInputAsHandled();
    }

    public override void _ExitTree()
    {
        _ready=false;
        if(GetViewport()!=null)GetViewport().SizeChanged-=ResizePanel;
        CommandRequested=null;Closed=null;
    }
}
