#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.Tilemaps;

/// <summary>
/// Creates a minimal, explicit startup scene for the empty project scaffold.
/// The command does not overwrite an existing scene at the destination.
/// </summary>
public static class PixelArtProjectSetup
{
    private const string SceneFolder = "Assets/Scenes";
    private const string SettingsFolder = "Assets/Settings";
    private const string RendererPath = SettingsFolder + "/Renderer2D.asset";
    private const string PipelinePath = SettingsFolder + "/URP2D.asset";
    private const string StartupScenePath = SceneFolder + "/Startup.unity";
    private const string SmokeScenePath = SceneFolder + "/PixelArtSmoke.unity";
    private const string SmokeArtFolder = "Assets/Art/Smoke";

    [MenuItem("Tools/Ngũ Mạch/Initialize Pixel Art Project")]
    public static void InitializeProject()
    {
        EnsureFolders();
        Ensure2DRenderPipeline();
        CreateStartupScene();
    }

    private static void EnsureFolders()
    {
        if (!AssetDatabase.IsValidFolder(SceneFolder))
            AssetDatabase.CreateFolder("Assets", "Scenes");
        if (!AssetDatabase.IsValidFolder(SettingsFolder))
            AssetDatabase.CreateFolder("Assets", "Settings");
    }

    private static void Ensure2DRenderPipeline()
    {
        var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
        if (pipeline == null)
        {
            var renderer = AssetDatabase.LoadAssetAtPath<Renderer2DData>(RendererPath);
            if (renderer == null)
            {
                renderer = ScriptableObject.CreateInstance<Renderer2DData>();
                AssetDatabase.CreateAsset(renderer, RendererPath);
            }

            pipeline = UniversalRenderPipelineAsset.Create(renderer);
            AssetDatabase.CreateAsset(pipeline, PipelinePath);
            AssetDatabase.SaveAssets();
        }

        GraphicsSettings.defaultRenderPipeline = pipeline;
        AssetDatabase.SaveAssets();
    }

    private static void CreateStartupScene()
    {
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(StartupScenePath) != null)
        {
            EditorUtility.DisplayDialog(
                "Startup scene already exists",
                $"Kept the existing scene at {StartupScenePath}.",
                "OK");
            AddSceneToBuildSettings(StartupScenePath);
            return;
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var cameraObject = new GameObject("Main Camera");
        cameraObject.tag = "MainCamera";
        cameraObject.transform.position = new Vector3(0f, 0f, -10f);
        var camera = cameraObject.AddComponent<Camera>();
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.055f, 0.047f, 0.075f, 1f);
        camera.allowHDR = false;
        camera.allowMSAA = false;
        camera.allowDynamicResolution = false;
        cameraObject.AddComponent<PixelArtCameraBootstrap>();

