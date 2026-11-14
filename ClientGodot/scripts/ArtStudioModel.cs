using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.IO;
using System.Security.Cryptography;
using GFile = Godot.FileAccess;

namespace Ngumach.VisualReboot;

/// <summary>Versioned presentation authoring format. Never grants equipment or applies combat events.</summary>
public sealed class ArtStudioDocument
{
    public int SchemaVersion { get; set; } = 1;
    public string Scope { get; set; } = "PRESENTATION_AUTHORING_ONLY";
    public string Name { get; set; } = "Nhân vật mới";
    public bool ProductionApproved { get; set; }
    public List<ArtStudioLayer> Layers { get; set; } = new();
    public List<ArtStudioSocket> Sockets { get; set; } = new();
    public List<ArtStudioClip> Clips { get; set; } = new();
}
public sealed class ArtStudioPose
{
    public float X { get; set; }
    public float Y { get; set; }
    public float PivotX { get; set; }
    public float PivotY { get; set; }
    public float ScaleX { get; set; } = 1;
    public float ScaleY { get; set; } = 1;
    public float Angle { get; set; }
    public float Alpha { get; set; } = 1;
    public int SourceFrame { get; set; }
    public ArtStudioPose Copy() => (ArtStudioPose)MemberwiseClone();
    public Transform2D Transform => new Transform2D(Mathf.DegToRad(Angle), new Vector2(ScaleX, ScaleY), 0, new Vector2(X, Y));
}
public sealed class ArtStudioLayer
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N");
    public string Name { get; set; } = "Layer";
    public string Kind { get; set; } = "sprite";
    public string Texture { get; set; } = "";
    public List<int[]> Regions { get; set; } = new();
    public ArtStudioPose Rest { get; set; } = new();
    public string AttachSocket { get; set; } = "";
    public int Z { get; set; }
    public bool Visible { get; set; } = true;
    public bool Locked { get; set; }
}
public sealed class ArtStudioSocket
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N");
    public string Name { get; set; } = "hand_r";
    public string LayerId { get; set; } = "";
    // Coordinates in the source region, BEFORE subtracting its pivot. Empty LayerId means actor space.
    public float X { get; set; }
    public float Y { get; set; }
}
public sealed class ArtStudioKey
{
    public int Frame { get; set; }
    public ArtStudioPose Pose { get; set; } = new();
}
public sealed class ArtStudioTrack
{
    public string LayerId { get; set; } = "";
    public bool Interpolate { get; set; } = true;
    public List<ArtStudioKey> Keys { get; set; } = new();
}
public sealed class ArtStudioMarker
{
    public string Name { get; set; } = "footstep";
    public string Kind { get; set; } = "sfx";
    public int Frame { get; set; }
    public float X { get; set; }
    public float Y { get; set; }
    public float Radius { get; set; } = 12;
}
public sealed class ArtStudioClip
{
    public string Name { get; set; } = "idle";
    public string Direction { get; set; } = "S";
    public string SourceNote { get; set; } = "Nguồn nhập tay; cần nghiệm thu pose và góc nhìn.";
    public bool Loop { get; set; } = true;
    public List<float> DurationsMs { get; set; } = Enumerable.Repeat(62.5f, 16).ToList();
    public List<ArtStudioTrack> Tracks { get; set; } = new();
    public List<ArtStudioMarker> Markers { get; set; } = new();
    public double Duration => DurationsMs.Sum(x => (double)x) / 1000;
}

