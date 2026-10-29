using System.Collections.Concurrent;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Quests;

public class RewardLedgerStore
{
    private readonly ConcurrentDictionary<(string CharacterId, string QuestId), RewardLedgerEntry>
        _ledger = new();

    public virtual bool TryRecord(string characterId, string questId, TurnInResult result)
    {
        var entry = new RewardLedgerEntry(result);
        return _ledger.TryAdd((characterId, questId), entry);
    }

    public TurnInResult? Find(string characterId, string questId)
    {
        if (_ledger.TryGetValue((characterId, questId), out var entry))
        {
            return entry.Result;
        }

        return null;
    }

    /// <summary>
    /// Remove a ledger entry. Exposed for self-check failure injection only.
    /// </summary>
    public void Remove(string characterId, string questId)
    {
        _ledger.TryRemove((characterId, questId), out _);
    }

    private sealed record RewardLedgerEntry(TurnInResult Result);
}