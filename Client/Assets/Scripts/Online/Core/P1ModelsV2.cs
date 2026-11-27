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
}
