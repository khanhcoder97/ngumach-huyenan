using System.Security.Cryptography;
using System.Text;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Teleport;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

public sealed class PortalOptions
{
    public const string SectionName = "P1:Portal";

    public bool Enabled { get; set; }

    // Not a new rule: this is the same 5 WU the accept, turn-in and talk verbs ship
    // (`P1:QuestAccept`/`P1:QuestTurnIn`/`P1:QuestTalk`), applied to standing at the
    // portal instead of at an NPC. DEC-TUTORIAL-TRANSPORT-20261106 forbids adding a
    // *new* waiting or fee rule ("không thêm yêu cầu quest ACTIVE/party hoặc
    // phí/cooldown ngoài nguồn"), and it never says a portal can be used from across
    // the map, so the shipped touch distance is the smallest sourced number available.
    // If the owner would rather portals have no range rule at all, that is one config
    // line and it should be their call, not a number I quietly drop.
    public double MaxInteractionDistanceWu { get; set; } = 5;
}

public static class PortalOptionsValidator
{
    public static void Validate(PortalOptions options)
    {
        if (!double.IsFinite(options.MaxInteractionDistanceWu) ||
            options.MaxInteractionDistanceWu <= 0)
        {
            throw new InvalidOperationException(
                "P1:Portal:MaxInteractionDistanceWu must be greater than zero.");
        }
    }
}

public sealed record AlphaPortal(
    string PortalId,
    string SourceMapId,
    double SourceXWu,
    double SourceYWu,
    string DestinationMapId,
    double DestinationXWu,
    double DestinationYWu);

// The alpha portal pair, read out of docs/production/Map_Production_Atlas_vi.md at
// the lines QOD-26 quoted (§cổng): `TP_BM_THANH_LAC` stands at (348,0) in Bến Mưa and
// arrives at Thanh Lạc (8,0) (the atlas names that arrival point `TP_TL_WEST`), and
// `TP_TL_BEN_MUA` stands at Thanh Lạc (20,0) and arrives back at Bến Mưa (348,0).
//
// Two things this deliberately does not do. It does not merge the Thanh Lạc arrival 8
// with the return portal 20 - the decision says to keep them apart, and they are
// different places on the same road. And it does not include `TP_BM_THANG_LONG`: the
// atlas puts that selector at the same (348,0) as the Thanh Lạc portal, and Thăng Long
// stays behind C1-06 ("không mở Thăng Long sớm"). A registry entry for it would be a
// route nobody approved reaching a map the alpha has no content for.
public static class AlphaPortalRegistry
{
    public static readonly IReadOnlyList<AlphaPortal> All =
    [
        new("TP_BM_THANH_LAC", "MAP_BEN_MUA", 348, 0, "MAP_THANH_LAC", 8, 0),
        new("TP_TL_BEN_MUA", "MAP_THANH_LAC", 20, 0, "MAP_BEN_MUA", 348, 0)
    ];

    public static AlphaPortal? Find(string portalId) =>
        All.FirstOrDefault(portal =>
            string.Equals(portal.PortalId, portalId, StringComparison.Ordinal));
}

public static class PortalErrorCodes
{
    public const string NotFound = "portal_not_found";
    public const string Locked = "portal_locked";
    public const string OutOfRange = "out_of_range";
    public const string NotAlive = "actor_not_alive";
    public const string IdempotencyConflict = "idempotency_conflict";
}

public sealed record PortalResult(
    string PortalId,
    string DestinationMapId,
    double DestinationXWu,
    double DestinationYWu,
    bool Applied,
    bool Replayed,
    long Revision,
    string EventId,
    int InflightCastsCancelled,
    int ReservedCountersCancelled,
    bool GuardWindowClosed);

public sealed record PortalOutcome(
    bool Accepted,
    PortalResult? Result,
    string? Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors)
{
    public static PortalOutcome Success(PortalResult result) =>
        new(true, result, null, false, Array.Empty<string>());

    public static PortalOutcome Rejected(
        string code,
        bool retryable,
        IReadOnlyList<string>? fieldErrors = null) =>
        new(false, null, code, retryable, fieldErrors ?? Array.Empty<string>());
}

// POST /p1/world/portal. The client sends exactly one thing - `portalId` - and the
// destination is whatever the registry says it is, which is the whole point of the
// decision's "server-owned destination, no arbitrary teleport".
//
// Historical receipt or conflict precedes registry lookup and fresh-state validation.
// Permission is read as the character's flag, NOT through
// `ChapterUnlockStore.AllowsPortal(character, mapId)`: that helper is destination
// specific (it only ever answers for MAP_THANH_LAC), so using it for both directions
// would lock the return leg at Thanh Lạc forever for a character who is already
// standing there. The decision pairs the two directions on the same grant, so the
// grant is what this route checks.
//
// The transition itself goes through `ITeleportService` - the map-pattern, bounds and
// revision rules already live there and are CI-covered, and a second writer of the
// same move would be a divergence waiting to happen. What that service does NOT do is
// clear combat state, and the decision requires cleanup on a map transition, so the
// cast/guard/counter teardown is done here the way `DeathReturnService` does it: close
// the guard window, cancel what the engine still has pending for this character, and
// report the counts it actually observed rather than a claimed number. Aggro needs no
// ledger: mob targeting is recomputed from distance every tick, so leaving the map
// drops it by itself.
public sealed class PortalService
{
    private readonly ITeleportService _teleport;
    private readonly ChapterUnlockStore _chapters;
    private readonly GuardWindowStore _windows;
    private readonly CombatTickEngine _engine;
    private readonly ServerClock _clock;
    private readonly PortalOptions _options;
    private readonly Dictionary<(string CharacterId, string Key), (string RequestHash, PortalResult Result)>
        _entries = new();

