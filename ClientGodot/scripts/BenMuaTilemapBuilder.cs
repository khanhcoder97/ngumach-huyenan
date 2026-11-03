using Godot;
using System.Collections.Generic;
using System.Text.Json;

/// <summary>
/// Runtime side of the tiledata converter (tools/convert_tiledata.py).
/// Reads the converter's tilemap.json + atlas.png and builds, in code:
///   3 visual TileMapLayers (ground -> water -> path, the handover's layer
///   order) sharing one TileSet whose atlas is the composited kit tiles, and
///   1 collision TileMapLayer whose TileSet carries a full-cell physics
///   polygon, filled ONLY from the tiledata `blocked` layer.
/// Collision is data-driven, never inferred from tile type — this strip
/// contains grass tiles that are blocked (warehouse footprint) and the
/// self-test checks exactly that case.
/// Godot mapping is direct (JSON row 0 = north = y 0) because Godot's Y
/// axis points down; the Unity import in TILEDATA_README needs y = 59 - r.
/// </summary>
public partial class BenMuaTilemapBuilder : Node
{
    [Export] public string DataPath = "res://assets/tilemap/strip_000_064/tilemap.json";
    [Export] public string AtlasPath = "res://assets/tilemap/strip_000_064/atlas.png";
    // Optional detail presentation overlays (tools/build_detail_layers.py):
    // the approved round-13 detail composite split by the blocked grid —
    // walkable-cell detail under the player, blocked-cell props over him.
    // Empty = off. Only applied when the texture size matches the map.
    [Export] public string DetailUnderPath = "";
    [Export] public string DetailOverPath = "";

    public int Cols { get; private set; }
    public int Rows { get; private set; }
    public int UniqueTiles { get; private set; }
    public Dictionary<string, int> LayerCounts { get; } = new();
    public int BlockedCount { get; private set; }

    private bool[,] _blocked;
    private TileMapLayer _ground, _water, _path, _collision;

    public TileMapLayer GroundLayer => _ground;
    public TileMapLayer CollisionLayer => _collision;
    public Sprite2D DetailUnderSprite { get; private set; }
    public Sprite2D DetailOverSprite { get; private set; }
    public bool DetailLayersActive => DetailUnderSprite != null && DetailOverSprite != null;

    public bool IsBlockedCell(int c, int r) =>
        c >= 0 && c < Cols && r >= 0 && r < Rows && _blocked[c, r];

