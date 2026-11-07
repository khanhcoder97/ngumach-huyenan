using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Isolated visual fitting room. Review candidates never enter the gameplay renderer path.</summary>
public partial class PaperDollLab : Control
{
    private PaperDollLabData _data=null!;
    private ModularCharacterRenderer _avatar=null!,_base=null!;
    private PaperDollGuides _guides=null!;
    private Control _stage=null!;
    private OptionButton _gender=null!,_hair=null!,_eyes=null!,_outfit=null!,_weapon=null!,_hat=null!,_cape=null!,_target=null!,_zoom=null!;
    private Label _status=null!,_frame=null!,_source=null!;
    private SpinBox _x=null!,_y=null!;
    private HSlider _timeline=null!;
    private CheckButton _all=null!,_showGuides=null!;
    private Button _play=null!;
    private bool _sync,_paused=true,_captureMode;
    private long _revision;
    private double _refresh;
    private string? _benchmarkPath;
    private ulong _benchmarkStart,_lastTick;
    private readonly List<double> _samples=new();
    private string _body="MK_M";
    private readonly Dictionary<string,string[]> _options=new(StringComparer.Ordinal);
    private const string DraftPath="user://paperdoll_lab/fit_draft.json";
    public override void _Ready()
    {
        try {Build();}
        catch(Exception error){GD.PushError("PAPERDOLL_LAB_INIT_FAIL "+error);GetTree().Quit(1);}
    }
    private void Build()
    {
        Engine.MaxFps=60;Theme=MoonGlassTheme.Create();
        var bg=new ColorRect{Color=Color.FromHtml("#20243b"),MouseFilter=MouseFilterEnum.Ignore};bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);AddChild(bg);
        _data=new PaperDollLabData();
        var margin=new MarginContainer();margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach(var edge in new[]{"left","right","top","bottom"})margin.AddThemeConstantOverride("margin_"+edge,18);
        AddChild(margin);var root=new VBoxContainer();root.AddThemeConstantOverride("separation",12);margin.AddChild(root);
        root.AddChild(MoonGlassTheme.Label("NGŨ MẠCH HUYỀN ẤN  /  PHÒNG THỬ NHÂN VẬT",23,MoonGlassTheme.Ink));
        root.AddChild(MoonGlassTheme.Label("BASE + TRANG BỊ TÁCH LỚP   ·   Minh Kiếm nam/nữ   ·   Candidate SOUTH idle",13,MoonGlassTheme.Blue));
        var row=new HBoxContainer{SizeFlagsVertical=SizeFlags.ExpandFill};row.AddThemeConstantOverride("separation",16);root.AddChild(row);
        var leftCard=MoonGlassTheme.Card();leftCard.CustomMinimumSize=new Vector2(245,0);leftCard.SizeFlagsHorizontal=SizeFlags.Fill;row.AddChild(leftCard);
        var leftScroll=new ScrollContainer{SizeFlagsVertical=SizeFlags.ExpandFill,HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled};leftCard.AddChild(leftScroll);
        var left=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};left.AddThemeConstantOverride("separation",8);leftScroll.AddChild(left);
        left.AddChild(MoonGlassTheme.Label("01  DIỆN MẠO",17,MoonGlassTheme.Gold));
        _gender=Choice(left,"Base cơ thể",new[]{"Nam","Nữ"});_gender.ItemSelected+=i=>{_body=i==0?"MK_M":"MK_F";Rebuild();};
        _hair=PartChoice(left,"Tóc","HAIR");_eyes=PartChoice(left,"Mắt","EYES");
        _outfit=Choice(left,"Trang phục",new[]{"Coverage nền","Giao lĩnh ngà / ngọc","Giao lĩnh chàm / bạc"});_outfit.Select(1);_outfit.ItemSelected+=_=>Rebuild();
        _weapon=PartChoice(left,"Vũ khí","WEAPON");_hat=PartChoice(left,"Mũ / trán quan","HAT");_cape=PartChoice(left,"Áo choàng","CAPE");
        _hair.Select(1);_eyes.Select(1);_weapon.Select(1);
        left.AddChild(MoonGlassTheme.Label("Cùng đồng hồ và pose key. Đổi đồ giữ vị trí trên timeline.",12,MoonGlassTheme.Muted));
        var center=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};row.AddChild(center);
        var header=new HBoxContainer();center.AddChild(header);header.AddChild(MoonGlassTheme.Label("02  XEM & SO SÁNH",17,MoonGlassTheme.Gold));
        _zoom=new OptionButton();foreach(int z in new[]{2,4,6})_zoom.AddItem(z+"×");_zoom.Select(1);header.AddChild(_zoom);_zoom.ItemSelected+=_=>Place();
        _stage=new Control{SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(560,220),ClipContents=true};center.AddChild(_stage);
        var field=new ColorRect{Color=Color.FromHtml("#c2d5cf"),MouseFilter=MouseFilterEnum.Ignore};field.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);_stage.AddChild(field);
        _guides=new PaperDollGuides();
        _base=new ModularCharacterRenderer{PlaybackPaused=true};_stage.AddChild(_base);
        _avatar=new ModularCharacterRenderer{PlaybackPaused=true};_stage.AddChild(_avatar);_stage.AddChild(_guides);
        var names=new HBoxContainer();center.AddChild(names);
        var baseLabel=MoonGlassTheme.Label("BASE GỐC",12);baseLabel.HorizontalAlignment=HorizontalAlignment.Center;names.AddChild(baseLabel);
        var dressedLabel=MoonGlassTheme.Label("BẢN THỬ GHÉP LỚP",12);dressedLabel.HorizontalAlignment=HorizontalAlignment.Center;names.AddChild(dressedLabel);
        _showGuides=new CheckButton{Text="Hiện điểm neo và khung master",ButtonPressed=true};center.AddChild(_showGuides);
        _showGuides.Toggled+=v=>{_guides.Visible=v;UpdateGuides();};
        var dirs=new HBoxContainer();center.AddChild(dirs);
        foreach(string d in Directions){var b=MoonGlassTheme.Button(d,48);b.Disabled=d!="S";b.TooltipText=d=="S"?"Nguồn hiện có":"Chưa có master đã fit cho hướng "+d;dirs.AddChild(b);}
        var playback=new HBoxContainer();center.AddChild(playback);
        _play=MoonGlassTheme.Button("Phát",90);playback.AddChild(_play);_play.Pressed+=()=>Pause(!_paused);
        var prev=MoonGlassTheme.Button("←",48);playback.AddChild(prev);prev.Pressed+=()=>Seek((_avatar.Animation.FrameIndex+15)%16);
        var next=MoonGlassTheme.Button("→",48);playback.AddChild(next);next.Pressed+=()=>Seek((_avatar.Animation.FrameIndex+1)%16);
        _frame=MoonGlassTheme.Label("",12);playback.AddChild(_frame);
        _timeline=new HSlider{MinValue=0,MaxValue=15,Step=1,CustomMinimumSize=new Vector2(0,28)};center.AddChild(_timeline);
        _timeline.ValueChanged+=v=>{if(!_sync)Seek((int)v);};
        var rightCard=MoonGlassTheme.Card();rightCard.CustomMinimumSize=new Vector2(255,0);rightCard.SizeFlagsHorizontal=SizeFlags.Fill;row.AddChild(rightCard);
        var rightScroll=new ScrollContainer{SizeFlagsVertical=SizeFlags.ExpandFill,HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled};rightCard.AddChild(rightScroll);
        var right=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};right.AddThemeConstantOverride("separation",8);rightScroll.AddChild(right);
        right.AddChild(MoonGlassTheme.Label("03  FIT TỪNG POSE",17,MoonGlassTheme.Gold));
        _target=new OptionButton();right.AddChild(_target);_target.ItemSelected+=_=>SyncInspector();
        _source=MoonGlassTheme.Label("",12,MoonGlassTheme.Muted);right.AddChild(_source);
        _x=Coordinate(right,"X trên canvas / offset");_y=Coordinate(right,"Y trên canvas / offset");
        _x.ValueChanged+=_=>Edit();_y.ValueChanged+=_=>Edit();
        _all=new CheckButton{Text="Áp cùng giá trị cho 16 pose"};right.AddChild(_all);
        right.AddChild(MoonGlassTheme.Label("Tọa độ logical pixel. Tóc/mũ/vũ khí theo anchor; áo/quần ở đây chỉ là mẫu tĩnh thử fit.",12,MoonGlassTheme.Muted));
        var save=MoonGlassTheme.Button("Lưu bản fit nháp",0,true);right.AddChild(save);save.Pressed+=Save;
        var load=MoonGlassTheme.Button("Mở bản fit nháp");right.AddChild(load);load.Pressed+=Load;
        var reset=MoonGlassTheme.Button("Khôi phục guide gốc");right.AddChild(reset);reset.Pressed+=()=>{_data.Reset();Rebuild();_status.Text="Đã khôi phục dữ liệu thử ban đầu.";};
        right.AddChild(MoonGlassTheme.Label("Bản nháp chỉ lưu cục bộ trong user://paperdoll_lab. Không ghi đè nguồn hoặc cấp trang bị.",11,MoonGlassTheme.Muted));
        _status=MoonGlassTheme.Label("",13,MoonGlassTheme.Gold);root.AddChild(_status);
        root.AddChild(MoonGlassTheme.Label("FIT LAB ONLY · 0 clip native được duyệt · còn thiếu split tay, walk/combat và 7 hướng · không phải màn tạo tài khoản.",12,MoonGlassTheme.Muted));
        _stage.Resized+=Place;Rebuild();Place();
        var args=OS.GetCmdlineUserArgs();
        if(args.Contains("--paperdoll-female")){_gender.Select(1);_body="MK_F";Rebuild();}
        if(args.Contains("--paperdoll-indigo")){_outfit.Select(2);_hair.Select(2);_weapon.Select(2);_cape.Select(2);Rebuild();}
        int benchmark=Array.IndexOf(args,"--paperdoll-benchmark");if(benchmark>=0&&benchmark+1<args.Length){_benchmarkPath=args[benchmark+1];_benchmarkStart=_lastTick=Godot.Time.GetTicksUsec();Pause(false);}
        if(args.Contains("--paperdoll-self-test"))SelfTest();
        int capture=Array.IndexOf(args,"--paperdoll-capture");if(capture>=0&&capture+1<args.Length)Capture(args[capture+1]);
    }
    private OptionButton Choice(VBoxContainer parent,string label,string[] choices)
    {
        parent.AddChild(MoonGlassTheme.Label(label,12,MoonGlassTheme.Muted));var control=new OptionButton{CustomMinimumSize=new Vector2(0,31)};
        foreach(string name in choices)control.AddItem(name);parent.AddChild(control);return control;
    }
    private OptionButton PartChoice(VBoxContainer parent,string label,string category)
    {
        var parts=_data.Data.Parts.Where(p=>p.Category==category).ToArray();_options[category]=parts.Select(p=>p.Id).ToArray();
        var control=Choice(parent,label,new[]{"Không dùng"}.Concat(parts.Select(p=>p.Name)).ToArray());control.ItemSelected+=_=>Rebuild();return control;
    }
    private SpinBox Coordinate(VBoxContainer parent,string label)
    {parent.AddChild(MoonGlassTheme.Label(label,12,MoonGlassTheme.Muted));var control=new SpinBox{MinValue=-96,MaxValue=96,Step=1,AllowGreater=false,AllowLesser=false,CustomMinimumSize=new Vector2(0,32)};parent.AddChild(control);return control;}
    private List<string> Selected()
    {
        var result=new List<string>();
        foreach(var pair in new[]{("HAIR",_hair),("EYES",_eyes),("WEAPON",_weapon),("HAT",_hat),("CAPE",_cape)})
            if(pair.Item2.Selected>0)result.Add(_options[pair.Item1][pair.Item2.Selected-1]);
        if(_outfit.Selected==1)result.AddRange(new[]{"CHEST_IVORY","LEGS_IVORY","BOOTS_BROWN"});
        if(_outfit.Selected==2)result.AddRange(new[]{"CHEST_INDIGO","LEGS_INDIGO","BOOTS_SILVER"});
        return result;
    }
    private bool Rebuild()
    {
        if(_avatar==null)return false;
        var look=_data.Build(_body,Selected(),++_revision);
        if(!_avatar.TryApplyForReview(look,out string reason)){_status.Text="Giữ bản trước: "+reason;return false;}
        if(!_base.TryApplyForReview(_data.Build(_body,Array.Empty<string>(),_revision),out reason))throw new Exception(reason);
        _base.SeekReviewFrame(_avatar.Animation.FrameIndex);
        string old=_target.ItemCount>0?_target.GetItemMetadata(_target.Selected).AsString():"";
        _target.Clear();
        foreach(string anchor in new[]{"head","face","chest","hip","hand_near"})
        {int i=_target.ItemCount;_target.AddItem("Neo · "+anchor);_target.SetItemMetadata(i,"anchor:"+anchor);}
        foreach(string id in Selected()){int i=_target.ItemCount;_target.AddItem(_data.Data.Parts.Single(p=>p.Id==id).Name);_target.SetItemMetadata(i,"part:"+id);}
        int index=Enumerable.Range(0,_target.ItemCount).FirstOrDefault(i=>_target.GetItemMetadata(i).AsString()==old);_target.Select(index);
        _status.Text="Đang thử: "+_data.FindBody(_body).Name+" · "+Selected().Count+" phần · nguồn/fit chưa được duyệt";
        SyncInspector();UpdateGuides();return true;
    }
    private void Edit()
    {
        if(_sync||_target.ItemCount==0)return;
        string target=_target.GetItemMetadata(_target.Selected).AsString();int frame=_avatar.Animation.FrameIndex;var value=new Pixel((int)_x.Value,(int)_y.Value);
        // Keep the editor draft and live preview atomic when a proposed fit leaves the canvas.
        string previous=_data.ExportDraft();
        if(target.StartsWith("anchor:",StringComparison.Ordinal))_data.SetAnchor(_body,target[7..],frame,value,_all.ButtonPressed);
        else _data.SetOffset(_body,target[5..],frame,value,_all.ButtonPressed);
        if(!Rebuild()){if(!_data.TryImportDraft(previous,out var error))throw new Exception(error);SyncInspector();}
    }
    private void SyncInspector()
    {
        if(_x==null||_target.ItemCount==0)return;_sync=true;
        string target=_target.GetItemMetadata(_target.Selected).AsString();int frame=_avatar.Animation.FrameIndex;
        Pixel value=target.StartsWith("anchor:",StringComparison.Ordinal)?_data.Anchor(_body,target[7..],frame):_data.Offset(_body,target[5..],frame);
        _x.Value=value.X;_y.Value=value.Y;_sync=false;
        _source.Text=target.StartsWith("anchor:",StringComparison.Ordinal)?"Guide thử · source-bound · chưa phê duyệt":"1 ảnh tĩnh / 16 placement · chỉ hướng S";
    }
    private void Place()
    {
        if(_stage==null||_avatar==null)return;
        int zoom=new[]{2,4,6}[_zoom.Selected];_avatar.Scale=_base.Scale=new Vector2(zoom,zoom);
        float ground=_stage.Size.Y/2+82;_base.Position=new(_stage.Size.X*.25f,ground);_avatar.Position=new(_stage.Size.X*.75f,ground);
        UpdateGuides();
    }
    private void UpdateGuides()
    {
        if(_guides==null||_avatar.Animation.Current==null)return;
        _guides.Origin=_avatar.Position;_guides.BaseOrigin=_base.Position;_guides.Zoom=_avatar.Scale.X;
        _guides.Anchors=_data.FindBody(_body).Frames[_avatar.Animation.FrameIndex].Anchors.Keys.ToDictionary(n=>n,n=>_data.Anchor(_body,n,_avatar.Animation.FrameIndex));
        _guides.QueueRedraw();
    }
    private void Pause(bool value){_paused=value;_avatar.PlaybackPaused=value;_play.Text=value?"Phát":"Tạm dừng";}
    private void Seek(int frame){Pause(true);_avatar.SeekReviewFrame(frame);_base.SeekReviewFrame(frame);SyncInspector();UpdateGuides();}
    private void Save()
    {
        DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath("user://paperdoll_lab"));
        using var file=FileAccess.Open(DraftPath,FileAccess.ModeFlags.Write);
        if(file==null){_status.Text="Không lưu được bản nháp: "+FileAccess.GetOpenError();return;}
        file.StoreString(_data.ExportDraft());_status.Text="Đã lưu bản fit nháp · chưa phê duyệt asset.";
    }
    private void Load()
    {
        if(!FileAccess.FileExists(DraftPath)){_status.Text="Chưa có bản nháp trên máy này.";return;}
        if(!_data.TryImportDraft(FileAccess.GetFileAsString(DraftPath),out var reason)){_status.Text="Từ chối bản nháp: "+reason;return;}
        if(!Rebuild())throw new Exception("validated draft failed to render");
        _status.Text="Đã mở bản nháp khớp đúng nguồn/guide.";
    }
    public override void _Process(double delta)
    {
        if(_avatar==null||_avatar.Animation.Current==null)return;
        MeasurePreview();
        _base.SeekReviewFrame(_avatar.Animation.FrameIndex);
        _refresh+=delta;if(_refresh<.05)return;_refresh=0;
        _sync=true;_timeline.Value=_avatar.Animation.FrameIndex;_sync=false;
        _frame.Text=$"Pose {_avatar.Animation.FrameIndex+1:00}/16 · "+(_captureMode?"ảnh tĩnh · không đo FPS":$"{(int)Engine.GetFramesPerSecond()} FPS render");
        SyncInspector();UpdateGuides();
    }
    private void MeasurePreview()
    {
        if(_benchmarkPath==null)return;ulong now=Godot.Time.GetTicksUsec();double elapsed=(now-_benchmarkStart)/1_000_000d;
        if(elapsed>2)_samples.Add((now-_lastTick)/1000d);_lastTick=now;
        if(elapsed<14)return;var ordered=_samples.OrderBy(v=>v).ToArray();
        var report=new{scene="PaperDollLab",scope="TWO_PREVIEW_ACTORS_ONLY_NOT_WORLD_CROWD_OR_COMBAT",targetFps=60,sourceCells=16,staticWearableImages=16,display=DisplayServer.GetName(),gpu=RenderingServer.GetVideoAdapterName(),warmupSeconds=2,measurementSeconds=elapsed-2,samples=ordered.Length,medianMs=ordered[ordered.Length/2],p95Ms=ordered[Math.Min(ordered.Length-1,(int)(ordered.Length*.95))],meanFps=1000/_samples.Average(),productionApproved=false};
        using var file=FileAccess.Open(_benchmarkPath,FileAccess.ModeFlags.Write);if(file==null)throw new Exception("benchmark output unavailable");file.StoreString(JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true})+"\n");
        GD.Print("PAPERDOLL_LAB_BENCHMARK "+JsonSerializer.Serialize(report));_benchmarkPath=null;GetTree().Quit();
    }
    public override void _UnhandledKeyInput(InputEvent ev)
    {if(ev is not InputEventKey key||!key.Pressed||key.Echo)return;if(key.Keycode==Key.Space)Pause(!_paused);if(key.Keycode==Key.Escape)GetTree().Quit();}
    private async void Capture(string path)
    {
        _captureMode=true;_showGuides.ButtonPressed=false;Seek(0);for(int i=0;i<5;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);
        var result=GetViewport().GetTexture().GetImage().SavePng(path);
        GD.Print("PAPERDOLL_LAB_CAPTURE "+result+" CANDIDATE_NOT_GAMEPLAY");GetTree().Quit(result==Error.Ok?0:1);
    }
    private void SelfTest()
    {
        int checks=0;void Check(bool value,string reason){if(!value)throw new Exception(reason);checks++;}
        try
        {
            foreach(var body in _data.Data.Bodies)
            {
                foreach(var part in _data.Data.Parts)
                {
                    var look=_data.Build(body.Id,new[]{part.Id},++_revision);
                    Check(TryCompile(look,true,out var compiled,out _),"candidate binding compile");
                    Check(compiled!.Clips["idle/S"].Frames.Count==16,"sixteen placement bindings");
                    Check(!_avatar.TryApply(look,out _),"unapproved study cannot enter production renderer");
                    Check(_avatar.TryApplyForReview(look,out _),"actual texture/region loads");
                }
            }
            _body="MK_M";_gender.Select(0);Check(Rebuild(),"rebuild visible controls");
            Seek(7);double elapsed=_avatar.Animation.Elapsed;_outfit.Select(2);_outfit.EmitSignal(OptionButton.SignalName.ItemSelected,2L);
            Check(_avatar.Animation.Elapsed==elapsed&&_avatar.Animation.FrameIndex==7,"outfit control preserves clock");
            _hat.Select(2);_hat.EmitSignal(OptionButton.SignalName.ItemSelected,2L);
            Check(!_avatar.Animation.Commands.Any(c=>c.PartId=="hair_front"),"hat hides hair token");
            _hat.Select(0);_hat.EmitSignal(OptionButton.SignalName.ItemSelected,0L);
            Check(_avatar.Animation.Commands.Any(c=>c.PartId=="hair_front"),"remove hat restores original hair");
            string before=_data.ExportDraft();var offset=_data.Offset(_body,"HAIR_CHESTNUT",7);
            _data.SetOffset(_body,"HAIR_CHESTNUT",7,offset+new Pixel(1,0),false);Check(Rebuild(),"single-frame edit");
            Check(_data.Offset(_body,"HAIR_CHESTNUT",7).X==offset.X+1&&_data.Offset(_body,"HAIR_CHESTNUT",6).X==offset.X,"edit is frame-specific");
            string saved=_data.ExportDraft();Check(_data.TryImportDraft(saved,out _),"draft roundtrip");
            Check(!_data.TryImportDraft(saved.Replace(_data.Data.CatalogueFingerprint,"STALE",StringComparison.Ordinal),out _)&&_data.ExportDraft()==saved,"stale draft atomically rejected");
            Check(!_data.TryImportDraft("{}",out _)&&_data.ExportDraft()==saved,"malformed draft rejected");
            var badDraft=JsonSerializer.Deserialize<PaperDollLabData.Draft>(saved)!;badDraft.Offsets["MK_M/UNKNOWN_PART"]=Enumerable.Repeat(new Pixel(0,0),16).ToArray();
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(badDraft),out _)&&_data.ExportDraft()==saved,"unknown part draft rejected atomically");
            badDraft=JsonSerializer.Deserialize<PaperDollLabData.Draft>(saved)!;badDraft.Offsets["MK_M/HAIR_CHESTNUT"]=new Pixel[15];
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(badDraft),out _)&&_data.ExportDraft()==saved,"missing pose mapping rejected atomically");
            _data.SetOffset(_body,"HAIR_CHESTNUT",7,offset,true);Check(Enumerable.Range(0,16).All(i=>_data.Offset(_body,"HAIR_CHESTNUT",i)==offset),"all-pose editor updates sixteen records");
            var candidate=_data.Build(_body,new[]{"HAIR_CHESTNUT"},++_revision);var candidatePart=candidate.Parts[0];
            var missing=candidatePart.Bindings.ToDictionary(p=>p.Key,p=>p.Value with{Frames=p.Value.Frames.Select(f=>f with{Texture="res://assets/paperdoll_lab/MISSING.png"}).ToArray()});
            var previousLook=_avatar.Animation.Current;
            Check(!_avatar.TryApplyForReview(candidate with{Parts=new[]{candidatePart with{Bindings=missing}}},out _)&&ReferenceEquals(previousLook,_avatar.Animation.Current),"missing real texture preserves committed presentation");
            Check(_data.TryImportDraft(before,out _),"restore draft");Check(Rebuild(),"restore preview");
            var session=_avatar.Animation;session.SeekFrame(0);var frames=new HashSet<int>();for(int i=0;i<72;i++){session.Advance(1d/60);frames.Add(session.FrameIndex);}
            Check(frames.Count==16,"one clock samples sixteen body cells");
            Check(!session.SeekFrame(16)&&!session.SeekFrame(-1),"invalid scrub rejected");
            _body="MK_F";_gender.Select(1);Check(Rebuild(),"female visible profile");
            GD.Print($"PAPERDOLL_LAB_SELF_TEST PASS assertions={checks} ACTUAL_TEXTURES_AND_UI_SIGNALS_NOT_ART_APPROVAL");
            GetTree().Quit();
        }
        catch(Exception error){GD.PushError("PAPERDOLL_LAB_SELF_TEST FAIL "+error);GetTree().Quit(1);}
    }
}
public partial class PaperDollGuides : Node2D
{
    public Vector2 Origin,BaseOrigin;
    public float Zoom=4;
    public Dictionary<string,Pixel> Anchors=new();
    public override void _Draw()
    {
        var line=new Color(.18f,.31f,.38f,.25f);
        foreach(var origin in new[]{BaseOrigin,Origin})
        {
            var top=origin-new Vector2(48,72)*Zoom;
            DrawRect(new Rect2(top,new Vector2(96,96)*Zoom),line,false);
            DrawLine(origin+new Vector2(-32,0)*Zoom,origin+new Vector2(32,0)*Zoom,line,1);
        }
        foreach(var (name,pixel) in Anchors)
        {
            var p=Origin+new Vector2(pixel.X-48,pixel.Y-72)*Zoom;var color=name=="ground"?Color.FromHtml("#b76560"):Color.FromHtml("#438cbd");
            DrawLine(p-new Vector2(4,0),p+new Vector2(4,0),color);DrawLine(p-new Vector2(0,4),p+new Vector2(0,4),color);
        }
    }
}
