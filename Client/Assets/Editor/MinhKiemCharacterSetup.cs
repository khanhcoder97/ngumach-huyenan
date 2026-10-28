using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Builds the full Minh Kiếm animation content from the approved sprite sheets:
/// 16 actions x 8 directions = 128 clips, an AnimatorController driven by
/// DirIndex / IsMoving / IsRunning / ActionId, a playable prefab and a test scene.
///
/// Animator contract (consumed by DirectionalAnimator2D):
///   DirIndex (int)  - sheet row: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
///   IsMoving (bool) - movement input active
///   IsRunning (bool)- run modifier held while moving
///   ActionId (int)  - -1 = locomotion (Idle/Walk/Run); otherwise an action code:
///                     0 Hurt, 1 Death, 2 Dodge, 3 Attack1, 4 Attack2, 5 Attack3,
///                     6 Skill1, 7 Skill2, 8 Skill3, 9 Jump, 10 Fall, 11 Land, 12 Interact
///
/// Run from the menu (Ngũ Mạch > Build Minh Kiếm Character) or headless:
///   Unity -batchmode -quit -executeMethod MinhKiemCharacterSetup.BuildAll
/// Sheet slicing lives in each minh_kiem_&lt;action&gt;.png.meta (48x64 cells,
/// 20 PPU, Point filter, pivot bottom-center) and is verified here per sheet.
/// </summary>
public static class MinhKiemCharacterSetup
{
    private const string ArtDir = "Assets/Art/Characters/MinhKiem";
    private const string AnimDir = "Assets/Animation/MinhKiem";
    private const string ControllerPath = AnimDir + "/MinhKiemAnimator.controller";
    private const string PrefabPath = "Assets/Prefabs/Player/MinhKiem.prefab";
    private const string ScenePath = "Assets/Scenes/MinhKiemWalkTest.unity";

