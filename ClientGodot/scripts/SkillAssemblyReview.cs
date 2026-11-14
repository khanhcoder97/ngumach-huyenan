using Godot;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace Ngumach.VisualReboot;

/// <summary>Editable, independent source clocks. Every event here is an authoring example.</summary>
public partial class SkillAssemblyReview : Control
{
    private ActorLibraryData _library = null!;
    private SkillAssemblySourceBounds _bounds = null!;
    private SkillAssemblyDocument _document = null!;
    private readonly List<SkillAssemblyPane> _panes = new();
    private readonly List<(SpinBox Box, Func<SkillAssemblyTrack,double> Read)> _numbers = new();
    private OptionButton _profiles = null!, _variants = null!, _tracks = null!, _anchors = null!, _rotations = null!;
    private CheckBox _loopTrack = null!;
    private Label _readout = null!, _notice = null!, _source = null!;
    private HSlider _seek = null!;
    private int _profileIndex, _variantIndex, _trackIndex, _resources = 5;
    private double _clock, _speed = 1;
    private float _zoom = 1;
    private bool _paused, _lowFx, _sync, _layoutDirty = true;
    private Vector2 _lastSize;
    private int _warmup = 2;
    private SkillAssemblyProfile Profile => _document.Profiles[_profileIndex];
    private SkillAssemblyVariant Variant => Profile.Variants[_variantIndex];
    private SkillAssemblyTrack? Track => Variant.Tracks.Count == 0 ? null : Variant.Tracks[Math.Clamp(_trackIndex,0,Variant.Tracks.Count-1)];

