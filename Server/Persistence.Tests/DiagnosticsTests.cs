using System.Text.Json;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

/// <summary>R8: readiness/metrics expose real state with no payloads, ids or secrets.</summary>
public sealed class DiagnosticsTests
{
    [Fact]
    public async Task Readiness_ReportsRealDatabaseAndProviderStatus()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");

        var readiness = await fixture.Diagnostics.ReadReadinessAsync();

        Assert.True(readiness.Ready);
        Assert.False(readiness.Degraded);
        Assert.Equal("ok", readiness.Reason);
        Assert.True(readiness.IntegrityOk);
        Assert.True(readiness.ForeignKeysOk);
        Assert.Equal(PersistenceMigrations.CurrentVersion, readiness.Provider.SchemaVersion);
        Assert.Equal("sqlite-single-host", readiness.Provider.Provider);
        Assert.Equal("dev-test", readiness.Provider.Profile);
        Assert.Equal("postgresql-online-spec", readiness.Provider.ProductionTarget);
        Assert.Equal("not-implemented", readiness.Provider.Status);
    }

    [Fact]
    public async Task Metrics_ContainCountsButNoPayloadsOrIdentifiers()
    {
        await using var fixture = await TestFixture.CreateAsync("char-secret");
        var lease = await fixture.AcquireAsync("char-secret");
        await fixture.CommitAsync(
            fixture.Request("key-secret", "char-secret", lease.FencingToken),
            "{\"sessionToken\":\"token-should-not-leak\"}");

        var metrics = await fixture.Diagnostics.ReadMetricsAsync();
        var json = JsonSerializer.Serialize(metrics) + JsonSerializer.Serialize(await fixture.Diagnostics.ReadReadinessAsync());

        Assert.Equal(1, metrics.TableCounts["receipts"]);
        Assert.Equal(1, metrics.PendingOutbox);
        Assert.DoesNotContain("token-should-not-leak", json, StringComparison.Ordinal);
        Assert.DoesNotContain("char-secret", json, StringComparison.Ordinal);
        Assert.DoesNotContain("sessionToken", json, StringComparison.Ordinal);
        Assert.DoesNotContain("key-secret", json, StringComparison.Ordinal);
    }

    [Fact]
    public async Task DeadLetterOutbox_IsDegradedButDatabaseStillReady()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-dead", "char-a", lease.FencingToken), "{\"gold\":1}");
        var item = (await fixture.Outbox.ReadAllAsync()).Single();
        Assert.True(await fixture.Outbox.DeadLetterAsync("worker-1", item.OutboxId, "poison"));

        var readiness = await fixture.Diagnostics.ReadReadinessAsync();

        Assert.True(readiness.Ready);
        Assert.True(readiness.Degraded);
        Assert.Equal("dead-letter-outbox-present", readiness.Reason);
        Assert.Equal(1, readiness.DeadLetterOutbox);
        Assert.Equal(0, readiness.PendingOutbox);
    }

    [Fact]
    public async Task Metrics_ExposeOldestPendingAgeWithoutReadingPayload()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-age", "char-a", lease.FencingToken), "{\"gold\":1}");

        var metrics = await fixture.Diagnostics.ReadMetricsAsync(DateTimeOffset.UtcNow.AddSeconds(60));

        Assert.NotNull(metrics.OldestPendingOutboxAgeSeconds);
        Assert.InRange(metrics.OldestPendingOutboxAgeSeconds!.Value, 59, 120);
    }
}
