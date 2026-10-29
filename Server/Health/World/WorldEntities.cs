using System.Text.RegularExpressions;

namespace Server.Health.World;

public static class WorldEntityKinds
{
    public const string Npc = "NPC";
    public const string Mob = "MOB";
    public const string Boss = "BOSS";
    public const string GatherNode = "GATHER_NODE";
    public const string Interactable = "INTERACTABLE";

    public static bool IsValid(string? value) => value is
        Npc or Mob or Boss or GatherNode or Interactable;
}

public static class WorldEntityStates
{
    public const string Active = "ACTIVE";
    public const string Alive = "ALIVE";
    public const string Dead = "DEAD";
    public const string Available = "AVAILABLE";
    public const string Depleted = "DEPLETED";

    public static string InitialFor(string kind) => kind switch
    {
        WorldEntityKinds.Npc => Active,
        WorldEntityKinds.Mob or WorldEntityKinds.Boss => Alive,
        _ => Available
    };

    public static string RemovedFor(string kind) => kind switch
    {
        WorldEntityKinds.Mob or WorldEntityKinds.Boss => Dead,
        WorldEntityKinds.GatherNode or WorldEntityKinds.Interactable => Depleted,
        _ => string.Empty
    };
}

public sealed record WorldEntityTemplate(string TemplateId, string Kind);

public sealed class WorldEntityInstance
{
    private readonly object _syncRoot = new();

    public required string EntityId { get; init; }
    public required string RecordId { get; init; }
    public required string Kind { get; init; }
    public required IReadOnlyList<string> TemplateIds { get; init; }
    public required string MapId { get; init; }
    public required string FloorId { get; init; }
    public required double X { get; set; }
    public required double Y { get; set; }
    public required int Quantity { get; init; }
    public required int RespawnSeconds { get; init; }

    public string State { get; private set; } = string.Empty;
    public long Revision { get; private set; }
    public long LifeId { get; private set; }
    public DateTimeOffset? RemovedAtUtc { get; private set; }

    internal void MoveTo(double x, double y)
    {
        X = x;
        Y = y;
        Revision++;
    }

    internal void Initialize()
    {
        State = WorldEntityStates.InitialFor(Kind);
        Revision = 1;
        LifeId = 1;
    }

    internal bool Remove(DateTimeOffset now)
    {
        lock (_syncRoot)
        {
            var removedState = WorldEntityStates.RemovedFor(Kind);
            if (removedState.Length == 0 ||
                string.Equals(State, removedState, StringComparison.Ordinal))
            {
                return false;
            }

            State = removedState;
            RemovedAtUtc = now;
            Revision++;
            return true;
        }
    }

    internal bool TryRespawn(DateTimeOffset now)
    {
        lock (_syncRoot)
        {
            if (RemovedAtUtc is not { } removedAt || RespawnSeconds <= 0)
            {
                return false;
            }

            if (now < removedAt.AddSeconds(RespawnSeconds))
            {
                return false;
            }

            State = WorldEntityStates.InitialFor(Kind);
            RemovedAtUtc = null;
            Revision++;
            LifeId++;
            return true;
        }
    }
}

public sealed class WorldEntityCatalog
{
    public WorldEntityCatalog(
        IReadOnlyList<WorldEntityTemplate> templates,
        IReadOnlyList<WorldEntityInstance> entities)
    {
        Templates = templates;
        Entities = entities;
    }

    public IReadOnlyList<WorldEntityTemplate> Templates { get; }

    public IReadOnlyList<WorldEntityInstance> Entities { get; }

    public int Count => Entities.Count;
}

public static class WorldEntityLoader
{
    private const string RelativePath = "Implementation/Content/Runtime/world_entities_bm.json";
    private const int MaxSearchDepth = 12;

    private static readonly System.Text.Json.JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex EntityIdPattern =
        new(@"^ENT_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex RecordIdPattern =
        new(@"^MAN-[A-Z0-9_-]+$", RegexOptions.CultureInvariant);

    private static readonly Regex TemplateIdPattern =
        new(@"^[A-Z][A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:WorldEntitiesPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:WorldEntitiesPath points to '{resolved}', which does not exist.");
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
                var candidate = Path.Combine(directory.FullName, RelativePath);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {RelativePath}. Set Content:WorldEntitiesPath or run from the repository.");
    }

    public static WorldEntityCatalog Load(string path, MapBoundsCatalog maps)
    {
        WorldEntitiesFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = System.Text.Json.JsonSerializer.Deserialize<WorldEntitiesFile>(
                stream, JsonOptions);
        }
        catch (System.Text.Json.JsonException exception)
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

