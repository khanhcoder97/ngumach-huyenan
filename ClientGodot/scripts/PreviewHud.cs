#nullable enable
using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>MoonGlass HUD. All gameplay values are detached authoritative data.</summary>
public partial class PreviewHud : Node2D
{
    public Vector2 Coordinates,Facing=Vector2.Up;
    public bool Compact,Online,LowFx;
    public string StatusText="Khám phá Bến Mưa bằng WASD hoặc phím mũi tên.",LastSkill="";
    public event Action<int>? SkillPressed;
    public event Action? AttackPressed,InventoryPressed,InteractPressed,RetryPressed,JournalPressed;
    public event Action<string>? MenuPressed;
    private NativeOnlineFrame? _frame;
    private Font _font=null!;
    private Texture2D _skills=null!;
    private readonly Rect2[] _icons=new Rect2[6];
    private MoonMapView _map=null!;
    private int _hover=-1,_questTab;
    private bool _attackHover,_chat;
    private double _press;
    private string _oldMessage="";
    private readonly Queue<string> _messages=new();
    private readonly List<(Rect2 Rect,string Icon,string Tip,Action Action)> _buttons=new();
    public static Vector2 AttackCenter=>new(1172,624);
    public static Vector2[] SkillCenters()=>Enumerable.Range(0,6).Select(i=>AttackCenter+Vector2.FromAngle(Mathf.DegToRad(176+i*26))*114).ToArray();
    public override void _Ready()
    {
        _font=ThemeDB.FallbackFont;
        _skills=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_skill_icons.png");
        using var manifest=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        for(int i=0;i<6;i++){var f=manifest.RootElement.GetProperty("uiIcons")[i];var r=f.GetProperty("rect");var b=f.GetProperty("contentBounds");_icons[i]=new Rect2(r[0].GetSingle()+b[0].GetSingle()-2,r[1].GetSingle()+b[1].GetSingle()-2,b[2].GetSingle()-b[0].GetSingle()+4,b[3].GetSingle()-b[1].GetSingle()+4);}
        var avatar=MoonGlassTheme.Image(MoonGlassTheme.Portrait,new Vector2(78,78),false);avatar.Position=new Vector2(29,31);avatar.Size=new Vector2(78,78);
        var shader=new Shader{Code="shader_type canvas_item; void fragment(){ if(distance(UV,vec2(0.5))>0.49){discard;} vec2 p=(UV-vec2(0.5))*0.78+vec2(0.53,0.49); COLOR=texture(TEXTURE,p); }"};
        avatar.Material=new ShaderMaterial{Shader=shader};AddChild(avatar);
        _map=new MoonMapView{Position=new Vector2(1060,54),Size=new Vector2(188,110)};AddChild(_map);
        AddButton(new Rect2(22,134,40,38),"Character","Nhân vật · C",()=>MenuPressed?.Invoke("Character"));
        AddButton(new Rect2(68,134,40,38),"Inventory","Túi đồ · I",()=>InventoryPressed?.Invoke());
        AddButton(new Rect2(114,134,40,38),"Skills","Kỹ năng · K",()=>MenuPressed?.Invoke("Skills"));
        AddButton(new Rect2(160,134,40,38),"Journal","Nhiệm vụ · J",()=>JournalPressed?.Invoke());
        AddButton(new Rect2(206,134,40,38),"Interact","Tương tác · E",()=>InteractPressed?.Invoke());
        AddButton(new Rect2(252,134,40,38),"Retry","Thử lại thao tác · R",()=>RetryPressed?.Invoke());
        var top=new[]{("Guild","Bang hội"),("Activities","Hoạt động"),("Mail","Thư tín"),("Settings","Cài đặt")};
        for(int i=0;i<top.Length;i++){var entry=top[i];AddButton(new Rect2(844+i*48,22,40,38),entry.Item1,entry.Item2,()=>MenuPressed?.Invoke(entry.Item1));}
        string[] dock={"Character","Inventory","Skills","Journal","WorldMap","Forge","Codex","Appearance","Social","Settings"};
        string[] names={"Nhân vật","Túi đồ","Kỹ năng","Nhiệm vụ","Bản đồ","Lò rèn","Bách khoa","Ngoại trang","Bạn bè","Cài đặt"};
        for(int i=0;i<dock.Length;i++){string id=dock[i],label=names[i];AddButton(new Rect2(397+i*48,665,39,36),id,label,()=>{if(id=="Inventory")InventoryPressed?.Invoke();else if(id=="Journal")JournalPressed?.Invoke();else MenuPressed?.Invoke(id);});}
        AddButton(new Rect2(22,608,40,32),"Chat","Nhật ký hệ thống",()=>_chat=!_chat);
        QueueRedraw();
    }
    private void AddButton(Rect2 rect,string icon,string tip,Action action)=>_buttons.Add((rect,icon,tip,action));
    public void ApplyOnline(NativeOnlineFrame frame){Online=true;_frame=frame;StatusText=frame.Message;_map.Frame=frame;QueueRedraw();}
    public override void _Process(double delta)
    {
        _press=Math.Max(0,_press-delta);var mouse=GetLocalMousePosition();_hover=Array.FindIndex(SkillCenters(),p=>p.DistanceTo(mouse)<=25);_attackHover=mouse.DistanceTo(AttackCenter)<=52;
        _map.Facing=Facing;
        if(StatusText!=_oldMessage){_oldMessage=StatusText;_messages.Enqueue(Friendly(StatusText));while(_messages.Count>6)_messages.Dequeue();}
        QueueRedraw();
    }
    private static string Friendly(string text)
    {
        if(text.Contains("out_of_range",StringComparison.Ordinal))return "Hãy tới gần mục tiêu hơn.";
        if(text.Contains("TURNIN",StringComparison.Ordinal)&&text.Contains("xác nhận",StringComparison.Ordinal))return "Đã giao nhận nhiệm vụ thành công.";
        if(text.Contains("ACCEPT",StringComparison.Ordinal)&&text.Contains("xác nhận",StringComparison.Ordinal))return "Đã nhận nhiệm vụ. Mở J để theo dõi.";
        return text;
    }
    private void Text(Vector2 at,string text,int size=14,Color? color=null)
    {_font??=ThemeDB.FallbackFont;DrawString(_font,at+Vector2.Down,text,HorizontalAlignment.Left,-1,size,new Color(.01f,.02f,.08f,.65f));DrawString(_font,at,text,HorizontalAlignment.Left,-1,size,color??MoonGlassTheme.Ink);}
    private void Center(Vector2 p,string text,int size=14,Color? color=null)=>Text(p-new Vector2(_font.GetStringSize(text,HorizontalAlignment.Left,-1,size).X/2,0),text,size,color);
    private void Panel(Rect2 rect,float alpha=.76f)
    {DrawStyleBox(MoonGlassTheme.Box(new Color(.15f,.17f,.29f,alpha),new Color(.65f,.7f,.96f,.43f),10,0),rect);DrawLine(rect.Position+new Vector2(13,1),rect.Position+new Vector2(rect.Size.X-13,1),new Color(.8f,.85f,1,.2f));}
    private void Bar(Rect2 rect,float value,Color low,Color high)
    {
        DrawStyleBox(MoonGlassTheme.Box(new Color(.05f,.06f,.14f,.72f),new Color(.65f,.7f,.94f,.32f),4,0),rect);
        float width=(rect.Size.X-2)*Mathf.Clamp(value,0,1);
        if(width<1)return;
        int n=Math.Max(1,(int)(width/8));
        for(int i=0;i<n;i++)DrawRect(new Rect2(rect.Position+new Vector2(1+width*i/n,1),new Vector2(width/n+.2f,rect.Size.Y-2)),low.Lerp(high,i/(float)n));
        DrawLine(rect.Position+new Vector2(2,2),rect.Position+new Vector2(width,2),new Color(1,1,1,.25f));
    }
    public override void _UnhandledInput(InputEvent ev)
    {
        if(ev is not InputEventMouseButton m||m.ButtonIndex!=MouseButton.Left||!m.Pressed)return;
        if(m.Position.DistanceTo(AttackCenter)<=52){_press=.16;AttackPressed?.Invoke();GetViewport().SetInputAsHandled();return;}
        var slots=SkillCenters();for(int i=0;i<6;i++)if(m.Position.DistanceTo(slots[i])<=25){_press=.16;SkillPressed?.Invoke(i);GetViewport().SetInputAsHandled();return;}
        foreach(var b in _buttons)if(b.Rect.HasPoint(m.Position)){b.Action();GetViewport().SetInputAsHandled();return;}
        if(new Rect2(22,22,348,100).HasPoint(m.Position)){MenuPressed?.Invoke("Character");GetViewport().SetInputAsHandled();return;}
        if(new Rect2(1050,22,208,160).HasPoint(m.Position)){MenuPressed?.Invoke("WorldMap");GetViewport().SetInputAsHandled();return;}
        if(new Rect2(22,192,278,30).HasPoint(m.Position)){_questTab=Math.Clamp((int)((m.Position.X-22)/92),0,2);GetViewport().SetInputAsHandled();return;}
        if(new Rect2(22,222,278,132).HasPoint(m.Position)){JournalPressed?.Invoke();GetViewport().SetInputAsHandled();}
    }
    public override void _Draw()
    {
        if(_font==null)return;
        Panel(new Rect2(22,22,348,100),.79f);
        DrawCircle(new Vector2(68,70),42,new Color(.3f,.33f,.55f,.8f));DrawArc(new Vector2(68,70),43,0,Mathf.Tau,64,MoonGlassTheme.Gold,1.3f,true);
        DrawArc(new Vector2(68,70),40,-Mathf.Pi*.7f,Mathf.Pi*.65f,48,MoonGlassTheme.Silver,1.2f,true);
        Text(new Vector2(120,43),"MINH KIẾM",17);Text(new Vector2(235,42),Online?"KIẾM KHÁCH":"THỬ GIAO DIỆN",10,MoonGlassTheme.Gold);
        var self=_frame?.World?.self;int hp=self?.hp??120,maxHp=self?.maxHp??120,mp=self?.mp??100,maxMp=self?.maxMp??100;
        Bar(new Rect2(120,51,233,15),hp/(float)Math.Max(1,maxHp),Color.FromHtml("#b84478"),MoonGlassTheme.Hp);Center(new Vector2(236,63),$"{hp} / {maxHp}",10);
        Bar(new Rect2(120,73,233,12),mp/(float)Math.Max(1,maxMp),Color.FromHtml("#4265b8"),MoonGlassTheme.Blue);Center(new Vector2(236,83),$"{mp} / {maxMp}",9);
        DrawCircle(new Vector2(124,101),3,Online?Color.FromHtml("#83ddc3"):MoonGlassTheme.Violet);
        Text(new Vector2(134,105),Online?"Bến Mưa":"Ngoại tuyến",11,MoonGlassTheme.Muted);
        long? coins=_frame?.Inventory?.currencies?.FirstOrDefault(c=>c.currencyId=="COIN")?.amount;
        Text(new Vector2(252,105),Online?"Đồng  "+(coins?.ToString()??"—"):"Kiếm ý",11,MoonGlassTheme.Gold);
        if(!Online||self!=null)for(int i=0;i<5;i++)DrawCircle(new Vector2(328+i*5,103),1.5f,i<(self?.swordIntent??0)?MoonGlassTheme.Violet:new Color(.61f,.64f,.8f,.3f));
        Panel(new Rect2(22,192,278,154),.65f);
        var tabs=new[]{"Chính tuyến","Hằng ngày","Sự kiện"};
        for(int i=0;i<3;i++){if(i==_questTab)DrawRect(new Rect2(24+i*92,194,90,27),new Color(.44f,.44f,.7f,.38f));Center(new Vector2(69+i*92,212),tabs[i],12,i==_questTab?MoonGlassTheme.Ink:MoonGlassTheme.Muted);}
        DrawLine(new Vector2(34,223),new Vector2(288,223),new Color(.65f,.68f,.9f,.2f));
        var q=NativeQuestCatalog.Tracked(_frame);
        if(_questTab==0)
        {
            Text(new Vector2(36,247),q!=null?NativeQuestCatalog.Find(q.questId)?.Title??"Nhật ký":"Hành trình Bến Mưa",15,MoonGlassTheme.Gold);
            var summary=Online?NativeQuestCatalog.Summary(q):"Khám phá ngôi làng bên dòng nước.";
            Text(new Vector2(36,272),summary.Length>35?summary[..32]+"…":summary,12);
            Text(new Vector2(36,296),q!=null?NativeQuestCatalog.StateLabel(q.state):"WASD · di chuyển  /  E · tương tác",11,MoonGlassTheme.Muted);
            Text(new Vector2(36,329),"J  Mở nhật ký",11,MoonGlassTheme.Silver);
        }
        else{Text(new Vector2(36,254),_questTab==1?"Nhiệm vụ hằng ngày":"Sự kiện đang diễn ra",14,MoonGlassTheme.Gold);Text(new Vector2(36,281),"Chưa có dữ liệu trong phiên này.",12,MoonGlassTheme.Muted);}
        Panel(new Rect2(1050,22,208,160),.8f);Text(new Vector2(1063,43),"BẾN MƯA",13,MoonGlassTheme.Ink);Text(new Vector2(1230,43),"N",11,MoonGlassTheme.Gold);
        Text(new Vector2(1063,177),"M  Bản đồ khu vực",10,MoonGlassTheme.Muted);
        Panel(new Rect2(385,658,501,49),.72f);
        foreach(var b in _buttons)
        {
            bool hover=b.Rect.HasPoint(GetLocalMousePosition());
            DrawStyleBox(MoonGlassTheme.Box(new Color(.2f,.23f,.4f,hover?.95f:.64f),new Color(.65f,.72f,1,hover?.8f:.27f),7,0),b.Rect);
            DrawTextureRect(MoonGlassIcons.Get(b.Icon),new Rect2(b.Rect.GetCenter()-Vector2.One*11,Vector2.One*22),false,hover?Colors.White:MoonGlassTheme.Silver);
        }
        var center=AttackCenter;
        DrawCircle(center,57,new Color(.07f,.1f,.22f,.22f));DrawCircle(center,52,new Color(.18f,.2f,.36f,.82f));
        DrawCircle(center,46,new Color(.35f,.34f,.55f,_attackHover?.85f:.5f));
        DrawArc(center,52,0,Mathf.Tau,80,MoonGlassTheme.Gold,_press>0?3:1.5f,true);DrawArc(center,47,-2.8f,-.5f,32,new Color(.8f,.83f,1,.45f),1,true);
        DrawTextureRect(MoonGlassIcons.Get("Skills"),new Rect2(center+new Vector2(-19,-32),new Vector2(38,38)),false,MoonGlassTheme.Gold);
        Center(center+new Vector2(0,23),"TẤN CÔNG",11,MoonGlassTheme.Ink);
        var positions=SkillCenters();
        for(int i=0;i<6;i++)
        {
            var p=positions[i];bool disabled=Online&&i>=3;
            DrawCircle(p,27,new Color(.03f,.05f,.15f,.35f));DrawCircle(p,25,new Color(.21f,.24f,.42f,.78f));
            DrawArc(p,25,0,Mathf.Tau,48,disabled?new Color(.5f,.55f,.7f,.5f):_hover==i?MoonGlassTheme.Gold:MoonGlassTheme.Silver,_hover==i?2.3f:1,true);
            var source=_icons[i];var size=source.Size*(34/Math.Max(source.Size.X,source.Size.Y));DrawTextureRectRegion(_skills,new Rect2(p-size/2,size),source,disabled?new Color(.55f,.57f,.74f,.62f):Colors.White);
            DrawCircle(p+new Vector2(17,18),8,new Color(.15f,.18f,.34f,.96f));Center(p+new Vector2(17,22),(i+1).ToString(),9,MoonGlassTheme.Ink);
        }
        Panel(new Rect2(22,650,327,53),.62f);
        Text(new Vector2(34,670),$"{Coordinates.X:0.0}, {Coordinates.Y:0.0}    ·    {Engine.GetFramesPerSecond()} FPS",11,MoonGlassTheme.Muted);
        string status=Friendly(StatusText);Text(new Vector2(34,691),status.Length>43?status[..40]+"…":status,11);
        if(_chat){Panel(new Rect2(22,465,327,135),.86f);Text(new Vector2(35,486),"Nhật ký hệ thống",13,MoonGlassTheme.Gold);int y=509;foreach(var message in _messages.TakeLast(4)){Text(new Vector2(35,y),message.Length>42?message[..39]+"…":message,11,MoonGlassTheme.Muted);y+=21;}}
        string? tip=_hover>=0?SkillVfxPlayer.Names[_hover]:_buttons.Where(b=>b.Rect.HasPoint(GetLocalMousePosition())).Select(b=>b.Tip).FirstOrDefault();
        if(tip!=null)
        {
            var at=GetLocalMousePosition()+new Vector2(-95,-65);at.X=Mathf.Clamp(at.X,16,1020);at.Y=Mathf.Clamp(at.Y,20,640);
            Panel(new Rect2(at,new Vector2(240,_hover>=0?49:31)),.96f);Text(at+new Vector2(10,20),tip,13,MoonGlassTheme.Ink);
            if(_hover>=0)Text(at+new Vector2(10,38),Online&&_hover>=3?"Chưa khả dụng trong phiên này":"Phím "+(_hover+1),10,MoonGlassTheme.Muted);
        }
    }
}
