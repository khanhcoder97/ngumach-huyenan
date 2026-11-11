using Godot;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Ngumach.VisualReboot;

/// <summary>Renders original PNGs only. Gizmos and geometry are editor guides, not substitute artwork.</summary>
public partial class ArtStudioCanvas : Control
{
    public ArtStudioDocument Document { get; set; } = null!;
    public int ClipIndex { get; set; }
    public string SelectedId { get; set; } = "";
    public int SelectedSocket { get; set; }
    public int SelectedMarker { get; set; }
    public double Frame { get; set; }
    public string SourceRoot { get; set; } = "";
    public string Tool { get; set; } = "move";
    public bool Guides { get; set; } = true;
    public bool Onion { get; set; }
    public bool Light { get; set; } = true;
    public bool Nearest { get; set; } = true;
    public float Zoom { get; set; } = 1;
    public Vector2 Pan { get; set; }
    public Action? BeginEdit { get; set; }
    public Action<Vector2, bool>? DragEdit { get; set; }
    public Action? EndEdit { get; set; }
    public Action? ViewChanged { get; set; }
    private Vector2 _last;
    private bool _drag, _pan;
    private readonly Dictionary<string, Texture2D> _textures = new();
    public Vector2 Origin => new Vector2(Size.X / 2, Size.Y * .86f) + Pan;
    public Transform2D View => new Transform2D(0, Vector2.One * Zoom, 0, Origin);
    public ArtStudioClip Clip => Document.Clips[ClipIndex];
    public override void _Ready() { ClipContents = true; MouseDefaultCursorShape = CursorShape.Cross; }
    public void ClearTextures() { foreach (var t in _textures.Values) t.Dispose(); _textures.Clear(); }
    public void FitContent()
    {
        if (Document == null || Size.X < 40 || Size.Y < 40) return;
        Rect2 bounds = default; bool first = true;
        foreach (var l in Document.Layers.Where(l => l.Visible))
        {
            var p = ArtStudioSampler.Pose(l, Clip, Frame); if (p.Alpha <= 0) continue;
            var r = l.Regions[p.SourceFrame]; var t = ArtStudioSampler.Transform(Document, Clip, l, Frame);
            var corner = -new Vector2(p.PivotX, p.PivotY);
            foreach (var point in new[] { corner, corner + new Vector2(r[2], 0), corner + new Vector2(r[2], r[3]), corner + new Vector2(0, r[3]) })
            { Vector2 world = t * point; if (first) { bounds = new Rect2(world, Vector2.Zero); first = false; } else bounds = bounds.Expand(world); }
        }
        if (first || bounds.Size.X <= 0 || bounds.Size.Y <= 0) return;
        Zoom = Math.Clamp(Math.Min((Size.X - 30) / bounds.Size.X, (Size.Y - 30) / bounds.Size.Y), .1f, 8);
        Pan = Size / 2 - new Vector2(Size.X / 2, Size.Y * .86f) - bounds.GetCenter() * Zoom; QueueRedraw();
    }
    public Texture2D SourceTexture(string file)
    {
        if (!_textures.TryGetValue(file, out var texture)) { texture = ArtStudioCodec.Texture(file, SourceRoot); _textures.Add(file, texture); }
        return texture;
    }
    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), Color.FromHtml(Light ? "#dce4eb" : "#272d46"));
        if (Document == null) return;
        TextureFilter = Nearest ? TextureFilterEnum.Nearest : TextureFilterEnum.Linear;
        if (Guides)
        {
            const int gap = 24;
            var grid = new Color(.32f, .4f, .55f, .13f);
            for (float x = Origin.X % (gap * Zoom); x < Size.X; x += gap * Zoom) DrawLine(new(x, 0), new(x, Size.Y), grid);
            for (float y = Origin.Y % (gap * Zoom); y < Size.Y; y += gap * Zoom) DrawLine(new(0, y), new(Size.X, y), grid);
            DrawLine(new(0, Origin.Y), new(Size.X, Origin.Y), new Color(.2f, .6f, .6f, .6f));
            DrawLine(new(Origin.X, 0), new(Origin.X, Size.Y), new Color(.3f, .4f, .8f, .5f));
        }
        try
        {
            if (Onion)
            {
                DrawLayers(Math.Max(0, (int)Frame - 1), new Color(.4f, .6f, 1, .18f));
                DrawLayers(Math.Min(Clip.DurationsMs.Count - 1, (int)Frame + 1), new Color(1, .5f, .4f, .18f));
            }
            DrawLayers(Frame, Colors.White);
            DrawSetTransformMatrix(Transform2D.Identity);
            if (!Guides) return;
            foreach (var s in Document.Sockets)
            {
                Vector2 p = View * ArtStudioSampler.SocketPoint(Document, Clip, s, Frame);
                Cross(p, MoonGlassTheme.Blue); DrawString(ThemeDB.FallbackFont, p + new Vector2(8, -7), s.Name, fontSize: 12, modulate: Color.FromHtml("#285a91"));
            }
            foreach (var m in Clip.Markers.Where(m => m.Frame == (int)Frame))
            {
                Vector2 p = View * new Vector2(m.X, m.Y); DrawArc(p, m.Radius * Zoom, 0, Mathf.Tau, 48, m.Kind == "hitbox" ? Colors.IndianRed : Colors.MediumPurple, 2);
                Cross(p, Colors.MediumPurple); DrawString(ThemeDB.FallbackFont, p + new Vector2(8, 14), m.Kind + ": " + m.Name, fontSize: 12, modulate: Color.FromHtml("#563f87"));
            }
            var selected = Document.Layers.FirstOrDefault(l => l.Id == SelectedId);
            if (selected != null && selected.Visible)
            {
                var pose = ArtStudioSampler.Pose(selected, Clip, Frame); var r = selected.Regions[pose.SourceFrame];
                var transform = View * ArtStudioSampler.Transform(Document, Clip, selected, Frame);
                Vector2 corner = -new Vector2(pose.PivotX, pose.PivotY);
                var box = new[] { corner, corner + new Vector2(r[2], 0), corner + new Vector2(r[2], r[3]), corner + new Vector2(0, r[3]), corner };
                for (int i = 1; i < box.Length; i++) DrawLine(transform * box[i - 1], transform * box[i], Color.FromHtml("#8b76bd"), 1);
                Cross(transform * Vector2.Zero, Color.FromHtml("#c06a38"));
            }
        }
        catch (Exception e)
        { DrawSetTransformMatrix(Transform2D.Identity); DrawString(ThemeDB.FallbackFont, new Vector2(15, 30), "Ảnh không đọc được: " + e.Message, fontSize: 14, modulate: Colors.IndianRed); }
    }
    private void DrawLayers(double frame, Color tint)
    {
        foreach (var l in Document.Layers.Where(l => l.Visible).OrderBy(l => l.Z))
        {
            var p = ArtStudioSampler.Pose(l, Clip, frame); var r = l.Regions[p.SourceFrame];
            DrawSetTransformMatrix(View * ArtStudioSampler.Transform(Document, Clip, l, frame));
            DrawTextureRectRegion(SourceTexture(l.Texture), new Rect2(-new Vector2(p.PivotX, p.PivotY), new Vector2(r[2], r[3])), new Rect2(r[0], r[1], r[2], r[3]), tint * new Color(1, 1, 1, p.Alpha));
        }
    }
    private void Cross(Vector2 p, Color color)
    { DrawLine(p - new Vector2(6, 0), p + new Vector2(6, 0), color, 2); DrawLine(p - new Vector2(0, 6), p + new Vector2(0, 6), color, 2); DrawCircle(p, 3, color); }
    public override void _GuiInput(InputEvent e)
    {
        if (e is InputEventMouseButton b)
        {
            if (b.Pressed && b.ButtonIndex is MouseButton.WheelUp or MouseButton.WheelDown)
            {
                Vector2 world = View.AffineInverse() * b.Position; Zoom = Math.Clamp(Zoom * (b.ButtonIndex == MouseButton.WheelUp ? 1.1f : 1 / 1.1f), .1f, 8);
                Pan += b.Position - View * world; QueueRedraw(); ViewChanged?.Invoke(); AcceptEvent();
            }
            if (b.ButtonIndex == MouseButton.Middle) { _pan = b.Pressed; _last = b.Position; AcceptEvent(); }
            if (b.ButtonIndex == MouseButton.Left)
            {
                if (b.Pressed) { _drag = true; _last = b.Position; BeginEdit?.Invoke(); }
                else if (_drag) { _drag = false; EndEdit?.Invoke(); }
                AcceptEvent();
            }
        }
        if (e is InputEventMouseMotion m)
        {
            if (_pan) { Pan += m.Position - _last; QueueRedraw(); }
            else if (_drag) DragEdit?.Invoke((m.Position - _last) / Zoom, m.CtrlPressed);
            _last = m.Position;
        }
    }
    public override void _ExitTree() => ClearTextures();
}