    public override void _Ready()
    {
        try
        {
            Engine.MaxFps = 60; ProcessPriority = -2; Theme = MoonGlassTheme.Create();
            _library = new ActorLibraryData(reviewMode:true); _bounds = new SkillAssemblySourceBounds(_library);
            var args = OS.GetCmdlineUserArgs(); string Arg(string key, string fallback) { int at=Array.IndexOf(args,key); return at>=0&&at+1<args.Length?args[at+1]:fallback; }
            _document = SkillAssemblyCodec.Decode(FileAccess.GetFileAsString(Arg("--assembly-project",SkillAssemblyCodec.Source)),_library);
            SkillAssemblyCodec.VerifyComponentFiles(_document,_library);
            string profileId=Arg("--assembly-profile",_document.Profiles[0].Id); _profileIndex=_document.Profiles.FindIndex(p=>p.Id==profileId);
            if(_profileIndex<0)throw new InvalidOperationException("Profile không tồn tại: "+profileId);
            string variantId=Arg("--assembly-variant",Profile.Variants[0].Id);_variantIndex=Profile.Variants.FindIndex(v=>v.Id==variantId);
            if(_variantIndex<0)throw new InvalidOperationException("Variant không tồn tại: "+variantId);
            _lowFx=args.Contains("--assembly-low-fx");_resources=int.Parse(Arg("--assembly-resource","5"),CultureInfo.InvariantCulture);
            if(_resources is <0 or >5)throw new InvalidOperationException("Resource xem cần0–5.");
            BuildUi(); _profiles.Select(_profileIndex); PopulateVariants(_variantIndex); Rebind();
            if(args.Contains("--assembly-time")){_clock=double.Parse(Arg("--assembly-time","0"),CultureInfo.InvariantCulture);_paused=true;}
            if(args.Contains("--assembly-self-test"))RunTests();
        }
        catch(Exception e){GD.PushError("SKILL_ASSEMBLY_LOAD_FAIL "+e);GetTree().Quit(1);}
    }
    private Button Button(Node parent,string label,Action action)
    {var b=new Button{Text=label};parent.AddChild(b);b.Pressed+=action;return b;}
    private void BuildUi()
    {
        var bg=new ColorRect{Color=Color.FromHtml("#1d2639"),MouseFilter=MouseFilterEnum.Ignore};bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);AddChild(bg);
        var margin=new MarginContainer();margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);foreach(string edge in new[]{"left","right","top","bottom"})margin.AddThemeConstantOverride("margin_"+edge,14);AddChild(margin);
        var stack=new VBoxContainer();margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label("GHÉP KỸ NĂNG / THÂN – VFX – TRẠNG THÁI",21,MoonGlassTheme.Gold));
        var controls=new HBoxContainer();stack.AddChild(controls);
        _profiles=new OptionButton();foreach(var p in _document.Profiles)_profiles.AddItem(p.Name+" · "+p.Id);controls.AddChild(_profiles);
        _variants=new OptionButton();controls.AddChild(_variants);
        _profiles.ItemSelected+=index=>{_profileIndex=(int)index;_variantIndex=0;PopulateVariants(0);Rebind();};
        _variants.ItemSelected+=index=>{_variantIndex=(int)index;Rebind();};
        Button(controls,"Dừng / Phát",()=>_paused=!_paused);Button(controls,"Phát lại",()=>{_clock=0;_paused=false;Apply();});
        var speed=new SpinBox{MinValue=.1,MaxValue=2,Step=.1,Value=1,Prefix="× ",CustomMinimumSize=new Vector2(95,0)};controls.AddChild(speed);speed.ValueChanged+=n=>_speed=n;
        var low=new CheckBox{Text="LowFX",ButtonPressed=_lowFx};controls.AddChild(low);low.Toggled+=n=>{_lowFx=n;Rebind();};
        var resources=new SpinBox{MinValue=0,MaxValue=5,Step=1,Value=_resources,Prefix="Tầng mẫu ",CustomMinimumSize=new Vector2(132,0)};controls.AddChild(resources);resources.ValueChanged+=n=>{_resources=(int)n;Rebind();};
        var row=new HBoxContainer{SizeFlagsVertical=SizeFlags.ExpandFill};stack.AddChild(row);
        var grid=new GridContainer{Columns=4,SizeFlagsHorizontal=SizeFlags.ExpandFill,SizeFlagsVertical=SizeFlags.ExpandFill};row.AddChild(grid);grid.AddThemeConstantOverride("h_separation",8);grid.AddThemeConstantOverride("v_separation",8);
        for(int facing=0;facing<8;facing++)
        {
            var card=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill,SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(180,180)};grid.AddChild(card);
            var pane=new SkillAssemblyPane{SizeFlagsHorizontal=SizeFlags.ExpandFill,SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(180,150)};card.AddChild(pane);_panes.Add(pane);pane.Resized+=()=>_layoutDirty=true;
            card.AddChild(MoonGlassTheme.Label(ArtStudioCodec.Directions[facing]+(facing>=5?" · thân lật, VFX xoay theo hướng":" · thân nguồn"),11,MoonGlassTheme.Muted));
        }
        var inspectorScroll=new ScrollContainer{CustomMinimumSize=new Vector2(245,0),SizeFlagsVertical=SizeFlags.ExpandFill};row.AddChild(inspectorScroll);
        var inspector=new VBoxContainer{CustomMinimumSize=new Vector2(228,0)};inspectorScroll.AddChild(inspector);
        inspector.AddChild(MoonGlassTheme.Label("CHỈNH LỚP VFX",16,MoonGlassTheme.Gold));_tracks=new OptionButton{SizeFlagsHorizontal=SizeFlags.ExpandFill,FitToLongestItem=false,ClipText=true,CustomMinimumSize=new Vector2(220,0)};inspector.AddChild(_tracks);_tracks.ItemSelected+=i=>{_trackIndex=(int)i;SyncInspector();};
        _source=MoonGlassTheme.Label("",11,MoonGlassTheme.Muted);_source.AutowrapMode=TextServer.AutowrapMode.WordSmart;inspector.AddChild(_source);
        Number(inspector,"Bắt đầu (s)",0,15,.01,t=>t.Start,(t,n)=>t.Start=n);
        Number(inspector,"Hiện trong (s)",.01,15,.01,t=>t.Duration,(t,n)=>t.Duration=n);
        Number(inspector,"Tiến / lùi",-300,300,1,t=>t.Forward,(t,n)=>t.Forward=(float)n);
        Number(inspector,"Lệch bên",-300,300,1,t=>t.Side,(t,n)=>t.Side=(float)n);
        Number(inspector,"X màn hình",-300,300,1,t=>t.ScreenX,(t,n)=>t.ScreenX=(float)n);
        Number(inspector,"Y màn hình",-300,300,1,t=>t.Elevation,(t,n)=>t.Elevation=(float)n);
        Number(inspector,"Kích thước",4,300,1,t=>t.Size,(t,n)=>t.Size=(float)n);
        Number(inspector,"Góc (độ)",-360,360,1,t=>t.Angle,(t,n)=>t.Angle=(float)n);
        Number(inspector,"Lớp Z",-10,10,1,t=>t.Z,(t,n)=>t.Z=(int)n);
        Number(inspector,"Bán kính cánh",0,120,1,t=>t.ResourceRadius,(t,n)=>t.ResourceRadius=(float)n);
        _anchors=new OptionButton();foreach(string a in new[]{"CASTER","TARGET","TARGET_HP","END"})_anchors.AddItem(a);inspector.AddChild(_anchors);_anchors.ItemSelected+=i=>{if(!_sync&&Track!=null){Track.Anchor=_anchors.GetItemText((int)i);Rebind(false);}};
        _rotations=new OptionButton();_rotations.AddItem("FACING");_rotations.AddItem("SCREEN");inspector.AddChild(_rotations);_rotations.ItemSelected+=i=>{if(!_sync&&Track!=null){Track.Rotation=_rotations.GetItemText((int)i);Rebind(false);}};
        _loopTrack=new CheckBox{Text="Lặp theo đồng hồ nguồn"};inspector.AddChild(_loopTrack);_loopTrack.Toggled+=n=>{if(!_sync&&Track!=null){Track.Loop=n;Rebind(false);}};
        var guides=new CheckBox{Text="Mốc xem / thanh HP mẫu",ButtonPressed=true};inspector.AddChild(guides);guides.Toggled+=n=>{foreach(var pane in _panes)pane.Guides=n;Apply();};
        var zoom=new SpinBox{MinValue=.5,MaxValue=2,Step=.1,Value=1,Prefix="Zoom × "};inspector.AddChild(zoom);zoom.ValueChanged+=n=>{_zoom=(float)n;_layoutDirty=true;};
        Button(inspector,"Xuất bản chỉnh JSON",Export);Button(inspector,"Mở bản chỉnh JSON",Open);
        _seek=new HSlider{MinValue=0,Step=1d/60,MaxValue=6,SizeFlagsHorizontal=SizeFlags.ExpandFill};stack.AddChild(_seek);_seek.ValueChanged+=n=>{if(!_sync){_clock=n;_paused=true;Apply();}};
        _readout=MoonGlassTheme.Label("",12,MoonGlassTheme.Blue);stack.AddChild(_readout);
        _notice=MoonGlassTheme.Label("",12,MoonGlassTheme.Gold);_notice.AutowrapMode=TextServer.AutowrapMode.WordSmart;stack.AddChild(_notice);
        stack.AddChild(MoonGlassTheme.Label("Ví dụ authoring · mốc vàng = root ảnh, vòng xanh/HP là mốc mục tiêu · không gửi lệnh server · ESC: đóng",11,MoonGlassTheme.Muted));
    }
    private void Number(Node parent,string label,double min,double max,double step,Func<SkillAssemblyTrack,double> read,Action<SkillAssemblyTrack,double> write)
    {
        var row=new HBoxContainer();parent.AddChild(row);row.AddChild(MoonGlassTheme.Label(label,12));var box=new SpinBox{MinValue=min,MaxValue=max,Step=step,SizeFlagsHorizontal=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(105,0)};row.AddChild(box);_numbers.Add((box,read));
        box.ValueChanged+=n=>{if(_sync||Track==null)return;double old=read(Track);write(Track,n);try{SkillAssemblyCodec.Validate(_document,_library);_notice.Text="Bản chỉnh chưa duyệt; PNG nguồn giữ nguyên.";Rebind(false);}catch(Exception e){write(Track,old);_notice.Text=e.Message;SyncInspector();}};
    }
    private void PopulateVariants(int selected)
    {_variants.Clear();foreach(var v in Profile.Variants)_variants.AddItem(v.Name);_variants.Select(selected);}
    private void Rebind(bool resetClock=true)
    {
        if(resetClock){_clock=0;_trackIndex=0;}
        for(int i=0;i<8;i++)_panes[i].Bind(_library,_bounds,Profile,Variant,i,_resources,_lowFx);
        _sync=true;_tracks.Clear();foreach(var t in Variant.Tracks)_tracks.AddItem(t.Id+" · "+t.ComponentId);if(Variant.Tracks.Count>0)_tracks.Select(Math.Clamp(_trackIndex,0,Variant.Tracks.Count-1));_seek.MaxValue=Variant.Duration;_sync=false;
        SyncInspector();_notice.Text=Variant.Note+" Kích thước/đường lướt là pixel xem art, không phải collider hoặc mét.";_layoutDirty=true;Apply();
    }
    private void SyncInspector()
    {
        _sync=true;var t=Track;
        foreach(var n in _numbers){n.Box.Editable=t!=null;if(t!=null)n.Box.Value=n.Read(t);}
        if(t!=null){_source.Text=t.ComponentId+"\n16 pose · đồng hồ nguồn "+t.SourceSeconds.ToString("0.00",CultureInfo.InvariantCulture)+" s · "+_library.Pages[t.ComponentId].VisualState;_anchors.Select(Array.IndexOf(new[]{"CASTER","TARGET","TARGET_HP","END"},t.Anchor));_rotations.Select(t.Rotation=="FACING"?0:1);_loopTrack.ButtonPressed=t.Loop;}
        else _source.Text="Không có lớp trong tình huống này.";
        _sync=false;
    }
    private void Apply()
    {
        if(_document==null||_panes.Count==0)return;
        if(_layoutDirty||_lastSize!=Size){_lastSize=Size;float fit=_panes.Min(p=>p.SuggestedScale)*_zoom;foreach(var p in _panes)p.Fit(fit);_layoutDirty=false;}
        foreach(var p in _panes)p.RenderAt(_clock);
        _sync=true;_seek.Value=_clock;_sync=false;
        var body=SkillAssemblySampler.Body(Profile,Variant,_clock);int approved=Variant.Tracks.Count(t=>_library.Pages[t.ComponentId].Approved);
        _readout.Text=$"{Profile.Name} / {Variant.Id} · {_clock:0.00}/{Variant.Duration:0.00}s · {body.Clip} · VFX nguồn duyệt {approved}/{Variant.Tracks.Count} · nguồn16 pose, render mục tiêu60FPS; video offline không đo FPS.";
    }
    public override void _Process(double delta)
    {
        if(_document==null||_panes.Count==0)return;
        if(_warmup>0){_warmup--;Apply();return;}
        if(!_paused){_clock+=delta*_speed;if(_clock>=Variant.Duration+.6)_clock%=Variant.Duration+.6;}
        Apply();
    }
    private void Export()
    {
        try{SkillAssemblyCodec.Validate(_document,_library);string folder="user://skill_assembly";DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath(folder));string path=folder+"/AssemblyEdit_"+DateTime.Now.ToString("yyyyMMdd_HHmmss_fff",CultureInfo.InvariantCulture)+".json";using(var file=FileAccess.Open(path,FileAccess.ModeFlags.Write)){if(file==null)throw new InvalidOperationException("Không ghi được JSON.");file.StoreString(SkillAssemblyCodec.Encode(_document));}_notice.Text="Đã lưu bản chỉnh chưa duyệt: "+ProjectSettings.GlobalizePath(path);}
        catch(Exception e){_notice.Text=e.Message;}
    }
    private void Open()
    {
        var dialog=new FileDialog{Access=FileDialog.AccessEnum.Filesystem,FileMode=FileDialog.FileModeEnum.OpenFile,Filters=new[]{"*.json ; Skill assembly"},Title="Mở bản chỉnh skill assembly"};AddChild(dialog);
        dialog.FileSelected+=path=>{try{var edited=SkillAssemblyCodec.Decode(FileAccess.GetFileAsString(path),_library);SkillAssemblyCodec.VerifyComponentFiles(edited,_library);_document=edited;_profileIndex=0;_variantIndex=0;_profiles.Clear();foreach(var p in edited.Profiles)_profiles.AddItem(p.Name+" · "+p.Id);_profiles.Select(0);PopulateVariants(0);Rebind();}catch(Exception e){_notice.Text=e.Message;}dialog.QueueFree();};dialog.Canceled+=()=>dialog.QueueFree();dialog.PopupCenteredRatio(.7f);
    }
    public override void _UnhandledKeyInput(InputEvent @event){if(@event is InputEventKey{Pressed:true,Keycode:Key.Escape})GetTree().Quit();}
    public override void _ExitTree()=>_library?.Dispose();
}
