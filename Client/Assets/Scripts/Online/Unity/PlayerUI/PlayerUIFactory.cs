// PlayerUIFactory — Programmatic runtime composition factory for the PlayerUI subsystem.
// Ensures that PlayerUIRoot and all panels can be bootstrapped without manual scene setup.
// Rules:
//   - Idempotent: re-uses existing child components if already present.
//   - Injects the provided UIDocument without searching the entire scene.
// Owner: Antigravity Remote — Issue #85.

using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    public static class PlayerUIFactory
    {
        public static PlayerUIRoot Create(GameObject host, UIDocument document)
        {
            if (host == null) throw new System.ArgumentNullException(nameof(host));

            var targetDoc = document != null ? document : host.GetComponent<UIDocument>();
            if (targetDoc == null)
            {
                targetDoc = host.GetComponentInChildren<UIDocument>();
            }

            var existing = host.GetComponentInChildren<PlayerUIRoot>();
            if (existing != null) return existing;

            var rootObj = new GameObject("PlayerUI_Root");
            rootObj.transform.SetParent(host.transform, false);

            var root = rootObj.AddComponent<PlayerUIRoot>();
            var inv = rootObj.AddComponent<InventoryPanel>();
            var character = rootObj.AddComponent<CharacterPanel>();
            var quest = rootObj.AddComponent<QuestJournalPanel>();
            var npc = rootObj.AddComponent<NpcDialoguePanel>();
            var settings = rootObj.AddComponent<SettingsPanel>();
            var map = rootObj.AddComponent<MapPanel>();
            var bar = rootObj.AddComponent<PlayerUIButtonBar>();
            var cinema = rootObj.AddComponent<CinemaOverlay>();

            // Store for settings
            if (host.GetComponent<PlayerPrefsSettingsStore>() == null)
            {
                host.AddComponent<PlayerPrefsSettingsStore>();
            }

            root.SetPanelReferences(inv, character, quest, npc, settings, map, bar, cinema);
            return root;
        }
    }
}
