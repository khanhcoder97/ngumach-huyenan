// OPC-14 M1 — Focus navigation policy (pure C#, no Unity dep).
// Tab order, focus trap inside an open modal, and focus restore on close.
// Native focusController wiring lives in P1OnlinePanel/PlayerUIRoot (Unity side).
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 21, OPC-14 M1).

using System;
using System.Collections.Generic;
using System.Linq;

namespace NguMach.Client.Presentation
{
    public sealed class FocusElement
    {
        public string Id { get; }
        public string Scope { get; }   // modal scope id, or "global"
        public int TabOrder { get; }
        public bool IsEditor { get; }  // TextField/Slider/etc. — Space inserts text, not shortcut

        public FocusElement(string id, string scope, int tabOrder, bool isEditor = false)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            Scope = string.IsNullOrEmpty(scope) ? "global" : scope;
            TabOrder = tabOrder;
            IsEditor = isEditor;
        }
    }

    public static class FocusNavigationPolicy
    {
        /// <summary>Ordered focusables within a scope (tab order ascending).</summary>
        public static IReadOnlyList<FocusElement> Ordered(IEnumerable<FocusElement> elements, string scope)
        {
            if (elements == null) return Array.Empty<FocusElement>();
            var list = new List<FocusElement>();
            foreach (var e in elements)
                if (e != null && (scope == null || e.Scope == scope)) list.Add(e);
            list.Sort((a, b) => a.TabOrder.CompareTo(b.TabOrder));
            return list;
        }

        /// <summary>
        /// Next focus id when Tab is pressed, trapping inside the active scope.
        /// Returns null when there is nothing to focus.
        /// </summary>
        public static string Next(string currentId, IEnumerable<FocusElement> elements, string activeScope)
        {
            var ordered = Ordered(elements, activeScope);
            if (ordered.Count == 0) return null;
            int idx = -1;
            for (int i = 0; i < ordered.Count; i++)
                if (ordered[i].Id == currentId) { idx = i; break; }
            int next = (idx + 1) % ordered.Count;
            return ordered[next].Id;
        }

        /// <summary>Previous focus id (Shift+Tab), trapping inside the active scope.</summary>
        public static string Previous(string currentId, IEnumerable<FocusElement> elements, string activeScope)
        {
            var ordered = Ordered(elements, activeScope);
            if (ordered.Count == 0) return null;
            int idx = -1;
            for (int i = 0; i < ordered.Count; i++)
                if (ordered[i].Id == currentId) { idx = i; break; }
            int prev = idx <= 0 ? ordered.Count - 1 : idx - 1;
            return ordered[prev].Id;
        }

        /// <summary>
        /// Restore focus on modal close: prefer the remembered id if still present,
        /// else the first focusable in the global scope.
        /// </summary>
        public static string Restore(string rememberedId, IEnumerable<FocusElement> elements)
        {
            var global = Ordered(elements, "global");
            if (global.Count == 0) return null;
            foreach (var e in global)
                if (e.Id == rememberedId) return rememberedId;
            return global[0].Id;
        }

        /// <summary>Whether the focused element is an editor (Space must insert text, not trigger shortcut).</summary>
        public static bool IsEditorFocused(IEnumerable<FocusElement> elements, string currentId)
        {
            if (elements == null || string.IsNullOrEmpty(currentId)) return false;
            foreach (var e in elements)
                if (e != null && e.Id == currentId) return e.IsEditor;
            return false;
        }
    }
}