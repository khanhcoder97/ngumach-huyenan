using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

// Q-C2: the narrative side of a quest, from the dialogue data rather than from
// prose. A node is only visible when the character's quest state matches its
// condition (the reveal gate), entering it can set one flag or progress a
// objective, and a CHOICE node must be answered with one of its own options.
// Text stays behind the text key: the server never composes dialogue, it only
// decides which line the client may show and what entering it does.
public static class NarrativeConditions
{
    public const string QuestAvailable = "QUEST_AVAILABLE";
    public const string QuestActive = "QUEST_ACTIVE";
    public const string QuestReadyToTurnIn = "QUEST_READY_TO_TURN_IN";

    public static bool IsKnown(string? value) =>
        value is QuestAvailable or QuestActive or QuestReadyToTurnIn;

    public static string? ForQuestState(string? state) => state switch
    {
        QuestStates.Available => QuestAvailable,
        QuestStates.Active => QuestActive,
        QuestStates.ReadyToTurnIn => QuestReadyToTurnIn,
        _ => null
    };
}

public static class NarrativeEnterEvents
{
    public const string AcceptQuest = "ACCEPT_QUEST";
    public const string ChoiceRequired = "CHOICE_REQUIRED";
    public const string CommitReward = "COMMIT_REWARD";
    public const string ObjectiveProgress = "OBJECTIVE_PROGRESS";

    public static bool IsKnown(string? value) =>
        value is AcceptQuest or ChoiceRequired or CommitReward or ObjectiveProgress;
}

public static class PartyPolicies
{
    // P1 has no party runtime: progression is per character and labelled as
    // such instead of implying shared credit.
    public const string SoloOnly = "SOLO_ONLY";
}

public sealed record NarrativeNodeChoice(string ChoiceId, string Flag);

public sealed record NarrativeNode(
    string QuestId,
    string GraphId,
    string NodeId,
    int Order,
    string Type,
    string SpeakerNpcId,
    string? ConditionKey,
    string? TextKey,
    string? NextNodeId,
    string? OnEnterEvent,
    string? Flag,
    string? ChoiceGroupId,
    IReadOnlyList<NarrativeNodeChoice> Choices);

public sealed class NarrativeNodeCatalog
{
    private readonly IReadOnlyDictionary<string, NarrativeNode> _nodes;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<NarrativeNode>> _byQuest;
    private readonly IReadOnlySet<string> _flags;

    private NarrativeNodeCatalog(
        IReadOnlyDictionary<string, NarrativeNode> nodes,
        IReadOnlyDictionary<string, IReadOnlyList<NarrativeNode>> byQuest,
        IReadOnlySet<string> flags)
    {
        _nodes = nodes;
        _byQuest = byQuest;
        _flags = flags;
    }

    public int Count => _nodes.Count;

    public IReadOnlySet<string> Flags => _flags;

    public bool TryGet(string nodeId, out NarrativeNode node) => _nodes.TryGetValue(nodeId, out node!);

    public IReadOnlyList<NarrativeNode> ForQuest(string questId) =>
        _byQuest.TryGetValue(questId, out var nodes) ? nodes : Array.Empty<NarrativeNode>();

    // The gate is evaluated here, not by the caller: a node whose condition does
    // not match the character's state simply does not exist for that character.
    public NarrativeNode? OfferNode(string questId, string? questState)
    {
        var condition = NarrativeConditions.ForQuestState(questState);
        if (condition is null)
        {
            return null;
        }

        foreach (var node in ForQuest(questId))
        {
            if (string.Equals(node.ConditionKey, condition, StringComparison.Ordinal))
            {
                return node;
            }
        }

        return null;
    }

    public const string RelativePath = "Implementation/Content/Runtime/narrative_nodes_v1.json";

