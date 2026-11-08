using System.Collections.Concurrent;

namespace Server.Health.Gameplay.Progress;

// DESIGN-BM-Q3-20261104 `xp.snapshotAt` = QUEST_ACCEPT_COMMIT and
// `xp.snapshotScope` = characterId + questId + questAttemptId: the level a quest
// is worth is the level the player had when they took it, not the level they
// reached while doing it. The accept path is the only writer, so a quest that was
// never accepted through it has no snapshot and the reward stays unresolved
// rather than being guessed from the current level.
//
// P1 has no quest-attempt lifecycle (a completed quest cannot be re-accepted, and
// nothing resets it), so the attempt component of the approved scope is constant
// and the (character, quest) pair identifies the one attempt that exists. State
// is in memory only, like the rest of the quest runtime.
public sealed class QuestXpSnapshotStore
{
    private readonly ConcurrentDictionary<(string CharacterId, string QuestId), int>
        _acceptedLevels = new();

    public void RecordAccept(string characterId, string questId, int acceptedLevel)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(questId);
        ArgumentOutOfRangeException.ThrowIfLessThan(acceptedLevel, 1);

        _acceptedLevels[(characterId, questId)] = acceptedLevel;
    }

    public bool TryGetAcceptedLevel(string characterId, string questId, out int acceptedLevel)
    {
        var found = _acceptedLevels.TryGetValue((characterId, questId), out var level);
        acceptedLevel = found ? level : 0;
        return found;
    }
}
