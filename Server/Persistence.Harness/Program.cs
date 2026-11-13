using System.Data;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using NguMach.Server.Persistence;

namespace NguMach.Server.Persistence.Harness;

public static class HarnessInfo
{
    public static string AssemblyPath => typeof(HarnessInfo).Assembly.Location;
}

/// <summary>
/// Subprocess fixture used by crash/restart and two-process tests. Modes are deliberately
/// small so the test can kill the process at exact transaction boundaries.
/// </summary>
public static class Program
{
    public static async Task<int> Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("usage: <mode> [--key value ...]");
            return 2;
        }

        var mode = args[0];
        var options = Parse(args.Skip(1));

        try
        {
            return mode switch
            {
                "init" => await InitAsync(options),
                "seed" => await SeedAsync(options),
                "commit" => await CommitAsync(options, crashAfterCommit: false),
                "lost-response" => await CommitAsync(options, crashAfterCommit: true),
                "crash-before-commit" => await CrashBeforeCommitAsync(options),
                "contend" => await ContendAsync(options),
                "hold-lease" => await HoldLeaseAsync(options),
                "try-lease" => await TryLeaseAsync(options),
                "read-state" => await ReadStateAsync(options),
                _ => Fail("unknown-mode:" + mode)
            };
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine(exception.ToString());
            return 1;
        }
    }

    private static PersistenceDatabase Database(Dictionary<string, string> options) =>
        new(PersistenceOptions.ForFile(Required(options, "db")));

    private static async Task<int> InitAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        Console.WriteLine(JsonSerializer.Serialize(new { status = "initialized", version = await database.GetSchemaVersionAsync() }));
        return 0;
    }

    private static async Task<int> SeedAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var identity = new IdentityStore(database);
        var account = Required(options, "account");
        var character = Required(options, "character");
        await identity.CreateAccountAsync(account);
        await identity.CreateCharacterAsync(character, account);
        Console.WriteLine(JsonSerializer.Serialize(new { status = "seeded", account, character }));
        return 0;
    }

    private static async Task<int> CommitAsync(Dictionary<string, string> options, bool crashAfterCommit)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var character = Required(options, "character");
        var owner = options.GetValueOrDefault("owner", character);
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(character, owner);
        if (!lease.Succeeded)
        {
            Console.WriteLine(JsonSerializer.Serialize(new { status = lease.Status.ToString(), error = lease.ErrorCode }));
            return 10;
        }

        var unitOfWork = new DurableUnitOfWork(database);
        var state = options.GetValueOrDefault("state", "{\"status\":\"committed\"}");
        var request = new MutationRequest(
            Required(options, "key"),
            character,
            options.GetValueOrDefault("operation", "harness-commit"),
            options.GetValueOrDefault("request", "{}"),
            long.Parse(options.GetValueOrDefault("expected", "0"), System.Globalization.CultureInfo.InvariantCulture),
            lease.Lease!.FencingToken);

        var outcome = await unitOfWork.ExecuteAsync(request, _ => PlanDecision.Accept(new MutationPlan(
            state,
            Array.Empty<LedgerEntry>(),
            new[] { new OutboxMessage("harness", "{\"key\":\"" + request.IdempotencyKey + "\"}") })));

        if (crashAfterCommit)
        {
            // Commit is durable, but the caller never receives the response.
            Console.Out.Flush();
            Environment.Exit(43);
        }

        Console.WriteLine(JsonSerializer.Serialize(new
        {
            status = outcome.Status.ToString(),
            revision = outcome.Revision,
            replayed = outcome.Replayed,
            result = outcome.ResultJson
        }));
        return outcome.Succeeded ? 0 : 11;
    }

    private static async Task<int> CrashBeforeCommitAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var character = Required(options, "character");
        var key = Required(options, "key");
        var now = DateTimeOffset.UtcNow.ToUniversalTime().ToString("O");

        await using var connection = await database.OpenAsync();
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);
        await using (var command = connection.CreateCommand())
        {
            command.Transaction = transaction;
            command.CommandText = "INSERT INTO player_state (character_id, revision, state_json, state_hash, updated_at) VALUES ($character, 1, '{\"half\":true}', 'uncommitted', $now) ON CONFLICT(character_id) DO UPDATE SET revision=excluded.revision, state_json=excluded.state_json, state_hash=excluded.state_hash, updated_at=excluded.updated_at;";
            command.Parameters.AddWithValue("$character", character);
            command.Parameters.AddWithValue("$now", now);
            await command.ExecuteNonQueryAsync();
        }

        await using (var command = connection.CreateCommand())
        {
            command.Transaction = transaction;
            command.CommandText = "INSERT INTO receipts (idempotency_key, owner_character_id, operation, request_hash, result_json, result_hash, revision, committed_at) VALUES ($key, $character, 'crash-before-commit', 'uncommitted', '{}', 'uncommitted', 1, $now);";
            command.Parameters.AddWithValue("$key", key);
            command.Parameters.AddWithValue("$character", character);
            command.Parameters.AddWithValue("$now", now);
            await command.ExecuteNonQueryAsync();
        }

        // No commit and no rollback: the OS process dies with the transaction open.
        Environment.Exit(42);
        return 42;
    }

    private static async Task<int> ContendAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var character = Required(options, "character");
        var owner = options.GetValueOrDefault("owner", character);
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(character, owner);
        if (!lease.Succeeded)
        {
            Console.WriteLine(JsonSerializer.Serialize(new { status = lease.Status.ToString(), error = lease.ErrorCode }));
            return 10;
        }

        var barrier = Required(options, "barrier");
        var deadline = DateTimeOffset.UtcNow.AddSeconds(15);
        while (!File.Exists(barrier))
        {
            if (DateTimeOffset.UtcNow > deadline)
            {
                Console.WriteLine(JsonSerializer.Serialize(new { status = "barrier-timeout" }));
                return 12;
            }

            await Task.Delay(10);
        }

        var request = new MutationRequest(
            Required(options, "key"),
            character,
            options.GetValueOrDefault("operation", "contend"),
            options.GetValueOrDefault("request", "{}"),
            long.Parse(options.GetValueOrDefault("expected", "0"), System.Globalization.CultureInfo.InvariantCulture),
            lease.Lease!.FencingToken);

        var unitOfWork = new DurableUnitOfWork(database);
        var outcome = await unitOfWork.ExecuteAsync(request, _ => PlanDecision.Accept(new MutationPlan(
            "{\"winner\":\"" + owner + "\"}",
            Array.Empty<LedgerEntry>(),
            Array.Empty<OutboxMessage>())));

        Console.WriteLine(JsonSerializer.Serialize(new
        {
            status = outcome.Status.ToString(),
            revision = outcome.Revision,
            replayed = outcome.Replayed,
            fencing = lease.Lease.FencingToken
        }));
        return outcome.Succeeded ? 0 : 11;
    }

    private static async Task<int> HoldLeaseAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(Required(options, "character"), Required(options, "owner"));
        Console.WriteLine(JsonSerializer.Serialize(new { status = lease.Status.ToString(), fencing = lease.Lease?.FencingToken ?? 0 }));
        var seconds = int.Parse(options.GetValueOrDefault("seconds", "1"), System.Globalization.CultureInfo.InvariantCulture);
        await Task.Delay(TimeSpan.FromSeconds(seconds));
        return lease.Succeeded ? 0 : 10;
    }

    private static async Task<int> TryLeaseAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(Required(options, "character"), Required(options, "owner"));
        Console.WriteLine(JsonSerializer.Serialize(new { status = lease.Status.ToString(), error = lease.ErrorCode, fencing = lease.Lease?.FencingToken ?? 0 }));
        return lease.Succeeded ? 0 : 10;
    }

    private static async Task<int> ReadStateAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var state = await database.ReadStateAsync(Required(options, "character"));
        Console.WriteLine(JsonSerializer.Serialize(new { state = state?.StateJson, revision = state?.Revision ?? 0 }));
        return 0;
    }

    private static int Fail(string message)
    {
        Console.Error.WriteLine(message);
        return 2;
    }

    private static Dictionary<string, string> Parse(IEnumerable<string> args)
    {
        var options = new Dictionary<string, string>(StringComparer.Ordinal);
        string? pending = null;
        foreach (var argument in args)
        {
            if (argument.StartsWith("--", StringComparison.Ordinal))
            {
                if (pending is not null)
                {
                    options[pending] = "true";
                }

                pending = argument[2..];
            }
            else if (pending is not null)
            {
                options[pending] = argument;
                pending = null;
            }
        }

        if (pending is not null)
        {
            options[pending] = "true";
        }

        return options;
    }

    private static string Required(Dictionary<string, string> options, string name) =>
        options.TryGetValue(name, out var value) && !string.IsNullOrWhiteSpace(value)
            ? value
            : throw new ArgumentException("missing --" + name);
}