    // Same discovery contract as the other runtime bundles: an explicit config
    // key wins, otherwise walk up from the content root looking for the file.
    public static string Discover(Microsoft.Extensions.Configuration.IConfiguration configuration,
        string contentRoot)
    {
        var configured = configuration["Content:NarrativeNodesPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:NarrativeNodesPath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);
        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < 12 && directory is not null; depth++)
            {
                var candidate = Path.Combine(directory.FullName, RelativePath);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {RelativePath}. Set Content:NarrativeNodesPath or run from the repository.");
    }

    private static readonly Regex TokenPattern =
        new(@"^[A-Z][A-Z0-9_]*$", RegexOptions.CultureInvariant);

    public static NarrativeNodeCatalog Load(string path)
    {
        using var stream = File.OpenRead(path);
        var file = JsonSerializer.Deserialize<NarrativeFile>(stream, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        }) ?? throw new InvalidOperationException($"{path}: file is empty.");

        if (file.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
        }

        var flags = new HashSet<string>(StringComparer.Ordinal);
        foreach (var flag in file.Flags ?? [])
        {
            if (!TokenPattern.IsMatch(flag))
            {
                throw new InvalidOperationException($"{path}: invalid flag '{flag}'.");
            }

            flags.Add(flag);
        }

        var nodes = new Dictionary<string, NarrativeNode>(StringComparer.Ordinal);
        var byQuest = new Dictionary<string, List<NarrativeNode>>(StringComparer.Ordinal);
        foreach (var entry in file.Nodes ?? [])
        {
            if (entry.NodeId is null || !TokenPattern.IsMatch(entry.NodeId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid nodeId '{entry.NodeId}'.");
            }

            if (!NarrativeConditions.IsKnown(entry.ConditionKey))
            {
                throw new InvalidOperationException(
                    $"{path}: node '{entry.NodeId}' has invalid conditionKey " +
                    $"'{entry.ConditionKey}'.");
            }

            if (entry.OnEnterEvent is not null && !NarrativeEnterEvents.IsKnown(entry.OnEnterEvent))
            {
                throw new InvalidOperationException(
                    $"{path}: node '{entry.NodeId}' has invalid onEnterEvent " +
                    $"'{entry.OnEnterEvent}'.");
            }

            if (entry.Flag is not null && !flags.Contains(entry.Flag))
            {
                throw new InvalidOperationException(
                    $"{path}: node '{entry.NodeId}' sets unknown flag '{entry.Flag}'.");
            }

            var choices = (entry.Choices ?? [])
                .Select(choice =>
                {
                    if (choice.ChoiceId is null || !TokenPattern.IsMatch(choice.ChoiceId) ||
                        choice.Flag is null || !flags.Contains(choice.Flag))
                    {
                        throw new InvalidOperationException(
                            $"{path}: node '{entry.NodeId}' has invalid choice " +
                            $"'{choice.ChoiceId}'/'{choice.Flag}'.");
                    }

                    return new NarrativeNodeChoice(choice.ChoiceId, choice.Flag);
                })
                .ToArray();

            if (string.Equals(entry.Type, "CHOICE", StringComparison.Ordinal) && choices.Length == 0)
            {
                throw new InvalidOperationException(
                    $"{path}: CHOICE node '{entry.NodeId}' has no options.");
            }

            var node = new NarrativeNode(
                entry.QuestId ?? string.Empty,
                entry.GraphId ?? string.Empty,
                entry.NodeId,
                entry.Order,
                entry.Type ?? string.Empty,
                entry.SpeakerNpcId ?? string.Empty,
                entry.ConditionKey,
                entry.TextKey,
                entry.NextNodeId,
                entry.OnEnterEvent,
                entry.Flag,
                entry.ChoiceGroupId,
                choices);

            if (!nodes.TryAdd(node.NodeId, node))
            {
                throw new InvalidOperationException($"{path}: duplicate nodeId '{node.NodeId}'.");
            }

            if (!byQuest.TryGetValue(node.QuestId, out var list))
            {
                list = [];
                byQuest[node.QuestId] = list;
            }

            list.Add(node);
        }

        foreach (var node in nodes.Values)
        {
            if (node.NextNodeId is not null && !nodes.ContainsKey(node.NextNodeId))
            {
                throw new InvalidOperationException(
                    $"{path}: node '{node.NodeId}' points at missing next node " +
                    $"'{node.NextNodeId}'.");
            }
        }

        return new NarrativeNodeCatalog(
            nodes,
            byQuest.ToDictionary(
                pair => pair.Key,
                pair => (IReadOnlyList<NarrativeNode>)pair.Value,
                StringComparer.Ordinal),
            flags);
    }

    private sealed class NarrativeFile
    {
        public int SchemaVersion { get; init; }
        public List<string>? Flags { get; init; }
        public List<NarrativeNodeFile>? Nodes { get; init; }
    }

    private sealed class NarrativeNodeFile
    {
        public string? QuestId { get; init; }
        public string? GraphId { get; init; }
        public string? NodeId { get; init; }
        public int Order { get; init; }
        public string? Type { get; init; }
        public string? SpeakerNpcId { get; init; }
        public string? ConditionKey { get; init; }
        public string? TextKey { get; init; }
        public string? NextNodeId { get; init; }
        public string? OnEnterEvent { get; init; }
        public string? Flag { get; init; }
        public string? ChoiceGroupId { get; init; }
        public List<NarrativeChoiceFile>? Choices { get; init; }
    }

    private sealed class NarrativeChoiceFile
    {
        public string? ChoiceId { get; init; }
        public string? Flag { get; init; }
    }
}

public static class NarrativeErrorCodes
{
    public const string UnknownNode = "narrative_unknown_node";
    public const string NotRevealed = "narrative_not_revealed";
    public const string WrongSpeaker = "narrative_wrong_speaker";
    public const string ChoiceRequired = "narrative_choice_required";
    public const string UnknownChoice = "narrative_unknown_choice";
}

public sealed record NarrativeEnterResult(
    bool Entered,
    string? ErrorCode,
    NarrativeNode? Node,
    string? NextNodeId,
    string? AppliedFlag,
    IReadOnlyList<string> ProgressedQuestIds,
    IReadOnlyList<NarrativeNodeChoice> Choices);

// Flags are per character and bounded: a long session must not grow an
// unbounded string set, and a flag outside the bundle vocabulary can never be
// written because the catalog validated every writer at load time.
public sealed class NarrativeFlagStore
{
    public const int Capacity = 128;

