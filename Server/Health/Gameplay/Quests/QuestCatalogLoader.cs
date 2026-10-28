using System.Text.Json;
using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Quests;

public static class QuestCatalogLoader
{
    private const string RelativeDirectory = "Implementation/Content/Examples/QuestDefinition";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex TargetIdPattern =
        new(@"^[A-Z][A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex StepIdPattern =
        new(@"^STEP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex NpcIdPattern =
        new(@"^NPC_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static string DiscoverDirectory(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:QuestsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!Directory.Exists(resolved))
            {
                throw new DirectoryNotFoundException(
                    $"Content:QuestsPath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < MaxSearchDepth && directory is not null; depth++)
            {
                var candidate = Path.Combine(directory.FullName, RelativeDirectory);
                if (Directory.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new DirectoryNotFoundException(
            $"Could not locate {RelativeDirectory}. Set Content:QuestsPath or run from the repository.");
    }

    public static QuestCatalog Load(string directory)
    {
        var files = Directory
            .EnumerateFiles(directory, "*.json", SearchOption.TopDirectoryOnly)
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToList();

        if (files.Count == 0)
        {
            throw new InvalidOperationException($"{directory}: no QuestDefinition JSON files found.");
        }

        var quests = new Dictionary<string, QuestDefinition>(StringComparer.Ordinal);
        foreach (var path in files)
        {
            QuestFile? file;
            try
            {
                using var stream = File.OpenRead(path);
                file = JsonSerializer.Deserialize<QuestFile>(stream, JsonOptions);
            }
            catch (JsonException exception)
            {
                throw new InvalidOperationException(
                    $"{path}: invalid JSON ({exception.Message})", exception);
            }

            if (file is null)
            {
                throw new InvalidOperationException($"{path}: file is empty.");
            }

            if (file.SchemaVersion != 1)
            {
                throw new InvalidOperationException(
                    $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
            }

            if (!P1Validation.IsQuestId(file.QuestId))
            {
                throw new InvalidOperationException($"{path}: invalid questId '{file.QuestId}'.");
            }

            var questId = file.QuestId!;

            if (!QuestTypes.IsKnown(file.QuestType))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid questType '{file.QuestType}'.");
            }

            var levelBand = file.LevelBand;
            if (levelBand is null || levelBand.Min is null || levelBand.Max is null)
            {
                throw new InvalidOperationException(
                    $"{path}: levelBand.min and levelBand.max are required.");
            }

            var minLevel = levelBand.Min.Value;
            var maxLevel = levelBand.Max.Value;
            if (minLevel < 1 || minLevel > 100 ||
                maxLevel < 1 || maxLevel > 100 ||
                minLevel > maxLevel)
            {
                throw new InvalidOperationException(
                    $"{path}: levelBand.min/max must be within 1..100 and min <= max.");
            }

            var prerequisites = file.PrerequisiteQuestIds;
            if (prerequisites is null)
            {
                throw new InvalidOperationException(
                    $"{path}: prerequisiteQuestIds must be an array.");
            }

            var prerequisiteIds = new List<string>(prerequisites.Count);
            var seenPrerequisites = new HashSet<string>(StringComparer.Ordinal);
            foreach (var prerequisite in prerequisites)
            {
                if (!P1Validation.IsQuestId(prerequisite))
                {
                    throw new InvalidOperationException(
                        $"{path}: invalid prerequisite quest ID '{prerequisite}'.");
                }

                if (string.Equals(prerequisite, questId, StringComparison.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"{path}: quest '{questId}' cannot require itself.");
                }

                if (!seenPrerequisites.Add(prerequisite))
                {
                    throw new InvalidOperationException(
                        $"{path}: duplicate prerequisite quest ID '{prerequisite}'.");
                }

                prerequisiteIds.Add(prerequisite);
            }

            var objectiveFiles = file.Objectives;
            if (objectiveFiles is null || objectiveFiles.Count == 0)
            {
                throw new InvalidOperationException(
                    $"{path}: objectives must be a non-empty array.");
            }

            var objectives = new List<QuestObjectiveDefinition>(objectiveFiles.Count);
            var seenObjectives = new HashSet<string>(StringComparer.Ordinal);
            foreach (var objectiveFile in objectiveFiles)
            {
                if (!P1Validation.IsObjectiveId(objectiveFile.ObjectiveId))
                {
                    throw new InvalidOperationException(
                        $"{path}: invalid objectiveId '{objectiveFile.ObjectiveId}'.");
                }

                var objectiveId = objectiveFile.ObjectiveId!;
                if (!seenObjectives.Add(objectiveId))
                {
                    throw new InvalidOperationException(
                        $"{path}: duplicate objectiveId '{objectiveId}'.");
                }

                if (!QuestObjectiveTypes.IsKnown(objectiveFile.Type))
                {
                    throw new InvalidOperationException(
                        $"{path}: objective '{objectiveId}' has invalid type '{objectiveFile.Type}'.");
                }

                var targetIds = objectiveFile.TargetIds;
                if (targetIds is null || targetIds.Count == 0)
                {
                    throw new InvalidOperationException(
                        $"{path}: objective '{objectiveId}' must have at least one target ID.");
                }

                var seenTargets = new HashSet<string>(StringComparer.Ordinal);
                foreach (var targetId in targetIds)
                {
                    if (targetId is null || !TargetIdPattern.IsMatch(targetId))
                    {
                        throw new InvalidOperationException(
                            $"{path}: objective '{objectiveId}' has invalid target ID '{targetId}'.");
                    }

                    if (!seenTargets.Add(targetId))
                    {
                        throw new InvalidOperationException(
                            $"{path}: objective '{objectiveId}' has duplicate target ID '{targetId}'.");
                    }
                }

                if (objectiveFile.Count is null || objectiveFile.Count.Value < 1)
                {
                    throw new InvalidOperationException(
                        $"{path}: objective '{objectiveId}' count must be at least 1.");
                }

                if (objectiveFile.MapId is null || !MapIdPattern.IsMatch(objectiveFile.MapId))
                {
                    throw new InvalidOperationException(
                        $"{path}: objective '{objectiveId}' has invalid mapId '{objectiveFile.MapId}'.");
                }

                objectives.Add(new QuestObjectiveDefinition(
                    objectiveId,
                    objectiveFile.Type!,
                    targetIds,
                    objectiveFile.Count.Value,
                    objectiveFile.MapId));
            }

            var initialStepId = QuestStepIds.FromObjectiveId(objectives[0].ObjectiveId);
            if (!StepIdPattern.IsMatch(initialStepId))
            {
                throw new InvalidOperationException(
                    $"{path}: derived step ID '{initialStepId}' is invalid.");
            }

            var startNpcId = file.StartNpcId;
            if (startNpcId is null || !NpcIdPattern.IsMatch(startNpcId))
            {
                throw new InvalidOperationException(
                    $"{path}: startNpcId '{startNpcId}' is invalid.");
            }

            var quest = new QuestDefinition(
                questId,
                file.QuestType!,
                startNpcId,
                levelBand.Min.Value,
                levelBand.Max.Value,
                prerequisiteIds,
                objectives,
                initialStepId);

            if (!quests.TryAdd(quest.QuestId, quest))
            {
                throw new InvalidOperationException($"{path}: duplicate questId '{quest.QuestId}'.");
            }
        }

        return new QuestCatalog(quests);
    }

    private sealed class QuestFile
    {
        public int SchemaVersion { get; init; }
        public string? QuestId { get; init; }
        public string? QuestType { get; init; }
        public string? StartNpcId { get; init; }
        public LevelBandFile? LevelBand { get; init; }
        public List<string>? PrerequisiteQuestIds { get; init; }
        public List<ObjectiveFile>? Objectives { get; init; }
    }

    private sealed class LevelBandFile
    {
        public int? Min { get; init; }
        public int? Max { get; init; }
    }

    private sealed class ObjectiveFile
    {
        public string? ObjectiveId { get; init; }
        public string? Type { get; init; }
        public List<string>? TargetIds { get; init; }
        public int? Count { get; init; }
        public string? MapId { get; init; }
    }
}
