// OPC-16 O4 — inventory v2 presenter. Read model only; equip/unequip are
// server-authoritative mutations. No local item moves, no synthesized stats.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class InventoryV2Presenter
    {
        private readonly IP1InventoryV2Adapter _adapter;
        private AsyncState<InventoryV2ViewState> _state = AsyncState<InventoryV2ViewState>.Idle;

        public AsyncState<InventoryV2ViewState> State => _state;
        public event Action OnChanged;

        public InventoryV2Presenter(IP1InventoryV2Adapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
        }

        public async Task<AsyncState<InventoryV2ViewState>> LoadAsync(CancellationToken ct)
        {
            if (_state.IsLoading) return _state;
            _state = _state.WithLoading();
            Notify();
            try
            {
                var result = await _adapter.ReadInventoryV2Async(ct);
                if (ct.IsCancellationRequested)
                {
                    RestoreValue();
                    ct.ThrowIfCancellationRequested();
                }
                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    Notify();
                    return _state;
                }
                var view = Build(_adapter.InventoryV2, _state.Value);
                if (view == null)
                {
                    _state = _state.WithError("empty_response");
                    Notify();
                    return _state;
                }
                _state = _state.WithValue(view);
                Notify();
                return _state;
            }
            catch (OperationCanceledException)
            {
                RestoreValue();
                throw;
            }
        }

        public void Select(string instanceId)
        {
            if (_state.Value == null) return;
            _state = _state.WithValue(_state.Value.WithSelection(instanceId));
            Notify();
        }

        public async Task<AsyncState<InventoryV2ViewState>> EquipAsync(string instanceId, CancellationToken ct)
        {
            if (_state.Value == null) return WithErrorNoValue("not_loaded");
            if (_adapter.HasPendingMutation) return WithErrorNoValue("pending_mutation");
            if (!_state.Value.CanEquip(instanceId)) return WithErrorNoValue("not_equippable");
            return await CommandAsync(
                () => _adapter.EquipV2Async(instanceId, _state.Value.InventoryRevision, ct), ct);
        }

        public async Task<AsyncState<InventoryV2ViewState>> UnequipAsync(string slotId, CancellationToken ct)
        {
            if (_state.Value == null) return WithErrorNoValue("not_loaded");
            if (_adapter.HasPendingMutation) return WithErrorNoValue("pending_mutation");
            if (!_state.Value.CanUnequip(slotId)) return WithErrorNoValue("wrong_location");
            return await CommandAsync(
                () => _adapter.UnequipV2Async(slotId, _state.Value.InventoryRevision, ct), ct);
        }

        private async Task<AsyncState<InventoryV2ViewState>> CommandAsync(Func<Task<P1Result>> send, CancellationToken ct)
        {
            try
            {
                var result = await send();
                if (ct.IsCancellationRequested) ct.ThrowIfCancellationRequested();

                // An error response may carry the authoritative current snapshot
                // (revision_conflict / slot_occupied): show it, never retry silently.
                var snapshot = _adapter.InventoryV2;
                if (snapshot != null && (result.Success || _state.Value == null ||
                    snapshot.inventoryRevision >= _state.Value.InventoryRevision))
                {
                    var rebuilt = Build(snapshot, _state.Value);
                    if (rebuilt != null)
                    {
                        _state = result.Success
                            ? new AsyncState<InventoryV2ViewState>(LoadPhase.Loaded, rebuilt, null)
                            : new AsyncState<InventoryV2ViewState>(LoadPhase.Error, rebuilt,
                                result.Code, result.CorrelationId);
                        Notify();
                        return _state;
                    }
                }
                _state = result.Success ? _state.WithError("empty_response") :
                    _state.WithError(result.Code, result.CorrelationId);
                Notify();
                return _state;
            }
            catch (OperationCanceledException)
            {
                RestoreValue();
                throw;
            }
        }

        private AsyncState<InventoryV2ViewState> WithErrorNoValue(string code)
        {
            _state = _state.WithError(code);
            Notify();
            return _state;
        }

        private void RestoreValue()
        {
            _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<InventoryV2ViewState>.Idle;
            Notify();
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler != null) handler();
        }

        private static InventoryV2ViewState Build(P1InventorySnapshotV2 snapshot, InventoryV2ViewState previous)
        {
            if (snapshot == null) return null;
            var equipment = new Dictionary<string, InventoryV2ItemView>(StringComparer.Ordinal);
            var seen = new HashSet<string>(StringComparer.Ordinal);
            var bag = new List<InventoryV2ItemView>();
            var unsupported = new List<UnsupportedEquipView>();

            if (snapshot.slots != null)
            {
                foreach (var slot in snapshot.slots)
                {
                    if (slot == null || string.IsNullOrEmpty(slot.slotId) || !seen.Add(slot.slotId)) continue;
                    if (slot.item != null)
                        equipment[slot.slotId] = new InventoryV2ItemView(slot.item);
                }
            }
            if (snapshot.bag != null)
            {
                foreach (var item in snapshot.bag)
                {
                    if (item == null || string.IsNullOrEmpty(item.instanceId)) continue;
                    if (!seen.Add(item.instanceId)) continue;
                    bag.Add(new InventoryV2ItemView(item));
                }
            }
            if (snapshot.unsupported != null)
            {
                foreach (var item in snapshot.unsupported)
                {
                    if (item == null || string.IsNullOrEmpty(item.instanceId)) continue;
                    if (!seen.Add(item.instanceId)) continue;
                    unsupported.Add(new UnsupportedEquipView(item));
                }
            }

            var currencies = new List<CurrencyView>();
            if (snapshot.currencies != null)
                foreach (var currency in snapshot.currencies)
                    if (currency != null) currencies.Add(new CurrencyView(currency));

            string selected = previous != null ? previous.SelectedInstanceId : null;
            if (selected != null && !seen.Contains(selected)) selected = null;

            return new InventoryV2ViewState(
                snapshot.inventoryRevision, equipment, bag, unsupported, currencies,
                snapshot.bagSlots, selected);
        }
    }
}
