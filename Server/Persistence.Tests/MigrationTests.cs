using Microsoft.Data.Sqlite;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class MigrationTests
{
    [Fact]
    public async Task Initialize_FreshDatabase_AppliesVersionOneAndChecksum()
    {
        await using var fixture = await TestFixture.CreateAsync();
        Assert.Equal(1, await fixture.Database.GetSchemaVersionAsync());

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
        Assert.Equal(1, await fixture.Database.GetSchemaVersionAsync());
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
        Assert.Equal(1, report.SchemaVersion);
    }

    [Fact]
    public async Task CanonicalJson_SortsKeysAndKeepsNumberLiterals()
    {
        var left = CanonicalJson.Normalize("{\"b\":2,\"a\":{\"z\":1,\"y\":[true,\"x\"]}}");
        var right = CanonicalJson.Normalize("{\"a\":{\"y\":[true,\"x\"],\"z\":1},\"b\":2}");
        Assert.Equal(left, right);
        Assert.Equal(CanonicalJson.HashJson(left), CanonicalJson.HashJson(right));
    }
}
