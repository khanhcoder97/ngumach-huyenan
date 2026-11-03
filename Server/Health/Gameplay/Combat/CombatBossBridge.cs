using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// QOD-21 Q2: the tick engine resolves player casts only against `MOB` entities.
// The P00-05 quest boss is a `BOSS` entity owned by the alpha encounter, which
// holds its HP. This bridge lets the engine treat exactly that live boss as a
// cast target — it asks the encounter whether an entity is the acting
// character's boss, takes the sourced defense for mitigation, and pushes the
// resolved damage into the encounter so its HP stays single-sourced there. When
// no bridge is wired (every production profile, the mob-combat e2e and both
// Codex negative probes) or it reports no live boss, the impact path is
// unchanged.
public interface ICombatBossBridge
{
    // Armor used as defense against the acting character's casts.
    int BossDefense { get; }

    bool IsLiveBossTarget(string characterId, WorldEntityInstance entity);

    // Applies cast damage to that owner's boss and reports HP before/after and
    // whether this hit killed it. The encounter owns the HP and phase bookkeeping.
    (int HpBefore, int HpAfter, bool Died) ApplyDamage(
        string characterId, int damage, long tick);
}