public static class ArtStudioCodec
{
    public static readonly string[] Directions = { "N", "NE", "E", "SE", "S", "SW", "W", "NW", "OMNI" };
    private static readonly JsonSerializerOptions Json = new() { WriteIndented = true, PropertyNameCaseInsensitive = true };
    public static string Encode(ArtStudioDocument doc) => JsonSerializer.Serialize(doc, Json);
    public static ArtStudioDocument Decode(string text)
    {
        if (text.Length > 4_000_000) throw new InvalidDataException("Project quá lớn (tối đa 4 MB JSON).");
        var doc = JsonSerializer.Deserialize<ArtStudioDocument>(text, Json) ?? throw new InvalidDataException("Project rỗng.");
        Validate(doc); return doc;
    }
    public static void Validate(ArtStudioDocument d)
    {
        void Need(bool ok, string why) { if (!ok) throw new InvalidDataException(why); }
        bool Fin(float n) => float.IsFinite(n) && Math.Abs(n) <= 100000;
        void Pose(ArtStudioPose p, int sources)
        {
            Need(p != null && new[] { p.X, p.Y, p.PivotX, p.PivotY, p.Angle, p.ScaleX, p.ScaleY, p.Alpha }.All(Fin), "Pose không hữu hạn.");
            Need(Math.Abs(p!.ScaleX) >= .001f && Math.Abs(p.ScaleY) >= .001f && Math.Abs(p.ScaleX) <= 100 && Math.Abs(p.ScaleY) <= 100 && p.Alpha >= 0 && p.Alpha <= 1, "Scale/alpha ngoài phạm vi.");
            Need(p.SourceFrame >= 0 && p.SourceFrame < sources, "Chỉ số ảnh nguồn ngoài sheet.");
        }
        Need(d.SchemaVersion == 1 && d.Scope == "PRESENTATION_AUTHORING_ONLY" && !d.ProductionApproved, "Không phải project authoring v1 / không được tự phê duyệt production.");
        Need(d.Name != null && d.Name.Length <= 120 && d.Layers != null && d.Clips != null && d.Sockets != null, "Thiếu dữ liệu project.");
        if (d.Layers is null || d.Clips is null || d.Sockets is null) throw new InvalidDataException("Thiếu danh sách layer/clip/socket.");
        Need(d.Layers!.Count is > 0 and <= 64 && d.Clips!.Count is > 0 and <= 64 && d.Sockets!.Count <= 128, "Quá giới hạn 64 layer / 64 clip / 128 socket.");
        Need(d.Layers.Select(l => l.Id).Distinct().Count() == d.Layers.Count && d.Sockets.Select(s => s.Id).Distinct().Count() == d.Sockets.Count, "ID trùng.");
        foreach (var l in d.Layers)
        {
            Need(!string.IsNullOrWhiteSpace(l.Id) && l.Name?.Length <= 120 && l.Kind is "sprite" or "vfx", "Layer không hợp lệ.");
            Need(ValidTexturePath(l.Texture), "Texture phải là PNG trong assets/imports/bundle, không được thoát thư mục.");
            Need(l.Regions != null && l.Regions.Count is > 0 and <= 512 && l.Regions.All(r => r is { Length: 4 } && r[0] >= 0 && r[1] >= 0 && r[2] > 0 && r[3] > 0 && (long)r[0] + r[2] <= 16384 && (long)r[1] + r[3] <= 16384), "Vùng ảnh sai.");
            Need(l.Z is >= -1000 and <= 1000 && l.AttachSocket != null, "Thứ tự layer sai.");
            Pose(l.Rest, l.Regions!.Count);
            Need(l.AttachSocket == "" || d.Sockets.Any(s => s.Id == l.AttachSocket), "Socket gắn layer không tồn tại.");
        }
        foreach (var s in d.Sockets)
            Need(s.Name?.Length <= 120 && Fin(s.X) && Fin(s.Y) && (s.LayerId == "" || d.Layers.Any(l => l.Id == s.LayerId)), "Socket không hợp lệ.");
        foreach (var l in d.Layers)
        {
            var seen = new HashSet<string>(); var at = l;
            while (at.AttachSocket != "")
            {
                Need(seen.Add(at.Id), "Chu trình layer/socket.");
                string host = d.Sockets.Single(s => s.Id == at.AttachSocket).LayerId;
                if (host == "") break;
                at = d.Layers.Single(x => x.Id == host);
            }
        }
        Need(d.Clips.Select(c => c.Name + "/" + c.Direction).Distinct().Count() == d.Clips.Count, "Tên clip/hướng trùng.");
        foreach (var c in d.Clips)
        {
            Need(!string.IsNullOrWhiteSpace(c.Name) && c.Name.Length <= 80 && Directions.Contains(c.Direction) && c.SourceNote != null && c.SourceNote.Length <= 500, "Tên clip/hướng sai.");
            Need(c.DurationsMs != null && c.DurationsMs.Count is >= 1 and <= 120 && c.DurationsMs.All(n => Fin(n) && n >= 5 && n <= 10000), "Timeline: 1–120 frame, 5–10000 ms/frame.");
            Need(c.Tracks != null && c.Markers != null && c.Tracks.Count <= d.Layers.Count && c.Markers.Count <= 256 && c.Tracks.Select(t => t.LayerId).Distinct().Count() == c.Tracks.Count, "Track/mốc trùng hoặc quá nhiều.");
            foreach (var t in c.Tracks!)
            {
                var l = d.Layers.SingleOrDefault(l => l.Id == t.LayerId); Need(l != null, "Track tham chiếu layer đã xóa.");
                Need(t.Keys != null && t.Keys.Count <= c.DurationsMs!.Count && t.Keys.Select(k => k.Frame).Distinct().Count() == t.Keys.Count, "Keyframe trùng.");
                foreach (var k in t.Keys!) { Need(k.Frame >= 0 && k.Frame < c.DurationsMs!.Count, "Key ngoài timeline."); Pose(k.Pose, l!.Regions.Count); }
            }
            foreach (var m in c.Markers!) Need(m.Name?.Length <= 120 && m.Kind is "sfx" or "hitbox" or "vfx" or "footstep" && m.Frame >= 0 && m.Frame < c.DurationsMs!.Count && Fin(m.X) && Fin(m.Y) && Fin(m.Radius) && m.Radius >= 0 && m.Radius <= 10000, "Mốc preview không hợp lệ.");
        }
    }
    public static bool ValidTexturePath(string p) => !string.IsNullOrWhiteSpace(p) && !p.Contains("..", StringComparison.Ordinal) && !p.Contains('\\') && !p.Contains('%') && p.EndsWith(".png", StringComparison.OrdinalIgnoreCase) &&
        (p.StartsWith("res://assets/", StringComparison.Ordinal) || p.StartsWith("user://art_studio/imports/", StringComparison.Ordinal) || (p.StartsWith("textures/", StringComparison.Ordinal) && !p.Contains(':')));
    public static string Resolve(string p, string root)
    {
        if (!ValidTexturePath(p)) throw new InvalidDataException("Texture path không hợp lệ.");
        if (p.StartsWith("res://", StringComparison.Ordinal) || p.StartsWith("user://", StringComparison.Ordinal)) return ProjectSettings.GlobalizePath(p);
        if (root == "") throw new InvalidDataException("Bundle chưa có thư mục gốc.");
        return Path.Combine(root, p.Replace('/', Path.DirectorySeparatorChar));
    }
    public static Texture2D Texture(string p, string root)
    {
        string abs = Resolve(p, root);
        var info = new FileInfo(abs); if (!info.Exists || info.Length > 64_000_000) throw new InvalidDataException("PNG thiếu hoặc lớn hơn 64 MB.");
        // Godot's decoder owns bitmap loading; pixels are not generated or rewritten here.
        var image = Image.LoadFromFile(abs);
        if (image == null || image.IsEmpty() || image.GetWidth() > 8192 || image.GetHeight() > 8192) throw new InvalidDataException("PNG lỗi hoặc vượt 8192 px.");
        var texture = ImageTexture.CreateFromImage(image); image.Dispose(); return texture;
    }
    public static void ValidateTextures(ArtStudioDocument doc, string root)
    {
        foreach (var group in doc.Layers.GroupBy(l => l.Texture))
        {
            using var texture = Texture(group.Key, root);
            foreach (var l in group) foreach (var r in l.Regions)
                if ((long)r[0] + r[2] > texture.GetWidth() || (long)r[1] + r[3] > texture.GetHeight()) throw new InvalidDataException("Crop ngoài ảnh: " + l.Name);
        }
    }
    public static void SaveAtomic(string path, ArtStudioDocument doc)
    {
        Validate(doc); string absolute = path.Contains("://", StringComparison.Ordinal) ? ProjectSettings.GlobalizePath(path) : Path.GetFullPath(path);
        Directory.CreateDirectory(Path.GetDirectoryName(absolute)!);
        string temp = absolute + ".writing";
        File.WriteAllText(temp, Encode(doc) + "\n");
        if (File.Exists(absolute)) File.Copy(absolute, absolute + ".bak", true);
        File.Move(temp, absolute, true);
    }
    public static string ImportPng(string path)
    {
        var info = new FileInfo(path); if (!info.Exists || info.Length > 64_000_000 || !path.EndsWith(".png", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Chỉ nhập PNG ≤64 MB.");
        string hash = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
        string target = "user://art_studio/imports/" + hash + ".png";
        string absolute = ProjectSettings.GlobalizePath(target); Directory.CreateDirectory(Path.GetDirectoryName(absolute)!);
        if (!File.Exists(absolute)) File.Copy(path, absolute);
        using var verified = Texture(target, ""); return target;
    }
    public static void ExportBundle(string path, ArtStudioDocument doc, string sourceRoot)
    {
        Validate(doc); ValidateTextures(doc, sourceRoot);
        var exported = Decode(Encode(doc)); string root = Path.GetDirectoryName(Path.GetFullPath(path))!;
        Directory.CreateDirectory(Path.Combine(root, "textures"));
        foreach (var l in exported.Layers)
        {
            var bytes = File.ReadAllBytes(Resolve(l.Texture, sourceRoot));
            string relative = "textures/" + Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant() + ".png";
            File.WriteAllBytes(Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar)), bytes); l.Texture = relative;
        }
        SaveAtomic(path, exported);
    }
    public static string[] Readiness(ArtStudioDocument doc)
    {
        var result = new List<string> { "Bản chỉnh hình ảnh; không tự thay nhân vật gameplay hoặc chỉ số." };
        foreach (var c in doc.Clips)
        {
            if (!doc.Layers.Any(l => l.Kind == "sprite" && l.Visible))
            {
                result.Add($"{c.Name}/{c.Direction}: VFX · {c.DurationsMs.Count} ô timing; không chứa pose nhân vật.");
                foreach (var l in doc.Layers.Where(l => l.Kind == "vfx" && l.Visible))
                { int used = Enumerable.Range(0, c.DurationsMs.Count).Select(f => ArtStudioSampler.Pose(l, c, f).SourceFrame).Distinct().Count(); result.Add($"{l.Name}: {l.Regions.Count} vùng ảnh nguồn; timeline tham chiếu {used} vùng. Dùng lại nguồn không tạo thêm ảnh mới."); }
                continue;
            }
            int unique = doc.Layers.Where(l => l.Kind == "sprite" && l.Visible).Select(l =>
                Enumerable.Range(0, c.DurationsMs.Count).Select(f => ArtStudioSampler.Pose(l, c, f).SourceFrame).Distinct().Count()).DefaultIfEmpty(0).Max();
            result.Add($"{c.Name}/{c.Direction}: {c.DurationsMs.Count} ô timeline · {unique} vùng ảnh sprite được dùng (chưa kiểm chứng pose khác nhau).");
            if (c.DurationsMs.Count < 16 || c.DurationsMs.Count > 20 || unique < 16) result.Add("Chưa đạt yêu cầu 16–20 pose vẽ thực/hành động/hướng. Nội suy transform không tạo thêm pose nguồn.");
        }
        result.Add("Hướng có dữ liệu: " + string.Join(", ", doc.Clips.Select(c => c.Direction).Distinct()) + ". Không tự sinh hướng còn thiếu.");
        return result.ToArray();
    }
}

