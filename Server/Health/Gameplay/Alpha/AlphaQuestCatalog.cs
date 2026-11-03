using Server.Health.Gameplay.Quests;

namespace Server.Health.Gameplay.Alpha;

// QOD-21 Q1c: the alpha quest pack lives in its own content directory and is
// merged over the canonical catalog only when P1:AlphaProfile:Enabled is true.
// With the gate OFF the canonical catalog is returned untouched, so P00-02..05
// stay BLOCKED exactly as the shipped production content defines them.
//
// The pack is the set of quest ids the approved design carries in questRules
// (DESIGN-BM-ALPHA-20261103): P00-02..05 unblocked plus the new C1-01 runtime
// record. The merger requires exactly that set — a typo'd or missing quest id
// fails startup instead of silently shipping a half-open chain.
public static class AlphaQuestCatalogMerger
{
    public const string OverlayRelativeDirectory =
        "Implementation/Content/Examples/QuestDefinitionAlpha";

    public const int MaxSearchDepth = 12;

    private static readonly string[] PackQuestIds =
        ["P00-02", "P00-03", "P00-04", "P00-05", "C1-01"];

    public static string DiscoverOverlayDirectory(string contentRoot)
    {
        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < MaxSearchDepth && directory is not null; depth++)
            {
                var candidate = Path.Combine(directory.FullName, OverlayRelativeDirectory);
                if (Directory.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new DirectoryNotFoundException(
            $"Could not locate {OverlayRelativeDirectory}. Run from the repository.");
    }

    public static QuestCatalog Merge(IQuestCatalog baseCatalog, QuestCatalog overlayCatalog)
    {
        ArgumentNullException.ThrowIfNull(baseCatalog);
        ArgumentNullException.ThrowIfNull(overlayCatalog);

        var overlayIds = new HashSet<string>(overlayCatalog.QuestIds, StringComparer.Ordinal);
        var packIds = new HashSet<string>(PackQuestIds, StringComparer.Ordinal);
        if (!overlayIds.SetEquals(packIds))
        {
            throw new InvalidOperationException(
                $"Alpha quest overlay must define exactly the design pack " +
                $"[{string.Join(", ", PackQuestIds)}]; found [{string.Join(", ", overlayIds)}].");
        }

        var merged = new Dictionary<string, QuestDefinition>(StringComparer.Ordinal);
        foreach (var questId in baseCatalog.QuestIds)
        {
            if (baseCatalog.TryGet(questId, out var baseDefinition))
            {
                merged[questId] = baseDefinition;
            }
        }

        foreach (var questId in PackQuestIds)
        {
            if (!overlayCatalog.TryGet(questId, out var overlayDefinition))
            {
                continue;
            }

            // An alpha BLOCKED definition would leave the quest as closed as the
            // canonical one while hiding that fact behind the gate.
            if (overlayDefinition.IsBlocked)
            {
                throw new InvalidOperationException(
                    $"Alpha quest overlay '{questId}' must be ACTIVE; " +
                    "a blocked alpha definition is a silent no-op.");
            }

            merged[questId] = overlayDefinition;
        }

        return new QuestCatalog(merged);
    }
}
