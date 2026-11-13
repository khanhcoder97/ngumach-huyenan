namespace NguMach.Server.Persistence;

/// <summary>
/// Raised for persistence setup/configuration failures that must fail closed
/// (migration checksum mismatch, future schema version, corrupt database).
/// </summary>
public sealed class PersistenceException : Exception
{
    public PersistenceException(string errorCode, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        ErrorCode = errorCode;
    }

    public string ErrorCode { get; }
}

public static class PersistenceErrorCodes
{
    public const string MigrationChecksumMismatch = "migration-checksum-mismatch";
    public const string MigrationFutureVersion = "migration-future-version";
    public const string MigrationFailed = "migration-failed";
    public const string DatabaseCorrupt = "database-corrupt";
    public const string BackupInvalid = "backup-invalid";
    public const string BackupHashMismatch = "backup-hash-mismatch";
    public const string RestoreFailed = "restore-failed";
    public const string InvalidArgument = "invalid-argument";
    public const string CharacterNotFound = "character-not-found";
    public const string AccountNotFound = "account-not-found";
    public const string Busy = "database-busy";
}
