using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Inventory;

public interface IInventoryService
{
    InventorySnapshot GetSnapshot(string characterId);

    InventoryOutcome Apply(PlayerSession actor, InventoryMutation? mutation);
}