        EditorSceneManager.SaveScene(scene, StartupScenePath);
        AddSceneToBuildSettings(StartupScenePath);
        AssetDatabase.SaveAssets();
        Debug.Log($"Created pixel-art startup scene: {StartupScenePath}");
    }

    [MenuItem("Tools/Ngũ Mạch/Create Pixel Art Smoke Scene")]
    public static void CreatePixelArtSmokeScene()
    {
        EnsureFolders();
        EnsureSmokeArtFolder();

        var floorSprite = GetOrCreateSmokeSprite("SmokeFloor.png", 16, 16, CreateFloorPixels());
        var heroSprite = GetOrCreateSmokeSprite("SmokeHero.png", 32, 96, CreateHeroPixels());
        var tilePath = SmokeArtFolder + "/SmokeFloor.asset";

        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(SmokeScenePath) != null)
        {
            EditorUtility.DisplayDialog("Smoke scene already exists", $"Kept {SmokeScenePath}.", "OK");
            AddSceneToBuildSettings(SmokeScenePath, false);
            return;
        }

        var floorTile = AssetDatabase.LoadAssetAtPath<Tile>(tilePath);
        if (floorTile == null)
        {
            floorTile = ScriptableObject.CreateInstance<Tile>();
            floorTile.sprite = floorSprite;
            AssetDatabase.CreateAsset(floorTile, tilePath);
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        CreateCamera();

        var gridObject = new GameObject("Pixel Grid", typeof(Grid));
        var grid = gridObject.GetComponent<Grid>();
        grid.cellSize = new Vector3(0.8f, 0.8f, 1f);

        var tilemapObject = new GameObject("Pixel Smoke Tilemap", typeof(Tilemap), typeof(TilemapRenderer));
        tilemapObject.transform.SetParent(gridObject.transform, false);
        var tilemap = tilemapObject.GetComponent<Tilemap>();
        for (var x = -20; x < 20; x++)
            tilemap.SetTile(new Vector3Int(x, -11, 0), floorTile);

        var hero = new GameObject("PIXEL_PLACEHOLDER_HERO");
        hero.transform.position = new Vector3(0f, -6.5f, 0f);
        var heroRenderer = hero.AddComponent<SpriteRenderer>();
        heroRenderer.sprite = heroSprite;
        heroRenderer.sortingOrder = 10;

        EditorSceneManager.SaveScene(scene, SmokeScenePath);
        AddSceneToBuildSettings(SmokeScenePath, false);
        AssetDatabase.SaveAssets();
        Debug.Log($"Created pixel-art smoke scene with placeholder art: {SmokeScenePath}");
    }

    private static void EnsureSmokeArtFolder()
    {
        if (!AssetDatabase.IsValidFolder("Assets/Art"))
            AssetDatabase.CreateFolder("Assets", "Art");
        if (!AssetDatabase.IsValidFolder(SmokeArtFolder))
            AssetDatabase.CreateFolder("Assets/Art", "Smoke");
    }

    private static Sprite GetOrCreateSmokeSprite(string fileName, int width, int height, Color32[] pixels)
    {
        var assetPath = SmokeArtFolder + "/" + fileName;
        var existing = AssetDatabase.LoadAssetAtPath<Sprite>(assetPath);
        if (existing != null)
            return existing;

        var texture = new Texture2D(width, height, TextureFormat.RGBA32, false, true);
        texture.SetPixels32(pixels);
        texture.Apply(false, true);
        var diskPath = Path.Combine(Application.dataPath, "Art", "Smoke", fileName);
        File.WriteAllBytes(diskPath, texture.EncodeToPNG());
        Object.DestroyImmediate(texture);

        AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
        return AssetDatabase.LoadAssetAtPath<Sprite>(assetPath);
    }

    private static Color32[] CreateFloorPixels()
    {
        var pixels = new Color32[16 * 16];
        var baseColor = new Color32(85, 69, 61, 255);
        var accent = new Color32(119, 93, 72, 255);
        for (var y = 0; y < 16; y++)
        for (var x = 0; x < 16; x++)
            pixels[y * 16 + x] = ((x + y * 3) % 11 == 0) ? accent : baseColor;
        return pixels;
    }

    private static Color32[] CreateHeroPixels()
    {
        const int width = 32;
        const int height = 96;
        var pixels = new Color32[width * height];
        var outline = new Color32(29, 24, 35, 255);
        var hair = new Color32(105, 58, 35, 255);
        var hairLight = new Color32(151, 89, 49, 255);
        var skin = new Color32(237, 184, 130, 255);
        var silver = new Color32(164, 178, 190, 255);
        var silverLight = new Color32(222, 226, 219, 255);
        var gold = new Color32(231, 180, 67, 255);
        var blue = new Color32(31, 66, 145, 255);
        var navy = new Color32(17, 34, 79, 255);
        var boot = new Color32(57, 53, 52, 255);

        Fill(pixels, width, 7, 0, 13, 8, outline);
        Fill(pixels, width, 8, 1, 12, 7, silver);
        Fill(pixels, width, 7, 7, 13, 21, outline);
        Fill(pixels, width, 8, 8, 12, 20, silverLight);
        Fill(pixels, width, 8, 8, 12, 10, gold);
        Fill(pixels, width, 17, 24, 26, 61, outline);
        Fill(pixels, width, 18, 25, 25, 59, blue);
        Fill(pixels, width, 20, 28, 22, 57, navy);
        Fill(pixels, width, 17, 22, 26, 24, gold);
        Fill(pixels, width, 8, 21, 24, 58, outline);
        Fill(pixels, width, 9, 22, 23, 57, silver);
        Fill(pixels, width, 11, 22, 21, 55, silverLight);
        Fill(pixels, width, 8, 34, 24, 37, gold);
        Fill(pixels, width, 3, 41, 8, 56, outline);
        Fill(pixels, width, 4, 42, 7, 54, silver);
        Fill(pixels, width, 4, 51, 7, 54, gold);
        Fill(pixels, width, 9, 56, 23, 83, outline);
        Fill(pixels, width, 10, 57, 22, 82, skin);
        Fill(pixels, width, 7, 61, 24, 88, outline);
        Fill(pixels, width, 8, 62, 23, 87, hair);
        Fill(pixels, width, 10, 83, 21, 88, hairLight);
        Fill(pixels, width, 5, 71, 9, 81, hair);
        Fill(pixels, width, 22, 70, 26, 81, hair);
        Fill(pixels, width, 12, 68, 14, 69, outline);
        Fill(pixels, width, 18, 68, 20, 69, outline);
        Fill(pixels, width, 14, 62, 18, 64, gold);
        return pixels;
    }

    private static void Fill(Color32[] pixels, int width, int left, int bottom, int right, int top, Color32 color)
    {
        for (var y = bottom; y <= top; y++)
        for (var x = left; x <= right; x++)
            pixels[y * width + x] = color;
    }

    private static GameObject CreateCamera()
    {
        var cameraObject = new GameObject("Main Camera");
        cameraObject.tag = "MainCamera";
        cameraObject.transform.position = new Vector3(0f, 0f, -10f);
        var camera = cameraObject.AddComponent<Camera>();
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.055f, 0.047f, 0.075f, 1f);
        camera.allowHDR = false;
        camera.allowMSAA = false;
        camera.allowDynamicResolution = false;
        cameraObject.AddComponent<PixelArtCameraBootstrap>();
        return cameraObject;
    }

    private static void AddSceneToBuildSettings(string scenePath, bool enabled = true)
    {
        var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
        scenes.RemoveAll(scene => scene.path == scenePath);
        scenes.Insert(0, new EditorBuildSettingsScene(scenePath, enabled));
        EditorBuildSettings.scenes = scenes.ToArray();
    }
}
#endif
