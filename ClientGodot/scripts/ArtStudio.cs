using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using GFile = Godot.FileAccess;

namespace Ngumach.VisualReboot;

/// <summary>Local, reversible sprite/animation/VFX authoring workbench. No gameplay authority.</summary>
public partial class ArtStudio : Control
{
    private ArtStudioDocument _doc = null!;
    private ArtStudioCanvas _stage = null!;
    private string _root = "", _path = "user://art_studio/projects/current.json", _selected = "sprite", _saved = "", _dragBefore = "";
    private int _clip, _frame;
    private bool _sync, _playing, _dirty, _dragChanged;
    private double _time;
    private readonly Stack<string> _undo = new(), _redo = new();
    private readonly Dictionary<string, SpinBox> _numbers = new();
    private ItemList _layers = null!;
    private OptionButton _library = null!, _clips = null!, _attach = null!, _socket = null!, _marker = null!, _direction = null!, _markerKind = null!;
    private LineEdit _layerName = null!, _clipName = null!, _socketName = null!, _markerName = null!, _source = null!;
    private Label _status = null!, _frameLabel = null!, _scope = null!, _fileLabel = null!;
    private RichTextLabel _report = null!, _events = null!;
    private CheckButton _visible = null!, _locked = null!, _keyMode = null!, _loop = null!, _interpolate = null!;
    private HSlider _timeline = null!;
    private ArtStudioTimeline _film = null!;
    private Button _play = null!, _undoButton = null!, _redoButton = null!;
    private (string Id, string Name)[] _entries = Array.Empty<(string, string)>();
    private string[] _socketIds = Array.Empty<string>();
    private FileDialog _dialog = null!;
    private Action<string>? _fileAction;
    private Action? _pending;
    private ConfirmationDialog _discard = null!;
    private ArtStudioPose? _clipboard;
    private ArtStudioLayer Layer => _doc.Layers.First(l => l.Id == _selected);
    private ArtStudioClip Clip => _doc.Clips[_clip];
    public override void _Ready()
    {
        try { Build(); }
        catch (Exception e) { GD.PushError("ART_STUDIO_FAIL " + e); GetTree().Quit(1); }
    }
    private void Build()
    {
        Engine.MaxFps = 60; Theme = MoonGlassTheme.Create();
        GetWindow().Title = "Ngũ Mạch Huyền Ấn — Sprite & VFX Studio";
        GetTree().AutoAcceptQuit = false;
        GetWindow().CloseRequested += () => ConfirmDiscard(() => GetTree().Quit());
        GetWindow().MinSize = new Vector2I(1100, 680);
        var bg = new ColorRect { Color = Color.FromHtml("#20243b"), MouseFilter = MouseFilterEnum.Ignore }; bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(bg);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string edge in new[] { "top", "bottom", "left", "right" }) margin.AddThemeConstantOverride("margin_" + edge, 12);
        AddChild(margin); var root = new VBoxContainer(); root.AddThemeConstantOverride("separation", 7); margin.AddChild(root);
        var header = Row(root); header.AddChild(MoonGlassTheme.Label("NGŨ MẠCH / SPRITE & VFX STUDIO", 20));
        Button(header, "Mở JSON", () => Choose(FileDialog.FileModeEnum.OpenFile, "*.json ; Studio project", p => ConfirmDiscard(() => LoadProject(p))));
        Button(header, "Lưu Ctrl+S", Save);
        Button(header, "Lưu thành…", () => Choose(FileDialog.FileModeEnum.SaveFile, "*.json ; Studio project", p => SaveAs(p)));
        Button(header, "Xuất bundle", () => Choose(FileDialog.FileModeEnum.SaveFile, "*.json ; Portable bundle", p => { ArtStudioCodec.ExportBundle(p, _doc, _root); Status("Đã xuất JSON + PNG gốc vào textures/. Chưa thay gameplay."); }));
        _fileLabel = MoonGlassTheme.Label("", 11, MoonGlassTheme.Muted); root.AddChild(_fileLabel);
        var split = new HSplitContainer { SizeFlagsVertical = SizeFlags.ExpandFill }; root.AddChild(split); split.SplitOffsets = new[] { 215 };
        var left = new VBoxContainer { CustomMinimumSize = new(205, 0) }; split.AddChild(left);
        left.AddChild(MoonGlassTheme.Label("THƯ VIỆN ASSET", 14, MoonGlassTheme.Gold));
        _library = new OptionButton { ClipText = true, SizeFlagsHorizontal = SizeFlags.ExpandFill }; left.AddChild(_library);
        _entries = ArtStudioLibrary.Entries(); foreach (var e in _entries) _library.AddItem(e.Name);
        Button(left, "Mở mẫu đã chọn", () => ConfirmDiscard(() => SetDocument(ArtStudioLibrary.Load(_entries[_library.Selected].Id), "", "")));
        _clips = new OptionButton { ClipText = true }; left.AddChild(_clips); _clips.ItemSelected += i => { if (!_sync) SelectClip((int)i); };
        left.AddChild(MoonGlassTheme.Label("LAYER / THỨ TỰ VẼ", 13, MoonGlassTheme.Blue));
        _layers = new ItemList { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new(200, 130) }; left.AddChild(_layers);
        _layers.ItemSelected += i => { if (!_sync) { _selected = _doc.Layers[(int)i].Id; Refresh(); } };
        var layerButtons = Row(left); Button(layerButtons, "+ PNG", () => Import(false)); Button(layerButtons, "Nhân đôi", DuplicateLayer); Button(layerButtons, "Xóa", DeleteLayer);
        var fx = new OptionButton(); foreach (var n in SkillVfxPlayer.Names) fx.AddItem(n); left.AddChild(fx);
        Button(left, "+ VFX có sẵn", () => Change(() => { ArtStudioLibrary.AddVfx(_doc, fx.Selected); _selected = _doc.Layers.Last().Id; }));
        var history = Row(left); _undoButton = Button(history, "↶ Undo", Undo); _redoButton = Button(history, "↷ Redo", Redo);
        left.AddChild(MoonGlassTheme.Label("Sprite nguyên khối · PNG gốc được giữ nguyên. Bản chỉnh animation/VFX lưu JSON riêng.", 11, MoonGlassTheme.Muted));
        var body = new HSplitContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill }; split.AddChild(body); body.SplitOffsets = new[] { 620 };
        var center = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, CustomMinimumSize = new(480, 0) }; body.AddChild(center);
        var views = Row(center);
        var tool = new OptionButton(); foreach (var name in new[] { "Kéo layer", "Kéo pivot", "Kéo socket", "Kéo mốc VFX/hit" }) tool.AddItem(name); views.AddChild(tool);
        tool.ItemSelected += i => _stage.Tool = new[] { "move", "pivot", "socket", "marker" }[(int)i];
        Toggle(views, "Lưới", true, v => { _stage.Guides = v; _stage.QueueRedraw(); });
        Toggle(views, "Onion", false, v => { _stage.Onion = v; _stage.QueueRedraw(); });
        Toggle(views, "Nền sáng", true, v => { _stage.Light = v; _stage.QueueRedraw(); });
        Button(views, "Fit", () => _stage.FitContent());
        _stage = new ArtStudioCanvas { CustomMinimumSize = new(440, 260), SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, Zoom = 1.7f };
        center.AddChild(_stage); _stage.BeginEdit = BeginDrag; _stage.DragEdit = Drag; _stage.EndEdit = EndDrag;
        _stage.ViewChanged = () => Status($"Zoom {_stage.Zoom:0.00}× · cuộn để zoom, giữ chuột giữa để pan.");
        _scope = MoonGlassTheme.Label("", 11, MoonGlassTheme.Muted); center.AddChild(_scope);
        var transport = Row(center);
        Button(transport, "|◀", () => Seek(0)); Button(transport, "◀", () => Seek(_frame - 1));
        _play = Button(transport, "▶ Phát", TogglePlay); Button(transport, "▶|", () => Seek(_frame + 1));
        transport.AddChild(new Label { Text = "Tốc độ ×", VerticalAlignment = VerticalAlignment.Center });
        var speed = new SpinBox { MinValue = .1, MaxValue = 4, Step = .1, Value = 1, CustomMinimumSize = new(80, 30) }; transport.AddChild(speed); _numbers["speed"] = speed;
        var fps = new OptionButton(); fps.AddItem("60 FPS"); fps.AddItem("30 FPS"); transport.AddChild(fps); fps.ItemSelected += i => Engine.MaxFps = i == 0 ? 60 : 30;
        _frameLabel = MoonGlassTheme.Label("", 12, MoonGlassTheme.Blue); center.AddChild(_frameLabel);
        _timeline = new HSlider { Step = 1, MinValue = 0 }; center.AddChild(_timeline); _timeline.ValueChanged += v => { if (!_sync) Seek((int)v); };
        var filmScroll = new ScrollContainer { CustomMinimumSize = new(0, 88), VerticalScrollMode = ScrollContainer.ScrollMode.Disabled }; center.AddChild(filmScroll);
        _film = new ArtStudioTimeline { Stage = _stage, Seek = Seek }; filmScroll.AddChild(_film);
        var right = new TabContainer { CustomMinimumSize = new(300, 0) }; body.AddChild(right);
        BuildLayerTab(Tab(right, "Layer")); BuildSheetTab(Tab(right, "Sheet")); BuildAnimationTab(Tab(right, "Anim")); BuildSocketTab(Tab(right, "Neo")); BuildMarkerTab(Tab(right, "VFX/Mốc"));
        var help = Tab(right, "Xuất"); _report = new RichTextLabel { FitContent = true, ScrollActive = false }; help.AddChild(_report);
        Button(help, "Mở thư mục bản lưu", () => { var dir = ProjectSettings.GlobalizePath("user://art_studio"); Directory.CreateDirectory(dir); OS.ShellOpen(dir); });
        Button(help, "Chụp màn hình studio", () => Choose(FileDialog.FileModeEnum.SaveFile, "*.png ; Screenshot", Capture));
        help.AddChild(MoonGlassTheme.Label("Space: phát/dừng · ←/→: frame · Ctrl+Z/Y: undo/redo · Ctrl+S: lưu. Kéo chuột trái trên sân khấu; Ctrl khi kéo để căn đơn vị. Cuộn zoom, chuột giữa pan.\n\nXuất bundle mang theo PNG nguyên gốc và cấu hình JSON. Mốc hitbox chỉ là hướng dẫn trình bày, không gây sát thương. Không tự thay client đang chơi.", 12));
        _events = new RichTextLabel { FitContent = false, CustomMinimumSize = new(0, 70) }; center.AddChild(_events);
        _status = MoonGlassTheme.Label("", 12, MoonGlassTheme.Gold); root.AddChild(_status);
        _dialog = new FileDialog { Access = FileDialog.AccessEnum.Filesystem, Size = new(900, 580), UseNativeDialog = false }; AddChild(_dialog);
        _dialog.FileSelected += p => Safe(() => _fileAction?.Invoke(p));
        _discard = new ConfirmationDialog { Title = "Bản chỉnh chưa lưu", DialogText = "Mở dữ liệu khác sẽ bỏ các thay đổi chưa lưu. Tiếp tục?" }; AddChild(_discard);
        _discard.Confirmed += () => { var pending = _pending; _pending = null; Safe(() => pending?.Invoke()); };
        int defaultIndex = Array.FindIndex(_entries, e => e.Id == "npc_lyan_idle"); _library.Select(defaultIndex);
        SetDocument(ArtStudioLibrary.Load("npc_lyan_idle"), "", "");
        var args = OS.GetCmdlineUserArgs(); int project = Array.IndexOf(args, "--studio-project");
        if (project >= 0 && project + 1 < args.Length) LoadProject(args[project + 1]);
        int entry = Array.IndexOf(args, "--studio-entry");
        if (entry >= 0 && entry + 1 < args.Length) { SetDocument(ArtStudioLibrary.Load(args[entry + 1]), "", ""); int item = Array.FindIndex(_entries, e => e.Id == args[entry + 1]); if (item >= 0) _library.Select(item); }
        int direction = Array.IndexOf(args, "--studio-direction");
        if (direction >= 0 && direction + 1 < args.Length) { int at = _doc.Clips.FindIndex(c => c.Direction == args[direction + 1]); if (at >= 0) SelectClip(at); }
        int frame = Array.IndexOf(args, "--studio-frame");
        if (frame >= 0 && frame + 1 < args.Length && int.TryParse(args[frame + 1], out int atFrame)) Seek(atFrame);
        if(args.Contains("--studio-loop"))Clip.Loop=true;
        if(args.Contains("--studio-play"))TogglePlay();
        if (args.Contains("--studio-self-test")) { RunTests(); return; }
        FitAfterLayout();
        int capture = Array.IndexOf(args, "--studio-capture"); if (capture >= 0 && capture + 1 < args.Length) Capture(args[capture + 1], true);
    }
    private void BuildLayerTab(VBoxContainer tab)
    {
        _layerName = Text(tab, "Tên layer", v => Change(() => Layer.Name = v));
        _visible = Toggle(tab, "Hiển thị", true, v => Change(() => Layer.Visible = v));
        _locked = Toggle(tab, "Khóa kéo/chỉnh", false, v => Change(() => Layer.Locked = v));
        _keyMode = Toggle(tab, "Chỉnh KEY tại frame hiện tại", true, _ => Refresh());
        tab.AddChild(MoonGlassTheme.Label("Tắt KEY để chỉnh pose nền. Layer đã có key vẫn dùng key của clip.", 11, MoonGlassTheme.Muted));
        Number(tab, "z", "Thứ tự lớp Z", -1000, 1000, 1, 0, v => Change(() => Layer.Z = (int)v));
        _attach = new OptionButton { ClipText = true }; tab.AddChild(MoonGlassTheme.Label("Gắn vào socket", 12)); tab.AddChild(_attach);
        _attach.ItemSelected += i => { if (!_sync) Change(() => Layer.AttachSocket = _socketIds[(int)i]); };
        foreach (var n in new[] { ("x", "Vị trí X", -10000d, 10000d, .5d), ("y", "Vị trí Y", -10000d, 10000d, .5d), ("px", "Pivot X (px nguồn)", -10000d, 10000d, .5d), ("py", "Pivot Y (px nguồn)", -10000d, 10000d, .5d),
            ("sx", "Scale X / âm = lật", -10d, 10d, .01d), ("sy", "Scale Y / âm = lật", -10d, 10d, .01d), ("angle", "Góc xoay °", -3600d, 3600d, 1d), ("alpha", "Độ hiện", 0d, 1d, .05d), ("source", "Ảnh nguồn #", 0d, 511d, 1d) })
        { string key = n.Item1; Number(tab, key, n.Item2, n.Item3, n.Item4, n.Item5, 0, v => EditPose(p => SetPoseValue(p, key, (float)v))); }
    }
    private void BuildSheetTab(VBoxContainer tab)
    {
        _source = Text(tab, "PNG gốc (chỉ đọc)", _ => { }); _source.Editable = false;
        Button(tab, "Thay PNG của layer…", () => Import(true));
        foreach (var name in new[] { "rx", "ry", "rw", "rh" })
        { string id = name; Number(tab, id, new Dictionary<string, string> { ["rx"] = "Crop X", ["ry"] = "Crop Y", ["rw"] = "Crop rộng", ["rh"] = "Crop cao" }[id], id is "rw" or "rh" ? 1 : 0, 8192, 1, 1, v => Change(() => { int index = Array.IndexOf(new[] { "rx", "ry", "rw", "rh" }, id); Layer.Regions[Pose().SourceFrame][index] = (int)v; }, true)); }
        tab.AddChild(MoonGlassTheme.Label("Sheet cũ dùng crop không đều đã đo sẵn. Chỉ tạo lưới mới cho sheet có ô bằng nhau.", 11, MoonGlassTheme.Muted));
        Number(tab, "cols", "Số cột", 1, 64, 1, 8, _ => { }); Number(tab, "rows", "Số hàng", 1, 64, 1, 10, _ => { });
        Button(tab, "Chia sheet theo lưới này", GridSheet);
        Button(tab, "Gán dãy ảnh nguồn vào clip", () => Change(() => { for (int f = 0; f < Clip.DurationsMs.Count; f++) { var p = Pose(f); p.SourceFrame = Math.Min(f, Layer.Regions.Count - 1); ArtStudioSampler.SetKey(Clip, Layer.Id, f, p); } }));
        tab.AddChild(MoonGlassTheme.Label("Gán nguồn không tạo ảnh mới; thiếu pose phải vẽ bổ sung. PNG gốc luôn giữ nguyên.", 11));
    }
    private void BuildAnimationTab(VBoxContainer tab)
    {
        _clipName = Text(tab, "Tên clip (Enter áp dụng)", v => Change(() => Clip.Name = v));
        _direction = new OptionButton(); foreach (var d in ArtStudioCodec.Directions) _direction.AddItem(d); tab.AddChild(_direction);
        _direction.ItemSelected += i => { if (!_sync) Change(() => Clip.Direction = ArtStudioCodec.Directions[(int)i]); };
        Number(tab, "count", "Số ô timeline", 1, 120, 1, 16, v => Change(() => { ArtStudioSampler.Resize(Clip, (int)v); _frame = Math.Min(_frame, (int)v - 1); }));
        Number(tab, "ms", "Thời gian frame này (ms)", 5, 10000, .5, 62.5, v => Change(() => Clip.DurationsMs[_frame] = (float)v));
        Button(tab, "Áp ms này cho toàn clip", () => Change(() => { float ms = (float)_numbers["ms"].Value; for (int i = 0; i < Clip.DurationsMs.Count; i++) Clip.DurationsMs[i] = ms; }));
        _loop = Toggle(tab, "Lặp clip", true, v => Change(() => Clip.Loop = v));
        _interpolate = Toggle(tab, "Nội suy vị trí / góc / scale", false, v => Change(() => Track().Interpolate = v));
        Button(tab, "Đặt key hiện tại", () => EditPose(_ => { }));
        Button(tab, "Xóa key tại frame", () => Change(() => { var t = Clip.Tracks.FirstOrDefault(t => t.LayerId == Layer.Id); t?.Keys.RemoveAll(k => k.Frame == _frame); }));
        var row = Row(tab); Button(row, "Copy pose", () => { _clipboard = Pose(); Status("Đã copy pose của layer, không sao chép bitmap."); });
        Button(row, "Paste pose", () => { if (_clipboard != null) Change(() => { if (_clipboard.SourceFrame >= Layer.Regions.Count) throw new Exception("Ảnh nguồn không có ở layer đích."); ArtStudioSampler.SetKey(Clip, Layer.Id, _frame, _clipboard); }); });
        Button(tab, "Nhân clip để chỉnh tiếp", () => Change(() => { var tmp = ArtStudioCodec.Decode(ArtStudioCodec.Encode(_doc)); var c = tmp.Clips[_clip]; c.Name += "_copy"; int n = 2; while (_doc.Clips.Any(x => x.Name == c.Name && x.Direction == c.Direction)) c.Name = Clip.Name + "_copy" + n++; _doc.Clips.Add(c); _clip = _doc.Clips.Count - 1; }));
        Button(tab, "Xóa clip", () => Change(() => { if (_doc.Clips.Count == 1) throw new Exception("Giữ ít nhất một clip."); _doc.Clips.RemoveAt(_clip); _clip = 0; _frame = 0; }));
        tab.AddChild(MoonGlassTheme.Label("16–20 pose nguồn/hành động/hướng; render mặc định 60 FPS. FPS hiển thị khác với số pose vẽ. Không tự chép pose để chứng nhận đủ animation.", 11, MoonGlassTheme.Muted));
    }
    private void BuildSocketTab(VBoxContainer tab)
    {
        _socket = new OptionButton { ClipText = true }; tab.AddChild(_socket); _socket.ItemSelected += i => { if (!_sync) { _stage.SelectedSocket = (int)i; Refresh(); } };
        _socketName = Text(tab, "Tên điểm neo", v => EditSocket(s => s.Name = v));
        Number(tab, "socketx", "Neo X (px nguồn layer)", -10000, 10000, .5, 0, v => EditSocket(s => s.X = (float)v));
        Number(tab, "sockety", "Neo Y (px nguồn layer)", -10000, 10000, .5, 0, v => EditSocket(s => s.Y = (float)v));
        Button(tab, "+ Neo trên layer đang chọn", () => Change(() => { var p = Pose(); _doc.Sockets.Add(new() { Name = "hand_r_" + (_doc.Sockets.Count + 1), LayerId = Layer.Id, X = p.PivotX, Y = p.PivotY }); _stage.SelectedSocket = _doc.Sockets.Count - 1; }));
        Button(tab, "+ Neo ở gốc nhân vật", () => Change(() => { _doc.Sockets.Add(new() { Name = "origin_" + (_doc.Sockets.Count + 1) }); _stage.SelectedSocket = _doc.Sockets.Count - 1; }));
        Button(tab, "Xóa neo đang chọn", () => Change(() => { if (_doc.Sockets.Count == 0) return; var s = _doc.Sockets[_stage.SelectedSocket]; if (_doc.Layers.Any(l => l.AttachSocket == s.Id)) throw new Exception("Hãy tháo layer đang gắn vào neo này trước."); _doc.Sockets.Remove(s); _stage.SelectedSocket = 0; }));
        tab.AddChild(MoonGlassTheme.Label("Neo trên layer dùng tọa độ pixel bên trong vùng crop; tự đi theo key, pivot, xoay và scale của layer. Gắn vũ khí/VFX qua tab Layer. Không cho phép gắn vòng lặp.", 12));
    }
    private void BuildMarkerTab(VBoxContainer tab)
    {
        tab.AddChild(MoonGlassTheme.Label("TIMING VFX CỦA LAYER ĐANG CHỌN", 12, MoonGlassTheme.Gold));
        Number(tab, "fxstart", "Bắt đầu (frame 0-based)", 0, 119, 1, 0, _ => { });
        Number(tab, "fxend", "Kết thúc (bao gồm frame)", 0, 119, 1, 15, _ => { });
        Number(tab, "fxcycles", "Số lần chạy sheet", 1, 10, 1, 1, _ => { });
        Button(tab, "Gán timing vào key VFX", () => Change(() =>
        {
            if (Layer.Kind != "vfx") throw new Exception("Chọn một layer VFX ở danh sách bên trái.");
            int start = (int)_numbers["fxstart"].Value, end = (int)_numbers["fxend"].Value, cycles = (int)_numbers["fxcycles"].Value;
            if (end < start || end >= Clip.DurationsMs.Count) throw new Exception("Khoảng VFX phải nằm trong timeline.");
            var rest = Pose(); if (rest.Alpha <= 0) rest.Alpha = 1;
            for (int f = 0; f < Clip.DurationsMs.Count; f++)
            {
                var p = rest.Copy(); p.Alpha = f >= start && f <= end ? rest.Alpha : 0;
                p.SourceFrame = f < start || f > end ? 0 : Math.Min(Layer.Regions.Count - 1, (int)((f - start) * cycles * (double)Layer.Regions.Count / (end - start + 1)) % Layer.Regions.Count);
                ArtStudioSampler.SetKey(Clip, Layer.Id, f, p);
            }
            Track().Interpolate = false;
        }));
        tab.AddChild(MoonGlassTheme.Label("VFX nhập PNG: chọn mục này rồi đổi loại layer bằng nút bên dưới. Đây là timing trình bày, không đổi thời điểm sát thương.", 11, MoonGlassTheme.Muted));
        Button(tab, "Đánh dấu layer là VFX", () => Change(() => Layer.Kind = "vfx"));
        Button(tab, "Đánh dấu layer là sprite", () => Change(() => Layer.Kind = "sprite"));
        tab.AddChild(MoonGlassTheme.Label("MỐC ÂM THANH / HITBOX / VFX", 12, MoonGlassTheme.Gold));
        _marker = new OptionButton { ClipText = true }; tab.AddChild(_marker); _marker.ItemSelected += i => { if (!_sync) { _stage.SelectedMarker = (int)i; Refresh(); } };
        _markerName = Text(tab, "Tên mốc / cue ID", v => EditMarker(m => m.Name = v));
        _markerKind = new OptionButton(); foreach (var n in new[] { "sfx", "hitbox", "vfx", "footstep" }) _markerKind.AddItem(n); tab.AddChild(_markerKind);
        _markerKind.ItemSelected += i => { if (!_sync) EditMarker(m => m.Kind = new[] { "sfx", "hitbox", "vfx", "footstep" }[(int)i]); };
        Number(tab, "markerframe", "Frame phát mốc", 0, 119, 1, 0, v => EditMarker(m => m.Frame = (int)v));
        Number(tab, "markerx", "Mốc X (không gian nhân vật)", -10000, 10000, .5, 0, v => EditMarker(m => m.X = (float)v));
        Number(tab, "markery", "Mốc Y", -10000, 10000, .5, 0, v => EditMarker(m => m.Y = (float)v));
        Number(tab, "radius", "Bán kính hướng dẫn", 0, 10000, .5, 12, v => EditMarker(m => m.Radius = (float)v));
        Button(tab, "+ Mốc tại frame hiện tại", () => Change(() => { Clip.Markers.Add(new() { Frame = _frame, Y = -70, Name = "cue_" + (Clip.Markers.Count + 1) }); _stage.SelectedMarker = Clip.Markers.Count - 1; }));
        Button(tab, "Xóa mốc", () => Change(() => { if (Clip.Markers.Count > 0) Clip.Markers.RemoveAt(_stage.SelectedMarker); _stage.SelectedMarker = 0; }));
        tab.AddChild(MoonGlassTheme.Label("Mốc SFX chỉ ghi cue ID và log khi playback đi qua. Chưa phát file âm thanh. Hitbox chỉ để chỉnh vị trí hình ảnh; server vẫn quyết định trúng/sát thương.", 12, MoonGlassTheme.Muted));
        Toggle(tab, "Giữ nét PNG (nearest)", true, v => { _stage.Nearest = v; _stage.QueueRedraw(); });
    }
    private HBoxContainer Row(Node parent) { var row = new HBoxContainer(); row.AddThemeConstantOverride("separation", 5); parent.AddChild(row); return row; }
    private VBoxContainer Tab(TabContainer tabs, string name)
    {
        var scroll = new ScrollContainer { Name = name, HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled }; tabs.AddChild(scroll);
        var box = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill }; box.AddThemeConstantOverride("separation", 7); scroll.AddChild(box); return box;
    }
    private Button Button(Node parent, string text, Action action)
    { var b = MoonGlassTheme.Button(text); b.AddThemeFontSizeOverride("font_size", 12); b.CustomMinimumSize = new(0, 30); parent.AddChild(b); b.Pressed += () => Safe(action); return b; }
    private CheckButton Toggle(Node parent, string text, bool value, Action<bool> action)
    { var c = new CheckButton { Text = text, ButtonPressed = value }; c.AddThemeFontSizeOverride("font_size", 12); parent.AddChild(c); c.Toggled += v => { if (!_sync) Safe(() => action(v)); }; return c; }
    private LineEdit Text(Node parent, string label, Action<string> action)
    { parent.AddChild(MoonGlassTheme.Label(label, 11, MoonGlassTheme.Muted)); var edit = new LineEdit { MaxLength = 120 }; parent.AddChild(edit); edit.TextSubmitted += v => { if (!_sync) Safe(() => action(v)); }; return edit; }
    private SpinBox Number(Node parent, string id, string label, double min, double max, double step, double initial, Action<double> action)
    {
        var row = Row(parent); row.AddChild(MoonGlassTheme.Label(label, 12));
        var n = new SpinBox { MinValue = min, MaxValue = max, Step = step, Value = initial, CustomMinimumSize = new(102, 29), UpdateOnTextChanged = false }; row.AddChild(n);
        n.AddThemeFontSizeOverride("font_size", 12); n.ValueChanged += v => { if (!_sync) Safe(() => action(v)); }; _numbers[id] = n; return n;
    }
    private void Safe(Action action) { try { action(); } catch (Exception e) { Status("Không áp dụng: " + e.Message); } }
    private void Status(string text) => _status.Text = text;
    private void ConfirmDiscard(Action action) { if (_dirty) { _pending = action; _discard.PopupCentered(); } else Safe(action); }
    private void Choose(FileDialog.FileModeEnum mode, string filter, Action<string> action)
    { _playing = false; _play.Text = "▶ Phát"; _fileAction = action; _dialog.FileMode = mode; _dialog.Filters = new[] { filter }; _dialog.CurrentFile = mode == FileDialog.FileModeEnum.SaveFile ? (filter.StartsWith("*.png", StringComparison.Ordinal) ? "studio.png" : "sprite-project.json") : ""; _dialog.PopupCentered(); }
    private ArtStudioPose Pose(int? frame = null) => ArtStudioSampler.Pose(Layer, Clip, frame ?? _frame);
    private ArtStudioTrack Track()
    { var t = Clip.Tracks.FirstOrDefault(t => t.LayerId == Layer.Id); if (t == null) { t = new() { LayerId = Layer.Id }; Clip.Tracks.Add(t); } return t; }
    private void SetDocument(ArtStudioDocument doc, string sourceRoot, string path)
    {
        ArtStudioCodec.Validate(doc); ArtStudioCodec.ValidateTextures(doc, sourceRoot);
        _doc = doc; _root = sourceRoot; _path = path == "" ? "user://art_studio/projects/current.json" : path; _clip = Math.Max(0, doc.Clips.FindIndex(c => c.Direction == "S")); _frame = 0; _selected = doc.Layers[0].Id;
        _playing = false; _time = 0; _undo.Clear(); _redo.Clear(); _saved = ArtStudioCodec.Encode(_doc); _dirty = false; _stage.ClearTextures(); _stage.SelectedSocket = _stage.SelectedMarker = 0;
        SelectClip(_clip); Status("Đã mở sprite cũ: " + doc.Name + ". PNG gốc giữ nguyên; chỉnh JSON riêng.");
    }
    private void Change(Action action, bool checkTextures = false)
    {
        if (_sync) return; _playing = false;
        string before = ArtStudioCodec.Encode(_doc); string selected = _selected; int clip = _clip, frame = _frame;
        try { action(); ArtStudioCodec.Validate(_doc); if (checkTextures) ArtStudioCodec.ValidateTextures(_doc, _root); }
        catch { _doc = ArtStudioCodec.Decode(before); _selected = selected; _clip = clip; _frame = frame; Refresh(); throw; }
        if (ArtStudioCodec.Encode(_doc) != before) { Push(before); _redo.Clear(); }
        _time = ArtStudioSampler.TimeAt(Clip, _frame); Refresh();
    }
    private void Push(string before) { _undo.Push(before); if (_undo.Count > 100) { var keep = _undo.Take(100).Reverse().ToArray(); _undo.Clear(); foreach (var s in keep) _undo.Push(s); } }
    private void EditPose(Action<ArtStudioPose> action)
    {
        if (Layer.Locked) { Status("Layer đang khóa."); return; }
        Change(() => { var p = _keyMode.ButtonPressed ? Pose() : Layer.Rest.Copy(); action(p); if (_keyMode.ButtonPressed) ArtStudioSampler.SetKey(Clip, Layer.Id, _frame, p); else Layer.Rest = p; });
    }
    private static void SetPoseValue(ArtStudioPose p, string id, float value)
    {
        switch (id) { case "x": p.X = value; break; case "y": p.Y = value; break; case "px": p.PivotX = value; break; case "py": p.PivotY = value; break; case "sx": p.ScaleX = value; break; case "sy": p.ScaleY = value; break; case "angle": p.Angle = value; break; case "alpha": p.Alpha = value; break; case "source": p.SourceFrame = (int)value; break; }
    }
    private void EditSocket(Action<ArtStudioSocket> action) { if (_doc.Sockets.Count > 0) Change(() => action(_doc.Sockets[_stage.SelectedSocket])); }
    private void EditMarker(Action<ArtStudioMarker> action) { if (Clip.Markers.Count > 0) Change(() => action(Clip.Markers[_stage.SelectedMarker])); }
    private void Refresh()
    {
        _sync = true;
        try
        {
            _clip = Math.Clamp(_clip, 0, _doc.Clips.Count - 1); _frame = Math.Clamp(_frame, 0, Clip.DurationsMs.Count - 1);
            if (_doc.Layers.All(l => l.Id != _selected)) _selected = _doc.Layers[0].Id;
            _layers.Clear(); foreach (var l in _doc.Layers) _layers.AddItem((l.Visible ? "● " : "○ ") + l.Name + (l.Locked ? " [khóa]" : "")); _layers.Select(_doc.Layers.IndexOf(Layer));
            _clips.Clear(); foreach (var c in _doc.Clips) _clips.AddItem(c.Name + " / " + c.Direction); _clips.Select(_clip);
            _layerName.Text = Layer.Name; _source.Text = Layer.Texture; _visible.ButtonPressed = Layer.Visible; _locked.ButtonPressed = Layer.Locked;
            var p = _keyMode.ButtonPressed ? Pose() : Layer.Rest;
            var values = new Dictionary<string, double> { ["x"] = p.X, ["y"] = p.Y, ["px"] = p.PivotX, ["py"] = p.PivotY, ["sx"] = p.ScaleX, ["sy"] = p.ScaleY, ["angle"] = p.Angle, ["alpha"] = p.Alpha, ["source"] = p.SourceFrame, ["z"] = Layer.Z, ["count"] = Clip.DurationsMs.Count, ["ms"] = Clip.DurationsMs[_frame] };
            _numbers["source"].MaxValue = Layer.Regions.Count - 1;
            var region = Layer.Regions[p.SourceFrame]; for (int i = 0; i < 4; i++) values[new[] { "rx", "ry", "rw", "rh" }[i]] = region[i];
            _clipName.Text = Clip.Name; _direction.Select(Array.IndexOf(ArtStudioCodec.Directions, Clip.Direction)); _loop.ButtonPressed = Clip.Loop;
            _interpolate.ButtonPressed = Clip.Tracks.FirstOrDefault(t => t.LayerId == Layer.Id)?.Interpolate ?? true;
            _attach.Clear(); _attach.AddItem("Không gắn (actor space)"); _socketIds = new[] { "" }.Concat(_doc.Sockets.Select(s => s.Id)).ToArray(); foreach (var s in _doc.Sockets) _attach.AddItem(s.Name); _attach.Select(Array.IndexOf(_socketIds, Layer.AttachSocket));
            _socket.Clear(); foreach (var s in _doc.Sockets) _socket.AddItem(s.Name); _socket.Disabled = _doc.Sockets.Count == 0;
            if (_doc.Sockets.Count > 0) { _stage.SelectedSocket = Math.Clamp(_stage.SelectedSocket, 0, _doc.Sockets.Count - 1); _socket.Select(_stage.SelectedSocket); var s = _doc.Sockets[_stage.SelectedSocket]; _socketName.Text = s.Name; values["socketx"] = s.X; values["sockety"] = s.Y; } else _socketName.Text = "";
            _marker.Clear(); foreach (var m in Clip.Markers) _marker.AddItem($"f{m.Frame}: {m.Name}"); _marker.Disabled = Clip.Markers.Count == 0;
            if (Clip.Markers.Count > 0) { _stage.SelectedMarker = Math.Clamp(_stage.SelectedMarker, 0, Clip.Markers.Count - 1); _marker.Select(_stage.SelectedMarker); var m = Clip.Markers[_stage.SelectedMarker]; _markerName.Text = m.Name; _markerKind.Select(Array.IndexOf(new[] { "sfx", "hitbox", "vfx", "footstep" }, m.Kind)); values["markerframe"] = m.Frame; values["markerx"] = m.X; values["markery"] = m.Y; values["radius"] = m.Radius; } else _markerName.Text = "";
            _numbers["markerframe"].MaxValue = Clip.DurationsMs.Count - 1;
            _numbers["fxstart"].MaxValue = _numbers["fxend"].MaxValue = Clip.DurationsMs.Count - 1;
            foreach (var v in values) _numbers[v.Key].Value = v.Value;
            _timeline.MaxValue = Clip.DurationsMs.Count - 1; _timeline.Value = _frame;
            _dirty = ArtStudioCodec.Encode(_doc) != _saved; _fileLabel.Text = (_dirty ? "● Chưa lưu · " : "Đã lưu/nạp · ") + ProjectSettings.GlobalizePath(_path);
            _undoButton.Disabled = _undo.Count == 0; _redoButton.Disabled = _redo.Count == 0; _play.Text = _playing ? "Ⅱ Dừng" : "▶ Phát";
            _report.Text = string.Join("\n\n", ArtStudioCodec.Readiness(_doc)); _scope.Text = $"{Clip.Direction} · {Clip.DurationsMs.Count} frame · clip {Clip.Duration:0.00}s · +X phải / +Y xuống\n{Clip.SourceNote}";
            SyncStage();
        }
        finally { _sync = false; }
    }
    private void SyncStage()
    {
        _stage.Document = _doc; _stage.SourceRoot = _root; _stage.ClipIndex = _clip; _stage.SelectedId = _selected;
        _stage.Frame = _playing ? ArtStudioSampler.FractionalFrame(Clip, _time) : _frame; _stage.QueueRedraw();
        _film.Refresh();
        _frameLabel.Text = $"FRAME {_frame + 1:00}/{Clip.DurationsMs.Count}  ·  {Clip.DurationsMs[_frame]:0.0} ms  ·  key layer: {string.Join(",", Clip.Tracks.FirstOrDefault(t => t.LayerId == Layer.Id)?.Keys.Select(k => k.Frame + 1) ?? Array.Empty<int>())}";
    }
    private void SelectClip(int index)
    {
        _playing = false; _clip = index; _frame = 0; _time = 0;
        var active = Clip.Tracks.Select(t => _doc.Layers.First(l => l.Id == t.LayerId)).FirstOrDefault(l => l.Kind == "sprite" && ArtStudioSampler.Pose(l, Clip, 0).Alpha > 0);
        if (active != null) _selected = active.Id; Refresh();
    }
    private async void FitAfterLayout()
    { for (int i = 0; i < 2; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); _stage.FitContent(); }
    private void Seek(int frame) { _playing = false; _frame = Math.Clamp(frame, 0, Clip.DurationsMs.Count - 1); _time = ArtStudioSampler.TimeAt(Clip, _frame); Refresh(); }
    private void TogglePlay()
    {
        _playing = !_playing;
        if (_playing && !Clip.Loop && _time >= Clip.Duration) { _time = 0; _frame = 0; }
        if (_playing && Math.Abs(_time - ArtStudioSampler.TimeAt(Clip, _frame)) < .00001)
            foreach (var m in Clip.Markers.Where(m => m.Frame == _frame)) LogMarker(m, 1);
        Refresh();
    }
    public override void _Process(double delta)
    {
        if (!_playing || _doc == null) return;
        double previous = _time, next = previous + delta * _numbers["speed"].Value;
        foreach (var m in Clip.Markers)
        {
            int cycles = ArtStudioSampler.MarkerCrossings(Clip, m, previous, next);
            if (cycles > 0) LogMarker(m, cycles);
        }
        _time = Clip.Loop ? next % Clip.Duration : Math.Min(next, Clip.Duration); _frame = ArtStudioSampler.FrameAt(Clip, _time);
        if (!Clip.Loop && next >= Clip.Duration) { _playing = false; Refresh(); }
        _sync = true; _timeline.Value = _frame; _sync = false; SyncStage();
    }
    private void LogMarker(ArtStudioMarker m, int cycles)
    { _events.Text = $"[{Clip.Name}/{Clip.Direction}] {m.Kind} / {m.Name} @ ({m.X:0.0},{m.Y:0.0}) f{m.Frame + 1} ×{cycles}\n" + _events.Text; if (_events.Text.Length > 2000) _events.Text = _events.Text[..2000]; }
    private void Undo() { if (_undo.Count == 0) return; _playing = false; _redo.Push(ArtStudioCodec.Encode(_doc)); _doc = ArtStudioCodec.Decode(_undo.Pop()); Refresh(); }
    private void Redo() { if (_redo.Count == 0) return; _playing = false; Push(ArtStudioCodec.Encode(_doc)); _doc = ArtStudioCodec.Decode(_redo.Pop()); Refresh(); }
    private void BeginDrag() { _playing = false; _dragChanged = false; _dragBefore = ArtStudioCodec.Encode(_doc); }
    private void Drag(Vector2 delta, bool snap)
    {
        if (_doc == null || Layer.Locked) return;
        if (snap) delta = delta.Round();
        if (_stage.Tool is "move" or "pivot")
        {
            var p = _keyMode.ButtonPressed ? Pose() : Layer.Rest.Copy();
            var world = ArtStudioSampler.Transform(_doc, Clip, Layer, _frame);
            if (_stage.Tool == "pivot") { Vector2 local = world.AffineInverse().BasisXform(delta); p.PivotX -= local.X; p.PivotY -= local.Y; }
            else
            {
                if (Layer.AttachSocket != "") { var own = p.Transform; var parent = world * own.AffineInverse(); delta = parent.AffineInverse().BasisXform(delta); }
                p.X += delta.X; p.Y += delta.Y;
            }
            if (_keyMode.ButtonPressed) ArtStudioSampler.SetKey(Clip, Layer.Id, _frame, p); else Layer.Rest = p;
        }
        else if (_stage.Tool == "socket" && _doc.Sockets.Count > 0)
        {
            var s = _doc.Sockets[_stage.SelectedSocket];
            if (s.LayerId != "") { var l = _doc.Layers.Single(l => l.Id == s.LayerId); delta = ArtStudioSampler.Transform(_doc, Clip, l, _frame).AffineInverse().BasisXform(delta); }
            s.X += delta.X; s.Y += delta.Y;
        }
        else if (_stage.Tool == "marker" && Clip.Markers.Count > 0) { var m = Clip.Markers[_stage.SelectedMarker]; m.X += delta.X; m.Y += delta.Y; }
        _dragChanged = true; Refresh();
    }
    private void EndDrag() { if (_dragChanged && ArtStudioCodec.Encode(_doc) != _dragBefore) { Push(_dragBefore); _redo.Clear(); Refresh(); } }
    private void DuplicateLayer()
    { Change(() => { var copy = ArtStudioCodec.Decode(ArtStudioCodec.Encode(_doc)).Layers.Single(l => l.Id == _selected); string old = copy.Id; copy.Id = Guid.NewGuid().ToString("N"); copy.Name += " copy"; copy.Z++; _doc.Layers.Add(copy); foreach (var c in _doc.Clips) { var track = c.Tracks.FirstOrDefault(t => t.LayerId == old); if (track != null) c.Tracks.Add(new() { LayerId = copy.Id, Interpolate = track.Interpolate, Keys = track.Keys.Select(k => new ArtStudioKey { Frame = k.Frame, Pose = k.Pose.Copy() }).ToList() }); } _selected = copy.Id; }); }
    private void DeleteLayer()
    {
        Change(() => { if (_doc.Layers.Count == 1) throw new Exception("Giữ ít nhất một layer."); if (_doc.Sockets.Any(s => s.LayerId == _selected && _doc.Layers.Any(l => l.AttachSocket == s.Id))) throw new Exception("Tháo các layer đang gắn vào neo của layer này trước."); _doc.Sockets.RemoveAll(s => s.LayerId == _selected); foreach (var c in _doc.Clips) c.Tracks.RemoveAll(t => t.LayerId == _selected); _doc.Layers.Remove(Layer); _selected = _doc.Layers[0].Id; });
    }
    private void Import(bool replace)
    {
        Choose(FileDialog.FileModeEnum.OpenFile, "*.png ; Sprite sheet / VFX", file =>
        {
            string resource = ArtStudioCodec.ImportPng(file); using var texture = ArtStudioCodec.Texture(resource, "");
            Change(() =>
            {
                if (replace) Layer.Texture = resource;
                else { var l = new ArtStudioLayer { Name = Path.GetFileNameWithoutExtension(file), Texture = resource, Regions = new() { new[] { 0, 0, texture.GetWidth(), texture.GetHeight() } }, Rest = new() { PivotX = texture.GetWidth() / 2f, PivotY = texture.GetHeight(), ScaleX = .5f, ScaleY = .5f } }; _doc.Layers.Add(l); _selected = l.Id; }
            }, true);
        });
    }
    private void GridSheet()
    {
        Change(() =>
        {
            using var texture = ArtStudioCodec.Texture(Layer.Texture, _root); int cols = (int)_numbers["cols"].Value, rows = (int)_numbers["rows"].Value;
            if (cols * rows > 512) throw new Exception("Tối đa 512 vùng nguồn/layer.");
            var regions = new List<int[]>();
            for (int y = 0; y < rows; y++) for (int x = 0; x < cols; x++) { int x0 = x * texture.GetWidth() / cols, y0 = y * texture.GetHeight() / rows; regions.Add(new[] { x0, y0, (x + 1) * texture.GetWidth() / cols - x0, (y + 1) * texture.GetHeight() / rows - y0 }); }
            Layer.Regions = regions; Layer.Rest.SourceFrame = 0; foreach (var c in _doc.Clips) foreach (var t in c.Tracks.Where(t => t.LayerId == _selected)) foreach (var k in t.Keys) k.Pose.SourceFrame = Math.Min(k.Pose.SourceFrame, regions.Count - 1);
        }, true);
    }
    private void LoadProject(string path)
    {
        string absolute = Path.GetFullPath(path); var doc = ArtStudioCodec.Decode(File.ReadAllText(absolute));
        SetDocument(doc, Path.GetDirectoryName(absolute)!, absolute);
    }
    private void Save() => SaveAs(_path);
    private void SaveAs(string path)
    {
        // A bundle-relative project needs portable textures when saved into another folder.
        string abs = path.Contains("://", StringComparison.Ordinal) ? ProjectSettings.GlobalizePath(path) : Path.GetFullPath(path);
        if (_doc.Layers.Any(l => l.Texture.StartsWith("textures/", StringComparison.Ordinal)) && Path.GetDirectoryName(abs) != _root)
        { ArtStudioCodec.ExportBundle(abs, _doc, _root); SetDocument(ArtStudioCodec.Decode(File.ReadAllText(abs)), Path.GetDirectoryName(abs)!, abs); }
        else { ArtStudioCodec.SaveAtomic(path, _doc); _path = path; _saved = ArtStudioCodec.Encode(_doc); Refresh(); }
        Status("Đã lưu: " + abs + " (.bak giữ bản trước).");
    }
    private async void Capture(string path, bool quit)
    {
        for (int i = 0; i < 5; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var error = GetViewport().GetTexture().GetImage().SavePng(path); GD.Print("ART_STUDIO_CAPTURE " + error);
        if (quit) GetTree().Quit(error == Error.Ok ? 0 : 1); else Status("Đã chụp studio: " + error);
    }
    private void Capture(string path) => Capture(path, false);
    public override void _UnhandledKeyInput(InputEvent e)
    {
        if (e is not InputEventKey k || !k.Pressed || k.Echo || GetViewport().GuiGetFocusOwner() is LineEdit or TextEdit) return;
        if (k.CtrlPressed && k.Keycode == Key.S) Safe(Save); else if (k.CtrlPressed && k.Keycode == Key.Z) Undo(); else if (k.CtrlPressed && k.Keycode == Key.Y) Redo();
        else if (k.Keycode == Key.Space) TogglePlay(); else if (k.Keycode == Key.Left) Seek(_frame - 1); else if (k.Keycode == Key.Right) Seek(_frame + 1); else return;
        GetViewport().SetInputAsHandled();
    }
}
