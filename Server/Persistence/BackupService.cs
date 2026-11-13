using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// SQLite backup/restore using the SQLite online backup API (never a raw copy of a live
/// WAL database). A backup is only published after integrity, schema and row counts are
/// verified, and a manifest records the SHA-256 digest of the finished file.
/// </summary>
public sealed class BackupService
{
    private readonly PersistenceDatabase _database;

    public BackupService(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
    }

    public async Task<BackupReport> CreateBackupAsync(string backupPath, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(backupPath);
        var fullBackupPath = Path.GetFullPath(backupPath);
        var fullSourcePath = Path.GetFullPath(_database.DatabasePath);
        if (string.Equals(fullBackupPath, fullSourcePath, StringComparison.OrdinalIgnoreCase))
        {
            throw new PersistenceException(PersistenceErrorCodes.InvalidArgument, "Backup path must differ from the live database path.");
        }

        Directory.CreateDirectory(Path.GetDirectoryName(fullBackupPath)!);
        var temporaryPath = fullBackupPath + ".tmp";
        File.Delete(temporaryPath);

        await using (var source = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false))
        await using (var target = new SqliteConnection(new SqliteConnectionStringBuilder
        {
            DataSource = temporaryPath,
            Mode = SqliteOpenMode.ReadWriteCreate,
            Pooling = false
        }.ToString()))
        {
            await target.OpenAsync(cancellationToken).ConfigureAwait(false);
            source.BackupDatabase(target);
        }

        var verification = await ValidateAsync(temporaryPath, cancellationToken).ConfigureAwait(false);
        if (!verification.IsValid)
        {
            File.Delete(temporaryPath);
            throw new PersistenceException(PersistenceErrorCodes.BackupInvalid, "Backup verification failed: " + string.Join("; ", verification.Errors));
        }

        if (File.Exists(fullBackupPath))
        {
            // Replace the previous manifest-bearing backup only after a verified new file
            // exists; File.Move(overwrite) keeps the old backup if the move itself fails.
            File.Move(temporaryPath, fullBackupPath, overwrite: true);
        }
        else
        {
            File.Move(temporaryPath, fullBackupPath);
        }

        var hash = await ComputeFileHashAsync(fullBackupPath, cancellationToken).ConfigureAwait(false);
        var manifest = new BackupManifest(fullBackupPath, hash, DateTimeOffset.UtcNow, verification.SchemaVersion, verification.TableCounts!);
        await WriteManifestAsync(fullBackupPath, manifest, cancellationToken).ConfigureAwait(false);

