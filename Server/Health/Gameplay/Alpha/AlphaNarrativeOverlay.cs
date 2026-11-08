using System.Text.Json;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

// WO32 item 1 / DEC-TUTORIAL-CLOSURE-20261108: the owner-approved source that closes
// the P00-05 tutorial. The narrative side adds ONE node (DLG_P00_05_CLASS_CONFIRM,
// spoken by NPC_CLASS_TRIAL) over the 229-node baseline and repoints the graph
// CLUE -> CLASS_CONFIRM -> TURN_IN. It is merged only while P1:AlphaProfile:Enabled
// is true; with the gate off the baseline catalog is returned untouched, so the
// production bundle is never rewritten by this path.
//
// The decision is explicit that this node confirms the server-created class and
// grants nothing itself (classPolicy CONFIRM_SERVER_CHARACTER_CLASS_NO_SELECTION_OR_RESPEC,
// rewardPolicy NO_GRANT_NO_TURNIN_NO_UNLOCK): the credit is one TALK objective, and
// the reward/chapter consequence stays with the separate turn-in verb. The loader
// pins those two policy tokens so a source edit that turned the node into a reward
// or a respec fails startup instead of silently shipping it.
public sealed record AlphaNarrativeOverlay(
    string NodeId,
    string QuestId,
    string GraphId,
    int Order,
    string Type,
    string SpeakerNpcId,
    string ConditionKey,
    string TextKey,
    string TextVi,
    string OnEnterEvent,
    string NextNodeId,
    string SourceStatus,
    string BindObjectiveId,
    IReadOnlyList<string> RequiredCompletedObjectiveIds,
    string RequiredMapId,
    string RequiredFloorId,
    IReadOnlyDictionary<string, JsonElement> GraphPatch,
    string ClassPolicy,
    string RewardPolicy);

public static class AlphaNarrativeOverlayLoader
{
    public const string RelativePath =
        "Implementation/Content/DesignBaselines/tutorial_closure_20261108.json";

    public const string DecisionId = "DEC-TUTORIAL-CLOSURE-20261108";
    public const string ApprovedStatus = "APPROVED_FOR_PRIVATE_ALPHA_IMPLEMENTATION";
    public const string ClassPolicy = "CONFIRM_SERVER_CHARACTER_CLASS_NO_SELECTION_OR_RESPEC";
    public const string RewardPolicy = "NO_GRANT_NO_TURNIN_NO_UNLOCK";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly HashSet<string> NodeTypes = new(StringComparer.Ordinal)
    {
        "OFFER", "CLUE", "CHOICE", "TURN_IN"
    };

