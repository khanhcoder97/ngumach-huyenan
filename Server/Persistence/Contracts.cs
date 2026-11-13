namespace NguMach.Server.Persistence;

/// <summary>Status of a durable mutation attempt.</summary>
public enum MutationStatus
{
    Committed,
    Replayed,
    Rejected,
    CapacityExceeded,
    RevisionConflict,
    OwnerConflict,
    RequestConflict,
    OwnershipDenied,
    LeaseAcquired,
    LeaseRenewed,
    LeaseHeld,
    LeaseMissing,
    LeaseExpired,
    StaleFencingToken,
    Busy,
    Failed
}

/// <summary>
/// A single fenced, idempotent command. The idempotency key is global (not scoped to a
/// character or life version) so a retried death/return or reward command can never be
/// replayed as a fresh grant in a later life.
/// </summary>
public sealed record MutationRequest(
    string IdempotencyKey,
    string OwnerCharacterId,
    string Operation,
    string RequestJson,
    long ExpectedRevision,
    long FencingToken);

/// <summary>One ledger row produced by a mutation plan.</summary>
public sealed record LedgerEntry(string EntryType, string PayloadJson);

/// <summary>One outbox message produced by a mutation plan.</summary>
public sealed record OutboxMessage(string Topic, string PayloadJson);

/// <summary>
/// Pure decision returned by a domain planner. The planner runs inside the same SQL
/// transaction after CAS, ownership and lease checks; it must not perform I/O or mutate
/// external state.
/// </summary>
public sealed record PlanDecision
{
    private PlanDecision(MutationPlan? plan, MutationStatus status, string? errorCode)
    {
        Plan = plan;
        Status = status;
        ErrorCode = errorCode;
    }

    public MutationPlan? Plan { get; }

    public MutationStatus Status { get; }

    public string? ErrorCode { get; }

    public bool IsAccepted => Plan is not null;

    public static PlanDecision Accept(MutationPlan plan) =>
        new(plan ?? throw new ArgumentNullException(nameof(plan)), MutationStatus.Committed, null);

    public static PlanDecision Reject(string errorCode) =>
        new(null, MutationStatus.Rejected, errorCode);

    public static PlanDecision CapacityExceeded(string errorCode) =>
        new(null, MutationStatus.CapacityExceeded, errorCode);
}

/// <summary>Validated, ready-to-commit plan. The library hashes and stores it atomically.</summary>
public sealed record MutationPlan(string NextStateJson, IReadOnlyList<LedgerEntry> Ledger, IReadOnlyList<OutboxMessage> Outbox);

/// <summary>Context handed to a planner after all fenced checks have passed.</summary>
public sealed record MutationContext(
    string IdempotencyKey,
    string OwnerCharacterId,
    string Operation,
    string RequestJson,
    long ExpectedRevision,
    long CurrentRevision,
    string? CurrentStateJson);

/// <summary>Result of one unit-of-work call. Replays return the historical result verbatim.</summary>
public sealed record MutationOutcome(
    MutationStatus Status,
    string? ErrorCode,
    long Revision,
    string? ResultJson,
    bool Replayed,
    int LedgerEntries,
    int OutboxMessages)
{
    public bool Committed => Status == MutationStatus.Committed;

    public bool Succeeded => Status is MutationStatus.Committed or MutationStatus.Replayed;

    public static MutationOutcome Rejected(MutationStatus status, string? errorCode) =>
        new(status, errorCode, 0, null, false, 0, 0);
}
