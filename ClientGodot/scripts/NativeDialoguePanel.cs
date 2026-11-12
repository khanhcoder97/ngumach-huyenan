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
    private Control _root=null!,_pageNavigation=null!;
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
    private bool _inventory,_journal,_committed,_replyOpen,_ready;
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
        _root=new Control{MouseFilter=Control.MouseFilterEnum.Stop,Theme=MoonGlassTheme.Create()};
        AddChild(_root);_root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        var backdrop=new ColorRect{Color=new Color(.055f,.065f,.15f,.22f),MouseFilter=Control.MouseFilterEnum.Stop};
        _root.AddChild(backdrop);backdrop.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _panel=new PanelContainer{MouseFilter=Control.MouseFilterEnum.Stop};
        _panel.AddThemeStyleboxOverride("panel",MoonGlassTheme.Box(new Color(.17f,.18f,.31f,.84f),new Color(.69f,.73f,.94f,.58f),12,18));
        _root.AddChild(_panel);
        _content=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};_content.AddThemeConstantOverride("separation",10);_panel.AddChild(_content);
        var header=new HBoxContainer();header.AddThemeConstantOverride("separation",12);
        _headerIcon=MoonGlassTheme.Image(MoonGlassIcons.Get("Journal"),new Vector2(30,30),false);_headerIcon.SizeFlagsHorizontal=Control.SizeFlags.ShrinkBegin;header.AddChild(_headerIcon);
        _title=new Label{Text="Hội thoại",SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,AutowrapMode=TextServer.AutowrapMode.WordSmart};
        _title.AddThemeFontSizeOverride("font_size",23);_title.AddThemeColorOverride("font_color",MoonGlassTheme.Ink);header.AddChild(_title);
        var close=Button("×",40);close.TooltipText="Đóng · Esc";close.Pressed+=HidePanel;header.AddChild(close);_content.AddChild(header);
        _status=MoonGlassTheme.Label("",12,MoonGlassTheme.Muted);_content.AddChild(_status);
        var line=new HSeparator();line.AddThemeStyleboxOverride("separator",new StyleBoxLine{Color=new Color(.65f,.7f,.9f,.28f),Thickness=1});_content.AddChild(line);
        var main=new HBoxContainer{SizeFlagsVertical=Control.SizeFlags.ExpandFill};main.AddThemeConstantOverride("separation",18);_content.AddChild(main);
        _sidebarScroll=new ScrollContainer{CustomMinimumSize=new Vector2(157,0),HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled,SizeFlagsVertical=Control.SizeFlags.ExpandFill};main.AddChild(_sidebarScroll);
        _sidebar=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};_sidebar.AddThemeConstantOverride("separation",5);_sidebarScroll.AddChild(_sidebar);BuildNavigation();
        _speakerArt=new VBoxContainer{CustomMinimumSize=new Vector2(126,0)};
        _speakerPortrait=MoonGlassTheme.Image(MoonGlassTheme.Hero(),new Vector2(120,170));_speakerArt.AddChild(_speakerPortrait);main.AddChild(_speakerArt);
        _scroll=new ScrollContainer{SizeFlagsVertical=Control.SizeFlags.ExpandFill,SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,
            HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled,CustomMinimumSize=new Vector2(0,120)};main.AddChild(_scroll);
        var scrollContent=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};_scroll.AddChild(scrollContent);
        _body=new RichTextLabel{BbcodeEnabled=false,FitContent=true,ScrollActive=false,SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(0,110)};
        _body.AddThemeFontSizeOverride("normal_font_size",18);_body.AddThemeColorOverride("default_color",MoonGlassTheme.Ink);scrollContent.AddChild(_body);
        _inventoryRows=new VBoxContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};_inventoryRows.AddThemeConstantOverride("separation",12);scrollContent.AddChild(_inventoryRows);
        _replyButtons=new VBoxContainer();_replyButtons.AddThemeConstantOverride("separation",5);_content.AddChild(_replyButtons);
        var nav=new HBoxContainer();_pageNavigation=nav;nav.AddThemeConstantOverride("separation",8);
        _back=Button("Trước",90);_back.Pressed+=Back;nav.AddChild(_back);
        _pageInfo=new Label{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill,HorizontalAlignment=HorizontalAlignment.Center,VerticalAlignment=VerticalAlignment.Center};
        _pageInfo.AddThemeFontSizeOverride("font_size",13);_pageInfo.AddThemeColorOverride("font_color",MoonGlassTheme.Muted);nav.AddChild(_pageInfo);
        _next=Button("Tiếp",90);_next.Pressed+=Next;nav.AddChild(_next);
        _action=MoonGlassTheme.Button("Đóng hội thoại",180,true);_action.Pressed+=FinalAction;nav.AddChild(_action);_content.AddChild(nav);
        var network=new HBoxContainer();network.AddThemeConstantOverride("separation",8);
        _refresh=Button("Làm mới",100);_refresh.Pressed+=()=>{if(_frame.ConnectionState==P1ConnectionState.Ready)_waitingKind=null;CommandRequested?.Invoke("REFRESH","","");Render();};network.AddChild(_refresh);
        _retry=MoonGlassTheme.Button("Thử lại thao tác",170,true);_retry.Pressed+=()=>CommandRequested?.Invoke("RETRY","","");network.AddChild(_retry);
        network.AddChild(new Control{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill});
        var leave=Button("Rời đi",100);leave.Pressed+=HidePanel;network.AddChild(leave);_content.AddChild(network);
    }

    private static Button Button(string text,float width)=>MoonGlassTheme.Button(text,width);

    private void ResizePanel()
    {
        if(_panel==null)return;
        var size=GetViewport().GetVisibleRect().Size;
        float w=Math.Min(_inventory?1120:880,Math.Max(300,size.X-48));
        float h=Math.Min(_inventory?620:510,Math.Max(300,size.Y-48));
        _panel.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.Center);
        _panel.OffsetLeft=-w/2;_panel.OffsetRight=w/2;
        _panel.OffsetTop=-h/2;_panel.OffsetBottom=h/2;
    }

    public void ShowNpc(string npcId,NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _frame=frame;_inventory=false;_journal=false;_committed=false;_replyOpen=false;_replyText=null;
        _waitingKind=null;_entry=null;_page=0;
        _npcId=_npcs.FirstOrDefault(n=>n.EntityId==npcId)?.NpcId??npcId;
        SelectEntry(true);
        IsOpen=true;_root.Visible=true;ResizePanel();Render();
    }

    public void ShowInventory(NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _section="Inventory";_frame=frame;_inventory=true;_journal=false;_entry=null;_waitingKind=null;_replyOpen=false;
        IsOpen=true;_root.Visible=true;ResizePanel();Render();
    }

    public void ShowJournal(NativeOnlineFrame frame)
    {
        if(!_ready)return;
        _section="Journal";_frame=frame;_inventory=true;_journal=true;_entry=null;_waitingKind=null;_replyOpen=false;
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
        var candidates=_entries.Where(e=>e.QuestId.StartsWith("P00-",StringComparison.Ordinal)&&e.Speaker==_npcId&&e.Checkpoint==null&&
            (e.Maps.Length==0||e.Maps.Contains(map,StringComparer.Ordinal)))
            .Select(e=>(Entry:e,State:QuestState(e.QuestId)))
            .Where(x=>x.State==x.Entry.State||(x.State=="COMPLETED"&&x.Entry.Command=="TURN_IN"&&x.Entry.Committed.Length>0))
            .OrderByDescending(x=>x.State=="READY_TO_TURN_IN"?4:x.State=="ACTIVE"?3:x.State=="AVAILABLE"?2:1)
            .ThenBy(x=>x.Entry.QuestId,StringComparer.Ordinal);
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
        UpdateLiveWorkspace();
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

    private string Fingerprint()=>string.Join("|",_section,_inventory,_journal,_npcId,_entry?.Id,_committed,_page,_replyOpen,
        _waitingKind,_frame.ConnectionState,_frame.Message,_frame.Inventory?.inventoryRevision,
        string.Join(";",_frame.Quests.Select(q=>q.questId+":"+q.state+":"+q.revision+":"+
            string.Join(",",q.objectiveCounters.OrderBy(p=>p.Key,StringComparer.Ordinal).Select(p=>p.Key+"="+p.Value)))),NpcInRange());

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
        _status.Text=_waitingKind!=null?"Đang xác nhận thao tác…":_frame.ConnectionState==P1ConnectionState.Ready?"Hành trình được đồng bộ với nhân vật của bạn.":"Kết nối để đồng bộ dữ liệu nhân vật.";
        _sidebarScroll.Visible=_inventory;_speakerArt.Visible=!_inventory;_pageNavigation.Visible=!_inventory;
        _refresh.Disabled=string.IsNullOrEmpty(_frame.SessionId);
        _retry.Visible=_frame.ConnectionState==P1ConnectionState.UncertainMutation;
        _retry.Disabled=string.IsNullOrEmpty(_frame.SessionId);
        _body.Visible=!_inventory;_inventoryRows.Visible=_inventory;
        foreach(var child in _replyButtons.GetChildren()){_replyButtons.RemoveChild(child);child.QueueFree();}
        if(_inventory){RenderWorkspace();return;}
        string name=_npcs.FirstOrDefault(n=>n.NpcId==_npcId)?.Name??_npcId;
        _headerIcon.Texture=MoonGlassIcons.Get("Journal");
        _speakerPortrait.Texture=_icons.TryGetValue(_npcId,out var art)?art:MoonGlassTheme.Hero();
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

    private void RenderJournal()
    {
        _title.Text="Nhật ký · Bến Mưa";
        _back.Visible=false;_next.Visible=false;_action.Visible=false;_pageInfo.Text="";
        foreach(var child in _inventoryRows.GetChildren()){_inventoryRows.RemoveChild(child);child.QueueFree();}
        foreach(var card in NativeQuestCatalog.All)
        {
            var q=_frame.Quests.FirstOrDefault(q=>q.questId==card.Id);
            var panel=MoonGlassTheme.Card(new Color(.29f,.3f,.47f,.48f));
            var column=new VBoxContainer();column.AddThemeConstantOverride("separation",6);panel.AddChild(column);
            void Line(string text,int size,Color color)
            {var label=new Label{Text=text,AutowrapMode=TextServer.AutowrapMode.WordSmart};label.AddThemeFontSizeOverride("font_size",size);label.AddThemeColorOverride("font_color",color);column.AddChild(label);}
            bool locked=q==null||q.state=="LOCKED";
            Line(locked?"Chặng chưa mở":card.Title,18,Color.FromHtml("#e5cda9"));
            Line(NativeQuestCatalog.StateLabel(q?.state),14,Color.FromHtml("#bdc5e5"));
            if(locked)Line("Chặng này chưa mở trong phiên hiện tại.",15,Color.FromHtml("#bdc5e5"));
            else
            {
                string excerpt=q!.state=="COMPLETED"?card.Completed:q.state=="AVAILABLE"?card.Offer:card.Clue;
                Line(excerpt,15,Color.FromHtml("#f3f3ff"));
                foreach(var obj in card.Objectives)
                {q.objectiveCounters.TryGetValue(obj.Id,out int count);Line(obj.Label+": "+count+" / "+obj.Count,14,Color.FromHtml("#b8c7f3"));}
                foreach(var extra in q.objectiveCounters.Where(p=>!card.Objectives.Any(o=>o.Id==p.Key)))
                    Line("Tiến độ bổ sung: "+extra.Value,14,Color.FromHtml("#b8c7f3"));
            }
            _inventoryRows.AddChild(panel);
        }
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
        CommandRequested=null;Closed=null;DisplaySettingsChanged=null;
    }
}
