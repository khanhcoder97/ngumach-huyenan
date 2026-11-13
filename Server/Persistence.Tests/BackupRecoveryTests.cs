using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class BackupRecoveryTests
{
    [Fact]
    public async Task CheckpointWal_ReportsSuccess()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-wal", "char-a", lease.FencingToken), "{\"gold\":1}");

        var checkpoint = await fixture.Database.CheckpointWalAsync();
        Assert.True(checkpoint.Succeeded);
        Assert.Equal(0, checkpoint.Busy);
    }

    [Fact]
    public async Task Recovery_ReportsPendingOutboxAndHealthyDatabase()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-recover", "char-a", lease.FencingToken), "{\"gold\":1}");

        var report = await fixture.Recovery.RecoverAsync();
        Assert.True(report.Healthy);
        Assert.True(report.WalCheckpointSucceeded);
        Assert.Equal(PersistenceMigrations.CurrentVersion, report.SchemaVersion);
        Assert.Equal(1, report.PendingOutbox);
        Assert.Equal(1, report.TableCounts["receipts"]);
    }

    [Fact]
    public async Task Backup_Restore_RoundTripsStateReceiptsAndOutbox()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-backup", "char-a", lease.FencingToken), "{\"gold\":7}", ("currency", "{\"gold\":7}"));

        var backupPath = fixture.Workspace.File("backup.sqlite");
        var backup = await fixture.Backups.CreateBackupAsync(backupPath);
        Assert.True(backup.Verification.IsValid);
        Assert.True(File.Exists(backupPath));
        Assert.True(File.Exists(backupPath + ".manifest.json"));
        Assert.Equal(64, backup.Sha256.Length);

        var restorePath = fixture.Workspace.File("restored.sqlite");
        var restored = await fixture.Backups.RestoreAsync(backupPath, restorePath);
        Assert.True(restored.Verification.IsValid);
        Assert.Equal(backup.TableCounts["receipts"], restored.TableCounts["receipts"]);
        Assert.Equal(backup.TableCounts["ledger"], restored.TableCounts["ledger"]);
        Assert.Equal(backup.TableCounts["outbox"], restored.TableCounts["outbox"]);

        var restoredDb = new PersistenceDatabase(PersistenceOptions.ForFile(restorePath));
        var state = await restoredDb.ReadStateAsync("char-a");
        Assert.Equal("{\"gold\":7}", state!.StateJson);
        Assert.NotNull(await restoredDb.ReadReceiptAsync("key-backup"));
    }

    [Fact]
    public async Task CorruptBackup_IsRejected()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var corruptPath = fixture.Workspace.File("corrupt.sqlite");
        await File.WriteAllTextAsync(corruptPath, "this is not a sqlite database at all");

        var verification = await fixture.Backups.ValidateAsync(corruptPath);
        Assert.False(verification.IsValid);
        await Assert.ThrowsAsync<PersistenceException>(() => fixture.Backups.RestoreAsync(corruptPath, fixture.Workspace.File("target.sqlite")));
    }

    [Fact]
    public async Task TruncatedBackup_IsRejected()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-truncate", "char-a", lease.FencingToken), "{\"gold\":1}");

        var backupPath = fixture.Workspace.File("truncated-source.sqlite");
        await fixture.Backups.CreateBackupAsync(backupPath);
        var truncatedPath = fixture.Workspace.File("truncated.sqlite");
        var bytes = await File.ReadAllBytesAsync(backupPath);
        await File.WriteAllBytesAsync(truncatedPath, bytes[..(bytes.Length / 3)]);

        var verification = await fixture.Backups.ValidateAsync(truncatedPath);
        Assert.False(verification.IsValid);
    }

    [Fact]
    public async Task ManifestDigestMismatch_IsRejected()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var backupPath = fixture.Workspace.File("tampered.sqlite");
        await fixture.Backups.CreateBackupAsync(backupPath);

        var manifestPath = backupPath + ".manifest.json";
        var manifest = await File.ReadAllTextAsync(manifestPath);
        await File.WriteAllTextAsync(manifestPath, manifest.Replace("\"Sha256\": \"", "\"Sha256\": \"0000", StringComparison.Ordinal));

        var exception = await Assert.ThrowsAsync<PersistenceException>(() => fixture.Backups.RestoreAsync(backupPath, fixture.Workspace.File("target.sqlite")));
        Assert.Equal(PersistenceErrorCodes.BackupHashMismatch, exception.ErrorCode);
    }

    [Fact]
    public async Task Restore_ToInvalidPath_FailsClosed()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var backupPath = fixture.Workspace.File("valid.sqlite");
        await fixture.Backups.CreateBackupAsync(backupPath);

        await Assert.ThrowsAnyAsync<Exception>(() => fixture.Backups.RestoreAsync(backupPath, "\0invalid\0path.sqlite"));
    }

    [Fact]
    public async Task MissingBackup_IsRejected()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var exception = await Assert.ThrowsAsync<PersistenceException>(() =>
            fixture.Backups.RestoreAsync(fixture.Workspace.File("missing.sqlite"), fixture.Workspace.File("target.sqlite")));
        Assert.Equal(PersistenceErrorCodes.BackupInvalid, exception.ErrorCode);
    }

    [Fact]
    public async Task Backup_IntoFileAsDirectory_FailsClosed()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var blocker = fixture.Workspace.File("blocker");
        await File.WriteAllTextAsync(blocker, "not a directory");

        await Assert.ThrowsAnyAsync<Exception>(() => fixture.Backups.CreateBackupAsync(Path.Combine(blocker, "backup.sqlite")));
        Assert.False(File.Exists(Path.Combine(blocker, "backup.sqlite")));
    }

    [Fact]
    public async Task Restore_ReplacesExistingTargetDataAtomically()
    {
        await using var source = await TestFixture.CreateAsync("char-a");
        var sourceLease = await source.AcquireAsync("char-a");
        await source.CommitAsync(source.Request("key-source", "char-a", sourceLease.FencingToken), "{\"gold\":1}");
        var backupPath = source.Workspace.File("source-backup.sqlite");
        await source.Backups.CreateBackupAsync(backupPath);

        await using var target = await TestFixture.CreateAsync("char-a");
        var targetLease = await target.AcquireAsync("char-a");
        await target.CommitAsync(target.Request("key-target", "char-a", targetLease.FencingToken), "{\"gold\":2}");
        Assert.Equal("{\"gold\":2}", (await target.Database.ReadStateAsync("char-a"))!.StateJson);

        await source.Backups.RestoreAsync(backupPath, target.Workspace.DatabasePath);

        var restored = new PersistenceDatabase(PersistenceOptions.ForFile(target.Workspace.DatabasePath));
        Assert.Equal("{\"gold\":1}", (await restored.ReadStateAsync("char-a"))!.StateJson);
        Assert.Null(await restored.ReadReceiptAsync("key-target"));
        Assert.NotNull(await restored.ReadReceiptAsync("key-source"));
        Assert.False(File.Exists(target.Workspace.DatabasePath + ".restore.tmp"));
        Assert.False(File.Exists(target.Workspace.DatabasePath + ".restore-old"));
    }

    [Fact]
    public async Task Restore_WhenTargetIoIsDenied_KeepsExistingDatabaseIntact()
    {
        await using var source = await TestFixture.CreateAsync("char-a");
        var sourceLease = await source.AcquireAsync("char-a");
        await source.CommitAsync(source.Request("key-source", "char-a", sourceLease.FencingToken), "{\"gold\":1}");
        var backupPath = source.Workspace.File("io-source.sqlite");
        await source.Backups.CreateBackupAsync(backupPath);

        await using var target = await TestFixture.CreateAsync("char-a");
        var targetLease = await target.AcquireAsync("char-a");
        await target.CommitAsync(target.Request("key-target", "char-a", targetLease.FencingToken), "{\"gold\":2}");

        // Hold the target open with FileShare.Read: Windows refuses the delete/replace that
        // a "copy over the live file" restore would need. The original must survive.
        using (new FileStream(target.Workspace.DatabasePath, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            await Assert.ThrowsAnyAsync<Exception>(() => source.Backups.RestoreAsync(backupPath, target.Workspace.DatabasePath));
        }

        var unchanged = new PersistenceDatabase(PersistenceOptions.ForFile(target.Workspace.DatabasePath));
        Assert.Equal("{\"gold\":2}", (await unchanged.ReadStateAsync("char-a"))!.StateJson);
        Assert.NotNull(await unchanged.ReadReceiptAsync("key-target"));
        Assert.False(File.Exists(target.Workspace.DatabasePath + ".restore.tmp"));
        Assert.False(File.Exists(target.Workspace.DatabasePath + ".restore-old"));
    }

    [Fact]
    public async Task Backup_WhenSourceIoIsDenied_PublishesNothing()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-io", "char-a", lease.FencingToken), "{\"gold\":1}");
        var backupPath = fixture.Workspace.File("denied-backup.sqlite");

        using (new FileStream(fixture.Workspace.DatabasePath, FileMode.Open, FileAccess.Read, FileShare.None))
        {
            await Assert.ThrowsAnyAsync<Exception>(() => fixture.Backups.CreateBackupAsync(backupPath));
        }

        Assert.False(File.Exists(backupPath));
        Assert.False(File.Exists(backupPath + ".manifest.json"));
        Assert.False(File.Exists(backupPath + ".tmp"));
    }

    [Fact]
    public async Task Restore_SameBackupTwice_IsRepeatable()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-repeat", "char-a", lease.FencingToken), "{\"gold\":9}", ("currency", "{\"gold\":9}"));
        var backupPath = fixture.Workspace.File("repeat.sqlite");
        var backup = await fixture.Backups.CreateBackupAsync(backupPath);
        var targetPath = fixture.Workspace.File("repeat-target.sqlite");

        var first = await fixture.Backups.RestoreAsync(backupPath, targetPath);
        var second = await fixture.Backups.RestoreAsync(backupPath, targetPath);

        Assert.Equal(first.Sha256, second.Sha256);
        Assert.Equal(backup.TableCounts["receipts"], second.TableCounts["receipts"]);
        Assert.Equal(backup.TableCounts["outbox"], second.TableCounts["outbox"]);
        var restored = new PersistenceDatabase(PersistenceOptions.ForFile(targetPath));
        Assert.Equal("{\"gold\":9}", (await restored.ReadStateAsync("char-a"))!.StateJson);
        Assert.False(File.Exists(targetPath + ".restore.tmp"));
        Assert.False(File.Exists(targetPath + ".restore-old"));
    }
}
