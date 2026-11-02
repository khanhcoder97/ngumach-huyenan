using System.Text.RegularExpressions;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

// QOD-21 Q1b: the seven approved overlay records enter the runtime catalogs
// only when P1:AlphaProfile:Enabled is true; with the gate OFF the base
// catalogs are returned untouched. The design kinds RESCUE_INTERACTABLE and
// QUEST_HAZARD are carried verbatim on the record layer, while runtime
// entity kinds stay closed (the WorldSnapshotV2 wire enum only knows
// MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE): villagers become per-character
// INTERACTABLE entities and the training-wave hazard gets a record but no
// runtime entity until the Q1c trial engine defines its warning surface.
public static class AlphaOverlayMerger
{
    public const string OverlayDesignStatePrefix = "ALPHA_OVERLAY:";
    public const string OverlayRespawnPolicy =
        "ALPHA_OVERLAY: per-character claim persists; no respawn";

    private static readonly Regex OverlayRecordIdPattern =
        new(@"^ALPHA-[A-Z0-9_-]+$", RegexOptions.CultureInvariant);

    private static readonly Regex OverlayEntityIdPattern =
        new(@"^[A-Z][A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static bool HasRuntimeEntity(string kind) =>
        string.Equals(kind, "INTERACTABLE", StringComparison.Ordinal) ||
        string.Equals(kind, "RESCUE_INTERACTABLE", StringComparison.Ordinal);

    public static WorldRecordCatalog MergeRecords(
        WorldRecordCatalog baseCatalog, AlphaDesign design, MapBoundsCatalog maps)
    {
        ArgumentNullException.ThrowIfNull(baseCatalog);
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(maps);
        // The ALPHA-* recordId pattern can never collide with the base MAN-*
        // ids (the file loader rejects anything else), so no cross-check here.
        ValidateOverlayShape(design, maps);

        var merged = new List<WorldRecord>(baseCatalog.All);
        foreach (var overlay in design.OverlayRecords)
        {
            merged.Add(new WorldRecord(
                overlay.RecordId,
                design.Scope.MapId,
                overlay.Kind,
                $"{OverlayDesignStatePrefix}{design.DecisionId}",
                new[] { overlay.EntityId },
                overlay.X,
                overlay.Y,
                RespawnSeconds: 0,
                OverlayRespawnPolicy,
                overlay.Condition ?? $"quest {overlay.QuestId}",
                Gather: null));
        }

        return new WorldRecordCatalog(merged);
    }

    public static WorldEntityCatalog MergeEntities(
        WorldEntityCatalog baseCatalog, AlphaDesign design, MapBoundsCatalog maps)
    {
        ArgumentNullException.ThrowIfNull(baseCatalog);
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(maps);
        ValidateOverlayShape(design, maps);
        foreach (var overlay in design.OverlayRecords)
        {
            if (baseCatalog.Entities.Any(entity =>
                    string.Equals(entity.EntityId, overlay.EntityId, StringComparison.Ordinal)))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay entityId '{overlay.EntityId}' collides with a world entity.");
            }
        }

        var templates = new List<WorldEntityTemplate>(baseCatalog.Templates);
        var entities = new List<WorldEntityInstance>(baseCatalog.Entities);
        foreach (var overlay in design.OverlayRecords)
        {
            if (!HasRuntimeEntity(overlay.Kind))
            {
                continue;
            }

            templates.Add(new WorldEntityTemplate(overlay.EntityId, WorldEntityKinds.Interactable));
            var entity = new WorldEntityInstance
            {
                EntityId = overlay.EntityId,
                RecordId = overlay.RecordId,
                Kind = WorldEntityKinds.Interactable,
                TemplateIds = new[] { overlay.EntityId },
                MapId = design.Scope.MapId,
                FloorId = "OVERWORLD",
                X = overlay.X,
                Y = overlay.Y,
                Quantity = overlay.CountPerCharacter ?? 1,
                RespawnSeconds = 0,
                ClaimPolicy = WorldEntityClaimPolicies.PerCharacter
            };
            entity.Initialize();
            entities.Add(entity);
        }

        return new WorldEntityCatalog(templates, entities);
    }

    private static void ValidateOverlayShape(AlphaDesign design, MapBoundsCatalog maps)
    {
        var recordIds = new HashSet<string>(StringComparer.Ordinal);
        var entityIds = new HashSet<string>(StringComparer.Ordinal);
        if (!maps.TryResolve(design.Scope.MapId, out var bounds))
        {
            throw new InvalidOperationException(
                $"Alpha scope map '{design.Scope.MapId}' has no registry bounds.");
        }

        foreach (var overlay in design.OverlayRecords)
        {
            if (!OverlayRecordIdPattern.IsMatch(overlay.RecordId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay recordId '{overlay.RecordId}' does not match ALPHA-*.");
            }

            if (!OverlayEntityIdPattern.IsMatch(overlay.EntityId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay entityId '{overlay.EntityId}' is invalid.");
            }

            if (!recordIds.Add(overlay.RecordId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay recordId '{overlay.RecordId}' is duplicated.");
            }

            if (!entityIds.Add(overlay.EntityId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay entityId '{overlay.EntityId}' is duplicated.");
            }

            if (overlay.Kind is not ("INTERACTABLE" or "RESCUE_INTERACTABLE" or "QUEST_HAZARD"))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' has unsupported kind '{overlay.Kind}'.");
            }

            if (!bounds.Contains(overlay.X, overlay.Y))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' at ({overlay.X},{overlay.Y}) " +
                    $"is outside {design.Scope.MapId} bounds.");
            }

            if (overlay.CountPerCharacter is <= 0)
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' countPerCharacter must be positive.");
            }
        }
    }
}
