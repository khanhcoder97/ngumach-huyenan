using Godot;
using System;
using System.Linq;

namespace Ngumach.VisualReboot;

public partial class ArtStudioTimeline : Control
{
    public ArtStudioCanvas Stage = null!;
    public Action<int>? Seek;
    private const int Cell = 45;
    public override void _Draw()
    {
        if (Stage?.Document == null) return;
        var doc = Stage.Document; var clip = Stage.Clip; var layer = doc.Layers.First(l => l.Id == Stage.SelectedId);
        var track = clip.Tracks.FirstOrDefault(t => t.LayerId == layer.Id);
        TextureFilter = TextureFilterEnum.Nearest;
        for (int f = 0; f < clip.DurationsMs.Count; f++)
        {
            var box = new Rect2(f * Cell + 1, 0, Cell - 2, 70);
            DrawRect(box, f == (int)Stage.Frame ? new Color(.4f, .38f, .64f) : new Color(.17f, .19f, .31f));
            DrawRect(box, f == (int)Stage.Frame ? MoonGlassTheme.Gold : new Color(.4f, .44f, .63f), false);
            try
            {
                var p = ArtStudioSampler.Pose(layer, clip, f); var r = layer.Regions[p.SourceFrame];
                var texture = Stage.SourceTexture(layer.Texture); float scale = Math.Min(39f / r[2], 48f / r[3]);
                Vector2 size = new(r[2] * scale, r[3] * scale); var target = new Rect2(new Vector2(f * Cell + (Cell - size.X) / 2, 3), size);
                DrawTextureRectRegion(texture, target, new Rect2(r[0], r[1], r[2], r[3]));
            }
            catch { /* The canvas already reports missing sources without crashing the editor. */ }
            DrawString(ThemeDB.FallbackFont, new Vector2(f * Cell + 5, 64), (f + 1).ToString("00"), fontSize: 11, modulate: MoonGlassTheme.Ink);
            if (track?.Keys.Any(k => k.Frame == f) == true) DrawCircle(new Vector2(f * Cell + 34, 60), 3, MoonGlassTheme.Gold);
            if (clip.Markers.Any(m => m.Frame == f)) DrawLine(new(f * Cell + 4, 3), new(f * Cell + 39, 3), MoonGlassTheme.Hp, 3);
        }
    }
    public void Refresh()
    { if (Stage?.Document != null) CustomMinimumSize = new(Stage.Clip.DurationsMs.Count * Cell, 72); QueueRedraw(); }
    public override void _GuiInput(InputEvent e)
    { if (e is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left } b) { Seek?.Invoke((int)(b.Position.X / Cell)); AcceptEvent(); } }
}
