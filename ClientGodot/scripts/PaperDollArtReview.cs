using Godot;
using System;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Tasks;

namespace Ngumach.VisualReboot;

/// <summary>Artwork review only. No procedural character drawing, equipment mutation or animation claims.</summary>
public partial class PaperDollArtReview : Control
{
    private sealed record Entry(string Id,string Name,string File,string Sha256,int[] Size,int PosesPerActor,int Actors,string Direction,bool LayerPackReady,bool AnimationReady,bool ProductionApproved);
    private sealed record Catalogue(int SchemaVersion,string Scope,string PreferredStyle,string RejectedStyle,Entry[] Entries,bool ProductionApproved);
    private Catalogue _catalogue=null!;
    private TextureRect _image=null!,_baseOverlay=null!;
    private Label _caption=null!,_detail=null!;
    private CheckButton _compare=null!,_crisp=null!;
    private Button[] _buttons=Array.Empty<Button>();
    private int _selected=2;
    public override void _Ready()
    {
        if(!OS.GetCmdlineUserArgs().Contains("--paperdoll-art-self-test")&&!OS.GetCmdlineUserArgs().Contains("--paperdoll-archived-review"))
        {Callable.From(()=>GetTree().ChangeSceneToFile("res://ArtStudio.tscn")).CallDeferred();return;}
        try{Build();}
        catch(Exception e){GD.PushError("PAPERDOLL_ART_REVIEW_FAIL "+e);GetTree().Quit(1);}
    }
    private void Build()
    {
        Engine.MaxFps=60;Theme=MoonGlassTheme.Create();
        _catalogue=JsonSerializer.Deserialize<Catalogue>(FileAccess.GetFileAsString("res://assets/paperdoll_style_v3/catalog.json"),new JsonSerializerOptions{PropertyNameCaseInsensitive=true})??throw new Exception("missing style artwork");
        if(_catalogue.SchemaVersion!=1||_catalogue.Entries.Length!=3||_catalogue.ProductionApproved||_catalogue.Scope!="STYLE_AND_PROPORTION_REVIEW_ONLY")throw new Exception("invalid review catalogue");
        foreach(var e in _catalogue.Entries)
        {
            if(!e.File.StartsWith("res://assets/paperdoll_style_v3/",StringComparison.Ordinal)||e.File.Contains("..",StringComparison.Ordinal)||e.AnimationReady||e.LayerPackReady||e.ProductionApproved||e.PosesPerActor!=1)throw new Exception("invalid artwork scope");
            string hash=Convert.ToHexString(SHA256.HashData(FileAccess.GetFileAsBytes(e.File))).ToLowerInvariant();
            if(hash!=e.Sha256)throw new Exception("artwork source changed: "+e.Id);
        }
        var background=new ColorRect{Color=Color.FromHtml("#20243b"),MouseFilter=MouseFilterEnum.Ignore};background.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);AddChild(background);
        var margin=new MarginContainer();margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach(string edge in new[]{"top","bottom","left","right"})margin.AddThemeConstantOverride("margin_"+edge,16);
        AddChild(margin);var root=new VBoxContainer();root.AddThemeConstantOverride("separation",10);margin.AddChild(root);
        root.AddChild(MoonGlassTheme.Label("NGŨ MẠCH HUYỀN ẤN  /  NHÂN VẬT — BẢN VẼ MỚI",22));
        root.AddChild(MoonGlassTheme.Label("GIỮ PHONG CÁCH PIXEL CHI TIẾT · TỈ LỆ CƠ THỂ DÀI HƠN · TRANG PHỤC VẼ THEO BASE",12,MoonGlassTheme.Blue));
        var split=new HBoxContainer{SizeFlagsVertical=SizeFlags.ExpandFill};split.AddThemeConstantOverride("separation",16);root.AddChild(split);
        var card=MoonGlassTheme.Card();card.SizeFlagsHorizontal=SizeFlags.Fill;card.CustomMinimumSize=new(265,0);split.AddChild(card);
        var left=new VBoxContainer();left.AddThemeConstantOverride("separation",10);card.AddChild(left);
        left.AddChild(MoonGlassTheme.Label("MẪU MASTER NAM / NỮ",16,MoonGlassTheme.Gold));
        _buttons=new Button[3];
        for(int i=0;i<3;i++){int index=i;_buttons[i]=MoonGlassTheme.Button(new[]{"01  Base cơ thể","02  Bộ áo + quần","03  Mẫu diện mạo"}[i]);left.AddChild(_buttons[i]);_buttons[i].Pressed+=()=>Select(index);}
        left.AddChild(MoonGlassTheme.Label("Nét vẽ bo tròn, đổ bóng chi tiết và các cụm pixel nhỏ theo phong cách trước.",13));
        left.AddChild(MoonGlassTheme.Label("Cổ, thân, tay và chân dài hơn. Bộ đồ được vẽ trực tiếp từ ảnh base mới.",13));
        _compare=new CheckButton{Text="Chồng base để đối chiếu"};left.AddChild(_compare);_compare.Toggled+=_=>UpdateOverlay();
        _crisp=new CheckButton{Text="Giữ nét pixel",ButtonPressed=true};left.AddChild(_crisp);_crisp.Toggled+=v=>{_image.TextureFilter=_baseOverlay.TextureFilter=v?TextureFilterEnum.Nearest:TextureFilterEnum.Linear;};
        var bg= new OptionButton();foreach(string name in new[]{"Nền sáng","Nền chàm"})bg.AddItem(name);left.AddChild(bg);
        var open=MoonGlassTheme.Button("Mở ảnh nguồn");left.AddChild(open);open.Pressed+=()=>OS.ShellOpen(ProjectSettings.GlobalizePath(_catalogue.Entries[_selected].File));
        _detail=MoonGlassTheme.Label("",11,MoonGlassTheme.Muted);left.AddChild(_detail);
        var right=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};split.AddChild(right);
        var stage=new Control{SizeFlagsHorizontal=SizeFlags.ExpandFill,SizeFlagsVertical=SizeFlags.ExpandFill,ClipContents=true,CustomMinimumSize=new(650,480)};right.AddChild(stage);
        var paper=new ColorRect{Color=Color.FromHtml("#e9edf0"),MouseFilter=MouseFilterEnum.Ignore};paper.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);stage.AddChild(paper);
        _baseOverlay=Picture();stage.AddChild(_baseOverlay);_image=Picture();stage.AddChild(_image);
        _baseOverlay.Texture=GD.Load<Texture2D>(_catalogue.Entries[0].File);
        bg.ItemSelected+=i=>paper.Color=Color.FromHtml(i==0?"#e9edf0":"#30364b");
        _caption=MoonGlassTheme.Label("",12,MoonGlassTheme.Gold);right.AddChild(_caption);
        root.AddChild(MoonGlassTheme.Label("Bản vẽ master hướng S, một pose · chưa phải bộ animation hoặc layer trang bị đã nghiệm thu · trang bị/chỉ số game giữ nguyên",11,MoonGlassTheme.Muted));
        Select(2);
        var args=OS.GetCmdlineUserArgs();
        if(args.Contains("--paperdoll-art-self-test"))SelfTest();
        int view=Array.IndexOf(args,"--paperdoll-art-view");if(view>=0&&view+1<args.Length&&int.TryParse(args[view+1],out int viewIndex))Select(Math.Clamp(viewIndex,0,2));
        int capture=Array.IndexOf(args,"--paperdoll-capture");if(capture>=0&&capture+1<args.Length)Capture(args[capture+1]);
    }
    private TextureRect Picture()
    {
        var image=new TextureRect{ExpandMode=TextureRect.ExpandModeEnum.IgnoreSize,StretchMode=TextureRect.StretchModeEnum.KeepAspectCentered,TextureFilter=TextureFilterEnum.Nearest,MouseFilter=MouseFilterEnum.Ignore};
        image.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);return image;
    }
    private void Select(int index)
    {
        _selected=index;var e=_catalogue.Entries[index];_image.Texture=GD.Load<Texture2D>(e.File);
        if(_image.Texture==null||_image.Texture.GetWidth()!=e.Size[0]||_image.Texture.GetHeight()!=e.Size[1])throw new Exception("invalid artwork texture");
        _caption.Text=e.Name+" · ảnh master phóng lớn để xem nét và tỉ lệ";
        _detail.Text="Nguồn: "+e.Size[0]+" × "+e.Size[1]+"\nHướng S · 1 pose mỗi nhân vật\nChồng ảnh chỉ để đối chiếu bằng mắt, chưa chứng nhận khớp layer theo pixel.";
        for(int i=0;i<_buttons.Length;i++)_buttons[i].Modulate=i==index?MoonGlassTheme.Gold:Colors.White;
        UpdateOverlay();
    }
    private void UpdateOverlay()
    {_baseOverlay.Visible=_compare.ButtonPressed&&_selected!=0;_baseOverlay.Modulate=new Color(1,1,1,.6f);_image.Modulate=new Color(1,1,1,_baseOverlay.Visible ? .7f : 1f);}
    public override void _UnhandledKeyInput(InputEvent e)
    {if(e is InputEventKey k&&k.Pressed&&!k.Echo&&k.Keycode==Key.Escape)GetTree().Quit();}
    private async void Capture(string path)
    {for(int i=0;i<5;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);var result=GetViewport().GetTexture().GetImage().SavePng(path);GD.Print("PAPERDOLL_ART_CAPTURE "+result+" SINGLE_POSE_NOT_GAMEPLAY");GetTree().Quit(result==Error.Ok?0:1);}
    private void SelfTest()
    {
        int assertions=0;
        for(int i=0;i<3;i++)
        {_buttons[i].EmitSignal(Button.SignalName.Pressed);if(_selected!=i||_image.Texture==null)throw new Exception("artwork selection signal failed");assertions++;}
        _compare.ButtonPressed=true;if(!_baseOverlay.Visible)throw new Exception("base comparison missing");assertions++;
        _buttons[0].EmitSignal(Button.SignalName.Pressed);if(_baseOverlay.Visible)throw new Exception("base should not duplicate itself");assertions++;
        if(_catalogue.Entries.Any(e=>e.AnimationReady||e.LayerPackReady||e.ProductionApproved))throw new Exception("single pose promoted");
        assertions++;GD.Print("PAPERDOLL_ART_REVIEW_SELF_TEST PASS assertions="+assertions+" STYLE_REVIEW_NOT_LAYER_OR_ANIMATION_ACCEPTANCE");GetTree().Quit();
    }
}