/// <summary>Shared sampler for editor and exported bundles. Time in seconds, Y positive down.</summary>
public static class ArtStudioSampler
{
    public static int MarkerCrossings(ArtStudioClip c, ArtStudioMarker m, double previous, double next)
    {
        double at = TimeAt(c, m.Frame);
        return c.Loop ? (int)Math.Floor((next - at) / c.Duration) - (int)Math.Floor((previous - at) / c.Duration) : previous < at && next >= at ? 1 : 0;
    }
    public static int FrameAt(ArtStudioClip c, double seconds)
    {
        double ms = c.Loop ? ((seconds % c.Duration + c.Duration) % c.Duration) * 1000 : Math.Clamp(seconds, 0, c.Duration) * 1000;
        for (int i = 0; i < c.DurationsMs.Count; i++) { if (ms < c.DurationsMs[i]) return i; ms -= c.DurationsMs[i]; }
        return c.DurationsMs.Count - 1;
    }
    public static double TimeAt(ArtStudioClip c, int frame) => c.DurationsMs.Take(frame).Sum(x => (double)x) / 1000;
    public static ArtStudioPose Pose(ArtStudioLayer l, ArtStudioClip c, double frame)
    {
        var t = c.Tracks.FirstOrDefault(t => t.LayerId == l.Id); if (t == null || t.Keys.Count == 0) return l.Rest.Copy();
        var before = t.Keys.Where(k => k.Frame <= frame).OrderBy(k => k.Frame).LastOrDefault();
        if (before == null) return l.Rest.Copy();
        var after = t.Keys.Where(k => k.Frame > frame).OrderBy(k => k.Frame).FirstOrDefault();
        if (!t.Interpolate || after == null) return before.Pose.Copy();
        float a = (float)((frame - before.Frame) / (after.Frame - before.Frame)); var p = before.Pose; var q = after.Pose;
        return new ArtStudioPose { X = Mathf.Lerp(p.X, q.X, a), Y = Mathf.Lerp(p.Y, q.Y, a), PivotX = Mathf.Lerp(p.PivotX, q.PivotX, a), PivotY = Mathf.Lerp(p.PivotY, q.PivotY, a),
            ScaleX = Math.Sign(p.ScaleX) == Math.Sign(q.ScaleX) ? Mathf.Lerp(p.ScaleX, q.ScaleX, a) : p.ScaleX, ScaleY = Math.Sign(p.ScaleY) == Math.Sign(q.ScaleY) ? Mathf.Lerp(p.ScaleY, q.ScaleY, a) : p.ScaleY, Angle = p.Angle + Mathf.RadToDeg(Mathf.AngleDifference(Mathf.DegToRad(p.Angle), Mathf.DegToRad(q.Angle))) * a,
            Alpha = Mathf.Lerp(p.Alpha, q.Alpha, a), SourceFrame = p.SourceFrame };
    }
    public static float FractionalFrame(ArtStudioClip c, double time)
    {
        int f = FrameAt(c, time); double local = c.Loop ? ((time % c.Duration + c.Duration) % c.Duration) : Math.Clamp(time, 0, c.Duration);
        return f + (float)Math.Clamp((local - TimeAt(c, f)) * 1000 / c.DurationsMs[f], 0, .999999);
    }
    public static Transform2D Transform(ArtStudioDocument d, ArtStudioClip c, ArtStudioLayer l, double frame, int depth = 0)
    {
        if (depth > 64) throw new InvalidDataException("Socket cycle.");
        var pose = Pose(l, c, frame); var own = pose.Transform;
        if (l.AttachSocket == "") return own;
        var socket = d.Sockets.Single(s => s.Id == l.AttachSocket);
        var parent = Transform2D.Identity; Vector2 pos = new(socket.X, socket.Y);
        if (socket.LayerId != "")
        {
            var host = d.Layers.Single(x => x.Id == socket.LayerId); var hp = Pose(host, c, frame);
            parent = Transform(d, c, host, frame, depth + 1); pos -= new Vector2(hp.PivotX, hp.PivotY);
        }
        return parent * new Transform2D(0, pos) * own;
    }
    public static Vector2 SocketPoint(ArtStudioDocument d, ArtStudioClip c, ArtStudioSocket s, double frame)
    {
        if (s.LayerId == "") return new(s.X, s.Y);
        var l = d.Layers.Single(x => x.Id == s.LayerId); var p = Pose(l, c, frame);
        return Transform(d, c, l, frame) * new Vector2(s.X - p.PivotX, s.Y - p.PivotY);
    }
    public static void SetKey(ArtStudioClip c, string id, int frame, ArtStudioPose pose)
    {
        var track = c.Tracks.FirstOrDefault(t => t.LayerId == id);
        if (track == null) { track = new() { LayerId = id }; c.Tracks.Add(track); }
        track.Keys.RemoveAll(k => k.Frame == frame); track.Keys.Add(new() { Frame = frame, Pose = pose.Copy() }); track.Keys.Sort((a, b) => a.Frame.CompareTo(b.Frame));
    }
    public static void Resize(ArtStudioClip c, int count)
    {
        float ms = c.DurationsMs.Last(); while (c.DurationsMs.Count < count) c.DurationsMs.Add(ms);
        if (c.DurationsMs.Count > count) c.DurationsMs.RemoveRange(count, c.DurationsMs.Count - count);
        foreach (var t in c.Tracks) t.Keys.RemoveAll(k => k.Frame >= count); c.Markers.RemoveAll(m => m.Frame >= count);
    }
}
