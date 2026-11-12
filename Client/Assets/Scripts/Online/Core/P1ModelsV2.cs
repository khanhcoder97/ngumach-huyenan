using System;
using Newtonsoft.Json;

namespace NguMach.Client.P1
{
    [Serializable] public sealed class P1WorldV2
    {
        [JsonProperty(Required = Required.Always)] public int schemaVersion;
        [JsonProperty(Required = Required.Always)] public string mapId, mapInstanceId, floorId, phase, serverTimeUtc;
        [JsonProperty(Required = Required.Always)] public long serverTick, revision;
        [JsonProperty(Required = Required.Always)] public P1Audience audience;
        [JsonProperty(Required = Required.Always)] public P1Self self;
        [JsonProperty(Required = Required.Always)] public P1EntityV2[] entities;
    }
    [Serializable] public sealed class P1Audience
    {
        [JsonProperty(Required = Required.Always)] public double aoiEnterWu, aoiLeaveWu;
    }
    [Serializable] public sealed class P1EntityV2
    {
        [JsonProperty(Required = Required.Always)] public string entityId, kind, mapInstanceId, floorId, phase, state, healthState;
        [JsonProperty(Required = Required.Always)] public bool targetable;
        [JsonProperty(Required = Required.Always)] public double x, y;
        [JsonProperty(Required = Required.Always)] public int hp, maxHp;
        [JsonProperty(Required = Required.Always)] public long revision, lifeId;
        public string availability;
    }
    [Serializable] public sealed class P1CastV2
    {
        public string actionKind, skillId, targetId, clientTimeUtc;
        public int inputSequence;
        public double aimX, aimY;
    }
    [Serializable] public sealed class P1CastResultV2
    {
        [JsonProperty(Required = Required.Always)] public string castId, actionKind, cooldownEndUtc;
        public string skillId;
        [JsonProperty(Required = Required.Always)] public int mp, mpCost;
        // Existing v2 server and its self-check return the last accepted sequence, despite the wire name.
        [JsonProperty("nextInputSequence", Required = Required.Always)] public int acceptedInputSequence;
        [JsonProperty(Required = Required.Always)] public P1EventV2[] events;
    }
    [Serializable] public sealed class P1EventV2
    {
        [JsonProperty(Required = Required.Always)] public string eventId, type, castId, actorId, mapInstanceId, floorId, emittedAtUtc;
        [JsonProperty(Required = Required.Always)] public long cursor, sourceRevision, serverTick;
        public string targetId;
        public long? targetLifeId, targetRevision;
        public int? hitIndex;
        public P1ImpactResultV2 result;
    }
    [Serializable] public sealed class P1ImpactResultV2
    {
        [JsonProperty(Required = Required.Always)] public bool hit, crit, immune;
        [JsonProperty(Required = Required.Always)] public int amount, absorbed, hpDamage;
    }
    [Serializable] public sealed class P1EventPageV2
    {
        [JsonProperty(Required = Required.Always)] public int schemaVersion;
        [JsonProperty(Required = Required.Always)] public string sessionId;
        [JsonProperty(Required = Required.Always)] public long nextCursor;
        [JsonProperty(Required = Required.Always)] public bool resyncRequired;
        public string resyncReason;
        [JsonProperty(Required = Required.Always)] public P1EventV2[] events;
    }
    [Serializable] public sealed class P1Interact { public string targetId; }
    [Serializable] public sealed class P1InteractResult
    {
        [JsonProperty(Required = Required.Always)] public string interactionId, targetId, recordId, kind, outcome, targetState, claimedAtUtc;
        public string respawnAtUtc;
        [JsonProperty(Required = Required.Always)] public P1Quest[] questUpdates;
    }
    [Serializable] public sealed class P1TurnInResult
    {
        [JsonProperty(Required = Required.Always)] public P1Quest questState;
        [JsonProperty(Required = Required.Always)] public P1RewardReceipt rewards;
        [JsonProperty(Required = Required.Always)] public string[] unlocks;
    }
    [Serializable] public sealed class P1RewardReceipt
    {
        [JsonProperty(Required = Required.Always)] public P1Currency[] currency;
        [JsonProperty(Required = Required.Always)] public P1RewardItem[] items;
        [JsonProperty(Required = Required.Always)] public P1RewardXp xp;
    }
    [Serializable] public sealed class P1RewardItem
    {
        [JsonProperty(Required = Required.Always)] public string templateId, location;
        [JsonProperty(Required = Required.Always)] public int stack;
    }
    [Serializable] public sealed class P1RewardXp
    {
        [JsonProperty(Required = Required.Always)] public string xpRule;
        [JsonProperty(Required = Required.Always)] public bool applied;
    }

