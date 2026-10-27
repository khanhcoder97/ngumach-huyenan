using System.Text.RegularExpressions;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Teleport;

public sealed class InMemoryTeleportService : ITeleportService
{
    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private readonly MapBoundsCatalog _maps;
    private readonly ServerClock _clock;

    public InMemoryTeleportService(MapBoundsCatalog maps, ServerClock clock)
    {
        _maps = maps;
        _clock = clock;
    }

    public TeleportOutcome Teleport(PlayerSession actor, TeleportCommand? command)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (command is null)
        {
            return TeleportOutcome.Invalid("command");
        }

        if (command.MapId is null || !MapIdPattern.IsMatch(command.MapId))
        {
            return TeleportOutcome.Invalid("mapId");
        }

        var mapId = command.MapId;

        if (!double.IsFinite(command.XWu))
        {
            return TeleportOutcome.Invalid("xWu");
        }

        if (!double.IsFinite(command.YWu))
        {
            return TeleportOutcome.Invalid("yWu");
        }

        if (!TeleportReasons.IsValid(command.Reason))
        {
            return TeleportOutcome.Rejected(
                TeleportErrorCodes.InvalidReason, retryable: false, "reason");
        }

        if (!_maps.TryResolve(mapId, out var bounds))
        {
            return TeleportOutcome.Rejected(
                TeleportErrorCodes.InvalidMap, retryable: false, "mapId");
        }

        if (!bounds.Contains(command.XWu, command.YWu))
        {
            var field = command.XWu < bounds.XMin || command.XWu > bounds.XMax
                ? "xWu"
                : "yWu";
            return TeleportOutcome.Rejected(
                TeleportErrorCodes.OutOfBounds, retryable: false, field);
        }

        var isDeathReturn = string.Equals(
            command.Reason, TeleportReasons.DeathReturn, StringComparison.Ordinal);

        lock (actor.SyncRoot)
        {
            var meetsCondition = isDeathReturn ? actor.Hp <= 0 : actor.Hp > 0;
            if (!meetsCondition)
            {
                return TeleportOutcome.Rejected(
                    TeleportErrorCodes.InvalidCondition, retryable: false, "reason",
                    WorldSnapshotFactory.Create(actor, _clock));
            }

            actor.MapId = mapId;
            actor.X = command.XWu;
            actor.Y = command.YWu;
            actor.LastMoveAtUtc = _clock.UtcNow;
            actor.Revision++;

            return TeleportOutcome.Success(WorldSnapshotFactory.Create(actor, _clock));
        }
    }
}
