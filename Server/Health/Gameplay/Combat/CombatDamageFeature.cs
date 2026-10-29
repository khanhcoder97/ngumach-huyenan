namespace Server.Health.Gameplay.Combat;

public sealed class P1CombatDamageOptions
{
    public const string SectionName = "P1:CombatDamage";

    public bool Enabled { get; set; }
}

// Lazy gate for the QOD-16 combat subset. The mob stat bundle, the SK-MK-03
// range migration and the DEC-022 guard precision bundle are only read when
// P1:CombatDamage:Enabled=true (OFF by default); enabling it logs a DEV STUB
// warning like the other feature gates. Self-check loads the bundles directly.
public sealed class CombatDamageFeature
{
    private readonly Lazy<MobStatBundle> _mobStats;
    private readonly Lazy<SkillRangeMigration> _rangeMigration;
    private readonly Lazy<GuardPrecisionBundle> _guardPrecision;

    public CombatDamageFeature(
        P1CombatDamageOptions options,
        IConfiguration configuration,
        IHostEnvironment environment)
    {
        Enabled = options.Enabled;
        _mobStats = new Lazy<MobStatBundle>(() =>
        {
            EnsureEnabled();
            var path = CombatMobStatLoader.DiscoverPath(
                configuration, environment.ContentRootPath);
            return CombatMobStatLoader.Load(path);
        });
        _rangeMigration = new Lazy<SkillRangeMigration>(() =>
        {
            EnsureEnabled();
            var path = SkillRangeMigrationLoader.DiscoverPath(
                configuration, environment.ContentRootPath);
            return SkillRangeMigrationLoader.Load(path);
        });
        _guardPrecision = new Lazy<GuardPrecisionBundle>(() =>
        {
            EnsureEnabled();
            var path = GuardPrecisionLoader.DiscoverPath(
                configuration, environment.ContentRootPath);
            return GuardPrecisionLoader.Load(path);
        });
    }

    public bool Enabled { get; }

    public MobStatBundle MobStats => _mobStats.Value;

    public SkillRangeMigration RangeMigration => _rangeMigration.Value;

    public GuardPrecisionBundle GuardPrecision => _guardPrecision.Value;

    private void EnsureEnabled()
    {
        if (!Enabled)
        {
            throw new InvalidOperationException(
                "P1:CombatDamage is disabled; combat mob stats are not loaded.");
        }
    }
}