    // P1/InventorySnapshotV2.schema.json (Qoder 77bc3a6). Side-by-side with the
    // frozen v1 five-slot contract; slots always carries all twelve tokens.
    [Serializable] public sealed class P1InventorySnapshotV2
    {
        [JsonProperty(Required = Required.Always)] public int schemaVersion;
        [JsonProperty(Required = Required.Always)] public string slotSpec;
        [JsonProperty(Required = Required.Always)] public long inventoryRevision;
        [JsonProperty(Required = Required.Always)] public int bagSlots;
        [JsonProperty(Required = Required.Always)] public P1EquipmentSlotV2[] slots;
        [JsonProperty(Required = Required.Always)] public P1ItemV2[] bag;
        [JsonProperty(Required = Required.Always)] public P1UnsupportedEquipV2[] unsupported;
        [JsonProperty(Required = Required.Always)] public P1Currency[] currencies;
    }
    [Serializable] public sealed class P1EquipmentSlotV2
    {
        [JsonProperty(Required = Required.Always)] public string slotId;
        [JsonProperty(Required = Required.AllowNull)] public P1ItemV2 item;
    }
    [Serializable] public sealed class P1ItemV2
    {
        [JsonProperty(Required = Required.Always)] public string instanceId, templateId;
        [JsonProperty(Required = Required.Always)] public int stack;
        [JsonProperty(Required = Required.Always)] public string location;
        [JsonProperty(Required = Required.AllowNull)] public string slotId;
        [JsonProperty(Required = Required.Always)] public int durability;
        [JsonProperty(Required = Required.Always)] public int version;
    }
    [Serializable] public sealed class P1UnsupportedEquipV2
    {
        [JsonProperty(Required = Required.Always)] public string instanceId, templateId;
        [JsonProperty(Required = Required.AllowNull)] public string sourceSlot;
        [JsonProperty(Required = Required.Always)] public string reason;
    }
    [Serializable] public sealed class P1EquipV2
    {
        [JsonProperty(Required = Required.Always)] public string itemInstanceId;
        [JsonProperty(Required = Required.Always)] public long expectedRevision;
    }
    [Serializable] public sealed class P1UnequipV2
    {
        [JsonProperty(Required = Required.Always)] public string slotId;
        [JsonProperty(Required = Required.Always)] public long expectedRevision;
    }

    // P1/DeathReturnRequest.schema.json — payload is deliberately empty: the
    // client can only express the intent, never a map, coordinate or anchor.
    [Serializable] public sealed class P1DeathReturnIntent { }

