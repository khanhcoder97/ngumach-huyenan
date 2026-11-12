using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Development review scene. Missing art stays visibly missing; no gameplay simulation.</summary>
public partial class ActorLibraryBrowser : Control
{
    private ActorLibraryData _library=null!;
    private readonly List<ActorLibraryData.Actor> _filtered=new();
    private readonly ActorLibrarySprite[] _sprites=new ActorLibrarySprite[8];
    private readonly Label[] _labels=new Label[8];
    private ItemList _list=null!;
    private OptionButton _category=null!,_clips=null!;
    private LineEdit _search=null!;
    private Label _title=null!,_status=null!,_frame=null!;
    private Control _stage=null!;
    private HSlider _timeline=null!;
    private Button _play=null!;
    private string _actor="",_clip="idle";
    private bool _paused,_sync,_staticCapture,_offlineMovie;
    private int _activeFrames=16;
    private int _captureFrame=8;
    private double _refresh;
    private string? _benchmarkPath;
    private ulong _benchmarkStart,_lastTick;
    private readonly List<double> _samples=new();
    public override void _Ready()
    {
        try{Build();}catch(Exception error){SetProcess(false);GD.PushError("ACTOR_LIBRARY_INIT_FAIL "+error);GetTree().Quit(1);}
    }
    private void Build()
    {
        Engine.MaxFps=60;if(DisplayServer.GetName()!="headless"){DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Enabled);float refresh=DisplayServer.ScreenGetRefreshRate();if(refresh>=59&&refresh<=61)Engine.MaxFps=0;}Theme=MoonGlassTheme.Create();
        AddChild(new ColorRect{Color=Color.FromHtml("#171c2d"),MouseFilter=MouseFilterEnum.Ignore,Size=new Vector2(1280,720)});
        _library=new ActorLibraryData(reviewMode:true);
        var margin=new MarginContainer();margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);foreach(var edge in new[]{"left","right","top","bottom"})margin.AddThemeConstantOverride("margin_"+edge,16);AddChild(margin);
        var split=new HBoxContainer();split.AddThemeConstantOverride("separation",20);margin.AddChild(split);
        var left=new VBoxContainer{CustomMinimumSize=new Vector2(300,0)};split.AddChild(left);
        left.AddChild(MoonGlassTheme.Label("THƯ VIỆN MỸ THUẬT",20,MoonGlassTheme.Gold));
        left.AddChild(MoonGlassTheme.Label("16–20 frame/hướng · render60FPS",12));
        _category=new OptionButton();foreach(var category in new[]{"Tất cả","CLASS","MOB","BOSS","NPC","VFX"})_category.AddItem(category);_category.Select(1);left.AddChild(_category);
        _search=new LineEdit{PlaceholderText="Tên hoặc ID..."};left.AddChild(_search);
        _list=new ItemList{SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(300,450)};left.AddChild(_list);
        var reload=MoonGlassTheme.Button("F5 · Tải lại catalogue");left.AddChild(reload);reload.Pressed+=Reload;
        var right=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};split.AddChild(right);
        _title=MoonGlassTheme.Label("",21,MoonGlassTheme.Gold);right.AddChild(_title);
        _status=MoonGlassTheme.Label("",12,MoonGlassTheme.Muted);_status.CustomMinimumSize=new Vector2(860,50);_status.AutowrapMode=TextServer.AutowrapMode.WordSmart;right.AddChild(_status);
        _clips=new OptionButton();right.AddChild(_clips);
        _stage=new Control{SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new Vector2(860,440)};right.AddChild(_stage);
        for(int i=0;i<8;i++)
        {
            _sprites[i]=new ActorLibrarySprite{Library=_library,Facing=i,DisplayHeight=88};_stage.AddChild(_sprites[i]);
            _labels[i]=MoonGlassTheme.Label("",13);_labels[i].Size=new Vector2(190,26);_labels[i].HorizontalAlignment=HorizontalAlignment.Center;_stage.AddChild(_labels[i]);
        }
        var bar=new HBoxContainer();right.AddChild(bar);_play=MoonGlassTheme.Button("Tạm dừng",120);bar.AddChild(_play);
        var previous=MoonGlassTheme.Button("← Khung",105);bar.AddChild(previous);var next=MoonGlassTheme.Button("Khung →",105);bar.AddChild(next);
        _frame=MoonGlassTheme.Label("",13);bar.AddChild(_frame);
        _timeline=new HSlider{MinValue=0,MaxValue=15,Step=1,CustomMinimumSize=new Vector2(0,32)};right.AddChild(_timeline);
        right.AddChild(MoonGlassTheme.Label("Công cụ kiểm art · không HTTP, sát thương hoặc cấp thưởng. Ô thiếu giữ nguyên trạng thái thiếu.",11,MoonGlassTheme.Muted));
        _category.ItemSelected+=_=>Filter();_search.TextChanged+=_=>Filter();_list.ItemSelected+=i=>SelectActor(_filtered[(int)i].Id);
        _clips.ItemSelected+=i=>SelectClip(_clips.GetItemText((int)i));
        _play.Pressed+=()=>Pause(!_paused);previous.Pressed+=()=>Step(-1);next.Pressed+=()=>Step(1);
        _timeline.ValueChanged+=v=>{if(!_sync){Pause(true);foreach(var sprite in _sprites)sprite.Seek((int)v);}};
        _stage.Resized+=Place;Filter();Place();
        var args=OS.GetCmdlineUserArgs();int actor=Array.IndexOf(args,"--actor");if(actor>=0&&actor+1<args.Length&&_library.Actors.ContainsKey(args[actor+1]))
        {string id=args[actor+1],kind=_library.Actors[id].Kind;for(int i=0;i<_category.ItemCount;i++)if(_category.GetItemText(i)==kind)_category.Select(i);Filter();int index=_filtered.FindIndex(a=>a.Id==id);if(index>=0)_list.Select(index);SelectActor(id);}
        int clip=Array.IndexOf(args,"--clip");if(clip>=0&&clip+1<args.Length)SelectClip(args[clip+1]);
        if(args.Contains("--library-self-test"))SelfTest();
        _offlineMovie=!string.IsNullOrEmpty(Engine.GetWriteMoviePath());
        int shotFrame=Array.IndexOf(args,"--library-frame");if(shotFrame>=0&&shotFrame+1<args.Length&&int.TryParse(args[shotFrame+1],out int requestedFrame))_captureFrame=Math.Clamp(requestedFrame,0,_activeFrames-1);
        int capture=Array.IndexOf(args,"--library-capture");if(capture>=0&&capture+1<args.Length)Capture(args[capture+1]);
        int benchmark=Array.IndexOf(args,"--library-benchmark");if(benchmark>=0&&_offlineMovie)throw new InvalidOperationException("Offline movie cannot be used as a real-time FPS benchmark.");if(benchmark>=0&&benchmark+1<args.Length){_benchmarkPath=args[benchmark+1];_benchmarkStart=Godot.Time.GetTicksUsec();_lastTick=_benchmarkStart;}
    }
    private void Filter()
    {
        _filtered.Clear();_list.Clear();string kind=_category.Selected==0?"":_category.GetItemText(_category.Selected);
        foreach(var actor in _library.Actors.Values.Where(a=>(kind.Length==0||a.Kind==kind)&&(a.Name.Contains(_search.Text,StringComparison.OrdinalIgnoreCase)||a.Id.Contains(_search.Text,StringComparison.OrdinalIgnoreCase))).OrderBy(a=>a.Kind).ThenBy(a=>a.Id,StringComparer.Ordinal))
        {_filtered.Add(actor);int available=actor.Clips.Count(c=>Enumerable.Range(0,8).All(d=>_library.Resolve(actor.Id,c,d,out _)));int row=_list.AddItem($"[{available}/{actor.Clips.Length}] {actor.Name}");_list.SetItemTooltip(row,"Số clip đủ hướng xem; không phải chứng nhận hoàn thiện actor. "+actor.Id);}
        if(_filtered.Count>0){_list.Select(0);SelectActor(_filtered[0].Id);}
    }
    private void SelectActor(string id)
    {
        _actor=id;var actor=_library.Actors[id];_title.Text=actor.Name+" · "+id;_clips.Clear();
        foreach(var clip in actor.Clips)_clips.AddItem(clip);
        SelectClip(actor.Clips[0]);
    }
    private void SelectClip(string clip)
    {
        _clip=clip;int selected=Enumerable.Range(0,_clips.ItemCount).FirstOrDefault(i=>_clips.GetItemText(i)==clip);if(_clips.ItemCount>0)_clips.Select(selected);
        foreach(var sprite in _sprites){sprite.ActorId=_actor;sprite.Clip=clip;sprite.Library=_library;sprite.Loop=true;sprite.Restart();sprite.ManualFrame=_paused?0:-1;}
        var actor=_library.Actors[_actor];
        _activeFrames=Enumerable.Range(0,8).Select(i=>_library.Resolve(_actor,clip,i,out var d)?d!.Frames.Length:0).DefaultIfEmpty(16).Max();if(_activeFrames==0)_activeFrames=16;_timeline.MaxValue=_activeFrames-1;
        for(int i=0;i<8;i++){bool available=_library.Resolve(_actor,clip,i,out var direction);_labels[i].Text=actor.Kind=="VFX"?(i==0?"VFX ·"+_activeFrames+"frame":""):(new[]{"N","NE","E","SE","S","SW","W","NW"}[i]+(available?(direction!.Flip?" · lật ảnh":" · nguồn"):" · CHƯA CÓ"));_sprites[i].DisplayHeight=actor.Kind=="BOSS"?130:actor.Kind=="VFX"?160:88;}
        if(actor.Kind=="VFX")for(int i=1;i<8;i++)_sprites[i].ActorId="";
        int ready=actor.Clips.Count(c=>Enumerable.Range(0,8).All(d=>_library.Resolve(_actor,c,d,out _)));
        var reviews=_library.ReviewStatus(_actor,clip).Split('\n');
        int sourceCount=reviews[0]=="CHƯA CÓ DỮ LIỆU"?0:reviews.Length;
        int holds=reviews.Count(r=>r.Contains(": HOLD",StringComparison.Ordinal));
        _status.Text=$"Clip có dữ liệu đủ hướng: {ready}/{actor.Clips.Length} · {_clip} · Phát lặp để kiểm tra, kể cả clip một lần.\n"+
            $"{sourceCount} nguồn · {holds} HOLD cần kiểm/sửa · Đủ nguồn không có nghĩa đã duyệt hình ảnh. Chi tiết từng nguồn trong Studio.";
        Place();
    }
    private void Place()
    {if(_stage==null)return;for(int i=0;i<8;i++){float x=(_stage.Size.X/4)*(i%4+.5f),y=(_stage.Size.Y/2)*(i/4+.65f);if(_library.Actors.TryGetValue(_actor,out var actor)&&actor.Kind=="VFX"){x=_stage.Size.X/2;y=_stage.Size.Y/2+70;}_sprites[i].Position=new Vector2(x,y);_labels[i].Position=new Vector2(x-95,y+14+(_actor=="MOB_CARPLING"?_sprites[i].DisplayHeight*.6f:0));}}
    private void Pause(bool paused){_paused=paused;_play.Text=paused?"Phát animation":"Tạm dừng";foreach(var sprite in _sprites){sprite.Paused=paused;sprite.ManualFrame=paused?sprite.DisplayedFrame:-1;}}
    private void Step(int delta){Pause(true);int current=_sprites.FirstOrDefault(s=>s.Available)?.DisplayedFrame??0;int frame=(current+delta+_activeFrames)%_activeFrames;foreach(var sprite in _sprites)sprite.Seek(frame);}
    private void Reload(){var old=_library;_library=new ActorLibraryData(reviewMode:true);Filter();old.Dispose();}
    public override void _Process(double delta)
    {
        if(_benchmarkPath!=null)
        {
            ulong now=Godot.Time.GetTicksUsec();double elapsed=(now-_benchmarkStart)/1_000_000d;
            if(elapsed>2)_samples.Add((now-_lastTick)/1000d);_lastTick=now;
            if(elapsed>=14)
            {
                var sorted=_samples.OrderBy(v=>v).ToArray();
                var report=new{scene="ActorLibrary",actor=_actor,clip=_clip,viewport=GetViewportRect().Size.ToString(),gpu=RenderingServer.GetVideoAdapterName(),display=DisplayServer.GetName(),targetFps=60,warmupSeconds=2,measurementSeconds=elapsed-2,samples=sorted.Length,medianMs=sorted[sorted.Length/2],p95Ms=sorted[Math.Min(sorted.Length-1,(int)(sorted.Length*.95))],meanFps=1000/_samples.Average(),note="Eight-direction art review scene only; not gameplay/combat/load acceptance."};
                using var file=FileAccess.Open(_benchmarkPath,FileAccess.ModeFlags.Write);file.StoreString(JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true})+"\n");GD.Print("ACTOR_LIBRARY_BENCHMARK "+JsonSerializer.Serialize(report));_benchmarkPath=null;GetTree().Quit();
            }
        }
        _refresh+=delta;if(_refresh<.1)return;_refresh=0;var sprite=_sprites.FirstOrDefault(s=>s.Available);
        if(sprite==null){_frame.Text="CHƯA CÓ SPRITE CHO CLIP NÀY";return;}_sync=true;_timeline.Value=sprite.DisplayedFrame;_sync=false;_frame.Text=$"Frame {sprite.DisplayedFrame+1}/{_activeFrames} · "+(_staticCapture?"Ảnh tĩnh · không đo FPS":_offlineMovie?"Video offline · không đo FPS":$"{Engine.GetFramesPerSecond()}FPS · {_library.CachedTextures}/8 texture cache");
    }
    public override void _UnhandledKeyInput(InputEvent ev)
    {if(ev is not InputEventKey key||!key.Pressed||key.Echo)return;if(key.Keycode==Key.Escape)GetTree().Quit();if(key.Keycode==Key.F5)Reload();if(key.Keycode==Key.Space)Pause(!_paused);}
    private async void Capture(string path)
    {_staticCapture=true;Pause(true);foreach(var sprite in _sprites)sprite.ManualFrame=_captureFrame;for(int i=0;i<5;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);var result=GetViewport().GetTexture().GetImage().SavePng(path);GD.Print("ACTOR_LIBRARY_CAPTURE "+result+" STATIC_FRAME_"+_captureFrame+"_NOT_GAMEPLAY");GetTree().Quit(result==Error.Ok?0:1);}
    private void SelfTest()
    {
        int checks=0;
        try
        {
            foreach(var page in _library.Pages.Values)foreach(var direction in page.Directions)
            {if(direction.Frames.Length<16||direction.Frames.Length>20)throw new Exception(page.Id);foreach(var frame in direction.Frames){if(frame.Region.Size.X<=0||frame.Region.Size.Y<=0||!FileAccess.FileExists(frame.File))throw new Exception(frame.File);var texture=_library.Texture(frame.File);if(texture==null||texture.GetWidth()+.1f<frame.Region.End.X||texture.GetHeight()+.1f<frame.Region.End.Y)throw new Exception("invalid texture/region "+frame.File);checks++;}}
            if(_library.Resolve("MISSING_ACTOR","idle",0,out _)||_library.Resolve("CLASS_MINH_KIEM","MISSING_CLIP",0,out _))throw new Exception("unexpected fallback");checks+=2;
            using(var live=new ActorLibraryData())foreach(var actor in live.Actors.Values)foreach(var clip in actor.Clips)foreach(int facing in Enumerable.Range(0,8))
            {if(live.Resolve(actor.Id,clip,facing,out var resolved)&&!live.Pages.Values.Any(p=>p.Approved&&p.Directions.Any(d=>ReferenceEquals(d.Frames,resolved!.Frames))))throw new Exception("unapproved new art escaped production gate");checks++;}
            foreach(var actor in _library.Actors.Values.Where(a=>!a.Mirror))foreach(var clip in actor.Clips)foreach(int facing in Enumerable.Range(5,3))
            {if(_library.Resolve(actor.Id,clip,facing,out var direction)&&direction!.Flip)throw new Exception("asymmetric actor incorrectly mirrored");checks++;}
            var probe=_sprites[0];probe.ActorId="CLASS_MINH_KIEM";probe.Clip="walk";probe.Facing=4;probe.ManualFrame=-1;probe.Paused=false;probe.Loop=false;probe.Restart();
            probe._Process(ActorLibraryData.Duration("walk")*2);if(probe.DisplayedFrame!=15)throw new Exception("one-shot did not hold final pose");checks++;
            probe.Seek(7);probe.ManualFrame=-1;probe._Process(0);if(probe.DisplayedFrame!=7)throw new Exception("scrub resume lost phase");checks++;
            probe.Loop=true;probe.Restart();var visited=new HashSet<int>();for(int i=0;i<60;i++){probe._Process(1d/60);visited.Add(probe.DisplayedFrame);}if(visited.Count!=16)throw new Exception("60FPS clock skipped source poses");checks++;
            foreach(string action in new[]{"telegraph_01","attack_01","recovery_01","hurt","death"})
            foreach(int facing in Enumerable.Range(0,8))
            {
                if(!_library.Resolve("MOB_CARPLING",action,facing,out var authored)||authored!.Frames.Length!=16)throw new Exception("missing Carpling combat direction: "+action+"/"+facing);checks++;
                probe.ActorId="MOB_CARPLING";probe.Clip=action;probe.Facing=facing;probe.ManualFrame=-1;probe.Restart();
                double duration=ActorLibraryData.Duration(probe.ActorId,action);var poses=new HashSet<int>();
                for(int i=0;i<Math.Ceiling(duration*60)+2;i++){probe._Process(1d/60);poses.Add(probe.DisplayedFrame);}
                if(poses.Count!=16)throw new Exception("Carpling review clock skipped source poses: "+action);checks++;
                probe.Loop=false;probe.Restart();probe._Process(duration*2);if(probe.DisplayedFrame!=15)throw new Exception("Carpling one-shot restarted: "+action);checks++;probe.Loop=true;
            }
            if(ActorLibraryData.Duration("MOB_CARPLING","telegraph_01")!=.45||ActorLibraryData.Duration("MOB_CARPLING","recovery_01")!=.5||ActorLibraryData.Duration("MOB_WATERROOT","telegraph_01")!=ActorLibraryData.Duration("telegraph_01"))throw new Exception("presentation timing leaked between actors");checks++;
            GD.Print("ACTOR_LIBRARY_SELF_TEST PASS assertions="+checks+" partial catalogue allowed; not complete art acceptance");GetTree().Quit();
        }
        catch(Exception e){GD.PushError("ACTOR_LIBRARY_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
    public override void _ExitTree()=>_library?.Dispose();
}
