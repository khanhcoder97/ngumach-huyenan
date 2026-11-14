using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Presentation authoring only. No protocol, damage, movement or state grants.</summary>
public sealed class SkillAssemblyDocument
{
    public int SchemaVersion { get; set; } = 1;
    public string Scope { get; set; } = "PRESENTATION_ASSEMBLY_REVIEW_ONLY";
    public bool ProductionApproved { get; set; }
    public string SourcePolicy { get; set; } = "";
    public string Units { get; set; } = "";
    public string[] Sources { get; set; } = Array.Empty<string>();
    public List<SkillAssemblyProfile> Profiles { get; set; } = new();
}
public sealed class SkillAssemblyProfile
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string ActorId { get; set; } = "";
    public string BodyClip { get; set; } = "";
    public float TargetDistance { get; set; } = 110;
    public List<SkillAssemblyVariant> Variants { get; set; } = new();
}
public sealed class SkillAssemblyVariant
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public double Duration { get; set; }
    public List<SkillAssemblyTrack> Tracks { get; set; } = new();
    public double DashStart { get; set; }
    public double DashDuration { get; set; }
    public float DashDistance { get; set; }
    public string OverrideClip { get; set; } = "";
    public double OverrideStart { get; set; }
    public string Note { get; set; } = "";
}
public sealed class SkillAssemblyTrack
{
    public string Id { get; set; } = "";
    public string ComponentId { get; set; } = "";
    public double Start { get; set; }
    public double Duration { get; set; }
    public double SourceSeconds { get; set; }
    public bool Loop { get; set; }
    public string Anchor { get; set; } = "CASTER";
    public float Forward { get; set; }
    public float Side { get; set; }
    public float ScreenX { get; set; }
    public float Elevation { get; set; } = -28;
    public float Size { get; set; } = 96;
    public string Rotation { get; set; } = "FACING";
    public float Angle { get; set; }
    public int Z { get; set; } = 2;
    public bool LowFxOptional { get; set; }
    public bool ResourceInstances { get; set; }
    public float ResourceRadius { get; set; } = 34;
    public bool DepthByFacing { get; set; } = true;
}

public static class SkillAssemblyCodec
{
    public const string Source = "res://assets/actor_library_v1/skill_assemblies.json";
    private static readonly JsonSerializerOptions Json = new() { PropertyNameCaseInsensitive = true, WriteIndented = true };
    public static string Encode(SkillAssemblyDocument value) => JsonSerializer.Serialize(value, Json);
    public static SkillAssemblyDocument Decode(string text, ActorLibraryData library)
    {
        if (text.Length > 4_000_000) throw new InvalidOperationException("Assembly JSON vượt 4 MB.");
        var value = JsonSerializer.Deserialize<SkillAssemblyDocument>(text, Json) ?? throw new InvalidOperationException("Assembly JSON rỗng.");
        Validate(value, library); return value;
    }
    public static void Validate(SkillAssemblyDocument value, ActorLibraryData library)
    {
        void Need(bool yes, string why) { if (!yes) throw new InvalidOperationException(why); }
        bool Number(double n, double min, double max) => double.IsFinite(n) && n >= min && n <= max;
        Need(value.SchemaVersion == 1 && value.Scope == "PRESENTATION_ASSEMBLY_REVIEW_ONLY" && !value.ProductionApproved, "Assembly chỉ dành cho authoring, không cấp approval.");
        Need(value.Profiles is { Count: > 0 and <= 64 } && value.Profiles.Select(p => p.Id).Distinct().Count() == value.Profiles.Count, "Profile rỗng/trùng.");
        foreach (var p in value.Profiles)
        {
            Need(p.Id.Length is > 0 and <= 80 && p.Name.Length is > 0 and <= 120, "Tên profile sai.");
            Need(p.ActorId is "CLASS_MINH_KIEM" or "CLASS_ANH_DAO" && library.Actors[p.ActorId].Clips.Contains(p.BodyClip), "Body profile chưa hỗ trợ.");
            Need(Number(p.TargetDistance, 0, 300) && p.Variants is { Count: > 0 and <= 12 } && p.Variants.Select(v => v.Id).Distinct().Count() == p.Variants.Count, "Variant sai.");
            foreach (var v in p.Variants)
            {
                Need(v.Id.Length is > 0 and <= 80 && v.Name.Length is > 0 and <= 120 && v.Note.Length <= 800 && Number(v.Duration, .1, 15), "Variant ngoài giới hạn.");
                Need(Number(v.DashStart, 0, v.Duration) && Number(v.DashDuration, 0, v.Duration - v.DashStart) && Number(v.DashDistance, 0, 160) && (v.DashDistance == 0 || v.DashDuration > 0), "Đường dịch chuyển xem sai.");
                Need(v.OverrideClip == "" || library.Actors[p.ActorId].Clips.Contains(v.OverrideClip), "Clip thay thế thiếu.");
                Need(Number(v.OverrideStart, 0, v.Duration) && v.Tracks is { Count: <= 32 } && v.Tracks.Select(t => t.Id).Distinct().Count() == v.Tracks.Count, "Track trùng/quá nhiều.");
                foreach (var t in v.Tracks)
                {
                    Need(t.Id.Length is > 0 and <= 80 && t.ComponentId.StartsWith("sk_", StringComparison.Ordinal) && library.Pages.TryGetValue(t.ComponentId, out _), "Component thiếu.");
                    var page = library.Pages[t.ComponentId];
                    Need(page.Directions.Length == 1 && page.Directions[0].Name == "OMNI" && page.Directions[0].Frames.Length == 16, "Component cần 16 pose nguồn OMNI.");
                    Need(Number(t.Start, 0, v.Duration) && Number(t.Duration, .01, v.Duration - t.Start + 1e-6) && Number(t.SourceSeconds, .1, 60), "Thời gian component sai.");
                    var sourceTiming = page.Directions[0].SourceFrameDurationsMs;
                    Need(sourceTiming == null || Math.Abs(sourceTiming.Sum() / 1000 - t.SourceSeconds) < 1e-5, "Nhịp source khác metadata.");
                    Need(t.Anchor is "CASTER" or "TARGET" or "TARGET_HP" or "END" && t.Rotation is "SCREEN" or "FACING", "Anchor/rotation không hợp lệ.");
                    Need(Number(t.Forward, -300, 300) && Number(t.Side, -300, 300) && Number(t.ScreenX, -300, 300) && Number(t.Elevation, -300, 300) && Number(t.Size, 4, 300) && Number(t.Angle, -360, 360) && Number(t.ResourceRadius, 0, 120) && t.Z is >= -10 and <= 10, "Placement ngoài giới hạn.");
                }
            }
        }
    }
    public static void VerifyComponentFiles(SkillAssemblyDocument document, ActorLibraryData library)
    {
        foreach (string id in document.Profiles.SelectMany(p => p.Variants).SelectMany(v => v.Tracks).Select(t => t.ComponentId).Distinct())
        {
            var page = library.Pages[id]; string file = page.Directions[0].Frames[0].File;
            if (!file.StartsWith(ActorLibraryData.Root + "sheets/", StringComparison.Ordinal) || page.Directions[0].Frames.Any(f => f.File != file) ||
                !FileAccess.FileExists(file) || Convert.ToHexString(SHA256.HashData(FileAccess.GetFileAsBytes(file))).ToLowerInvariant() != page.SourceSha256)
                throw new InvalidOperationException("Nguồn component/hash sai: " + id);
        }
    }
}