    // P1/DeathReturnResponse.schema.json (DEC-DEATH-RETURN-20261105).
    [Serializable] public sealed class P1DeathReturnResultV1
    {
        [JsonProperty(Required = Required.Always)] public bool applied;
        [JsonProperty(Required = Required.Always)] public bool replayed;
        [JsonProperty(Required = Required.Always)] public string mapId;
        [JsonProperty(Required = Required.Always)] public double xWu, yWu;
        [JsonProperty(Required = Required.Always)] public int hp, maxHp, mp, maxMp;
        [JsonProperty(Required = Required.Always)] public long serverTick, revision;
        [JsonProperty(Required = Required.Always)] public P1DeathReturnCleared cleared;
        [JsonProperty(Required = Required.Always)] public P1DeathReturnPenalties penalties;
        [JsonProperty(Required = Required.AllowNull)] public long? nextReturnAllowedAtTick;
    }
    [Serializable] public sealed class P1DeathReturnCleared
    {
        [JsonProperty(Required = Required.Always)] public int inflightCasts, reservedCounters;
        [JsonProperty(Required = Required.Always)] public bool guardWindowClosed, movementWindowReset;
    }
    [Serializable] public sealed class P1DeathReturnPenalties
    {
        [JsonProperty(Required = Required.Always)] public int xp, currency, durability;
    }

    // P1/QuestTalkRequest.schema.json (Qoder pin 6814126) — NPC dialogue intent.
    // Gate: P1:QuestTalk:Enabled + AlphaProfile (default OFF). The client names
    // only the NPC and node; quest/attempt/objective/speaker are server-derived.
    [Serializable] public sealed class P1QuestTalkIntent
    {
        [JsonProperty(Required = Required.Always)] public string npcId;
        [JsonProperty(Required = Required.Always)] public string nodeId;
    }

    // P1/TalkResponse.schema.json (Qoder pin 6814126) — narrative credit only:
    // no XP, turn-in, chapter unlock or map movement. credited/replayed are the
    // server's decision; the nullable receipt fields are explicit on the wire.
    [Serializable] public sealed class P1QuestTalkResult
    {
        [JsonProperty(Required = Required.Always)] public string questId;
        public string objectiveId;
        [JsonProperty(Required = Required.Always)] public string npcId;
        [JsonProperty(Required = Required.Always)] public string nodeId;
        [JsonProperty(Required = Required.Always)] public bool credited;
        [JsonProperty(Required = Required.Always)] public bool replayed;
        public string appliedFlag;
        public string eventId;
        [JsonProperty(Required = Required.Always)] public long revision;
    }

    // P1/PortalRequest.schema.json (Qoder pin 6814126) — portal intent,
    // server-owned destination. Gate: P1:Portal:Enabled + AlphaProfile (OFF).
    [Serializable] public sealed class P1WorldPortalIntent
    {
        [JsonProperty(Required = Required.Always)] public string portalId;
    }

    // P1/PortalResponse.schema.json (Qoder pin 6814126) — receipt of one map
    // transition: the destination the server chose plus what the transition
    // cleared. A replay keeps the original destination; it never pulls the
    // character back.
    [Serializable] public sealed class P1WorldPortalResult
    {
        [JsonProperty(Required = Required.Always)] public string portalId;
        [JsonProperty(Required = Required.Always)] public string mapId;
        [JsonProperty(Required = Required.Always)] public double xWu, yWu;
        [JsonProperty(Required = Required.Always)] public bool applied, replayed;
        [JsonProperty(Required = Required.Always)] public long revision;
        [JsonProperty(Required = Required.Always)] public string eventId;
        public int inflightCastsCancelled, reservedCountersCancelled;
        public bool guardWindowClosed;
    }

    // QOD-28 MAP_VIEWED is approved for private-alpha but its wire schema is not
    // frozen yet (binding/schema/example pending owner approval). This model is
    // an interim acknowledgement, not a frozen contract; do not treat
    // acknowledged/serverTick as the final QOD-28 payload.
    [Serializable] public sealed class P1QuestMapViewedIntent
    {
        [JsonProperty(Required = Required.Always)] public string questId;
    }

    // Interim MAP_VIEWED acknowledgement — NOT a frozen contract (QOD-28).
    [Serializable] public sealed class P1QuestMapViewedResult
    {
        [JsonProperty(Required = Required.Always)] public string questId;
        [JsonProperty(Required = Required.Always)] public bool acknowledged;
        [JsonProperty(Required = Required.Always)] public long serverTick, revision;
    }
}
