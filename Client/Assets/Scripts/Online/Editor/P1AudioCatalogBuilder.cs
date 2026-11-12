using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace NguMach.Client.P1.Editor
{
    // Codex-owned authoring bridge. Does not modify Muse's builder/scenes/importers.
    public sealed class P1AudioCatalogBuilder : IPreprocessBuildWithReport
    {
        public int callbackOrder { get { return 0; } }
        public void OnPreprocessBuild(BuildReport report) { Build(); }
        [MenuItem("Ngu Mach/Audio/Build Runtime Catalog")]
        public static void Build()
        {
            var source = "Assets/AudioManifests/game_audio_v1.json";
            if (!File.Exists(source)) throw new BuildFailedException("Missing original game audio manifest");
            string json = File.ReadAllText(source);
            var catalog = P1AudioCatalog.Parse(json);
            // Validate all imported references before modifying generated resources.
            foreach (var cue in catalog.cues)
                foreach (var clip in cue.clips)
                    if (AssetDatabase.LoadAssetAtPath<AudioClip>(clip.path.Substring("Client/".Length)) == null)
                        throw new BuildFailedException("Audio missing/unimported/LFS pointer: " + clip.path);
            string root = "Assets/Resources/P1Audio";
            Directory.CreateDirectory(root + "/Cues"); AssetDatabase.Refresh();
            foreach (var cue in catalog.cues)
            {
                string path = root + "/Cues/" + cue.cueKey.ToLowerInvariant() + ".asset";
                EnsureFolder(Path.GetDirectoryName(path).Replace('\\', '/'));
                var asset = AssetDatabase.LoadAssetAtPath<P1AudioCueAsset>(path);
                if (asset == null) { asset = ScriptableObject.CreateInstance<P1AudioCueAsset>(); AssetDatabase.CreateAsset(asset, path); }
                asset.cueKey = cue.cueKey; asset.clips = new AudioClip[cue.clips.Length];
                for (int i = 0; i < asset.clips.Length; i++)
                    asset.clips[i] = AssetDatabase.LoadAssetAtPath<AudioClip>(cue.clips[i].path.Substring("Client/".Length));
                EditorUtility.SetDirty(asset);
            }
            File.WriteAllText(root + "/catalog.json", json);
            AssetDatabase.SaveAssets(); AssetDatabase.Refresh();
            Debug.Log("P1 audio catalog: " + catalog.cues.Length + " on-demand cue resources generated. Engine listening review still required.");
        }
        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/'); EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
