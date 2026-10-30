// AG1+AG2 — InventoryPresenter: builds InventoryViewState from P1Client data.
// No Unity dependency. Uses IP1UIAdapter for commands.
// Rules:
//   - inventoryRevision old never overwrites new (handled by P1Client already, but we guard too).
//   - Duplicate-slot, out-of-range, unknown-template produce diagnosticWarnings, never silently drops items.
//   - Search/filter is a view projection only — does NOT change slot indices.
//   - Empty/loading/error states never imply items are gone.
//   - Item display metadata resolved from ItemMetadataResolver.
// Owner: Antigravity Remote — Issue #80, #85.

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

            try
            {
                var result = await _adapter.ReadInventoryAsync(ct);
                if (ct.IsCancellationRequested)
                {
                    _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<InventoryViewState>.Idle;
                    NotifyChanged();
                    ct.ThrowIfCancellationRequested();
                }

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

                // Guard: only apply if newer revision.
                if (_state.Value != null && inv.inventoryRevision < _state.Value.InventoryRevision)
                {
                    _state = _state.WithValue(_state.Value); // restore Loaded phase with current value
                    NotifyChanged();
                    return _state; // stale response, keep current
                }

                _state = _state.WithValue(BuildViewState(inv, _state.Value));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<InventoryViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
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
            var unassignedBagItems = new List<P1Item>();

            var items = inv.items ?? Array.Empty<P1Item>();
            foreach (var item in items)
            {
                if (item == null) { warnings.Add("null_item_entry"); continue; }
                if (string.IsNullOrEmpty(item.instanceId)) { warnings.Add("missing_instance_id"); continue; }
                if (!seenInstances.Add(item.instanceId)) { warnings.Add("duplicate_instance_id:" + item.instanceId); continue; }

                // Separate EQUIPPED / BANK from BAG
                if (string.Equals(item.location, "EQUIPPED", StringComparison.OrdinalIgnoreCase))
                {
                    // Equipment does not occupy standard bag slots; valid equipment slot names (e.g. MAIN_HAND)
                    // must not trigger out_of_range_slot warnings.
                    continue;
                }
                if (string.Equals(item.location, "BANK", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                // Item belongs to BAG (or default location)
                if (!string.IsNullOrEmpty(item.slot))
                {
                    if (int.TryParse(item.slot, out int slotIndex))
                    {
                        if (slotIndex >= 0 && slotIndex < InventoryViewState.TotalSlots)
                        {
                            if (!seenSlotIndices.Add(slotIndex))
                            {
                                warnings.Add("duplicate_slot_index:" + slotIndex + ":" + item.instanceId);
                            }
                            else
                            {
                                var meta = ItemMetadataResolver.Resolve(item.templateId);
                                slots[slotIndex] = new ItemSlotView(item, meta.DisplayName, meta.Rarity);
                            }
                        }
                        else
                        {
                            warnings.Add("out_of_range_slot:" + item.slot + ":" + item.instanceId);
                        }
                    }
                    else
                    {
                        // Non-numeric slot in BAG (e.g. named slot), treat as unassigned bag item
                        unassignedBagItems.Add(item);
                    }
                }
                else
                {
                    // Omitted slot in BAG: valid per contract, assign to next free linear slot
                    unassignedBagItems.Add(item);
                }
            }

            // Pass 2: Assign linear free slots to unassigned BAG items
            int freeSearchIndex = 0;
            foreach (var item in unassignedBagItems)
            {
                while (freeSearchIndex < InventoryViewState.TotalSlots && seenSlotIndices.Contains(freeSearchIndex))
                {
                    freeSearchIndex++;
                }

                if (freeSearchIndex < InventoryViewState.TotalSlots)
                {
                    seenSlotIndices.Add(freeSearchIndex);
                    var meta = ItemMetadataResolver.Resolve(item.templateId);
                    slots[freeSearchIndex] = new ItemSlotView(item, meta.DisplayName, meta.Rarity);
                    freeSearchIndex++;
                }
                else
                {
                    warnings.Add("inventory_full_overflow:" + item.instanceId);
                }
            }

            // Restore selection if instanceId still present.
            string selectedId = prev?.SelectedInstanceId;
            if (selectedId != null && !seenInstances.Contains(selectedId))
                selectedId = null;

            var currencies = new List<CurrencyView>();
            if (inv.currencies != null)
            {
                foreach (var c in inv.currencies)
                    if (c != null) currencies.Add(new CurrencyView(c));
            }

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
