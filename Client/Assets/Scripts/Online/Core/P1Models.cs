using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace NguMach.Client.P1
{
    // Transport DTOs, deliberately independent of Unity and the server assembly.
    [Serializable] public sealed class P1Envelope<T>
    {
        public int schemaVersion = 1;
        public string requestId, idempotencyKey, sentAtUtc, characterId;
        public T payload;
    }
    [Serializable] public sealed class P1Response<T>
    {
        [JsonProperty(Required = Required.Always)] public int schemaVersion;
        [JsonProperty(Required = Required.Always)] public string requestId;
        public string sessionId, serverTimeUtc;
        public long? revision;
        public T result;
        public P1Error error;
    }
    [Serializable] public sealed class P1Error
    {
        public string code, messageKey, correlationId;
        public bool retryable;
        public string[] fieldErrors;
    }
    [Serializable] public sealed class P1World
    {
        [JsonProperty(Required = Required.Always)] public string mapId;
        [JsonProperty(Required = Required.Always)] public long serverTick, revision;
        public string serverTimeUtc;
        [JsonProperty(Required = Required.Always)] public P1Self self;
        [JsonProperty(Required = Required.Always)] public P1Entity[] entities;
    }
    [Serializable] public sealed class P1Self
    {
        [JsonProperty(Required = Required.Always)] public string characterId, classId;
        [JsonProperty(Required = Required.Always)] public double x, y;
        [JsonProperty(Required = Required.Always)] public int hp, maxHp, mp, maxMp, swordIntent;
    }
    [Serializable] public sealed class P1Entity
    {
        public string entityId, kind, state, telegraphId;
        public double x, y;
        public int hp, maxHp;
    }
    [Serializable] public sealed class P1Quest
    {
        [JsonProperty(Required = Required.Always)] public string questId, state, stepId;
        [JsonProperty(Required = Required.Always)] public Dictionary<string, int> objectiveCounters;
        [JsonProperty(Required = Required.Always)] public long revision;
    }
    [Serializable] public sealed class P1Inventory
    {
        [JsonProperty(Required = Required.Always)] public long inventoryRevision;
        [JsonProperty(Required = Required.Always)] public P1Item[] items;
        [JsonProperty(Required = Required.Always)] public P1Currency[] currencies;
    }
    [Serializable] public sealed class P1Item
    {
        public string instanceId, templateId, location, slot;
        public int stack, durability, version;
    }
    [Serializable] public sealed class P1Currency { public string currencyId; public long amount; }
    [Serializable] public sealed class P1CombatEvent
    {
        public int schemaVersion;
        public string eventId, eventType, aggregateId, emittedAtUtc;
        public long aggregateRevision;
        public P1CombatPayload payload;
    }
    [Serializable] public sealed class P1CombatPayload
    {
        public string sourceId, targetId, skillId, cooldownEndsAtUtc;
        public int? damage;
        public bool? hit;
    }
    [Serializable] public sealed class P1SessionRequest { public string classId = "CLASS_MINH_KIEM"; }
    [Serializable] public sealed class P1Move { public int inputSequence; public double moveX, moveY; }
    [Serializable] public sealed class P1Cast
    {
        public int inputSequence;
        public string skillId, targetId;
        public double aimX, aimY;
    }
    [Serializable] public sealed class P1QuestAccept { public string questId, npcId; }

    public enum P1ConnectionState { Disconnected, Connecting, Ready, NeedsResync, UncertainMutation, Expired }

    public sealed class P1Request
    {
        public string Method { get; private set; }
        public string Path { get; private set; }
        public string Body { get; private set; }
        public string SessionId { get; private set; }
        public string CorrelationId { get; private set; }
        public P1Request(string method, string path, string body, string session, string correlation)
        { Method = method; Path = path; Body = body; SessionId = session; CorrelationId = correlation; }
    }
    public sealed class P1HttpReply
    {
        public int StatusCode;
        public string Body, CorrelationId;
    }
    public sealed class P1Result
    {
        public bool Success;
        public string Code, CorrelationId;
        public static P1Result Ok() { return new P1Result { Success = true }; }
        public static P1Result Fail(string code, string correlation = null)
        { return new P1Result { Code = code, CorrelationId = correlation }; }
    }
}
