// CharacterPresenter — Presentation controller for character sheet and 12 equipment slots.
// Pure C#, no Unity dependency.
// Rules:
//   - Reads authoritative vitals from P1Self.
//   - Strictly requires location == "EQUIPPED" for equipped items (DEC-021/023).
//   - Disables actions when server endpoints are not available.
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class CharacterPresenter
    {
        private readonly IP1UIAdapter _adapter;
        private AsyncState<CharacterViewState> _state = AsyncState<CharacterViewState>.Idle;
        private int _generation;

        public AsyncState<CharacterViewState> State => _state;
        public event Action OnChanged;

        public CharacterPresenter(IP1UIAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
        }

        public void Refresh()
        {
            int curGen = ++_generation;
            var self = _adapter.Self;
            if (self == null)
            {
                _state = AsyncState<CharacterViewState>.Idle;
                OnChanged?.Invoke();
                return;
            }

            var equippedMap = new Dictionary<string, ItemSlotView>(StringComparer.OrdinalIgnoreCase);
            var inv = _adapter.Inventory;
            if (inv?.items != null)
            {
                foreach (var item in inv.items)
                {
                    if (item == null) continue;
                    bool isEquipped = string.Equals(item.location, "EQUIPPED", StringComparison.OrdinalIgnoreCase);

                    if (isEquipped && !string.IsNullOrEmpty(item.slot))
                    {
                        string canonicalSlot = CharacterViewState.NormalizeSlot(item.slot);
                        if (!string.IsNullOrEmpty(canonicalSlot))
                        {
                            var meta = ItemMetadataResolver.Resolve(item.templateId);
                            equippedMap[canonicalSlot] = new ItemSlotView(item, meta.DisplayName, meta.Rarity);
                        }
                    }
                }
            }

            if (curGen != _generation) return;
            var view = new CharacterViewState(self, equippedMap);
            _state = _state.WithValue(view);
            OnChanged?.Invoke();
        }

        public void Clear()
        {
            ++_generation;
            _state = AsyncState<CharacterViewState>.Idle;
            OnChanged?.Invoke();
        }

        public Task<P1Result> EquipAsync(string instanceId, string targetSlot, CancellationToken ct)
        {
            return Task.FromResult(P1Result.Fail("UNSUPPORTED_ENDPOINT", "authoritative action unavailable in baseline"));
        }

        public Task<P1Result> UnequipAsync(string slotKey, CancellationToken ct)
        {
            return Task.FromResult(P1Result.Fail("UNSUPPORTED_ENDPOINT", "authoritative action unavailable in baseline"));
        }

        public Task<P1Result> SalvageAsync(string instanceId, CancellationToken ct)
        {
            return Task.FromResult(P1Result.Fail("UNSUPPORTED_ENDPOINT", "authoritative action unavailable in baseline"));
        }
    }
}