    private readonly ConcurrentDictionary<string, List<string>> _flags = new(StringComparer.Ordinal);
    private readonly object _sync = new();

    public bool Set(string characterId, string flag)
    {
        lock (_sync)
        {
            if (!_flags.TryGetValue(characterId, out var flags))
            {
                flags = [];
                _flags[characterId] = flags;
            }

            if (flags.Contains(flag, StringComparer.Ordinal))
            {
                return false;
            }

            flags.Add(flag);
            if (flags.Count > Capacity)
            {
                flags.RemoveAt(0);
            }

            return true;
        }
    }

    public IReadOnlyList<string> For(string characterId)
    {
        lock (_sync)
        {
            return _flags.TryGetValue(characterId, out var flags) ? [.. flags] : [];
        }
    }
}

public sealed class NarrativeService
{
    private readonly NarrativeNodeCatalog _catalog;
    private readonly IQuestService _questState;
    private readonly NarrativeFlagStore _flags;

    public NarrativeService(
        NarrativeNodeCatalog catalog,
        IQuestService questState,
        NarrativeFlagStore flags)
    {
        _catalog = catalog;
        _questState = questState;
        _flags = flags;
    }

    public string PartyPolicy => PartyPolicies.SoloOnly;

    public NarrativeEnterResult Offer(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var current = _questState.GetState(actor.CharacterId, questId).State;
        var node = _catalog.OfferNode(questId, current?.State);
        return node is null
            ? new NarrativeEnterResult(false, NarrativeErrorCodes.NotRevealed, null, null, null, [], [])
            : new NarrativeEnterResult(true, null, node, node.NextNodeId, null, [], node.Choices);
    }

    public NarrativeEnterResult Enter(
        PlayerSession actor,
        string questId,
        string npcId,
        string nodeId,
        string? choiceId = null)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!_catalog.TryGet(nodeId, out var node) ||
            !string.Equals(node.QuestId, questId, StringComparison.Ordinal))
        {
            return new NarrativeEnterResult(
                false, NarrativeErrorCodes.UnknownNode, null, null, null, [], []);
        }

        if (!string.Equals(node.SpeakerNpcId, npcId, StringComparison.Ordinal))
        {
            return new NarrativeEnterResult(
                false, NarrativeErrorCodes.WrongSpeaker, null, null, null, [], []);
        }

        var current = _questState.GetState(actor.CharacterId, questId).State;
        if (!string.Equals(
                node.ConditionKey,
                NarrativeConditions.ForQuestState(current?.State),
                StringComparison.Ordinal))
        {
            return new NarrativeEnterResult(
                false, NarrativeErrorCodes.NotRevealed, null, null, null, [], []);
        }

        string? appliedFlag = null;
        if (node.Choices.Count > 0)
        {
            if (choiceId is null)
            {
                return new NarrativeEnterResult(
                    false, NarrativeErrorCodes.ChoiceRequired, node, null, null, [], node.Choices);
            }

            var choice = node.Choices.FirstOrDefault(candidate =>
                string.Equals(candidate.ChoiceId, choiceId, StringComparison.Ordinal));
            if (choice is null)
            {
                return new NarrativeEnterResult(
                    false, NarrativeErrorCodes.UnknownChoice, node, null, null, [], node.Choices);
            }

            appliedFlag = choice.Flag;
        }
        else
        {
            appliedFlag = node.Flag;
        }

        if (appliedFlag is not null)
        {
            _flags.Set(actor.CharacterId, appliedFlag);
        }

        var progressed = new List<string>();
        if (string.Equals(
                node.OnEnterEvent, NarrativeEnterEvents.ObjectiveProgress, StringComparison.Ordinal))
        {
            var eventId = Convert.ToHexString(
                    SHA256.HashData(Encoding.UTF8.GetBytes(node.NodeId + "|" + actor.CharacterId)))
                .ToLowerInvariant()[..32];
            foreach (var state in _questState.RecordVerifiedEvent(
                         actor, eventId, QuestProgressEventTypes.Talk, npcId, actor.MapId))
            {
                progressed.Add(state.QuestId);
            }
        }

        return new NarrativeEnterResult(
            true, null, node, node.NextNodeId, appliedFlag, progressed, node.Choices);
    }
}
