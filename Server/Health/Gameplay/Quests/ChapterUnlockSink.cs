namespace Server.Health.Gameplay.Quests;

// QOD-21 Q4: the optional "this quest finished with a chapter consequence" seam.
//
// Turn-in already owns one atomic transaction (grant → flip → XP → ledger), so a
// consequence of a completion has to be written inside it and revoked if a later
// step rolls back. It is an interface rather than a call into the alpha profile
// because this namespace must not depend on which profile exists: with no sink
// registered, turn-in behaves exactly as it did before.
public interface IChapterUnlockSink
{
    // True when the sink recorded something for this completion, which is how the
    // caller knows a rollback has to revoke it. Implementations must be no-ops for
    // quests that carry no chapter consequence.
    bool OnQuestCompleted(string characterId, string questId);

    void Revoke(string characterId, string questId);
}
