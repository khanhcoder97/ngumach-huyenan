using Godot;
using System;
using System.IO;
using System.Linq;

namespace Ngumach.VisualReboot;

public partial class ArtStudio
{
    private void RunTests()
    {
        try
        {
            int n = 0;
            void Check(bool ok, string why) { if (!ok) throw new Exception(why); n++; }
            void Reject(Action action, string why) { bool rejected = false; try { action(); } catch { rejected = true; } Check(rejected, why); }
            foreach (var e in _entries)
            {
                var doc = ArtStudioLibrary.Load(e.Id); ArtStudioCodec.ValidateTextures(doc, "");
                Check(doc.Clips.All(c => c.DurationsMs.Count is >= 16 and <= 20), "wrong timeline count: " + e.Id);
                foreach (var c in doc.Clips)
                    foreach (var l in doc.Layers)
                    {
                        Check(ArtStudioSampler.FrameAt(c, 0) == 0 && ArtStudioSampler.FrameAt(c, c.Duration) == (c.Loop ? 0 : c.DurationsMs.Count - 1), "clip boundary");
                        for (int f = 0; f < c.DurationsMs.Count; f++) { var p = ArtStudioSampler.Pose(l, c, f); Check(p.SourceFrame >= 0 && p.SourceFrame < l.Regions.Count, "source binding"); }
                    }
            }
            foreach (string action in new[] { "idle", "walk", "telegraph_01", "attack_01", "recovery_01", "hurt", "death" })
            {
                var grouped = ArtStudioLibrary.Load("actor:MOB_CARPLING:" + action).Clips.Single(c => c.Direction == "S");
                string page = "mob_carpling_" + action + (action is "idle" or "walk" ? "" : "_s");
                var raw = ArtStudioLibrary.Load(page).Clips.Single(c => c.Direction == "S");
                Check(Math.Abs(grouped.Duration - raw.Duration) < .00001 && Math.Abs(grouped.Duration - ActorLibraryData.Duration("MOB_CARPLING", action)) < .00001, "raw/group timing mismatch: " + action);
                if (action != "idle" && action != "walk") Check(!grouped.Loop && !raw.Loop, "combat source must default to one shot");
            }
            foreach (string action in new[] { "telegraph_01", "attack_01", "recovery_01", "hurt", "death" })
            {
                var group = ArtStudioLibrary.Load("actor:MOB_CARPLING:" + action);
                Check(group.Clips.Count == 8, "missing combat direction: " + action);
                foreach (var previewClip in group.Clips)
                {
                    string source = previewClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => previewClip.Direction };
                    var raw = ArtStudioLibrary.Load("mob_carpling_" + action + "_" + source.ToLowerInvariant()).Clips.Single();
                    Check(Math.Abs(previewClip.Duration - raw.Duration) < .00001 && !previewClip.Loop, "combat timing/loop mismatch: " + action + "/" + previewClip.Direction);
                }
            }
            foreach (string action in new[] { "idle", "walk", "run", "turn", "telegraph_01", "attack_01", "recovery_01", "telegraph_02", "attack_02", "recovery_02", "hurt", "death" })
            {
                var group = ArtStudioLibrary.Load("actor:MOB_WATERROOT:" + action);
                Check(group.Clips.Count == 8, "missing Waterroot direction: " + action);
                foreach (var rootClip in group.Clips)
                {
                    string source = rootClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => rootClip.Direction };
                    var raw = ArtStudioLibrary.Load("mob_waterroot_" + action + "_" + source.ToLowerInvariant()).Clips.Single();
                    bool loop = action is "idle" or "walk" or "run";
                    Check(rootClip.Loop == loop && raw.Loop == rootClip.Loop, "Waterroot loop mismatch");
                    Check(Math.Abs(rootClip.Duration - raw.Duration) < .00001 && Math.Abs(rootClip.Duration - ActorLibraryData.Duration("MOB_WATERROOT", action)) < .00001, "Waterroot raw/group timing mismatch");
                    if (!loop) Check(ArtStudioSampler.FrameAt(rootClip, rootClip.Duration * 2) == 15, "Waterroot one-shot did not hold final pose");
                }
            }
            var rootRipple = ArtStudioLibrary.Load("sk_mob_waterroot_01_ripple_component").Clips.Single();
            Check(!rootRipple.Loop && Math.Abs(rootRipple.Duration - .7) < .00001, "root warning cue duration/loop mismatch");
            Check(ArtStudioSampler.FrameAt(rootRipple, rootRipple.Duration * 2) == 15, "root cue final pose");
            var guard = ArtStudioLibrary.Load("actor:CLASS_MINH_KIEM:skill_01");
            Check(guard.Clips.Count == 8, "guard missing directions");
            foreach (var guardClip in guard.Clips)
            {
                string facing = guardClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => guardClip.Direction };
                var raw = ArtStudioLibrary.Load("class_minh_kiem_skill_01_" + facing.ToLowerInvariant()).Clips.Single();
                Check(!guardClip.Loop && !raw.Loop && Math.Abs(guardClip.Duration - .8) < .00001 && Math.Abs(raw.Duration - guardClip.Duration) < .00001, "guard raw/group profile mismatch");
                Check(ArtStudioSampler.FrameAt(guardClip, guardClip.Duration * 2) == 15, "guard did not hold final pose");
            }
            foreach (string action in new[] { "skill_02", "skill_03", "skill_04", "skill_05", "skill_06", "hurt", "death", "dodge" })
            {
                var grouped = ArtStudioLibrary.Load("actor:CLASS_MINH_KIEM:" + action);
                Check(grouped.Clips.Count == 8, "missing timed skill directions");
                foreach (var skillClip in grouped.Clips)
                {
                    string facing = skillClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => skillClip.Direction };
                    var raw = ArtStudioLibrary.Load("class_minh_kiem_" + action + "_" + facing.ToLowerInvariant()).Clips.Single();
                    Check(skillClip.DurationsMs.SequenceEqual(raw.DurationsMs) && !skillClip.Loop && !raw.Loop, "raw/group source timing differs");
                    Check(Math.Abs(skillClip.Duration - ActorLibraryData.Duration("CLASS_MINH_KIEM", action)) < .00001, "skill preview duration differs");
                    var visited = new System.Collections.Generic.HashSet<int>();
                    for (int step = 0; step < Math.Ceiling(skillClip.Duration * 60) + 2; step++) visited.Add(ArtStudioSampler.FrameAt(skillClip, step / 60d));
                    Check(visited.Count == 16 && ArtStudioSampler.FrameAt(skillClip, skillClip.Duration * 2) == 15, "timed source poses skipped/restarted");
                    if (action == "skill_02") Check(ArtStudioSampler.FrameAt(skillClip, .15) == 4 && ArtStudioSampler.FrameAt(skillClip, .35) == 10, "Studio Tam Long phases");
                    if (action == "skill_03") Check(ArtStudioSampler.FrameAt(skillClip, .1) == 4 && ArtStudioSampler.FrameAt(skillClip, .22) == 8 && ArtStudioSampler.FrameAt(skillClip, .36) == 12, "Studio Kiem Tran phases");
                    if (action == "skill_05") Check(ArtStudioSampler.FrameAt(skillClip, .08) == 4 && ArtStudioSampler.FrameAt(skillClip, .24) == 10, "Studio Bach Hong presentation phases");
                    if (action == "skill_06") Check(ArtStudioSampler.FrameAt(skillClip, .70) == 6 && ArtStudioSampler.FrameAt(skillClip, 1.05) == 10, "Studio Van Tuong phases");
                    if (action == "dodge") Check(ArtStudioSampler.FrameAt(skillClip, .08) == 4 && ArtStudioSampler.FrameAt(skillClip, .26) == 10, "Studio dodge presentation phases");
                    var roundtrip = ArtStudioCodec.Decode(ArtStudioCodec.Encode(grouped));
                    Check(roundtrip.Clips.Single(c => c.Direction == skillClip.Direction).DurationsMs.SequenceEqual(skillClip.DurationsMs), "timed JSON roundtrip changed durations");
                }
            }
            foreach (string action in new[] { "skill_01", "skill_02", "skill_03", "skill_04", "skill_05", "skill_06", "dodge" })
            {
                var grouped = ArtStudioLibrary.Load("actor:CLASS_ANH_DAO:" + action);
                Check(grouped.Clips.Count == 8, "Anh Dao directions missing");
                foreach (var anhClip in grouped.Clips)
                {
                    string facing = anhClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => anhClip.Direction };
                    var raw = ArtStudioLibrary.Load("class_anh_dao_" + action + "_" + facing.ToLowerInvariant()).Clips.Single();
                    Check(anhClip.DurationsMs.SequenceEqual(raw.DurationsMs) && !anhClip.Loop && !raw.Loop, "Anh Dao raw/group timing or one-shot differs");
                    Check(Math.Abs(anhClip.Duration - ActorLibraryData.Duration("CLASS_ANH_DAO", action)) < .00001, "Anh Dao duration differs");
                    var visited = new System.Collections.Generic.HashSet<int>();
                    for (int tick = 0; tick < Math.Ceiling(anhClip.Duration * 60) + 2; tick++) visited.Add(ArtStudioSampler.FrameAt(anhClip, tick / 60d));
                    Check(visited.Count == 16 && ArtStudioSampler.FrameAt(anhClip, anhClip.Duration * 2) == 15, "Anh Dao source frames skipped/restarted");
                    if (action == "skill_01") Check(ArtStudioSampler.FrameAt(anhClip, .12) == 4 && ArtStudioSampler.FrameAt(anhClip, .32) == 10, "Studio Huyet Nguyet phases");
                    if (action == "skill_02") Check(ArtStudioSampler.FrameAt(anhClip, .16) == 4 && ArtStudioSampler.FrameAt(anhClip, .40) == 10, "Studio Tan Hoa phases");
                    if (action == "skill_03") Check(ArtStudioSampler.FrameAt(anhClip, .14) == 4 && ArtStudioSampler.FrameAt(anhClip, .24) == 7 && ArtStudioSampler.FrameAt(anhClip, .32) == 9 && ArtStudioSampler.FrameAt(anhClip, .42) == 12, "Studio Xich Anh two-cut phases");
                    if (action == "skill_04") Check(ArtStudioSampler.FrameAt(anhClip, .20) == 6 && ArtStudioSampler.FrameAt(anhClip, .36) == 10, "Studio Tuoc Mach phases");
                    if (action == "skill_05") Check(ArtStudioSampler.FrameAt(anhClip, .08) == 4 && ArtStudioSampler.FrameAt(anhClip, .30) == 12, "Studio Anh Bo phases");
                    if (action == "skill_06") Check(ArtStudioSampler.FrameAt(anhClip, .55) == 4 && ArtStudioSampler.FrameAt(anhClip, .80) == 12, "Studio Tu Diem charge/release");
                    if (action == "dodge") Check(ArtStudioSampler.FrameAt(anhClip, .08) == 4 && ArtStudioSampler.FrameAt(anhClip, .26) == 10, "Studio Anh Dao dodge phases");
                    var roundtrip = ArtStudioCodec.Decode(ArtStudioCodec.Encode(grouped));
                    Check(roundtrip.Clips.Single(c => c.Direction == anhClip.Direction).DurationsMs.SequenceEqual(anhClip.DurationsMs), "Anh Dao timing JSON roundtrip");
                }
            }
            foreach (var component in ArtStudioLibrary.ComponentEntries())
            {
                var composite = ArtStudioLibrary.Load("actor:CLASS_MINH_KIEM:skill_01");
                var source = ArtStudioLibrary.Load(component.Id); var componentLayer = source.Layers.Single();
                int layers = composite.Layers.Count;
                ArtStudioLibrary.AddComponent(composite, component.Id); ArtStudioCodec.ValidateTextures(composite, "");
                var inserted = composite.Layers.Last();
                Check(composite.Layers.Count == layers + 1 && inserted.Kind == "vfx" && inserted.Texture == componentLayer.Texture, "component layer did not retain source");
                Check(inserted.Regions.Count == 16 && inserted.Regions.Zip(componentLayer.Regions).All(pair => pair.First.SequenceEqual(pair.Second)), "component source regions changed");
                foreach (var compositeClip in composite.Clips)
                {
                    var frames = Enumerable.Range(0, compositeClip.DurationsMs.Count).Select(f => ArtStudioSampler.Pose(inserted, compositeClip, f).SourceFrame).ToArray();
                    Check(frames.SequenceEqual(Enumerable.Range(0, 16)), "component insertion skipped/reordered poses");
                }
                var roundtrip = ArtStudioCodec.Decode(ArtStudioCodec.Encode(composite));
                Check(!roundtrip.ProductionApproved && roundtrip.Layers.Last().Texture == componentLayer.Texture, "manual component insertion promoted approval or lost texture");
            }
            string guardBefore = ArtStudioCodec.Encode(guard);
            Reject(() => ArtStudioLibrary.AddComponent(guard, "mob_waterroot_idle_s"), "non-component source inserted as VFX");
            Check(ArtStudioCodec.Encode(guard) == guardBefore, "rejected component changed document");
            foreach (var guardClip in guard.Clips) ArtStudioSampler.Resize(guardClip, 8);
            Reject(() => ArtStudioLibrary.AddComponent(guard, "sk_mk_01_parry_component"), "short timeline silently dropped component poses");
            foreach (var profile in new[] { ("sk_mk_01_parry_component", .4, false), ("sk_ad_01_cut_component", .32, false), ("sk_hb_01_ink_hit_component", .32, false), ("sk_tc_01_dust_component", .35, false), ("sk_lc_01_mark_component", 1d, true), ("sk_mob_waterroot_02_line_component", .7, false), ("sk_mob_waterroot_02_spike_component", .4, false), ("sk_mob_waterroot_02_retract_component", .6, false) })
            {
                var component = ArtStudioLibrary.Load(profile.Item1).Clips.Single();
                Check(component.Loop == profile.Item3 && Math.Abs(component.Duration - profile.Item2) < .00001, "component preview profile mismatch: " + profile.Item1);
                var visited = new System.Collections.Generic.HashSet<int>();
                for (int step = 0; step < Math.Ceiling(component.Duration * 60); step++) visited.Add(ArtStudioSampler.FrameAt(component, step / 60d));
                Check(visited.Count == 16, "60-step component preview skipped source poses: " + profile.Item1);
                Check(ArtStudioSampler.FrameAt(component, component.Duration * 2) == (component.Loop ? 0 : 15), "component loop/end boundary: " + profile.Item1);
            }
            foreach (var profile in new[] { ("sk_mk_02_trail_component", .32), ("sk_mk_02_stop_dust_component", .32), ("sk_mk_04_gain_component", .4), ("sk_mk_04_break_component", .32), ("sk_mk_04_expire_component", .4), ("sk_mk_05_trail_component", .32), ("sk_mk_06_charge_component", .7), ("sk_mk_06_cut_component", .35) })
            {
                var source = ArtStudioLibrary.Load(profile.Item1);
                var componentClip = source.Clips.Single();
                Check(!componentClip.Loop && Math.Abs(componentClip.Duration - profile.Item2) < .00001, "new component profile mismatch");
                var visited = new System.Collections.Generic.HashSet<int>();
                for (int step = 0; step < Math.Ceiling(componentClip.Duration * 60) + 2; step++) visited.Add(ArtStudioSampler.FrameAt(componentClip, step / 60d));
                Check(visited.Count == 16 && ArtStudioSampler.FrameAt(componentClip, componentClip.Duration * 2) == 15, "new component source skipped/restarted");
                Check(ArtStudioCodec.Decode(ArtStudioCodec.Encode(source)).Clips.Single().DurationsMs.SequenceEqual(componentClip.DurationsMs), "component timing JSON changed");
            }
            foreach (string action in new[] { "walk", "interact" })
            {
                var group = ArtStudioLibrary.Load("actor:NPC_BOAT_KEEPER:" + action);
                Check(group.Clips.Count == 8, "missing NPC direction: " + action);
                foreach (var npcClip in group.Clips)
                {
                    string source = npcClip.Direction switch { "SW" => "SE", "W" => "E", "NW" => "NE", _ => npcClip.Direction };
                    var raw = ArtStudioLibrary.Load("npc_boat_keeper_" + action + "_" + source.ToLowerInvariant()).Clips.Single();
                    Check(npcClip.Loop == (action == "walk") && raw.Loop == npcClip.Loop, "NPC loop mismatch: " + action + "/" + npcClip.Direction);
                    Check(Math.Abs(npcClip.Duration - raw.Duration) < .00001 && Math.Abs(npcClip.Duration - ActorLibraryData.Duration("NPC_BOAT_KEEPER", action)) < .00001, "NPC duration mismatch");
                    if (action == "interact") Check(ArtStudioSampler.FrameAt(npcClip, npcClip.Duration * 2) == 15, "NPC interaction did not hold final pose");
                }
            }
            var original = ArtStudioCodec.Encode(_doc); var sourceHash = System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(ArtStudioCodec.Resolve(Layer.Texture, "")));
            _keyMode.ButtonPressed = true; _numbers["x"].Value = 17;
            Check(Math.Abs(Pose().X - 17) < .001, "inspector signal did not edit a key");
            Undo(); Check(ArtStudioCodec.Encode(_doc) == original, "undo mismatch"); Redo(); Check(Pose().X == 17, "redo mismatch");
            _visible.ButtonPressed = false; Check(!Layer.Visible, "visibility signal"); Undo();
            _locked.ButtonPressed = true; float x = Pose().X; _numbers["x"].Value = 29; Check(Pose().X == x, "locked layer changed"); _locked.ButtonPressed = false;
            Layer.Rest.X = 0; BeginDrag(); Drag(new Vector2(7, -3), false); EndDrag(); Check(Pose().X == x + 7, "drag edit"); Undo(); Check(Pose().X == x, "drag undo");
            Seek(5); Check(_frame == 5 && _stage.Frame == 5, "seek");
            var test = ArtStudioCodec.Decode(original); var layer = test.Layers[0]; var clip = test.Clips.First(c => c.Direction == "S");
            clip.Tracks.Clear(); layer.Rest = new();
            ArtStudioSampler.SetKey(clip, layer.Id, 0, new() { X = 0, Angle = 350 }); ArtStudioSampler.SetKey(clip, layer.Id, 10, new() { X = 100, Angle = 10 });
            Check(Math.Abs(ArtStudioSampler.Pose(layer, clip, 5).X - 50) < .001, "interpolation");
            Check(Math.Abs(ArtStudioSampler.Pose(layer, clip, 5).Angle - 360) < .01, "angle shortest arc");
            clip.Tracks[0].Interpolate = false; Check(ArtStudioSampler.Pose(layer, clip, 5).X == 0, "step mode");
            clip.DurationsMs[0] = 20; clip.DurationsMs[1] = 200; Check(ArtStudioSampler.FrameAt(clip, .05) == 1, "variable duration"); clip.Loop = false;
            Check(ArtStudioSampler.FrameAt(clip, 500) == 15, "one-shot clamp");
            var marker = new ArtStudioMarker { Frame = 1 }; double hit = ArtStudioSampler.TimeAt(clip, 1);
            Check(ArtStudioSampler.MarkerCrossings(clip, marker, 0, hit + .001) == 1, "skipped marker");
            Check(ArtStudioSampler.MarkerCrossings(clip, marker, hit + .001, clip.Duration + 1) == 0, "one-shot repeated marker");
            clip.Loop = true; Check(ArtStudioSampler.MarkerCrossings(clip, marker, 0, clip.Duration * 3 + hit + .001) == 4, "multi-loop marker");
            var socket = new ArtStudioSocket { Id = "hand", LayerId = layer.Id, X = 10, Y = 20 }; test.Sockets.Add(socket);
            layer.Rest = new() { X = 4, Y = 8, ScaleX = 2, ScaleY = 2 }; clip.Tracks.Clear();
            Check(ArtStudioSampler.SocketPoint(test, clip, socket, 0).IsEqualApprox(new Vector2(24, 48)), "socket transform");
            var child = new ArtStudioLayer { Id = "weapon", Texture = layer.Texture, Regions = layer.Regions.Select(r => r.ToArray()).ToList(), AttachSocket = "hand", Rest = new() { X = 3, Y = 0 } }; test.Layers.Add(child);
            Check((ArtStudioSampler.Transform(test, clip, child, 0) * Vector2.Zero).IsEqualApprox(new Vector2(30, 48)), "attachment transform");
            layer.AttachSocket = "hand"; Reject(() => ArtStudioCodec.Validate(test), "cycle accepted"); layer.AttachSocket = "";
            child.Texture = "textures/../secret.png"; Reject(() => ArtStudioCodec.Validate(test), "traversal accepted"); child.Texture = layer.Texture;
            child.Rest.X = float.NaN; Reject(() => ArtStudioCodec.Validate(test), "NaN accepted"); child.Rest.X = 0;
            child.Rest.SourceFrame = 500; Reject(() => ArtStudioCodec.Validate(test), "invalid source accepted"); child.Rest.SourceFrame = 0;
            clip.Markers.Add(new() { Frame = 15 }); ArtStudioSampler.Resize(clip, 8); Check(clip.DurationsMs.Count == 8 && clip.Markers.Count == 0, "resize did not prune");
            test.ProductionApproved = true; Reject(() => ArtStudioCodec.Validate(test), "self approval"); test.ProductionApproved = false;
            Check(ArtStudioCodec.Readiness(test).Any(x => x.Contains("Chưa đạt", StringComparison.Ordinal)), "static poses promoted");
            string folder = ProjectSettings.GlobalizePath("user://art_studio/tests"); Directory.CreateDirectory(folder); string path = Path.Combine(folder, "roundtrip.json");
            ArtStudioCodec.SaveAtomic(path, test); var reload = ArtStudioCodec.Decode(File.ReadAllText(path)); Check(ArtStudioCodec.Encode(reload) == ArtStudioCodec.Encode(test), "save roundtrip");
            ArtStudioCodec.SaveAtomic(path, test); Check(File.Exists(path + ".bak"), "backup missing");
            ArtStudioCodec.ExportBundle(Path.Combine(folder, "export", "actor.json"), test, ""); var bundle = ArtStudioCodec.Decode(File.ReadAllText(Path.Combine(folder, "export", "actor.json")));
            ArtStudioCodec.ValidateTextures(bundle, Path.Combine(folder, "export")); Check(bundle.Layers.All(l => l.Texture.StartsWith("textures/", StringComparison.Ordinal)), "export not portable");
            string imported = ArtStudioCodec.ImportPng(ArtStudioCodec.Resolve(layer.Texture, "")); Check(File.ReadAllBytes(ArtStudioCodec.Resolve(imported, "")).SequenceEqual(File.ReadAllBytes(ArtStudioCodec.Resolve(layer.Texture, ""))), "import altered PNG");
            Check(sourceHash.SequenceEqual(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(ArtStudioCodec.Resolve(Layer.Texture, "")))), "source changed");
            _doc = ArtStudioCodec.Decode(original); _clip = _doc.Clips.FindIndex(c => c.Direction == "S"); _frame = 0; _selected = _doc.Layers[0].Id;
            Change(() => ArtStudioLibrary.AddVfx(_doc, 0)); Check(_doc.Layers.Count == 2 && _doc.Layers.Last().Regions.Count == 6, "VFX preset");
            Undo(); Check(_doc.Layers.Count == 1, "VFX undo");
            GD.Print($"ART_STUDIO_SELF_TEST PASS assertions={n} libraryEntries={_entries.Length} ORIGINAL_PNG_UNCHANGED NOT_PRODUCTION_APPROVAL"); GetTree().Quit();
        }
        catch (Exception e) { GD.PushError("ART_STUDIO_SELF_TEST FAIL " + e); GetTree().Quit(1); }
    }
}
