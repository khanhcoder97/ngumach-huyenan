using Godot;
namespace Ngumach.VisualReboot;

/// <summary>World-only camera. A CanvasLayer keeps the HUD independent of zoom.
/// This 2D camera never tilts or rotates; overhead perspective belongs to the art.</summary>
public partial class TopDownCamera : Camera2D
{
    public const float PixelsPerWorldUnit = 20f;
    public static readonly Vector2 WideWorldSize = new(64, 36);
    public static readonly Vector2 CompactWorldSize = new(48, 27);
    private Vector2 _mapPixels;
    private Vector2 _mapOrigin;
    private Vector2 _worldView = WideWorldSize;
    public Vector2 VisibleWorldSize => _worldView;
    public bool Compact => _worldView == CompactWorldSize;

    public void Configure(Vector2 mapPixels)
    {
        _mapPixels = mapPixels;
        _mapOrigin=Vector2.Zero;
        PositionSmoothingEnabled = false;
        Rotation = 0;
        IgnoreRotation = true;
        Enabled = true;
        SetCompact(false);
    }

    public void ConfigureBounds(Rect2 bounds)
    {
        Configure(bounds.Size);_mapOrigin=bounds.Position;
    }

    public void SetCompact(bool compact)
    {
        _worldView = compact ? CompactWorldSize : WideWorldSize;
        // The root viewport is fixed 1280x720; keep 16:9 on every device.
        Zoom = new Vector2(1280f / (_worldView.X * PixelsPerWorldUnit),
                           720f / (_worldView.Y * PixelsPerWorldUnit));
    }

    public Vector2 Constrain(Vector2 target)
    {
        var half = _worldView * PixelsPerWorldUnit / 2;
        float Axis(float value, float extent, float margin) =>
            extent <= margin * 2 ? extent / 2 : Mathf.Clamp(value, margin, extent - margin);
        return new Vector2(Mathf.Round(Axis(target.X-_mapOrigin.X, _mapPixels.X, half.X)+_mapOrigin.X),
                           Mathf.Round(Axis(target.Y-_mapOrigin.Y, _mapPixels.Y, half.Y)+_mapOrigin.Y));
    }

    public void Follow(Vector2 target) => GlobalPosition = Constrain(target);
}