        return new BackupReport(fullBackupPath, hash, manifest.CreatedAt, verification.SchemaVersion, verification.TableCounts!, verification);
    }

    public async Task<BackupVerification> ValidateAsync(string backupPath, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(backupPath);
        var fullPath = Path.GetFullPath(backupPath);
        if (!File.Exists(fullPath))
        {
            return BackupVerification.Invalid(new[] { "backup-file-missing" });
        }

        try
        {
            await using var connection = new SqliteConnection(new SqliteConnectionStringBuilder
            {
                DataSource = fullPath,
                Mode = SqliteOpenMode.ReadOnly,
                Pooling = false
            }.ToString());
            await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
            await using var command = connection.CreateCommand();
            command.CommandText = "PRAGMA integrity_check;";
            var integrity = Convert.ToString(await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false), System.Globalization.CultureInfo.InvariantCulture) ?? "unknown";
            if (!string.Equals(integrity, "ok", StringComparison.OrdinalIgnoreCase))
            {
                return BackupVerification.Invalid(new[] { "integrity-check-failed:" + integrity });
            }

            await using var versionCommand = connection.CreateCommand();
            versionCommand.CommandText = "SELECT COALESCE(MAX(version), 0) FROM schema_migrations;";
            int version;
            try
            {
                version = Convert.ToInt32(await versionCommand.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false), System.Globalization.CultureInfo.InvariantCulture);
            }
            catch (SqliteException)
            {
                return BackupVerification.Invalid(new[] { "schema-migrations-missing" });
            }

            if (version > PersistenceMigrations.CurrentVersion)
            {
                return BackupVerification.Invalid(new[] { "future-schema-version:" + version });
            }

            var counts = new Dictionary<string, long>(StringComparer.Ordinal);
            foreach (var table in new[] { "accounts", "characters", "player_state", "receipts", "ledger", "outbox", "leases", "outbox_consumers", "consumer_effects", "life_state", "life_receipts" })
            {
                await using var countCommand = connection.CreateCommand();
                countCommand.CommandText = $"SELECT COUNT(*) FROM {table};";
                counts[table] = Convert.ToInt64(await countCommand.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false), System.Globalization.CultureInfo.InvariantCulture);
            }

            return new BackupVerification(true, version, counts, Array.Empty<string>());
        }
        catch (Exception exception) when (exception is SqliteException or InvalidOperationException or IOException)
        {
            return BackupVerification.Invalid(new[] { "backup-unreadable:" + exception.Message });
        }
    }

    /// <summary>
    /// Restores a verified backup into a target file using the SQLite backup API. Existing
    /// target data is replaced atomically by SQLite and the restored file is re-verified.
    /// </summary>
    public async Task<BackupReport> RestoreAsync(string backupPath, string targetPath, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(backupPath);
        ArgumentException.ThrowIfNullOrWhiteSpace(targetPath);

        var verification = await ValidateAsync(backupPath, cancellationToken).ConfigureAwait(false);
        if (!verification.IsValid)
        {
            throw new PersistenceException(PersistenceErrorCodes.BackupInvalid, "Backup verification failed: " + string.Join("; ", verification.Errors));
        }

        var manifest = await ReadManifestAsync(backupPath, cancellationToken).ConfigureAwait(false);
        if (manifest is not null)
        {
            var actualHash = await ComputeFileHashAsync(backupPath, cancellationToken).ConfigureAwait(false);
            if (!string.Equals(actualHash, manifest.Sha256, StringComparison.OrdinalIgnoreCase))
            {
                throw new PersistenceException(PersistenceErrorCodes.BackupHashMismatch, "Backup digest does not match its manifest.");
            }
        }

        var fullTarget = Path.GetFullPath(targetPath);
        var fullBackup = Path.GetFullPath(backupPath);
        if (string.Equals(fullTarget, fullBackup, StringComparison.OrdinalIgnoreCase))
        {
            throw new PersistenceException(PersistenceErrorCodes.InvalidArgument, "Restore target must differ from the backup path.");
        }

        Directory.CreateDirectory(Path.GetDirectoryName(fullTarget)!);
        var temporaryTarget = fullTarget + ".restore.tmp";
        var previousTarget = fullTarget + ".restore-old";
        TryDelete(temporaryTarget);
        TryDelete(temporaryTarget + "-wal");
        TryDelete(temporaryTarget + "-shm");
        TryDelete(previousTarget);
        TryDelete(previousTarget + "-wal");
        TryDelete(previousTarget + "-shm");

        try
        {
            // Copy into a sibling temp file first. The live target (and its WAL sidecars)
            // are only touched after the copy has been verified, so a failed or partial
            // restore cannot destroy the existing database.
            await using (var source = new SqliteConnection(new SqliteConnectionStringBuilder
            {
                DataSource = fullBackup,
                Mode = SqliteOpenMode.ReadOnly,
                Pooling = false
            }.ToString()))
            await using (var target = new SqliteConnection(new SqliteConnectionStringBuilder
            {
                DataSource = temporaryTarget,
                Mode = SqliteOpenMode.ReadWriteCreate,
                Pooling = false
            }.ToString()))
            {
                await source.OpenAsync(cancellationToken).ConfigureAwait(false);
                await target.OpenAsync(cancellationToken).ConfigureAwait(false);
                source.BackupDatabase(target);
            }

            var staged = await ValidateAsync(temporaryTarget, cancellationToken).ConfigureAwait(false);
            if (!staged.IsValid)
            {
                throw new PersistenceException(PersistenceErrorCodes.RestoreFailed, "Restored database verification failed: " + string.Join("; ", staged.Errors));
            }

            try
            {
                if (File.Exists(fullTarget))
                {
                    File.Move(fullTarget, previousTarget);
                }

                MoveIfExists(fullTarget + "-wal", previousTarget + "-wal");
                MoveIfExists(fullTarget + "-shm", previousTarget + "-shm");

                File.Move(temporaryTarget, fullTarget);
                var restored = await ValidateAsync(fullTarget, cancellationToken).ConfigureAwait(false);
                if (!restored.IsValid)
                {
                    throw new PersistenceException(PersistenceErrorCodes.RestoreFailed, "Restored database verification failed: " + string.Join("; ", restored.Errors));
                }

                TryDelete(previousTarget);
                TryDelete(previousTarget + "-wal");
                TryDelete(previousTarget + "-shm");
                var restoredHash = await ComputeFileHashAsync(fullTarget, cancellationToken).ConfigureAwait(false);
                return new BackupReport(fullTarget, restoredHash, DateTimeOffset.UtcNow, restored.SchemaVersion, restored.TableCounts!, restored);
            }
            catch
            {
                TryDelete(fullTarget);
                TryDelete(fullTarget + "-wal");
                TryDelete(fullTarget + "-shm");
                if (File.Exists(previousTarget))
                {
                    File.Move(previousTarget, fullTarget);
                    MoveIfExists(previousTarget + "-wal", fullTarget + "-wal");
                    MoveIfExists(previousTarget + "-shm", fullTarget + "-shm");
                }

                throw;
            }
        }
        finally
        {
            TryDelete(temporaryTarget);
            TryDelete(temporaryTarget + "-wal");
            TryDelete(temporaryTarget + "-shm");
        }
    }

    private static void MoveIfExists(string source, string destination)
    {
        if (File.Exists(source))
        {
            File.Move(source, destination, overwrite: true);
        }
    }

    private static void TryDelete(string path)
    {
        try
        {
            if (File.Exists(path))
            {
                File.Delete(path);
            }
        }
        catch (IOException)
        {
            // A concurrent reader still holds the file; leaving it is safer than deleting
            // anything outside this restore's own paths.
        }
        catch (UnauthorizedAccessException)
        {
            // Same: fail closed without touching unrelated files.
        }
    }

    public static async Task<string> ComputeFileHashAsync(string path, CancellationToken cancellationToken = default)
    {
        await using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 81920, useAsync: true);
        var hash = await SHA256.HashDataAsync(stream, cancellationToken).ConfigureAwait(false);
        return Convert.ToHexString(hash).ToLowerInvariant();
    }

    private static async Task WriteManifestAsync(string backupPath, BackupManifest manifest, CancellationToken cancellationToken)
    {
        var manifestPath = backupPath + ".manifest.json";
        var json = JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(manifestPath, json, cancellationToken).ConfigureAwait(false);
    }

    private static async Task<BackupManifest?> ReadManifestAsync(string backupPath, CancellationToken cancellationToken)
    {
        var manifestPath = Path.GetFullPath(backupPath) + ".manifest.json";
        if (!File.Exists(manifestPath))
        {
            return null;
        }

        var json = await File.ReadAllTextAsync(manifestPath, cancellationToken).ConfigureAwait(false);
        return JsonSerializer.Deserialize<BackupManifest>(json);
    }
}

public sealed record BackupManifest(string SourcePath, string Sha256, DateTimeOffset CreatedAt, int SchemaVersion, IReadOnlyDictionary<string, long> TableCounts);

public sealed record BackupVerification(bool IsValid, int SchemaVersion, IReadOnlyDictionary<string, long>? TableCounts, IReadOnlyList<string> Errors)
{
    public static BackupVerification Invalid(IReadOnlyList<string> errors) => new(false, 0, null, errors);
}

public sealed record BackupReport(string Path, string Sha256, DateTimeOffset CreatedAt, int SchemaVersion, IReadOnlyDictionary<string, long> TableCounts, BackupVerification Verification);
