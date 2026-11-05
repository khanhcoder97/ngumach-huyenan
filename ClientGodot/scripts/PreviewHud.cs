using Godot;
using System;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Live HUD. Online values are read from detached authoritative snapshots.</summary>
public partial class PreviewHud : Node2D
{
    public Vector2 Coordinates;
    public bool Compact, Online;
    public string StatusText="WASD / phím mũi tên để di chuyển.";
    public string LastSkill="";
    public bool LowFx;
    public event Action<int>? SkillPressed;
    public event Action? AttackPressed,InventoryPressed,InteractPressed,RetryPressed,JournalPressed;
    private NativeOnlineFrame? _frame;
    public static Vector2 AttackCenter=>new(1172,624);
    public static Vector2[] SkillCenters()
    {
        var points=new Vector2[6];
        for(int i=0;i<6;i++){float a=Mathf.DegToRad(176+i*26);points[i]=AttackCenter+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*114;}
        return points;
    }
    private readonly Color _panel=new(.035f,.065f,.055f,.96f);
    private readonly Color _bronze=Color.FromHtml("#be9b53"),_ink=Color.FromHtml("#eee6cc");
    private Font _font=null!;
    private Texture2D _skillTexture=null!;
    private readonly Rect2[] _skillIconRects=new Rect2[6];
    private int _hover=-1;
    public override void _Ready()
    {
        _font=ThemeDB.FallbackFont;
        _skillTexture=GD.Load<Texture2D>("res://assets/combat_v1/minh_kiem_skill_icons.png");
        using var manifest=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        for(int i=0;i<6;i++)
        {
            var icon=manifest.RootElement.GetProperty("uiIcons")[i];var r=icon.GetProperty("rect");var b=icon.GetProperty("contentBounds");
            _skillIconRects[i]=new Rect2(r[0].GetSingle()+b[0].GetSingle()-2,r[1].GetSingle()+b[1].GetSingle()-2,
                b[2].GetSingle()-b[0].GetSingle()+4,b[3].GetSingle()-b[1].GetSingle()+4);
        }
        QueueRedraw();
    }
    public override void _Process(double delta)
    {
        int hover=-1;var at=GetLocalMousePosition();var slots=SkillCenters();
        for(int i=0;i<6;i++)if(at.DistanceTo(slots[i])<=23){hover=i;break;}
        if(hover!=_hover){_hover=hover;QueueRedraw();}
    }
    public void ApplyOnline(NativeOnlineFrame frame){Online=true;_frame=frame;StatusText=frame.Message;QueueRedraw();}
    private void Text(Vector2 at,string text,int size=14,Color? color=null)=>
        DrawString(_font,at,text,HorizontalAlignment.Left,-1,size,color??_ink);
    private void Panel(Rect2 r){DrawRect(r,_panel);DrawRect(r,_bronze,false,2);}
    public override void _UnhandledInput(InputEvent @event)
    {
        if(@event is not InputEventMouseButton m||m.ButtonIndex!=MouseButton.Left||!m.Pressed)return;
        if(m.Position.DistanceTo(AttackCenter)<=48){AttackPressed?.Invoke();GetViewport().SetInputAsHandled();return;}
        var slots=SkillCenters();
        for(int i=0;i<6;i++)if(m.Position.DistanceTo(slots[i])<=23){SkillPressed?.Invoke(i);GetViewport().SetInputAsHandled();return;}
        if(new Rect2(16,236,90,32).HasPoint(m.Position)){InventoryPressed?.Invoke();GetViewport().SetInputAsHandled();}
        else if(new Rect2(112,236,90,32).HasPoint(m.Position)){InteractPressed?.Invoke();GetViewport().SetInputAsHandled();}
        else if(new Rect2(208,236,90,32).HasPoint(m.Position)){RetryPressed?.Invoke();GetViewport().SetInputAsHandled();}
        else if(new Rect2(16,128,282,98).HasPoint(m.Position)){JournalPressed?.Invoke();GetViewport().SetInputAsHandled();}
    }
    public override void _Draw()
    {
        if(_font==null)return;
        Panel(new Rect2(16,16,282,100));
        Text(new Vector2(28,38),Online?"MINH KIẾM · ONLINE LOCAL":"MINH KIẾM · THỬ HÌNH ẢNH",14,_bronze);
        var self=_frame?.World?.self;
        int hp=self?.hp??120,maxHp=self?.maxHp??120,mp=self?.mp??100,maxMp=self?.maxMp??100;
        DrawRect(new Rect2(28,49,254,13),Color.FromHtml("#392c2a"));
        DrawRect(new Rect2(29,50,252*Mathf.Clamp(hp/(float)Math.Max(1,maxHp),0,1),11),Color.FromHtml("#b95650"));
        Text(new Vector2(112,60),$"{hp} / {maxHp}",11);
        DrawRect(new Rect2(28,69,254,11),Color.FromHtml("#284342"));
        DrawRect(new Rect2(29,70,252*Mathf.Clamp(mp/(float)Math.Max(1,maxMp),0,1),9),Color.FromHtml("#428fa3"));
        Text(new Vector2(113,79),$"{mp} / {maxMp}",10);
        var coins=_frame?.Inventory?.currencies?.FirstOrDefault(c=>c.currencyId=="COIN")?.amount;
        Text(new Vector2(28,102),Online?(coins.HasValue?$"Đồng: {coins.Value}":"Đang đọc túi đồ..."):"1–6: thử VFX · Space: đánh mẫu",13);
        Panel(new Rect2(16,128,282,98));
        Text(new Vector2(28,151),Compact?"Camera 48 × 27 WU":"Camera 64 × 36 WU",14,_bronze);
        if(Online)
        {
            var q=NativeQuestCatalog.Tracked(_frame);
            string title=q!=null?NativeQuestCatalog.Find(q.questId)?.Title??"Nhật ký":"Nhật ký · Bến Mưa";
            string progress=NativeQuestCatalog.Summary(q);
            Text(new Vector2(28,174),title,15);
            Text(new Vector2(28,195),progress.Length>38?progress[..35]+"…":progress,13);
            Text(new Vector2(28,216),"J · Nhật ký nhiệm vụ",12,_bronze);
        }
        else
        {
            Text(new Vector2(28,176),"F2: rộng/gọn · F6: giảm hiệu ứng",13);
            Text(new Vector2(28,198),LowFx?"VFX: thấp":"VFX: đầy đủ",13);
            Text(new Vector2(28,218),LastSkill,12,_bronze);
        }
        foreach(var b in new[]{(16,"Túi [I]"),(112,"Nói [E]"),(208,"Thử lại [R]")})
        {Panel(new Rect2(b.Item1,236,90,32));Text(new Vector2(b.Item1+7,257),b.Item2,12);}
        Panel(new Rect2(1108,16,156,110));
        Text(new Vector2(1120,38),Online?"BẾN MƯA":"BẾN MƯA · ART",12,_bronze);
        DrawRect(new Rect2(1120,49,132,61),Color.FromHtml("#243b2c"));
        if(_frame?.World is { } world)
        {
            Vector2 Point(double x,double y)=>new(1120+(float)x/360*132,75+(72-(float)y)/84*31);
            DrawRect(new Rect2(1120,75,132,31),Color.FromHtml("#547449"));
            foreach(var e in world.entities.Where(e=>e.kind=="NPC"))DrawCircle(Point(e.x,e.y),1.6f,_bronze);
            DrawCircle(Point(world.self.x,world.self.y),2.5f,_ink);
        }
        else
        {DrawRect(new Rect2(1120,49,132,38),Color.FromHtml("#4d7444"));DrawRect(new Rect2(1120,87,132,23),Color.FromHtml("#28675d"));DrawCircle(new Vector2(1188,77),3,_ink);}
        var center=AttackCenter;DrawCircle(center,48,_panel);DrawArc(center,48,0,Mathf.Tau,48,_bronze,2);
        Text(center+new Vector2(-25,5),"ĐÁNH",16,_bronze);
        var slotCenters=SkillCenters();
        for(int i=0;i<6;i++)
        {
            var p=slotCenters[i];var color=Online&&i>=3?Color.FromHtml("#59665b"):_bronze;
            DrawCircle(p,23,_panel);DrawArc(p,23,0,Mathf.Tau,32,color,_hover==i?3:2);
            var source=_skillIconRects[i];var size=source.Size*(32/Math.Max(source.Size.X,source.Size.Y));
            DrawTextureRectRegion(_skillTexture,new Rect2(p-size/2,size),source,
                Online&&i>=3?new Color(.4f,.4f,.4f,.8f):Colors.White);
            DrawRect(new Rect2(p+new Vector2(7,7),new Vector2(15,14)),_panel);
            Text(p+new Vector2(10,19),(i+1).ToString(),11,color);
        }
        if(_hover>=0)
        {
            var p=slotCenters[_hover];var at=new Vector2(Mathf.Clamp(p.X-110,16,1044),p.Y-75);
            Panel(new Rect2(at,new Vector2(220,45)));
            Text(at+new Vector2(9,18),SkillVfxPlayer.Names[_hover],13,_bronze);
            Text(at+new Vector2(9,35),Online&&_hover>=3?"Chưa hỗ trợ online":Online?"Máy chủ xác nhận hành động":"Thử hình ảnh ngoại tuyến",11);
        }
        Panel(new Rect2(16,650,810,56));
        Text(new Vector2(28,672),Online?"WASD di chuyển · E nói/nhặt · J nhật ký · I túi · Space đánh · 1–3 kỹ năng":"WASD di chuyển · 1–6 thử kỹ năng · Space đánh mẫu · H ẩn HUD",13);
        var status=StatusText.Length>106?StatusText[..103]+"...":StatusText;
        Text(new Vector2(28,695),status,13,_bronze);
        DrawLine(new Vector2(16,714),new Vector2(1264,714),_bronze,2);
    }
}
