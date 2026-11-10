using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Visual authoring workbench. Does not change gameplay equipment slots or stats.</summary>
public partial class PaperDollLab : Control
{
    private PaperDollLabData _data=null!;
    private ModularCharacterRenderer _avatar=null!,_base=null!;
    private PaperDollGuides _guides=null!;
    private Control _stage=null!;
    private OptionButton _gender=null!,_hair=null!,_eyes=null!,_outfit=null!,_boots=null!,_weapon=null!,_hat=null!,_cape=null!,_target=null!,_zoom=null!,_coords=null!,_attach=null!;
    private Label _status=null!,_frame=null!,_source=null!,_layerOrder=null!;
    private SpinBox _x=null!,_y=null!,_pivotX=null!,_pivotY=null!,_angle=null!,_scale=null!;
    private HSlider _timeline=null!;
    private CheckButton _all=null!,_showGuides=null!,_flipH=null!,_flipV=null!,_visible=null!;
    private Button _play=null!,_front=null!,_back=null!,_undo=null!,_redo=null!;
    private bool _sync,_paused=true,_captureMode,_captureTools,_drag;
    private int _captureFrame;
    private TabContainer _tabs=null!;
    private long _revision;
    private double _refresh;
    private string _body="MK_M",_dragBefore="";
    private Vector2 _dragStart;
    private Pixel _dragValue;
    private readonly Stack<string> _undos=new(),_redos=new();
    private readonly Dictionary<string,string[]> _options=new(StringComparer.Ordinal);
    private readonly string[] _anchorNames={"canvas","ground","head","face","chest","hip","hand_near"};
    private string? _benchmarkPath;
    private ulong _benchmarkStart,_lastTick;
    private readonly List<double> _samples=new();
    private string DraftPath=>_data.Registered?"user://paperdoll_lab/fit_registered_master_v1.json":"user://paperdoll_lab/fit_legacy_v2.json";
    public override void _Ready(){try{Build();}catch(Exception e){GD.PushError("PAPERDOLL_LAB_INIT_FAIL "+e);GetTree().Quit(1);}}
    private void Build()
    {
        Engine.MaxFps=60;Theme=MoonGlassTheme.Create();_data=new PaperDollLabData(!OS.GetCmdlineUserArgs().Contains("--paperdoll-legacy"));
        var bg=new ColorRect{Color=Color.FromHtml("#20243b"),MouseFilter=MouseFilterEnum.Ignore};bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);AddChild(bg);
        var margin=new MarginContainer();margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach(string edge in new[]{"left","right","top","bottom"})margin.AddThemeConstantOverride("margin_"+edge,16);
        AddChild(margin);var root=new VBoxContainer();root.AddThemeConstantOverride("separation",9);margin.AddChild(root);
        root.AddChild(MoonGlassTheme.Label("NGŨ MẠCH HUYỀN ẤN  /  PAPER-DOLL STUDIO",22));
        root.AddChild(MoonGlassTheme.Label("MASTER CHUNG · Tỉ lệ 4,5 đầu · Trang phục theo cùng khớp cơ thể · Trang bị gameplay giữ nguyên",12,MoonGlassTheme.Blue));
        var row=new HBoxContainer{SizeFlagsVertical=SizeFlags.ExpandFill};row.AddThemeConstantOverride("separation",12);root.AddChild(row);
        VBoxContainer Panel(int width,string title)
        {
            var card=MoonGlassTheme.Card();card.CustomMinimumSize=new(width,0);card.SizeFlagsHorizontal=SizeFlags.Fill;row.AddChild(card);
            var scroll=new ScrollContainer{HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled};card.AddChild(scroll);
            var content=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};content.AddThemeConstantOverride("separation",7);scroll.AddChild(content);
            content.AddChild(MoonGlassTheme.Label(title,16,MoonGlassTheme.Gold));return content;
        }
        var left=Panel(235,"01  DIỆN MẠO");
        _gender=Choice(left,"Base",new[]{"Nam","Nữ"});_gender.ItemSelected+=i=>{_body=i==0?"MK_M":"MK_F";Rebuild();};
        _hair=PartChoice(left,"Tóc","HAIR");_eyes=PartChoice(left,"Mắt","EYES");
        _outfit=Choice(left,"Bộ áo + quần",new[]{"Coverage nền","Bộ giao lĩnh ngà / ngọc","Bộ giao lĩnh chàm / bạc"});_outfit.Select(1);_outfit.ItemSelected+=_=>Rebuild();
        _boots=PartChoice(left,"Giày · độc lập bộ áo/quần","BOOTS");_boots.Select(1);
        _weapon=PartChoice(left,"Kiếm chéo / hướng lưỡi","WEAPON");
        _hat=PartChoice(left,"Nón / trán quan · giữ tóc","HAT");_cape=PartChoice(left,"Áo choàng","CAPE");
        _hair.Select(1);_eyes.Select(1);_weapon.Select(Array.IndexOf(_options["WEAPON"],"JIAN_STEEL_RIGHT")+1);
        left.AddChild(MoonGlassTheme.Label("Một bộ ngoại hình thay cả áo/quần. Item, slot trang bị và chỉ số chiến đấu không đổi.",12,MoonGlassTheme.Muted));
        var center=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};row.AddChild(center);
        var header=new HBoxContainer();center.AddChild(header);header.AddChild(MoonGlassTheme.Label("02  KÉO THẢ & SO SÁNH",16,MoonGlassTheme.Gold));
        _zoom=new OptionButton();foreach(int z in new[]{2,4,6})_zoom.AddItem(z+"×");_zoom.Select(1);header.AddChild(_zoom);_zoom.ItemSelected+=_=>Place();
        _stage=new Control{SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new(510,210),ClipContents=true};center.AddChild(_stage);
        var field=new ColorRect{Color=Color.FromHtml("#c2d5cf"),MouseFilter=MouseFilterEnum.Ignore};field.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);_stage.AddChild(field);
        _base=new ModularCharacterRenderer{PlaybackPaused=true,ReviewTextureResolver=RegisteredPaperDollMaster.Texture};_stage.AddChild(_base);
        _avatar=new ModularCharacterRenderer{PlaybackPaused=true,ReviewTextureResolver=RegisteredPaperDollMaster.Texture};_stage.AddChild(_avatar);
        _guides=new PaperDollGuides();_stage.AddChild(_guides);_stage.GuiInput+=StageInput;
        var captions=new HBoxContainer();center.AddChild(captions);
        foreach(string name in new[]{"BASE NỀN","BỘ NGOẠI HÌNH"}){var l=MoonGlassTheme.Label(name,12);l.HorizontalAlignment=HorizontalAlignment.Center;captions.AddChild(l);}
        _showGuides=new CheckButton{Text="Điểm neo, pivot & biên lớp",ButtonPressed=true};center.AddChild(_showGuides);_showGuides.Toggled+=v=>{_guides.Visible=v;UpdateGuides();};
        center.AddChild(MoonGlassTheme.Label("Kéo: di chuyển · Ctrl+bấm: chọn lớp · Alt+bấm: đặt pivot · Ctrl+Z/Y: hoàn tác",11,MoonGlassTheme.Muted));
        var directions=new HBoxContainer();center.AddChild(directions);
        foreach(string d in Directions){var b=MoonGlassTheme.Button(d,42);b.Disabled=d!="S";b.TooltipText=d=="S"?"Nguồn S/idle":"Chưa có source hướng "+d;directions.AddChild(b);}
        var playback=new HBoxContainer();center.AddChild(playback);
        _play=MoonGlassTheme.Button("Phát",85);playback.AddChild(_play);_play.Pressed+=()=>Pause(!_paused);
        foreach(int delta in new[]{-1,1}){int step=delta;var b=MoonGlassTheme.Button(delta<0?"←":"→",44);playback.AddChild(b);b.Pressed+=()=>Seek((_avatar.Animation.FrameIndex+step+16)%16);}
        _frame=MoonGlassTheme.Label("",12);playback.AddChild(_frame);
        _timeline=new HSlider{MinValue=0,MaxValue=15,Step=1,CustomMinimumSize=new(0,26)};center.AddChild(_timeline);_timeline.ValueChanged+=v=>{if(!_sync)Seek((int)v);};
        var right=Panel(300,"03  INSPECTOR");
        _target=new OptionButton();right.AddChild(_target);_target.ItemSelected+=_=>SyncInspector();
        _source=MoonGlassTheme.Label("",11,MoonGlassTheme.Muted);right.AddChild(_source);
        _all=new CheckButton{Text="Áp cho cả 16 placement"};right.AddChild(_all);
        var tabs=_tabs=new TabContainer{SizeFlagsVertical=SizeFlags.ExpandFill,CustomMinimumSize=new(0,370)};right.AddChild(tabs);
        VBoxContainer Tab(string name){var s=new ScrollContainer{Name=name,HorizontalScrollMode=ScrollContainer.ScrollMode.Disabled};tabs.AddChild(s);var v=new VBoxContainer{SizeFlagsHorizontal=SizeFlags.ExpandFill};v.AddThemeConstantOverride("separation",5);s.AddChild(v);return v;}
        var position=Tab("Vị trí");
        _coords=Choice(position,"Hệ tọa độ X/Y",new[]{"Offset theo neo","Canvas master 96×96","Màn hình / viewport"});_coords.ItemSelected+=_=>SyncInspector();
        _attach=Choice(position,"Gắn vào điểm neo",_anchorNames);_attach.ItemSelected+=i=>{if(!_sync&&PartTarget(out var id))Mutate(()=>_data.SetAttachment(_body,id,Frame,(string)_anchorNames[(int)i],_all.ButtonPressed));};
        _x=Number(position,"X",-4096,4096,1);_y=Number(position,"Y",-4096,4096,1);_x.ValueChanged+=_=>EditPosition();_y.ValueChanged+=_=>EditPosition();
        _pivotX=Number(position,"Pivot X · pixel nguồn",-1536,1536,1);_pivotY=Number(position,"Pivot Y · pixel nguồn",-1536,1536,1);
        _pivotX.ValueChanged+=_=>EditPivot();_pivotY.ValueChanged+=_=>EditPivot();
        var snap=MoonGlassTheme.Button("Đưa pivot về điểm neo");position.AddChild(snap);snap.Pressed+=()=>{if(PartTarget(out var id))Mutate(()=>_data.SetOffset(_body,id,Frame,new Pixel(0,0),_all.ButtonPressed));};
        var paint=Tab("Góc & lớp");
        _angle=Number(paint,"Góc thêm quanh pivot · độ",-180,180,1);_scale=Number(paint,"Tỷ lệ lớp · thử fit",.25,2,.05);
        _angle.ValueChanged+=_=>EditTransform();_scale.ValueChanged+=_=>EditTransform();
        _flipH=new CheckButton{Text="Lật ngang"};_flipV=new CheckButton{Text="Lật dọc"};_visible=new CheckButton{Text="Hiện lớp",ButtonPressed=true};
        foreach(var b in new[]{_flipH,_flipV,_visible})paint.AddChild(b);
        _flipH.Toggled+=_=>EditTransform();_flipV.Toggled+=_=>EditTransform();
        _visible.Toggled+=v=>{if(!_sync&&PartTarget(out var id))Mutate(()=>_data.SetHidden(_body,id,Frame,!v,_all.ButtonPressed));};
        var layerButtons=new HBoxContainer();paint.AddChild(layerButtons);
        _front=MoonGlassTheme.Button("Lên trước");_back=MoonGlassTheme.Button("Ra sau");layerButtons.AddChild(_front);layerButtons.AddChild(_back);
        _front.Pressed+=()=>MoveLayer(1);_back.Pressed+=()=>MoveLayer(-1);
        _layerOrder=MoonGlassTheme.Label("",11,MoonGlassTheme.Muted);paint.AddChild(_layerOrder);
        var drafts=Tab("Bản nháp");
        var history=new HBoxContainer();drafts.AddChild(history);_undo=MoonGlassTheme.Button("Hoàn tác");_redo=MoonGlassTheme.Button("Làm lại");history.AddChild(_undo);history.AddChild(_redo);
        _undo.Pressed+=()=>History(false);_redo.Pressed+=()=>History(true);
        foreach(var pair in new[]{("Lưu fit draft",(Action)Save),("Mở fit draft",(Action)Load),("Xuất master gốc .aseprite",(Action)ExportSource),("Chép pose trước",(Action)CopyPrevious),("Khôi phục gốc",(Action)(()=>Mutate(_data.Reset)))})
        {var b=MoonGlassTheme.Button(pair.Item1);drafts.AddChild(b);b.Pressed+=pair.Item2;}
        drafts.AddChild(MoonGlassTheme.Label("Draft v2 lưu offset, attachment, pivot, góc, tỷ lệ, lật, ẩn lớp và thứ tự vẽ theo pose. Draft v1 cũ được giữ riêng.",12,MoonGlassTheme.Muted));
        _status=MoonGlassTheme.Label("",12,MoonGlassTheme.Gold);root.AddChild(_status);
        root.AddChild(MoonGlassTheme.Label("MASTER KỸ THUẬT · S/idle · 16 pose dùng chung cơ thể / trang phục · chưa nghiệm thu art hoặc thay hero gameplay",11,MoonGlassTheme.Muted));
        _stage.Resized+=Place;if(!Rebuild())throw new Exception("invalid initial appearance");Place();
        var args=OS.GetCmdlineUserArgs();
        if(args.Contains("--paperdoll-female")){_gender.Select(1);_body="MK_F";Rebuild();}
        if(args.Contains("--paperdoll-indigo")){_outfit.Select(2);_hair.Select(2);_cape.Select(2);Rebuild();}
        if(args.Contains("--paperdoll-hat")){_hat.Select(2);Rebuild();}
        int pose=Array.IndexOf(args,"--paperdoll-pose");if(pose>=0&&pose+1<args.Length&&int.TryParse(args[pose+1],out var f))_captureFrame=Math.Clamp(f,0,15);
        if(args.Contains("--paperdoll-capture-tools")){_captureTools=true;SelectSlot("weapon_near");_tabs.CurrentTab=1;}
        int benchmark=Array.IndexOf(args,"--paperdoll-benchmark");if(benchmark>=0&&benchmark+1<args.Length){_benchmarkPath=args[benchmark+1];_benchmarkStart=_lastTick=Godot.Time.GetTicksUsec();Pause(false);}
        int export=Array.IndexOf(args,"--paperdoll-export-master");if(export>=0&&export+1<args.Length){if(!_data.Registered)throw new Exception("legacy PNG source cannot export a registered master");RegisteredPaperDollMaster.ExportSources(args[export+1]);GD.Print("REGISTERED_MASTER_EXPORTED source layers; not approved art");GetTree().Quit();return;}
        if(args.Contains("--paperdoll-self-test"))SelfTest();
        int capture=Array.IndexOf(args,"--paperdoll-capture");if(capture>=0&&capture+1<args.Length)Capture(args[capture+1]);
    }
    private int Frame=>_avatar.Animation.FrameIndex;
    private OptionButton Choice(VBoxContainer box,string label,string[] names)
    {box.AddChild(MoonGlassTheme.Label(label,12,MoonGlassTheme.Muted));var b=new OptionButton{CustomMinimumSize=new(0,31)};foreach(string n in names)b.AddItem(n);box.AddChild(b);return b;}
    private OptionButton PartChoice(VBoxContainer box,string label,string category)
    {var p=_data.Data.Parts.Where(p=>p.Category==category).ToArray();_options[category]=p.Select(p=>p.Id).ToArray();var b=Choice(box,label,new[]{"Không dùng"}.Concat(p.Select(p=>p.Name)).ToArray());b.ItemSelected+=_=>Rebuild();return b;}
    private SpinBox Number(VBoxContainer box,string label,double min,double max,double step)
    {box.AddChild(MoonGlassTheme.Label(label,11,MoonGlassTheme.Muted));var s=new SpinBox{MinValue=min,MaxValue=max,Step=step,CustomMinimumSize=new(0,30)};box.AddChild(s);return s;}
    private List<string> Selected()
    {
        var a=new List<string>();foreach(var pair in new[]{("HAIR",_hair),("EYES",_eyes),("WEAPON",_weapon),("BOOTS",_boots),("HAT",_hat),("CAPE",_cape)})if(pair.Item2.Selected>0)a.Add(_options[pair.Item1][pair.Item2.Selected-1]);
        if(_outfit.Selected>0){a.Add("OUTFIT_"+(_outfit.Selected==1?"IVORY":"INDIGO")+"_"+(_body=="MK_M"?"M":"F"));}return a;
    }
    private string Target=>_target.ItemCount==0?"":_target.GetItemMetadata(_target.Selected).AsString();
    private bool PartTarget(out string id){id=Target.StartsWith("part:",StringComparison.Ordinal)?Target[5..]:"";return id.Length>0;}
    private string? SlotTarget()=>PartTarget(out var id)?_data.FindPart(id).Slot:Target.StartsWith("layer:",StringComparison.Ordinal)?Target[6..]:null;
    private bool Rebuild()
    {
        if(_avatar==null)return false;
        if(!_avatar.TryApplyForReview(_data.Build(_body,Selected(),++_revision),out string reason)){_status.Text="Giữ bản trước: "+reason;return false;}
        if(!_base.TryApplyForReview(_data.Build(_body,Array.Empty<string>(),_revision),out reason))throw new Exception(reason);
        _base.SeekReviewFrame(Frame);string old=Target;_target.Clear();
        void Add(string label,string key){int i=_target.ItemCount;_target.AddItem(label);_target.SetItemMetadata(i,key);}
        foreach(string id in Selected())Add(_data.FindPart(id).Name,"part:"+id);
        Add("Skin · bàn tay trước","layer:hand_near");Add("Skin · cơ thể","layer:body");
        foreach(string n in _anchorNames.Where(n=>n is not "canvas" and not "ground"))Add("Neo · "+n,"anchor:"+n);
        _target.Select(Enumerable.Range(0,_target.ItemCount).FirstOrDefault(i=>_target.GetItemMetadata(i).AsString()==old));
        _status.Text=_data.FindBody(_body).Name+" · bộ hiển thị liền · "+Selected().Count+" phần · không đổi trang bị gameplay";
        SyncInspector();UpdateGuides();return true;
    }
    private void PushUndo(string before){if(before==_data.ExportDraft())return;_undos.Push(before);_redos.Clear();}
    private bool Mutate(Action edit,bool history=true)
    {
        if(_sync)return false;Pause(true);string before=_data.ExportDraft();
        try {edit();if(!Rebuild())throw new Exception("vượt canvas hoặc transform không hợp lệ");if(history)PushUndo(before);SyncInspector();return true;}
        catch(Exception e){if(!_data.TryImportDraft(before,out var error))throw new Exception(error);SyncInspector();_status.Text="Đã giữ bản trước: "+e.Message;return false;}
    }
    private void History(bool redo)
    {
        var source=redo?_redos:_undos;var destination=redo?_undos:_redos;if(source.Count==0)return;
        string before=_data.ExportDraft(),target=source.Peek();if(!_data.TryImportDraft(target,out var reason)){_status.Text=reason;return;}
        if(!Rebuild()){_data.TryImportDraft(before,out _);return;}source.Pop();destination.Push(before);SyncInspector();
    }
    private void EditPosition()
    {
        if(_sync)return;bool part=PartTarget(out string id);if(!part&&!Target.StartsWith("anchor:",StringComparison.Ordinal))return;
        var value=new Vector2((float)_x.Value,(float)_y.Value);
        if(_coords.Selected==2)value=_avatar.ToLocal(value)+new Vector2(48,72);
        var pixel=new Pixel((int)Math.Round(value.X),(int)Math.Round(value.Y));
        Mutate(()=>{
            if(!part){_data.SetAnchor(_body,Target[7..],Frame,pixel,_all.ButtonPressed);return;}
            if(_coords.Selected==0)_data.SetOffset(_body,id,Frame,pixel,_all.ButtonPressed);
            else foreach(int i in _all.ButtonPressed?Enumerable.Range(0,16):new[]{Frame})_data.SetOffset(_body,id,i,pixel-_data.Anchor(_body,_data.Attachment(_body,id,i),i),false);
        });
    }
    private void EditPivot()
    {if(_sync||!PartTarget(out var id))return;int ppu=_data.FindPart(id).SourcePixelsPerUnit;Mutate(()=>_data.SetPivotPreservingPlacement(_body,id,Frame,_pivotX.Value/ppu,_pivotY.Value/ppu,_all.ButtonPressed));}
    private void EditTransform()
    {
        if(_sync||!PartTarget(out var id))return;int ppu=_data.FindPart(id).SourcePixelsPerUnit;
        var t=new PaintTransform(_pivotX.Value/ppu,_pivotY.Value/ppu,_angle.Value,_scale.Value,_flipH.ButtonPressed,_flipV.ButtonPressed);
        Mutate(()=>_data.SetTransform(_body,id,Frame,t,_all.ButtonPressed));
    }
    private void MoveLayer(int delta){var slot=SlotTarget();if(slot!=null)Mutate(()=>_data.MoveLayer(_body,slot,Frame,delta,_all.ButtonPressed));}
    private void SyncInspector()
    {
        if(_x==null||_target.ItemCount==0)return;_sync=true;
        bool part=PartTarget(out var id),anchor=Target.StartsWith("anchor:",StringComparison.Ordinal);
        foreach(var c in new[]{_pivotX,_pivotY,_angle,_scale})c.Editable=part;
        _x.Editable=_y.Editable=part||anchor;_attach.Disabled=!part;
        _flipH.Disabled=_flipV.Disabled=_visible.Disabled=!part;_front.Disabled=_back.Disabled=SlotTarget()==null;
        Pixel v=part?(_coords.Selected==0?_data.Offset(_body,id,Frame):_data.AbsolutePosition(_body,id,Frame)):anchor?_data.Anchor(_body,Target[7..],Frame):new(0,0);
        Vector2 display=new(v.X,v.Y);if(_coords.Selected==2)display=_avatar.GetGlobalTransform()*(display-new Vector2(48,72));
        _x.Value=display.X;_y.Value=display.Y;
        var t=part?_data.Transform(_body,id,Frame):Identity;int ppu=part?_data.FindPart(id).SourcePixelsPerUnit:1;
        _pivotX.Value=t.PivotX*ppu;_pivotY.Value=t.PivotY*ppu;_angle.Value=t.Degrees;_scale.Value=t.Scale;
        _flipH.ButtonPressed=t.FlipH;_flipV.ButtonPressed=t.FlipV;_visible.ButtonPressed=!part||!_data.IsHidden(_body,id,Frame);
        if(part)_attach.Select(Array.IndexOf(_anchorNames,_data.Attachment(_body,id,Frame)));
        _source.Text=part?(_data.Registered?"Cùng master / pose · pivot theo nguồn":"PNG cũ bị giữ để tham khảo"):"Guide / skin pass · theo pose";
        _layerOrder.Text="Sau → trước:\n"+string.Join(" → ",_data.Order(_body,Frame));
        _undo.Disabled=_undos.Count==0;_redo.Disabled=_redos.Count==0;_sync=false;
        UpdateGuides();
    }
    private Vector2 ActorMouse(Vector2 stagePosition)=>_avatar.ToLocal(_stage.GetGlobalTransform()*stagePosition);
    private void SelectSlot(string slot)
    {int i=Enumerable.Range(0,_target.ItemCount).FirstOrDefault(i=>{string k=_target.GetItemMetadata(i).AsString();return k.StartsWith("part:",StringComparison.Ordinal)&&_data.FindPart(k[5..]).Slot==slot;});_target.Select(i);SyncInspector();}
    private void StageInput(InputEvent ev)
    {
        if(ev is InputEventMouseButton button&&button.ButtonIndex==MouseButton.Left)
        {
            if(!button.Pressed){if(_drag){_drag=false;PushUndo(_dragBefore);SyncInspector();}return;}
            Pause(true);var mouse=ActorMouse(button.Position);
            if(button.CtrlPressed)
            {
                foreach(var c in _avatar.Animation.Commands.Reverse())
                {if(!Selected().Any(id=>_data.FindPart(id).Slot==c.PartId))continue;var p=FromActor(c,mouse.X,mouse.Y);if(p.X>=0&&p.Y>=0&&p.X<(double)c.Region.Width/c.SourcePixelsPerUnit&&p.Y<(double)c.Region.Height/c.SourcePixelsPerUnit){SelectSlot(c.PartId);break;}}
                return;
            }
            if(button.AltPressed&&PartTarget(out var id))
            {
                var c=_avatar.Animation.Commands.FirstOrDefault(c=>c.PartId==_data.FindPart(id).Slot);if(c.Texture==null)return;
                var p=FromActor(c,mouse.X,mouse.Y);var def=_data.FindPart(id);int ppu=def.SourcePixelsPerUnit;var sourceRegion=_data.Region(id,Frame);
                p=new Point(p.X+(double)(c.Region.X-sourceRegion[0])/ppu,p.Y+(double)(c.Region.Y-sourceRegion[1])/ppu);var t=_data.Transform(_body,id,Frame);
                Mutate(()=>_data.SetPivotPreservingPlacement(_body,id,Frame,Math.Round(p.X*ppu)/ppu,Math.Round(p.Y*ppu)/ppu,_all.ButtonPressed));return;
            }
            if(PartTarget(out id)||Target.StartsWith("anchor:",StringComparison.Ordinal))
            {_drag=true;_dragBefore=_data.ExportDraft();_dragStart=mouse;_dragValue=PartTarget(out id)?_data.Offset(_body,id,Frame):_data.Anchor(_body,Target[7..],Frame);}
        }
        if(ev is InputEventMouseMotion motion&&_drag)
        {
            var delta=ActorMouse(motion.Position)-_dragStart;var value=_dragValue+new Pixel((int)Math.Round(delta.X),(int)Math.Round(delta.Y));
            if(PartTarget(out var id))Mutate(()=>_data.SetOffset(_body,id,Frame,value,_all.ButtonPressed),false);
            else Mutate(()=>_data.SetAnchor(_body,Target[7..],Frame,value,_all.ButtonPressed),false);
        }
    }
    private void Place()
    {
        if(_stage==null||_avatar==null)return;int z=new[]{2,4,6}[_zoom.Selected];_avatar.Scale=_base.Scale=new(z,z);
        var body=_data.FindBody(_body);float height=(float)body.Frames[0].Region[3]/body.SourcePixelsPerUnit;
        float ground=_stage.Size.Y/2+Math.Min(_stage.Size.Y/2-8,height*z/2);_base.Position=new(_stage.Size.X*.25f,ground);_avatar.Position=new(_stage.Size.X*.75f,ground);UpdateGuides();
    }
    private void UpdateGuides()
    {
        if(_guides==null||_avatar.Animation.Current==null)return;
        _guides.Origin=_avatar.Position;_guides.BaseOrigin=_base.Position;_guides.Zoom=_avatar.Scale.X;
        _guides.Anchors=_data.FindBody(_body).Frames[Frame].Anchors.Where(a=>a.Key!="canvas").ToDictionary(a=>a.Key,a=>_data.Anchor(_body,a.Key,Frame));
        _guides.Selected=null;var slot=SlotTarget();if(slot!=null)foreach(var c in _avatar.Animation.Commands)if(c.PartId==slot)_guides.Selected=c;
        _guides.QueueRedraw();
    }
    private void Pause(bool p){_paused=p;_avatar.PlaybackPaused=p;_play.Text=p?"Phát":"Tạm dừng";}
    private void Seek(int f){Pause(true);_avatar.SeekReviewFrame(f);_base.SeekReviewFrame(f);SyncInspector();UpdateGuides();}
    private void CopyPrevious()
    {
        if(!PartTarget(out var id))return;int previous=(Frame+15)%16;
        var offset=_data.Offset(_body,id,previous);var transform=_data.Transform(_body,id,previous);var attachment=_data.Attachment(_body,id,previous);bool hidden=_data.IsHidden(_body,id,previous);
        Mutate(()=>{_data.SetAttachment(_body,id,Frame,attachment,false);_data.SetOffset(_body,id,Frame,offset,false);_data.SetTransform(_body,id,Frame,transform,false);_data.SetHidden(_body,id,Frame,hidden,false);});
    }
    private void ExportSource()
    {if(!_data.Registered){_status.Text="Chỉ xuất nguồn master đăng ký.";return;}string folder=ProjectSettings.GlobalizePath("user://paperdoll_lab/registered_sources/"+RegisteredPaperDollMaster.Fingerprint[..12]);RegisteredPaperDollMaster.ExportSources(folder);_status.Text="Đã xuất master gốc .aseprite; fit draft lưu riêng: "+folder;}
    private void Save()
    {DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath("user://paperdoll_lab"));using var f=FileAccess.Open(DraftPath,FileAccess.ModeFlags.Write);if(f==null){_status.Text="Không lưu được draft";return;}f.StoreString(_data.ExportDraft());_status.Text="Đã lưu draft v2 · ngoại hình thử · không đổi trang bị.";}
    private void Load()
    {
        if(!FileAccess.FileExists(DraftPath)){_status.Text="Chưa có draft v2; draft cũ không bị ghi đè.";return;}
        string before=_data.ExportDraft();if(!_data.TryImportDraft(FileAccess.GetFileAsString(DraftPath),out var reason)){_status.Text="Từ chối: "+reason;return;}
        if(!Rebuild()){_data.TryImportDraft(before,out _);return;}PushUndo(before);SyncInspector();
    }
    public override void _Process(double delta)
    {
        if(_avatar==null||_avatar.Animation.Current==null)return;MeasurePreview();_base.SeekReviewFrame(Frame);
        _refresh+=delta;if(_refresh<.05)return;_refresh=0;_sync=true;_timeline.Value=Frame;_sync=false;
        _frame.Text=$"Pose {Frame+1:00}/16 · "+(_captureMode?"ảnh tĩnh":$"{(int)Engine.GetFramesPerSecond()} FPS");SyncInspector();
    }
    private void MeasurePreview()
    {
        if(_benchmarkPath==null)return;ulong now=Godot.Time.GetTicksUsec();double elapsed=(now-_benchmarkStart)/1_000_000d;
        if(elapsed>2)_samples.Add((now-_lastTick)/1000d);_lastTick=now;if(elapsed<14)return;var a=_samples.OrderBy(v=>v).ToArray();
        var report=new{scene="PaperDollLabV2",scope="TWO_PREVIEWS_NOT_WORLD_OR_COMBAT",targetFps=60,gpu=RenderingServer.GetVideoAdapterName(),measurementSeconds=elapsed-2,samples=a.Length,medianMs=a[a.Length/2],p95Ms=a[Math.Min(a.Length-1,(int)(a.Length*.95))],meanFps=1000/_samples.Average(),productionApproved=false};
        using var file=FileAccess.Open(_benchmarkPath,FileAccess.ModeFlags.Write);file.StoreString(JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true})+"\n");GD.Print("PAPERDOLL_LAB_BENCHMARK "+JsonSerializer.Serialize(report));_benchmarkPath=null;GetTree().Quit();
    }
    public override void _UnhandledKeyInput(InputEvent ev)
    {if(ev is not InputEventKey k||!k.Pressed||k.Echo)return;if(k.CtrlPressed&&k.Keycode==Key.Z)History(false);else if(k.CtrlPressed&&k.Keycode==Key.Y)History(true);else if(k.Keycode==Key.Space)Pause(!_paused);else if(k.Keycode==Key.Escape)GetTree().Quit();}
    private async void Capture(string path)
    {
        _captureMode=true;_showGuides.ButtonPressed=_captureTools;Seek(_captureFrame);for(int i=0;i<5;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);var result=GetViewport().GetTexture().GetImage().SavePng(path);GD.Print("PAPERDOLL_LAB_CAPTURE "+result+" CANDIDATE_NOT_GAMEPLAY");GetTree().Quit(result==Error.Ok?0:1);
    }
}
public partial class PaperDollGuides : Node2D
{
    public Vector2 Origin,BaseOrigin;
    public float Zoom=4;
    public Dictionary<string,Pixel> Anchors=new();
    public DrawCommand? Selected;
    public override void _Draw()
    {
        var line=new Color(.18f,.31f,.38f,.25f);
        foreach(var o in new[]{BaseOrigin,Origin}){DrawRect(new Rect2(o-new Vector2(48,72)*Zoom,new Vector2(96,96)*Zoom),line,false);DrawLine(o-new Vector2(30,0)*Zoom,o+new Vector2(30,0)*Zoom,line);}
        foreach(var (name,p) in Anchors){var v=Origin+new Vector2(p.X-48,p.Y-72)*Zoom;var c=name=="ground"?Colors.IndianRed:Color.FromHtml("#438cbd");DrawLine(v-new Vector2(3,0),v+new Vector2(3,0),c);DrawLine(v-new Vector2(0,3),v+new Vector2(0,3),c);}
        if(Selected is DrawCommand command)
        {
            var a=Corners(command);for(int i=0;i<4;i++)DrawLine(Origin+new Vector2((float)a[i].X,(float)a[i].Y)*Zoom,Origin+new Vector2((float)a[(i+1)%4].X,(float)a[(i+1)%4].Y)*Zoom,Color.FromHtml("#8066d4"),1);
            var p=Origin+new Vector2(command.Position.X,command.Position.Y)*Zoom;DrawCircle(p,3,Colors.DarkOrange);
            DrawLine(p,p+new Vector2(20,0),Colors.IndianRed);DrawLine(p,p+new Vector2(0,20),Colors.SteelBlue);
        }
    }
}
