using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using static Ngumach.VisualReboot.ModularCharacterModel;

namespace Ngumach.VisualReboot;

/// <summary>Metadata fixtures only. This does not certify artwork, fit or GPU performance.</summary>
public partial class ModularCharacterSelfTest : Node
{
    private int _checks;
    private static bool ResourcesReady(ClipPlan _)=>true;
    private void Check(bool value,string message){if(!value)throw new Exception(message);_checks++;}
    private static Look Fixture(long revision=1,int frames=16,bool female=false,bool helmet=false)
    {
        string rig=female?"RIG_HUMAN_F_V1":"RIG_HUMAN_M_V1";
        var clips=new Dictionary<string,Clip>(StringComparer.Ordinal);
        foreach(string action in new[]{"idle","walk","death"})foreach(string direction in Directions)
        {
            string key=action+"/"+direction;var poses=Enumerable.Range(0,frames).Select(i=>new Pose(key+"/"+i,
                new Dictionary<string,Pixel>{{"ground",new(48,72)},{"head",new(48,43+i%2)},{"hand_near",new(60,56+i%2)}},
                new Dictionary<string,Slice>{{"body",new("fixture:body",new(0,0,20,36),new(38,36))},{"hand_near",new("fixture:hand",new(0,0,8,8),new(56,52+i%2))}},
                new[]{"weapon_far","body","shirt","eyes","hair","hat","weapon_near","hand_near"})).ToArray();
            clips.Add(key,new Clip(key,rig+"/"+action,action=="walk"?.8:action=="death"?1.2:1,action!="death",poses));
        }
        Part Make(string id,string slot,PartMode mode,Slice template,string? weapon=null,string[]? hides=null)
        {
            var bindings=clips.ToDictionary(p=>p.Key,p=>new Binding(p.Value.PoseSet,Enumerable.Range(0,frames).Select(i=>template with{Hidden=slot=="eyes"&&p.Key.EndsWith("/N",StringComparison.Ordinal)}).ToArray(),p.Value.Poses.Select(pose=>pose.Fingerprint).ToArray()),StringComparer.Ordinal);
            return new Part(id,slot,rig,weapon,mode,false,hides??Array.Empty<string>(),bindings);
        }
        var parts=new List<Part>{Make("SHIRT_A","shirt",PartMode.Deformable,new("fixture:shirt",new(0,0,16,12),new(40,50))),
            Make("EYES_A","eyes",PartMode.AnchoredRigid,new("fixture:eyes",new(0,0,4,2),new(-2,0),"head")),
            Make("HAIR_A","hair",PartMode.AnchoredRigid,new("fixture:hair",new(0,0,16,13),new(-8,-12),"head")),
            Make("JIAN_A","weapon_near",PartMode.AnchoredRigid,new("fixture:weapon",new(0,0,4,24),new(0,-16),"hand_near"),"JIAN")};
        if(helmet)parts.Add(Make("HAT_A","hat",PartMode.AnchoredRigid,new("fixture:hat",new(0,0,14,10),new(-7,-10),"head"),hides:new[]{"hair"}));
        return new Look(revision,new BodyPack("BASE_MK_"+(female?"F":"M"),"CLASS_MINH_KIEM",rig,"JIAN",new(96,96),new(48,72),false,clips),parts.ToArray());
    }
    public override void _Ready()
    {
        try{Run();GD.Print($"MODULAR_CHARACTER_SELF_TEST PASS assertions={_checks} METADATA_FIXTURE_NOT_ART_FIT_OR_GAMEPLAY_ACCEPTANCE");GetTree().Quit();}
        catch(Exception e){GD.PushError("MODULAR_CHARACTER_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
    private void Run()
    {
        foreach(bool female in new[]{false,true})foreach(int frames in new[]{16,20})
        {Check(TryCompile(Fixture(frames:frames,female:female),true,out var plan,out _),"valid fixture rig/frame count");Check(plan!.Clips.Count==24,"eight directions per fixture action");}
        var look=Fixture();Check(TryCompile(look,true,out var compiled,out _),"compile fixture");
        Check(!compiled!.Clips["idle/N"].Frames[0].Any(c=>c.PartId=="eyes"),"eyes explicitly hidden on back view");
        var draw=compiled.Clips["idle/S"].Frames[0].ToArray();
        Check(Array.FindIndex(draw,c=>c.PartId=="body")<Array.FindIndex(draw,c=>c.PartId=="shirt"),"shirt covers body");
        Check(Array.FindIndex(draw,c=>c.PartId=="weapon_near")<Array.FindIndex(draw,c=>c.PartId=="hand_near"),"hand covers weapon grip");
        Check(draw.Single(c=>c.PartId=="eyes").Position==new Pixel(-2,-29),"one common origin; anchored eye position");
        Check(TryCompile(Fixture(helmet:true),true,out var hat,out _),"helmet fixture");
        Check(!hat!.Clips["idle/S"].Frames[0].Any(c=>c.PartId=="hair"),"helmet hair occlusion");
        Check(look.Parts.Single(p=>p.Slot=="eyes").Bindings["idle/S"].Frames.Select(f=>f.Texture).Distinct().Count()==1,"one rigid source may have sixteen pose bindings");
        Check(!TryCompile(look,false,out _,out var gate)&&gate.Contains("not production approved",StringComparison.Ordinal),"fixture cannot enter production");
        Check(!TryCompile(Fixture(frames:6),true,out _,out _),"six-frame body rejected");
        Check(!TryCompile(look with{Body=look.Body with{Canvas=new(97,96)}},true,out _,out _),"canvas mismatch rejected");
        Check(!TryCompile(look with{Parts=new[]{look.Parts[0],look.Parts[0]}},true,out _,out _),"duplicate visual slot rejected");
        Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{RigId="RIG_HUMAN_F_V1"}}},true,out _,out _),"wrong body fit rejected");
        Check(!TryCompile(look with{Parts=new[]{look.Parts[^1] with{WeaponFamily="BOW"}}},true,out _,out _),"wrong weapon family rejected");
        Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{Hides=new[]{"body"}}}},true,out _,out _),"wearable cannot hide actor");
        var bindings=look.Parts[0].Bindings.ToDictionary(p=>p.Key,p=>p.Value,StringComparer.Ordinal);
        bindings.Remove("walk/NW");Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{Bindings=bindings}}},true,out _,out _),"missing part direction rejected");
        bindings=look.Parts[0].Bindings.ToDictionary(p=>p.Key,p=>p.Value,StringComparer.Ordinal);
        bindings["idle/S"]=bindings["idle/S"] with{PoseSet="WRONG"};Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{Bindings=bindings}}},true,out _,out _),"wrong pose version rejected");
        bindings["idle/S"]=look.Parts[0].Bindings["idle/S"] with{Frames=look.Parts[0].Bindings["idle/S"].Frames.Take(15).ToArray()};Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{Bindings=bindings}}},true,out _,out _),"missing overlay frame rejected");
        bindings["idle/S"]=look.Parts[0].Bindings["idle/S"] with{Frames=look.Parts[0].Bindings["idle/S"].Frames.Select(f=>f with{Offset=new(-1000,0)}).ToArray()};Check(!TryCompile(look with{Parts=new[]{look.Parts[0] with{Bindings=bindings}}},true,out _,out _),"out of canvas rejected");
        var clips=look.Body.Clips.ToDictionary(p=>p.Key,p=>p.Value,StringComparer.Ordinal);var poses=clips["idle/S"].Poses.ToArray();poses[^1]=poses[^1] with{Fingerprint=poses[0].Fingerprint};clips["idle/S"]=clips["idle/S"] with{Poses=poses};Check(!TryCompile(look with{Body=look.Body with{Clips=clips}},true,out _,out _),"duplicated source pose rejected");
        poses=look.Body.Clips["idle/S"].Poses.ToArray();poses[0]=poses[0] with{Fingerprint="UPDATED_BODY_AND_GUIDES"};clips["idle/S"]=clips["idle/S"] with{Poses=poses};Check(!TryCompile(look with{Body=look.Body with{Clips=clips}},true,out _,out _),"regenerated body cannot silently reuse stale fitted clothing");
        var session=new Session();Check(session.TryApply(look,true,ResourcesReady,out _),"first look applies");var visited=new HashSet<int>{session.FrameIndex};for(int i=0;i<60;i++){session.Advance(1d/60);visited.Add(session.FrameIndex);}Check(visited.Count==16,"60FPS clock samples all sixteen idle poses");
        session.Advance(.35);double elapsed=session.Elapsed;int frame=session.FrameIndex;
        Check(session.TryApply(Fixture(2,helmet:true),true,ResourcesReady,out _),"swap appearance");Check(session.Elapsed==elapsed&&session.FrameIndex==frame,"gear swap preserves clock");
        Check(!session.TryApply(Fixture(1),true,ResourcesReady,out _)&&session.Current!.Revision==2,"stale revision ignored");
        Check(!session.TryApply(Fixture(3),true,_=>false,out _)&&session.Current!.Revision==2&&session.Elapsed==elapsed,"resource failure retains whole previous look");
        bool inner=false;Check(!session.TryApply(Fixture(4),true,plan=>{inner=session.TryApply(Fixture(5),true,ResourcesReady,out _);return true;},out _)&&inner&&session.Current!.Revision==5,"late load cannot overwrite newer look");
        Check(session.TryPlay("walk/S",ResourcesReady,true)&&session.FrameIndex==frame,"walk keeps phase");double walkTime=session.Elapsed;
        Check(session.TryPlay("walk/S",ResourcesReady)&&session.Elapsed==walkTime,"repeated state packet does not restart animation");
        Check(session.TryPlay("walk/NE",ResourcesReady,true)&&session.FrameIndex==frame,"direction change keeps phase");
        Check(!session.TryPlay("MISSING/S",ResourcesReady)&&session.ClipKey=="walk/NE","missing action does not alter state");
        Check(session.TryPlay("death/S",ResourcesReady),"death exists");session.Advance(10);Check(session.FrameIndex==15,"one-shot remains on final pose");
        var mutable=Fixture(10);var frozen=new Session();Check(frozen.TryApply(mutable,true,ResourcesReady,out _),"compile independent snapshot");var before=frozen.Commands.ToArray();mutable.Parts[0].Bindings["idle/S"].Frames[0]=mutable.Parts[0].Bindings["idle/S"].Frames[0] with{Offset=new(0,0)};Check(before.SequenceEqual(frozen.Commands),"caller mutation cannot move committed clothes");
        var twenty=new Session();Check(twenty.TryApply(Fixture(frames:20),true,ResourcesReady,out _),"twenty-frame pack");twenty.TryPlay("death/S",ResourcesReady);twenty.Advance(3);Check(twenty.FrameIndex==19,"twenty-frame one-shot holds pose20");
        Check(!TryCompile(look with{Body=look.Body with{Approved=true,SourcePixelsPerUnit=6}},false,out _,out var nativeGate)&&nativeGate.Contains("native pixel master",StringComparison.Ordinal),"review calibration cannot enter native production");
        Check(!TryCompile(look with{Body=look.Body with{SourcePixelsPerUnit=0}},true,out _,out _),"zero source calibration rejected");
        var calibrated=look with{Body=look.Body with{SourcePixelsPerUnit=6}};Check(TryCompile(calibrated,true,out var scaled,out _)&&scaled!.Clips["idle/S"].Frames[0].All(c=>c.SourcePixelsPerUnit==6),"one declared source calibration inherited by body and parts");
        Check(twenty.SeekFrame(7)&&twenty.FrameIndex==7,"scrub chooses requested pose");double scrubTime=twenty.Elapsed;Check(!twenty.SeekFrame(-1)&&!twenty.SeekFrame(20)&&twenty.Elapsed==scrubTime,"out-of-range scrub preserves clock");
        var changing=new Session();changing.TryApply(Fixture(),true,ResourcesReady,out _);
        Check(!changing.TryApply(Fixture(2),true,plan=>{changing.TryPlay("walk/S",ResourcesReady);return true;},out _)&&changing.Current!.Revision==1&&changing.ClipKey=="walk/S","action change cannot commit texture pages for the wrong clip");
        Check(!changing.TryPlay("death/S",plan=>{changing.TryApply(Fixture(3),true,ResourcesReady,out _);return true;})&&changing.Current!.Revision==3&&changing.ClipKey=="walk/S","prepared action cannot overwrite a newer appearance");
    }
}
