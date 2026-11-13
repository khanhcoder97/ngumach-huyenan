using System.Data;
using System.Diagnostics;
using System.Runtime.InteropServices;
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
                "hold-lease-then-commit" => await HoldLeaseThenCommitAsync(options),
                "try-lease" => await TryLeaseAsync(options),
                "read-state" => await ReadStateAsync(options),
                "benchmark" => await BenchmarkAsync(options),
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
        new(new PersistenceOptions
        {
            DatabasePath = Required(options, "db"),
            LeaseTtl = Milliseconds(options, "lease-ttl-ms", 60_000),
            ReconnectGrace = Milliseconds(options, "grace-ms", 120_000),
            BusyTimeout = Milliseconds(options, "busy-timeout-ms", 10_000)
        });

    private static TimeSpan Milliseconds(Dictionary<string, string> options, string name, int fallback) =>
        TimeSpan.FromMilliseconds(int.Parse(options.GetValueOrDefault(name, fallback.ToString(System.Globalization.CultureInfo.InvariantCulture)), System.Globalization.CultureInfo.InvariantCulture));

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

    private static async Task<int> HoldLeaseThenCommitAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var character = Required(options, "character");
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(character, Required(options, "owner"));
        Console.WriteLine(JsonSerializer.Serialize(new { status = lease.Status.ToString(), fencing = lease.Lease?.FencingToken ?? 0 }));
        if (!lease.Succeeded)
        {
            return 10;
        }

        if (options.TryGetValue("ready-file", out var readyFile))
        {
            await File.WriteAllTextAsync(readyFile, "ready");
        }

        if (options.TryGetValue("barrier", out var barrierPath))
        {
            // Deterministic test handshake: wait until the test has committed a takeover,
            // instead of racing a fixed delay against process startup and machine load.
            var deadline = DateTimeOffset.UtcNow.AddSeconds(15);
            while (!File.Exists(barrierPath))
            {
                if (DateTimeOffset.UtcNow > deadline)
                {
                    Console.WriteLine(JsonSerializer.Serialize(new { status = "barrier-timeout" }));
                    return 12;
                }

                await Task.Delay(10);
            }
        }
        else
        {
            await Task.Delay(int.Parse(options.GetValueOrDefault("delay-ms", "1000"), System.Globalization.CultureInfo.InvariantCulture));
        }

        var request = new MutationRequest(
            Required(options, "key"),
            character,
            options.GetValueOrDefault("operation", "harness-commit"),
            options.GetValueOrDefault("request", "{}"),
            long.Parse(options.GetValueOrDefault("expected", "0"), System.Globalization.CultureInfo.InvariantCulture),
            lease.Lease!.FencingToken);

        var unitOfWork = new DurableUnitOfWork(database);
        var outcome = await unitOfWork.ExecuteAsync(request, _ => PlanDecision.Accept(new MutationPlan(
            options.GetValueOrDefault("state", "{\"status\":\"late-writer\"}"),
            Array.Empty<LedgerEntry>(),
            Array.Empty<OutboxMessage>())));

        Console.WriteLine(JsonSerializer.Serialize(new
        {
            status = outcome.Status.ToString(),
            error = outcome.ErrorCode,
            revision = outcome.Revision,
            fencing = lease.Lease.FencingToken
        }));
        return outcome.Succeeded ? 0 : 11;
    }

    /// <summary>
    /// R8 benchmark: real file DB, real fenced commits and real receipt replays. Reports
    /// hardware, configured load, database size and latency percentiles. It does not remove
    /// fencing, fsync or the receipt path to make numbers look better.
    /// </summary>
    private static async Task<int> BenchmarkAsync(Dictionary<string, string> options)
    {
        var database = Database(options);
        await database.InitializeAsync();
        var character = Required(options, "character");
        var identity = new IdentityStore(database);
        var account = options.GetValueOrDefault("account", "benchmark-account");
        await identity.CreateAccountAsync(account);
        await identity.CreateCharacterAsync(character, account);

        var iterations = int.Parse(options.GetValueOrDefault("iterations", "200"), System.Globalization.CultureInfo.InvariantCulture);
        var replays = int.Parse(options.GetValueOrDefault("replays", "2000"), System.Globalization.CultureInfo.InvariantCulture);
        var concurrency = int.Parse(options.GetValueOrDefault("concurrency", "0"), System.Globalization.CultureInfo.InvariantCulture);
        var contentionIterations = int.Parse(options.GetValueOrDefault("contention-iterations", "50"), System.Globalization.CultureInfo.InvariantCulture);
        var leases = new LeaseStore(database);
        var lease = await leases.AcquireAsync(character, "benchmark-owner");
        if (!lease.Succeeded)
        {
            return Fail("benchmark-lease-failed:" + lease.ErrorCode);
        }

        var unitOfWork = new DurableUnitOfWork(database);
        var commitLatencies = new List<double>(iterations);
        var errors = 0;
        for (var index = 0; index < iterations; index++)
        {
            var request = new MutationRequest(
                "bench-key-" + index.ToString(System.Globalization.CultureInfo.InvariantCulture),
                character,
                "benchmark",
                "{\"amount\":1}",
                index,
                lease.Lease!.FencingToken);

            var stopwatch = Stopwatch.StartNew();
            var outcome = await unitOfWork.ExecuteAsync(request, context => PlanDecision.Accept(new MutationPlan(
                "{\"revision\":" + (context.CurrentRevision + 1).ToString(System.Globalization.CultureInfo.InvariantCulture) + "}",
                new[] { new LedgerEntry("benchmark", "{\"index\":" + index.ToString(System.Globalization.CultureInfo.InvariantCulture) + "}") },
                new[] { new OutboxMessage("benchmark", "{\"index\":" + index.ToString(System.Globalization.CultureInfo.InvariantCulture) + "}") })));
            stopwatch.Stop();
            commitLatencies.Add(stopwatch.Elapsed.TotalMilliseconds);
            if (!outcome.Committed)
            {
                errors++;
            }
        }

        var replayLatencies = new List<double>(replays);
        for (var index = 0; index < replays; index++)
        {
            var request = new MutationRequest(
                "bench-key-0",
                character,
                "benchmark",
                "{\"amount\":1}",
                0,
                lease.Lease!.FencingToken);
            var stopwatch = Stopwatch.StartNew();
            var outcome = await unitOfWork.ExecuteAsync(request, _ => throw new InvalidOperationException("replay must not plan"));
            stopwatch.Stop();
            replayLatencies.Add(stopwatch.Elapsed.TotalMilliseconds);
            if (outcome.Status != MutationStatus.Replayed)
            {
                errors++;
            }
        }

        var dispatcher = new OutboxDispatcher(new OutboxStore(database));
        var dispatched = 0;
        var dispatchStopwatch = Stopwatch.StartNew();
        for (var batch = 0; batch < 10_000; batch++)
        {
            var report = await dispatcher.DispatchBatchAsync(
                "benchmark-consumer",
                "benchmark-worker",
                (_, applyOnce, cancellationToken) => applyOnce((_, _, _) => Task.CompletedTask),
                batchSize: PersistenceLimits.OutboxMaxBatch);
            dispatched += report.Applied;
            if (report.Claimed == 0)
            {
                break;
            }
        }

        dispatchStopwatch.Stop();

        var contention = new List<double>();
        var contentionErrors = 0;
        if (concurrency > 0)
        {
            var tasks = new List<Task>(concurrency);
            for (var worker = 0; worker < concurrency; worker++)
            {
                var workerIndex = worker;
                tasks.Add(Task.Run(async () =>
                {
                    var workerCharacter = character + "-c" + workerIndex.ToString(System.Globalization.CultureInfo.InvariantCulture);
                    await identity.CreateCharacterAsync(workerCharacter, account);
                    var workerLease = await leases.AcquireAsync(workerCharacter, "benchmark-owner-" + workerIndex.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    if (!workerLease.Succeeded)
                    {
                        Interlocked.Increment(ref contentionErrors);
                        return;
                    }

                    for (var index = 0; index < contentionIterations; index++)
                    {
                        var request = new MutationRequest(
                            "bench-c" + workerIndex.ToString(System.Globalization.CultureInfo.InvariantCulture) + "-" + index.ToString(System.Globalization.CultureInfo.InvariantCulture),
                            workerCharacter,
                            "benchmark",
                            "{\"amount\":1}",
                            index,
                            workerLease.Lease!.FencingToken);
                        var stopwatch = Stopwatch.StartNew();
                        var outcome = await unitOfWork.ExecuteAsync(request, context => PlanDecision.Accept(new MutationPlan(
                            "{\"revision\":" + (context.CurrentRevision + 1).ToString(System.Globalization.CultureInfo.InvariantCulture) + "}",
                            Array.Empty<LedgerEntry>(),
                            Array.Empty<OutboxMessage>())));
                        stopwatch.Stop();
                        if (outcome.Committed)
                        {
                            lock (contention)
                            {
                                contention.Add(stopwatch.Elapsed.TotalMilliseconds);
                            }
                        }
                        else
                        {
                            Interlocked.Increment(ref contentionErrors);
                        }
                    }
                }));
            }

            await Task.WhenAll(tasks);
        }

        var databasePath = database.DatabasePath;
        var result = new
        {
            mode = "benchmark",
            hardware = new
            {
                os = RuntimeInformation.OSDescription,
                architecture = RuntimeInformation.ProcessArchitecture.ToString(),
                processorCount = Environment.ProcessorCount,
                dotnet = Environment.Version.ToString()
            },
            database = new
            {
                schemaVersion = await database.GetSchemaVersionAsync(),
                sizeBytes = new FileInfo(databasePath).Length,
                walBytes = File.Exists(databasePath + "-wal") ? new FileInfo(databasePath + "-wal").Length : 0,
                busyTimeoutMs = database.Options.BusyTimeout.TotalMilliseconds
            },
            config = new { iterations, replays, concurrency, contentionIterations },
            commit = Percentiles(commitLatencies),
            replay = Percentiles(replayLatencies),
            outbox = new { applied = dispatched, totalMs = Math.Round(dispatchStopwatch.Elapsed.TotalMilliseconds, 2) },
            contention = Percentiles(contention),
            contentionErrors,
            errors
        };

        Console.WriteLine(JsonSerializer.Serialize(result));
        return errors == 0 && contentionErrors == 0 ? 0 : 12;
    }

    private static object Percentiles(List<double> values)
    {
        if (values.Count == 0)
        {
            return new { count = 0, p50Ms = 0d, p95Ms = 0d, p99Ms = 0d, maxMs = 0d, totalMs = 0d };
        }

        values.Sort();
        return new
        {
            count = values.Count,
            p50Ms = Math.Round(Percentile(values, 0.50), 3),
            p95Ms = Math.Round(Percentile(values, 0.95), 3),
            p99Ms = Math.Round(Percentile(values, 0.99), 3),
            maxMs = Math.Round(values[^1], 3),
            totalMs = Math.Round(values.Sum(), 2)
        };
    }

    private static double Percentile(List<double> sorted, double percentile)
    {
        var rank = (int)Math.Ceiling(percentile * sorted.Count) - 1;
        return sorted[Math.Clamp(rank, 0, sorted.Count - 1)];
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
