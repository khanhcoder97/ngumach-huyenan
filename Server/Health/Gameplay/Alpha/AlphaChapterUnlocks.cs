using System.Collections.Concurrent;
using Server.Health.Gameplay.Quests;

namespace Server.Health.Gameplay.Alpha;

// QOD-21 Q4: the server's own record that a character finished the Bến Mưa
// opening and may reach chapter one.
//
// The design states this as prose (questRules.P00-05.unlock: "P00-05 turn-in
// commits CHAPTER_C1_UNLOCKED and MAP_THANH_LAC portal access; C1-01 record
// minLevel11 per existing chapter spec, not silently marked complete"), so the
// two tokens it names are pinned here and AlphaProfileValidator refuses a design
// whose sentence no longer carries them — a renamed flag or portal map fails
// startup instead of quietly granting the wrong thing.
//
// Nothing on the wire carries a grant: no route may move an actor between maps
// yet (teleport is DI-only and death-return is the packet this checkpoint ships),
// so this is the authority those paths consult once they exist. The unlock does
// not make C1-01 completable by fiat — availability stays derived from the quest
// graph (C1-01 requires P00-05 COMPLETED) and acceptance stays gated by its own
// minLevel 11, so "silently marked complete" has no path here.
public static class AlphaChapterUnlockRules
{
    public const string QuestId = "P00-05";
    public const string Flag = "CHAPTER_C1_UNLOCKED";
    public const string PortalMapId = "MAP_THANH_LAC";
}

public sealed class ChapterUnlockStore : IChapterUnlockSink
{
    // Bounded like the other per-character ledgers: an idle character must not be
    // able to grow this one forever.
    public const int Capacity = 256;

    private readonly AlphaProfileOptions _options;
    private readonly object _sync = new();
    private readonly Dictionary<(string CharacterId, string QuestId), string> _grants = new();
    private readonly Queue<(string CharacterId, string QuestId)> _order = new();

    public ChapterUnlockStore(AlphaProfileOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);
        _options = options;
    }

    public int Count
    {
        get
        {
            lock (_sync)
            {
                return _grants.Count;
            }
        }
    }

    public bool OnQuestCompleted(string characterId, string questId)
    {
        if (!_options.Enabled ||
            !string.Equals(questId, AlphaChapterUnlockRules.QuestId, StringComparison.Ordinal))
        {
            return false;
        }

        var key = (characterId, questId);
        lock (_sync)
        {
            if (_grants.ContainsKey(key))
            {
                return false;
            }

            _grants[key] = AlphaChapterUnlockRules.Flag;
            _order.Enqueue(key);
            while (_order.Count > Capacity && _order.TryDequeue(out var oldest))
            {
                _grants.Remove(oldest);
            }
        }

        return true;
    }

    public void Revoke(string characterId, string questId)
    {
        lock (_sync)
        {
            _grants.Remove((characterId, questId));
        }
    }

    public bool HasFlag(string characterId, string flag)
    {
        lock (_sync)
        {
            return _grants.Any(grant =>
                string.Equals(grant.Key.CharacterId, characterId, StringComparison.Ordinal) &&
                string.Equals(grant.Value, flag, StringComparison.Ordinal));
        }
    }

    public bool AllowsPortal(string characterId, string mapId) =>
        _options.Enabled &&
        string.Equals(mapId, AlphaChapterUnlockRules.PortalMapId, StringComparison.Ordinal) &&
        HasFlag(characterId, AlphaChapterUnlockRules.Flag);
}
