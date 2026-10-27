using Server.Health.World;

namespace Server.Health.Gameplay.Teleport;

public interface ITeleportService
{
    TeleportOutcome Teleport(PlayerSession actor, TeleportCommand? command);
}