        var templates = new List<WorldEntityTemplate>(file.Templates?.Count ?? 0);
        var templateIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var template in file.Templates ?? [])
        {
            if (template.TemplateId is null ||
                !TemplateIdPattern.IsMatch(template.TemplateId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid templateId '{template.TemplateId}'.");
            }

            if (!WorldEntityKinds.IsValid(template.Kind))
            {
                throw new InvalidOperationException(
                    $"{path}: template {template.TemplateId} has invalid kind '{template.Kind}'.");
            }

            if (!templateIds.Add(template.TemplateId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate templateId '{template.TemplateId}'.");
            }

            templates.Add(new WorldEntityTemplate(template.TemplateId, template.Kind!));
        }

        var entities = new List<WorldEntityInstance>(file.Entities?.Count ?? 0);
        var entityIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var source in file.Entities ?? [])
        {
            if (source.EntityId is null || !EntityIdPattern.IsMatch(source.EntityId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid entityId '{source.EntityId}'.");
            }

            if (!entityIds.Add(source.EntityId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate entityId '{source.EntityId}'.");
            }

            if (source.RecordId is null || !RecordIdPattern.IsMatch(source.RecordId))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} has invalid recordId '{source.RecordId}'.");
            }

            if (!WorldEntityKinds.IsValid(source.Kind))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} has invalid kind '{source.Kind}'.");
            }

            var sourceTemplates = source.TemplateIds ?? [];
            if (sourceTemplates.Count == 0)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} needs at least one templateId.");
            }

            foreach (var templateId in sourceTemplates)
            {
                if (!templateIds.Contains(templateId))
                {
                    throw new InvalidOperationException(
                        $"{path}: {source.EntityId} references unknown template '{templateId}'.");
                }
            }

            if (source.MapId is null || source.MapId != file.MapId)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} mapId '{source.MapId}' does not match bundle.");
            }

            if (!maps.TryResolve(source.MapId, out var bounds))
            {
                throw new InvalidOperationException(
                    $"{path}: mapId '{source.MapId}' has no registry bounds.");
            }

            if (source.XWu is not { } x || !double.IsFinite(x) ||
                source.YWu is not { } y || !double.IsFinite(y) ||
                !bounds.Contains(x, y))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} position is invalid or outside bounds.");
            }

            if (source.Quantity is not { } quantity || quantity < 1)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} quantity must be >= 1.");
            }

            if (source.RespawnSeconds is not { } respawn || respawn < 0)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.EntityId} respawnSeconds must be >= 0.");
            }

            var entity = new WorldEntityInstance
            {
                EntityId = source.EntityId,
                RecordId = source.RecordId,
                Kind = source.Kind!,
                TemplateIds = sourceTemplates,
                MapId = source.MapId,
                FloorId = source.FloorId ?? "OVERWORLD",
                X = x,
                Y = y,
                Quantity = quantity,
                RespawnSeconds = respawn
            };
            entity.Initialize();
            entities.Add(entity);
        }

        return new WorldEntityCatalog(templates, entities);
    }

    private sealed class WorldEntitiesFile
    {
        public int SchemaVersion { get; init; }
        public string? MapId { get; init; }
        public List<TemplateFile>? Templates { get; init; }
        public List<EntityFile>? Entities { get; init; }
    }

    private sealed class TemplateFile
    {
        public string? TemplateId { get; init; }
        public string? Kind { get; init; }
    }

    private sealed class EntityFile
    {
        public string? EntityId { get; init; }
        public string? RecordId { get; init; }
        public string? Kind { get; init; }
        public List<string>? TemplateIds { get; init; }
        public string? MapId { get; init; }
        public string? FloorId { get; init; }
        public double? XWu { get; init; }
        public double? YWu { get; init; }
        public int? Quantity { get; init; }
        public int? RespawnSeconds { get; init; }
    }
}

public sealed class WorldEntityRegistry
{
    private readonly IReadOnlyDictionary<string, WorldEntityInstance> _entities;
    private readonly IServerClock _clock;

    public WorldEntityRegistry(WorldEntityCatalog catalog, IServerClock clock)
    {
        _entities = catalog.Entities.ToDictionary(
            entity => entity.EntityId, entity => entity);
        _clock = clock;
    }

    public int Count => _entities.Count;

    public IEnumerable<WorldEntityInstance> All => _entities.Values;

    public bool TryGet(string entityId, out WorldEntityInstance entity) =>
        _entities.TryGetValue(entityId, out entity!);

    public bool Despawn(string entityId)
    {
        if (!_entities.TryGetValue(entityId, out var entity))
        {
            return false;
        }

        return entity.Remove(_clock.UtcNow);
    }

    public int Update()
    {
        var now = _clock.UtcNow;
        var respawned = 0;
        foreach (var entity in _entities.Values)
        {
            if (entity.TryRespawn(now))
            {
                respawned++;
            }
        }

        return respawned;
    }
}
