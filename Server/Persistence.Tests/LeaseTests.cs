using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class LeaseTests
{
    [Fact]
    public async Task NewOwner_GetsFencingTokenOne()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var result = await fixture.Leases.AcquireAsync("char-a", "owner-a");
        Assert.True(result.Succeeded);
        Assert.Equal(MutationStatus.LeaseAcquired, result.Status);
        Assert.Equal(1, result.Lease!.FencingToken);
    }

    [Fact]
    public async Task SameOwner_RenewsWithSameFencingToken()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var first = await fixture.AcquireAsync("char-a");
        var second = await fixture.Leases.AcquireAsync("char-a", "char-a");
        Assert.True(second.Succeeded);
        Assert.Equal(MutationStatus.LeaseRenewed, second.Status);
        Assert.Equal(first.FencingToken, second.Lease!.FencingToken);
    }

    [Fact]
    public async Task OtherOwner_WhileActive_IsRefused()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.AcquireAsync("char-a", "owner-a");
        var second = await fixture.Leases.AcquireAsync("char-a", "owner-b");
        Assert.False(second.Succeeded);
        Assert.Equal(MutationStatus.LeaseHeld, second.Status);
    }

    [Fact]
    public async Task Expired_WithinGrace_SameOwner_KeepsFencingToken()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var start = DateTimeOffset.UtcNow;
        var first = await fixture.Leases.AcquireAsync("char-a", "owner-a", start);
        var insideGrace = start + fixture.Database.Options.LeaseTtl + TimeSpan.FromSeconds(30);

        var resumed = await fixture.Leases.AcquireAsync("char-a", "owner-a", insideGrace);
        Assert.True(resumed.Succeeded);
        Assert.Equal(first.Lease!.FencingToken, resumed.Lease!.FencingToken);
    }

    [Fact]
    public async Task Expired_AfterGrace_NewOwner_IncrementsFencing()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var start = DateTimeOffset.UtcNow;
        var first = await fixture.Leases.AcquireAsync("char-a", "owner-a", start);
        var afterGrace = start + fixture.Database.Options.LeaseTtl + fixture.Database.Options.ReconnectGrace + TimeSpan.FromSeconds(1);

        var takeover = await fixture.Leases.AcquireAsync("char-a", "owner-b", afterGrace);
        Assert.True(takeover.Succeeded);
        Assert.Equal(first.Lease!.FencingToken + 1, takeover.Lease!.FencingToken);
        Assert.Equal("owner-b", takeover.Lease.OwnerToken);
    }

    [Fact]
    public async Task Renew_WithStaleToken_IsRefused()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var renewed = await fixture.Leases.RenewAsync("char-a", "char-a", lease.FencingToken + 1);
        Assert.False(renewed.Succeeded);
        Assert.Equal(MutationStatus.StaleFencingToken, renewed.Status);
    }

    [Fact]
    public async Task Release_RequiresMatchingFencingToken()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        Assert.False(await fixture.Leases.ReleaseAsync("char-a", "char-a", lease.FencingToken + 1));
        Assert.True(await fixture.Leases.ReleaseAsync("char-a", "char-a", lease.FencingToken));
        Assert.Null(await fixture.Leases.ReadAsync("char-a"));
    }

    [Fact]
    public async Task UnknownCharacter_IsDenied()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var result = await fixture.Leases.AcquireAsync("char-ghost", "owner");
        Assert.False(result.Succeeded);
        Assert.Equal(MutationStatus.OwnershipDenied, result.Status);
    }

    [Fact]
    public async Task PrincipalAccount_MustOwnCharacter()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var denied = await fixture.Leases.AcquireAsync("char-a", "owner-a", principalAccountId: "account-other");
        Assert.False(denied.Succeeded);
        Assert.Equal(MutationStatus.OwnershipDenied, denied.Status);

        var allowed = await fixture.Leases.AcquireAsync("char-a", "owner-a", principalAccountId: "account-1");
        Assert.True(allowed.Succeeded);
    }
}
