using Server.Health.Gameplay.Progress;

namespace Server.Health.Gameplay.Alpha;

// DESIGN-BM-Q3-20261104 `xp` (extending DESIGN-BM-ALPHA-20261103 `progression`),
// the only place the alpha profile turns a quest reward into a number:
// nextLevelXp(L) = 100 + 50L + 25L² for the level the player had when the quest
// was accepted, and the grant is floor(nextLevelXp * numerator / 100) with
// `normalQuestXpNumerator` 25 and `bossQuestXpNumerator` 55 over
// `denominator` 100. The worked examples the decision ships — L1 175 → 43/96,
// L2 300 → 75/165, L3 475 → 118/261 — are pinned by the self-check.
//
// Reading of the sourced fields, recorded rather than invented: the design names
// exactly two numerators and no per-quest table, so "boss" is taken to be the
// quest that carries a BOSS objective (P00-05 in the alpha pack, and the only
// quest in the shipped catalog that does) and every other quest is the normal
// case. `absoluteSourceRewardWins` has no data path yet — `rewards.xpRule` is a
// rule token and no quest record carries an absolute amount — so this resolver is
// only ever consulted for a token it knows, and reports nothing rather than
// inventing an amount for anything else.
public sealed class AlphaQuestXpRules : IQuestXpRule
{
    // The formula is checked against the source text so a design change cannot be
    // silently served by the arithmetic that was written for the old one.
    private const string ExpectedXpToNext = "ceil(100+50*L+25*L*L)";
    private const string LevelBandBase = "LEVEL_BAND_BASE";
    private const long BaseTerm = 100;
    private const long LinearTerm = 50;
    private const long SquareTerm = 25;

    private readonly int _normalNumerator;
    private readonly int _bossNumerator;
    private readonly int _denominator;

    public AlphaQuestXpRules(AlphaProgressionRules progression)
    {
        ArgumentNullException.ThrowIfNull(progression);
        if (!string.Equals(progression.XpToNext, ExpectedXpToNext, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"Alpha progression xpToNext '{progression.XpToNext}' is not the formula " +
                $"this resolver implements ({ExpectedXpToNext}).");
        }

        if (!progression.AcceptSnapshot)
        {
            throw new InvalidOperationException(
                "Alpha progression acceptSnapshot must be true: the resolver values a quest " +
                "at the level it was accepted at.");
        }

        if (progression.Denominator <= 0)
        {
            throw new InvalidOperationException(
                $"Alpha progression denominator must be positive, found {progression.Denominator}.");
        }

        if (progression.NormalQuestXpNumerator < 0 || progression.BossQuestXpNumerator < 0)
        {
            throw new InvalidOperationException(
                "Alpha progression XP numerators must be non-negative.");
        }

        _normalNumerator = progression.NormalQuestXpNumerator;
        _bossNumerator = progression.BossQuestXpNumerator;
        _denominator = progression.Denominator;
    }

    public long? Resolve(QuestXpRequest request)
    {
        // Unknown rule token, or no accept snapshot for this quest: no source for
        // the amount, so nothing is applied.
        if (!string.Equals(request.RuleId, LevelBandBase, StringComparison.Ordinal) ||
            request.AcceptedLevel < 1)
        {
            return null;
        }

        var level = request.AcceptedLevel;
        var nextLevelXp = checked(BaseTerm + (LinearTerm * level) + (SquareTerm * level * level));
        var numerator = request.IsBossQuest ? _bossNumerator : _normalNumerator;

        // FLOOR_NONNEGATIVE: both operands are non-negative, so integer division
        // truncates toward zero, which is the floor.
        return checked(nextLevelXp * numerator) / _denominator;
    }
}
