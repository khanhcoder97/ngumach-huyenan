using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public sealed class QuestTalkOptions
{
    public const string SectionName = "P1:QuestTalk";

    public bool Enabled { get; set; }

    // DEC-TUTORIAL-TRANSPORT-20261106: "khoảng cách tối đa 5 WU tới anchor của NPC".
    // The same 5 the accept and turn-in verbs already ship, not a new number.
    public double MaxInteractionDistanceWu { get; set; } = 5;
}

public static class QuestTalkOptionsValidator
{
    public static void Validate(QuestTalkOptions options)
    {
        if (!double.IsFinite(options.MaxInteractionDistanceWu) ||
            options.MaxInteractionDistanceWu <= 0)
        {
            throw new InvalidOperationException(
                "P1:QuestTalk:MaxInteractionDistanceWu must be greater than zero.");
        }
    }
}

public static class TalkErrorCodes
{
    public const string UnknownNode = "narrative_unknown_node";
    public const string ChoiceRequired = "narrative_choice_required";
    public const string NotRevealed = "invalid_transition";
    public const string WrongSpeaker = "npc_mismatch";
    public const string OutOfRange = "out_of_range";
    public const string QuestNotFound = "quest_not_found";
    public const string IdempotencyConflict = "idempotency_conflict";
}

// The receipt-shaped answer the wire carries. It has no XP, no reward, no unlock,
// no chapter field and no destination on purpose: DEC-TUTORIAL-TRANSPORT-20261106
// grants none of those through this verb, and a field that can never be filled is
// the clearest statement of that in the contract itself.
public sealed record TalkResult(
    string QuestId,
    string? ObjectiveId,
    string NpcId,
    string NodeId,
    bool Credited,
    bool Replayed,
    string? AppliedFlag,
    string? EventId,
    long Revision);

public sealed record TalkOutcome(
    bool Accepted,
    TalkResult? Result,
    string? Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors)
{
    public static TalkOutcome Success(TalkResult result) =>
        new(true, result, null, false, Array.Empty<string>());

    public static TalkOutcome Rejected(
        string code,
        bool retryable,
        IReadOnlyList<string>? fieldErrors = null) =>
        new(false, null, code, retryable, fieldErrors ?? Array.Empty<string>());
}

// POST /p1/quests/talk over the narrative domain that already exists
// (`NarrativeService`, shipped by Q-C2 with its reveal conditions and flag store).
// This service does not re-implement conversation logic: it owns the four things a
// wire surface has and the domain cannot - who is asking, whether they are standing
// at the NPC, whether this exact request was already answered, and which objective
// the credit belongs to.
//
// Two rules from the decision shape the whole method:
//   * The client names ONLY `npcId` and `nodeId`. The quest is derived from the node
//     (`NarrativeNode.QuestId`), never requested, so a client cannot pick which quest
//     a line of dialogue advances; and the first node is never auto-selected - an
//     unknown or choice-requiring node is refused instead of guessed.
//   * A closed reveal gate answers `invalid_transition` naming `revealGate`. It is
//     not `quest_not_found`: the quest exists, the character simply has not earned
//     the right to hear the line yet, and pretending otherwise would hide the exact
//     reason a player is stuck.
public sealed class QuestTalkService
{
    private const string GroundFloor = "OVERWORLD";

    // The sourced dedupe tuple is character + quest attempt + objective/node. P1 has
    // no attempt lifecycle to read (the escort machine documents the same gap and
    // keeps the component at its first value), so the attempt here is that same first
    // value rather than a number invented for this route. Everything else in the key
    // is real and per-character.
    public const string QuestAttemptId = "1";

    private readonly NarrativeNodeCatalog _nodes;
    private readonly NarrativeService _narrative;
    private readonly IQuestService _quests;
    private readonly IQuestCatalog _catalog;
    private readonly NpcAnchorCatalog _anchors;
    private readonly QuestTalkOptions _options;
    private readonly Dictionary<(string CharacterId, string Key), (string RequestHash, TalkResult Result)>
        _entries = new();

    public QuestTalkService(
        NarrativeNodeCatalog nodes,
        NarrativeService narrative,
        IQuestService quests,
        IQuestCatalog catalog,
        NpcAnchorCatalog anchors,
        QuestTalkOptions options)
    {
        _nodes = nodes;
        _narrative = narrative;
        _quests = quests;
        _catalog = catalog;
        _anchors = anchors;
        _options = options;
    }

    public TalkOutcome Talk(
        PlayerSession actor,
        string npcId,
        string nodeId,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var key = (actor.CharacterId, idempotencyKey);
        var requestHash = Hash(npcId, nodeId);
        lock (actor.SyncRoot)
        lock (_entries)
        {
            // A receipt remains readable after its own credit changes the reveal gate.
            if (_entries.TryGetValue(key, out var previous))
            {
                if (!string.Equals(previous.RequestHash, requestHash, StringComparison.Ordinal))
                {
                    return TalkOutcome.Rejected(
                        TalkErrorCodes.IdempotencyConflict, retryable: false, ["idempotencyKey"]);
                }

                return TalkOutcome.Success(previous.Result with { Replayed = true });
            }

            if (!_nodes.TryGet(nodeId, out var node))
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.UnknownNode, retryable: false, ["payload.nodeId"]);
            }

