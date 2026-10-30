#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace NguMach.Client.P1.Editor
{
    public static class PlayerUIBuilder
    {
        [MenuItem("Tools/Ngu Mach/Setup PlayerUI in Scene")]
        [MenuItem("Ngu Mach/UI/Setup PlayerUI in Scene")]
        public static void SetupInScene()
        {
            // Prefer existing P1OnlinePanel host if present
            var onlinePanel = Object.FindFirstObjectByType<P1OnlinePanel>();
            GameObject host = onlinePanel != null ? onlinePanel.gameObject : GameObject.Find("PlayerUI_Host");

            if (host == null)
            {
                host = new GameObject("PlayerUI_Host");
                Undo.RegisterCreatedObjectUndo(host, "Create PlayerUI_Host");
            }

            var doc = host.GetComponent<UIDocument>() ?? Object.FindFirstObjectByType<UIDocument>();
            if (doc == null)
            {
                doc = host.AddComponent<UIDocument>();
            }

            var hook = host.GetComponent<P1PlayerUIHook>();
            if (hook == null)
            {
                hook = host.AddComponent<P1PlayerUIHook>();
            }

            var existingRoot = host.GetComponentInChildren<PlayerUIRoot>();
            if (existingRoot == null)
            {
                existingRoot = PlayerUIFactory.Create(host, doc);
            }

            EditorUtility.SetDirty(host);
            Debug.Log("[PlayerUIBuilder] PlayerUI successfully setup on host: " + host.name);
        }
    }
}
#endif
