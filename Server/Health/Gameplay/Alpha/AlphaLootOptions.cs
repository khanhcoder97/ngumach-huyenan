using Server.Health.Gameplay.Combat;

namespace Server.Health.Gameplay.Alpha;

// The private-alpha loot switch. It is separate from `P1:AlphaProfile` on purpose:
// DESIGN-BM-Q3-20261104 `loot` keeps `defaultGrantEnabled: false` and names
// `P1:AlphaLoot:GrantEnabled` as the only thing that may turn a rolled receipt into
// a payable grant, so an operator can run the alpha content while still paying
// nothing out.
public sealed class AlphaLootOptions
{
    public const string SectionName = "P1:AlphaLoot";

    public bool GrantEnabled { get; set; }
}

public static class AlphaLootPolicy
{
    // `loot.effectiveGrant` = AlphaProfile.Enabled AND explicit private alpha
    // AND AlphaLoot.GrantEnabled. All three, because the only source for the mob
    // coin band is the alpha design, and that design is approved for private
    // alpha — not for production economy.
    public static bool EffectiveGrantEnabled(
        AlphaLootOptions loot,
        AlphaProfileOptions profile,
        AlphaDesign design)
    {
        ArgumentNullException.ThrowIfNull(loot);
        ArgumentNullException.ThrowIfNull(profile);
        ArgumentNullException.ThrowIfNull(design);

        return loot.GrantEnabled && profile.Enabled && IsPrivateAlpha(design);
    }

    // "explicit private alpha profile": the approved status names the scope, and a
    // profile that ships default-on would not be a private alpha.
    public static bool IsPrivateAlpha(AlphaDesign design) =>
        design.Status.Contains(
            "PRIVATE_ALPHA", StringComparison.Ordinal) &&
        !design.DefaultEnabled;

    public static void Validate(
        AlphaLootOptions loot,
        AlphaProfileOptions profile,
        AlphaDesign design)
    {
        ArgumentNullException.ThrowIfNull(loot);

        if (!loot.GrantEnabled || EffectiveGrantEnabled(loot, profile, design))
        {
            return;
        }

        throw new InvalidOperationException(
            "P1:AlphaLoot:GrantEnabled=true requires P1:AlphaProfile:Enabled=true and a " +
            $"design that is explicitly private alpha (status '{design.Status}', " +
            $"defaultEnabled '{design.DefaultEnabled}'): the mob coin band exists only in " +
            "DESIGN-BM-ALPHA-20261103, so no other profile may pay it out.");
    }
}

// Implements the alpha side of the grant decision. Everything here is a reading of
// `lootAlphaOnly`; a field the design does not state stops the payout rather than
// being filled in.
public sealed class AlphaLootGrantPolicy : ILootGrantPolicy
{
    private const string MobLevelTerm = "mobLevel";
    private const string TwiceMobLevelTerm = "2*mobLevel";

    private readonly AlphaDesign _design;
    private readonly AlphaProfileOptions _profile;
    private readonly AlphaLootOptions _loot;
    private readonly bool _bandIsSourced;

    public AlphaLootGrantPolicy(
        AlphaDesign design,
        AlphaProfileOptions profile,
        AlphaLootOptions loot)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(profile);
        ArgumentNullException.ThrowIfNull(loot);
        _design = design;
        _profile = profile;
        _loot = loot;

        var rules = design.Loot;
        // The band is stated as expressions over the mob level. Anything else is
        // not the sourced band, so the grant stays blocked.
        _bandIsSourced = rules.InclusiveIntegers &&
            string.Equals(rules.CoinMinExpression, MobLevelTerm, StringComparison.Ordinal) &&
            string.Equals(rules.CoinMaxExpression, TwiceMobLevelTerm, StringComparison.Ordinal);
    }

    public LootGrantDecision Decide(Func<int> mobLevel)
    {
        if (!_loot.GrantEnabled)
        {
            // The profile is what makes the band exist: with it off nothing about
            // the shipped loot bundle changed, and the shipped blocked reason stays.
            return new LootGrantDecision(
                false,
                _profile.Enabled && AlphaLootPolicy.IsPrivateAlpha(_design)
                    ? LootGrantPolicies.DryRunReason
                    : LootGrantPolicies.SourceShortReason,
                0,
                0);
        }

        if (!AlphaLootPolicy.EffectiveGrantEnabled(_loot, _profile, _design) ||
            !_bandIsSourced)
        {
            return new LootGrantDecision(false, LootGrantPolicies.SourceShortReason, 0, 0);
        }

        // Only a kill that may actually be paid reads the mob-stat bundle.
        var level = mobLevel();
        if (level < 1)
        {
            return new LootGrantDecision(false, LootGrantPolicies.SourceShortReason, 0, 0);
        }

        return new LootGrantDecision(true, null, level, checked(level * 2));
    }
}