    public override void _Ready()
    {
        string json = FileAccess.GetFileAsString(DataPath);
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        Cols = root.GetProperty("cols").GetInt32();
        Rows = root.GetProperty("rows").GetInt32();
        var tileIds = root.GetProperty("tileIds");
        UniqueTiles = tileIds.GetArrayLength();
        _blocked = new bool[Cols, Rows];

        // --- visual TileSet from the composited atlas ---
        var atlasTex = GD.Load<Texture2D>(AtlasPath);
        var atlasSource = new TileSetAtlasSource
        {
            Texture = atlasTex,
            TextureRegionSize = new Vector2I(16, 16),
        };
        var index = root.GetProperty("tileIndex");
        foreach (var prop in index.EnumerateObject())
        {
            var xy = prop.Value;
            atlasSource.CreateTile(new Vector2I(xy[0].GetInt32(), xy[1].GetInt32()));
        }
        var visualSet = new TileSet { TileSize = new Vector2I(16, 16) };
        visualSet.AddSource(atlasSource, 0);

        _ground = MakeLayer("GroundLayer", visualSet);
        _water = MakeLayer("WaterLayer", visualSet);
        _path = MakeLayer("PathLayer", visualSet);

        var cells = root.GetProperty("cells");
        FillLayer(_ground, cells.GetProperty("ground"), index);
        FillLayer(_water, cells.GetProperty("water"), index);
        FillLayer(_path, cells.GetProperty("path"), index);
        foreach (var kv in LayerCounts)
            GD.Print($"TILEMAP layer {kv.Key}: {kv.Value} cells");

        // --- collision TileSet: one transparent tile, full-cell polygon ---
        var colSet = new TileSet { TileSize = new Vector2I(16, 16) };
        colSet.AddPhysicsLayer(0);
        var blank = Image.Create(16, 16, false, Image.Format.Rgba8);
        blank.Fill(new Color(0, 0, 0, 0));
        var colSource = new TileSetAtlasSource
        {
            Texture = ImageTexture.CreateFromImage(blank),
            TextureRegionSize = new Vector2I(16, 16),
        };
        colSource.CreateTile(Vector2I.Zero);
        colSet.AddSource(colSource, 0);
        // Polygon must be set AFTER the source joins a TileSet that has a
        // physics layer, otherwise TileData reports 0 physics layers and
        // the polygon is silently dropped (caught by the collision test).
        var td = colSource.GetTileData(Vector2I.Zero, 0);
        td.SetCollisionPolygonsCount(0, 1);
        td.SetCollisionPolygonPoints(0, 0, new[]
        {
            new Vector2(-8, -8), new Vector2(8, -8),
            new Vector2(8, 8), new Vector2(-8, 8),
        });
        _collision = MakeLayer("CollisionLayer", colSet);
        GD.Print($"TILEMAP collision tile polygons: {td.GetCollisionPolygonsCount(0)}");

        int n = 0;
        foreach (var cell in root.GetProperty("blocked").EnumerateArray())
        {
            int c = cell[0].GetInt32(), r = cell[1].GetInt32();
            _blocked[c, r] = true;
            _collision.SetCell(new Vector2I(c, r), 0, Vector2I.Zero);
            n++;
        }
        BlockedCount = n;
        GD.Print($"TILEMAP built: {Cols}x{Rows}, tiles={UniqueTiles}, blocked={BlockedCount}");
        BuildDetailLayers();
    }

    /// <summary>Detail overlays sit at z 5 (above the tile layers, below
    /// the player at z 10) and z 15 (props above the player, so he passes
    /// behind houses/trees). Purely visual: collision/geometry untouched.</summary>
    private void BuildDetailLayers()
    {
        if (string.IsNullOrEmpty(DetailUnderPath) || string.IsNullOrEmpty(DetailOverPath))
            return;
        var under = GD.Load<Texture2D>(DetailUnderPath);
        var over = GD.Load<Texture2D>(DetailOverPath);
        var want = new Vector2I(Cols * 16, Rows * 16);
        if (under == null || over == null || under.GetSize() != want || over.GetSize() != want)
        {
            GD.PushWarning($"Detail layers skipped: size mismatch (want {want})");
            return;
        }
        DetailUnderSprite = MakeDetailSprite("DetailUnder", under, 5);
        DetailOverSprite = MakeDetailSprite("DetailOver", over, 15);
        GD.Print($"TILEMAP detail layers on: under z=5, over z=15 ({want.X}x{want.Y})");
    }

    private Sprite2D MakeDetailSprite(string name, Texture2D tex, int z)
    {
        var s = new Sprite2D
        {
            Name = name,
            Texture = tex,
            Centered = false,
            Position = Vector2.Zero,
            ZIndex = z,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest
        };
        AddChild(s);
        return s;
    }

    private TileMapLayer MakeLayer(string name, TileSet set)
    {
        var layer = new TileMapLayer { Name = name, TileSet = set };
        layer.TextureFilter = CanvasItem.TextureFilterEnum.Nearest;
        AddChild(layer);
        return layer;
    }

    private void FillLayer(TileMapLayer layer, JsonElement cellList, JsonElement index)
    {
        // tilemap.json cell = [c, r, tileIndexIntoIds]; resolve id -> atlas xy.
        int count = 0;
        foreach (var cell in cellList.EnumerateArray())
        {
            int c = cell[0].GetInt32(), r = cell[1].GetInt32(), ti = cell[2].GetInt32();
            // index is keyed by id; the converter lists ids in atlas order,
            // so tile index ti maps to atlas (ti % 8, ti / 8).
            var xy = new Vector2I(ti % 8, ti / 8);
            layer.SetCell(new Vector2I(c, r), 0, xy);
            count++;
        }
        LayerCounts[layer.Name] = count;
    }
}
