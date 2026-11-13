using System.Diagnostics;
using System.Text.Json;
using NguMach.Server.Persistence.Harness;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class SubprocessTests
{
    [Fact]
    public async Task CrashBeforeCommit_LeavesNoHalfWrittenRows()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var result = await RunHarnessAsync(
            "crash-before-commit",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--key", "key-crash-before");

        Assert.Equal(42, result.ExitCode);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(0, counts["receipts"]);
        Assert.Equal(0, counts["outbox"]);
        Assert.Null(await fixture.Database.ReadStateAsync("char-a"));
    }

    [Fact]
    public async Task CrashAfterCommit_LostResponse_ReplaysWithoutDoubleGrant()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var crashed = await RunHarnessAsync(
            "lost-response",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--key", "key-lost-response",
            "--expected", "0",
            "--state", "{\"gold\":5}");

        Assert.Equal(43, crashed.ExitCode);
        var state = await fixture.Database.ReadStateAsync("char-a");
        Assert.NotNull(state);
        Assert.Equal(1, state!.Revision);

        // The caller retries after restart with the same key and payload.
        var lease = await fixture.AcquireAsync("char-a");
        var replay = await fixture.UnitOfWork.ExecuteAsync(
            new MutationRequest("key-lost-response", "char-a", "harness-commit", "{}", 0, lease.FencingToken),
            _ => throw new Xunit.Sdk.XunitException("lost-response replay must not plan a new mutation"));
        Assert.Equal(MutationStatus.Replayed, replay.Status);
        Assert.Equal(1, replay.Revision);

        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["outbox"]);
    }

    [Fact]
    public async Task TwoProcesses_SameKeySamePayload_OneCommitAndOneReplay()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var barrier = fixture.Workspace.File("barrier");

        var first = StartHarness(
            "contend",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "char-a",
            "--key", "key-two-process",
            "--request", "{\"amount\":1}",
            "--barrier", barrier);
        var second = StartHarness(
            "contend",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "char-a",
            "--key", "key-two-process",
            "--request", "{\"amount\":1}",
            "--barrier", barrier);

        await Task.Delay(300);
        await File.WriteAllTextAsync(barrier, "go");
        var results = await Task.WhenAll(first, second);

        Assert.All(results, result => Assert.Equal(0, result.ExitCode));
        var statuses = results.Select(result => ParseStatus(result.StandardOutput)).ToArray();
        Assert.Contains("Committed", statuses);
        Assert.Contains("Replayed", statuses);

        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["player_state"]);
        Assert.Equal(0, counts["outbox"]);
    }

    [Fact]
    public async Task TwoProcesses_DifferentOwners_OnlyOneReceivesLease()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var holder = StartHarness(
            "hold-lease",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "owner-a",
            "--seconds", "2");
        await Task.Delay(300);
        var challenger = await RunHarnessAsync(
            "try-lease",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "owner-b");

        Assert.Equal(10, challenger.ExitCode);
        Assert.Contains("LeaseHeld", challenger.StandardOutput);
        Assert.Equal(0, (await holder).ExitCode);
    }

    [Fact]
    public async Task ExpiredLease_NewOwnerCommits_OldOwnerIsRefusedAsStale()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var ready = fixture.Workspace.File("old-ready");
        var barrier = fixture.Workspace.File("old-go");

        // The old process owns fencing token 1 and waits past its 200 ms lease TTL.
        var oldWriter = StartHarness(
            "hold-lease-then-commit",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "owner-old",
            "--lease-ttl-ms", "200",
            "--grace-ms", "0",
            "--ready-file", ready,
            "--barrier", barrier,
            "--key", "key-old-writer",
            "--state", "{\"writer\":\"old\"}");

        await WaitForFileAsync(ready, "old writer did not acquire its lease");

        // A real second process takes over with a higher fencing token and commits first.
        var takeover = await RunHarnessAsync(
            "try-lease",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-a",
            "--owner", "owner-new",
            "--lease-ttl-ms", "200",
            "--grace-ms", "0");
        Assert.Equal(0, takeover.ExitCode);
        Assert.Contains("\"fencing\":2", takeover.StandardOutput);

        var newLease = await fixture.Leases.AcquireAsync("char-a", "owner-new", DateTimeOffset.UtcNow);
        Assert.True(newLease.Succeeded);
        var committed = await fixture.CommitAsync(
            fixture.Request("key-new-writer", "char-a", newLease.Lease!.FencingToken, expected: 0),
            "{\"writer\":\"new\"}");
        Assert.Equal(MutationStatus.Committed, committed.Status);

        // Only now let the old writer attempt its stale commit.
        await File.WriteAllTextAsync(barrier, "go");
        var oldResult = await oldWriter;
        Assert.Equal(11, oldResult.ExitCode);
        Assert.Contains("StaleFencingToken", oldResult.StandardOutput);
        Assert.Equal("{\"writer\":\"new\"}", (await fixture.Database.ReadStateAsync("char-a"))!.StateJson);
        Assert.Null(await fixture.Database.ReadReceiptAsync("key-old-writer"));
    }

    [Fact]
    public async Task BenchmarkMode_MeasuresRealCommitAndReplay()
    {
        await using var fixture = await TestFixture.CreateAsync("char-bench");
        var result = await RunHarnessAsync(
            "benchmark",
            "--db", fixture.Workspace.DatabasePath,
            "--character", "char-bench",
            "--iterations", "5",
            "--replays", "20",
            "--concurrency", "2",
            "--contention-iterations", "3");

        Assert.Equal(0, result.ExitCode);
        using var document = JsonDocument.Parse(result.StandardOutput.Trim());
        var root = document.RootElement;
        Assert.Equal(5, root.GetProperty("commit").GetProperty("count").GetInt32());
        Assert.Equal(20, root.GetProperty("replay").GetProperty("count").GetInt32());
        Assert.Equal(5, root.GetProperty("outbox").GetProperty("applied").GetInt32());
        Assert.Equal(PersistenceMigrations.CurrentVersion, root.GetProperty("database").GetProperty("schemaVersion").GetInt32());
    }

    [Fact]
    public async Task ManyCharacters_OldKeyStillReplaysWithoutNewGrant()
    {
        await using var fixture = await TestFixture.CreateAsync("char-original");
        var lease = await fixture.AcquireAsync("char-original");
        var request = fixture.Request("key-life", "char-original", lease.FencingToken);
        await fixture.CommitAsync(request, "{\"life\":1}");

        for (var index = 0; index < 300; index++)
        {
            var character = "char-churn-" + index;
            await fixture.Identity.CreateCharacterAsync(character, "account-1");
            var churnLease = await fixture.AcquireAsync(character);
            await fixture.CommitAsync(
                fixture.Request("key-churn-" + index, character, churnLease.FencingToken),
                "{\"life\":1}");
        }

        // A later life for the same character retries the old key: replay, never a fresh grant.
        var laterLease = await fixture.AcquireAsync("char-original");
        var replay = await fixture.UnitOfWork.ExecuteAsync(
            new MutationRequest("key-life", "char-original", "test", "{\"amount\":1}", 0, laterLease.FencingToken),
            _ => throw new Xunit.Sdk.XunitException("old key must not plan a new mutation"));

        Assert.Equal(MutationStatus.Replayed, replay.Status);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(301, counts["receipts"]);
        Assert.Equal(301, counts["outbox"]);
    }

    private static async Task WaitForFileAsync(string path, string failureMessage)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(15);
        while (!File.Exists(path))
        {
            if (DateTimeOffset.UtcNow > deadline)
            {
                throw new Xunit.Sdk.XunitException(failureMessage + " within 15 seconds.");
            }

            await Task.Delay(10);
        }
    }

    private static string ParseStatus(string output)
    {
        using var document = JsonDocument.Parse(output.Trim());
        return document.RootElement.GetProperty("status").GetString()!;
    }

    private static async Task<ProcessResult> RunHarnessAsync(params string[] args)
    {
        var process = StartHarness(args);
        return await process;
    }

    private static Task<ProcessResult> StartHarness(params string[] args)
    {
        var dotnet = Environment.GetEnvironmentVariable("DOTNET_HOST_PATH") ?? "dotnet";
        var startInfo = new ProcessStartInfo(dotnet)
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false
        };
        startInfo.ArgumentList.Add(HarnessInfo.AssemblyPath);
        foreach (var argument in args)
        {
            startInfo.ArgumentList.Add(argument);
        }

        var process = Process.Start(startInfo) ?? throw new InvalidOperationException("Could not start harness process.");
        return ReadAsync(process);
    }

    private static async Task<ProcessResult> ReadAsync(Process process)
    {
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        return new ProcessResult(process.ExitCode, await stdout, await stderr);
    }

    private sealed record ProcessResult(int ExitCode, string StandardOutput, string StandardError);
}
