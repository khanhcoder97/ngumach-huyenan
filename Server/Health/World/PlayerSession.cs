namespace Server.Health.World;

public sealed class PlayerSession
{
    public PlayerSession(
        string sessionId,
        string characterId,
        string classId,
        string mapId,
        double x,
        double y,
        int hp,
        int maxHp,
        int mp,
        int maxMp,
        DateTimeOffset createdAtUtc)
    {
        SessionId = sessionId;
        CharacterId = characterId;
        ClassId = classId;
        MapId = mapId;
        X = x;
        Y = y;
        Hp = hp;
        MaxHp = maxHp;
        Mp = mp;
        MaxMp = maxMp;
        CreatedAtUtc = createdAtUtc;
        LastMoveAtUtc = createdAtUtc;
        Revision = 1;
    }

    public string SessionId { get; }
    public string CharacterId { get; }
    public string ClassId { get; }
    public string FloorId { get; set; } = "OVERWORLD";
    public int Level { get; set; } = 1;
    public string MapId { get; set; }
    public DateTimeOffset CreatedAtUtc { get; }
    public object SyncRoot { get; } = new();

    public double X { get; set; }
    public double Y { get; set; }
    public int Hp { get; set; }
    public int MaxHp { get; set; }
    public int Mp { get; set; }
    public int MaxMp { get; set; }
    public int SwordIntent { get; set; }
    public long Revision { get; set; }
    public int LastInputSequence { get; set; }
    public DateTimeOffset LastMoveAtUtc { get; set; }
}
