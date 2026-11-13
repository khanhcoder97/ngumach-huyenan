namespace NguMach.Server.Persistence.Domain;

/// <summary>Stable capability names used by the remote persistence adapters (R7).</summary>
public static class DomainCapabilities
{
    public const string Inventory = "inventory";
    public const string Quest = "quest";
    public const string Experience = "xp";
    public const string Currency = "currency";
    public const string Loot = "loot";
    public const string Equipment = "equipment";
    public const string Consume = "consume";
    public const string Stats = "stat";
    public const string Craft = "craft";
    public const string Mail = "mail";
    public const string Trade = "trade";
    public const string Guild = "guild";
    public const string Rank = "rank";
    public const string LifeDeathReturn = "life-death-return";
    public const string Attempt = "attempt";
    public const string Activation = "activation";
    public const string Reset = "reset";

    public static IReadOnlyList<string> All { get; } = new[]
    {
        Inventory, Quest, Experience, Currency, Loot, Equipment, Consume, Stats, Craft, Mail,
        Trade, Guild, Rank, LifeDeathReturn, Attempt, Activation, Reset
    };
}

public sealed record DomainCapability(string Name, int Version)
{
    public string Key => Name + "@" + Version.ToString(System.Globalization.CultureInfo.InvariantCulture);
}

/// <summary>A domain command addressed to one character; the library owns durability only.</summary>
public sealed record DomainCommand(
    string Capability,
    string Operation,
    string CharacterId,
    string PayloadJson,
    int CapabilityVersion = 1);

/// <summary>
/// Pure adapter implemented by the gameplay owner. It computes a plan or a refusal and must
/// not perform I/O; the persistence library runs it inside the fenced SQL transaction.
/// </summary>
public interface IDomainCommandAdapter
{
    DomainCapability Capability { get; }

    PlanDecision Plan(DomainCommand command, string? currentStateJson);
}

/// <summary>
/// Capability registry. Missing capabilities stay unsupported (never silently accepted) and a
/// duplicate name/version is rejected at registration time.
/// </summary>
public sealed class DomainAdapterRegistry
{
    private readonly Dictionary<string, IDomainCommandAdapter> _adapters = new(StringComparer.Ordinal);

    public IReadOnlyList<DomainCapability> Capabilities =>
        _adapters.Values.Select(adapter => adapter.Capability).OrderBy(capability => capability.Key, StringComparer.Ordinal).ToArray();

    public void Register(IDomainCommandAdapter adapter)
    {
        ArgumentNullException.ThrowIfNull(adapter);
        ArgumentException.ThrowIfNullOrWhiteSpace(adapter.Capability.Name);
        if (adapter.Capability.Version < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(adapter), "Capability version must be positive.");
        }

        if (!_adapters.TryAdd(adapter.Capability.Key, adapter))
        {
            throw new InvalidOperationException($"Capability '{adapter.Capability.Key}' is already registered.");
        }
    }

    public bool TryResolve(string capability, int version, out IDomainCommandAdapter? adapter) =>
        _adapters.TryGetValue(capability + "@" + version.ToString(System.Globalization.CultureInfo.InvariantCulture), out adapter);

    public PlanDecision Plan(DomainCommand command, string? currentStateJson)
    {
        ArgumentNullException.ThrowIfNull(command);
        if (!TryResolve(command.Capability, command.CapabilityVersion, out var adapter) || adapter is null)
        {
            return PlanDecision.Reject("unsupported-capability");
        }

        return adapter.Plan(command, currentStateJson);
    }
}

/// <summary>Adapter that refuses every plan until the gameplay owner implements it.</summary>
public sealed class UnsupportedDomainAdapter : IDomainCommandAdapter
{
    public UnsupportedDomainAdapter(DomainCapability capability)
    {
        Capability = capability;
    }

    public DomainCapability Capability { get; }

    public PlanDecision Plan(DomainCommand command, string? currentStateJson) => PlanDecision.Reject("unsupported-capability");
}

