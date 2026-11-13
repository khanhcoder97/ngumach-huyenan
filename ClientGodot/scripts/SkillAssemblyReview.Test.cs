using Godot;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Ngumach.VisualReboot;

public partial class SkillAssemblyReview
{
    private void RunTests()
    {
        try
        {
            int checks=0;void Check(bool ok,string why){if(!ok)throw new InvalidOperationException(why);checks++;}
            Check(_document.Profiles.Count==12,"twelve skill profiles");Check(_document.Profiles.Sum(p=>p.Variants.Count)==20,"twenty conditional scenarios");
            var round=SkillAssemblyCodec.Decode(SkillAssemblyCodec.Encode(_document),_library);Check(round.Profiles.Count==12&&!round.ProductionApproved,"authoring roundtrip changed approval");
            void Reject(Action<SkillAssemblyDocument> change)
            {
                var copy=SkillAssemblyCodec.Decode(SkillAssemblyCodec.Encode(_document),_library);change(copy);bool rejected=false;
                try{SkillAssemblyCodec.Validate(copy,_library);}catch(InvalidOperationException){rejected=true;}Check(rejected,"invalid authoring edit accepted");
            }
            Reject(d=>d.ProductionApproved=true);Reject(d=>d.SchemaVersion=99);Reject(d=>d.Profiles[0].Variants[0].Tracks[0].Duration=0);
            Reject(d=>d.Profiles[0].Variants[0].Tracks[0].Anchor="HTTP");Reject(d=>d.Profiles[0].Variants[0].Tracks[0].ScreenX=float.NaN);
            Reject(d=>d.Profiles[0].Variants[0].Tracks[0].ComponentId="class_minh_kiem_walk_e");
            Reject(d=>d.Profiles[0].Variants[0].Tracks[0].SourceSeconds=1.7);
            Reject(d=>d.Profiles[0].Variants[0].Tracks[0].ResourceRadius=float.NaN);
            using var production=new ActorLibraryData();
            foreach(var profile in _document.Profiles)
            foreach(var variant in profile.Variants)
            {
                foreach(int facing in Enumerable.Range(0,8))
                {
                    Check(_library.Resolve(profile.ActorId,profile.BodyClip,facing,out var body)&&body!.Frames.Length==16,"missing authored body angle");
                    Check(production.Resolve(profile.ActorId,profile.BodyClip,facing,out _),"skill body approval gate");
                    Check(body!.Flip==(facing>=5),"body mirror ownership changed");
                    var sample=SkillAssemblySampler.Body(profile,variant,variant.Duration);Check(sample.Clip=="idle","body not restored after review scenario");
                }
                if(variant.OverrideClip!="")Check(SkillAssemblySampler.Body(profile,variant,variant.OverrideStart).Clip==variant.OverrideClip,"counter body override missing");
                if(variant.DashDistance>0)
                {
                    Check(SkillAssemblySampler.Travel(variant,0)==0,"dash starts early");
                    Check(Math.Abs(SkillAssemblySampler.Travel(variant,variant.DashStart+variant.DashDuration)-variant.DashDistance)<.001,"visual path endpoint");
                }
                foreach(var t in variant.Tracks)
                {
                    var source=_library.Pages[t.ComponentId].Directions.Single();
                    Check(source.Frames.Length==16,"component source was padded or missing");
                    Check(SkillAssemblySampler.ComponentFrame(t,source,t.Start-.001)==-1,"component starts early");
                    Check(SkillAssemblySampler.ComponentFrame(t,source,t.Start)==0,"component starts at wrong source frame");
                    Check(SkillAssemblySampler.ComponentFrame(t,source,t.Start+t.Duration)==-1,"last fragment stuck past end");
                    if(!t.Loop)
                    {
                        var visited=new HashSet<int>();for(int f=0;f<16;f++)visited.Add(SkillAssemblySampler.ComponentFrame(t,source,t.Start+(f+.5)*t.Duration/16));
                        // Nonuniform smoke/sweep timings are inspected with their
                        // original cumulative phase clock, not uniform frame time.
                        if(source.SourceFrameDurationsMs==null||source.SourceFrameDurationsMs.Distinct().Count()==1)Check(visited.Count==16,"retimed uniform source lost a pose at slow inspection");
                    }
                    else if(t.Duration>t.SourceSeconds*1.5)
                    {
                        Check(SkillAssemblySampler.ComponentFrame(t,source,t.Start+t.SourceSeconds*.25)==SkillAssemblySampler.ComponentFrame(t,source,t.Start+t.SourceSeconds*1.25),"host duration stretched the loop source clock");
                    }
                    for(double time=0;time<=variant.Duration+.05;time+=1d/60)
                    {
                        int frame=SkillAssemblySampler.ComponentFrame(t,source,time);Check(frame is >=-1 and <=15,"source frame outside16");
                        Check(frame<0||(time+1e-9>=t.Start&&time+1e-9<t.Start+t.Duration),"component outside its own event window");
                    }
                }
                for(int f=0;f<8;f++){_panes[f].Size=new Vector2(220,180);_panes[f].Bind(_library,_bounds,profile,variant,f,5,false);}
                float common=_panes.Min(p=>p.SuggestedScale);Check(common>0,"layout bounds empty");foreach(var pane in _panes)pane.Fit(common);
                Check(_panes.All(p=>Math.Abs(p.BodyDisplayHeight-_panes[0].BodyDisplayHeight)<.001),"auto-fit changed actor scale by facing");
                foreach(double time in new[]{0d,variant.Duration*.25,variant.Duration*.5,variant.Duration})
                foreach(var pane in _panes){pane.RenderAt(time);Check(pane.BodyFrame is >=0 and <=15,"rendered body frame outside source");}
                foreach(var pane in _panes){pane.RenderAt(variant.Duration);Check(pane.VisibleEffects==0,"FX state leaked after scenario");}
            }
            var phan=_document.Profiles.Single(p=>p.Id=="SK_MK_01");Check(!phan.Variants.Single(v=>v.Id=="guard_timeout").Tracks.Any(t=>t.Id is "parry" or "counter"),"timeout manufactured a counter");
            var guard=phan.Variants[0].Tracks[0];Check(SkillAssemblySampler.Depth(guard,0)==0&&SkillAssemblySampler.Depth(guard,4)==guard.Z,"north front cue must be occluded by the body");
            guard.DepthByFacing=false;Check(SkillAssemblySampler.Depth(guard,0)==guard.Z,"manual depth override ignored");guard.DepthByFacing=true;
            var mark=_document.Profiles.Single(p=>p.Id=="SK_AD_02");Check(mark.Variants.Where(v=>v.Id!="mark_trigger").All(v=>v.Tracks.All(t=>t.ComponentId!="sk_ad_02_pop_component")),"expiry/cancel auto exploded mark");
            var kiem=_document.Profiles.Single(p=>p.Id=="SK_MK_03").Variants.Single();Check(kiem.Tracks.Select(t=>t.Start).SequenceEqual(new[]{0d,.12,.26}),"triple-cut beat schedule changed");
            Check(kiem.Tracks.All(t=>!t.LowFxOptional),"LowFX may erase mandatory sword beats");
            foreach(var profile in _document.Profiles.Where(p=>p.Id is "SK_MK_01" or "SK_MK_03" or "SK_AD_01" or "SK_AD_03"))
            foreach(var variant in profile.Variants)
            foreach(var track in variant.Tracks.Where(t=>t.Id is "counter" or "cut" or "cut1" or "cut2" or "cut3" or "first" or "reverse"))
            for(int facing=0;facing<8;facing++)
                Check((SkillAssemblySampler.Anchor(track,profile,variant,facing,track.Start)-SkillAssemblySampler.Facings[facing]*SkillAssemblySampler.Travel(variant,track.Start)).Y < -20,"hand-height slash attached below the boots");
            var bach=_document.Profiles.Single(p=>p.Id=="SK_MK_05").Variants[0];Check(bach.Tracks.Single().Duration==.16&&bach.Tracks.All(t=>!t.ComponentId.Contains("impact",StringComparison.Ordinal)),"mobility trail widened i-frame/added impact");
            var tu=_document.Profiles.Single(p=>p.Id=="SK_AD_06");var release=tu.Variants[0];
            var petal=release.Tracks.Single(t=>t.ResourceInstances);Check(2*petal.ResourceRadius*Math.Sin(Math.PI/5)>petal.Size,"five heat petals overlap into one unreadable cluster");
            foreach(int resource in Enumerable.Range(0,6))
            foreach(bool low in new[]{false,true})
            {
                _panes[0].Bind(_library,_bounds,tu,release,0,resource,low);_panes[0].Fit(.5f);_panes[0].RenderAt(.9);
                Check(_panes[0].VisibleEffects==(low?1:1+resource),"heat petals/LowFX budget erased main sweep or invented resource");
            }
            SkillAssemblyCodec.VerifyComponentFiles(_document,_library);
            GD.Print("SKILL_ASSEMBLY_SELF_TEST PASS profiles=12 scenarios=20 angles=8 assertions="+checks+" INDEPENDENT_SOURCE_CLOCKS CONDITIONAL_EVENTS_ONLY NO_GAMEPLAY_MUTATION");GetTree().Quit();
        }
        catch(Exception e){GD.PushError("SKILL_ASSEMBLY_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
}
