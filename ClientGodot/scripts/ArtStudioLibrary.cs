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
        using var library = new ActorLibraryData(reviewMode: true);
        var grouped = library.Actors.Values.Where(a => a.Kind != "VFX").SelectMany(a => a.Clips.Where(c => Enumerable.Range(0, 8).Any(i => library.Resolve(a.Id, c, i, out _))).Select(c => ("actor:" + a.Id + ":" + c, "[Nhóm hướng] " + a.Name + " / " + c)));
        return new[] { ("motion:idle", "Minh Kiếm / idle"), ("motion:walk", "Minh Kiếm / walk"), ("motion:attack", "Minh Kiếm / attack"), ("motion:cast", "Minh Kiếm / cast"), ("demo:kiem_tran", "[VFX] Kiếm Trận · 3 cung / demo") }
            .Concat(grouped)
            .Concat(json.RootElement.GetProperty("pages").EnumerateArray().Where(p => p.GetProperty("file").GetString() != "")
            .Select(p => (p.GetProperty("id").GetString()!, p.GetProperty("id").GetString()!))).ToArray();
    }
    public static ArtStudioDocument Load(string id)
    {
        if (id.StartsWith("motion:", StringComparison.Ordinal)) return Motion(id[7..]);
        if (id.StartsWith("actor:", StringComparison.Ordinal)) { var parts = id.Split(':'); return Actor(parts[1], parts[2]); }
        if (id == "demo:kiem_tran") return KiemTran();
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/actor_library_v1/pages.json"));
        var p = json.RootElement.GetProperty("pages").EnumerateArray().Single(p => p.GetProperty("id").GetString() == id);
        bool vfx = id.StartsWith("sk_", StringComparison.Ordinal);
        var l = new ArtStudioLayer { Id = "sprite", Name = id, Kind = vfx ? "vfx" : "sprite", Texture = "res://assets/actor_library_v1/" + p.GetProperty("file").GetString() };
        var doc = new ArtStudioDocument { Name = id, Layers = new() { l } };
        foreach (var d in p.GetProperty("directions").EnumerateArray())
        {
            string direction = d.GetProperty("direction").GetString()!;
            float reference = d.TryGetProperty("referenceHeight", out var rh) ? rh.GetSingle() : p.GetProperty("referenceHeight").GetSingle();
            var frames = d.GetProperty("frames").EnumerateArray().ToArray();
            float width = frames.Max(f => f.GetProperty("bounds")[2].GetSingle() - f.GetProperty("bounds")[0].GetSingle());
            float scale = (vfx ? 160 : 140) / Math.Max(1, vfx ? Math.Max(width, reference) : reference); bool flip = d.GetProperty("flip").GetBoolean();
            double seconds = p.TryGetProperty("previewDurationSeconds", out var secondsJson) ? secondsJson.GetDouble() : SourceDuration(id);
            bool loop = p.TryGetProperty("previewLoop", out var loopJson) ? loopJson.GetBoolean() : !OneShot(id);
            string acceptance = p.GetProperty("productionApproved").GetBoolean() ? "Nguồn đã kiểm native; bản chỉnh Studio vẫn cần kiểm riêng." : "Nguồn chờ nghiệm thu.";
            var c = new ArtStudioClip { Name = id, Direction = direction, Loop = loop, SourceNote = (flip ? "Lật ngang theo metadata · " : "Nguồn sheet · ") + p.GetProperty("visualState").GetString() + " · " + acceptance + (p.TryGetProperty("previewDurationSeconds", out _) || p.TryGetProperty("sourceFrameDurationsMs", out _) ? " Timing xem nguồn, không phải cửa sổ gameplay." : ""), DurationsMs = p.TryGetProperty("sourceFrameDurationsMs", out var sourceTiming) ? sourceTiming.EnumerateArray().Select(n => n.GetSingle()).ToList() : Enumerable.Repeat((float)(seconds * 1000 / frames.Length), frames.Length).ToList() };
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
    private static double SourceDuration(string id)
    {
        if (id == "sk_mob_waterroot_01_ripple_component") return .7;
        string? owner = id.StartsWith("mob_carpling_", StringComparison.Ordinal) ? "MOB_CARPLING" : id.StartsWith("mob_waterroot_", StringComparison.Ordinal) ? "MOB_WATERROOT" : id.StartsWith("class_minh_kiem_", StringComparison.Ordinal) ? "CLASS_MINH_KIEM" : null;
        if (owner == null) return id.Contains("walk", StringComparison.Ordinal) ? .8 : 1.6;
        string action = id[(owner.Length+1)..];
        foreach (string facing in new[] { "_n", "_ne", "_e", "_se", "_s", "_sw", "_w", "_nw" })
            if (action.EndsWith(facing, StringComparison.Ordinal)) { action = action[..^facing.Length]; break; }
        return ActorLibraryData.Duration(owner, action);
    }
    public static ArtStudioDocument Actor(string actor, string action)
    {
        using var library = new ActorLibraryData(reviewMode: true);
        var doc = new ArtStudioDocument { Name = library.Actors[actor].Name + " / " + action + " · ghép hướng nguồn" };
        for (int i = 0; i < 8; i++)
        {
            if (!library.Resolve(actor, action, i, out var d)) continue;
            var frames = d!.Frames; string texture = frames[0].File;
            if (frames.Any(f => f.File != texture)) throw new InvalidOperationException("Một hướng phải tham chiếu một sheet trong adapter hiện tại.");
            var l = new ArtStudioLayer { Id = "dir_" + i, Name = library.Actors[actor].Name + " / " + d.Name, Kind = library.Actors[actor].Kind == "VFX" ? "vfx" : "sprite", Texture = texture };
            foreach (var f in frames) l.Regions.Add(new[] { (int)f.Region.Position.X, (int)f.Region.Position.Y, (int)f.Region.Size.X, (int)f.Region.Size.Y });
            l.Rest.Alpha = 0; doc.Layers.Add(l);
            string note = (d.Flip ? "Hướng lật · " : "Hướng nguồn · ") + library.ReviewStatus(actor, action);
            var c = new ArtStudioClip { Name = action, Direction = d.Name, Loop = !OneShot(action), SourceNote = note.Length > 480 ? note[..480] : note, DurationsMs = d.SourceFrameDurationsMs?.Select(ms => (float)ms).ToList() ?? Enumerable.Repeat((float)(ActorLibraryData.Duration(actor, action) * 1000 / frames.Length), frames.Length).ToList() };
            var t = new ArtStudioTrack { LayerId = l.Id, Interpolate = false }; c.Tracks.Add(t);
            for (int f = 0; f < frames.Length; f++)
            { float scale = 140 / Math.Max(1, d.Height); var pv = frames[f].Pivot; t.Keys.Add(new() { Frame = f, Pose = new() { SourceFrame = f, PivotX = pv.X, PivotY = pv.Y, ScaleX = d.Flip ? -scale : scale, ScaleY = scale } }); }
            doc.Clips.Add(c);
        }
        if (doc.Clips.Count == 0) throw new InvalidOperationException("Chưa có hướng nào cho action này.");
        ArtStudioCodec.Validate(doc); return doc;
    }
    private static ArtStudioDocument KiemTran()
    {
        var doc = Load("sk_mk_03_arc_component"); doc.Name = "Kiếm Trận · demo 3 cung, chưa là toàn bộ animation kỹ năng";
        var original = doc.Layers[0]; var sources = original.Regions; var basis = original.Rest.Copy();
        doc.Layers.Clear(); doc.Clips.Clear();
        // Exact visual beat boundaries .10/.22/.36 s; the underlying 16 source regions stay original.
        double[] boundaries = { 0, .02, .04, .06, .08, .10, .12, .14, .16, .18, .20, .22, .24, .26, .28, .30, .32, .36, .40, .44, .46 };
        var c = new ArtStudioClip { Name = "kiem_tran_vfx_demo", Direction = "OMNI", Loop = false, SourceNote = "3 lần dùng cùng thành phần cung 16 ảnh; 20 ô timing không phải 20 pose nhân vật mới.", DurationsMs = boundaries.Zip(boundaries.Skip(1), (a, b) => (float)((b - a) * 1000)).ToList() };
        double[] starts = { 0, .12, .26 }; float[] angles = { 0, -35, 35 };
        for (int i = 0; i < 3; i++)
        {
            var l = new ArtStudioLayer { Id = "arc_" + i, Name = "Cung " + (i + 1), Kind = "vfx", Texture = original.Texture, Regions = sources.Select(r => r.ToArray()).ToList(), Rest = basis.Copy(), Z = i };
            l.Rest.Alpha = 0; doc.Layers.Add(l);
            var t = new ArtStudioTrack { LayerId = l.Id, Interpolate = false }; c.Tracks.Add(t);
            for (int f = 0; f < c.DurationsMs.Count; f++)
            { double local = boundaries[f] - starts[i]; var p = basis.Copy(); p.X = 0; p.Y = -70; p.Angle = angles[i]; p.ScaleX *= i == 2 ? 1.25f : 1; p.ScaleY *= i == 2 ? 1.25f : 1; p.Alpha = local >= -.00001 && local < .20 ? 1 : 0; p.SourceFrame = Math.Clamp((int)(Math.Max(0, local) / .20 * 16), 0, 15); t.Keys.Add(new() { Frame = f, Pose = p }); }
        }
        doc.Clips.Add(c); ArtStudioCodec.Validate(doc); return doc;
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
            var c = new ArtStudioClip { Name = action, Direction = ArtStudioCodec.Directions[di], Loop = !OneShot(action), SourceNote = frames[0].GetProperty("flip").GetBoolean() ? "Nguồn lật ngang theo metadata motion16." : "Minh Kiếm / bộ motion16 có sẵn, crop và pivot nguồn được giữ.", DurationsMs = Enumerable.Repeat(d.GetProperty("duration").GetSingle() * 1000 / frames.Length, frames.Length).ToList() };
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
    public static (string Id, string Name)[] ComponentEntries()
    {
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/actor_library_v1/pages.json"));
        return json.RootElement.GetProperty("pages").EnumerateArray()
            .Where(p => p.GetProperty("id").GetString()!.StartsWith("sk_", StringComparison.Ordinal) && p.GetProperty("id").GetString()!.EndsWith("_component", StringComparison.Ordinal))
            .Select(p => (p.GetProperty("id").GetString()!, p.GetProperty("id").GetString()! + " · " + p.GetProperty("visualState").GetString())).ToArray();
    }
    public static void AddComponent(ArtStudioDocument doc, string id)
    {
        if (!ComponentEntries().Any(e => e.Id == id)) throw new InvalidOperationException("Chọn component VFX trong thư viện nguồn.");
        // Keep all original regions, pivots and source order. This is a manual
        // placement starting point, not a complete skill or combat event binding.
        var source = Load(id); var original = source.Layers.Single(); var sequence = source.Clips.Single();
        if (sequence.DurationsMs.Count != 16) throw new InvalidOperationException("Component cần đủ 16 khung nguồn.");
        if (doc.Clips.Any(c => c.DurationsMs.Count < 16)) throw new InvalidOperationException("Timeline cần ít nhất 16 ô để không bỏ khung component.");
        var layer = new ArtStudioLayer { Id = Guid.NewGuid().ToString("N"), Name = "Component / " + id, Kind = "vfx", Texture = original.Texture,
            Regions = original.Regions.Select(r => r.ToArray()).ToList(), Z = 20, Rest = original.Rest.Copy() };
        layer.Rest.Alpha = 0; doc.Layers.Add(layer);
        foreach (var clip in doc.Clips)
        {
            for (int frame = 0; frame < clip.DurationsMs.Count; frame++)
            {
                int sourceFrame = Math.Min(15, frame * 16 / clip.DurationsMs.Count);
                var pose = ArtStudioSampler.Pose(original, sequence, sourceFrame).Copy();
                pose.X = 45; pose.Y = -75; pose.ScaleX *= .5f; pose.ScaleY *= .5f;
                ArtStudioSampler.SetKey(clip, layer.Id, frame, pose);
            }
            clip.SourceNote += " Component nguồn trải đều trên timeline để chỉnh tay; timing/lớp/vị trí chưa gắn sự kiện gameplay.";
        }
        ArtStudioCodec.Validate(doc);
    }
    private static bool OneShot(string id) => id == "turn" || id.Contains("_turn_", StringComparison.Ordinal) || new[] { "death", "hurt", "dodge", "attack", "cast", "skill_", "telegraph", "recovery", "interact", "arc_component", "crack_component", "ripple_component" }.Any(t => id.Contains(t, StringComparison.Ordinal));
}
