using Godot;
using System;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using static Ngumach.VisualReboot.ModularCharacterModel;
namespace Ngumach.VisualReboot;
public partial class PaperDollLab
{
    private void SelfTest()
    {
        int checks=0;void Check(bool v,string m){if(!v)throw new Exception(m);checks++;}
        try
        {
            foreach(var body in _data.Data.Bodies)
            foreach(var part in _data.Data.Parts.Where(p=>p.RigId==null||p.RigId==body.RigId))
            {
                var look=_data.Build(body.Id,new[]{part.Id},++_revision);
                Check(TryCompile(look,true,out var p,out var compileReason),"compatible texture binding "+body.Id+" "+part.Id+": "+compileReason);
                Check(p!.Clips["idle/S"].Frames.Count==16,"sixteen placement records");
                Check(!_avatar.TryApply(look,out _),"study cannot enter production");
                Check(_avatar.TryApplyForReview(look,out _),"real texture/region/transform loads");
            }
            if(_data.Registered)
            {
                var versioned=_data.Build("MK_M",new[]{"OUTFIT_IVORY_M"},1);Check(!TryCompile(versioned with{Parts=new[]{versioned.Parts[0] with{RigId="RIG_HUMAN_M_V1"}}},true,out _,out _),"V1 clothes cannot be mixed with V2 anatomical master");
                int mismatches=0,leaks=0;foreach(string body in new[]{"MK_M","MK_F"})foreach(string palette in new[]{"IVORY","INDIGO"})foreach(int frame in Enumerable.Range(0,16))
                {string sex=body=="MK_M"?"M":"F";var ids=new[]{"OUTFIT_"+palette+"_"+sex,"HAIR_CHESTNUT","EYES_JADE","BOOTS_BROWN","JIAN_STEEL_RIGHT","HAT_TRAVELLER"};mismatches+=RegisteredPaperDollMaster.RegistrationMismatch(_data,body,ids,frame);leaks+=RegisteredPaperDollMaster.UncoveredBaseGarmentPixels(body,ids[0],frame);}
                Check(mismatches==0,"64 registered composites equal monolithic master pixel-for-pixel");
                Check(leaks==0,"base undershirt/shorts do not leak outside complete outfit");
                Check(_data.Data.Bodies.All(b=>b.SourcePixelsPerUnit==1),"native master uses one source pixel per logical pixel");
                Check(_data.Data.Parts.Where(p=>p.Category=="OUTFIT").All(p=>p.FrameRegions?.Length==16),"outfit artwork follows all sixteen authored joint poses");
                GD.Print("REGISTERED_MASTER_COVERAGE composites=64 uncoveredBaseGarmentPixels="+leaks);
                GD.Print("REGISTERED_MASTER_PIXEL_COMPARE composites=64 mismatchedPixels="+mismatches+" TECHNICAL_REGISTRATION_NOT_ART_APPROVAL");
            }
            _body="MK_M";_gender.Select(0);Check(Rebuild(),"restore male UI");
            Check(Selected().Count(id=>_data.FindPart(id).Slot=="outfit")==1&&!Selected().Any(id=>id.StartsWith("CHEST_",StringComparison.Ordinal)||id.StartsWith("LEGS_",StringComparison.Ordinal)),"shirt and trousers are one visual");
            Check(_data.Data.Parts.Where(p=>p.Category=="OUTFIT").All(p=>p.RigId!=null)&&_data.Data.Parts.Count(p=>p.Category=="OUTFIT")==4,"outfit has male/female variants");
            bool wrongRig=false;try{_data.Build("MK_M",new[]{"OUTFIT_IVORY_F"},999);}catch(ArgumentException){wrongRig=true;}Check(wrongRig,"wrong-gender fit rejected");
            Seek(7);double elapsed=_avatar.Animation.Elapsed;_outfit.Select(2);_outfit.EmitSignal(OptionButton.SignalName.ItemSelected,2L);
            Check(_avatar.Animation.Elapsed==elapsed&&Frame==7,"full outfit changes preserve clock");
            _hat.Select(2);_hat.EmitSignal(OptionButton.SignalName.ItemSelected,2L);
            Check(_avatar.Animation.Commands.Any(c=>c.PartId=="hair_front")&&_avatar.Animation.Commands.Any(c=>c.PartId=="hat_front"),"traveller hat keeps hair");
            var a=_avatar.Animation.Commands.ToArray();Check(Array.FindIndex(a,c=>c.PartId=="hair_front")<Array.FindIndex(a,c=>c.PartId=="hat_front"),"hat draws over retained hair");
            _hair.Select(2);_hair.EmitSignal(OptionButton.SignalName.ItemSelected,2L);
            var underHat=_avatar.Animation.Commands.Single(c=>c.PartId=="hair_front");Check(underHat.Region.Y>_data.Region("HAIR_TOPKNOT",Frame)[1],"hat clips topknot only while keeping fringe/sides");
            _hat.Select(0);_hat.EmitSignal(OptionButton.SignalName.ItemSelected,0L);
            Check(_avatar.Animation.Commands.Single(c=>c.PartId=="hair_front").Region.Y==_data.Region("HAIR_TOPKNOT",Frame)[1],"remove hat restores full original hair region");
            Check(Selected().Contains("BOOTS_BROWN"),"outfit change does not change independent boots");
            if(_data.Registered)
            {SelectSlot("weapon_near");string beforePivot=_data.ExportDraft();var beforeCorners=Corners(_avatar.Animation.Commands.Single(c=>c.PartId=="weapon_near"));_pivotX.Value+=1;var afterCorners=Corners(_avatar.Animation.Commands.Single(c=>c.PartId=="weapon_near"));Check(beforeCorners.SequenceEqual(afterCorners),"pivot editing preserves source placement on native grid");Check(_data.TryImportDraft(beforePivot,out _),"restore pivot draft");Rebuild();}
            SelectSlot("weapon_near");var sword=_avatar.Animation.Commands.Single(c=>c.PartId=="weapon_near");
            var bodyDef=_data.FindBody(_body);var skin=bodyDef.Frames[Frame];
            Check((double)sword.Region.Height/sword.SourcePixelsPerUnit*(sword.Transform??Identity).Scale<(double)skin.Region[3]/bodyDef.SourcePixelsPerUnit,"sword shorter than body");
            var pivot=ToActor(sword,(sword.Transform??Identity).PivotX,(sword.Transform??Identity).PivotY);
            var hand=_data.Anchor(_body,"hand_near",Frame);
            Check(Math.Abs(pivot.X-(hand.X-48))<.001&&Math.Abs(pivot.Y-(hand.Y-72))<.001,"sword grip pivot locks to hand");
            a=_avatar.Animation.Commands.ToArray();Check(Array.FindIndex(a,c=>c.PartId=="weapon_near")<Array.FindIndex(a,c=>c.PartId=="hand_near"),"skin hand covers grip");
            string original=_data.ExportDraft();_angle.Value=25;
            Check(Math.Abs((_avatar.Animation.Commands.Single(c=>c.PartId=="weapon_near").Transform??Identity).Degrees-25)<.001,"rotation control changes renderer");
            History(false);Check(_data.Transform(_body,Selected().Single(id=>_data.FindPart(id).Slot=="weapon_near"),Frame).Degrees==0,"undo rotation");
            History(true);Check(_data.Transform(_body,Selected().Single(id=>_data.FindPart(id).Slot=="weapon_near"),Frame).Degrees==25,"redo rotation");
            Check(_data.TryImportDraft(original,out _),"restore source draft");Check(Rebuild(),"restore visual");
            SelectSlot("weapon_near");string swordId=Target[5..];_coords.Select(1);_coords.EmitSignal(OptionButton.SignalName.ItemSelected,1L);
            Pixel abs=_data.AbsolutePosition(_body,swordId,Frame);_x.Value=abs.X+1;
            Check(_data.AbsolutePosition(_body,swordId,Frame).X==abs.X+1,"master coordinate editing maps to local offset");
            Pixel beforeAttach=_data.AbsolutePosition(_body,swordId,Frame);_attach.Select(Array.IndexOf(_anchorNames,"chest"));_attach.EmitSignal(OptionButton.SignalName.ItemSelected,(long)_attach.Selected);
            Check(_data.Attachment(_body,swordId,Frame)=="chest"&&_data.AbsolutePosition(_body,swordId,Frame)==beforeAttach,"changing attachment preserves canvas placement");
            _visible.ButtonPressed=false;Check(!_avatar.Animation.Commands.Any(c=>c.PartId=="weapon_near"),"visibility hides only selected presentation layer");
            _visible.ButtonPressed=true;Check(_avatar.Animation.Commands.Any(c=>c.PartId=="weapon_near"),"visibility restores item");
            int index=Array.IndexOf(_data.Order(_body,Frame),"weapon_near");_front.EmitSignal(Button.SignalName.Pressed);
            Check(Array.IndexOf(_data.Order(_body,Frame),"weapon_near")==index+1,"front control reorders painter layer");
            _back.EmitSignal(Button.SignalName.Pressed);Check(Array.IndexOf(_data.Order(_body,Frame),"weapon_near")==index,"back control restores painter order");
            _coords.Select(2);_coords.EmitSignal(OptionButton.SignalName.ItemSelected,2L);Pixel pos=_data.AbsolutePosition(_body,swordId,Frame);_x.Value+=_avatar.Scale.X;
            Check(_data.AbsolutePosition(_body,swordId,Frame).X==pos.X+1,"viewport coordinate editing converts through actor transform");
            Check(_data.TryImportDraft(original,out _),"reset before drag");Rebuild();SelectSlot("weapon_near");
            var start=new Vector2(_stage.Size.X*.75f,_stage.Size.Y*.5f);Pixel beforeDrag=_data.Offset(_body,swordId,Frame);
            _stage.EmitSignal(Control.SignalName.GuiInput,new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=true,Position=start});
            _stage.EmitSignal(Control.SignalName.GuiInput,new InputEventMouseMotion{Position=start+new Vector2(_avatar.Scale.X*2,_avatar.Scale.Y),ButtonMask=MouseButtonMask.Left});
            _stage.EmitSignal(Control.SignalName.GuiInput,new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=false,Position=start+new Vector2(8,4)});
            Check(_data.Offset(_body,swordId,Frame)==beforeDrag+new Pixel(2,1),"drag event converts stage pixels to actor units");
            History(false);Check(_data.Offset(_body,swordId,Frame)==beforeDrag,"one drag is one undo operation");
            string save=_data.ExportDraft();Check(_data.TryImportDraft(save,out _),"draft v2 roundtrip");
            Check(!_data.TryImportDraft(save.Replace(_data.Data.CatalogueFingerprint,"STALE",StringComparison.Ordinal),out _)&&_data.ExportDraft()==save,"stale source rejected atomically");
            var bad=JsonSerializer.Deserialize<PaperDollLabData.Draft>(save)!;bad.Transforms["MK_M/"+swordId]=Enumerable.Repeat(new PaintTransform(0,0,0,0),16).ToArray();
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(bad),out _)&&_data.ExportDraft()==save,"invalid transform rejected atomically");
            bad=JsonSerializer.Deserialize<PaperDollLabData.Draft>(save)!;bad.Orders["MK_M"]=Enumerable.Range(0,16).Select(i=>Enumerable.Repeat("body",9).ToArray()).ToArray();
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(bad),out _)&&_data.ExportDraft()==save,"duplicate layer order rejected");
            bad=JsonSerializer.Deserialize<PaperDollLabData.Draft>(save)!;bad.Attachments["MK_M/"+swordId]=Enumerable.Repeat("UNKNOWN",16).ToArray();
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(bad),out _)&&_data.ExportDraft()==save,"unknown attachment rejected");
            bad=JsonSerializer.Deserialize<PaperDollLabData.Draft>(save)!;bad.Hidden["MK_M/"+swordId]=new bool[15];
            Check(!_data.TryImportDraft(JsonSerializer.Serialize(bad),out _)&&_data.ExportDraft()==save,"missing per-pose visibility rejected");
            Check(!_data.TryImportDraft("{}",out _)&&_data.ExportDraft()==save,"old/malformed schema rejected");
            var t=new PaintTransform(2,3,37,.75,true,true);var draw=new DrawCommand("test","fixture",new(0,0,60,80),new(1,2),4,t);
            var q=ToActor(draw,4,7);var inverse=FromActor(draw,q.X,q.Y);Check(Math.Abs(inverse.X-4)<.0001&&Math.Abs(inverse.Y-7)<.0001,"rotation scale mirror coordinate roundtrip");
            _data.SetOffset(_body,swordId,Frame,beforeDrag,true);Check(Enumerable.Range(0,16).All(i=>_data.Offset(_body,swordId,i)==beforeDrag),"all-pose placement edit");
            var candidate=_data.Build(_body,new[]{swordId},++_revision);var cp=candidate.Parts[0];var bindings=cp.Bindings.ToDictionary(p=>p.Key,p=>p.Value with{Frames=p.Value.Frames.Select(f=>f with{Texture="res://assets/paperdoll_lab/MISSING.png"}).ToArray()});
            var previous=_avatar.Animation.Current;Check(!_avatar.TryApplyForReview(candidate with{Parts=new[]{cp with{Bindings=bindings}}},out _)&&ReferenceEquals(previous,_avatar.Animation.Current),"missing texture retains previous look");
            _data.Reset();Rebuild();Seek(0);var frames=new HashSet<int>();for(int i=0;i<(int)Math.Ceiling(_data.Data.Seconds*60)+1;i++){_avatar.Animation.Advance(1d/60);frames.Add(Frame);}Check(frames.Count==16,"one clock visits all body candidate cells");
            _gender.Select(1);_gender.EmitSignal(OptionButton.SignalName.ItemSelected,1L);
            Check(_body=="MK_F"&&Selected().Any(id=>id=="OUTFIT_INDIGO_F"),"gender switch resolves outfit variant");
            GD.Print($"PAPERDOLL_LAB_SELF_TEST PASS assertions={checks} ACTUAL_TEXTURE_UI_TRANSFORMS_NOT_ART_APPROVAL");GetTree().Quit();
        }
        catch(Exception e){GD.PushError("PAPERDOLL_LAB_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
}