            if (!string.Equals(node.SpeakerNpcId, npcId, StringComparison.Ordinal))
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.WrongSpeaker, retryable: false, ["payload.npcId"]);
            }

            if (node.Choices.Count > 0)
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.ChoiceRequired, retryable: false, ["payload.nodeId"]);
            }

            var questId = node.QuestId;
            if (!_catalog.TryGet(questId, out var definition))
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.QuestNotFound, retryable: false, ["payload.nodeId"]);
            }

            if (!_anchors.TryResolve(npcId, actor.MapId, out var anchor) ||
                !string.Equals(anchor.FloorId, GroundFloor, StringComparison.Ordinal) ||
                !string.Equals(actor.FloorId, anchor.FloorId, StringComparison.Ordinal))
            {
                return TalkOutcome.Rejected(TalkErrorCodes.OutOfRange, retryable: true);
            }

            var deltaX = actor.X - anchor.X;
            var deltaY = actor.Y - anchor.Y;
            if (Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY)) >
                _options.MaxInteractionDistanceWu + 1e-9)
            {
                return TalkOutcome.Rejected(TalkErrorCodes.OutOfRange, retryable: true);
            }

            var before = _quests.GetState(actor, questId).State;
            if (!string.Equals(node.ConditionKey,
                    NarrativeConditions.ForQuestState(before?.State), StringComparison.Ordinal))
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.NotRevealed, retryable: true, ["revealGate"]);
            }

            // DEC-TUTORIAL-CLOSURE-20261108: the overlay node binds a map/floor and the
            // objectives that must already be committed. A fresh TALK that misses them is
            // refused here rather than entered with zero credit - the ordered objective
            // gate would otherwise silently no-op and hide why the player is stuck. The
            // baseline nodes carry no binding (null), so their behaviour is unchanged.
            if (node.RequiredMapId is not null &&
                !string.Equals(node.RequiredMapId, actor.MapId, StringComparison.Ordinal))
            {
                return TalkOutcome.Rejected(TalkErrorCodes.OutOfRange, retryable: true, ["map"]);
            }

            if (node.RequiredFloorId is not null &&
                !string.Equals(node.RequiredFloorId, actor.FloorId, StringComparison.Ordinal))
            {
                return TalkOutcome.Rejected(TalkErrorCodes.OutOfRange, retryable: true, ["floor"]);
            }

            if (node.RequiredCompletedObjectiveIds is { Count: > 0 } requiredIds)
            {
                foreach (var requiredId in requiredIds)
                {
                    var requiredObjective = definition.Objectives.FirstOrDefault(candidate =>
                        string.Equals(candidate.ObjectiveId, requiredId, StringComparison.Ordinal));
                    if (requiredObjective is null ||
                        Counter(before?.ObjectiveCounters, requiredObjective) < requiredObjective.Count)
                    {
                        return TalkOutcome.Rejected(
                            TalkErrorCodes.NotRevealed, retryable: true, ["prerequisiteObjective"]);
                    }
                }
            }

            var objective = definition.Objectives.FirstOrDefault(candidate =>
                string.Equals(candidate.Type, QuestObjectiveTypes.Talk, StringComparison.Ordinal) &&
                candidate.TargetIds.Any(target =>
                    string.Equals(target, npcId, StringComparison.Ordinal)));
            var counterBefore = Counter(before?.ObjectiveCounters, objective);
            var entered = _narrative.Enter(actor, questId, npcId, nodeId);
            if (!entered.Entered)
            {
                return TalkOutcome.Rejected(
                    TalkErrorCodes.NotRevealed, retryable: true, ["revealGate"]);
            }

            var after = _quests.GetState(actor, questId).State;
            var credited = objective is not null && Counter(after?.ObjectiveCounters, objective) > counterBefore;
            var eventId = credited
                ? "PQTALK_" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
                        string.Join('|', actor.CharacterId, QuestAttemptId, questId,
                            objective!.ObjectiveId, nodeId))))
                    .ToLowerInvariant()
                : null;

            var result = new TalkResult(
                questId,
                credited ? objective!.ObjectiveId : null,
                npcId,
                nodeId,
                credited,
                Replayed: false,
                AppliedFlag: entered.AppliedFlag,
                eventId,
                after?.Revision ?? before?.Revision ?? 0);
            _entries[key] = (requestHash, result);
            return TalkOutcome.Success(result);
        }
    }

    private static int Counter(
        IReadOnlyDictionary<string, int>? counters,
        QuestObjectiveDefinition? objective) =>
        counters is not null && objective is not null &&
        counters.TryGetValue(objective.ObjectiveId, out var value)
            ? value
            : 0;

    private static string Hash(string npcId, string nodeId) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes($"{npcId}|{nodeId}")));
}
