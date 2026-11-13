using NguMach.Server.Persistence;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

/// <summary>
/// Per-test temp directory. Cleanup is bounded to the exact directory this test created;
/// no wildcard deletion of the shared temp folder is allowed.
/// </summary>
public sealed class TempWorkspace : IAsyncDisposable
{
    private static readonly string Root = Path.Combine(Path.GetTempPath(), "ngumach-qr01-tests");

    private TempWorkspace(string directory)
    {
        DirectoryPath = directory;
        DatabasePath = Path.Combine(directory, "qr01.sqlite");
    }

    public string DirectoryPath { get; }

    public string DatabasePath { get; }

    public static TempWorkspace Create()
    {
        var directory = Path.Combine(Root, Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        var resolved = Path.GetFullPath(directory);
        if (!resolved.StartsWith(Path.GetFullPath(Root) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("Test workspace escaped the bounded temp root.");
        }

        return new TempWorkspace(resolved);
    }

    public string File(string name) => Path.Combine(DirectoryPath, name);

    public ValueTask DisposeAsync()
    {
        var resolved = Path.GetFullPath(DirectoryPath);
        if (resolved.StartsWith(Path.GetFullPath(Root) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && Directory.Exists(resolved))
        {
            try
            {
                Directory.Delete(resolved, recursive: true);
            }
            catch (IOException)
            {
                // A subprocess may still be releasing the file; the unique directory stays
                // under the test root for manual inspection instead of deleting anything else.
            }
        }

        return ValueTask.CompletedTask;
    }
}

/// <summary>Initialized database with one account and one character per requested id.</summary>
public sealed class TestFixture : IAsyncDisposable
{
    private TestFixture(TempWorkspace workspace, PersistenceDatabase database)
    {
        Workspace = workspace;
        Database = database;
        Identity = new IdentityStore(database);
        Leases = new LeaseStore(database);
        UnitOfWork = new DurableUnitOfWork(database);
        Outbox = new OutboxStore(database);
        Backups = new BackupService(database);
        Recovery = new RecoveryService(database);
        Life = new LifeReceiptStore(database);
        Diagnostics = new PersistenceDiagnostics(database);
    }

    public TempWorkspace Workspace { get; }

    public PersistenceDatabase Database { get; }

    public IdentityStore Identity { get; }

    public LeaseStore Leases { get; }

    public DurableUnitOfWork UnitOfWork { get; }

    public OutboxStore Outbox { get; }

    public BackupService Backups { get; }

    public RecoveryService Recovery { get; }

    public LifeReceiptStore Life { get; }

    public PersistenceDiagnostics Diagnostics { get; }

    public static async Task<TestFixture> CreateAsync(params string[] characters)
    {
        var workspace = TempWorkspace.Create();
        var database = new PersistenceDatabase(PersistenceOptions.ForFile(workspace.DatabasePath));
        await database.InitializeAsync();
        var fixture = new TestFixture(workspace, database);
        await fixture.Identity.CreateAccountAsync("account-1");
        foreach (var character in characters.Length == 0 ? new[] { "char-a" } : characters)
        {
            await fixture.Identity.CreateCharacterAsync(character, "account-1");
        }

        return fixture;
    }

    public async Task<LeaseGrant> AcquireAsync(string character, string? owner = null, DateTimeOffset? now = null)
    {
        var result = await Leases.AcquireAsync(character, owner ?? character, now);
        Assert.True(result.Succeeded, result.ErrorCode);
        return result.Lease!;
    }

    public MutationRequest Request(string key, string character, long fencing, long expected = 0, string operation = "test", string body = "{\"amount\":1}") =>
        new(key, character, operation, body, expected, fencing);

    public Task<MutationOutcome> CommitAsync(MutationRequest request, string state, params (string Type, string Json)[] ledger) =>
        UnitOfWork.ExecuteAsync(request, _ => PlanDecision.Accept(new MutationPlan(
            state,
            ledger.Select(entry => new LedgerEntry(entry.Type, entry.Json)).ToArray(),
            new[] { new OutboxMessage("test-topic", "{\"key\":\"" + request.IdempotencyKey + "\"}") })));

    public async Task ExecuteAsync(string sql)
    {
        await using var connection = await Database.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        await command.ExecuteNonQueryAsync();
    }

    public async ValueTask DisposeAsync()
    {
        await Workspace.DisposeAsync();
    }
}