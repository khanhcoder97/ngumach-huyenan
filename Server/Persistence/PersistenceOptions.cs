namespace NguMach.Server.Persistence;

/// <summary>
/// Configuration for the QR-01 SQLite persistence profile.
/// SQLite is a single-host development/test profile; the production target remains
/// the OnlineSpec PostgreSQL provider and is not replaced by this module.
/// </summary>
public sealed record PersistenceOptions
{
    public required string DatabasePath { get; init; }

    /// <summary>How long a connection waits on a locked database before failing.</summary>
    public TimeSpan BusyTimeout { get; init; } = TimeSpan.FromSeconds(10);

    /// <summary>Default lease lifetime handed out by <see cref="LeaseStore"/>.</summary>
    public TimeSpan LeaseTtl { get; init; } = TimeSpan.FromSeconds(60);

    /// <summary>
    /// Reconnect grace window counted from lease expiry. The same owner token may
    /// reacquire the lease without losing its fencing token inside this window.
    /// </summary>
    public TimeSpan ReconnectGrace { get; init; } = TimeSpan.FromSeconds(120);

    /// <summary>How long an outbox claim stays owned before another worker may retry it.</summary>
    public TimeSpan OutboxClaimTtl { get; init; } = TimeSpan.FromSeconds(30);

    public static PersistenceOptions ForFile(string databasePath) => new() { DatabasePath = databasePath };

    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(DatabasePath))
        {
            throw new ArgumentException("DatabasePath is required.", nameof(DatabasePath));
        }

        if (BusyTimeout <= TimeSpan.Zero || LeaseTtl <= TimeSpan.Zero || ReconnectGrace < TimeSpan.Zero || OutboxClaimTtl <= TimeSpan.Zero)
        {
            throw new ArgumentOutOfRangeException(nameof(PersistenceOptions), "Timeouts must be positive and ReconnectGrace must not be negative.");
        }
    }
}
