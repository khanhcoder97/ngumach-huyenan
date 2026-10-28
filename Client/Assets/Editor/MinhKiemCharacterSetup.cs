using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Builds the Minh Kiếm walk content from the approved sprite sheet:
/// 8 looping walk clips (one per sheet row), an AnimatorController driven by
/// DirIndex/IsMoving, a playable prefab and a test scene.
/// Run from the menu (Ngũ Mạch &gt; Build Minh Kiếm Character) or headless:
///   Unity -batchmode -quit -executeMethod MinhKiemCharacterSetup.BuildAll
/// The sheet slicing itself lives in minh_kiem_walk.png.meta (48 sprites,
/// 48x64 cells, 20 PPU, Point filter, pivot bottom-center) and is verified here.
/// </summary>
public static class MinhKiemCharacterSetup
{
    private const string SheetPath = "Assets/Art/Characters/MinhKiem/minh_kiem_walk.png";
    private const string AnimDir = "Assets/Animation/MinhKiem";
    private const string ControllerPath = AnimDir + "/MinhKiemAnimator.controller";
    private const string PrefabPath = "Assets/Prefabs/Player/MinhKiem.prefab";
    private const string ScenePath = "Assets/Scenes/MinhKiemWalkTest.unity";
    private const float WalkFps = 8f;

