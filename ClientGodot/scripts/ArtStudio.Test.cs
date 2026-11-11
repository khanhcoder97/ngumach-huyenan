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
