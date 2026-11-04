using Godot;
namespace Ngumach.VisualReboot;

/// <summary>Live code-drawn staging HUD; no baked image labels or old Muse UI.</summary>
public partial class PreviewHud : Node2D
{
    public Vector2 Coordinates;
    public static Vector2 AttackCenter => new(1172,624);
    public static Vector2[] SkillCenters()
    {
        var points = new Vector2[6];
        for(int i=0;i<6;i++){float a=Mathf.DegToRad(176+i*26);points[i]=AttackCenter+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*114;}
        return points;
    }
    public bool Compact;
    private readonly Color _panel = new(0.055f, .09f, .085f, .94f);
    private readonly Color _bronze = Color.FromHtml("#be9b53");
    private readonly Color _ink = Color.FromHtml("#e7dfbe");
    private Font _font = null!;
    public override void _Ready() { _font = ThemeDB.FallbackFont; QueueRedraw(); }
    private void Text(Vector2 at, string text, int size = 14, Color? color = null) =>
        DrawString(_font, at, text, HorizontalAlignment.Left, -1, size, color ?? _ink);
    private void Panel(Rect2 r) { DrawRect(r, _panel); DrawRect(r, _bronze, false, 2); }

    public override void _Draw()
    {
        if (_font == null) return;
        Panel(new Rect2(16,16,250,100));
        Text(new Vector2(28,38), "MINH KIẾM · BẢN THỬ HÌNH ẢNH", 14, _bronze);
        DrawRect(new Rect2(28,49,222,13), Color.FromHtml("#392c2a"));
        DrawRect(new Rect2(29,50,220,11), Color.FromHtml("#b95650"));
        Text(new Vector2(92,60), "120 / 120", 11);
        DrawRect(new Rect2(28,69,222,11), Color.FromHtml("#284342"));
        DrawRect(new Rect2(29,70,180,9), Color.FromHtml("#428fa3"));
        Text(new Vector2(28,101), "WASD / ↑↓←→  Di chuyển", 13);
        Panel(new Rect2(16,128,250,57));
        Text(new Vector2(28,151), Compact ? "Camera 48 × 27 WU" : "Camera 64 × 36 WU", 14, _bronze);
        Text(new Vector2(28,173), "F2: đổi tầm nhìn · H: ẩn HUD", 13);
        Panel(new Rect2(1108,16,156,110));
        Text(new Vector2(1120,38), "BẾN MƯA · STAGING", 12, _bronze);
        DrawRect(new Rect2(1120,49,132,38), Color.FromHtml("#4d7444"));
        DrawRect(new Rect2(1120,87,132,23), Color.FromHtml("#28675d"));
        DrawLine(new Vector2(1188,49),new Vector2(1188,87),_bronze,3);
        DrawCircle(new Vector2(1188,77),3,_ink);
        // Six slots on a constant-radius arc around the main attack circle.
        var center = AttackCenter;
        DrawCircle(center, 48, _panel);
        DrawArc(center,48,0,Mathf.Tau,48,_bronze,2);
        Text(center + new Vector2(-25,5), "ĐÁNH", 16, _bronze);
        for (int i=0;i<6;i++)
        {
            var p = SkillCenters()[i];
            DrawCircle(p, 23, _panel);
            DrawArc(p,23,0,Mathf.Tau,32,_bronze,2);
            Text(p + new Vector2(-4,5), (i+1).ToString(), 14);
        }
        Text(new Vector2(16,680), $"Vị trí {Coordinates.X:0.0}, {Coordinates.Y:0.0} · ESC: đóng", 13);
        Text(new Vector2(16,704), "THỬ CAMERA / ART · Chưa nối server · Chưa có animation đi/chém", 13, _bronze);
        DrawLine(new Vector2(16,714),new Vector2(1264,714),_bronze,2);
    }
}
