using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

public interface ICombatService
{
    CombatOutcome Resolve(PlayerSession actor, CombatCommand command, string? idempotencyKey = null);
}