    public PortalService(
        ITeleportService teleport,
        ChapterUnlockStore chapters,
        GuardWindowStore windows,
        CombatTickEngine engine,
        ServerClock clock,
        PortalOptions options)
    {
        _teleport = teleport;
        _chapters = chapters;
        _windows = windows;
        _engine = engine;
        _clock = clock;
        _options = options;
    }

    private static int ObservedCancellations(IReadOnlyList<CombatEventV2> events, string type) =>
        events.Count(ev => string.Equals(ev.Type, type, StringComparison.Ordinal));

    public PortalOutcome Move(
        PlayerSession actor,
        string portalId,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var key = (actor.CharacterId, idempotencyKey);
        var requestHash = Hash(portalId);
        lock (_entries)
        {
            if (_entries.TryGetValue(key, out var previous))
            {
                if (!string.Equals(previous.RequestHash, requestHash, StringComparison.Ordinal))
                {
                    return PortalOutcome.Rejected(
                        PortalErrorCodes.IdempotencyConflict,
                        retryable: false,
                        ["idempotencyKey"]);
                }

                return PortalOutcome.Success(previous.Result with { Replayed = true });
            }

            var portal = AlphaPortalRegistry.Find(portalId);
            if (portal is null)
            {
                return PortalOutcome.Rejected(
                    PortalErrorCodes.NotFound, retryable: false, ["payload.portalId"]);
            }

            return _engine.SerializeActor(actor, () =>
            {
                if (!string.Equals(actor.MapId, portal.SourceMapId, StringComparison.Ordinal) ||
                    !string.Equals(actor.FloorId, "OVERWORLD", StringComparison.Ordinal))
                {
                    return PortalOutcome.Rejected(PortalErrorCodes.OutOfRange, retryable: true);
                }

                var deltaX = actor.X - portal.SourceXWu;
                var deltaY = actor.Y - portal.SourceYWu;
                if (Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY)) >
                    _options.MaxInteractionDistanceWu + 1e-9)
                {
                    return PortalOutcome.Rejected(PortalErrorCodes.OutOfRange, retryable: true);
                }

                if (actor.Hp <= 0)
                {
                    return PortalOutcome.Rejected(PortalErrorCodes.NotAlive, retryable: true);
                }

                if (!_chapters.HasFlag(actor.CharacterId, AlphaChapterUnlockRules.Flag))
                {
                    return PortalOutcome.Rejected(
                        PortalErrorCodes.Locked, retryable: true, ["chapterPermission"]);
                }

                var transition = _teleport.Teleport(
                    actor,
                    new TeleportCommand(
                        portal.DestinationMapId,
                        portal.DestinationXWu,
                        portal.DestinationYWu,
                        TeleportReasons.Quest));
                if (!transition.IsSuccess)
                {
                    return PortalOutcome.Rejected(
                        transition.ErrorCode ?? TeleportErrorCodes.InvalidMap,
                        transition.Retryable,
                        transition.Field is null ? Array.Empty<string>() : [transition.Field]);
                }

                var revision = transition.Snapshot!.Revision;
                var guardWasOpen = _windows.FindAny(actor.CharacterId) is { IsOpen: true };
                _windows.Close(actor.CharacterId, GuardWindowEndReasons.MapOrFloorChange);
                var cancelled = _engine.CancelPendingFor(actor.CharacterId);
                var endCount = ObservedCancellations(cancelled, CombatEventTypesV2.End);
                var cancelCount = ObservedCancellations(cancelled, CombatEventTypesV2.Cancel);
                var result = new PortalResult(
                    portal.PortalId,
                    portal.DestinationMapId,
                    portal.DestinationXWu,
                    portal.DestinationYWu,
                    Applied: true,
                    Replayed: false,
                    revision,
                    EventId(portal, actor.CharacterId),
                    endCount,
                    Math.Max(0, cancelCount - endCount),
                    guardWasOpen);
                _entries[key] = (requestHash, result);
                return PortalOutcome.Success(result);
            });
        }
    }

    private static string Hash(string portalId) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(portalId)));

    // Deterministic and per-character, so a replay of this receipt cannot be
    // confused with another character's use of the same portal.
    private static string EventId(AlphaPortal portal, string characterId) =>
        "P1PORTAL_" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
                string.Join('|', characterId, portal.PortalId, portal.DestinationMapId))))
            .ToLowerInvariant();
}
