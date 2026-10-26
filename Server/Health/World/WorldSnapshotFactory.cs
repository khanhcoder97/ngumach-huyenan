using Server.Health.Contracts;

namespace Server.Health.World;

public static class WorldSnapshotFactory
{
    public static WorldSnapshot Create(PlayerSession session, ServerClock clock) =>
        new()
        {
            MapId = session.MapId,
            ServerTick = clock.Tick,
            Revision = session.Revision,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Self = new WorldSelf
            {
                CharacterId = session.CharacterId,
                ClassId = session.ClassId,
                X = session.X,
                Y = session.Y,
                Hp = session.Hp,
                MaxHp = session.MaxHp,
                Mp = session.Mp,
                MaxMp = session.MaxMp,
                SwordIntent = session.SwordIntent
            },
            Entities = Array.Empty<WorldEntity>()
        };
}
