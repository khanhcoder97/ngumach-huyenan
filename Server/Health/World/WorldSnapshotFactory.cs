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

    public static WorldSnapshotV2 CreateV2(
        PlayerSession session, WorldAoiProjectionService projection, ServerClock clock)
    {
        WorldAoiViewer viewer;
        WorldSnapshotV2Self self;
        long revision;
        long tick;
        string now;
        lock (session.SyncRoot)
        {
            viewer = new WorldAoiViewer(
                session.CharacterId, session.MapId, session.FloorId, session.X, session.Y);
            self = new WorldSnapshotV2Self
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
            };
            revision = session.Revision;
            tick = clock.Tick;
            now = P1Time.ToUtcString(clock.UtcNow);
        }

        // Boss impacts hold their domain lock before taking the actor lock.
        var entities = projection.Project(viewer).Select(MapEntityV2).ToArray();
        return new WorldSnapshotV2
        {
            MapId = viewer.MapId,
            MapInstanceId = viewer.MapId + WorldAudience.MapInstanceSuffix,
            FloorId = viewer.FloorId,
            Phase = WorldAudience.Phase,
            ServerTick = tick,
            Revision = revision,
            ServerTimeUtc = now,
            Audience = new WorldAudienceV2(),
            Self = self,
            Entities = entities
        };
    }

    private static WorldEntityV2 MapEntityV2(ProjectedEntityV2 entity) => new()
    {
        EntityId = entity.EntityId,
        Kind = entity.Kind,
        MapInstanceId = entity.MapInstanceId,
        FloorId = entity.FloorId,
        Phase = entity.Phase,
        X = entity.X,
        Y = entity.Y,
        State = entity.State,
        HealthState = entity.HealthState,
        Targetable = entity.Targetable,
        Availability = entity.Availability,
        Hp = entity.Hp,
        MaxHp = entity.MaxHp,
        Revision = entity.Revision,
        LifeId = entity.LifeId
    };
}
