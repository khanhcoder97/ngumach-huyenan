using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using Server.Health.Gameplay.Inventory;

namespace Server.Health.Contracts;

public static class P1Json
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };
}

public static class P1Time
{
    private const string UtcFormat = "yyyy-MM-dd'T'HH:mm:ss'Z'";

    public static string ToUtcString(DateTimeOffset value) =>
        value.ToUniversalTime().ToString(UtcFormat, CultureInfo.InvariantCulture);
}

public static class P1ErrorCodes
{
    public const string InvalidPayload = "invalid_payload";
    public const string SessionNotFound = "session_not_found";
    public const string StaleSequence = "stale_sequence";
    public const string InvalidMap = "invalid_map";
    public const string MovementTooFar = "movement_too_far";
    public const string MovementBlocked = "movement_blocked";
}

public static class P1Validation
{
    private const int CharacterIdMaxLength = 64;

    private static readonly Regex CharacterIdPattern =
        new(@"^CHR_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex UtcTimestampPattern =
        new(@"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
            RegexOptions.CultureInvariant);

    private static readonly Regex TargetIdPattern =
        new(@"^[A-Z][A-Z0-9_]*$", RegexOptions.CultureInvariant);

    private static readonly Regex SkillIdPattern =
        new(@"^SK-MK-0[1-3]$", RegexOptions.CultureInvariant);

    private static readonly Regex QuestIdPattern =
        new(@"^[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{2}$", RegexOptions.CultureInvariant);

    private static readonly Regex ObjectiveIdPattern =
        new(@"^OBJ_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex NpcIdPattern =
        new(@"^NPC_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex EntityIdPattern =
        new(@"^ENT_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    // DEC-ALPHA-INTERACT-IDS-20261105: the alpha overlay's interactables are
    // addressed by their own ALPHA_ prefix, which an ENT_-only vocabulary cannot
    // name — but the approval is an exact list of the six published ids, not the
    // prefix. So the alpha set is enumerated and nothing else under ALPHA_ is
    // addressable: the training hazard (ALPHA_WAVE_BM_TRAINING) is a server-side
    // rect the wave trial reads by position, and any other ALPHA_ id is refused as
    // invalid_payload before the registry is consulted.
    public static readonly IReadOnlySet<string> AlphaInteractEntityIds =
        new HashSet<string>(StringComparer.Ordinal)
        {
            "ALPHA_OBJ_BM_FRAGMENT",
            "ALPHA_OBJ_BM_RIPPLE_01",
            "ALPHA_OBJ_BM_RIPPLE_02",
            "ALPHA_OBJ_BM_RIPPLE_03",
            "ALPHA_OBJ_BM_VILLAGER_01",
            "ALPHA_OBJ_BM_VILLAGER_02"
        };

    public static bool IsHex32(string? value)
    {
        if (value is null || value.Length != 32)
        {
            return false;
        }

        foreach (var character in value)
        {
            if (!char.IsAsciiDigit(character) && character is not (>= 'a' and <= 'f'))
            {
                return false;
            }
        }

        return true;
    }

    public static bool IsCharacterId(string? value) =>
        value is not null &&
        value.Length <= CharacterIdMaxLength &&
        CharacterIdPattern.IsMatch(value);

    public static bool IsTargetId(string? value) =>
        value is not null && TargetIdPattern.IsMatch(value);

    public static bool IsSkillId(string? value) =>
        value is not null && SkillIdPattern.IsMatch(value);

    public static bool IsQuestId(string? value) =>
        value is not null && QuestIdPattern.IsMatch(value);

    public static bool IsObjectiveId(string? value) =>
        value is not null && ObjectiveIdPattern.IsMatch(value);

    public static bool IsNpcId(string? value) =>
        value is not null && NpcIdPattern.IsMatch(value);

    public static bool IsEntityId(string? value) =>
        value is not null && EntityIdPattern.IsMatch(value);

    // What the interact route may address: a canonical ENT_ entity, or one of the
    // six alpha ids the decision published.
    public static bool IsInteractTargetId(string? value) =>
        IsEntityId(value) || (value is not null && AlphaInteractEntityIds.Contains(value));

    public static bool TryParseUtc(string? value, out DateTimeOffset parsed)
    {
        parsed = default;
        if (value is null || !UtcTimestampPattern.IsMatch(value))
        {
            return false;
        }

        return DateTimeOffset.TryParseExact(
            value,
            "yyyy-MM-dd'T'HH:mm:ss'Z'",
            CultureInfo.InvariantCulture,
            DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal,
            out parsed);
    }

    public static List<string> ValidateMoveEnvelope(MoveEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (envelope.Payload.InputSequence is null ||
            envelope.Payload.InputSequence.Value < 1)
        {
            errors.Add("payload.inputSequence");
        }

        if (!IsUnitComponent(envelope.Payload.MoveX))
        {
            errors.Add("payload.moveX");
        }

        if (!IsUnitComponent(envelope.Payload.MoveY))
        {
            errors.Add("payload.moveY");
        }

        if (envelope.Payload.ClientTimeUtc is not null &&
            !TryParseUtc(envelope.Payload.ClientTimeUtc, out _))
        {
            errors.Add("payload.clientTimeUtc");
        }

        return errors;
    }

    private static bool IsUnitComponent(double? value) =>
        value is { } component &&
        double.IsFinite(component) &&
        component >= -1 &&
        component <= 1;

    public static List<string> ValidateCombatEnvelope(CombatEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        var payload = envelope.Payload;
        if (payload.InputSequence is null || payload.InputSequence.Value < 1)
        {
            errors.Add("payload.inputSequence");
        }

        if (!IsSkillId(payload.SkillId))
        {
            errors.Add("payload.skillId");
        }

        if (payload.TargetId is not null && !IsTargetId(payload.TargetId))
        {
            errors.Add("payload.targetId");
        }

        if (!IsUnitComponent(payload.AimX))
        {
            errors.Add("payload.aimX");
        }

        if (!IsUnitComponent(payload.AimY))
        {
            errors.Add("payload.aimY");
        }

        if (payload.ClientTimeUtc is not null &&
            !TryParseUtc(payload.ClientTimeUtc, out _))
        {
            errors.Add("payload.clientTimeUtc");
        }

        return errors;
    }

    public static List<string> ValidateQuestAcceptEnvelope(QuestAcceptEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!IsQuestId(envelope.Payload.QuestId))
        {
            errors.Add("payload.questId");
        }

        if (!IsNpcId(envelope.Payload.NpcId))
        {
            errors.Add("payload.npcId");
        }

        return errors;
    }

    public static List<string> ValidateInteractEnvelope(InteractEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!IsInteractTargetId(envelope.Payload.TargetId))
        {
            errors.Add("payload.targetId");
        }

        return errors;
    }

    private static readonly Regex NodeIdPattern = new(
        @"^[A-Z][A-Z0-9_]{2,63}$", RegexOptions.CultureInvariant);

    // A narrative node id is the catalog's own vocabulary (DLG_*): upper case, at
    // least three characters, no separators beyond underscore. Pinned to
    // TalkRequest.schema.json so the wire and this validator cannot drift.
    public static bool IsNodeId(string? value) =>
        value is not null && NodeIdPattern.IsMatch(value);

    // The two alpha route ids are the enum in PortalRequest.schema.json, and this is
    // the same list kept in one place on the server side: the registry is the source
    // of truth and an id it does not publish is refused as payload.portalId before any
    // state is read. TP_BM_THANG_LONG is absent on purpose.
    public static bool IsPortalId(string? value) =>
        Server.Health.Gameplay.Alpha.AlphaPortalRegistry.Find(value ?? string.Empty) is not null;

    public static List<string> ValidatePortalEnvelope(PortalEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateEnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!IsPortalId(envelope.Payload.PortalId))
        {
            errors.Add("payload.portalId");
        }

        return errors;
    }

    public static List<string> ValidateTalkEnvelope(TalkEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateEnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!IsNpcId(envelope.Payload.NpcId))
        {
            errors.Add("payload.npcId");
        }

        if (!IsNodeId(envelope.Payload.NodeId))
        {
            errors.Add("payload.nodeId");
        }

        return errors;
    }

