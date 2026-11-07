namespace Server.Health.Gameplay.Combat;

// One mob death the engine has actually resolved: the entity and life that died,
// the event id the engine wrote to the owner's combat stream, and the character
// whose cast or counter caused it. This is the only kill shape the domain may
// credit against, because every field is already authoritative server-side.
public readonly record struct CombatMobKill(
    string KillerCharacterId,
    string EntityId,
    string RecordId,
    long LifeId,
    string DeathEventId);

// QOD-21 Q2: the quest machines that pay objective credit for a kill (the P00-04
// escort waves) must not infer it from a polled world state, where a shared
// spawn cannot tell whose fight it belonged to and a minted id is not a
// deduplication key. The tick engine therefore hands each resolved death to this
// sink at the moment it emits the DEATH event. When no sink is wired — every
// production profile, the mob-combat e2e and both Codex negative probes — the
// kill path is unchanged.
public interface ICombatKillSink
{
    void OnMobKilled(CombatMobKill kill);
}