    public static string Discover(
        Microsoft.Extensions.Configuration.IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:TutorialClosurePath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:TutorialClosurePath points to '{resolved}', which does not exist.");
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
            $"Could not locate {RelativePath}. Set Content:TutorialClosurePath or run from the repository.");
    }

    public static AlphaNarrativeOverlay Load(string path)
    {
        using var stream = File.OpenRead(path);
        var file = JsonSerializer.Deserialize<ClosureFile>(stream, JsonOptions)
            ?? throw new InvalidOperationException($"{path}: file is empty.");

        if (file.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
        }

        if (!string.Equals(file.DecisionId, DecisionId, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: decisionId '{file.DecisionId}' is not {DecisionId}.");
        }

        if (!string.Equals(file.Status, ApprovedStatus, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: status '{file.Status}' is not {ApprovedStatus}; " +
                "the narrative overlay only loads from the owner-approved private-alpha source.");
        }

        if (file.ProductionEnabled)
        {
            throw new InvalidOperationException(
                $"{path}: productionEnabled must be false; this overlay is private-alpha only.");
        }

        var overlay = file.NarrativeOverlay
            ?? throw new InvalidOperationException($"{path}: narrativeOverlay is missing.");

        RequireToken(path, "nodeId", overlay.NodeId);
        RequireToken(path, "questId", overlay.QuestId);
        RequireToken(path, "graphId", overlay.GraphId);
        RequireToken(path, "speakerNpcId", overlay.SpeakerNpcId);
        RequireToken(path, "textKey", overlay.TextKey);
        RequireToken(path, "nextNodeId", overlay.NextNodeId);
        RequireToken(path, "bindObjectiveId", overlay.BindObjectiveId);
        RequireToken(path, "requiredMapId", overlay.RequiredMapId);
        RequireToken(path, "requiredFloorId", overlay.RequiredFloorId);
        RequireToken(path, "sourceStatus", overlay.SourceStatus);

        if (string.IsNullOrWhiteSpace(overlay.TextVi))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.textVi must carry the approved line.");
        }

        if (overlay.Order <= 0)
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.order must be positive.");
        }

        if (!NodeTypes.Contains(overlay.Type ?? string.Empty))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.type '{overlay.Type}' is not a known node type.");
        }

        if (!NarrativeConditions.IsKnown(overlay.ConditionKey))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.conditionKey '{overlay.ConditionKey}' is unknown.");
        }

        if (!NarrativeEnterEvents.IsKnown(overlay.OnEnterEvent))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.onEnterEvent '{overlay.OnEnterEvent}' is unknown.");
        }

        // This overlay path ships the no-choice CLUE node only. A flag or a branch
        // would need the baseline flag vocabulary merged too, which the decision does
        // not approve, so a non-null setFlag/choiceGroupId or any choice fails here.
        if (overlay.SetFlag is not null || overlay.ChoiceGroupId is not null ||
            (overlay.Choices is not null && overlay.Choices.Count > 0))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay must set no flag and carry no choices.");
        }

        if (!string.Equals(overlay.ClassPolicy, ClassPolicy, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.classPolicy '{overlay.ClassPolicy}' is not {ClassPolicy}.");
        }

        if (!string.Equals(overlay.RewardPolicy, RewardPolicy, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.rewardPolicy '{overlay.RewardPolicy}' is not {RewardPolicy}.");
        }

        var required = overlay.RequiredCompletedObjectiveIds ?? [];
        if (required.Count == 0 || required.Any(string.IsNullOrWhiteSpace))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.requiredCompletedObjectiveIds must name at least one objective.");
        }

        var patch = overlay.GraphPatch ?? new Dictionary<string, JsonElement>();
        if (patch.Count == 0)
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.graphPatch must repoint the baseline graph.");
        }

        return new AlphaNarrativeOverlay(
            overlay.NodeId!,
            overlay.QuestId!,
            overlay.GraphId!,
            overlay.Order,
            overlay.Type!,
            overlay.SpeakerNpcId!,
            overlay.ConditionKey!,
            overlay.TextKey!,
            overlay.TextVi!,
            overlay.OnEnterEvent!,
            overlay.NextNodeId!,
            overlay.SourceStatus!,
            overlay.BindObjectiveId!,
            required,
            overlay.RequiredMapId!,
            overlay.RequiredFloorId!,
            patch,
            overlay.ClassPolicy!,
            overlay.RewardPolicy!);
    }

    private static void RequireToken(string path, string field, string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new InvalidOperationException(
                $"{path}: narrativeOverlay.{field} must not be empty.");
        }
    }

    private sealed class ClosureFile
    {
        public int SchemaVersion { get; init; }
        public string? DecisionId { get; init; }
        public string? Status { get; init; }
        public bool ProductionEnabled { get; init; }
        public OverlayFile? NarrativeOverlay { get; init; }
    }

    private sealed class OverlayFile
    {
        public string? NodeId { get; init; }
        public string? QuestId { get; init; }
        public string? GraphId { get; init; }
        public int Order { get; init; }
        public string? Type { get; init; }
        public string? SpeakerNpcId { get; init; }
        public string? ConditionKey { get; init; }
        public string? TextKey { get; init; }
        public string? TextVi { get; init; }
        public string? OnEnterEvent { get; init; }
        public string? NextNodeId { get; init; }
        public string? SetFlag { get; init; }
        public string? ChoiceGroupId { get; init; }
        public List<JsonElement>? Choices { get; init; }
        public string? SourceStatus { get; init; }
        public string? BindObjectiveId { get; init; }
        public List<string>? RequiredCompletedObjectiveIds { get; init; }
        public string? RequiredMapId { get; init; }
        public string? RequiredFloorId { get; init; }
        public Dictionary<string, JsonElement>? GraphPatch { get; init; }
        public string? ClassPolicy { get; init; }
        public string? RewardPolicy { get; init; }
    }
}