    public static List<string> ValidateTurnInEnvelope(TurnInEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateEnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!IsQuestId(envelope.Payload.QuestId))
        {
            errors.Add("payload.questId");
        }

        if (!IsNpcId(envelope.Payload.NpcId))
        {
            errors.Add("payload.npcId");
        }

        return errors;
    }

    public static List<string> ValidateEquipEnvelope(EquipEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateEnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        var instanceId = envelope.Payload.ItemInstanceId;
        if (instanceId is null || instanceId.Length is < 1 or > 64)
        {
            errors.Add("payload.itemInstanceId");
        }

        if (envelope.Payload.ExpectedRevision is null or < 1)
        {
            errors.Add("payload.expectedRevision");
        }

        return errors;
    }

    public static List<string> ValidateUnequipEnvelope(UnequipEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateEnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!EquipmentSlots.IsValid(envelope.Payload.Slot))
        {
            errors.Add("payload.slot");
        }

        if (envelope.Payload.ExpectedRevision is null or < 1)
        {
            errors.Add("payload.expectedRevision");
        }

        return errors;
    }

    // The v2 inventory envelopes differ from v1 only in the schema version they
    // carry (2) and the slot vocabulary `unequip` names; the header rules are the
    // same, so the answers stay comparable across the two contract generations.
    public static List<string> ValidateEquipV2Envelope(EquipV2Envelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateV2EnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        var instanceId = envelope.Payload.ItemInstanceId;
        if (instanceId is null || instanceId.Length is < 1 or > 64)
        {
            errors.Add("payload.itemInstanceId");
        }

        if (envelope.Payload.ExpectedRevision is null or < 1)
        {
            errors.Add("payload.expectedRevision");
        }

        return errors;
    }

    public static List<string> ValidateUnequipV2Envelope(UnequipV2Envelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        ValidateV2EnvelopeHeader(
            errors, envelope.SchemaVersion, envelope.RequestId, envelope.IdempotencyKey,
            envelope.SentAtUtc, envelope.CharacterId);

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (!InventoryV2Slots.IsValid(envelope.Payload.SlotId))
        {
            errors.Add("payload.slotId");
        }

        if (envelope.Payload.ExpectedRevision is null or < 1)
        {
            errors.Add("payload.expectedRevision");
        }

        return errors;
    }

    // DEC-DEATH-RETURN-20261105: the payload has no fields, so there is nothing to
    // validate inside it. Presence is still required - a request that omits
    // "payload" is a different shape than the one the decision froze - and no
    // destination may ever appear here, because the anchor is server-owned.
    public static List<string> ValidateDeathReturnEnvelope(DeathReturnEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
        }

        return errors;
    }

    private static void ValidateV2EnvelopeHeader(
        List<string> errors,
        int? schemaVersion,
        string? requestId,
        string? idempotencyKey,
        string? sentAtUtc,
        string? characterId)
    {
        if (schemaVersion != 2)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(requestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(idempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(sentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(characterId))
        {
            errors.Add("characterId");
        }
    }

    private static void ValidateEnvelopeHeader(
        List<string> errors,
        int? schemaVersion,
        string? requestId,
        string? idempotencyKey,
        string? sentAtUtc,
        string? characterId)
    {
        if (schemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(requestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(idempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(sentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(characterId))
        {
            errors.Add("characterId");
        }
    }
}