    private static readonly string[] RowNames = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };

    private sealed class ActionDef
    {
        public readonly string Name;      // state/clip prefix, e.g. "Attack1"
        public readonly string Sheet;     // sprite stem, e.g. "attack1"
        public readonly int Frames;
        public readonly float Fps;
        public readonly bool Loop;
        public readonly int ActionId;     // -1 for locomotion actions

        public ActionDef(string name, string sheet, int frames, float fps, bool loop, int actionId)
        {
            Name = name; Sheet = sheet; Frames = frames; Fps = fps; Loop = loop; ActionId = actionId;
        }
    }

    // Locomotion first (ActionId -1), then one-shot / hold actions by code.
    private static readonly ActionDef[] Actions =
    {
        new ActionDef("Idle",     "idle",     4, 6f,  true,  -1),
        new ActionDef("Walk",     "walk",     6, 8f,  true,  -1),
        new ActionDef("Run",      "run",      6, 12f, true,  -1),
        new ActionDef("Hurt",     "hurt",     2, 8f,  false, 0),
        new ActionDef("Death",    "death",    4, 8f,  false, 1),
        new ActionDef("Dodge",    "dodge",    4, 12f, false, 2),
        new ActionDef("Attack1",  "attack1",  5, 12f, false, 3),
        new ActionDef("Attack2",  "attack2",  5, 12f, false, 4),
        new ActionDef("Attack3",  "attack3",  5, 12f, false, 5),
        new ActionDef("Skill1",   "skill1",   6, 12f, false, 6),
        new ActionDef("Skill2",   "skill2",   6, 12f, false, 7),
        new ActionDef("Skill3",   "skill3",   6, 12f, false, 8),
        new ActionDef("Jump",     "jump",     4, 12f, false, 9),
        new ActionDef("Fall",     "fall",     4, 8f,  true,  10),
        new ActionDef("Land",     "land",     4, 12f, false, 11),
        new ActionDef("Interact", "interact", 4, 8f,  false, 12),
    };

    [MenuItem("Ngũ Mạch/Build Minh Kiếm Character")]
    public static void BuildAll()
    {
        EnsureFolder("Assets/Animation/MinhKiem");
        EnsureFolder("Assets/Prefabs/Player");
        EnsureFolder("Assets/Scenes");

        var clips = new Dictionary<string, AnimationClip>();
        int built = 0, failed = 0;
        foreach (ActionDef def in Actions)
        {
            List<Sprite> sprites = LoadSprites(def);
            if (sprites == null)
            {
                failed++;
                continue;
            }
            for (int row = 0; row < 8; row++)
                clips[def.Name + "_" + RowNames[row]] = BuildClip(def, sprites, row);
            built++;
        }
        if (failed > 0)
            Debug.LogError($"MinhKiemCharacterSetup: {failed} sheet(s) failed verification; controller built from {built} actions only.");

        AnimatorController controller = BuildController(clips);
        BuildPrefab(controller);
        BuildTestScene();

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log($"MinhKiemCharacterSetup: build complete ({built} actions, {clips.Count} clips, controller, prefab, test scene).");
    }

    private static List<Sprite> LoadSprites(ActionDef def)
    {
        string path = $"{ArtDir}/minh_kiem_{def.Sheet}.png";
        var result = new List<Sprite>();
        foreach (Object o in AssetDatabase.LoadAllAssetsAtPath(path))
        {
            if (o is Sprite s)
                result.Add(s);
        }
        int expected = def.Frames * 8;
        if (result.Count != expected)
        {
            Debug.LogError($"MinhKiemCharacterSetup: expected {expected} sprites in {path}, found {result.Count}. Skipping {def.Name}.");
            return null;
        }
        return result;
    }

    private static AnimationClip BuildClip(ActionDef def, List<Sprite> sprites, int row)
    {
        string rowName = RowNames[row];
        string clipPath = $"{AnimDir}/{def.Name}_{rowName}.anim";
        var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
        if (clip == null)
        {
            clip = new AnimationClip();
            AssetDatabase.CreateAsset(clip, clipPath);
        }

        clip.frameRate = def.Fps;
        var binding = new EditorCurveBinding
        {
            type = typeof(SpriteRenderer),
            path = "",
            propertyName = "m_Sprite"
        };

        var keyframes = new ObjectReferenceKeyframe[def.Frames];
        for (int f = 0; f < def.Frames; f++)
        {
            Sprite frame = sprites.Find(s => s.name == $"minh_kiem_{def.Sheet}_{rowName}_{f}");
            if (frame == null)
                Debug.LogError($"MinhKiemCharacterSetup: missing sprite minh_kiem_{def.Sheet}_{rowName}_{f}");
            keyframes[f] = new ObjectReferenceKeyframe { time = f / def.Fps, value = frame };
        }

        AnimationUtility.SetObjectReferenceCurve(clip, binding, keyframes);
        AnimationUtility.SetAnimationClipSettings(clip, new AnimationClipSettings
        {
            loopTime = def.Loop,
            startTime = 0f,
            stopTime = def.Frames / def.Fps
        });
        EditorUtility.SetDirty(clip);
        return clip;
    }

    private static AnimatorController BuildController(Dictionary<string, AnimationClip> clips)
    {
        var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
        if (controller == null)
            controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);

        // Parameters (idempotent). ActionId defaults to -1 (locomotion).
        EnsureParameter(controller, "DirIndex", AnimatorControllerParameterType.Int);
        EnsureParameter(controller, "IsMoving", AnimatorControllerParameterType.Bool);
        EnsureParameter(controller, "IsRunning", AnimatorControllerParameterType.Bool);
        EnsureParameter(controller, "ActionId", AnimatorControllerParameterType.Int);
        AnimatorControllerParameter[] ps = controller.parameters;
        for (int i = 0; i < ps.Length; i++)
            if (ps[i].name == "ActionId")
                ps[i].defaultInt = -1;
        controller.parameters = ps;

        AnimatorStateMachine sm = controller.layers[0].stateMachine;

        // Remove every previously generated state so re-runs stay clean.
        var kept = new List<ChildAnimatorState>();
        foreach (ChildAnimatorState child in sm.states)
        {
            if (child.state != null && IsGeneratedState(child.state.name))
                Object.DestroyImmediate(child.state, true);
            else
                kept.Add(child);
        }
        sm.states = kept.ToArray();

        var states = new Dictionary<string, AnimatorState>();
        foreach (ActionDef def in Actions)
        {
            for (int row = 0; row < 8; row++)
            {
                string key = def.Name + "_" + RowNames[row];
                if (!clips.TryGetValue(key, out AnimationClip clip))
                    continue;
                AnimatorState st = sm.AddState(key, new Vector3(260f * row, 60f * StateRowIndex(def), 0f));
                st.motion = clip;
                states[key] = st;
            }
        }
        if (states.TryGetValue("Idle_S", out AnimatorState idleS))
            sm.defaultState = idleS;

        // AnyState transitions: an action (or locomotion mode) plays when its
        // conditions match; returning ActionId to -1 hands control back to locomotion.
        foreach (AnimatorStateTransition t in sm.anyStateTransitions)
            Object.DestroyImmediate(t, true);
        sm.anyStateTransitions = new AnimatorStateTransition[0];

        foreach (ActionDef def in Actions)
        {
            for (int row = 0; row < 8; row++)
            {
                if (!states.TryGetValue(def.Name + "_" + RowNames[row], out AnimatorState st))
                    continue;
                AnimatorStateTransition tr = sm.AddAnyStateTransition(st);
                tr.hasExitTime = false;
                tr.duration = 0f;
                tr.canTransitionToSelf = false;
                tr.AddCondition(AnimatorConditionMode.Equals, def.ActionId, "ActionId");
                if (def.ActionId < 0)
                {
                    // Locomotion routing: Idle when still, Walk/Run while moving.
                    if (def.Name == "Idle")
                        tr.AddCondition(AnimatorConditionMode.IfNot, 0f, "IsMoving");
                    else if (def.Name == "Walk")
                    {
                        tr.AddCondition(AnimatorConditionMode.If, 0f, "IsMoving");
                        tr.AddCondition(AnimatorConditionMode.IfNot, 0f, "IsRunning");
                    }
                    else if (def.Name == "Run")
                    {
                        tr.AddCondition(AnimatorConditionMode.If, 0f, "IsMoving");
                        tr.AddCondition(AnimatorConditionMode.If, 0f, "IsRunning");
                    }
                }
                tr.AddCondition(AnimatorConditionMode.Equals, row, "DirIndex");
            }
        }

        EditorUtility.SetDirty(controller);
        return controller;
    }

    private static bool IsGeneratedState(string name)
    {
        foreach (ActionDef def in Actions)
            if (name.StartsWith(def.Name + "_"))
                return true;
        return false;
    }

    private static int StateRowIndex(ActionDef def)
    {
        for (int i = 0; i < Actions.Length; i++)
            if (Actions[i] == def)
                return i;
        return 0;
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
        renderer.sprite = FindSprite("idle", "S", 0) ?? FindSprite("walk", "S", 0);

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

    private static Sprite FindSprite(string sheet, string row, int frame)
    {
        foreach (Object o in AssetDatabase.LoadAllAssetsAtPath($"{ArtDir}/minh_kiem_{sheet}.png"))
            if (o is Sprite s && s.name == $"minh_kiem_{sheet}_{row}_{frame}")
                return s;
        return null;
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
