using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Adapts existing authored sheets and their exact irregular rectangles. Does not manufacture frames.</summary>
public static class ArtStudioLibrary
{
    public static (string Id, string Name)[] Entries()
    {
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/actor_library_v1/pages.json"));
        return new[] { ("motion:idle", "Minh Kiếm / idle"), ("motion:walk", "Minh Kiếm / walk"), ("motion:attack", "Minh Kiếm / attack"), ("motion:cast", "Minh Kiếm / cast") }
            .Concat(json.RootElement.GetProperty("pages").EnumerateArray().Where(p => p.GetProperty("file").GetString() != "")
            .Select(p => (p.GetProperty("id").GetString()!, p.GetProperty("id").GetString()!))).ToArray();
    }
    public static ArtStudioDocument Load(string id)
    {
        if (id.StartsWith("motion:", StringComparison.Ordinal)) return Motion(id[7..]);
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/actor_library_v1/pages.json"));
        var p = json.RootElement.GetProperty("pages").EnumerateArray().Single(p => p.GetProperty("id").GetString() == id);
        bool vfx = id.EndsWith("_vfx", StringComparison.Ordinal);
        var l = new ArtStudioLayer { Id = "sprite", Name = id, Kind = vfx ? "vfx" : "sprite", Texture = "res://assets/actor_library_v1/" + p.GetProperty("file").GetString() };
        var doc = new ArtStudioDocument { Name = id, Layers = new() { l } };
        foreach (var d in p.GetProperty("directions").EnumerateArray())
        {
            string direction = d.GetProperty("direction").GetString()!;
            float reference = d.TryGetProperty("referenceHeight", out var rh) ? rh.GetSingle() : p.GetProperty("referenceHeight").GetSingle();
            float scale = 140 / Math.Max(1, reference); bool flip = d.GetProperty("flip").GetBoolean();
            var frames = d.GetProperty("frames").EnumerateArray().ToArray();
            var c = new ArtStudioClip { Name = id, Direction = direction, SourceNote = (flip ? "Lật ngang theo metadata · " : "Nguồn sheet cũ · ") + p.GetProperty("visualState").GetString() + " · chưa nghiệm thu mới.", DurationsMs = Enumerable.Repeat(id.Contains("walk", StringComparison.Ordinal) ? 50f : 100f, frames.Length).ToList() };
            var track = new ArtStudioTrack { LayerId = l.Id, Interpolate = false }; c.Tracks.Add(track);
            foreach (var f in frames)
            {
                int index = l.Regions.Count; l.Regions.Add(f.GetProperty("rect").EnumerateArray().Select(n => n.GetInt32()).ToArray());
                var pv = f.GetProperty("pivot");
                track.Keys.Add(new() { Frame = track.Keys.Count, Pose = new() { PivotX = pv[0].GetSingle(), PivotY = pv[1].GetSingle(), ScaleX = flip ? -scale : scale, ScaleY = scale, SourceFrame = index } });
            }
            doc.Clips.Add(c);
        }
        l.Rest = doc.Clips.First().Tracks[0].Keys[0].Pose.Copy();
        ArtStudioCodec.Validate(doc); return doc;
    }
    private static ArtStudioDocument Motion(string action)
    {
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/motion16/manifest.json"));
        var dirs = json.RootElement.GetProperty("clips").GetProperty(action).EnumerateArray().ToArray();
        var doc = new ArtStudioDocument { Name = "Minh Kiếm / " + action };
        for (int di = 0; di < dirs.Length; di++)
        {
            var d = dirs[di]; var frames = d.GetProperty("frames").EnumerateArray().ToArray();
            var l = new ArtStudioLayer { Id = "sprite_" + di, Name = "Minh Kiếm / " + ArtStudioCodec.Directions[di], Texture = "res://assets/motion16/" + frames[0].GetProperty("file").GetString() };
            foreach (var f in frames) l.Regions.Add(f.GetProperty("rect").EnumerateArray().Select(n => n.GetInt32()).ToArray());
            l.Rest.Alpha = 0; doc.Layers.Add(l);
            var c = new ArtStudioClip { Name = action, Direction = ArtStudioCodec.Directions[di], SourceNote = frames[0].GetProperty("flip").GetBoolean() ? "Nguồn lật ngang theo metadata motion16." : "Minh Kiếm / bộ motion16 có sẵn, crop và pivot nguồn được giữ.", DurationsMs = Enumerable.Repeat(d.GetProperty("duration").GetSingle() * 1000 / frames.Length, frames.Length).ToList() };
            var t = new ArtStudioTrack { LayerId = l.Id, Interpolate = false }; c.Tracks.Add(t);
            for (int i = 0; i < frames.Length; i++)
            {
                var f = frames[i]; var pivot = f.GetProperty("pivot"); float scale = 140 / d.GetProperty("sourceHeight").GetSingle();
                t.Keys.Add(new() { Frame = i, Pose = new() { PivotX = pivot[0].GetSingle(), PivotY = pivot[1].GetSingle(), ScaleX = f.GetProperty("flip").GetBoolean() ? -scale : scale, ScaleY = scale, SourceFrame = i } });
            }
            doc.Clips.Add(c);
        }
        ArtStudioCodec.Validate(doc); return doc;
    }
    public static void AddVfx(ArtStudioDocument doc, int skill)
    {
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        var frames = json.RootElement.GetProperty("vfx")[skill].EnumerateArray().ToArray();
        var l = new ArtStudioLayer { Id = Guid.NewGuid().ToString("N"), Name = "VFX / " + SkillVfxPlayer.Names[skill], Kind = "vfx", Texture = "res://assets/combat_v1/minh_kiem_vfx.png", Z = 20,
            Rest = new() { X = 45, Y = -75, PivotX = 104.5f, PivotY = 104.5f, ScaleX = .8f, ScaleY = .8f } };
        foreach (var f in frames) l.Regions.Add(f.GetProperty("rect").EnumerateArray().Select(n => n.GetInt32()).ToArray());
        doc.Layers.Add(l);
        foreach (var clip in doc.Clips)
            for (int i = 0; i < clip.DurationsMs.Count; i++)
            { var pose = l.Rest.Copy(); pose.SourceFrame = Math.Min(frames.Length - 1, i * frames.Length / clip.DurationsMs.Count); ArtStudioSampler.SetKey(clip, l.Id, i, pose); }
    }
}