// Mirrors AlphaQuestCatalogMerger: a pure addition over the base catalog that fails
// startup if the approved node no longer binds to the content it claims. Every
// binding the decision names is checked against the authoritative catalogs (quest
// objectives and NPC anchors), not against prose, so a renamed objective or a moved
// NPC anchor is a startup error rather than a runtime refusal nobody can trace.
public static class AlphaNarrativeOverlayMerger
{
    public static NarrativeNodeCatalog Merge(
        NarrativeNodeCatalog baseCatalog,
        AlphaNarrativeOverlay overlay,
        IQuestCatalog questCatalog,
        NpcAnchorCatalog anchors)
    {
        ArgumentNullException.ThrowIfNull(baseCatalog);
        ArgumentNullException.ThrowIfNull(overlay);
        ArgumentNullException.ThrowIfNull(questCatalog);
        ArgumentNullException.ThrowIfNull(anchors);

        if (!questCatalog.TryGet(overlay.QuestId, out var definition))
        {
            throw new InvalidOperationException(
                $"narrative overlay quest '{overlay.QuestId}' is not in the running quest catalog.");
        }

        if (definition.IsBlocked)
        {
            throw new InvalidOperationException(
                $"narrative overlay quest '{overlay.QuestId}' is BLOCKED; the alpha pack must activate it.");
        }

        var bindObjective = definition.Objectives.FirstOrDefault(objective =>
            string.Equals(objective.ObjectiveId, overlay.BindObjectiveId, StringComparison.Ordinal));
        if (bindObjective is null)
        {
            throw new InvalidOperationException(
                $"narrative overlay bindObjectiveId '{overlay.BindObjectiveId}' is not an objective of " +
                $"'{overlay.QuestId}'.");
        }

        if (!string.Equals(bindObjective.Type, QuestObjectiveTypes.Talk, StringComparison.Ordinal) ||
            !bindObjective.TargetIds.Contains(overlay.SpeakerNpcId, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"narrative overlay bindObjectiveId '{overlay.BindObjectiveId}' must be a TALK objective " +
                $"targeting '{overlay.SpeakerNpcId}'.");
        }

        foreach (var requiredId in overlay.RequiredCompletedObjectiveIds)
        {
            if (!definition.Objectives.Any(objective =>
                    string.Equals(objective.ObjectiveId, requiredId, StringComparison.Ordinal)))
            {
                throw new InvalidOperationException(
                    $"narrative overlay requiredCompletedObjectiveId '{requiredId}' is not an objective of " +
                    $"'{overlay.QuestId}'.");
            }
        }

        if (!anchors.TryResolve(overlay.SpeakerNpcId, overlay.RequiredMapId, out var anchor) ||
            !string.Equals(anchor.FloorId, overlay.RequiredFloorId, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"narrative overlay speaker '{overlay.SpeakerNpcId}' has no anchor on " +
                $"{overlay.RequiredMapId}/{overlay.RequiredFloorId}.");
        }

        var graphNodes = baseCatalog.ForQuest(overlay.QuestId);
        if (graphNodes.Count == 0 ||
            !graphNodes.Any(node => string.Equals(node.GraphId, overlay.GraphId, StringComparison.Ordinal)))
        {
            throw new InvalidOperationException(
                $"narrative overlay graph '{overlay.GraphId}' for '{overlay.QuestId}' is not in the baseline.");
        }

        if (!baseCatalog.TryGet(overlay.NextNodeId, out _))
        {
            throw new InvalidOperationException(
                $"narrative overlay nextNodeId '{overlay.NextNodeId}' is not in the baseline.");
        }

        var replacements = new Dictionary<string, NarrativeNode>(StringComparer.Ordinal);
        foreach (var (key, value) in overlay.GraphPatch)
        {
            var dot = key.IndexOf('.');
            if (dot <= 0 || dot == key.Length - 1)
            {
                throw new InvalidOperationException(
                    $"narrative overlay graphPatch key '{key}' must be 'nodeId.field'.");
            }

            var nodeId = key[..dot];
            var field = key[(dot + 1)..];
            if (!baseCatalog.TryGet(nodeId, out var baseNode))
            {
                throw new InvalidOperationException(
                    $"narrative overlay graphPatch targets node '{nodeId}', which the baseline does not publish.");
            }

            NarrativeNode replacement;
            if (string.Equals(field, "nextNodeId", StringComparison.Ordinal))
            {
                if (value.ValueKind != JsonValueKind.String || value.GetString() is not { } next)
                {
                    throw new InvalidOperationException(
                        $"narrative overlay graphPatch '{key}' must be a string node id.");
                }

                replacement = baseNode with { NextNodeId = next };
            }
            else if (string.Equals(field, "order", StringComparison.Ordinal))
            {
                if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out var order))
                {
                    throw new InvalidOperationException(
                        $"narrative overlay graphPatch '{key}' must be an integer order.");
                }

                replacement = baseNode with { Order = order };
            }
            else
            {
                throw new InvalidOperationException(
                    $"narrative overlay graphPatch field '{field}' is not supported (nextNodeId, order).");
            }

            if (!replacements.TryAdd(nodeId, replacement))
            {
                throw new InvalidOperationException(
                    $"narrative overlay graphPatch patches node '{nodeId}' more than once.");
            }
        }

        var node = new NarrativeNode(
            overlay.QuestId,
            overlay.GraphId,
            overlay.NodeId,
            overlay.Order,
            overlay.Type,
            overlay.SpeakerNpcId,
            overlay.ConditionKey,
            overlay.TextKey,
            overlay.NextNodeId,
            overlay.OnEnterEvent,
            Flag: null,
            ChoiceGroupId: null,
            Choices: Array.Empty<NarrativeNodeChoice>(),
            BindObjectiveId: overlay.BindObjectiveId,
            RequiredCompletedObjectiveIds: overlay.RequiredCompletedObjectiveIds,
            RequiredMapId: overlay.RequiredMapId,
            RequiredFloorId: overlay.RequiredFloorId);

        return baseCatalog.WithOverlay(node, replacements);
    }
}