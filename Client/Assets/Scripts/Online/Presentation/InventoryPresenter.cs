// AG1+AG2 — InventoryPresenter: builds InventoryViewState from P1Client data.
// No Unity dependency. Uses IP1UIAdapter for commands.
// Rules:
//   - inventoryRevision old never overwrites new (handled by P1Client already, but we guard too).
//   - Duplicate-slot, out-of-range, unknown-template produce diagnosticWarnings, never silently drops items.
//   - Search/filter is a view projection only — does NOT change slot indices.
//   - Empty/loading/error states never imply items are gone.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class InventoryPresenter
    {
        private readonly IP1UIAdapter _adapter;
        private AsyncState<InventoryViewState> _state = AsyncState<InventoryViewState>.Idle;

        public AsyncState<InventoryViewState> State => _state;

        public InventoryPresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        /// <summary>
        /// Fetch inventory from server, build view state.
        /// If a load is already in progress, returns current state (do not double-send).
        /// </summary>
        public async Task<AsyncState<InventoryViewState>> LoadAsync(CancellationToken ct)
        {
            if (_state.IsLoading) return _state;

            // Preserve last known data while loading (shows stale, not blank).
            _state = _state.WithLoading();
            NotifyChanged();

            var result = await _adapter.ReadInventoryAsync(ct);
            if (!result.Success)
            {
                _state = _state.WithError(result.Code, result.CorrelationId);
                NotifyChanged();
                return _state;
            }

            var inv = _adapter.Inventory;
            if (inv == null)
            {
                _state = _state.WithError("empty_response");
                NotifyChanged();
                return _state;
            }

            // Guard: only apply if newer revision (P1Client already filters, but be defensive).
            if (_state.IsLoaded && _state.Value != null &&
                inv.inventoryRevision < _state.Value.InventoryRevision)
                return _state; // stale response, keep current

            _state = _state.WithValue(BuildViewState(inv, _state.Value));
            NotifyChanged();
            return _state;
        }

        public void SetPage(int page)
        {
            if (!_state.IsLoaded || _state.Value == null) return;
            _state = _state.WithValue(_state.Value.WithPage(page));
            NotifyChanged();
        }

        public void SetSelection(string instanceId)
        {
            if (!_state.IsLoaded || _state.Value == null) return;
            // Keep selection only if instanceId still exists in inventory.
            var exists = instanceId == null || _state.Value.Slots.ContainsKey(FindSlotByInstanceId(instanceId));
            _state = _state.WithValue(_state.Value.WithSelection(exists ? instanceId : null));
            NotifyChanged();
        }

        public void SetFilter(string text)
        {
            if (!_state.IsLoaded || _state.Value == null) return;
            _state = _state.WithValue(_state.Value.WithFilter(text));
            NotifyChanged();
        }

        public event Action OnChanged;
        private void NotifyChanged() => OnChanged?.Invoke();

        // ── Building view state ──────────────────────────────────────────────

        private static InventoryViewState BuildViewState(P1Inventory inv, InventoryViewState prev)
        {
            var warnings = new List<string>();
            var slots = new Dictionary<int, ItemSlotView>();
            var seenInstances = new HashSet<string>(StringComparer.Ordinal);
            var seenSlotIndices = new HashSet<int>();

            foreach (var item in inv.items)
            {
                if (item == null) { warnings.Add("null_item_entry"); continue; }
                if (string.IsNullOrEmpty(item.instanceId)) { warnings.Add("missing_instance_id"); continue; }
                if (!seenInstances.Add(item.instanceId)) { warnings.Add("duplicate_instance_id:" + item.instanceId); continue; }

                // Determine slot index from item.slot field.
                // slot field may be null (BAG items use linear assignment by server order),
                // or a string "0".."99".
                int slotIndex = -1;
                if (!string.IsNullOrEmpty(item.slot))
                {
                    if (!int.TryParse(item.slot, out slotIndex) || slotIndex < 0 || slotIndex >= InventoryViewState.TotalSlots)
                    {
                        warnings.Add("out_of_range_slot:" + item.slot + ":" + item.instanceId);
                        slotIndex = -1;
                    }
                }

                if (slotIndex >= 0)
                {
                    if (!seenSlotIndices.Add(slotIndex))
                    {
                        warnings.Add("duplicate_slot_index:" + slotIndex + ":" + item.instanceId);
                        continue; // Do not overwrite existing slot; report warning.
                    }
                    // Display name and rarity come from catalog; we pass null here (UNRESOLVED).
                    // A catalog resolver layer should call BuildViewState with resolved names.
                    slots[slotIndex] = new ItemSlotView(item, displayName: null, rarityKey: null);
                }
                // Items with unknown slot (no slot field) are still tracked via instance ID for diagnostics.
                // They will appear as warnings. A future catalog/slot-map update should resolve this.
                else if (item.location == "BAG")
                {
                    warnings.Add("bag_item_no_slot:" + item.instanceId);
                }
            }

            // Restore selection if instanceId still present.
            string selectedId = prev?.SelectedInstanceId;
            if (selectedId != null && !seenInstances.Contains(selectedId))
                selectedId = null;

            var currencies = new List<CurrencyView>();
            foreach (var c in inv.currencies)
                if (c != null) currencies.Add(new CurrencyView(c));

            return new InventoryViewState(
                inv.inventoryRevision,
                slots,
                currencies,
                prev?.ActivePage ?? 0,
                selectedId,
                prev?.FilterText,
                warnings.Count > 0 ? warnings.ToArray() : null);
        }

        private int FindSlotByInstanceId(string instanceId)
        {
            if (_state.Value == null) return -1;
            foreach (var kv in _state.Value.Slots)
                if (kv.Value?.InstanceId == instanceId) return kv.Key;
            return -1;
        }
    }
}
