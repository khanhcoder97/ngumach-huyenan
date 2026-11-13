using Microsoft.Data.Sqlite;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class MigrationTests
{
    [Fact]
    public async Task Initialize_FreshDatabase_AppliesVersionOneAndChecksum()
    {
        await using var fixture = await TestFixture.CreateAsync();
        Assert.Equal(PersistenceMigrations.CurrentVersion, await fixture.Database.GetSchemaVersionAsync());

        await using var connection = new SqliteConnection($"Data Source={fixture.Workspace.DatabasePath}");
        await connection.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT name, checksum FROM schema_migrations WHERE version = 1;";
        await using var reader = await command.ExecuteReaderAsync();
        Assert.True(await reader.ReadAsync());
        Assert.Equal("qr01-core", reader.GetString(0));
        Assert.Equal(64, reader.GetString(1).Length);
    }

    [Fact]
    public async Task Initialize_IsIdempotent()
    {
        await using var fixture = await TestFixture.CreateAsync();
        await fixture.Database.InitializeAsync();
        await fixture.Database.InitializeAsync();
        Assert.Equal(PersistenceMigrations.CurrentVersion, await fixture.Database.GetSchemaVersionAsync());
    }

    [Fact]
    public async Task TamperedChecksum_FailsClosed()
    {
        await using var fixture = await TestFixture.CreateAsync();
        await using (var connection = new SqliteConnection($"Data Source={fixture.Workspace.DatabasePath}"))
        {
            await connection.OpenAsync();
            await using var command = connection.CreateCommand();
            command.CommandText = "UPDATE schema_migrations SET checksum = 'tampered' WHERE version = 1;";
            await command.ExecuteNonQueryAsync();
        }

        var exception = await Assert.ThrowsAsync<PersistenceException>(() => fixture.Database.InitializeAsync());
        Assert.Equal(PersistenceErrorCodes.MigrationChecksumMismatch, exception.ErrorCode);
    }

    [Fact]
    public async Task FutureSchemaVersion_FailsClosed()
    {
        await using var fixture = await TestFixture.CreateAsync();
        await using (var connection = new SqliteConnection($"Data Source={fixture.Workspace.DatabasePath}"))
        {
            await connection.OpenAsync();
            await using var command = connection.CreateCommand();
            command.CommandText = "INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (99, 'future', 'x', '2026-01-01T00:00:00.0000000+00:00');";
            await command.ExecuteNonQueryAsync();
        }

        var exception = await Assert.ThrowsAsync<PersistenceException>(() => fixture.Database.InitializeAsync());
        Assert.Equal(PersistenceErrorCodes.MigrationFutureVersion, exception.ErrorCode);
    }

    [Fact]
    public async Task IntegrityCheck_ReportsHealthyEmptyDatabase()
    {
        await using var fixture = await TestFixture.CreateAsync();
        var report = await fixture.Database.VerifyIntegrityAsync();
        Assert.True(report.IntegrityOk);
        Assert.True(report.ForeignKeysOk);
        Assert.Equal(PersistenceMigrations.CurrentVersion, report.SchemaVersion);
    }

    [Fact]
    public async Task CanonicalJson_SortsKeysAndKeepsNumberLiterals()
    {
        var left = CanonicalJson.Normalize("{\"b\":2,\"a\":{\"z\":1,\"y\":[true,\"x\"]}}");
        var right = CanonicalJson.Normalize("{\"a\":{\"y\":[true,\"x\"],\"z\":1},\"b\":2}");
        Assert.Equal(left, right);
        Assert.Equal(CanonicalJson.HashJson(left), CanonicalJson.HashJson(right));
    }

    [Fact]
    public async Task Upgrade_FromV1_AppliesV2AndKeepsExistingData()
    {
        var workspace = TempWorkspace.Create();
        await using (workspace)
        {
            await using (var connection = new SqliteConnection($"Data Source={workspace.DatabasePath}"))
            {
                await connection.OpenAsync();
                await using (var pragma = connection.CreateCommand())
                {
                    pragma.CommandText = "PRAGMA journal_mode=WAL;";
                    await pragma.ExecuteNonQueryAsync();
                }

                await using (var create = connection.CreateCommand())
                {
                    create.CommandText = "CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT NOT NULL, checksum TEXT NOT NULL, applied_at TEXT NOT NULL);";
                    await create.ExecuteNonQueryAsync();
                }

                await using (var v1 = connection.CreateCommand())
                {
                    v1.CommandText = PersistenceMigrations.All[0].Sql;
                    await v1.ExecuteNonQueryAsync();
                }

                await using (var record = connection.CreateCommand())
                {
                    record.CommandText = "INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (1, $name, $checksum, $applied);";
                    record.Parameters.AddWithValue("$name", PersistenceMigrations.All[0].Name);
                    record.Parameters.AddWithValue("$checksum", PersistenceMigrations.Checksum(PersistenceMigrations.All[0]));
                    record.Parameters.AddWithValue("$applied", DateTimeOffset.UtcNow.ToString("O"));
                    await record.ExecuteNonQueryAsync();
                }

                await using (var seed = connection.CreateCommand())
                {
                    seed.CommandText = "INSERT INTO accounts (account_id, created_at) VALUES ('account-v1', $now); INSERT INTO characters (character_id, account_id, created_at) VALUES ('char-v1', 'account-v1', $now);";
                    seed.Parameters.AddWithValue("$now", DateTimeOffset.UtcNow.ToString("O"));
                    await seed.ExecuteNonQueryAsync();
                }
            }

            var database = new PersistenceDatabase(PersistenceOptions.ForFile(workspace.DatabasePath));
            Assert.Equal(1, await database.GetSchemaVersionAsync());
            Assert.Equal(PersistenceMigrations.CurrentVersion, await database.MigrateAsync());

            var counts = await database.GetTableCountsAsync();
            Assert.Equal(1, counts["accounts"]);
            Assert.Equal(1, counts["characters"]);

            await using var verify = new SqliteConnection($"Data Source={workspace.DatabasePath}");
            await verify.OpenAsync();
            await using var columns = verify.CreateCommand();
            columns.CommandText = "SELECT name FROM pragma_table_info('outbox') WHERE name = 'dead_at';";
            Assert.Equal("dead_at", (string?)await columns.ExecuteScalarAsync());

            await using var lifeTable = verify.CreateCommand();
            lifeTable.CommandText = "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name IN ('life_state', 'life_receipts');";
            Assert.Equal(2L, (long)(await lifeTable.ExecuteScalarAsync() ?? 0L));
        }
    }
}