    private static readonly string[] RowNames = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };

    [MenuItem("Ngũ Mạch/Build Minh Kiếm Character")]
    public static void BuildAll()
    {
        EnsureFolder("Assets/Animation/MinhKiem");
        EnsureFolder("Assets/Prefabs/Player");
        EnsureFolder("Assets/Scenes");

        List<Sprite> sprites = LoadSprites();
        if (sprites.Count != 48)
        {
            Debug.LogError($"MinhKiemCharacterSetup: expected 48 sprites in {SheetPath}, found {sprites.Count}. Aborting.");
            return;
        }

        AnimationClip[] clips = new AnimationClip[8];
        for (int row = 0; row < 8; row++)
            clips[row] = BuildWalkClip(RowNames[row], sprites, row);

        AnimatorController controller = BuildController(clips);
        BuildPrefab(controller);
        BuildTestScene();

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("MinhKiemCharacterSetup: build complete (8 clips, controller, prefab, test scene).");
    }

    private static List<Sprite> LoadSprites()
    {
        var result = new List<Sprite>();
        foreach (Object o in AssetDatabase.LoadAllAssetsAtPath(SheetPath))
        {
            if (o is Sprite s)
                result.Add(s);
        }
        return result;
    }

    private static AnimationClip BuildWalkClip(string rowName, List<Sprite> sprites, int row)
    {
        string clipPath = $"{AnimDir}/Walk_{rowName}.anim";
        var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
        if (clip == null)
        {
            clip = new AnimationClip();
            AssetDatabase.CreateAsset(clip, clipPath);
        }

        clip.frameRate = WalkFps;
        var binding = new EditorCurveBinding
        {
            type = typeof(SpriteRenderer),
            path = "",
            propertyName = "m_Sprite"
        };

        var keyframes = new ObjectReferenceKeyframe[6];
        for (int f = 0; f < 6; f++)
        {
            Sprite frame = sprites.Find(s => s.name == $"minh_kiem_walk_{rowName}_{f}");
            if (frame == null)
                Debug.LogError($"MinhKiemCharacterSetup: missing sprite minh_kiem_walk_{rowName}_{f}");
            keyframes[f] = new ObjectReferenceKeyframe { time = f / WalkFps, value = frame };
        }

        AnimationUtility.SetObjectReferenceCurve(clip, binding, keyframes);
        AnimationUtility.SetAnimationClipSettings(clip, new AnimationClipSettings
        {
            loopTime = true,
            startTime = 0f,
            stopTime = 6f / WalkFps
        });
        EditorUtility.SetDirty(clip);
        return clip;
    }

    private static AnimatorController BuildController(AnimationClip[] clips)
    {
        var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
        if (controller == null)
            controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);

        // Parameters (idempotent).
        EnsureParameter(controller, "DirIndex", AnimatorControllerParameterType.Int);
        EnsureParameter(controller, "IsMoving", AnimatorControllerParameterType.Bool);

        AnimatorStateMachine sm = controller.layers[0].stateMachine;

        // Remove previously generated Walk_* states so re-runs stay clean.
        var kept = new List<ChildAnimatorState>();
        foreach (ChildAnimatorState child in sm.states)
        {
            if (child.state != null && child.state.name.StartsWith("Walk_"))
                Object.DestroyImmediate(child.state, true);
            else
                kept.Add(child);
        }
        sm.states = kept.ToArray();

        var states = new AnimatorState[8];
        for (int row = 0; row < 8; row++)
        {
            states[row] = sm.AddState("Walk_" + RowNames[row]);
            states[row].motion = clips[row];
        }
        sm.defaultState = states[4]; // Walk_S (front)

        // AnyState -> Walk_<row> while moving and DirIndex matches the row.
        foreach (AnimatorStateTransition t in sm.anyStateTransitions)
            Object.DestroyImmediate(t, true);
        sm.anyStateTransitions = new AnimatorStateTransition[0];

        for (int row = 0; row < 8; row++)
        {
            AnimatorStateTransition tr = sm.AddAnyStateTransition(states[row]);
            tr.hasExitTime = false;
            tr.duration = 0f;
            tr.canTransitionToSelf = false;
            tr.AddCondition(AnimatorConditionMode.If, 0f, "IsMoving");
            tr.AddCondition(AnimatorConditionMode.Equals, row, "DirIndex");
        }

        EditorUtility.SetDirty(controller);
        return controller;
    }

    private static void EnsureParameter(AnimatorController controller, string name, AnimatorControllerParameterType type)
    {
        foreach (AnimatorControllerParameter p in controller.parameters)
            if (p.name == name)
                return;
        controller.AddParameter(name, type);
    }

    private static void BuildPrefab(AnimatorController controller)
    {
        var go = new GameObject("MinhKiem");

        var renderer = go.AddComponent<SpriteRenderer>();
        Sprite firstFrame = AssetDatabase.LoadAssetAtPath<Sprite>(SheetPath);
        Object[] assets = AssetDatabase.LoadAllAssetsAtPath(SheetPath);
        foreach (Object o in assets)
            if (o is Sprite s && s.name == "minh_kiem_walk_S_0")
                firstFrame = s;
        renderer.sprite = firstFrame;

        var animator = go.AddComponent<Animator>();
        animator.runtimeAnimatorController = controller;

        var body = go.AddComponent<Rigidbody2D>();
        body.gravityScale = 0f;
        body.freezeRotation = true;

        var collider = go.AddComponent<CapsuleCollider2D>();
        collider.size = new Vector2(1.2f, 0.6f);
        collider.offset = new Vector2(0f, 0.3f);
        collider.direction = CapsuleDirection2D.Horizontal;

        go.AddComponent<PlayerController2D>();
        go.AddComponent<DirectionalAnimator2D>();

        PrefabUtility.SaveAsPrefabAsset(go, PrefabPath);
        Object.DestroyImmediate(go);
        Debug.Log("MinhKiemCharacterSetup: prefab saved at " + PrefabPath);
    }

    private static void BuildTestScene()
    {
        Scene scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(
            UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
            UnityEditor.SceneManagement.NewSceneMode.Single);

        // Camera with the project's locked pixel-art bootstrap.
        var camGo = new GameObject("Main Camera");
        camGo.tag = "MainCamera";
        var cam = camGo.AddComponent<Camera>();
        cam.orthographic = true;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.16f, 0.23f, 0.35f); // rainy blue placeholder (Bến Mưa mood)
        camGo.AddComponent<PixelArtCameraBootstrap>();
        camGo.transform.position = new Vector3(0f, 0f, -10f);
        // PixelPerfectCamera is added by PixelArtCameraBootstrap at runtime (URP 2D type).
        var ppcType = System.Type.GetType("UnityEngine.Rendering.Universal.PixelPerfectCamera, Unity.RenderPipelines.Universal.Runtime");
        if (ppcType != null)
            camGo.AddComponent(ppcType);

        // Player instance.
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        if (prefab != null)
        {
            GameObject player = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            player.transform.position = Vector3.zero;
        }

        UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("MinhKiemCharacterSetup: test scene saved at " + ScenePath);
    }

    private static void EnsureFolder(string path)
    {
        string[] parts = path.Split('/');
        string current = parts[0];
        for (int i = 1; i < parts.Length; i++)
        {
            string next = current + "/" + parts[i];
            if (!AssetDatabase.IsValidFolder(next))
                AssetDatabase.CreateFolder(current, parts[i]);
            current = next;
        }
    }
}
