using NguMach.Server.Persistence.Domain;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class DomainAdapterTests
{
    [Fact]
    public void Registry_ExposesEveryAssignedCapabilityVersion()
    {
        var registry = new DomainAdapterRegistry();
        foreach (var capability in DomainCapabilities.All)
        {
            registry.Register(new UnsupportedDomainAdapter(new DomainCapability(capability, 1)));
        }

        Assert.Equal(DomainCapabilities.All.Count, registry.Capabilities.Count);
        Assert.Contains(registry.Capabilities, capability => capability.Key == "life-death-return@1");
        Assert.Contains(registry.Capabilities, capability => capability.Key == "inventory@1");
    }

    [Fact]
    public void UnregisteredOrWrongVersion_StaysUnsupported()
    {
        var registry = new DomainAdapterRegistry();
        registry.Register(new UnsupportedDomainAdapter(new DomainCapability(DomainCapabilities.Inventory, 1)));

        var missing = registry.Plan(new DomainCommand(DomainCapabilities.Quest, "accept", "char-a", "{}"), null);
        var wrongVersion = registry.Plan(new DomainCommand(DomainCapabilities.Inventory, "grant", "char-a", "{}", CapabilityVersion: 2), null);

        Assert.Equal(MutationStatus.Rejected, missing.Status);
        Assert.Equal("unsupported-capability", missing.ErrorCode);
        Assert.Equal("unsupported-capability", wrongVersion.ErrorCode);
    }

    [Fact]
    public void DuplicateCapability_IsRejectedAtRegistration()
    {
        var registry = new DomainAdapterRegistry();
        registry.Register(new UnsupportedDomainAdapter(new DomainCapability(DomainCapabilities.Currency, 1)));

        Assert.Throws<InvalidOperationException>(() =>
            registry.Register(new UnsupportedDomainAdapter(new DomainCapability(DomainCapabilities.Currency, 1))));
    }

    [Fact]
    public void ImplementedAdapter_IsCalledInsideTheFencedPlan()
    {
        var registry = new DomainAdapterRegistry();
        registry.Register(new GrantOneGoldAdapter());

        var decision = registry.Plan(new DomainCommand(DomainCapabilities.Currency, "grant", "char-a", "{\"amount\":1}"), "{\"gold\":0}");

        Assert.True(decision.IsAccepted);
        Assert.Contains("gold", decision.Plan!.NextStateJson, StringComparison.Ordinal);
    }

    private sealed class GrantOneGoldAdapter : IDomainCommandAdapter
    {
        public DomainCapability Capability { get; } = new(DomainCapabilities.Currency, 1);

        public PlanDecision Plan(DomainCommand command, string? currentStateJson) =>
            PlanDecision.Accept(new MutationPlan("{\"gold\":1}", Array.Empty<LedgerEntry>(), Array.Empty<OutboxMessage>()));
    }
}
