// OPC-16 O4 — immutable 12-slot inventory v2 view state.
// Server snapshot is the only source; the presenter never invents a slot,
// item, currency or stat. Unsupported equipped items stay visible as warnings.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class InventoryV2ViewState
    {
        // Read-only wrapper over a private array: consumers can enumerate and
        // index the canonical order but cannot rewrite the elements process-wide.
        public static readonly IReadOnlyList<string> SlotOrder = Array.AsReadOnly(new[]
        {
            "HAT", "CHEST", "LEGS", "WEAPON", "GLOVES", "BOOTS",
            "NECK", "RING_L", "RING_R", "PENDANT", "CLOAK", "SEAL"
        });

        public long InventoryRevision { get; }
        public IReadOnlyDictionary<string, InventoryV2ItemView> Equipment { get; }
        public IReadOnlyList<InventoryV2ItemView> Bag { get; }
        public IReadOnlyList<UnsupportedEquipView> Unsupported { get; }
        public IReadOnlyList<CurrencyView> Currencies { get; }
        public string SelectedInstanceId { get; }
        public int BagSlots { get; }

        private static readonly IReadOnlyDictionary<string, InventoryV2ItemView> EmptyEquipment =
            new System.Collections.ObjectModel.ReadOnlyDictionary<string, InventoryV2ItemView>(
                new Dictionary<string, InventoryV2ItemView>());

        public InventoryV2ViewState(
            long inventoryRevision,
            IReadOnlyDictionary<string, InventoryV2ItemView> equipment,
            IReadOnlyList<InventoryV2ItemView> bag,
            IReadOnlyList<UnsupportedEquipView> unsupported,
            IReadOnlyList<CurrencyView> currencies,
            int bagSlots = 100,
            string selectedInstanceId = null)
        {
            InventoryRevision = inventoryRevision;
            // Defensive copies: these collections are built from the server
            // snapshot the client core owns. The view publishes read-only copies
            // so a UI consumer can never mutate live inventory state through a
            // cast, and a caller that reuses its collections after construction
            // cannot change an already-published view.
            Equipment = CopyEquipment(equipment);
            Bag = CopyBag(bag);
            Unsupported = CopyUnsupported(unsupported);
            Currencies = CopyCurrencies(currencies);
            BagSlots = bagSlots;
            SelectedInstanceId = selectedInstanceId;
        }

        private static IReadOnlyDictionary<string, InventoryV2ItemView> CopyEquipment(
            IReadOnlyDictionary<string, InventoryV2ItemView> source)
        {
            if (source == null || source.Count == 0) return EmptyEquipment;
            var copy = new Dictionary<string, InventoryV2ItemView>(source.Count, StringComparer.Ordinal);
            foreach (var pair in source) copy[pair.Key] = pair.Value;
            return new System.Collections.ObjectModel.ReadOnlyDictionary<string, InventoryV2ItemView>(copy);
        }

        private static IReadOnlyList<InventoryV2ItemView> CopyBag(IReadOnlyList<InventoryV2ItemView> source)
        {
            if (source == null || source.Count == 0) return Array.Empty<InventoryV2ItemView>();
            var copy = new InventoryV2ItemView[source.Count];
            for (int i = 0; i < copy.Length; i++) copy[i] = source[i];
            return Array.AsReadOnly(copy);
        }

        private static IReadOnlyList<UnsupportedEquipView> CopyUnsupported(IReadOnlyList<UnsupportedEquipView> source)
        {
            if (source == null || source.Count == 0) return Array.Empty<UnsupportedEquipView>();
            var copy = new UnsupportedEquipView[source.Count];
            for (int i = 0; i < copy.Length; i++) copy[i] = source[i];
            return Array.AsReadOnly(copy);
        }

        private static IReadOnlyList<CurrencyView> CopyCurrencies(IReadOnlyList<CurrencyView> source)
        {
            if (source == null || source.Count == 0) return Array.Empty<CurrencyView>();
            var copy = new CurrencyView[source.Count];
            for (int i = 0; i < copy.Length; i++) copy[i] = source[i];
            return Array.AsReadOnly(copy);
        }

        public InventoryV2ViewState WithSelection(string instanceId)
        {
            var exists = instanceId == null || FindEquippedSlot(instanceId) != null || ContainsBagItem(instanceId);
            return new InventoryV2ViewState(InventoryRevision, Equipment, Bag, Unsupported, Currencies,
                BagSlots, exists ? instanceId : null);
        }

        public InventoryV2ItemView GetEquipped(string slotId)
        {
            if (slotId == null) return null;
            InventoryV2ItemView item;
            return Equipment.TryGetValue(slotId, out item) ? item : null;
        }

        public string FindEquippedSlot(string instanceId)
        {
            if (string.IsNullOrEmpty(instanceId)) return null;
            foreach (var pair in Equipment)
                if (pair.Value != null && pair.Value.InstanceId == instanceId) return pair.Key;
            return null;
        }

        public bool ContainsBagItem(string instanceId)
        {
            if (string.IsNullOrEmpty(instanceId)) return false;
            for (int i = 0; i < Bag.Count; i++)
                if (Bag[i] != null && Bag[i].InstanceId == instanceId) return true;
            return false;
        }

        public bool CanEquip(string instanceId)
        {
            return ContainsBagItem(instanceId) && FindEquippedSlot(instanceId) == null;
        }

        public bool CanUnequip(string slotId)
        {
            return GetEquipped(slotId) != null;
        }
    }

    public sealed class InventoryV2ItemView
    {
        public string InstanceId { get; }
        public string TemplateId { get; }
        public int Stack { get; }
        public string Location { get; }
        public string SlotId { get; }
        public int Durability { get; }
        public int Version { get; }
        public string DisplayName { get; }

        public InventoryV2ItemView(P1ItemV2 item, string displayName = null)
        {
            if (item == null) throw new ArgumentNullException(nameof(item));
            InstanceId = item.instanceId;
            TemplateId = item.templateId;
            Stack = item.stack;
            Location = item.location;
            SlotId = item.slotId;
            Durability = item.durability;
            Version = item.version;
            DisplayName = displayName ?? item.templateId + " (UNRESOLVED)";
        }
    }

    public sealed class UnsupportedEquipView
    {
        public string InstanceId { get; }
        public string TemplateId { get; }
        public string SourceSlot { get; }
        public string Reason { get; }
        public string ReasonVi { get; }

        public UnsupportedEquipView(P1UnsupportedEquipV2 item)
        {
            if (item == null) throw new ArgumentNullException(nameof(item));
            InstanceId = item.instanceId;
            TemplateId = item.templateId;
            SourceSlot = item.sourceSlot;
            Reason = item.reason;
            ReasonVi = item.reason == "UNMAPPED_SLOT"
                ? "Trang bị này không có ô tương thích trong 12 ô hiện tại."
                : "Trang bị này không hiển thị được trong 12 ô hiện tại.";
        }
    }
}
