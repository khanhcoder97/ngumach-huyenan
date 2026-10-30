#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace NguMach.Client.P1.Editor
{
    public static class PlayerUIBuilder
    {
        [MenuItem("Ngu Mach/UI/Setup PlayerUI in Scene")]
        public static void SetupInScene()
        {
            var host = GameObject.Find("PlayerUI_Host");
            if (host == null)
            {
                host = new GameObject("PlayerUI_Host");
                Undo.RegisterCreatedObjectUndo(host, "Create PlayerUI_Host");
            }

            var doc = host.GetComponent<UIDocument>();
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
            Debug.Log("[PlayerUIBuilder] PlayerUI successfully setup in scene with UIDocument and Hook.");
        }
    }
}
#endif