public static class SkillAssemblySampler
{
    public static readonly Vector2[] Facings = { Vector2.Up, new Vector2(1,-1).Normalized(), Vector2.Right, new Vector2(1,1).Normalized(), Vector2.Down, new Vector2(-1,1).Normalized(), Vector2.Left, new Vector2(-1,-1).Normalized() };
    // Half-open windows remove the last fragment at the end. A loop uses its
    // own source clock; a one-shot retimes the source only within its window.
    public static int ComponentFrame(SkillAssemblyTrack track, ActorLibraryData.Direction source, double clock)
    {
        if (clock + 1e-9 < track.Start || clock + 1e-9 >= track.Start + track.Duration) return -1;
        double elapsed = Math.Max(0, clock - track.Start);
        double local = track.Loop ? elapsed % track.SourceSeconds : elapsed * track.SourceSeconds / track.Duration;
        if (track.Loop && track.SourceSeconds - local < 1e-9) local = 0;
        if (source.SourceFrameDurationsMs == null) return Math.Clamp((int)(local / track.SourceSeconds * source.Frames.Length + 1e-7), 0, source.Frames.Length - 1);
        double ms = local * 1000;
        for (int frame = 0; frame < source.Frames.Length; frame++) { if (ms + 1e-7 < source.SourceFrameDurationsMs[frame]) return frame; ms -= source.SourceFrameDurationsMs[frame]; }
        return source.Frames.Length - 1;
    }
    public static float Travel(SkillAssemblyVariant variant, double clock) => variant.DashDuration <= 0 ? 0 : variant.DashDistance * (float)Math.Clamp((clock - variant.DashStart) / variant.DashDuration, 0, 1);
    public static int Depth(SkillAssemblyTrack track, int facing) => track.DepthByFacing && track.Z > 1 && track.Anchor == "CASTER" && track.Forward > 0 && track.Rotation == "FACING" && Facings[facing].Y < -.1f ? 0 : track.Z;
    public static (string Clip, double Local) Body(SkillAssemblyProfile profile, SkillAssemblyVariant variant, double clock)
    {
        string clip = profile.BodyClip; double local = Math.Max(0, clock);
        if (variant.OverrideClip != "" && clock >= variant.OverrideStart) { clip = variant.OverrideClip; local = clock - variant.OverrideStart; }
        double duration = ActorLibraryData.Duration(profile.ActorId, clip);
        return local < duration ? (clip, local) : ("idle", (local - duration) % ActorLibraryData.Duration(profile.ActorId, "idle"));
    }
    public static Vector2 Anchor(SkillAssemblyTrack track, SkillAssemblyProfile profile, SkillAssemblyVariant variant, int facing, double clock)
    {
        Vector2 face = Facings[facing], side = new Vector2(-face.Y, face.X);
        Vector2 point = track.Anchor switch { "TARGET" or "TARGET_HP" => face * profile.TargetDistance, "END" => face * variant.DashDistance, _ => face * Travel(variant, clock) };
        return point + face * track.Forward + side * track.Side + new Vector2(track.ScreenX, track.Elevation);
    }
}
